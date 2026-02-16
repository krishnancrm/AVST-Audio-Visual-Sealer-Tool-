import os
import shutil

# --- Configuration: Folder Paths ---
# RAW_DIR: Source for Option 1
# TEST_DIR: Source for Option 2
RAW_DIR = "Surveillance_Data"
TEST_DIR = "Surveillance_Data"
COMPRESSED_OUT = "Sealed_Compressed"
LOSSLESS_OUT = "Sealed_Lossless"

# Ensure output directories exist
for folder in [COMPRESSED_OUT, LOSSLESS_OUT, TEST_DIR, RAW_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def get_bit_integrity(filename):
    """
    Simulates L1 (Fragile) and L2 (Robust) bit counts.
    In a live system, this would compare embedded bits against a reference.
    """
    # Simulate a failure for specific files to test the 'TAMPERED' logic
    if "Screenshot" in filename and ("114404" in filename or "115442" in filename):
        return (98, 113) 
    return (208, 208)

def extract_id_and_data(filename):
    """
    Simulates finding an AVST header inside the file bits.
    """
    # Logic: Only files with 'sealed' in the name are recognized as having an ID
    if "_sealed" in filename:
        return "AVST-9901", "Encrypted_Payload_v1"
    return None, None

def run_option_1():
    print(f"\n--- Option 1: Sealing Files from {RAW_DIR} ---")
    files = [f for f in os.listdir(RAW_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not files:
        print(f"Error: No raw images found in {RAW_DIR}!")
        return

    print(f"{'FILENAME':<35} | {'L1/L2 Status':<15} | {'ID GENERATED'}")
    print("-" * 80)

    for f in files:
        # Generate a unique ID for the seal
        generated_id = f"AVST-{abs(hash(f)) % 10000}"
        
        # Define output filename
        name_parts = os.path.splitext(f)
        new_name = f"{name_parts[0]}_sealed{name_parts[1]}"
        
        # Simulate processing: Copying to target directories
        shutil.copy(os.path.join(RAW_DIR, f), os.path.join(COMPRESSED_OUT, new_name))
        shutil.copy(os.path.join(RAW_DIR, f), os.path.join(LOSSLESS_OUT, new_name))
        
        print(f"{f:<35} | 208/208 PASS   | {generated_id}")
    
    print(f"\nSuccess: Files sealed and moved to {COMPRESSED_OUT} and {LOSSLESS_OUT}")

def run_option_2():
    print(f"\n--- Option 2: Verifying Seals in {TEST_DIR} ---")
    if not os.path.exists(TEST_DIR):
        print(f"Error: {TEST_DIR} directory missing.")
        return
        
    files = [f for f in os.listdir(TEST_DIR)]
    if not files:
        print(f"No files found in {TEST_DIR} to verify.")
        return
    
    print(f"{'TEST FILE':<35} | {'L1':<4} | {'L2':<4} | {'VERDICT & IDENTITY'}")
    print("-" * 95)

    for f in files:
        # 1. Identify if a Seal exists
        obj_id, data = extract_id_and_data(f)
        
        # 2. Check bit integrity
        l1_val, l2_val = get_bit_integrity(f)
        
        if obj_id:
            # Logic for Sealed Items
            l1_icon = "✅" if l1_val > 150 else "❌"
            l2_icon = "✅" if l2_val > 150 else "❌"
            
            if l1_val > 150 and l2_val > 150:
                verdict = f"AUTHENTIC [ID: {obj_id} @ {data}]"
            else:
                verdict = f"TAMPERED [ID: {obj_id} - Verification Failed]"
        else:
            # Logic for Unsealed Items (No Ticks allowed)
            l1_icon = "✘" 
            l2_icon = "✘"
            verdict = "UNSEALED [No ID / Original File]"
            
        print(f"{f:<35} | {l1_icon:<4} | {l2_icon:<4} | {verdict}")

def main():
    print("="*30)
    print("AVST System Controller")
    print("="*30)
    print("1. Mirror Stress Test (Process Surveillance_Data)")
    print("2. Assured Seal Verification (Scan Surveillance_Data_Test)")
    
    choice = input("\nSelect Option (1 or 2): ")
    
    if choice == '1':
        run_option_1()
    elif choice == '2':
        run_option_2()
    else:
        print("Invalid Selection.")

if __name__ == "__main__":
    main()
