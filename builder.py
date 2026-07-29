import os
import sys
import time
import shutil
import subprocess

os.system("")

RESET = "\033[0m"
BOLD = "\033[1m"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
WHITE = "\033[37m"

BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"


def RGB(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def success(text):
    print(f"{GREEN}  [+] {text}{RESET}")


def error(text):
    print(f"{RED}  [!] {text}{RESET}")


def warning(text):
    print(f"{YELLOW}  [~] {text}{RESET}")


def info(text):
    print(f"{CYAN}  [>] {text}{RESET}")


def fake_typing(text, delay=0.03, color=None):
    if color:
        print(color, end="", flush=True)
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    if color:
        print(RESET, end="", flush=True)
    print()


def fake_loading_bar(text="Loading", duration=1.0, steps=30, color=None):
    bar_color = color if color else RGB(0, 153, 255)
    print()
    print(f"  {CYAN}{text}{RESET}")
    print(f"  {CYAN}[{RESET}", end="", flush=True)

    step_time = duration / steps

    for i in range(steps):
        time.sleep(step_time)
        print(f"{bar_color}█{RESET}", end="", flush=True)

    print(f"{CYAN}]{RESET} ", end="")
    print(f"{GREEN}Done{RESET}")
    print()


def fake_dots(text, dots=5, delay=0.25):
    print(f"\n  {CYAN}{text}{RESET}", end="", flush=True)
    for _ in range(dots):
        time.sleep(delay)
        print(f"{CYAN}.{RESET}", end="", flush=True)
    print()


def fake_scanning(lines, delay=0.12):
    for line in lines:
        time.sleep(delay)
        print(f"  {RGB(0, 153, 255)}>{RESET} {line}")


def print_banner():
    print(f"{RGB(255, 255, 255)}  {'=' * 60}{RESET}")
    print(f"{RGB(220, 242, 255)}  ██████╗ ██╗   ██╗██╗██╗     ██████╗ ███████╗██████╗ {RESET}")
    print(f"{RGB(190, 230, 255)}  ██╔══██╗██║   ██║██║██║     ██╔══██╗██╔════╝██╔══██╗{RESET}")
    print(f"{RGB(150, 215, 255)}  ██████╔╝██║   ██║██║██║     ██║  ██║█████╗  ██████╔╝{RESET}")
    print(f"{RGB(105, 198, 255)}  ██╔══██╗██║   ██║██║██║     ██║  ██║██╔══╝  ██╔══██╗{RESET}")
    print(f"{RGB(65, 180, 255)}  ██████╔╝╚██████╔╝██║███████╗██████╔╝███████╗██║  ██║{RESET}")
    print(f"{RGB(25, 165, 255)}  ╚═════╝  ╚═════╝ ╚═╝╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝{RESET}")
    print(f"{RGB(0, 153, 255)}          HEX_EYE — EXE Builder Script{RESET}")
    print(f"{RGB(0, 153, 255)}  {'=' * 60}{RESET}")
    print()


def print_step_header(step, total, title):
    print()
    print(f"  {RGB(0, 153, 255)}{'─' * 60}{RESET}")
    print(f"  {BOLD}{BRIGHT_WHITE}STEP {step}/{total}  —  {title}{RESET}")
    print(f"  {RGB(0, 153, 255)}{'─' * 60}{RESET}")
    print()


def print_final_banner(exe_path, duration):
    print()
    print(f"  {RGB(0, 200, 100)}{'═' * 60}{RESET}")
    print(f"  {BOLD}{BRIGHT_GREEN}  BUILD SUCCESSFUL{RESET}")
    print(f"  {RGB(0, 200, 100)}{'═' * 60}{RESET}")
    print()
    print(f"  {BRIGHT_WHITE}Output file:{RESET}")
    print(f"  {RGB(0, 153, 255)}  {exe_path}{RESET}")
    print()
    print(f"  {BRIGHT_WHITE}Build time:{RESET}  {RGB(0, 200, 100)}{duration:.1f} seconds{RESET}")
    print()
    print(f"  {RGB(0, 153, 255)}{'═' * 60}{RESET}")
    print()


def print_fail_banner():
    print()
    print(f"  {BRIGHT_RED}{'═' * 60}{RESET}")
    print(f"  {BOLD}{BRIGHT_RED}  BUILD FAILED{RESET}")
    print(f"  {BRIGHT_RED}{'═' * 60}{RESET}")
    print()


# ------------------------------------------------------------
# Build steps
# ------------------------------------------------------------

SOURCE_FILE = "hex_eye_src.py"
OUTPUT_NAME = "HEX_EYE"
TOTAL_STEPS = 5


def step_check_environment():
    print_step_header(1, TOTAL_STEPS, "Checking Environment")

    fake_scanning([
        "Checking Python installation...",
        "Checking PyInstaller installation...",
        "Checking source file...",
    ], delay=0.2)

    print()

    # Check Python
    python_version = sys.version.split(" ")[0]
    success(f"Python found: {python_version}")

    # Check PyInstaller
    result = shutil.which("pyinstaller")
    if result is None:
        error("PyInstaller not found.")
        print()
        warning("Install it with:  pip install pyinstaller")
        print()
        return False

    success(f"PyInstaller found: {result}")

    # Check source file
    if not os.path.isfile(SOURCE_FILE):
        error(f"Source file not found: {SOURCE_FILE}")
        print()
        warning(f"Make sure {SOURCE_FILE} is in the same folder as this builder.")
        print()
        return False

    source_size = os.path.getsize(SOURCE_FILE)
    success(f"Source file found: {SOURCE_FILE} ({source_size:,} bytes)")

    fake_loading_bar("  Environment check", duration=0.8, steps=20, color=RGB(0, 200, 100))
    return True


def step_clean_old_build():
    print_step_header(2, TOTAL_STEPS, "Cleaning Old Build Files")

    targets = ["build", "dist", f"{OUTPUT_NAME}.spec"]
    found_any = False

    for target in targets:
        if os.path.exists(target):
            found_any = True
            info(f"Found: {target}")

    if not found_any:
        info("No old build files found. Nothing to clean.")
        fake_loading_bar("  Clean", duration=0.5, steps=15, color=RGB(0, 200, 100))
        return True

    print()
    fake_dots("  Removing old files", dots=5, delay=0.2)
    print()

    try:
        if os.path.isdir("build"):
            shutil.rmtree("build")
            success("Removed: build/")

        if os.path.isdir("dist"):
            shutil.rmtree("dist")
            success("Removed: dist/")

        if os.path.isfile(f"{OUTPUT_NAME}.spec"):
            os.remove(f"{OUTPUT_NAME}.spec")
            success(f"Removed: {OUTPUT_NAME}.spec")

    except Exception as e:
        error(f"Could not clean old files: {e}")
        return False

    fake_loading_bar("  Cleanup", duration=0.6, steps=15, color=RGB(0, 200, 100))
    return True


def step_run_pyinstaller():
    print_step_header(3, TOTAL_STEPS, "Running PyInstaller")

    command = [
        "pyinstaller",
        "--onefile",
        "--name", OUTPUT_NAME,
        SOURCE_FILE,
    ]

    info(f"Command: {' '.join(command)}")
    print()
    fake_dots("  Starting PyInstaller", dots=4, delay=0.3)
    print()

    print(f"  {RGB(0, 153, 255)}{'─' * 60}{RESET}")
    print(f"  {YELLOW}PyInstaller output:{RESET}")
    print(f"  {RGB(0, 153, 255)}{'─' * 60}{RESET}")
    print()

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        for line in process.stdout:
            line = line.rstrip()
            if line:
                if "ERROR" in line or "error" in line:
                    print(f"  {RED}{line}{RESET}")
                elif "WARNING" in line or "warning" in line:
                    print(f"  {YELLOW}{line}{RESET}")
                elif "INFO" in line:
                    print(f"  {CYAN}{line}{RESET}")
                else:
                    print(f"  {WHITE}{line}{RESET}")

        process.wait()

        print()
        print(f"  {RGB(0, 153, 255)}{'─' * 60}{RESET}")
        print()

        if process.returncode != 0:
            error(f"PyInstaller exited with code: {process.returncode}")
            return False

        success(f"PyInstaller finished with exit code: {process.returncode}")
        return True

    except FileNotFoundError:
        error("PyInstaller command not found.")
        warning("Install it with:  pip install pyinstaller")
        return False

    except Exception as e:
        error(f"Unexpected error running PyInstaller: {e}")
        return False


def step_verify_output():
    print_step_header(4, TOTAL_STEPS, "Verifying Output")

    exe_path = os.path.join("dist", f"{OUTPUT_NAME}.exe")

    fake_scanning([
        "Checking dist folder...",
        f"Looking for {OUTPUT_NAME}.exe...",
        "Verifying file size...",
    ], delay=0.2)

    print()

    if not os.path.isfile(exe_path):
        error(f"Expected output not found: {exe_path}")
        return False, None

    exe_size = os.path.getsize(exe_path)
    success(f"Output file found: {exe_path}")
    success(f"File size: {exe_size / (1024 * 1024):.2f} MB ({exe_size:,} bytes)")

    if exe_size < 1024:
        warning("File seems very small. Build may have failed silently.")
        return False, None

    fake_loading_bar("  Verification", duration=0.6, steps=15, color=RGB(0, 200, 100))
    return True, exe_path


def step_move_exe():
    print_step_header(5, TOTAL_STEPS, "Moving EXE to Current Folder")

    src = os.path.join("dist", f"{OUTPUT_NAME}.exe")
    dst = f"{OUTPUT_NAME}.exe"

    fake_dots("  Moving file", dots=4, delay=0.2)
    print()

    try:
        if os.path.isfile(dst):
            warning(f"Old {OUTPUT_NAME}.exe found in current folder. Replacing it.")
            os.remove(dst)

        shutil.move(src, dst)
        success(f"Moved to: {os.path.abspath(dst)}")

    except Exception as e:
        error(f"Could not move EXE: {e}")
        warning(f"Your EXE is still available at: {src}")
        return src

    fake_loading_bar("  Finalizing", duration=0.6, steps=15, color=RGB(0, 200, 100))
    return dst


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    clear_screen()
    print_banner()

    fake_typing("  Initializing HEX_EYE Builder...", delay=0.03, color=CYAN)
    time.sleep(0.3)
    fake_scanning([
        "Loading build configuration",
        f"Target source  : {SOURCE_FILE}",
        f"Target output  : {OUTPUT_NAME}.exe",
        "Build mode     : --onefile",
    ], delay=0.15)

    fake_loading_bar("  Preparing builder", duration=1.0, steps=25)

    build_start = time.time()

    # Step 1
    if not step_check_environment():
        print_fail_banner()
        input("  Press ENTER to exit...")
        return

    # Step 2
    if not step_clean_old_build():
        print_fail_banner()
        input("  Press ENTER to exit...")
        return

    # Step 3
    if not step_run_pyinstaller():
        print_fail_banner()
        input("  Press ENTER to exit...")
        return

    # Step 4
    verified, exe_path = step_verify_output()
    if not verified:
        print_fail_banner()
        input("  Press ENTER to exit...")
        return

    # Step 5
    final_path = step_move_exe()

    build_end = time.time()
    build_duration = build_end - build_start

    print_final_banner(os.path.abspath(final_path), build_duration)

    input("  Press ENTER to exit...")


if __name__ == "__main__":
    main()
