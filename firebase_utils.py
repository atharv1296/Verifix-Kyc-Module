import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
import os
import json

# Initialize Firebase
cred = None
db = None

def initialize_firebase():
    """Initialize Firebase Admin SDK from environment variables or config file"""
    global cred, db
    
    if not firebase_admin._apps:
        # Method 1: Try to load from environment variables (for Render/Production)
        firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS')
        
        if firebase_creds_json:
            try:
                # Parse JSON from environment variable
                config = json.loads(firebase_creds_json)
                cred = credentials.Certificate(config)
                firebase_admin.initialize_app(cred)
                db = firestore.client()
                print("✅ Firebase initialized successfully from environment variables")
                return True
            except Exception as e:
                print(f"⚠️  Error loading Firebase from environment: {str(e)}")
                print("   → App will run in TEST MODE (verification disabled)")
                return False
        
        # Method 2: Try to load from firebase_config.json (for local development)
        elif os.path.exists('firebase_config.json'):
            try:
                # Try to load and validate the config first
                with open('firebase_config.json', 'r') as f:
                    config = json.load(f)
                
                # Check if it has placeholder values
                if config.get('private_key', '').startswith('-----BEGIN PRIVATE KEY-----\nYOUR_'):
                    print("⚠️  Firebase config has placeholder values.")
                    print("   → Download actual service account key from Firebase Console")
                    print("   → Replace firebase_config.json with downloaded file")
                    print("   → App will run in TEST MODE (verification disabled)")
                    return False
                
                cred = credentials.Certificate('firebase_config.json')
                firebase_admin.initialize_app(cred)
                db = firestore.client()
                print("✅ Firebase initialized successfully from config file")
                return True
            except ValueError as e:
                print(f"⚠️  Firebase initialization failed: {str(e)}")
                print("   → Please add valid Firebase credentials to firebase_config.json")
                print("   → App will run in TEST MODE (verification disabled)")
                return False
            except Exception as e:
                print(f"⚠️  Error loading Firebase config: {str(e)}")
                print("   → App will run in TEST MODE (verification disabled)")
                return False
        else:
            print("⚠️  No Firebase credentials found.")
            print("   → Set FIREBASE_CREDENTIALS environment variable (production)")
            print("   → OR add firebase_config.json file (local development)")
            print("   → App will run in TEST MODE (verification disabled)")
            return False
    else:
        db = firestore.client()
        return True
    
    return False

def hash_aadhaar(aadhaar_number):
    """Create SHA-256 hash of Aadhaar number"""
    if not aadhaar_number:
        return None
    return hashlib.sha256(aadhaar_number.encode()).hexdigest()

def get_last4_aadhaar(aadhaar_number):
    """Get last 4 digits of Aadhaar"""
    if not aadhaar_number or len(aadhaar_number) < 4:
        return None
    return aadhaar_number[-4:]

def normalize_name(name):
    """Normalize name for comparison (remove extra spaces, convert to uppercase)"""
    if not name:
        return ""
    return " ".join(name.upper().split())

def fetch_firebase_data(aadhaar_number):
    """Fetch user data from Firebase Firestore using Aadhaar number directly"""
    if not db:
        initialize_firebase()
    
    if not db:
        return None
    
    try:
        # Try as integer first (for number type storage in Firebase)
        try:
            aadhaar_int = int(aadhaar_number)
            users_ref = db.collection('mock_aadhaar_users')
            
            # Try querying with aadhaar_hash field first
            query = users_ref.where('aadhaar_hash', '==', aadhaar_int).limit(1)
            results = query.get()
            
            if results:
                for doc in results:
                    return doc.to_dict()
            
            # If not found, try aadhaar_number field
            query = users_ref.where('aadhaar_number', '==', aadhaar_int).limit(1)
            results = query.get()
            
            if results:
                for doc in results:
                    return doc.to_dict()
        except (ValueError, TypeError):
            pass
        
        # If not found, try as string
        aadhaar_str = str(aadhaar_number)
        users_ref = db.collection('mock_aadhaar_users')
        
        # Try aadhaar_hash as string
        query = users_ref.where('aadhaar_hash', '==', aadhaar_str).limit(1)
        results = query.get()
        
        if results:
            for doc in results:
                return doc.to_dict()
        
        # Try aadhaar_number as string
        query = users_ref.where('aadhaar_number', '==', aadhaar_str).limit(1)
        results = query.get()
        
        if results:
            for doc in results:
                return doc.to_dict()
        
        return None
    except Exception as e:
        print(f"❌ Error fetching from Firebase: {e}")
        return None

def verify_kyc_data(ocr_data, firebase_data):
    """
    Simplified verification: If Aadhaar hash matches and record exists, it's verified
    Returns: (verified: bool, match_details: dict)
    """
    if not firebase_data:
        return False, {"error": "No Firebase record found"}
    
    # Simplified verification - just check if record exists
    # Since we already found the record by Aadhaar hash, it's verified
    match_details = {
        "aadhaar_match": True,
        "record_found": True,
        "overall_verified": True
    }
    
    return True, match_details

def process_verification(ocr_data):
    """
    Process KYC verification:
    1. Query Firebase by Aadhaar number
    2. Compare Firebase name with PAN card OCR name
    3. Verify if names match
    """
    pan_data = ocr_data.get("pan", {})
    aadhaar_data = ocr_data.get("aadhaar", {})
    
    pan_name = pan_data.get("name")
    aadhaar_number = aadhaar_data.get("aadhaar_number")
    
    if not aadhaar_number:
        return {
            "verified": False,
            "error": "No Aadhaar number found in OCR data",
            "match_details": None,
            "firebase_data": None,
            "test_mode": False
        }
    
    if not pan_name:
        return {
            "verified": False,
            "error": "No name found in PAN card OCR data",
            "match_details": None,
            "firebase_data": None,
            "test_mode": False
        }
    
    # Initialize Firebase if not already done
    firebase_initialized = initialize_firebase()
    
    # If Firebase not initialized, return test mode response
    if not firebase_initialized or not db:
        return {
            "verified": False,
            "error": "Firebase not configured - Running in TEST MODE. OCR extraction successful!",
            "match_details": None,
            "firebase_data": None,
            "test_mode": True,
            "aadhaar_number": aadhaar_number,
            "note": "Configure Firebase to enable verification"
        }
    
    # Fetch Firebase data using Aadhaar number
    firebase_data = fetch_firebase_data(aadhaar_number)
    
    if not firebase_data:
        return {
            "verified": False,
            "error": "Invalid Aadhaar number",
            "match_details": {
                "aadhaar_match": False,
                "record_found": False,
                "name_match": False,
                "overall_verified": False
            },
            "firebase_data": None,
            "test_mode": False
        }
    
    # Get Firebase name and compare with PAN name
    firebase_name = firebase_data.get('name', '')
    
    # Normalize names for comparison (uppercase, remove extra spaces)
    pan_name_normalized = normalize_name(pan_name)
    firebase_name_normalized = normalize_name(firebase_name)
    
    # Check if names match
    names_match = pan_name_normalized == firebase_name_normalized
    
    # Record found but check name match
    if not names_match:
        return {
            "verified": False,
            "error": f"Name mismatch: PAN card name '{pan_name}' does not match Firebase name '{firebase_name}'",
            "match_details": {
                "aadhaar_match": True,
                "record_found": True,
                "name_match": False,
                "overall_verified": False,
                "pan_name": pan_name,
                "firebase_name": firebase_name
            },
            "firebase_data": {
                "name": firebase_data.get('name'),
                "aadhaar_number": str(firebase_data.get('aadhaar_hash') or firebase_data.get('aadhaar_number')),
                "dob": firebase_data.get('dob'),
                "gender": firebase_data.get('gender'),
                "mobile": firebase_data.get('mobile'),
                "data_type": firebase_data.get('data_type'),
                "consent": firebase_data.get('consent'),
                "verified": firebase_data.get('verified')
            },
            "test_mode": False
        }
    
    # Everything matches - VERIFIED!
    return {
        "verified": True,
        "error": None,
        "match_details": {
            "aadhaar_match": True,
            "record_found": True,
            "name_match": True,
            "overall_verified": True,
            "pan_name": pan_name,
            "firebase_name": firebase_name
        },
        "firebase_data": {
            "name": firebase_data.get('name'),
            "aadhaar_number": str(firebase_data.get('aadhaar_hash') or firebase_data.get('aadhaar_number')),
            "dob": firebase_data.get('dob'),
            "gender": firebase_data.get('gender'),
            "mobile": firebase_data.get('mobile'),
            "data_type": firebase_data.get('data_type'),
            "consent": firebase_data.get('consent'),
            "verified": firebase_data.get('verified')
        },
        "test_mode": False
    }
