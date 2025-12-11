"""
Simple test script to validate the API setup
Run this after starting the server: python test_api.py
"""
import sys
import time

def test_imports():
    """Test if all required packages can be imported."""
    print("🧪 Testing imports...")
    
    packages = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('pydantic', 'Pydantic'),
        ('tensorflow', 'TensorFlow'),
        ('numpy', 'NumPy'),
        ('scipy', 'SciPy'),
    ]
    
    failed = []
    for package, name in packages:
        try:
            __import__(package)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            failed.append(package)
    
    if failed:
        print(f"\n❌ Missing packages: {', '.join(failed)}")
        print("💡 Install with: pip install -r requirements-api.txt")
        return False
    
    print("✅ All imports successful!\n")
    return True


def test_structure():
    """Test if directory structure is correct."""
    print("🧪 Testing project structure...")
    
    import os
    from pathlib import Path
    
    base = Path(__file__).parent
    
    required_dirs = [
        'src/domain/entities',
        'src/domain/value_objects',
        'src/domain/repositories',
        'src/application/use_cases',
        'src/application/dtos',
        'src/infrastructure/ml',
        'src/infrastructure/repositories',
        'src/infrastructure/config',
        'src/presentation/api',
        'src/presentation/schemas',
        'src/shared',
    ]
    
    failed = []
    for dir_path in required_dirs:
        full_path = base / dir_path
        if full_path.exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} (missing)")
            failed.append(dir_path)
    
    if failed:
        print(f"\n❌ Missing directories: {len(failed)}")
        return False
    
    print("✅ All directories exist!\n")
    return True


def test_model_files():
    """Test if model files exist."""
    print("🧪 Testing model files...")
    
    from pathlib import Path
    
    base = Path(__file__).parent
    model_dir = base / 'models' / 'ecg_nv_cnn'
    
    required_files = [
        'model_v7.keras',
        'meta_v7.json'
    ]
    
    if not model_dir.exists():
        print(f"  ❌ Model directory not found: {model_dir}")
        print("  💡 Make sure models are in: models/ecg_nv_cnn/")
        return False
    
    failed = []
    for file in required_files:
        file_path = model_dir / file
        if file_path.exists():
            size = file_path.stat().st_size / (1024 * 1024)  # MB
            print(f"  ✅ {file} ({size:.1f} MB)")
        else:
            print(f"  ❌ {file} (missing)")
            failed.append(file)
    
    if failed:
        print(f"\n❌ Missing model files: {', '.join(failed)}")
        print("💡 Run the training script first: python deteccionarritmias.py")
        return False
    
    print("✅ All model files exist!\n")
    return True


def test_api_startup():
    """Test if API can start (imports and configurations)."""
    print("🧪 Testing API configuration...")
    
    try:
        # Test settings
        from src.infrastructure.config.settings import settings
        print(f"  ✅ Settings loaded")
        print(f"     - App: {settings.APP_NAME}")
        print(f"     - Version: {settings.APP_VERSION}")
        print(f"     - Model: {settings.MODEL_NAME}")
        
        # Test app creation
        from src.presentation.app import app
        print(f"  ✅ FastAPI app created")
        
        # Test dependency container
        from src.infrastructure.config.dependencies import get_container
        container = get_container()
        print(f"  ✅ Dependency container initialized")
        
        print("✅ API configuration valid!\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("ECG Arrhythmia Detection API - Setup Validation")
    print("=" * 60)
    print()
    
    tests = [
        ("Import Test", test_imports),
        ("Structure Test", test_structure),
        ("Model Files Test", test_model_files),
        ("API Configuration Test", test_api_startup),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} failed with exception: {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to start the API.")
        print("\n📝 Next steps:")
        print("   1. python main.py")
        print("   2. Open http://localhost:8000/docs")
        print("   3. Try: python examples/api_usage.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
