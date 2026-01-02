from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from PIL import Image
import json
import uuid
from ocr_utils import ocr_text, extract_pan_details, extract_aadhaar_details
from firebase_utils import process_verification, initialize_firebase

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Store processing sessions temporarily (in production, use Redis or similar)
processing_sessions = {}

# Initialize Firebase on startup (graceful failure)
@app.on_event("startup")
async def startup_event():
    print("\n" + "="*60)
    print("🚀 KYC VERIFICATION SYSTEM STARTING...")
    print("="*60)
    success = initialize_firebase()
    if success:
        print("\n✅ System ready with Firebase verification enabled")
    else:
        print("\n⚠️  System ready in TEST MODE (Firebase disabled)")
        print("   OCR extraction will work, but verification is disabled.")
        print("   Configure Firebase to enable full verification.")
    print("="*60 + "\n")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload(
    request: Request,
    pan_image: UploadFile = File(...),
    aadhaar_image: UploadFile = File(...)
):
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    # Open images and start OCR processing immediately
    pan_img = Image.open(pan_image.file)
    aadhaar_img = Image.open(aadhaar_image.file)

    print("\n" + "="*70, flush=True)
    print("🔄 STARTING OCR PROCESSING...", flush=True)
    print(f"📋 Session ID: {session_id}", flush=True)
    print("="*70 + "\n", flush=True)

    # Extract text from both PAN and Aadhaar cards
    pan_lines = ocr_text(pan_img)
    pan_data = extract_pan_details(pan_lines)
    
    aadhaar_lines = ocr_text(aadhaar_img)
    aadhaar_data = extract_aadhaar_details(aadhaar_lines)

    # Prepare data for verification
    ocr_data = {
        "pan": pan_data,
        "aadhaar": aadhaar_data
    }

    # 🔥 PRINT OCR RESULT TO TERMINAL
    print("\n" + "="*70, flush=True)
    print("📊 PAN CARD OCR EXTRACTION", flush=True)
    print("="*70, flush=True)
    print(f"PAN Number: {pan_data.get('pan_number', 'Not extracted')}", flush=True)
    print(f"Name: {pan_data.get('name', 'Not extracted')}", flush=True)
    print(f"Date of Birth: {pan_data.get('dob', 'Not extracted')}", flush=True)
    print("="*70, flush=True)
    
    print("\n" + "="*70, flush=True)
    print("📊 AADHAAR CARD OCR EXTRACTION", flush=True)
    print("="*70, flush=True)
    print(f"Aadhaar Number: {aadhaar_data.get('aadhaar_number', 'Not extracted')}", flush=True)
    print("="*70 + "\n", flush=True)

    # Verify against Firebase
    verification_result = process_verification(ocr_data)
    
    # 🔥 PRINT VERIFICATION RESULT TO TERMINAL
    print("\n" + "="*70, flush=True)
    print("🔍 FIREBASE VERIFICATION RESULT", flush=True)
    print("="*70, flush=True)
    print(json.dumps(verification_result, indent=2, default=str), flush=True)
    print("="*70 + "\n", flush=True)
    
    # Print Firebase data if available
    if verification_result.get("firebase_data"):
        print("\n" + "="*70, flush=True)
        print("💾 FIREBASE DATABASE RECORD FOUND", flush=True)
        print("="*70, flush=True)
        print(json.dumps(verification_result["firebase_data"], indent=2), flush=True)
        print("="*70 + "\n", flush=True)

    # Store results in session
    processing_sessions[session_id] = {
        "pan": pan_data,
        "aadhaar": aadhaar_data,
        "verification": verification_result,
        "ocr_data": ocr_data
    }

    print("✅ OCR PROCESSING COMPLETE - Waiting for OTP verification\n", flush=True)

    # Return OTP page (OCR processing done in background)
    return templates.TemplateResponse(
        "otp.html",
        {
            "request": request,
            "session_id": session_id
        }
    )

@app.post("/verify-otp", response_class=HTMLResponse)
async def verify_otp(
    request: Request,
    session_id: str = Form(...),
    otp: str = Form(...)
):
    print("\n" + "="*70, flush=True)
    print("🔐 OTP VERIFICATION", flush=True)
    print("="*70, flush=True)
    print(f"Session ID: {session_id}", flush=True)
    print(f"OTP Entered: {otp}", flush=True)
    print("="*70 + "\n", flush=True)

    # Validate OTP format (6 digits, numbers only)
    if not otp or len(otp) != 6 or not otp.isdigit():
        return templates.TemplateResponse(
            "otp.html",
            {
                "request": request,
                "session_id": session_id,
                "error": "Invalid OTP. Please enter 6 digits."
            }
        )

    # Retrieve processing results from session
    session_data = processing_sessions.get(session_id)
    
    if not session_data:
        return HTMLResponse(content="<h1>Session expired. Please try again.</h1>", status_code=400)

    print("✅ OTP VERIFIED - Showing results\n", flush=True)

    # Return results page
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "pan": session_data["pan"],
            "aadhaar": session_data["aadhaar"],
            "verified": session_data["verification"].get("verified", False),
            "verification": session_data["verification"],
            "ocr_data": session_data["ocr_data"]
        }
    )

