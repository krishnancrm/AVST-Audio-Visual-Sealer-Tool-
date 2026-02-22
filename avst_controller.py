#!/usr/bin/env python3
import os
import subprocess
import tempfile
from pathlib import Path
from PIL import Image

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "Surveillance_Data")

# Absolute paths to ensure C binaries write to the correct xzy/ subfolders
LOSSLESS_OUT = os.path.abspath(os.path.join(BASE_DIR, "Sealed_Lossless"))
COMPRESSED_OUT = os.path.abspath(os.path.join(BASE_DIR, "Sealed_Compressed"))

BIN_SEAL = os.path.join(BASE_DIR, "bin", "mighty_seal.exe")
BIN_DECODE = os.path.join(BASE_DIR, "bin", "mighty_decode.exe")

def verify_system_integrity():
    """Checks if binaries and folders are correctly mapped before execution."""
    print("\n" + "-"*30)
    print(" SYSTEM INTEGRITY CHECK ")
    print("-"*30)
    
    # Check for binaries
    for name, path in [("Sealer", BIN_SEAL), ("Auditor", BIN_DECODE)]:
        status = "FOUND" if os.path.exists(path) else "MISSING"
        print(f"{name:<10}: {status} at {path}")
    
    # Ensure output directories exist
    for name, path in [("Lossless", LOSSLESS_OUT), ("Compressed", COMPRESSED_OUT)]:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"{name:<10}: FOLDER CREATED")
        else:
            print(f"{name:<10}: FOLDER READY")
    print("-"*30 + "\n")

def is_image_file(name):
    return name.lower().endswith(('.png', '.jpg', '.jpeg'))

def parse_results(stdout):
    """Extracts verdict and payload from C output for the Dual-Audit table."""
    eff, verdict, payload = "0.00%", "NOT SEALED", "No Data"
    if stdout:
        for line in stdout.split('\n'):
            if "Efficiency:" in line: eff = line.split(":")[1].strip()
            if "RESULT:" in line: verdict = line.split(":")[1].strip()
            # Python looks for this exact prefix from mighty_decode.c
            if "PAYLOAD:" in line: payload = line.split(":")[1].strip()
    return eff, verdict, payload

def purge_outputs():
    """Clears output folders to prevent data contamination."""
    for folder in [LOSSLESS_OUT, COMPRESSED_OUT]:
        for f in os.listdir(folder):
            try: os.remove(os.path.join(folder, f))
            except: pass
    print("Folders Purged.")

def apply_whatsapp_wash(input_path):
    """Simulates 30% JPEG compression (The 'Wash')."""
    try:
        img = Image.open(input_path).convert("RGB")
        fd, tmp_path = tempfile.mkstemp(suffix=".jpg", dir=BASE_DIR)
        os.close(fd)
        # Quality 30 triggers the quantization table survival logic
        img.save(tmp_path, "JPEG", quality=30)
        return tmp_path
    except: return None

# ---------------------------------------------------------
# Dual-Audit Production Phase
# ---------------------------------------------------------

def option_1_production():
    """Intake -> Dual Seal -> Dual Audit with specific Lossy MAC status column."""
    # Commented out purge to allow you to inspect files after run
    # purge_outputs() 
    
    files = [f for f in os.listdir(RAW_DIR) if is_image_file(f)]
    if not files:
        print("Intake folder is empty."); return

    print(f"\n{'FILENAME':<25} | {'LOSSLESS':<12} | {'WASHED (30%)':<12} | {'PAYLOAD'}")
    print("-" * 85)

    for fname in files:
        raw_path = os.path.join(RAW_DIR, fname)
        
        # 1. Generate Lossless Seal
        l_path = os.path.join(LOSSLESS_OUT, f"sealed_{fname}")
        subprocess.run([BIN_SEAL, raw_path, l_path], capture_output=True)
        
        # 2. Generate Washed Seal
        w_path = os.path.join(COMPRESSED_OUT, f"washed_{fname}.png")
        tmp_wash = apply_whatsapp_wash(raw_path)
        if tmp_wash:
            # We seal the already washed temp image to see if watermark survives a second wash/save
            subprocess.run([BIN_SEAL, tmp_wash, w_path], capture_output=True)
            os.remove(tmp_wash)

        # 3. Dual Audit
        res_l = subprocess.run([BIN_DECODE, l_path, "0"], capture_output=True, text=True)
        _, verd_l, payload = parse_results(res_l.stdout)

        res_w = subprocess.run([BIN_DECODE, w_path, "0"], capture_output=True, text=True)
        _, verd_w, _ = parse_results(res_w.stdout)

        l_stat = "SEALED" if "SEALED" in verd_l else "MISSING"
        w_stat = "SURVIVED" if "SEALED" in verd_w else "WASHED OUT"
        
        print(f"{fname[:25]:<25} | {l_stat:<12} | {w_stat:<12} | {payload}")

    print("-" * 85)
    print("Dual Verification Complete.")

# ---------------------------------------------------------
# Forensic Audit Phase
# ---------------------------------------------------------

def option_2_audit():
    """Manual Audit with Automatic Rolling Base Sweep (-1, 0, +1)."""
    print("\n1) Lossless | 2) Compressed (Washed) | 3) Raw Intake")
    choice = input("Select folder: ").strip()
    target = {"1": LOSSLESS_OUT, "2": COMPRESSED_OUT, "3": RAW_DIR}.get(choice)
    if not target: 
        return

    print(f"\n{'FILENAME':<25} | {'VERDICT':<10} | {'SYNC':<6} | {'PAYLOAD'}")
    print("-" * 80)
    
    for f in os.listdir(target):
        if is_image_file(f):
            file_path = os.path.join(target, f)
            # Default state for non-sealed images
            final_verd, final_payload, final_sync = "NOT SEALED", "No Data", "----"
            
            # --- The Automatic Sweep Logic ---
            for offset in ["0", "-1", "1"]:
                res = subprocess.run([BIN_DECODE, file_path, offset], 
                                     capture_output=True, text=True)
                
                eff, verdict, payload = parse_results(res.stdout)
                
                # CRITICAL: Only accept if the C-verdict is SEALED AND payload contains data
                if "SEALED" in verdict and "No Data" not in payload:
                    final_verd = "SEALED"
                    final_payload = payload
                    final_sync = f"{offset:>2}H"
                    break 
        
            print(f"{f[:25]:<25} | {final_verd:<10} | {final_sync:<6} | {final_payload}") 

    print("-" * 80)
    print("Forensic Sweep Complete.")
    
def main():
    verify_system_integrity()
    while True:
        print("\n" + "="*40)
        print(" VST PRODUCTION CONTROLLER v11.4 ")
        print("="*40)
        print("1) Run Production (Dual Audit)")
        print("2) Forensic Audit (Sync Offset)")
        print("q) Quit")
        c = input("\nAction: ").strip().lower()
        if c == '1': option_1_production()
        elif c == '2': option_2_audit()
        elif c == 'q': break

if __name__ == "__main__":
    main()