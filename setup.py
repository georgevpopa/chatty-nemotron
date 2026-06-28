#!/usr/bin/env python3
"""
Chatty Nemotron - Setup & Auto-Installer
Rulează: python setup.py
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(cmd, cwd=None):
    """Execută comandă și afișează output."""
    print(f"\n🔄 Rulare: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr and "warning" not in result.stderr.lower():
        print(f"⚠️ {result.stderr}")
    return result.returncode == 0


def check_python():
    """Verifică versiunea Python."""
    version = sys.version_info
    print(f"📍 Python detectat: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10+ necesar!")
        return False
    return True


def create_venv():
    """Creează virtual environment."""
    venv_path = Path(".venv")

    if venv_path.exists():
        print("✅ Virtual environment existent.")
        return True

    print("📦 Creare virtual environment...")
    return run_command([sys.executable, "-m", "venv", ".venv"])


def install_deps():
    """Instalează dependențele."""
    print("📥 Instalare dependențe...")

    if platform.system() == "Windows":
        pip_cmd = [".venv\\Scripts\\pip", "install", "-r", "requirements.txt"]
    else:
        pip_cmd = [".venv/bin/pip", "install", "-r", "requirements.txt"]

    return run_command(pip_cmd)


def create_env():
    """Creează .env din .env.example dacă nu există."""
    env_path = Path(".env")
    example_path = Path(".env.example")

    if env_path.exists():
        print("✅ Fișier .env existent.")
        return True

    if example_path.exists():
        print("📝 Creare .env din .env.example...")
        env_path.write_text(example_path.read_text(), encoding="utf-8")
        print("⚠️ IMPORTANT: Editează fișierul .env și adaugă cheile tale API!")
        return True

    print("❌ .env.example negăsit!")
    return False


def create_dirs():
    """Creează directoare necesare."""
    dirs = ["uploads", "edits", "static/backgrounds"]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("✅ Directoare create.")


def check_images():
    """Verifică imagini de fundal."""
    bg_dir = Path("static/backgrounds")
    images = list(bg_dir.glob("*"))

    if not images or all(f.name == ".gitkeep" for f in images):
        print("\n🖼️ IMAGINI DE FUNDAL LIPSESC!")
        print("   Copiază 5-8 imagini în static/backgrounds/:")
        print("   - white.png, dark.jpeg, crimson.jpeg")
        print("   - white 2.png, purple.jpeg")
        print("   - navy.jpeg, sage.jpeg, gold.jpeg (opționale)")
        print("   Sau folosește propriile imagini și editează THEME_MAP în app/main.py")
        return False

    print(f"✅ {len([i for i in images if i.name != '.gitkeep'])} imagini de fundal găsite.")
    return True


def main():
    """Flux principal de instalare."""
    print("=" * 60)
    print("   🤖 CHATTY NEMOTRON - SETUP")
    print("=" * 60)

    # Verifică Python
    if not check_python():
        sys.exit(1)

    # Creează structura
    create_dirs()

    # Creează venv
    if not create_venv():
        print("❌ Eroare la crearea virtual environment.")
        sys.exit(1)

    # Instalează dependențe
    if not install_deps():
        print("❌ Eroare la instalarea dependențelor.")
        sys.exit(1)

    # Creează .env
    create_env()

    # Verifică imagini
    has_images = check_images()

    # Final
    print("\n" + "=" * 60)
    print("   ✅ SETUP COMPLET!")
    print("=" * 60)

    if not has_images:
        print("\n⚠️ ATENȚIE: Adaugă imaginile de fundal înainte de pornire!")

    print("\n📋 PAȘII URMĂTORI:")
    print("   1. Editează .env și adaugă cheile API")
    if not has_images:
        print("   2. Copiază imaginile de fundal în static/backgrounds/")
        print("   3. Rulează: starter.bat (Windows) sau ./starter.sh (Linux/Mac)")
    else:
        print("   2. Rulează: starter.bat (Windows) sau ./starter.sh (Linux/Mac)")

    print("\n🚀 Pornire rapidă:")
    if platform.system() == "Windows":
        print("   starter.bat")
    else:
        print("   ./starter.sh")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
