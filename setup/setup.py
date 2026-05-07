import subprocess
import sys
import os
import shutil

def check_and_install(package_name, import_name=None):
    if import_name is None:
        import_name = package_name.replace('-', '_')
        
    print(f"Checking {package_name}...")
    try:
        __import__(import_name)
        print(f"[OK] {package_name} is already installed.")
    except ImportError:
        print(f"[MISSING] {package_name} not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"[OK] {package_name} installed successfully.")
        except Exception as e:
            print(f"[ERROR] Could not install {package_name}: {e}")

def check_ffmpeg():
    print("Checking for FFmpeg...")
    if shutil.which("ffmpeg"):
        print("[OK] FFmpeg is detected in system PATH.")
        return True
    
    try:
        import static_ffmpeg
        print("[OK] static-ffmpeg package is available.")
        return True
    except ImportError:
        pass
        
    print("[WARNING] FFmpeg not found! High-quality merging will not work.")
    print("Tip: Install it via 'pip install static-ffmpeg' or download from ffmpeg.org")
    return False

def install_from_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        print(f"Installing from {req_path}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
            print("[OK] All requirements installed.")
        except Exception as e:
            print(f"[ERROR] Failed to install requirements: {e}")
    else:
        print("[ERROR] requirements.txt not found in setup folder.")

if __name__ == "__main__":
    print("=== YouTube Downloader Environment Setup ===")
    print(f"Python executable: {sys.executable}")
    print("-" * 40)
    
    install_from_requirements()
    check_ffmpeg()
    
    print("-" * 40)
    print("Setup finished. You can now run the application.")
    input("Press Enter to close...")
