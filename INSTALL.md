# 📖 Ghid Instalare Completă — Chatty Nemotron

## Cerințe minime

- **Python 3.10+** (recomandat 3.11)
- **2 GB RAM** liberi
- **Cheie API** (minimum una: NVIDIA / OpenAI / Groq)

---

## Windows

### Pasul 1: Instalează Python

1. Descarcă de la [python.org](https://www.python.org/downloads/)
2. La instalare, **bifează** "Add Python to PATH"
3. Verifică: `python --version` → ar trebui să afișeze 3.10+

### Pasul 2: Clonează repo-ul

```powershell
git clone https://github.com/username/chatty-nemotron.git
cd chatty-nemotron
```

### Pasul 3: Rulează setup automat

```powershell
python setup.py
```

Acest script va:
- ✅ Verifica versiunea Python
- ✅ Crea virtual environment (`.venv/`)
- ✅ Instala toate dependențele
- ✅ Crea fișierul `.env` din template
- ✅ Crea directoarele necesare

### Pasul 4: Configurează cheile API

```powershell
notepad .env
```

Completează cel puțin o cheie:
```env
NVIDIA_API_KEY=nvapi-ta-cheie-aici
```

### Pasul 5: Adaugă imaginile de fundal

Copiază 5-8 imagini în `static/backgrounds/`:
- `white.png`, `dark.jpeg`, `crimson.jpeg`
- `white 2.png`, `purple.jpeg`
- `navy.jpeg`, `sage.jpeg`, `gold.jpeg` (opționale)

### Pasul 6: Pornește aplicația

```powershell
# Metoda 1: Dublu-click pe starter.bat
starter.bat

# Metoda 2: Din PowerShell
.venv\Scripts\streamlit run app/main.py --server.port=8880
```

Browserul se deschide automat la: **http://localhost:8880**

---

## Linux (Ubuntu/Debian)

```bash
# 1. Instalează dependențe sistem
sudo apt update
sudo apt install python3 python3-venv python3-pip git

# 2. Clonează
git clone https://github.com/username/chatty-nemotron.git
cd chatty-nemotron

# 3. Setup
python3 setup.py

# 4. Editează .env
nano .env

# 5. Imagini
mkdir -p static/backgrounds
# Copiază imaginile...

# 6. Pornește
chmod +x starter.sh
./starter.sh
```

---

## macOS

```bash
# 1. Instalează Homebrew (dacă nu ai)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Instalează Python
brew install python git

# 3. Clonează
git clone https://github.com/username/chatty-nemotron.git
cd chatty-nemotron

# 4. Setup
python3 setup.py

# 5. Editează .env
nano .env

# 6. Imagini
mkdir -p static/backgrounds
# Copiază imaginile...

# 7. Pornește
chmod +x starter.sh
./starter.sh
```

---

## Docker (opțional)

```bash
# Build
docker build -t chatty-nemotron .

# Run
docker run -p 8880:8880 --env-file .env chatty-nemotron
```

Sau cu docker-compose:
```bash
docker-compose up -d
```

---

## 🐛 Depanare

| Problemă | Soluție |
|----------|---------|
| `python` nu este recunoscut | Adaugă Python în PATH sau folosește `py -3` |
| `ImportError` la pornire | Rulează `clear_cache.bat` sau `rm -rf __pycache__` |
| Port 8880 ocupat | `netstat -ano \| findstr :8880` apoi `taskkill /PID <pid> /F` |
| Imagini nu apar | Verifică `static/backgrounds/` și numele fișierelor (case-sensitive) |
| Modelul nu apare | Verifică `.env` și `config/providers.json` |

---

## 📞 Suport

- Deschide un [Issue](https://github.com/username/chatty-nemotron/issues) pe GitHub
- Sau contactează-ne la: contact@example.com
