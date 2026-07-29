from pathlib import Path
import struct
import csv
import math
import os
import hashlib
import time
import sys
import zipfile
import tarfile
import gzip
import bz2

# Enable ANSI colors on Windows terminals
os.system("")

# Console colors
RESET = "\033[0m"
BOLD = "\033[1m"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"


def RGB(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"


INTERVAL_TYPES = ["fs", "ps", "ns", "us", "ms", "s", "min", "hour"]

# Magic bytes for common file format detection
MAGIC_SIGNATURES = [
    (b"\x50\x4B\x03\x04", "ZIP archive / Office document"),
    (b"\x50\x4B\x05\x06", "ZIP archive (empty)"),
    (b"\x25\x50\x44\x46", "PDF document"),
    (b"\x4D\x5A",         "Windows EXE / DLL"),
    (b"\x7F\x45\x4C\x46", "ELF executable (Linux)"),
    (b"\xFF\xD8\xFF",     "JPEG image"),
    (b"\x89\x50\x4E\x47", "PNG image"),
    (b"\x47\x49\x46\x38", "GIF image"),
    (b"\x42\x4D",         "BMP image"),
    (b"\x49\x44\x33",     "MP3 audio (ID3 tag)"),
    (b"\xFF\xFB",         "MP3 audio"),
    (b"\x52\x49\x46\x46", "RIFF container (WAV/AVI)"),
    (b"\x00\x00\x01\xBA", "MPEG video"),
    (b"\x00\x00\x01\xB3", "MPEG video"),
    (b"\x1F\x8B",         "GZIP compressed"),
    (b"\x42\x5A\x68",     "BZIP2 compressed"),
    (b"\xFD\x37\x7A\x58", "XZ compressed"),
    (b"\x37\x7A\xBC\xAF", "7-Zip archive"),
    (b"\x52\x61\x72\x21", "RAR archive"),
    (b"\xD0\xCF\x11\xE0", "MS Office legacy (DOC/XLS/PPT)"),
    (b"\xEF\xBB\xBF",     "UTF-8 text with BOM"),
    (b"\xFF\xFE",         "UTF-16 LE text"),
    (b"\xFE\xFF",         "UTF-16 BE text"),
    (b"\x53\x51\x4C\x69", "SQLite database"),
    (b"\x4D\x54\x68\x64", "MIDI audio"),
]

# Compression ratio threshold for ZIP bomb warning
BOMB_RATIO_THRESHOLD = 100
BOMB_SIZE_THRESHOLD = 1 * 1024 * 1024 * 1024  # 1 GB uncompressed


# ------------------------------------------------------------
# Console helpers
# ------------------------------------------------------------

def success(text):
    print(f"{GREEN}{text}{RESET}")


def error(text):
    print(f"{RED}{text}{RESET}")


def warning(text):
    print(f"{YELLOW}{text}{RESET}")


def info(text):
    print(f"{CYAN}{text}{RESET}")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\nPress ENTER to continue...")


# ------------------------------------------------------------
# Fake loading helpers
# ------------------------------------------------------------

def fake_loading_bar(text="Loading", duration=1.0, steps=20):
    print()
    print(f"{CYAN}{text}{RESET}")
    print(f"{CYAN}[{RESET}", end="", flush=True)

    step_time = duration / steps

    for i in range(steps):
        time.sleep(step_time)
        print(f"{RGB(0, 153, 255)}█{RESET}", end="", flush=True)

    print(f"{CYAN}]{RESET} ", end="")
    success("Done")
    print()


def fake_typing(text, delay=0.03, color=None):
    if color:
        print(color, end="", flush=True)

    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)

    if color:
        print(RESET, end="", flush=True)

    print()


def fake_scanning(lines, delay=0.08):
    for line in lines:
        time.sleep(delay)
        print(f"  {CYAN}>{RESET} {line}")


def fake_dots(text="Processing", dots=5, delay=0.3):
    print(f"\n{CYAN}{text}{RESET}", end="", flush=True)

    for _ in range(dots):
        time.sleep(delay)
        print(f"{CYAN}.{RESET}", end="", flush=True)

    print()


# ------------------------------------------------------------
# Banner
# ------------------------------------------------------------

def print_banner():
    print(f"{RGB(255, 255, 255)}=================================================================={RESET}")
    print(f"{RGB(220, 242, 255)}██╗  ██╗███████╗██╗  ██╗        ███████╗██╗   ██╗███████╗{RESET}")
    print(f"{RGB(190, 230, 255)}██║  ██║██╔════╝╚██╗██╔╝        ██╔════╝╚██╗ ██╔╝██╔════╝{RESET}")
    print(f"{RGB(150, 215, 255)}███████║█████╗   ╚███╔╝         █████╗   ╚████╔╝ █████╗  {RESET}")
    print(f"{RGB(105, 198, 255)}██╔══██║██╔══╝   ██╔██╗         ██╔══╝    ╚██╔╝  ██╔══╝  {RESET}")
    print(f"{RGB(65, 180, 255)}██║  ██║███████╗██╔╝ ██╗███████╗███████╗   ██║   ███████╗{RESET}")
    print(f"{RGB(25, 165, 255)}╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝   ╚══════╝{RESET}")
    print(f"{RGB(0, 153, 255)}               File inspection & hex analysis{RESET}")
    print(f"{RGB(0, 153, 255)}=================================================================={RESET}")


def startup_sequence():
    clear_screen()
    print_banner()
    print()
    fake_typing("  Initializing HEX_EYE...", delay=0.04, color=CYAN)
    fake_scanning([
        "Loading binary read modules",
        "Loading hex analysis engine",
        "Loading string extractor",
        "Loading entropy calculator",
        "Loading hash modules",
        "Loading format signatures",
        "Loading archive inspection engine",
        "Loading help tips",
    ], delay=0.15)
    fake_loading_bar("  Starting up", duration=1.2, steps=30)
    fake_typing("  HEX_EYE is ready.", delay=0.04, color=GREEN)
    time.sleep(0.5)


# ------------------------------------------------------------
# Binary read helpers
# ------------------------------------------------------------

def read_u16_le(data, offset):
    return struct.unpack_from("<H", data, offset)[0]


def read_u32_le(data, offset):
    return struct.unpack_from("<I", data, offset)[0]


def read_f32_le(data, offset):
    return struct.unpack_from("<f", data, offset)[0]


def safe_read_u16(data, offset):
    if offset + 2 > len(data):
        return None
    return struct.unpack_from("<H", data, offset)[0]


def safe_read_u32(data, offset):
    if offset + 4 > len(data):
        return None
    return struct.unpack_from("<I", data, offset)[0]


def safe_read_i32(data, offset):
    if offset + 4 > len(data):
        return None
    return struct.unpack_from("<i", data, offset)[0]


def safe_read_f32(data, offset):
    if offset + 4 > len(data):
        return None
    value = struct.unpack_from("<f", data, offset)[0]
    if math.isfinite(value):
        return value
    return None


def printable_ascii(byte_data):
    return "".join(chr(b) if 32 <= b <= 126 else "." for b in byte_data)


def count_nonzero_bytes(data):
    return len(data) - data.count(0)


def read_file_bytes(path):
    try:
        return path.read_bytes()
    except Exception as e:
        error("ERROR: Could not read file.")
        print(e)
        return None


# ------------------------------------------------------------
# User input
# ------------------------------------------------------------

def get_file_path_from_user():
    print()
    print("Enter the full path to the file you want to inspect.")
    print("Any file type is accepted.")
    print()
    print("Example:")
    print(r"  C:\workspace\data\mydata.bin")
    print(r"  C:\workspace\data\mydata.PLW")
    print(r"  C:\workspace\data\archive.zip")
    print()

    file_path = input("File path: ").strip().strip('"')

    if not file_path:
        warning("No file path entered.")
        return None

    path = Path(file_path).resolve()

    if not path.exists():
        print()
        error("ERROR: File not found.")
        print(path)
        return None

    if not path.is_file():
        print()
        error("ERROR: Path is not a file.")
        print(path)
        return None

    return path


# ------------------------------------------------------------
# Magic byte detection
# ------------------------------------------------------------

def detect_magic_bytes(data):
    for magic, description in MAGIC_SIGNATURES:
        if data[:len(magic)] == magic:
            return description
    return None


# ------------------------------------------------------------
# General inspection helpers
# ------------------------------------------------------------

def is_mostly_text(data, sample_size=4096):
    sample = data[:sample_size]

    if not sample:
        return False, 0.0

    text_chars = sum(1 for b in sample if b in (9, 10, 13) or 32 <= b <= 126)
    ratio = text_chars / len(sample)
    return ratio > 0.85, ratio


def extract_readable_strings(data, min_length=4, max_strings=40):
    strings = []
    current = bytearray()

    for b in data:
        if 32 <= b <= 126:
            current.append(b)
        else:
            if len(current) >= min_length:
                strings.append(current.decode("ascii", errors="replace"))
                if len(strings) >= max_strings:
                    break
            current = bytearray()

    if len(current) >= min_length and len(strings) < max_strings:
        strings.append(current.decode("ascii", errors="replace"))

    return strings


def inspect_possible_float32_values(data, max_values=20):
    values = []
    limit = min(len(data), 4096)

    for offset in range(0, limit - 4, 4):
        value = safe_read_f32(data, offset)

        if value is None:
            continue

        if -1_000_000 <= value <= 1_000_000 and abs(value) > 1e-12:
            values.append((offset, value))

        if len(values) >= max_values:
            break

    return values


def inspect_possible_int16_values(data, max_values=20):
    values = []
    limit = min(len(data), 4096)

    for offset in range(0, limit - 2, 2):
        value = struct.unpack_from("<h", data, offset)[0]

        if value != 0:
            values.append((offset, value))

        if len(values) >= max_values:
            break

    return values


def format_size(size_bytes):
    if size_bytes >= 1024 ** 3:
        return f"{size_bytes / (1024 ** 3):.2f} GB"
    elif size_bytes >= 1024 ** 2:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes} bytes"


# ------------------------------------------------------------
# Option 1: Deep byte check
# ------------------------------------------------------------

def check_nonzero_blocks(path):
    block_size = 1024 * 1024

    try:
        file_size = path.stat().st_size
    except Exception as e:
        error("ERROR: Could not access file information.")
        print(e)
        return False

    total_nonzero = 0
    first_nonzero = None
    last_nonzero = None

    print()
    info("Deep Byte Check")
    print("===============")
    print()
    print("File:", path)
    print("Size:", file_size, "bytes")
    print()

    try:
        with path.open("rb") as f:
            offset = 0

            while True:
                block = f.read(block_size)

                if not block:
                    break

                block_nonzero = len(block) - block.count(0)

                if block_nonzero:
                    for i, b in enumerate(block):
                        if b != 0:
                            absolute = offset + i

                            if first_nonzero is None:
                                first_nonzero = absolute

                            last_nonzero = absolute

                    print(f"Block at offset {offset}: {block_nonzero} non-zero bytes")

                total_nonzero += block_nonzero
                offset += len(block)

    except Exception as e:
        error("ERROR: Could not read file.")
        print(e)
        return False

    print()
    print("Total non-zero bytes :", total_nonzero)
    print("First non-zero offset:", first_nonzero)
    print("Last non-zero offset :", last_nonzero)

    if total_nonzero == 0:
        print()
        warning("RESULT: This file contains only zero bytes.")
        warning("No meaningful data can be extracted.")
        return False

    print()
    success("RESULT: This file contains data.")
    return True


# ------------------------------------------------------------
# Option 2: Full file inspection
# ------------------------------------------------------------

def full_file_inspection(path):
    print()
    info("Full File Inspection")
    print("====================")
    print()
    print("File:", path)

    data = read_file_bytes(path)

    if data is None:
        return

    file_size = len(data)
    nonzero = count_nonzero_bytes(data)

    # --- Basic info ---
    print()
    print(f"{RGB(150, 215, 255)}[ Basic Info ]{RESET}")
    print("-" * 40)
    print("File name  :", path.name)
    print("Extension  :", path.suffix if path.suffix else "(none)")
    print("Size       :", file_size, "bytes")
    print("Non-zero   :", nonzero, "bytes")
    print("Zero bytes :", file_size - nonzero, "bytes")

    if file_size > 0:
        print("Data ratio :", round(nonzero / file_size * 100, 2), "%")

    if nonzero == 0:
        print()
        warning("RESULT: This file contains only zero bytes.")
        warning("No meaningful data can be extracted.")
        return

    # --- Magic byte detection ---
    print()
    print(f"{RGB(150, 215, 255)}[ Format Detection ]{RESET}")
    print("-" * 40)

    magic_result = detect_magic_bytes(data)

    if magic_result:
        success(f"Magic bytes match: {magic_result}")
    else:
        warning("No known magic bytes detected.")
        print("File may be a proprietary, custom, or raw binary format.")

    # --- Text detection ---
    mostly_text, text_ratio = is_mostly_text(data)
    print()
    print(f"Text-like ratio: {round(text_ratio * 100, 2)}%")

    if mostly_text:
        success("File appears to be mostly text-based.")
    else:
        info("File appears to be binary.")

    # --- Hex preview ---
    print()
    print(f"{RGB(150, 215, 255)}[ Hex Preview — First 256 Bytes ]{RESET}")
    print("-" * 40)

    for i in range(0, min(256, file_size), 16):
        chunk = data[i:i + 16]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        text_part = printable_ascii(chunk)
        print(f"  {i:08x}  {hex_part:<47}  {text_part}")

    # --- Readable strings ---
    print()
    print(f"{RGB(150, 215, 255)}[ Readable Strings (first 30) ]{RESET}")
    print("-" * 40)

    strings = extract_readable_strings(data, min_length=4, max_strings=30)

    if strings:
        for i, s in enumerate(strings, start=1):
            print(f"  {i:02d}: {s}")
    else:
        print("  No readable strings found.")

    # --- Numeric probing ---
    print()
    print(f"{RGB(150, 215, 255)}[ Numeric Probe — float32 near start ]{RESET}")
    print("-" * 40)

    float_values = inspect_possible_float32_values(data)

    if float_values:
        for offset, value in float_values:
            print(f"  Offset {offset:8d}: {value}")
    else:
        print("  No obvious float32 values found near the start.")

    print()
    print(f"{RGB(150, 215, 255)}[ Numeric Probe — int16 near start ]{RESET}")
    print("-" * 40)

    int_values = inspect_possible_int16_values(data)

    if int_values:
        for offset, value in int_values:
            print(f"  Offset {offset:8d}: {value}")
    else:
        print("  No obvious int16 values found near the start.")

    # --- Entropy estimate ---
    print()
    print(f"{RGB(150, 215, 255)}[ Byte Frequency / Entropy Estimate ]{RESET}")
    print("-" * 40)

    sample = data[:4096]
    byte_counts = [0] * 256

    for b in sample:
        byte_counts[b] += 1

    unique_bytes = sum(1 for c in byte_counts if c > 0)
    most_common = max(range(256), key=lambda i: byte_counts[i])
    most_common_count = byte_counts[most_common]

    entropy = 0.0
    for c in byte_counts:
        if c > 0:
            p = c / len(sample)
            entropy -= p * math.log2(p)

    print(f"  Unique byte values : {unique_bytes} / 256")
    print(f"  Most common byte   : 0x{most_common:02x} ({most_common_count} times in first 4096 bytes)")
    print(f"  Shannon entropy    : {entropy:.4f} bits/byte")

    if entropy > 7.5:
        warning("High entropy — file may be encrypted or compressed.")
    elif entropy > 5.0:
        info("Medium entropy — likely a structured binary format.")
    else:
        success("Low entropy — likely plain text or simple structured data.")

    # --- Summary ---
    print()
    print(f"{RGB(150, 215, 255)}[ Summary ]{RESET}")
    print("-" * 40)

    if magic_result:
        print(f"  Detected format : {magic_result}")
    elif mostly_text:
        print("  Detected format : Text-based (no magic bytes)")
    else:
        print("  Detected format : Unknown binary")

    print(f"  File size       : {file_size} bytes")
    print(f"  Data ratio      : {round(nonzero / file_size * 100, 2)}%")
    print(f"  Entropy         : {entropy:.4f} bits/byte")

    if magic_result and "ZIP" in magic_result:
        print()
        info("TIP: This looks like a ZIP file. Use option [8] to inspect the archive contents.")


# ------------------------------------------------------------
# Option 3: Hex viewer
# ------------------------------------------------------------

def hex_viewer(path):
    print()
    info("Hex Viewer")
    print("==========")
    print()
    print("File:", path)

    data = read_file_bytes(path)

    if data is None:
        return

    file_size = len(data)

    if file_size == 0:
        warning("File is empty.")
        return

    print(f"File size: {file_size} bytes")
    print()
    print("How many bytes to view from the start?")
    print("Default is 512. Max is the full file size.")
    print()

    try:
        user_input = input("Bytes to view [512]: ").strip()
        view_size = int(user_input) if user_input else 512
        view_size = max(16, min(view_size, file_size))
    except ValueError:
        view_size = 512

    print()
    print(f"{RGB(150, 215, 255)}Hex dump — first {view_size} bytes:{RESET}")
    print()
    print(f"  {'Offset':<10}  {'Hex':47}  {'Text'}")
    print(f"  {'-'*10}  {'-'*47}  {'-'*16}")

    for i in range(0, view_size, 16):
        chunk = data[i:i + 16]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        text_part = printable_ascii(chunk)
        print(f"  {i:08x}  {hex_part:<47}  {text_part}")


# ------------------------------------------------------------
# Option 4: Extract readable strings
# ------------------------------------------------------------

def extract_strings_to_txt(path):
    print()
    info("Extract Readable Strings")
    print("=========================")

    data = read_file_bytes(path)

    if data is None:
        return

    if count_nonzero_bytes(data) == 0:
        print()
        warning("RESULT: File contains only zero bytes.")
        warning("Nothing useful can be extracted.")
        return

    strings = extract_readable_strings(data, min_length=4, max_strings=100000)

    output_path = path.with_suffix(".strings.txt")

    try:
        with output_path.open("w", encoding="utf-8", errors="replace") as f:
            f.write("Readable strings extracted by HEX_EYE\n")
            f.write(f"Source file: {path}\n\n")

            for s in strings:
                f.write(s)
                f.write("\n")

        print()
        success(f"Strings extracted: {len(strings)}")
        print("Output file:", output_path)

    except Exception as e:
        print()
        error("ERROR: Could not write output file.")
        print(e)


# ------------------------------------------------------------
# Option 5: Export raw numeric guesses
# ------------------------------------------------------------

def export_raw_numeric_guesses(path):
    print()
    info("Export Raw Numeric Guesses")
    print("===========================")
    print()
    warning("WARNING: These are raw guesses, not confirmed data.")
    print("This creates CSV files with all possible numeric interpretations.")
    print("Use these files for investigation only.")
    print()

    try:
        file_size = path.stat().st_size
    except Exception as e:
        error("ERROR: Could not access file information.")
        print(e)
        return

    if file_size > 50 * 1024 * 1024:
        warning("WARNING: This file is larger than 50 MB.")
        print("Raw numeric export may create very large CSV files.")
        confirm = input("Continue? [Y/N]: ").strip().lower()

        if confirm != "y":
            warning("Export cancelled.")
            return

    data = read_file_bytes(path)

    if data is None:
        return

    if count_nonzero_bytes(data) == 0:
        warning("RESULT: File contains only zero bytes. Nothing to export.")
        return

    float_output = path.with_suffix(".raw_float32.csv")
    int16_output = path.with_suffix(".raw_int16.csv")
    int32_output = path.with_suffix(".raw_int32.csv")

    try:
        with float_output.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["offset", "float32_little_endian"])

            for offset in range(0, len(data) - 4, 4):
                value = safe_read_f32(data, offset)
                if value is None:
                    continue
                writer.writerow([offset, value])

        with int16_output.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["offset", "int16_little_endian", "value_div_10", "value_div_100"])

            for offset in range(0, len(data) - 2, 2):
                raw = struct.unpack_from("<h", data, offset)[0]
                writer.writerow([offset, raw, raw / 10.0, raw / 100.0])

        with int32_output.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["offset", "int32_little_endian"])

            for offset in range(0, len(data) - 4, 4):
                raw = safe_read_i32(data, offset)
                if raw is not None:
                    writer.writerow([offset, raw])

        print()
        success("Raw numeric files created:")
        print(" ", float_output)
        print(" ", int16_output)
        print(" ", int32_output)

        print()
        warning("Reminder: These are raw guesses only.")
        print("Look for columns with realistic values such as temperatures, counters, or timestamps.")

    except Exception as e:
        print()
        error("ERROR: Could not export raw numeric guesses.")
        print(e)


# ------------------------------------------------------------
# Option 6: Calculate file hash
# ------------------------------------------------------------

def calculate_file_hash(path):
    print()
    info("File Hash Calculator")
    print("====================")

    block_size = 1024 * 1024

    try:
        file_size = path.stat().st_size
    except Exception as e:
        error("ERROR: Could not access file information.")
        print(e)
        return

    print()
    print("File     :", path)
    print("Size     :", file_size, "bytes")
    print()

    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()

    try:
        with path.open("rb") as f:
            while True:
                block = f.read(block_size)
                if not block:
                    break
                md5.update(block)
                sha1.update(block)
                sha256.update(block)

    except Exception as e:
        error("ERROR: Could not read file.")
        print(e)
        return

    print(f"{'MD5':<8}: ", end="")
    success(md5.hexdigest())

    print(f"{'SHA1':<8}: ", end="")
    success(sha1.hexdigest())

    print(f"{'SHA256':<8}: ", end="")
    success(sha256.hexdigest())

    print()
    print("Use these hashes to verify file integrity or compare files across machines.")
    print("Identical hash = identical file contents.")


# ------------------------------------------------------------
# Option 7: PicoLog-style file to CSV (bonus)
# ------------------------------------------------------------

def convert_plw_to_csv(path):
    output_path = path.with_suffix(".csv")

    data = read_file_bytes(path)

    if data is None:
        return False

    file_size = len(data)

    print()
    info("PicoLog-style File to CSV Converter")
    print("=====================================")
    print()
    print("Input file:", path)
    print("File size :", file_size, "bytes")

    nonzero_count = count_nonzero_bytes(data)
    print("Non-zero  :", nonzero_count, "bytes")

    if nonzero_count == 0:
        print()
        error("ERROR: File contains only zero bytes. No data can be converted.")
        return False

    if file_size < 1684:
        print()
        error("ERROR: File is too small to be a valid PicoLog-style file.")
        return False

    try:
        header_size = read_u16_le(data, 0)
        signature = data[2:42]
        header_version = read_u32_le(data, 42)
        num_channels = read_u32_le(data, 46)
        sample_count_1 = read_u32_le(data, 550)
        sample_count_2 = read_u32_le(data, 554)

        if sample_count_1 > 0 and sample_count_2 > 0:
            last_sample = min(sample_count_1, sample_count_2)
        else:
            last_sample = max(sample_count_1, sample_count_2)

        interval = read_u32_le(data, 562)
        timing_units_u16 = read_u16_le(data, 566)
        timing_units_u32 = read_u32_le(data, 566)

        if 0 <= timing_units_u16 < len(INTERVAL_TYPES):
            timing_units = timing_units_u16
        else:
            timing_units = timing_units_u32

    except Exception as e:
        print()
        error("ERROR: Could not read header.")
        print(e)
        return False

    print()
    print("Detected header fields:")
    print("-----------------------")
    print("Header size       :", header_size)
    print("Signature         :", printable_ascii(signature))
    print("Header version    :", header_version)
    print("Number of channels:", num_channels)
    print("Sample count 1    :", sample_count_1)
    print("Sample count 2    :", sample_count_2)
    print("Using sample count:", last_sample)
    print("Interval          :", interval)

    if 0 <= timing_units < len(INTERVAL_TYPES):
        print("Timing units      :", timing_units, INTERVAL_TYPES[timing_units])
    else:
        print("Timing units      :", timing_units, "(unknown)")

    if header_size <= 0 or header_size >= file_size:
        print()
        error(f"ERROR: Header size looks invalid: {header_size}")
        return False

    if header_version < 1 or header_version > 20:
        print()
        error(f"ERROR: Header version looks invalid: {header_version}")
        return False

    if num_channels <= 0 or num_channels > 100:
        print()
        error(f"ERROR: Number of channels looks invalid: {num_channels}")
        return False

    record_size = 4 * (num_channels + 1)
    possible_records = (file_size - header_size) // record_size
    records_to_read = min(last_sample, possible_records)

    print("Record size       :", record_size, "bytes")
    print("Possible records  :", possible_records)
    print("Records to export :", records_to_read)
    print()
    print("Output file:", output_path)

    confirm = input("\nContinue conversion? [Y/N]: ").strip().lower()

    if confirm != "y":
        warning("Conversion cancelled.")
        return False

    if records_to_read <= 0:
        print()
        error("ERROR: No records to read.")
        return False

    try:
        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            header = ["sample_number"] + [f"channel_{i + 1}" for i in range(num_channels)]
            writer.writerow(header)

            offset = header_size
            exported = 0
            bad_values = 0

            for _ in range(records_to_read):
                if offset + record_size > file_size:
                    break

                sample_number = read_u32_le(data, offset)
                offset += 4

                row = [sample_number]

                for ch in range(num_channels):
                    value = read_f32_le(data, offset)
                    offset += 4

                    if not math.isfinite(value):
                        bad_values += 1

                    row.append(value)

                writer.writerow(row)
                exported += 1

        print()
        success("Conversion finished successfully.")
        print("Rows exported     :", exported)
        print("Non-finite values :", bad_values)
        print("CSV created       :", output_path)
        return True

    except Exception as e:
        print()
        error("ERROR: Conversion failed.")
        print(e)
        return False


# ------------------------------------------------------------
# Option 9: Archive inspection
# ------------------------------------------------------------

def inspect_archive(path):
    print()
    info("Archive Inspection")
    print("==================")
    print()
    print("File:", path)

    data = read_file_bytes(path)

    if data is None:
        return

    magic_result = detect_magic_bytes(data)

    print()
    print(f"{RGB(150, 215, 255)}[ Detected Format ]{RESET}")
    print("-" * 40)

    if magic_result:
        success(f"Detected: {magic_result}")
    else:
        warning("Could not detect archive format from magic bytes.")
        return

    # --- Route to correct handler ---
    if "ZIP" in magic_result:
        inspect_zip(path)
    elif "GZIP" in magic_result:
        inspect_gzip(path)
    elif "BZIP2" in magic_result:
        inspect_bzip2(path)
    elif "RAR" in magic_result:
        print()
        warning("RAR format detected.")
        warning("RAR inspection requires the 'rarfile' package.")
        print("Install it with:  pip install rarfile")
        print("Also requires WinRAR or unrar to be installed on your system.")
    elif "7-Zip" in magic_result:
        print()
        warning("7-Zip format detected.")
        warning("7z inspection requires the 'py7zr' package.")
        print("Install it with:  pip install py7zr")
    else:
        print()
        warning("This format is not a supported archive type for deep inspection.")
        print("Supported: ZIP, GZIP, BZIP2")
        print("Requires extra package: RAR, 7z")


def print_bomb_warning():
    print()
    print(f"{BRIGHT_RED}{'!' * 60}{RESET}")
    print(f"{BRIGHT_RED}  WARNING: POSSIBLE ZIP BOMB DETECTED{RESET}")
    print(f"{BRIGHT_RED}  This archive has a suspicious compression ratio.{RESET}")
    print(f"{BRIGHT_RED}  DO NOT extract this file without caution.{RESET}")
    print(f"{BRIGHT_RED}{'!' * 60}{RESET}")


def inspect_zip(path):
    print()
    print(f"{RGB(150, 215, 255)}[ ZIP Archive Contents ]{RESET}")
    print("-" * 60)

    try:
        with zipfile.ZipFile(path, "r") as zf:
            entries = zf.infolist()

            total_compressed = 0
            total_uncompressed = 0
            nested_archives = []
            suspicious_entries = []

            print(f"  {'#':<5} {'Filename':<40} {'Compressed':>12} {'Uncompressed':>14} {'Ratio':>8}")
            print(f"  {'-'*5} {'-'*40} {'-'*12} {'-'*14} {'-'*8}")

            for i, entry in enumerate(entries, start=1):
                compressed = entry.compress_size
                uncompressed = entry.file_size

                total_compressed += compressed
                total_uncompressed += uncompressed

                ratio = (uncompressed / compressed) if compressed > 0 else 0

                ratio_str = f"{ratio:.1f}x"
                ratio_color = RESET

                if ratio > BOMB_RATIO_THRESHOLD:
                    ratio_color = BRIGHT_RED
                    suspicious_entries.append((entry.filename, compressed, uncompressed, ratio))
                elif ratio > 10:
                    ratio_color = YELLOW

                ext = Path(entry.filename).suffix.lower()
                if ext in (".zip", ".rar", ".7z", ".gz", ".bz2", ".tar"):
                    nested_archives.append(entry.filename)

                fname = entry.filename if len(entry.filename) <= 38 else entry.filename[:35] + "..."

                print(f"  {i:<5} {fname:<40} {format_size(compressed):>12} {format_size(uncompressed):>14} {ratio_color}{ratio_str:>8}{RESET}")

            # --- Totals ---
            print()
            print(f"{RGB(150, 215, 255)}[ Totals ]{RESET}")
            print("-" * 40)
            print(f"  Total files        : {len(entries)}")
            print(f"  Total compressed   : {format_size(total_compressed)}")
            print(f"  Total uncompressed : {format_size(total_uncompressed)}")

            overall_ratio = (total_uncompressed / total_compressed) if total_compressed > 0 else 0
            print(f"  Overall ratio      : {overall_ratio:.1f}x")

            # --- Nested archives ---
            if nested_archives:
                print()
                print(f"{RGB(150, 215, 255)}[ Nested Archives Detected ]{RESET}")
                print("-" * 40)
                warning(f"  Found {len(nested_archives)} archive(s) inside this archive:")
                for name in nested_archives:
                    print(f"  {YELLOW}>{RESET} {name}")
                print()
                warning("Nested archives are a common ZIP bomb technique.")
                warning("Do not extract without caution.")

            # --- Suspicious entries ---
            if suspicious_entries:
                print()
                print(f"{RGB(150, 215, 255)}[ Suspicious Entries ]{RESET}")
                print("-" * 40)
                for fname, comp, uncomp, ratio in suspicious_entries:
                    print(f"  {BRIGHT_RED}>{RESET} {fname}")
                    print(f"    Compressed   : {format_size(comp)}")
                    print(f"    Uncompressed : {format_size(uncomp)}")
                    print(f"    Ratio        : {ratio:.1f}x")

            # --- Bomb verdict ---
            print()
            print(f"{RGB(150, 215, 255)}[ Verdict ]{RESET}")
            print("-" * 40)

            is_bomb = (
                overall_ratio > BOMB_RATIO_THRESHOLD or
                total_uncompressed > BOMB_SIZE_THRESHOLD or
                len(suspicious_entries) > 0
            )

            if is_bomb:
                print_bomb_warning()
            elif nested_archives:
                warning("CAUTION: Contains nested archives. Inspect carefully before extracting.")
            else:
                success("No obvious ZIP bomb indicators detected.")
                print(f"  Overall compression ratio of {overall_ratio:.1f}x looks normal.")

    except zipfile.BadZipFile:
        error("ERROR: File is not a valid ZIP archive or is corrupted.")
    except Exception as e:
        error("ERROR: Could not inspect ZIP archive.")
        print(e)


def inspect_gzip(path):
    print()
    print(f"{RGB(150, 215, 255)}[ GZIP Archive Info ]{RESET}")
    print("-" * 40)

    compressed_size = path.stat().st_size

    try:
        with gzip.open(path, "rb") as gz:
            uncompressed_data = gz.read(100 * 1024 * 1024)  # Read up to 100 MB
            uncompressed_size = len(uncompressed_data)
            truncated = len(uncompressed_data) == 100 * 1024 * 1024

        ratio = (uncompressed_size / compressed_size) if compressed_size > 0 else 0

        print(f"  Compressed size   : {format_size(compressed_size)}")
        print(f"  Uncompressed size : {format_size(uncompressed_size)}", end="")

        if truncated:
            print(f" {YELLOW}(reading stopped at 100 MB limit){RESET}")
        else:
            print()

        print(f"  Compression ratio : {ratio:.1f}x")

        print()
        print(f"{RGB(150, 215, 255)}[ Verdict ]{RESET}")
        print("-" * 40)

        if ratio > BOMB_RATIO_THRESHOLD or (truncated and ratio > 10):
            print_bomb_warning()
        else:
            success("No obvious GZIP bomb indicators detected.")

    except Exception as e:
        error("ERROR: Could not inspect GZIP file.")
        print(e)


def inspect_bzip2(path):
    print()
    print(f"{RGB(150, 215, 255)}[ BZIP2 Archive Info ]{RESET}")
    print("-" * 40)

    compressed_size = path.stat().st_size

    try:
        with bz2.open(path, "rb") as bz:
            uncompressed_data = bz.read(100 * 1024 * 1024)  # Read up to 100 MB
            uncompressed_size = len(uncompressed_data)
            truncated = len(uncompressed_data) == 100 * 1024 * 1024

        ratio = (uncompressed_size / compressed_size) if compressed_size > 0 else 0

        print(f"  Compressed size   : {format_size(compressed_size)}")
        print(f"  Uncompressed size : {format_size(uncompressed_size)}", end="")

        if truncated:
            print(f" {YELLOW}(reading stopped at 100 MB limit){RESET}")
        else:
            print()

        print(f"  Compression ratio : {ratio:.1f}x")

        print()
        print(f"{RGB(150, 215, 255)}[ Verdict ]{RESET}")
        print("-" * 40)

        if ratio > BOMB_RATIO_THRESHOLD or (truncated and ratio > 10):
            print_bomb_warning()
        else:
            success("No obvious BZIP2 bomb indicators detected.")

    except Exception as e:
        error("ERROR: Could not inspect BZIP2 file.")
        print(e)


# ------------------------------------------------------------
# Help
# ------------------------------------------------------------

def show_help():
    print()
    print("HEX_EYE — Quick Help")
    print("=====================")
    print()
    print("HEX_EYE is a file inspection and hex analysis tool.")
    print("Drop any file into it and find out what is inside.")
    print()
    print("Options:")
    print()
    print("  [1] Deep byte check")
    print("      Scans the entire file block by block.")
    print("      Tells you if the file contains any data at all.")
    print()
    print("  [2] Full file inspection")
    print("      Detects file format via magic bytes.")
    print("      Shows hex preview, readable strings, numeric probes,")
    print("      entropy estimate, and a full summary.")
    print()
    print("  [3] Hex viewer")
    print("      Shows a clean formatted hex dump of the file.")
    print("      You choose how many bytes to view.")
    print()
    print("  [4] Extract readable strings")
    print("      Pulls all human-readable text out of the file")
    print("      and saves it to a .txt file.")
    print()
    print("  [5] Export raw numeric guesses")
    print("      Interprets every byte as float32, int16, and int32")
    print("      and exports the results to CSV for investigation.")
    print()
    print("  [6] Calculate file hash")
    print("      Computes MD5, SHA1, and SHA256 hashes.")
    print("      Use this to verify file integrity.")
    print()
    print("  [7] PicoLog-style file to CSV  (bonus converter)")
    print("      Attempts to convert a PicoLog-format binary file to CSV.")
    print("      Only works if the file matches the expected structure.")
    print()
    print("  [8] Inspect compressed archive")
    print("      Peeks inside ZIP, GZIP, BZIP2 archives without extracting.")
    print("      Lists all files, sizes, compression ratios.")
    print("      Detects nested archives and ZIP bomb indicators.")
    print("      Supported natively : ZIP, GZIP, BZIP2")
    print("      Requires extra package: RAR (rarfile), 7z (py7zr)")
    print()
    print("Tips:")
    print("  - Start with option [2] for a full overview of any unknown file.")
    print("  - Use option [1] first if you suspect the file may be empty.")
    print("  - Use option [8] on any archive before extracting it.")
    print("  - Raw numeric exports are guesses only, not confirmed data.")
    print("  - Any file type is accepted.")
    print()
    print("Example paths:")
    print(r"  C:\workspace\data\mydata.bin")
    print(r"  C:\workspace\data\mydata.PLW")
    print(r"  C:\Downloads\unknown.zip")


# ------------------------------------------------------------
# Main menu
# ------------------------------------------------------------

def main_menu():
    # startup_sequence()

    option_names = {
        "1": "Deep Byte Check",
        "2": "Full File Inspection",
        "3": "Hex Viewer",
        "4": "String Extractor",
        "5": "Raw Numeric Export",
        "6": "Hash Calculator",
        "7": "PicoLog Converter",
        "8": "Archive Inspection",
        "9": "Help",
    }

    while True:
        clear_screen()
        print_banner()

        print()
        print(f"{BOLD}{CYAN}Menu{RESET}")
        print(f"{CYAN} ═╦═ {RESET}")
        print(f"{CYAN}  ║  {RESET}")
        print(f"{CYAN}  ╠════════════{RESET} Deep byte check                      {GREEN}[1]{RESET}")
        print(f"{CYAN}  ╠═══════════{RESET} Full file inspection                  {GREEN}[2]{RESET}")
        print(f"{CYAN}  ╠══════════{RESET} Hex viewer                             {GREEN}[3]{RESET}")
        print(f"{CYAN}  ╠═════════{RESET} Extract readable strings to TXT         {GREEN}[4]{RESET}")
        print(f"{CYAN}  ╠════════{RESET} Export raw numeric guesses to CSV        {GREEN}[5]{RESET}")
        print(f"{CYAN}  ╠═══════{RESET} Calculate file hash                       {GREEN}[6]{RESET}")
        print(f"{CYAN}  ╠══════{RESET} PicoLog-style file to CSV                  {YELLOW}[7]{RESET}")
        print(f"{CYAN}  ╠═════{RESET} Inspect compressed archive                  {GREEN}[8]{RESET}")
        print(f"{CYAN}  ╠════{RESET} Help                                         {GREEN}[9]{RESET}")
        print(f"{CYAN}  ╚═══{RESET} Exit                                          {RED}[0]{RESET}")
        print()

        choice = input("Choose option: ").strip()

        clear_screen()
        print_banner()

        if choice == "0":
            print()
            fake_typing("  Shutting down HEX_EYE...", delay=0.04, color=CYAN)
            fake_loading_bar("  Closing", duration=0.8, steps=20)
            fake_typing("  Goodbye.", delay=0.05, color=GREEN)
            time.sleep(0.5)
            break

        elif choice in option_names:

            if choice != "9":
                fake_dots(f"  Loading {option_names[choice]}", dots=4, delay=0.2)
                time.sleep(0.2)
            else:
                fake_dots(f"  Loading {option_names[choice]}", dots=4, delay=0.2)
                time.sleep(0.2)

            if choice == "1":
                path = get_file_path_from_user()
                if path:
                    fake_loading_bar("  Scanning file", duration=0.8, steps=20)
                    check_nonzero_blocks(path)

            elif choice == "2":
                path = get_file_path_from_user()
                if path:
                    fake_loading_bar("  Analyzing file", duration=1.0, steps=25)
                    full_file_inspection(path)

            elif choice == "3":
                path = get_file_path_from_user()
                if path:
                    fake_loading_bar("  Reading bytes", duration=0.6, steps=15)
                    hex_viewer(path)

            elif choice == "4":
                path = get_file_path_from_user()
                if path:
                    fake_loading_bar("  Extracting strings", duration=0.8, steps=20)
                    extract_strings_to_txt(path)

            elif choice == "5":
                path = get_file_path_from_user()
                if path:
                    fake_loading_bar("  Preparing numeric export", duration=0.8, steps=20)
                    export_raw_numeric_guesses(path)

            elif choice == "6":
                path = get_file_path_from_user()
                if path:
                    fake_loading_bar("  Computing hashes", duration=0.8, steps=20)
                    calculate_file_hash(path)

            elif choice == "7":
                path = get_file_path_from_user()
                if path:
                    fake_loading_bar("  Loading converter", duration=0.8, steps=20)
                    convert_plw_to_csv(path)

            elif choice == "8":
                path = get_file_path_from_user()
                if path:
                    fake_loading_bar("  Opening archive", duration=0.8, steps=20)
                    inspect_archive(path)

            elif choice == "9":
                show_help()
                
            pause()

        else:
            print()
            error("Invalid option.")
            time.sleep(0.8)


if __name__ == "__main__":
    main_menu()
