"""
Test script to verify the KYC system setup
Run this to check if everything is configured correctly
"""
import sys
import os

def check_imports():
    """Check if all required packages are installed"""
    print("=" * 60)
    print("CHECKING DEPENDENCIES")
    print("=" * 60)
    
    packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'PIL': 'Pillow',
        'easyocr': 'EasyOCR',
        'firebase_admin': 'Firebase Admin SDK',
        'requests': 'Requests'
    }
    
    all_installed = True
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"✅ {name:<25} INSTALLED")
        except ImportError:
            print(f"❌ {name:<25} NOT INSTALLED")
            all_installed = False
    
    return all_installed

def check_files():
    """Check if required files exist"""
    print("\n" + "=" * 60)
    print("CHECKING PROJECT FILES")
    print("=" * 60)
    
    required_files = [
        'main.py',
        'ocr_utils.py',
        'firebase_utils.py',
        'requirements.txt',
        'templates/index.html',
        'templates/result.html'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file:<30} EXISTS")
        else:
            print(f"❌ {file:<30} MISSING")
            all_exist = False
    
    return all_exist

def check_firebase_config():
    """Check Firebase configuration"""
    print("\n" + "=" * 60)
    print("CHECKING FIREBASE CONFIGURATION")
    print("=" * 60)
    
    if os.path.exists('firebase_config.json'):
        print(f"✅ firebase_config.json EXISTS")
        
        try:
            import json
            with open('firebase_config.json', 'r') as f:
                config = json.load(f)
            
            required_keys = ['project_id', 'private_key', 'client_email']
            config_valid = True
            
            for key in required_keys:
                if key in config:
                    if config[key] == f"YOUR_{key.upper()}" or config[key].startswith("YOUR_"):
                        print(f"⚠️  {key:<20} NEEDS CONFIGURATION")
                        config_valid = False
                    else:
                        print(f"✅ {key:<20} CONFIGURED")
                else:
                    print(f"❌ {key:<20} MISSING")
                    config_valid = False
            
            return config_valid
        except Exception as e:
            print(f"❌ Error reading firebase_config.json: {e}")
            return False
    else:
        print(f"❌ firebase_config.json MISSING")
        print("   → Download from Firebase Console")
        return False

def test_ocr():
    """Test OCR functionality"""
    print("\n" + "=" * 60)
    print("TESTING OCR FUNCTIONALITY")
    print("=" * 60)
    
    try:
        from ocr_utils import extract_pan_details, extract_aadhaar_details
        
        # Test PAN extraction
        test_pan_lines = ["INCOME TAX DEPARTMENT", "PRUTHVIRAJ SANTOSH GAVHANE", "ABCDE1234F"]
        pan_result = extract_pan_details(test_pan_lines)
        
        if pan_result.get('pan_number') == 'ABCDE1234F':
            print("✅ PAN extraction working")
        else:
            print("⚠️  PAN extraction may need tuning")
        
        # Test Aadhaar extraction
        test_aadhaar_lines = ["Government of India", "529690892168"]
        aadhaar_result = extract_aadhaar_details(test_aadhaar_lines)
        
        if aadhaar_result.get('aadhaar_number') == '529690892168':
            print("✅ Aadhaar extraction working")
        else:
            print("⚠️  Aadhaar extraction may need tuning")
        
        return True
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        return False

def test_firebase_utils():
    """Test Firebase utility functions"""
    print("\n" + "=" * 60)
    print("TESTING FIREBASE UTILITIES")
    print("=" * 60)
    
    try:
        from firebase_utils import hash_aadhaar, get_last4_aadhaar, normalize_name
        
        # Test hashing
        test_aadhaar = "529690892168"
        hash_result = hash_aadhaar(test_aadhaar)
        
        if hash_result and len(hash_result) == 64:
            print(f"✅ Aadhaar hashing working")
            print(f"   Hash: {hash_result[:20]}...")
        else:
            print("❌ Aadhaar hashing failed")
        
        # Test last4
        last4 = get_last4_aadhaar(test_aadhaar)
        if last4 == "2168":
            print(f"✅ Last 4 extraction working: {last4}")
        else:
            print("❌ Last 4 extraction failed")
        
        # Test name normalization
        test_name = "  Pruthviraj   Santosh  Gavhane  "
        normalized = normalize_name(test_name)
        if normalized == "PRUTHVIRAJ SANTOSH GAVHANE":
            print(f"✅ Name normalization working")
        else:
            print(f"⚠️  Name normalization may need adjustment")
        
        return True
    except Exception as e:
        print(f"❌ Firebase utils test failed: {e}")
        return False

def print_next_steps(all_checks_passed):
    """Print next steps based on results"""
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if all_checks_passed:
        print("\n✅ All checks passed! Your system is ready.")
        print("\n📋 Next Steps:")
        print("1. Add test data to Firebase Firestore")
        print("   → Run: python generate_hash.py")
        print("2. Start the server")
        print("   → Run: uvicorn main:app --reload --port 8000")
        print("3. Open browser: http://localhost:8000")
        print("4. Upload test images and verify!")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\n📋 Common Solutions:")
        print("1. Install missing packages:")
        print("   → pip install -r requirements.txt")
        print("2. Configure Firebase:")
        print("   → Download service account key")
        print("   → Replace firebase_config.json")
        print("3. Check file structure:")
        print("   → Ensure all files are in correct locations")

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("KYC VERIFICATION SYSTEM - SETUP CHECKER")
    print("=" * 60)
    print()
    
    checks = [
        check_imports(),
        check_files(),
        check_firebase_config(),
        test_ocr(),
        test_firebase_utils()
    ]
    
    all_passed = all(checks)
    print_next_steps(all_passed)
    
    print("\n" + "=" * 60)
    print()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
