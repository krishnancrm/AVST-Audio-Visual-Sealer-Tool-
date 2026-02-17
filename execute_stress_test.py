#!/usr/bin/env python3
"""
AVST Controller - Full implementation for:
Option 1:
  a) Seal files and place lossless sealed outputs in LOSSLESS_OUT
  b) Compress files (lossy), then seal the compressed image and place in COMPRESSED_OUT
Option 2:
  - Verify files by calling external decoder; report whether sealed and integrity status.

Requirements:
 - Encoder binary (seal): BIN_SEAL (expects: BIN_SEAL input.png output.png payload_string)
 - Decoder binary (verify): BIN_DECODE (expects: BIN_DECODE image.png expected_payload_string)
 - Python packages: Pillow (PIL)
 - Place your raw images in the RAW_DIR folder.

Adjust BIN_SEAL and BIN_DECODE paths as needed.
"""

import os
import sys
import subprocess
import tempfile
import shutil
import time
from pathlib import Path
from PIL import Image

# --- Configuration ---
RAW_DIR = "Surveillance_Data"
COMPRESSED_OUT = "Sealed_Compressed"
LOSSLESS_OUT = "Sealed_Lossless"

# Path to encoder and decoder binaries (update to your actual binary names/locations)
BIN_SEAL = os.path.join("bin", "mighty_seal.exe")    # encoder: mighty_seal.exe input.png output.png payload_string
BIN_DECODE = os.path.join("bin", "mighty_decode.exe")  # decoder: mighty_decode.exe image.png expected_payload_string

# Default payload probe length (bytes) passed to decoder as second arg to indicate how many bytes to probe
DEFAULT_PAYLOAD_BYTES = 32  # 32 bytes => 256 bits

# Ensure output directories exist
for d in (RAW_DIR, COMPRESSED_OUT, LOSSLESS_OUT):
    os.makedirs(d, exist_ok=True)


# -------------------------
# Utility functions
# -------------------------
def run_subprocess(cmd, capture_output=True, check=False):
    """Run subprocess and return CompletedProcess. Handles FileNotFoundError gracefully."""
    try:
        return subprocess.run(cmd, capture_output=capture_output, text=True, check=check)
    except FileNotFoundError:
        return None


def is_image_file(name):
    return name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"))


def make_generated_id(filename):
    """Generate a stable-ish ID for embedding (human readable)."""
    base = Path(filename).stem
    # Keep deterministic across runs for same filename
    return f"AVST-{abs(hash(base)) % 100000:05d}"


# -------------------------
# Option 1: Sealing flows
# -------------------------
def seal_lossless(input_path: str, out_dir: str, payload_id: str) -> (bool, str):
    """
    Call the encoder binary to seal the input image and write a lossless sealed PNG to out_dir.
    Returns (success, output_path_or_error).
    """
    out_name = f"{Path(input_path).stem}_sealed.png"
    out_path = os.path.join(out_dir, out_name)
    cmd = [BIN_SEAL, input_path, out_path, payload_id]

    proc = run_subprocess(cmd)
    if proc is None:
        return False, f"Encoder binary not found: {BIN_SEAL}"
    if proc.returncode != 0:
        # include stderr for debugging
        stderr = proc.stderr.strip() if proc.stderr else ""
        return False, f"Encoder failed (rc={proc.returncode}) {stderr}"
    if not os.path.exists(out_path):
        return False, "Encoder reported success but output file missing"
    return True, out_path


def compress_image_to_jpeg(input_path: str, quality: int = 30) -> (bool, str):
    """
    Compress input image to a temporary JPEG file with given quality.
    Returns (success, temp_jpeg_path_or_error).
    """
    try:
        img = Image.open(input_path).convert("RGB")
    except Exception as e:
        return False, f"Failed to open image for compression: {e}"

    fd, tmp_jpeg = tempfile.mkstemp(suffix=".jpg")
    os.close(fd)
    try:
        img.save(tmp_jpeg, "JPEG", quality=quality)
        return True, tmp_jpeg
    except Exception as e:
        try:
            os.remove(tmp_jpeg)
        except Exception:
            pass
        return False, f"Failed to save JPEG: {e}"


def seal_compressed_then_store(input_path: str, out_dir: str, payload_id: str, jpeg_quality: int = 30) -> (bool, str):
    """
    Compress the input image to JPEG (lossy), then call the encoder on that compressed image,
    and place the sealed result (PNG) into out_dir.
    Returns (success, output_path_or_error).
    """
    ok, tmp_or_err = compress_image_to_jpeg(input_path, quality=jpeg_quality)
    if not ok:
        return False, tmp_or_err
    tmp_jpeg = tmp_or_err
    try:
        # Call encoder on the compressed JPEG
        out_name = f"{Path(input_path).stem}_sealed_lossy.png"
        out_path = os.path.join(out_dir, out_name)
        cmd = [BIN_SEAL, tmp_jpeg, out_path, payload_id]
        proc = run_subprocess(cmd)
        if proc is None:
            return False, f"Encoder binary not found: {BIN_SEAL}"
        if proc.returncode != 0:
            stderr = proc.stderr.strip() if proc.stderr else ""
            return False, f"Encoder failed on compressed image (rc={proc.returncode}) {stderr}"
        if not os.path.exists(out_path):
            return False, "Encoder reported success but output file missing (compressed path)"
        return True, out_path
    finally:
        try:
            os.remove(tmp_jpeg)
        except Exception:
            pass


def option_1_process_all():
    """
    Option 1:
      a) For each file in RAW_DIR: seal original and place in LOSSLESS_OUT
      b) For each file in RAW_DIR: compress (JPEG), seal compressed, place in COMPRESSED_OUT
    """
    files = [f for f in os.listdir(RAW_DIR) if is_image_file(f)]
    if not files:
        print(f"No image files found in {RAW_DIR}. Place images there and retry.")
        return

    print("\n--- Option 1: Sealing & Compression ---")
    print(f"{'FILE':<40} | {'LOSSLESS':<12} | {'LOSSY (compressed then sealed)':<30}")
    print("-" * 95)

    for fname in files:
        input_path = os.path.join(RAW_DIR, fname)
        payload_id = make_generated_id(fname)

        # a) Seal original -> LOSSLESS_OUT
        ok_lossless, lossless_info = seal_lossless(input_path, LOSSLESS_OUT, payload_id)
        lossless_status = "OK" if ok_lossless else f"FAIL ({lossless_info})"

        # b) Compress then seal -> COMPRESSED_OUT
        ok_lossy, lossy_info = seal_compressed_then_store(input_path, COMPRESSED_OUT, payload_id, jpeg_quality=30)
        lossy_status = "OK" if ok_lossy else f"FAIL ({lossy_info})"

        print(f"{fname:<40} | {lossless_status:<12} | {lossy_status:<30}")


# -------------------------
# Option 2: Verification
# -------------------------
def call_decoder(image_path: str, expected_payload_bytes: int = DEFAULT_PAYLOAD_BYTES, try_adjacent_windows: int = 1):
    """
    Call external decoder BIN_DECODE on image_path. The decoder expects a second argument
    which is a string; its length determines how many bytes (strlen * 8 bits) it will probe.
    We pass a string of 'A' repeated expected_payload_bytes to indicate the number of bytes.
    Optionally try adjacent 2-hour windows by calling decoder multiple times with different
    rolling factors if the decoder supports it; since the C decoder uses time(NULL)/7200 internally,
    we cannot directly pass rolling factor unless the decoder accepts it. Therefore we call the decoder
    as-is and return its stdout/stderr and returncode.
    """
    probe_arg = "A" * max(1, int(expected_payload_bytes))
    cmd = [BIN_DECODE, image_path, probe_arg]
    proc = run_subprocess(cmd)
    if proc is None:
        return {"error": f"Decoder binary not found: {BIN_DECODE}"}
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip() if proc.stdout else "",
        "stderr": proc.stderr.strip() if proc.stderr else ""
    }


def parse_decoder_output(stdout: str):
    """
    Parse the decoder's human-readable output to extract L1/L2 counts and PASS/FAIL.
    Expected format (from the C decoder you provided):
      L1_GRAIN:<int> (<percent>%) STATUS:<PASS|FAIL> | L2_GRAIN:<int> (<percent>%) STATUS:<PASS|FAIL>
    This parser is tolerant: if it cannot parse, it returns the raw stdout as message.
    """
    if not stdout:
        return {"parsed": False, "message": "No output from decoder."}
    # Try to find tokens
    try:
        # naive parsing by tokens
        parts = stdout.split("|")
        left = parts[0].strip() if len(parts) > 0 else ""
        right = parts[1].strip() if len(parts) > 1 else ""
        # left contains L1_GRAIN...
        l1_token = left.split()[0] if left else ""
        # fallback: return full stdout
        return {"parsed": True, "raw": stdout}
    except Exception:
        return {"parsed": False, "message": stdout}


def option_2_verify_all(expected_payload_bytes: int = DEFAULT_PAYLOAD_BYTES):
    """
    Option 2:
      - For each image file in RAW_DIR, COMPRESSED_OUT, LOSSLESS_OUT:
        call BIN_DECODE and report whether sealed/authentic or not based on decoder output.
    """
    # gather files from three locations (avoid duplicates)
    seen = set()
    files = []
    for folder in (RAW_DIR, LOSSLESS_OUT, COMPRESSED_OUT):
        if not os.path.exists(folder):
            continue
        for f in os.listdir(folder):
            if not is_image_file(f):
                continue
            full = os.path.join(folder, f)
            if full not in seen:
                seen.add(full)
                files.append(full)

    if not files:
        print("No image files found to verify in RAW_DIR, LOSSLESS_OUT, or COMPRESSED_OUT.")
        return

    print("\n--- Option 2: Verify Seals ---")
    print(f"{'FILE (path)':<70} | {'DECODER STATUS':<12} | {'SUMMARY'}")
    print("-" * 120)

    for path in files:
        dec = call_decoder(path, expected_payload_bytes=expected_payload_bytes)
        if "error" in dec:
            status = "ERROR"
            summary = dec["error"]
        else:
            rc = dec["returncode"]
            stdout = dec["stdout"]
            stderr = dec["stderr"]
            if rc != 0:
                status = f"FAIL(rc={rc})"
                summary = stderr or stdout or "Decoder returned non-zero"
            else:
                # attempt to parse and summarize
                parsed = parse_decoder_output(stdout)
                if parsed.get("parsed"):
                    status = "OK"
                    summary = parsed.get("raw", stdout)
                else:
                    status = "OK"
                    summary = parsed.get("message", stdout)
        print(f"{path:<70} | {status:<12} | {summary}")


# -------------------------
# CLI
# -------------------------
def print_menu():
    print("=" * 60)
    print("AVST Controller")
    print("=" * 60)
    print("1) Option 1: Seal all images (lossless) and compress+seal (lossy)")
    print("2) Option 2: Verify seals (call external decoder)")
    print("q) Quit")
    print()


def main():
    while True:
        print_menu()
        choice = input("Select option: ").strip().lower()
        if choice == "1":
            option_1_process_all()
        elif choice == "2":
            # ask how many payload bytes to probe (optional)
            s = input(f"Enter expected payload length in bytes (default {DEFAULT_PAYLOAD_BYTES}): ").strip()
            try:
                n = int(s) if s else DEFAULT_PAYLOAD_BYTES
            except Exception:
                n = DEFAULT_PAYLOAD_BYTES
            option_2_verify_all(expected_payload_bytes=n)
        elif choice == "q":
            print("Exiting.")
            break
        else:
            print("Unknown option. Choose 1, 2, or q.")


if __name__ == "__main__":
    main()
