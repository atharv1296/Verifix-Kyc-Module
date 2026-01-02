# 🔥 Firebase Setup - Step by Step

## Current Status

Your app is running in **TEST MODE** because Firebase credentials are not configured.

- ✅ OCR extraction works
- ❌ Database verification disabled

---

## 📥 Getting Your Firebase Credentials

### Step 1: Go to Firebase Console

Open: https://console.firebase.google.com/

### Step 2: Select Your Project

Click on: **aadhaar-verification-448b8** (or create a new project if needed)

### Step 3: Enable Firestore Database

1. In the left sidebar, click **"Firestore Database"**
2. Click **"Create Database"**
3. Choose **"Start in test mode"** (for development)
4. Select a location (e.g., us-central)
5. Click **"Enable"**

### Step 4: Download Service Account Key

1. Click the **⚙️ gear icon** (Settings) in the left sidebar
2. Click **"Project settings"**
3. Go to the **"Service accounts"** tab
4. Click **"Generate new private key"**
5. Click **"Generate key"** in the popup
6. A JSON file will download (e.g., `aadhaar-verification-448b8-firebase-adminsdk-xxxxx.json`)

### Step 5: Replace firebase_config.json

1. Open the downloaded JSON file in a text editor
2. **Copy ALL the contents**
3. Open `firebase_config.json` in your project
4. **Replace everything** with the copied content
5. Save the file

**Example of what the file should look like:**

```json
{
  "type": "service_account",
  "project_id": "aadhaar-verification-448b8",
  "private_key_id": "abc123def456...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkq...[LONG KEY]...==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@aadhaar-verification-448b8.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/...",
  "universe_domain": "googleapis.com"
}
```

### Step 6: Restart the Server

Stop the server (Ctrl+C) and start again:

```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
✅ Firebase initialized successfully
✅ System ready with Firebase verification enabled
```

---

## 📊 Adding Test Data to Firestore

### Step 1: Generate Hash

Run the helper script:

```bash
python generate_hash.py
```

Copy the **aadhaar_hash** value and the JSON structure.

### Step 2: Add to Firestore

1. Go to Firebase Console → Firestore Database
2. Click **"Start collection"**
3. Collection ID: `users`
4. Click **"Next"**
5. Document ID: **Auto-ID** (or enter custom ID)
6. Click **"Add field"** for each field:

| Field Name | Type | Value |
|------------|------|-------|
| `name` | string | `PRUTHVIRAJ SANTOSH GAVHANE` |
| `aadhaar_hash` | string | *(paste the generated hash)* |
| `aadhaar_last4` | string | `2168` |
| `dob` | string | `15/01/1995` |
| `gender` | string | `male` |
| `mobile` | string | `+919876543210` |
| `verified` | boolean | `false` |
| `consent` | boolean | `true` |
| `data_type` | string | `kyc` |

7. Click **"Save"**

### Step 3: Test Verification

1. Upload PAN and Aadhaar images matching the data
2. System should now show **VERIFIED ✅**

---

## 🔍 Troubleshooting

### Error: "Incorrect padding"

**Problem:** Firebase credentials are still placeholder values

**Solution:** Follow Step 5 above - replace entire content with downloaded JSON

### Error: "Permission denied"

**Problem:** Firestore security rules are too strict

**Solution:** 
1. Go to Firestore → Rules tab
2. For testing, use:
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```
3. Click **"Publish"**

⚠️ **Warning:** This allows all access. Use proper security rules in production!

### Error: "Failed to initialize"

**Problem:** JSON file format is incorrect

**Solution:** 
- Ensure no extra commas at end of lines
- Verify quotes are correct (use double quotes `"`)
- Check that private_key has proper line breaks (`\n`)

### "No matching record found"

**Problem:** Hash doesn't match or collection name is wrong

**Solution:**
- Run `python generate_hash.py` to verify hash
- Check collection name is `users` (lowercase)
- Ensure Aadhaar number in test data matches uploaded image

---

## ✅ Success Indicators

Firebase is correctly configured when you see:

```bash
🚀 KYC VERIFICATION SYSTEM STARTING...
============================================================
⚠️  Firebase config has placeholder values.    # ❌ BEFORE
   → Download actual service account key from Firebase Console
   
✅ Firebase initialized successfully            # ✅ AFTER
✅ System ready with Firebase verification enabled
============================================================
```

---

## 🎯 Quick Reference

| Step | Action | Status |
|------|--------|--------|
| 1 | Go to Firebase Console | [ ] |
| 2 | Create/Select project | [ ] |
| 3 | Enable Firestore | [ ] |
| 4 | Download service account key | [ ] |
| 5 | Replace firebase_config.json | [ ] |
| 6 | Restart server | [ ] |
| 7 | Generate test hash | [ ] |
| 8 | Add data to Firestore | [ ] |
| 9 | Test verification | [ ] |

---

## 📞 Still Need Help?

1. Check the terminal output for specific error messages
2. Review SETUP_GUIDE.md for detailed instructions
3. Run `python test_setup.py` to diagnose issues
4. Ensure Python version is 3.10+ (you're on 3.9.0 - consider upgrading)

---

**Current Python Version Warning:**

You're using Python 3.9.0 which is past its end of life. Consider upgrading to Python 3.10 or later:

```bash
# Download from: https://www.python.org/downloads/
# Then recreate virtual environment:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

**Once Firebase is configured, you'll be able to verify documents against your database! 🎉**
