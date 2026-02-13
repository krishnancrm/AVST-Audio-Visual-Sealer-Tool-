import os
import cv2
import csv
import time

# Import your compiled binaries (.pyd files)
import encoder
import decoder
import telemetry

# --- PORTABLE PATH LOGIC ---
# This finds the folder where THIS script is saved
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# It expects a 'Screenshots' folder inside your 'ABC' project folder
INPUT_DIR = os.path.join(BASE_DIR, "Screenshots")
OUTPUT_DIR = os.path.join(BASE_DIR, "jigsaw_encoded")
REPORT_FILE = os.path.join(BASE_DIR, "final_forensic_report_batch.csv")

def run_portable_batch():
    # Ensure folders exist
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    if not os.path.exists(INPUT_DIR):
        print(f"[ERROR] Please create a folder named 'Screenshots' at {INPUT_DIR}")
        return

    # Capture Silicon Anchor Session Data
    session_witness = telemetry.get_current_telemetry()
    
    # Intake: Automatically grab all valid image files
    images = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    results = []

    print(f"[LOG] Processing {len(images)} files from: {INPUT_DIR}")

    for i, name in enumerate(images, 1):
        in_p = os.path.join(INPUT_DIR, name)
        out_p = os.path.join(OUTPUT_DIR, f"sealed_{name.split('.')[0]}.jpg")
        
        # 1. ENCODE (The 'Intake' happens here)
        witness_s = encoder.seal_media(in_p, "temp.png", "10")
        
        # 2. ATTACK (Quality 10 Stress Test)
        temp = cv2.imread("temp.png")
        cv2.imwrite(out_p, temp, [int(cv2.IMWRITE_JPEG_QUALITY), 10])
        
        # 3. DECODE (Verification)
        score = decoder.verify_media(out_p, witness_s)
        
        status = "PASS" if score >= 0.65 else "FAIL"
        results.append([name, round(score, 4), status])
        print(f"[{i}/{len(images)}] {name}: {status} ({score:.2%})")

    # Save Results
    with open(REPORT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Filename", "Score", "Status"])
        writer.writerows(results)

if __name__ == "__main__":
    run_portable_batch()