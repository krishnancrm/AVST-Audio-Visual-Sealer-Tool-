import os
import shutil
import subprocess
from PIL import Image

# --- Configuration: Folder Paths ---
RAW_DIR = "Surveillance_Data"
COMPRESSED_OUT = "Sealed_Compressed"
LOSSLESS_OUT = "Sealed_Lossless"
# Source directory for verification (Option 2)
TEST_DIR = "Surveillance_Data" 

# Paths to hardened binaries in the bin folder
BIN_DIR = "bin"
SEALER_EXE = os.path.join(BIN_DIR, "mighty_seal.exe")
AUDITOR_EXE = os.path.join(BIN_DIR, "mighty_decode.exe")
SIGNATURE = "MAC:00:1A:2B|GPS:10.5,76.2"

# Ensure output directories exist
for folder in [COMPRESSED_OUT, LOSSLESS_OUT, RAW_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def apply_whatsapp_wash(lossless_src, compressed_dst):
    """
    Simulates WhatsApp/Social Media compression.
    PNG -> Low Quality JPEG -> PNG
    """
    try:
        img = Image.open(lossless_src)
        temp_jpg = "temp_wash_buffer.jpg"
        # Quality 30 strips L1 grain but tests L2 survival
        img.convert("RGB").save(temp_jpg, "JPEG", quality=30) 
        
        washed_img = Image.open(temp_jpg)
        washed_img.save(compressed_dst, "PNG")
        
        if os.path.exists(temp_jpg):
            os.remove(temp_jpg)
        return True
    except Exception as e:
        print(f"⚠️ Compression failed: {e}")
        return False

def run_option_1():
    print(f"\n--- Option 1: Sealing & Compression Stress Test ---")
    files = [f for f in os.listdir(RAW_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not files:
        print(f"Error: No raw images found in {RAW_DIR}!")
        return

    print(f"{'FILENAME':<35} | {'STATUS'}")
    print("-" * 55)

    for f in files:
        input_path = os.path.join(RAW_DIR, f)
        # Final output names
        out_name = f"{os.path.splitext(f)[0]}_sealed.png"
        lossless_path = os.path.join(LOSSLESS_OUT, out_name)
        compressed_path = os.path.join(COMPRESSED_OUT, out_name)
        
        # 1. ACTUAL SEALING: Reach into /bin to run the C-engine
        # This replaces the old shutil.copy simulation
        result = subprocess.run([SEALER_EXE, input_path, lossless_path, SIGNATURE], capture_output=True)
        
        if result.returncode == 0 and os.path.exists(lossless_path):
            # 2. ACTUAL COMPRESSION: Run the wash logic
            # This achieves the 335KB -> 215KB reduction
            success = apply_whatsapp_wash(lossless_path, compressed_path)
            
            status = "✅ SEALED & WASHED" if success else "⚠️ WASH FAILED"
            print(f"{f:<35} | {status}")
        else:
            print(f"{f:<35} | ❌ SEALING FAILED")

def run_option_2():
    print(f"\n--- Option 2: Verifying Seals in {TEST_DIR} ---")
    files = [f for f in os.listdir(TEST_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not files:
        print(f"No files found in {TEST_DIR} to verify.")
        return
    
    print(f"{'TEST FILE':<35} | {'L1':<4} | {'L2':<4} | {'VERDICT'}")
    print("-" * 95)

    for f in files:
        target_path = os.path.join(TEST_DIR, f)
        
        # 3. ACTUAL AUDIT: Call mighty_decode.exe to scan pixels
        # This replaces the hardcoded (208, 208) simulation
        result = subprocess.run([AUDITOR_EXE, target_path, SIGNATURE], capture_output=True, text=True)
        raw_output = result.stdout.strip()

        # Parse real L1/L2 PASS/FAIL from your binary output
        l1_pass = "PASS" in raw_output.split("|")[0] if "|" in raw_output else False
        l2_pass = "PASS" in raw_output.split("|")[1] if "|" in raw_output else False
        
        l1_icon = "✅" if l1_pass else "❌"
        l2_icon = "✅" if l2_pass else "❌"
        
        # Verify identity presence
        if l2_pass:
            verdict = "AUTHENTIC" + (" (DISTRIBUTED)" if not l1_pass else "")
        else:
            verdict = "UNSEALED / TAMPERED"
            
        print(f"{f:<35} | {l1_icon:<4} | {l2_icon:<4} | {verdict}")

def main():
    print("="*35)
    print("   AVST System Controller v4.0")
    print("="*35)
    print("1. Mirror Stress Test (Process Surveillance_Data)")
    print("2. Assured Seal Verification (Audit Pixels)")
    
    choice = input("\nSelect Option (1 or 2): ")
    if choice == '1': run_option_1()
    elif choice == '2': run_option_2()

if __name__ == "__main__":
    main()
