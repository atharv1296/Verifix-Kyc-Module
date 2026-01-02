import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate('firebase_config.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()
users_ref = db.collection('users')

print("🔍 Testing Firebase queries for Aadhaar: 659301385094\n")

# Test 1: Query as integer
print("1️⃣ Query: aadhaar_hash == 659301385094 (integer)")
try:
    results = users_ref.where('aadhaar_hash', '==', 659301385094).limit(5).get()
    results_list = list(results)
    print(f"   Results found: {len(results_list)}")
    for doc in results_list:
        print(f"   ✅ Doc ID: {doc.id}")
        print(f"   Data: {doc.to_dict()}\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")

# Test 2: Query as string
print("2️⃣ Query: aadhaar_hash == '659301385094' (string)")
try:
    results = users_ref.where('aadhaar_hash', '==', '659301385094').limit(5).get()
    results_list = list(results)
    print(f"   Results found: {len(results_list)}")
    for doc in results_list:
        print(f"   ✅ Doc ID: {doc.id}")
        print(f"   Data: {doc.to_dict()}\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")

# Test 3: Get all documents
print("3️⃣ Getting all documents in 'users' collection:")
try:
    all_docs = users_ref.limit(10).get()
    all_docs_list = list(all_docs)
    print(f"   Total documents: {len(all_docs_list)}")
    for doc in all_docs_list:
        data = doc.to_dict()
        print(f"   📄 Doc ID: {doc.id}")
        print(f"      aadhaar_hash: {data.get('aadhaar_hash')} (type: {type(data.get('aadhaar_hash')).__name__})")
        print(f"      name: {data.get('name')}\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")
