# HEX_EYE
# author: bg0dmtl

A command-line file inspection and hex analysis tool.
Inspect, probe, and analyze any unknown binary or text-based file directly from the terminal.

The tool provides an ASCII menu and can be started with a `.bat` launcher or run directly via Python.

------------------------------------

## 1. What This Tool Does

This tool can:

1. Deep byte check — scan the entire file and detect if it contains any real data
2. Full file inspection — detect format, show hex preview, strings, numeric probes, entropy and summary
3. Hex viewer — display a formatted hex dump of any file
4. Extract readable strings — pull all human-readable text out of a binary file and save to TXT
5. Export raw numeric guesses — interpret file bytes as float32, int16, int32 and export to CSV
6. Calculate file hash — compute MD5, SHA1, and SHA256 hashes for integrity checks
7. PicoLog-style file to CSV — bonus converter for Pico-style .PLW binary files

------------------------------------

## 2. Requirements

Python must be installed.

Check Python via console:

    python --version
    py --version

WARNING: No additional Python packages are required.
The tool only uses standard Python libraries.

------------------------------------

## 3. How to Start

Run HEX_EYE.bat

If the .bat does not work, run the script directly:

    python hex_eye.py

------------------------------------

## 4. Deep Byte Check

Choose option: [1] Deep byte check
Enter the full path to the file you want to check.

RESULTS:
RESULT: This file contains data.              -> File has readable content, continue with inspection
RESULT: This file contains only zero bytes.   -> No data can be extracted from this file

------------------------------------

## 5. Full File Inspection

Choose option: [2] Full file inspection
Enter the full path to the file.

This option runs a full analysis and shows:

- File name, extension, size, and data ratio
- Format detection via magic bytes (ZIP, PDF, EXE, PNG, MP3, and more)
- Text vs binary detection
- Hex preview of the first 256 bytes
- Readable strings found inside the file
- Numeric probes (float32 and int16 values near the file start)
- Shannon entropy estimate
- Full summary

Entropy guide:
> 7.5 bits/byte   -> File may be encrypted or compressed
5.0 - 7.5         -> Likely a structured binary format
< 5.0             -> Likely plain text or simple structured data

------------------------------------

## 6. Hex Viewer

Choose option: [3] Hex viewer
Enter the full path to the file.
Enter how many bytes to view (default is 512).

Output shows offset, hex values, and printable text side by side.

------------------------------------

## 7. Extract Readable Strings

Choose option: [4] Extract readable strings to TXT
Enter the full path to the file.

All human-readable ASCII strings found inside the file are saved to a .txt file
next to the original file.

Example:
Input:  C:\workspace\data\mydata.bin
Output: C:\workspace\data\mydata.strings.txt

------------------------------------

## 8. Export Raw Numeric Guesses

Choose option: [5] Export raw numeric guesses to CSV
Enter the full path to the file.

WARNING: These are raw guesses, not confirmed measurement data.
Use these files for investigation only.

Three CSV files are created next to the original file:

    .raw_float32.csv   -> every 4 bytes interpreted as float32 little-endian
    .raw_int16.csv     -> every 2 bytes interpreted as int16, also divided by 10 and 100
    .raw_int32.csv     -> every 4 bytes interpreted as int32 little-endian

Look for columns that contain realistic values such as temperatures, counters, or timestamps.

WARNING: Files larger than 50 MB will prompt a confirmation before export.

------------------------------------

## 9. Calculate File Hash

Choose option: [6] Calculate file hash
Enter the full path to the file.

Computes three hashes at once:

    MD5
    SHA1
    SHA256

Use these hashes to verify file integrity or compare files across machines.
Identical hash = identical file contents.
Different hash = files are not the same.

------------------------------------

## 10. PicoLog-style File to CSV (Bonus)

Choose option: [7] PicoLog-style file to CSV
Enter the full path to your .PLW file.

This option attempts to convert a Pico-style binary .PLW file to .CSV format.
It only works if the file matches the expected PicoLog binary structure.

RESULTS:
Conversion finished successfully.          -> CSV created next to the original file
ERROR: File contains only zero bytes.      -> File cannot be converted
ERROR: File is too small.                  -> File does not match expected structure
ERROR: Header size looks invalid.          -> File may not be supported
ERROR: Header version looks invalid.       -> File may not be supported
ERROR: Number of channels looks invalid.   -> File may not be supported
ERROR: No records to read.                 -> No readable data found

Example:
Input:  C:\workspace\data\mydata.PLW
Output: C:\workspace\data\mydata.csv

IMPORTANT: Always verify the converted CSV values before using them.

------------------------------------

## 11. Notes

This tool cannot repair corrupted or damaged files.
This tool cannot recover data from files that contain only zero bytes.
Raw numeric exports are guesses only and are not confirmed measurement data.
The PicoLog converter is intended for Pico-style .PLW files only. Other formats may not work.
Any file type can be loaded into the inspection options, not just .PLW files.

------------------------------------

## 12. Detected File Formats (Magic Bytes)

The full inspection option can automatically identify the following formats:

    ZIP archive / Office document
    PDF document
    Windows EXE / DLL
    ELF executable (Linux)
    JPEG image
    PNG image
    GIF image
    BMP image
    MP3 audio
    WAV / AVI (RIFF container)
    MPEG video
    GZIP compressed
    BZIP2 compressed
    XZ compressed
    7-Zip archive
    RAR archive
    MS Office legacy (DOC / XLS / PPT)
    UTF-8 text with BOM
    UTF-16 text
    SQLite database
    MIDI audio

If no match is found, the file is reported as unknown binary or text-based.