import re
import numpy as np
from PIL import Image
import easyocr
from datetime import datetime

reader = easyocr.Reader(['en'], gpu=False)

def preprocess_image(pil_img):
    arr = np.array(pil_img.convert('L'))
    arr = np.clip(arr * 1.3, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def ocr_text(pil_img):
    processed = preprocess_image(pil_img)
    results = reader.readtext(np.array(processed), detail=1)
    return [r[1].strip() for r in results if r[1].strip()]

def extract_pan_details(lines):
    """Extract PAN details including name, father's name, and DOB"""
    pan = None
    name = None
    father_name = None
    dob = None
    
    # Extract PAN number
    for line in lines:
        m = re.findall(r'[A-Z]{5}[0-9]{4}[A-Z]', line.replace(" ", ""))
        if m:
            pan = m[0]
            break

    # Extract name (usually the largest text or after "Name" keyword)
    for i, line in enumerate(lines):
        if re.search(r'name', line, re.IGNORECASE) and i + 1 < len(lines):
            name = lines[i + 1].strip()
            break
    
    # If name not found, look for capital letters pattern
    if not name:
        for line in lines:
            if re.match(r'^[A-Z\s]{10,}$', line):
                name = line.strip()
                break
    
    # Extract Father's name
    for i, line in enumerate(lines):
        if re.search(r'father', line, re.IGNORECASE) and i + 1 < len(lines):
            father_name = lines[i + 1].strip()
            break
    
    # Extract DOB (various formats: DD/MM/YYYY, DD-MM-YYYY, etc.)
    for line in lines:
        dob_match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4})', line)
        if dob_match:
            dob = dob_match.group(1)
            break

    return {
        "name": name,
        "father_name": father_name,
        "pan_number": pan,
        "dob": dob
    }

def extract_aadhaar_details(lines):
    """Extract Aadhaar details including name and number"""
    text = " ".join(lines).replace(" ", "")
    aadhaar = next(iter(re.findall(r'\d{12}', text)), None)
    
    name = None
    dob = None
    gender = None
    
    # Extract name from Aadhaar
    for i, line in enumerate(lines):
        # Skip lines with "Government" or "India" or numbers
        if re.search(r'government|india|\d{4,}', line, re.IGNORECASE):
            continue
        # Look for name pattern (capital letters)
        if re.match(r'^[A-Z\s]{10,}$', line):
            name = line.strip()
            break
    
    # Extract DOB
    for line in lines:
        # Look for DOB or Year of Birth
        if re.search(r'dob|birth|yob', line, re.IGNORECASE):
            dob_match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4})', line)
            if dob_match:
                dob = dob_match.group(1)
    
    # Extract Gender
    for line in lines:
        if re.search(r'male|female', line, re.IGNORECASE):
            gender_match = re.search(r'(male|female)', line, re.IGNORECASE)
            if gender_match:
                gender = gender_match.group(1).lower()

    return {
        "aadhaar_number": aadhaar,
        "name": name,
        "dob": dob,
        "gender": gender,
        "vid": None
    }
