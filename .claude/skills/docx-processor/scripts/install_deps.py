#!/usr/bin/env python3
"""
Install dependencies for DOCX processing
"""

import subprocess
import sys

def install_dependency(package):
    """Install a Python package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Successfully installed {package}")
    except subprocess.CalledProcessError:
        print(f"Failed to install {package}")
        return False
    return True

def main():
    required_packages = [
        "python-docx",
    ]

    print("Installing DOCX processing dependencies...")

    for package in required_packages:
        print(f"Installing {package}...")
        if not install_dependency(package):
            print(f"Failed to install {package}. Please install manually.")
            sys.exit(1)

    print("All dependencies installed successfully!")

if __name__ == "__main__":
    main()