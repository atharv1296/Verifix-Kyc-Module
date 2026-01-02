# ================== PAN + AADHAAR KYC EXTRACTOR (IMAGE ONLY | VS Code) ==================

import re
import json
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import numpy as np
import easyocr
from datetime import datetime

# ---------------- OCR INITIALIZATION ----------------
print("🔧 Initializing EasyOCR reader (this may take a moment)...")
reader = easyocr.Reader(['en'], gpu=False)
print("✅ OCR ready\n")

# ---------------- IMAGE LOADING ----------------
def load_image(file_path):
    """Load IMAGE ONLY (jpg, png)"""
    try:
        return Image.open(file_path).convert("RGB")
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        return None

# ---------------- PREPROCESSING ----------------
def preprocess_image(pil_img):
    """Enhance image for OCR"""
    arr = np.array(pil_img.convert('L'))
    arr = np.clip(arr * 1.3, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def ocr_text(pil_img):
    """Run OCR"""
    processed = preprocess_image(pil_img)
    results = reader.readtext(np.array(processed), detail=1)
    return [r[1].strip() for r in results if r[1].strip()]

# ---------------- UTILS ----------------
def clean_text(text):
    return re.sub(r'[^A-Z0-9 /\-\.]', '', text.upper()).strip()

def validate_pan(pan):
    return bool(re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan or ""))

def fix_pan_ocr_errors(text):
    text = text.replace(" ", "")
    if len(text) != 10:
        return text

    num_to_char = {'0': 'O', '1': 'I', '2': 'Z', '5': 'S', '8': 'B', '6': 'G'}
    char_to_num = {'O': '0', 'I': '1', 'Z': '2', 'S': '5', 'B': '8', 'G': '6'}

    chars = list(text)
    for i in range(5):
        if chars[i].isdigit():
            chars[i] = num_to_char.get(chars[i], chars[i])
    for i in range(5, 9):
        if chars[i].isalpha():
            chars[i] = char_to_num.get(chars[i], chars[i])
    if chars[9].isdigit():
        chars[9] = num_to_char.get(chars[9], chars[9])

    return "".join(chars)

def validate_date(date_str):
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%d/%m/%Y")
        except:
            pass
    return None

# ---------------- PAN EXTRACTION ----------------
def extract_pan_number(lines):
    for line in lines:
        cleaned = clean_text(line)
        matches = re.findall(r'([A-Z]{5})\s*([0-9]{4})\s*([A-Z])', cleaned)
        for m in matches:
            pan = "".join(m)
            if validate_pan(pan):
                return pan

    joined = "".join(lines).replace(" ", "")
    for c in re.findall(r'[A-Z0-9]{10}', joined):
        fixed = fix_pan_ocr_errors(c)
        if validate_pan(fixed):
            return fixed
    return None

def extract_dob(lines):
    for line in lines:
        dates = re.findall(r'\b\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4}\b', line)
        for d in dates:
            valid = validate_date(d)
            if valid:
                return valid
    return None

def extract_names_from_pan(lines):
    upper = [clean_text(l) for l in lines]
    blacklist = ['INCOME','TAX','GOVERNMENT','INDIA','DEPARTMENT','PAN','DATE','BIRTH']

    father_idx = next((i for i,l in enumerate(upper) if 'FATHER' in l), None)

    father_name = None
    if father_idx is not None and father_idx + 1 < len(upper):
        cand = upper[father_idx + 1]
        if cand.isalpha() and cand not in blacklist:
            father_name = cand

    name = None
    if father_idx:
        for i in range(father_idx - 1, -1, -1):
            cand = upper[i]
            if cand.isalpha() and cand not in blacklist:
                name = cand
                break

    return name, father_name

def extract_pan_details(lines):
    return {
        "document_type": "PAN Card",
        "pan_number": extract_pan_number(lines),
        "name": extract_names_from_pan(lines)[0],
        "father_name": extract_names_from_pan(lines)[1],
        "dob": extract_dob(lines)
    }

# ---------------- AADHAAR EXTRACTION ----------------
def extract_aadhaar_details(lines):
    text = " ".join(lines).replace(" ", "")
    aadhaar = next(iter(re.findall(r'\d{12}', text)), None)
    return {
        "document_type": "Aadhaar Card",
        "aadhaar_number": aadhaar
    }

# ---------------- GUI ----------------
def get_file_path_gui(doc_type):
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title=f"Select {doc_type} Image",
        filetypes=[("Images", "*.jpg *.jpeg *.png")]
    )
    root.destroy()
    return path

# ---------------- MAIN ----------------
if __name__ == "__main__":
    print("\n🏦 KYC DOCUMENT VERIFICATION SYSTEM (IMAGE ONLY)")
    print("="*60)

    pan_path = get_file_path_gui("PAN Card")
    pan_data = None
    if pan_path:
        lines = ocr_text(load_image(pan_path))
        pan_data = extract_pan_details(lines)

    aadhaar_path = get_file_path_gui("Aadhaar Card")
    aadhaar_data = None
    if aadhaar_path:
        lines = ocr_text(load_image(aadhaar_path))
        aadhaar_data = extract_aadhaar_details(lines)

    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pan": pan_data,
        "aadhaar": aadhaar_data
    }

    print(json.dumps(result, indent=2))

    with open("kyc_results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\n💾 Results saved to kyc_results.json")
