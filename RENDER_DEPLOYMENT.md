# Render Deployment Guide for KYC Verification System

## Step 1: Prepare Firebase Credentials

1. Open your `firebase_config.json` file
2. Copy the **entire contents** of the file
3. Minify it to a single line (remove all line breaks and extra spaces)

**Example:**
```json
{"type":"service_account","project_id":"your-project-id","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_x509_cert_url":"..."}
```

## Step 2: Configure Render Environment Variables

In your Render dashboard, add this environment variable:

**Name:** `FIREBASE_CREDENTIALS`  
**Value:** (paste the minified JSON from step 1)

## Step 3: Deployment Configuration

Use these settings in Render:

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Language:** Python 3
- **Branch:** main

## Step 4: Requirements

Ensure your `requirements.txt` includes:
```txt
fastapi==0.128.0
uvicorn[standard]==0.39.0
python-multipart==0.0.9
easyocr==1.7.2
Pillow==10.2.0
firebase-admin==6.5.0
requests==2.32.2
```

## How It Works

The app now supports **two methods** for Firebase credentials:

1. **Environment Variable** (Production/Render):
   - Reads from `FIREBASE_CREDENTIALS` environment variable
   - Perfect for cloud deployment

2. **Config File** (Local Development):
   - Reads from `firebase_config.json` file
   - Keep this file in `.gitignore` for security

## Local Development

For local development, just use your existing `firebase_config.json` file. The app will automatically detect and use it.

## Testing

After deployment:
1. Upload PAN and Aadhaar images
2. Enter any 6-digit OTP
3. Check if Firebase verification works
4. View console logs in Render dashboard

## Troubleshooting

If Firebase doesn't initialize:
- Check that `FIREBASE_CREDENTIALS` is set correctly
- Ensure JSON is valid (no syntax errors)
- Verify Firebase project permissions
- Check Render logs for error messages
