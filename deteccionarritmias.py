import os
import json
from collections import defaultdict, Counter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import wfdb
from scipy.signal import butter, filtfilt
from sklearn.metrics import (
    confusion_matrix, 
    classification_report, 
    accuracy_score, 
    precision_recall_fscore_support,
    precision_recall_curve,
    precision_score,
    recall_score
)
from sklearn.model_selection import StratifiedShuffleSplit
from imblearn.over_sampling import RandomOverSampler

import tensorflow as tf
from tensorflow.keras import layers, callbacks, optimizers, regularizers, Input, Model

# MLOps: MLflow tracking
import mlflow
import mlflow.keras
from datetime import datetime

# Configurar MLflow
mlflow.set_tracking_uri("file:./mlruns")  # Almacenamiento local
mlflow.set_experiment("deteccion_arritmias_ecg")

BASE_PATH = os.path.join(os.path.dirname(__file__), 'mit-bih')
SAVE_DIR  = os.path.join(os.path.dirname(__file__), 'models', 'ecg_nv_cnn')
os.makedirs(SAVE_DIR, exist_ok=True)

DERIV_IDX = 0               # 0=MLII, 1=V5
FS = 360
HALF = int(0.5*FS)
WIN  = 2*HALF               # 360 muestras (1 s)

CLASSES = ['N','V']
AAMI = defaultdict(lambda: 'Q')
AAMI.update({'N':'N','L':'N','R':'N','e':'N','j':'N', 'V':'V','E':'V'})

TRAIN_RECORDS = [100,101,102,103,104,105,106,107,108,109,
                 111,112,113,114,115,116,117,118,119,
                 121,122,123,124]
TEST_RECORDS  = [200,201,202,203,205,207,208,209,210,
                 212,213,214,215,217,219,220,221,222,
                 223,228,230,231,232,233,234]

# === Flags de experimento (puedes desactivar cuando quieras) ===
USE_AUGMENT   = True     # pequeñas perturbaciones (jitter/gain/warp leve)
USE_RULEGUARD = True     # post-filtro para recortar FP de V
RANDOM_SEED   = 42
np.random.seed(RANDOM_SEED)

"""**Utilidades de señal y dataset**"""

def bandpass(signal, fs=360, low=0.5, high=40.0, order=4):
    nyq = 0.5*fs
    b, a = butter(order, [low/nyq, high/nyq], btype='band')
    return filtfilt(b, a, signal, method="gust")

def robust_z(x, eps=1e-6):
    # z-score robusto (por ventana)
    mu  = np.mean(x)
    std = np.std(x)
    return (x - mu) / (std + eps)

def extract_windows(record_id, base_path, deriv_idx=0):
    """
    Salida:
      X_sig: (n, WIN)  ventana ECG filtrada y normalizada (z-score)
      X_rr : (n, 3)    [RR_prev, RR_next, ratio]
      y    : (n,)      'N' o 'V'
    """
    rec = wfdb.rdrecord(os.path.join(base_path, f'{record_id}'))
    ann = wfdb.rdann   (os.path.join(base_path, f'{record_id}'), 'atr')

    sig = rec.p_signal[:, deriv_idx].astype(np.float32)
    sig = bandpass(sig, fs=FS, low=0.5, high=40.0, order=4)

    samples = ann.sample
    symbols = ann.symbol
    rr_sec = np.diff(samples) / FS

    X_sig, X_rr, y = [], [], []
    for i, (samp, sym) in enumerate(zip(samples, symbols)):
        s0, s1 = samp - HALF, samp + HALF
        if s0 < 0 or s1 > len(sig):  # ventana incompleta
            continue

        w = sig[s0:s1]
        w = robust_z(w)

        rr_prev = rr_sec[i-1] if 0 <= i-1 < len(rr_sec) else np.nan
        rr_next = rr_sec[i]   if i < len(rr_sec)      else np.nan
        if np.isnan(rr_prev) or np.isnan(rr_next):
            continue
        ratio = rr_next / (rr_prev + 1e-6)

        cls = AAMI[sym]
        if cls in CLASSES:
            X_sig.append(w); X_rr.append([rr_prev, rr_next, ratio]); y.append(cls)

    if not X_sig:
        return (np.empty((0, WIN), np.float32),
                np.empty((0, 3),  np.float32),
                np.array([]))
    return (np.stack(X_sig).astype(np.float32),
            np.stack(X_rr).astype(np.float32),
            np.array(y))

def build_dataset(records, base_path, deriv_idx):
    Xs, Xr, ys = [], [], []
    for rid in records:
        X_sig, X_rr, y = extract_windows(rid, base_path, deriv_idx)
        if X_sig.shape[0]==0:
            print(f'[ADVERTENCIA] Record {rid} sin ventanas válidas (deriv_idx={deriv_idx}).')
            continue
        Xs.append(X_sig); Xr.append(X_rr); ys.append(y)
    if not Xs:
        return (np.empty((0, WIN), np.float32),
                np.empty((0, 3),  np.float32),
                np.array([]))
    return (np.concatenate(Xs), np.concatenate(Xr), np.concatenate(ys))

# Construir train/test
Xtr_sig, Xtr_rr, ytr = build_dataset(TRAIN_RECORDS, BASE_PATH, DERIV_IDX)
Xte_sig, Xte_rr, yte = build_dataset(TEST_RECORDS , BASE_PATH, DERIV_IDX)

print("Train:", Xtr_sig.shape, Xtr_rr.shape, Counter(ytr))
print("Test :", Xte_sig.shape, Xte_rr.shape, Counter(yte))

if Xtr_sig.shape[0]==0 or Xte_sig.shape[0]==0:
    raise RuntimeError("No hay datos. Revisa BASE_PATH/DERIV_IDX y .dat/.hea/.atr")

# Etiquetas binarias
ytr_bin = (ytr == 'V').astype(np.int32)
yte_bin = (yte == 'V').astype(np.int32)

# Expandir canal para la CNN
Xtr_sig_cnn = np.expand_dims(Xtr_sig, -1).astype(np.float32)
Xte_sig_cnn = np.expand_dims(Xte_sig, -1).astype(np.float32)

# Definir objetivos de umbral (necesario antes de MLflow)
TARGET_PREC = 0.83
TARGET_REC  = 0.85

# ==================== MLOps: Iniciar experimento MLflow ====================
run_name = f"CNN_v7_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
mlflow.start_run(run_name=run_name)

print(f"\n🚀 MLflow Run iniciado: {run_name}")
print(f"   Run ID: {mlflow.active_run().info.run_id}")

# Log de hiperparámetros
mlflow.log_params({
    "deriv_idx": DERIV_IDX,
    "fs": FS,
    "win": WIN,
    "use_augment": USE_AUGMENT,
    "use_ruleguard": USE_RULEGUARD,
    "random_seed": RANDOM_SEED,
    "focal_gamma": 2.0,
    "focal_alpha": 0.35,
    "target_prec": TARGET_PREC,
    "target_rec": TARGET_REC,
    "batch_size": 256,
    "epochs_max": 30,
    "lr_initial": 1e-3,
    "dropout_rate": 0.35,
    "l2_regularization": 1e-4
})

# Log de distribución de datos
mlflow.log_metrics({
    "train_samples_total": int(Xtr_sig.shape[0]),
    "test_samples_total": int(Xte_sig.shape[0]),
    "train_V_original": int((ytr == 'V').sum()),
    "train_N_original": int((ytr == 'N').sum()),
    "test_V_samples": int((yte == 'V').sum()),
    "test_N_samples": int((yte == 'N').sum())
})

# Data augmentation (opcional) y oversampling real (sin SMOTE)
rng = np.random.default_rng(RANDOM_SEED)

def augment_block(w, fs=FS):
    # Pequeñas perturbaciones que no rompen morfología
    if not USE_AUGMENT:
        return w
    x = w.copy()
    # 1) jitter gaussiano leve
    x += rng.normal(0, 0.01, size=x.shape).astype(np.float32)
    # 2) gain leve (±5%)
    x = (1.0 + rng.uniform(-0.05, 0.05)) * x
    # 3) time-warp ligero (re-sample local)  — muy suave
    # evitamos librerías externas; hacemos un warp lineal simple 0.98–1.02
    scale = rng.uniform(0.98, 1.02)
    idx = np.clip((np.arange(len(x)) * scale).round().astype(int), 0, len(x)-1)
    x = x[idx]
    if len(x) < len(w):
        x = np.pad(x, (0, len(w)-len(x)), mode='edge')
    elif len(x) > len(w):
        x = x[:len(w)]
    return robust_z(x)

# Construir índices balanceados por oversampling de V (reales)
idx_V = np.where(ytr_bin==1)[0]
idx_N = np.where(ytr_bin==0)[0]
ratio = max(1, int(len(idx_N)/max(1,len(idx_V))) - 1)  # cuántas veces replicar V
idx_bal = np.concatenate([idx_N, np.tile(idx_V, ratio)])
rng.shuffle(idx_bal)

# Aplicar augmentation SOLO a una fracción de V replicados
Xtr_sig_bal = Xtr_sig_cnn[idx_bal].copy()
Xtr_rr_bal  = Xtr_rr[idx_bal].astype(np.float32).copy()
ytr_bin_bal = ytr_bin[idx_bal].astype(np.int32).copy()

if USE_AUGMENT:
    # detecta qué muestras son V en el set balanceado
    mask_V = (ytr_bin_bal==1)
    V_idx = np.where(mask_V)[0]
    # aplica augment a ~50% de V balanceados
    take = rng.choice(V_idx, size=int(0.5*len(V_idx)), replace=False)
    for i in take:
        Xtr_sig_bal[i,:,0] = augment_block(Xtr_sig_bal[i,:,0])

print("Distribución balanceada:", Counter(ytr_bin_bal))
print("Shapes:", Xtr_sig_bal.shape, Xtr_rr_bal.shape, Xte_sig_cnn.shape)

# Log datos balanceados
mlflow.log_metrics({
    "train_V_balanced": int((ytr_bin_bal == 1).sum()),
    "train_N_balanced": int((ytr_bin_bal == 0).sum()),
    "balance_ratio": float((ytr_bin_bal == 1).sum() / (ytr_bin_bal == 0).sum())
})

# [C06] Modelo CNN-1D (señal + RR)
tf.keras.backend.clear_session()

inp_sig = Input(shape=(WIN, 1), name='sig')
x = layers.Conv1D(32, 7, padding='same', activation='relu')(inp_sig)
x = layers.MaxPooling1D(2)(x)
x = layers.Conv1D(64, 5, padding='same', activation='relu')(x)
x = layers.MaxPooling1D(2)(x)
x = layers.Conv1D(128, 3, padding='same', activation='relu')(x)
x = layers.GlobalAveragePooling1D()(x)

inp_rr = Input(shape=(3,), name='rr')
y = layers.Dense(16, activation='relu')(inp_rr)

z = layers.Concatenate()([x, y])
# L2 suave ayuda a bajar sobre-confianza (menos FP)
z = layers.Dense(64, activation='relu', kernel_regularizer=regularizers.l2(1e-4))(z)
z = layers.Dropout(0.35)(z)
out = layers.Dense(1, activation='sigmoid')(z)

model = Model(inputs=[inp_sig, inp_rr], outputs=out)
model.summary()

# [C07] Loss, métricas y callbacks (Focal + PR-AUC)
def binary_focal_loss(gamma=2.0, alpha=0.35):
    import tensorflow as tf
    def loss(y_true, y_pred):
        y_true = tf.cast(y_true, tf.float32)
        y_pred = tf.clip_by_value(y_pred, 1e-7, 1-1e-7)
        pt = tf.where(tf.equal(y_true, 1), y_pred, 1-y_pred)
        w  = tf.where(tf.equal(y_true, 1), alpha, 1-alpha)
        return -tf.reduce_mean(w * tf.pow(1-pt, gamma) * tf.math.log(pt))
    return loss

pr_auc = tf.keras.metrics.AUC(curve='PR', name='pr_auc')

model.compile(
    optimizer=optimizers.Adam(1e-3),
    loss=binary_focal_loss(gamma=2.0, alpha=0.35),
    metrics=['accuracy', pr_auc]
)

cb = [
    callbacks.ReduceLROnPlateau(monitor='val_pr_auc', factor=0.5, patience=3, verbose=1, mode='max'),
    callbacks.EarlyStopping(monitor='val_pr_auc', patience=6, restore_best_weights=True, verbose=1, mode='max')
]

# [C08] Entrenamiento
hist = model.fit(
    x={'sig': Xtr_sig_bal, 'rr': Xtr_rr_bal},
    y=ytr_bin_bal,
    validation_split=0.15,
    epochs=30,
    batch_size=256,
    callbacks=cb,
    verbose=1
)

# Log métricas de entrenamiento por época
for epoch in range(len(hist.history['loss'])):
    mlflow.log_metrics({
        "train_loss": float(hist.history['loss'][epoch]),
        "train_accuracy": float(hist.history['accuracy'][epoch]),
        "train_pr_auc": float(hist.history['pr_auc'][epoch]),
        "val_loss": float(hist.history['val_loss'][epoch]),
        "val_accuracy": float(hist.history['val_accuracy'][epoch]),
        "val_pr_auc": float(hist.history['val_pr_auc'][epoch])
    }, step=epoch)

# [C09] Selección de umbral en distribución real + (opcional) Platt
# hold-out del TRAIN ORIGINAL (sin SMOTE/oversampling) ~15%
sss = StratifiedShuffleSplit(n_splits=1, test_size=0.15, random_state=RANDOM_SEED)
for tr_idx, val_idx in sss.split(Xtr_sig, ytr_bin):
    Xval_sig = np.expand_dims(Xtr_sig[val_idx], -1).astype(np.float32)
    Xval_rr  = Xtr_rr[val_idx].astype(np.float32)
    yval     = ytr_bin[val_idx].astype(np.int32)

# Probabilidades
proba_val_raw  = model.predict({'sig': Xval_sig, 'rr': Xval_rr}, batch_size=512, verbose=0).ravel()
proba_test_raw = model.predict({'sig': Xte_sig_cnn, 'rr': Xte_rr}, batch_size=512, verbose=0).ravel()

# Calibración Platt opcional (suele estabilizar el umbral)
from sklearn.linear_model import LogisticRegression
platt = LogisticRegression(max_iter=1000)
platt.fit(proba_val_raw.reshape(-1,1), yval)
proba_val  = platt.predict_proba(proba_val_raw.reshape(-1,1))[:,1]
proba_test = platt.predict_proba(proba_test_raw.reshape(-1,1))[:,1]

# Elegir umbral buscando Prec objetivo y buen recall
prec, rec, thr = precision_recall_curve(yval, proba_val)
cands_both = [(p, r, t, (2*p*r)/(p+r+1e-9))
              for t, p, r in zip(thr, prec[1:], rec[1:])
              if (p >= TARGET_PREC and r >= TARGET_REC)]
if cands_both:
    cands_both.sort(key=lambda x: x[3], reverse=True)
    thr_opt, p_val, r_val = cands_both[0][2], cands_both[0][0], cands_both[0][1]
    msg = "Cumple metas (Prec y Rec)"
else:
    allp = [(p, r, t, (2*p*r)/(p+r+1e-9)) for t,p,r in zip(thr, prec[1:], rec[1:])]
    allp.sort(key=lambda x: x[3], reverse=True)
    thr_opt, p_val, r_val = allp[0][2], allp[0][0], allp[0][1]
    msg = "Mejor F1 posible (no alcanzó ambas metas)"

print(f"[Umbral] thr_opt={thr_opt:.4f} | Prec_val={p_val:.3f} | Rec_val={r_val:.3f} | {msg}")

# Log del umbral óptimo
mlflow.log_metrics({
    "threshold_optimal": float(thr_opt),
    "threshold_precision_val": float(p_val),
    "threshold_recall_val": float(r_val)
})
mlflow.log_param("threshold_selection_method", msg)

# Predicción binaria en TEST (sin post-filtro aún)
ypred_bin = (proba_test >= thr_opt).astype(np.int32)

# [C10] RuleGuard-V (opcional): recorta FP de V usando RR y "ancho QRS" aproximado
def qrs_width_ms_from_window(w, fs=FS, center=None, rel_thr=0.5, max_ms=200):
    L = len(w)
    if center is None:
        center = L//2
    dv = np.abs(np.diff(w, prepend=w[0]))
    kernel = np.ones(5)/5.0
    env = np.convolve(dv, kernel, mode='same')
    peak = np.max(env[max(0,center-20):min(L,center+20)]) + 1e-9
    thr = rel_thr * peak
    left = center
    while left>1 and env[left] > thr:
        left -= 1
    right = center
    while right<L-2 and env[right] > thr:
        right += 1
    width_samples = right - left
    width_ms = 1000.0 * width_samples / fs
    return min(width_ms, max_ms)

if USE_RULEGUARD:
    # Sintoniza umbrales con la validación (misma que C09)
    Xval_sig_raw = Xval_sig.squeeze(-1)
    rr_ratio_val = Xval_rr[:,1] / (Xval_rr[:,0] + 1e-6)
    qrs_val_ms   = np.array([qrs_width_ms_from_window(w) for w in Xval_sig_raw])
    yhat_val     = (proba_val >= thr_opt).astype(np.int32)

    TARGET_PREC_RG = max(0.85, TARGET_PREC)  # apunta un poco más alto en Prec
    best = (0.0, (0.90,1.10,110)) # (F1, (rr_lo, rr_hi, qrs_thr))
    from sklearn.metrics import precision_recall_fscore_support, f1_score

    for rr_lo in np.linspace(0.85, 0.95, 6):
        for rr_hi in np.linspace(1.05, 1.20, 4):
            for qrs_thr in [90, 100, 110, 120, 130]:
                ytmp = yhat_val.copy()
                mask = (ytmp==1) & (rr_ratio_val>rr_lo) & (rr_ratio_val<rr_hi) & (qrs_val_ms<qrs_thr)
                ytmp[mask] = 0
                p,r,f1,_ = precision_recall_fscore_support(yval, ytmp, average='binary', zero_division=0)
                if p>=TARGET_PREC_RG and f1>best[0]:
                    best = (f1, (rr_lo, rr_hi, qrs_thr))

    rr_lo, rr_hi, qrs_thr = best[1]
    print(f"[RuleGuard-V] RR∈({rr_lo:.2f},{rr_hi:.2f}), QRS<{qrs_thr} ms")
    
    # Log parámetros de RuleGuard
    mlflow.log_params({
        "ruleguard_rr_lo": float(rr_lo),
        "ruleguard_rr_hi": float(rr_hi),
        "ruleguard_qrs_thr": int(qrs_thr)
    })

    rr_ratio_te = Xte_rr[:,1] / (Xte_rr[:,0] + 1e-6)
    qrs_te_ms   = np.array([qrs_width_ms_from_window(w) for w in Xte_sig])
    ypred_rg    = ypred_bin.copy()
    mask_te     = (ypred_rg==1) & (rr_ratio_te>rr_lo) & (rr_ratio_te<rr_hi) & (qrs_te_ms<qrs_thr)
    ypred_rg[mask_te] = 0
else:
    ypred_rg = ypred_bin

# [C11] Métricas finales
def show_results(y_true, y_pred, title="CNN N vs V"):
    acc = accuracy_score(y_true, y_pred)
    cm  = confusion_matrix(y_true, y_pred, labels=[0,1])
    rep = classification_report(y_true, y_pred, target_names=['N','V'], digits=4)
    pV  = precision_score(y_true, y_pred, pos_label=1)
    rV  = recall_score   (y_true, y_pred, pos_label=1)
    print(f"Accuracy (test): {acc:.4f}")
    print("\nMatriz de confusión [real N,V] x [pred N,V]:\n", cm)
    print("\nReporte:\n", rep)
    print(f"[Clase V] Precisión={pV:.4f} | Recall={rV:.4f}")
    plt.figure(figsize=(3.6,3.2))
    plt.imshow(cm, interpolation='nearest')
    plt.xticks([0,1], ['N','V']); plt.yticks([0,1], ['N','V'])
    for i in range(2):
        for j in range(2):
            plt.text(j, i, cm[i,j], ha='center', va='center')
    plt.xlabel('Predicho'); plt.ylabel('Real'); plt.title(f'Confusión ({title})')
    plt.tight_layout(); plt.show()

print("===> Resultados SIN/CON RuleGuard (según flag) <===")
show_results(yte_bin, ypred_rg, title="CNN N vs V")

# Log métricas finales de test
acc_final = accuracy_score(yte_bin, ypred_rg)
cm_final = confusion_matrix(yte_bin, ypred_rg, labels=[0,1])
prec_V = precision_score(yte_bin, ypred_rg, pos_label=1)
rec_V = recall_score(yte_bin, ypred_rg, pos_label=1)
f1_V = 2 * (prec_V * rec_V) / (prec_V + rec_V + 1e-9)
prec_N = precision_score(yte_bin, ypred_rg, pos_label=0)
rec_N = recall_score(yte_bin, ypred_rg, pos_label=0)
f1_N = 2 * (prec_N * rec_N) / (prec_N + rec_N + 1e-9)

mlflow.log_metrics({
    "test_accuracy": float(acc_final),
    "test_precision_V": float(prec_V),
    "test_recall_V": float(rec_V),
    "test_f1_V": float(f1_V),
    "test_precision_N": float(prec_N),
    "test_recall_N": float(rec_N),
    "test_f1_N": float(f1_N),
    "test_TN": int(cm_final[0,0]),
    "test_FP": int(cm_final[0,1]),
    "test_FN": int(cm_final[1,0]),
    "test_TP": int(cm_final[1,1])
})

# Curvas de entrenamiento
fig_training = plt.figure(figsize=(10,4))
plt.subplot(1,2,1); plt.plot(hist.history['loss'], label='train'); plt.plot(hist.history['val_loss'], label='val'); plt.title('Pérdida'); plt.xlabel('Época'); plt.ylabel('Pérdida'); plt.legend()
plt.subplot(1,2,2); plt.plot(hist.history['accuracy'], label='train'); plt.plot(hist.history['val_accuracy'], label='val'); plt.title('Accuracy'); plt.xlabel('Época'); plt.ylabel('Accuracy'); plt.legend()
plt.tight_layout()
mlflow.log_figure(fig_training, "training_curves.png")
plt.show()

# [C12] Guardar modelo + metadatos
import pandas as pd
keras_path = os.path.join(SAVE_DIR, 'model_v7.keras')
model.save(keras_path)
print("Guardado:", keras_path)

# Log modelo en MLflow con registro automático
mlflow.keras.log_model(
    model, 
    "model",
    registered_model_name="ECG_Arritmias_NvsV"
)

savedmodel_dir = os.path.join(SAVE_DIR, 'saved_model_v7')
model.export(savedmodel_dir)
print("Guardado:", savedmodel_dir)

history_csv_path = os.path.join(SAVE_DIR, 'history_v7.csv')
pd.DataFrame(hist.history).to_csv(history_csv_path, index=False)
meta = {
    "classes": ["N","V"],
    "fs": FS, "win": WIN, "deriv_idx": DERIV_IDX,
    "train_records": TRAIN_RECORDS, "test_records": TEST_RECORDS,
    "normalizacion": "z-score por ventana (robusto)",
    "inputs": {"sig": [WIN,1], "rr": [3]},
    "augmentation": bool(USE_AUGMENT),
    "ruleguard": bool(USE_RULEGUARD),
    "threshold_note": "thr_opt seleccionado en validación de distribución real + Platt",
    "mlflow_run_id": mlflow.active_run().info.run_id,
    "timestamp": datetime.now().isoformat()
}
meta_json_path = os.path.join(SAVE_DIR, 'meta_v7.json')
with open(meta_json_path, 'w') as f:
    json.dump(meta, f, indent=2)
print("Guardado history_v7.csv y meta_v7.json")

# Log artefactos en MLflow
mlflow.log_artifact(keras_path, "models")
mlflow.log_artifact(history_csv_path, "metrics")
mlflow.log_artifact(meta_json_path, "metadata")

# TFLite
tflite_path = os.path.join(SAVE_DIR, 'model_v7.tflite')
converter = tf.lite.TFLiteConverter.from_saved_model(savedmodel_dir)
tflite_model = converter.convert()
with open(tflite_path, 'wb') as f:
    f.write(tflite_model)
tflite_size_kb = round(len(tflite_model)/1024, 1)
print("Guardado TFLite:", tflite_path, "tamaño:", tflite_size_kb, "KB")

# Log TFLite y su tamaño
mlflow.log_artifact(tflite_path, "models")
mlflow.log_metric("model_size_kb", tflite_size_kb)

# Finalizar run de MLflow
mlflow.end_run()
print(f"\n✅ Experimento MLflow completado")
print(f"   Para ver resultados: mlflow ui")
print(f"   Luego abre: http://127.0.0.1:5000")