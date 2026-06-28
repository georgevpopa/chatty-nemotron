# 📖 Complete Installation Guide — Chatty Nemotron

## Minimum Requirements

- **Python 3.10+** (recommended 3.11)
- **2 GB free RAM**
- **API Key** (at least one: NVIDIA / OpenAI / Groq)

---

## Windows

### Step 1: Install Python

1. Download from [python.org](https://www.python.org/downloads/)
2. During installation, **check** "Add Python to PATH"
3. Verify: `python --version` → should show 3.10+

### Step 2: Clone the repository

```powershell
git clone https://github.com/username/chatty-nemotron.git
cd chatty-nemotron
```

### Step 3: Run automated setup

```powershell
python setup.py
```

This script will:
- ✅ Check Python version
- ✅ Create virtual environment (`.venv/`)
- ✅ Install all dependencies
- ✅ Create `.env` file from template
- ✅ Create necessary directories

### Step 4: Configure API keys

```powershell
notepad .env
```

Fill in at least one key:
```env
NVIDIA_API_KEY=nvapi-your-key-here
```

### Step 5: Add background images

Copy 7 images into `static/backgrounds/`:
- `white.png`, `dark.jpeg`, `purple.jpeg`
- `cybertron.jpeg`, `navy.jpeg`, `sage.jpeg`, `gold.jpeg`

### Step 6: Start the application

```powershell
# Method 1: Double-click starter.bat
starter.bat

# Method 2: From PowerShell
.venv\Scripts\streamlit run app/main.py --server.port=8880
```

The browser opens automatically at: **http://localhost:8880**

---

## Linux (Ubuntu/Debian)

### Step 1: Install system dependencies

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip git
```

### Step 2: Clone the repository

```bash
git clone https://github.com/username/chatty-nemotron.git
cd chatty-nemotron
```

### Step 3: Run setup

```bash
python3 setup.py
```

### Step 4: Edit environment variables

```bash
nano .env
```

### Step 5: Add background images

```bash
mkdir -p static/backgrounds
# Copy your images here...
```

### Step 6: Start the application

```bash
chmod +x starter.sh
./starter.sh
```

---

## macOS

### Step 1: Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Python & Git

```bash
brew install python git
```

### Step 3: Clone the repository

```bash
git clone https://github.com/username/chatty-nemotron.git
cd chatty-nemotron
```

### Step 4: Run setup

```bash
python3 setup.py
```

### Step 5: Edit environment variables

```bash
nano .env
```

### Step 6: Add background images

```bash
mkdir -p static/backgrounds
# Copy your images here...
```

### Step 7: Start the application

```bash
chmod +x starter.sh
./starter.sh
```

---

## Docker (Optional)

```bash
# Build the image
docker build -t chatty-nemotron .

# Run the container
docker run -p 8880:8880 --env-file .env chatty-nemotron
```

Or using docker-compose:
```bash
docker-compose up -d
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `python` not recognized | Add Python to PATH or use `py -3` |
| `ImportError` on startup | Run `clear_cache.bat` or `rm -rf __pycache__` |
| Port 8880 in use | Run `netstat -ano | findstr :8880` then `taskkill /PID <pid> /F` |
| Images not showing | Check `static/backgrounds/` and filenames (they are case-sensitive) |
| Model not appearing | Check `.env` and `config/providers.json` |

---

## 📞 Support

- Open an [Issue](https://github.com/username/chatty-nemotron/issues) on GitHub
- Or contact us at: contact@example.com