"""
Helper script to create Firebase document structure for KYC verification
"""

if __name__ == "__main__":
    print("=" * 50)
    print("FIREBASE DOCUMENT STRUCTURE GENERATOR")
    print("=" * 50)
    
    # Example from your OCR data
    aadhaar = "529690892168"
    
    print(f"\n📊 Input Aadhaar: {aadhaar}")
    print(f"🔢 Last 4 Digits: {aadhaar[-4:]}")
    
    print("\n" + "=" * 50)
    print("FIREBASE DOCUMENT STRUCTURE")
    print("=" * 50)
    
    firebase_doc = {
        "name": "Atharv Saudagar Pawar",
        "aadhaar_hash": 659301385094,  # Store as NUMBER type in Firebase (field name: aadhaar_hash)
        "aadhaar_last4": "5094",
        "dob": "2005-05-28",
        "gender": "Male",
        "mobile": "9518995696",
        "verified": False,
        "consent": True,
        "data_type": "MOCK"
    }
    
    import json
    print("\n📋 Copy this to your Firebase Firestore:\n")
    print(json.dumps(firebase_doc, indent=2))
    
    print("\n" + "=" * 50)
    print("\n✅ To add this to Firebase:")
    print("1. Go to Firebase Console → Firestore Database")
    print("2. Create/Open collection: 'users'")
    print("3. Add a new document")
    print("4. Copy and paste the JSON above")
    print("5. Important: Store 'aadhaar_number' field with full Aadhaar")
    print("\n" + "=" * 50)
