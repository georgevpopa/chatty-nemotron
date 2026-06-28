# 🤖 Chatty Nemotron

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/georgevpopa/chatty-nemotron?style=social)](https://github.com/georgevpopa/chatty-nemotron/stargazers)

> Multi-model AI DevOps assistant with customizable visual themes, file upload, image generation/editing, and persistent local conversation history.

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/georgevpopa/chatty-nemotron.git
cd chatty-nemotron

# 2. Run automated setup (creates venv, installs deps, creates .env)
python setup.py

# 3. Edit .env with your API key
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
| **🎨 8 Visual Themes** | 5 original + 3 professional (Midnight Navy, Forest Sage, Solar Gold) |
| **📎 Drag & Drop Upload** | Text, images, documents — analyzed by multimodal AI |
| **🖼️ Image Generation** | FLUX.1, Stable Diffusion XL from text prompt |
| **🖌️ Image Editing** | Upload image + edit prompt |
| **💾 Auto-Save** | Automatically saves every conversation to local SQLite |
| **📜 History** | Load, delete, and navigate through past conversations |
| **⚙️ External Config** | Add models via JSON — no code changes needed |
| **🚀 One-Click Start** | `starter.bat` / `starter.sh` — fully automated launch |

---

## 📸 Screenshot

![Chatty Nemotron Interface](<img width="3437" height="1230" alt="screenshoot" src="https://github.com/user-attachments/assets/e34b927d-c0b5-40e9-a2bc-f3a8c7fe0df4" />)

---

## 🎨 Available Themes

| Theme | File | Vibe |
|-------|------|------|
| Minimal Light | `white.png` | Clean, minimalist |
| Cyber Dark | `dark.jpeg` | Tech, neon cyan |
| Crimson Style | `crimson.jpeg` | Dramatic, red |
| Angelic White | `white 2.png` | Soft, warm |
| Deep Purple | `purple.jpeg` | Mystic, purple |
| **Midnight Navy** 🆕 | `navy.jpeg` | Corporate, professional |
| **Forest Sage** 🆕 | `sage.jpeg` | Natural, elegant |
| **Solar Gold** 🆕 | `gold.jpeg` | Luxury, premium |

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
| **Images** | `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp` | Visual analysis (VLM models) |
| **Documents** | `.pdf`, `.docx`, `.xlsx`, `.pptx` | Detects, waits for manual description |

### How It Works

1. **Drag & Drop** or click the upload zone
2. Preview appears in an expander
3. Type a message and press Enter
4. File is sent together with the message to the AI
5. Multimodal models (Kimi, MiniMax, Qwen, Mistral VLM) process the image directly

---

## 🖼️ Image Generation & Editing

### Generation
1. Select model: **FLUX.1** or **Stable Diffusion XL**
2. Write a descriptive prompt
3. Choose size: `1024x1024`, `512x512`, `256x256`
4. Click **"Generate"**

### Editing
1. **Upload** the original image
2. Write an edit prompt (e.g., *"Change the sky to a sunset"*)
3. Optional: check **"Use mask"** for selective editing
4. Click **"Edit"**

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
| Pillow | Image processing |
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
