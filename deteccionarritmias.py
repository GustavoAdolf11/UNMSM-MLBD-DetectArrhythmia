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
    precision_recall_fscore_support
)
from imblearn.over_sampling import RandomOverSampler

import tensorflow as tf
from tensorflow.keras import layers, callbacks, optimizers, Input, Model


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

"""**Utilidades de señal y dataset**"""

def bandpass(signal, fs=360, low=0.5, high=40.0, order=4):
    nyq = 0.5*fs
    b, a = butter(order, [low/nyq, high/nyq], btype='band')
    return filtfilt(b, a, signal, method="gust")

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
        if s0 < 0 or s1 > len(sig):
            continue

        w = sig[s0:s1]
        w = (w - w.mean()) / (w.std() + 1e-6)

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
                np.empty((0, 3), np.float32),
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
                np.empty((0, 3), np.float32),
                np.array([]))
    return (np.concatenate(Xs), np.concatenate(Xr), np.concatenate(ys))

"""**Construir train/test**"""

Xtr_sig, Xtr_rr, ytr = build_dataset(TRAIN_RECORDS, BASE_PATH, DERIV_IDX)
Xte_sig, Xte_rr, yte = build_dataset(TEST_RECORDS , BASE_PATH, DERIV_IDX)

print("Train:", Xtr_sig.shape, Xtr_rr.shape, Counter(ytr))
print("Test :", Xte_sig.shape, Xte_rr.shape, Counter(yte))

if Xtr_sig.shape[0]==0 or Xte_sig.shape[0]==0:
    raise RuntimeError("No hay datos. Revisa BASE_PATH/DERIV_IDX y .dat/.hea/.atr")

"""**Preparar labels + oversampling**"""

ytr_bin = (ytr == 'V').astype(np.int32)
yte_bin = (yte == 'V').astype(np.int32)

ros = RandomOverSampler(sampling_strategy='auto', random_state=42)
Xtr_sig_bal, ytr_bin_bal = ros.fit_resample(Xtr_sig, ytr_bin)
idx_resampled = ros.sample_indices_
Xtr_rr_bal = Xtr_rr[idx_resampled]

print("Train balanceado:", Counter(ytr_bin_bal))

Xtr_sig_bal = np.expand_dims(Xtr_sig_bal, axis=-1)  # (n,360,1)
Xte_sig_cnn = np.expand_dims(Xte_sig, axis=-1)



"""**Definir CNN-1D (2 entradas: señal y RR)**"""

inp_sig = Input(shape=(WIN, 1), name='sig')
x = layers.Conv1D(32, 7, activation='relu', padding='same')(inp_sig)
x = layers.MaxPooling1D(2)(x)
x = layers.Conv1D(64, 5, activation='relu', padding='same')(x)
x = layers.MaxPooling1D(2)(x)
x = layers.Conv1D(128, 3, activation='relu', padding='same')(x)
x = layers.GlobalAveragePooling1D()(x)

inp_rr = Input(shape=(3,), name='rr')
y = layers.Dense(16, activation='relu')(inp_rr)

z = layers.Concatenate()([x, y])
z = layers.Dense(64, activation='relu')(z)
z = layers.Dropout(0.4)(z)
out = layers.Dense(1, activation='sigmoid')(z)

model = Model(inputs=[inp_sig, inp_rr], outputs=out)
model.compile(optimizer=optimizers.Adam(1e-3),
              loss='binary_crossentropy',
              metrics=['accuracy'])
model.summary()

"""**Entrenar**"""

cb = [
    callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1),
    callbacks.EarlyStopping(monitor='val_loss', patience=6, restore_best_weights=True, verbose=1)
]

hist = model.fit(
    x={'sig': Xtr_sig_bal, 'rr': Xtr_rr_bal},
    y=ytr_bin_bal,
    validation_split=0.15,
    epochs=25,
    batch_size=256,
    callbacks=cb,
    verbose=1
)

"""**Evaluar**"""

proba = model.predict({'sig': Xte_sig_cnn, 'rr': Xte_rr}, batch_size=512).ravel()
thr = 0.5
ypred_bin = (proba >= thr).astype(np.int32)

acc = accuracy_score(yte_bin, ypred_bin)
cm  = confusion_matrix(yte_bin, ypred_bin, labels=[0,1])

print(f"\nAccuracy (test): {acc:.4f}")
print("\nMatriz de confusión [real N,V] x [pred N,V]:\n", cm)
print("\nReporte:\n", classification_report(yte_bin, ypred_bin, target_names=['N','V'], digits=4))

# Curvas de entrenamiento
plt.figure(figsize=(10,4))
plt.subplot(1,2,1); plt.plot(hist.history['loss'], label='train'); plt.plot(hist.history['val_loss'], label='val'); plt.title('Pérdida'); plt.legend()
plt.subplot(1,2,2); plt.plot(hist.history['accuracy'], label='train'); plt.plot(hist.history['val_accuracy'], label='val'); plt.title('Accuracy'); plt.legend()
plt.tight_layout(); plt.show()

# Matriz de confusión visual
plt.figure(figsize=(3.6,3.2))
plt.imshow(cm, interpolation='nearest')
plt.xticks([0,1], ['N','V']); plt.yticks([0,1], ['N','V'])
for i in range(2):
    for j in range(2):
        plt.text(j, i, cm[i,j], ha='center', va='center')
plt.xlabel('Predicho'); plt.ylabel('Real'); plt.title('Confusión (CNN N vs V)')
plt.tight_layout(); plt.show()

"""**Guardar modelo (Keras + TFLite) + metadatos**"""
# Guardar en formato nativo Keras (.keras)
keras_path = os.path.join(SAVE_DIR, 'model.keras')
model.save(keras_path)
print("Guardado:", keras_path)

# Guardar en formato SavedModel (para TFLite / TFServing)
savedmodel_dir = os.path.join(SAVE_DIR, 'saved_model')
model.export(savedmodel_dir)   # 👈 ESTE es el nuevo método
print("Guardado:", savedmodel_dir)

# Historial y metadatos
pd.DataFrame(hist.history).to_csv(os.path.join(SAVE_DIR, 'history.csv'), index=False)
meta = {
    "classes": ["N","V"],
    "fs": FS, "win": WIN, "deriv_idx": DERIV_IDX,
    "train_records": TRAIN_RECORDS, "test_records": TEST_RECORDS,
    "normalizacion": "z-score por ventana",
    "inputs": {"sig": [WIN,1], "rr": [3]},
    "threshold_default": 0.5
}
with open(os.path.join(SAVE_DIR, 'meta.json'), 'w') as f:
    json.dump(meta, f, indent=2)
print("Guardado history.csv y meta.json")

# Exportar a TFLite
tflite_path = os.path.join(SAVE_DIR, 'model_nv.tflite')
converter = tf.lite.TFLiteConverter.from_saved_model(savedmodel_dir)  # 👈 usar el exportado
tflite_model = converter.convert()
with open(tflite_path, 'wb') as f:
    f.write(tflite_model)
print("Guardado TFLite:", tflite_path, "tamaño:", len(tflite_model)/1024, "KB")