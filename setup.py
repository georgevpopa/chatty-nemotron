#!/usr/bin/env python3
"""
Chatty Nemotron - Setup & Auto-Installer
Run: python setup.py
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(cmd, cwd=None):
    """Execute command and display output."""
    print(f"\n🔄 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr and "warning" not in result.stderr.lower():
        print(f"⚠️ {result.stderr}")
    return result.returncode == 0


def check_python():
    """Check Python version."""
    version = sys.version_info
    print(f"📍 Python detected: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10+ required!")
        return False
    return True


def create_venv():
    """Create virtual environment."""
    venv_path = Path(".venv")

    if venv_path.exists():
        print("✅ Virtual environment already exists.")
        return True

    print("📦 Creating virtual environment...")
    return run_command([sys.executable, "-m", "venv", ".venv"])


def install_deps():
    """Install dependencies."""
    print("📥 Installing dependencies...")

    if platform.system() == "Windows":
        pip_cmd = [".venv\\Scripts\\pip", "install", "-r", "requirements.txt"]
    else:
        pip_cmd = [".venv/bin/pip", "install", "-r", "requirements.txt"]

    return run_command(pip_cmd)


def create_env():
    """Create .env from .env.example if it doesn't exist."""
    env_path = Path(".env")
    example_path = Path(".env.example")

    if env_path.exists():
        print("✅ .env file already exists.")
        return True

    if example_path.exists():
        print("📝 Creating .env from .env.example...")
        env_path.write_text(example_path.read_text(), encoding="utf-8")
        print("⚠️ IMPORTANT: Edit .env and add your API keys!")
        return True

    print("❌ .env.example not found!")
    return False


def create_dirs():
    """Create necessary directories."""
    dirs = ["uploads", "static/backgrounds"]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("✅ Directories created.")


def check_images():
    """Check background images."""
    bg_dir = Path("static/backgrounds")
    images = list(bg_dir.glob("*"))

    if not images or all(f.name == ".gitkeep" for f in images):
        print("\n🖼️ BACKGROUND IMAGES MISSING!")
        print("   Copy 7 images into static/backgrounds/:")
        print("   - white.png, dark.jpeg, purple.jpeg")
        print("   - cybertron.jpeg, navy.jpeg, sage.jpeg, gold.jpeg")
        print("   Or use your own images and edit THEME_MAP in app/main.py")
        return False

    print(f"✅ {len([i for i in images if i.name != '.gitkeep'])} background images found.")
    return True


def main():
    """Main installation flow."""
    print("=" * 60)
    print("   🤖 CHATTY NEMOTRON - SETUP")
    print("=" * 60)

    # Check Python
    if not check_python():
        sys.exit(1)

    # Create structure
    create_dirs()

    # Create venv
    if not create_venv():
        print("❌ Error creating virtual environment.")
        sys.exit(1)

    # Install dependencies
    if not install_deps():
        print("❌ Error installing dependencies.")
        sys.exit(1)

    # Create .env
    create_env()

    # Check images
    has_images = check_images()

    # Final
    print("\n" + "=" * 60)
    print("   ✅ SETUP COMPLETE!")
    print("=" * 60)

    if not has_images:
        print("\n⚠️ WARNING: Add background images before starting!")

    print("\n📋 NEXT STEPS:")
    print("   1. Edit .env and add your API keys")
    if not has_images:
        print("   2. Copy background images to static/backgrounds/")
        print("   3. Run: starter.bat (Windows) or ./starter.sh (Linux/Mac)")
    else:
        print("   2. Run: starter.bat (Windows) or ./starter.sh (Linux/Mac)")

    print("\n🚀 Quick start:")
    if platform.system() == "Windows":
        print("   starter.bat")
    else:
        print("   ./starter.sh")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()