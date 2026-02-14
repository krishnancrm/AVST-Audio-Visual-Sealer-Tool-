import os
import subprocess
from PIL import Image

# Use the same payload string for both layers
SIGNATURE = "MAC:00:1A:2B|GPS:10.5,76.2"
SOURCE_DIR = "Surveillance_Data"
PNG_DIR = "Sealed_Lossless"
JPG_DIR = "Sealed_Compressed"

def run_mirror_test():
    for d in [PNG_DIR, JPG_DIR]:
        if not os.path.exists(d): os.makedirs(d)

    files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:20]
    
    print(f"{'FILENAME':<20} | {'L1 (Fragile)':<20} | {'L2 (Robust)':<20}")
    print("-" * 75)

    for f in files:
        in_p = os.path.join(SOURCE_DIR, f)
        base = os.path.splitext(f)[0]
        png_p = os.path.join(PNG_DIR, f"{base}_lossless.png")
        jpg_p = os.path.join(JPG_DIR, f"{base}_wa_sim.jpg")

        # 1. Seal and simulate WhatsApp/X (Resize to 1600 + Quality 70)
        subprocess.run(["mighty_seal.exe", in_p, png_p, SIGNATURE], capture_output=True)
        with Image.open(png_p) as img:
            img.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
            img.convert("RGB").save(jpg_p, "JPEG", quality=70)

        # 2. Audit Compressed
        dec_jpg = subprocess.run(["mighty_decode.exe", jpg_p, SIGNATURE], capture_output=True, text=True)
        res = dec_jpg.stdout.strip()
        
        # Parse the Two-Layer output
        parts = res.split("|")
        l1 = parts[0].replace("L1_GRAIN:", "").strip()
        l2 = parts[1].replace("L2_GRAIN:", "").strip()
        
        print(f"{f:<20} | {l1:<20} | {l2:<20}")

if __name__ == "__main__":
    run_mirror_test()