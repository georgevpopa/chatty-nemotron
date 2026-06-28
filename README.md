# 🤖 Chatty Nemotron

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/georgevpopa/chatty-nemotron?style=social)](https://github.com/georgevpopa/chatty-nemotron/stargazers)

> Multi-model AI DevOps assistant with customizable visual themes, multimodal file upload, and persistent local conversation history.

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/georgevpopa/chatty-nemotron.git
cd chatty-nemotron

# 2. Run automated setup (creates venv, installs deps, creates .env)
python setup.py

# 3. Edit .env with your API keys
notepad .env        # Windows
nano .env           # Linux/Mac

# 4. Copy background images to static/backgrounds/

# 5. Launch!
starter.bat         # Windows (double-click)
./starter.sh        # Linux/Mac
```

The app will be available at: **http://localhost:8880**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **🤖 34+ AI Models** | NVIDIA NIM (30 models), OpenAI, Groq — extensible to any OpenAI-compatible API |
| **🔄 Auto-Fallback** | If one model fails, automatically tries the next in queue |
| **🧠 Chain of Thought** | Detects and displays reasoning (Nemotron, GPT-OSS) in a separate expander |
| **🎨 7 Visual Themes** | Custom backgrounds with adaptive text contrast (light/dark) |
| **📎 Drag & Drop Upload** | Text files and images — analyzed by multimodal AI |
| **💾 Auto-Save** | Automatically saves every conversation to local SQLite |
| **📜 History** | Load, delete, and navigate through past conversations |
| **⚙️ External Config** | Add models via JSON — no code changes needed |
| **🚀 One-Click Start** | `starter.bat` / `starter.sh` — fully automated launch |

---

## 📸 Screenshot

![Chatty Nemotron Interface]
<img width="3422" height="1212" alt="screenshoot" src="https://github.com/user-attachments/assets/22a461a8-e726-4ea8-8948-13a713cb4371" />




---

## 🎨 Available Themes

| Theme | File | Vibe |
|-------|------|------|
| Minimal Light | `white.png` | Clean, minimalist |
| Cyber Dark | `dark.jpeg` | Tech, neon cyan |
| Deep Purple | `purple.jpeg` | Mystic, purple |
| Cybertron | `cybertron.jpeg` | Sci-fi, blue |
| Midnight Navy | `navy.jpeg` | Corporate, professional |
| Forest Sage | `sage.jpeg` | Natural, elegant |
| Solar Gold | `gold.jpeg` | Luxury, premium |

---

## 🤖 Available AI Models

### NVIDIA NIM (30 models)
Nemotron Ultra 550B, Nemotron Super 120B, Nemotron Nano Omni 30B, Llama 3.3 Nemotron Super 49B, DeepSeek V4 Flash/Pro, GPT-OSS 20B/120B, Mistral Nemotron, Mistral Medium/Small/Large 3.5, Ministral 14B, Mixtral 8x22B/8x7B, Llama 3.3/3.1/3 70B, Dracarys Llama 3.1 70B, Gemma 4 31B, DiffusionGemma 26B, Gemma 3N E4B/E2B, MiniMax M3/M2.7, Kimi K2.6, Qwen 3.5 122B/397B, Qwen3-Next 80B, GLM 5.1

### OpenAI
GPT-4o, GPT-4o Mini

### Groq
Llama 3.1 70B, Mixtral 8x7B

---

## 📎 File Upload & Multimodal

| File Type | Extensions | What AI Does |
|-----------|------------|--------------|
| **Text** | `.txt`, `.py`, `.md`, `.json`, `.yaml`, `.csv`, `.log`, `.js`, `.html`, `.css`, `.sql` | Reads and analyzes content |
| **Images** | `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp` | Visual analysis via multimodal models (VLM) |
| **Documents** | `.pdf`, `.docx`, `.xlsx`, `.pptx` | Detects, waits for manual description |

### How It Works

1. **Drag & Drop** or click the upload zone
2. Preview appears in an expander
3. Type a message and press Enter
4. File is sent together with the message to the AI
5. Multimodal models (Kimi, MiniMax, Qwen, Mistral VLM) process the image directly

> **Note:** The selected model must have `"features": ["multimodal", "vision"]` in `providers.json` to analyze images.

---

## ⚙️ Add a New Model

Edit `config/providers.json` — **no code changes needed**:

```json
{
  "id": "nvidia/nemotron-3-ultra-550b-a55b",
  "label": "Nemotron Ultra 550B",
  "description": "1M context, reasoning, coding",
  "stream_parser": "reasoning",
  "default_params": {
    "temperature": 1,
    "max_tokens": 16384
  }
}
```

Restart and it appears automatically in the dropdown.

### Add a Vision-Capable Model (Multimodal)

For image analysis support, include the `features` field:

```json
{
  "id": "gpt-4o",
  "label": "GPT-4o",
  "description": "OpenAI multimodal vision model",
  "stream_parser": "standard",
  "features": ["multimodal", "vision"],
  "default_params": {
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

---

## 🛡️ Privacy First

- ✅ All data stays **local**
- ✅ API keys are in `.env` — **never** on Git
- ✅ Conversation history in **local SQLite**
- ✅ No tracking, no analytics

---

## 🧰 Tech Stack

| Component | Role |
|-----------|------|
| Python 3.11 | Runtime |
| Streamlit 1.40+ | UI framework |
| OpenAI SDK | Universal API client |
| SQLite3 | Local persistence |

---

## 🐳 Docker (Optional)

```bash
docker-compose up -d
```

---

## 📖 Documentation

- [INSTALL.md](INSTALL.md) — Detailed installation guide
- [config/providers.json](config/providers.json) — Model configuration

---

## 🤝 Contributing

PRs welcome! Open an [Issue](https://github.com/georgevpopa/chatty-nemotron/issues) or propose improvements.

---

## 📜 License

[MIT License](LICENSE) — see file for details.

---

> **Author:** [georgevpopa](https://github.com/georgevpopa) 🚀  
> If you like this project, give it a ⭐!

[![Star History Chart](https://api.star-history.com/svg?repos=georgevpopa/chatty-nemotron&type=Date)](https://star-history.com/#georgevpopa/chatty-nemotron&Date)
