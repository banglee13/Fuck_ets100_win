#!/usr/bin/env python3
"""
Fuck ETS100 - Windows Version - Python Launcher
Run with: python run.py
"""

import sys
import subprocess
import os

def check_python():
    print("="*40)
    print("   Fuck ETS100 - Windows Version")
    print("="*40)
    print()
    
    print(f"[1/3] Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8+ is required")
        input("Press Enter to exit...")
        return False
    return True

def install_dependencies():
    print("[2/3] Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt",
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
        ])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Warning: Dependency installation may have issues ({e})")
        print("Continuing anyway...")
        return True

def run_main():
    print()
    print("[3/3] Starting program...")
    print()
    try:
        subprocess.check_call([sys.executable, "main.py"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Program exited with error: {e}")
        input("Press Enter to exit...")
        return False

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    if check_python():
        if install_dependencies():
            run_main()
