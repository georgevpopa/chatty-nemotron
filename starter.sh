#!/bin/bash

# Chatty Nemotron - Starter (Linux/Mac)

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=========================================="
echo "   🤖 Chatty Nemotron - Pornire..."
echo "=========================================="

# Verifică venv
if [ ! -f ".venv/bin/python" ]; then
    echo "❌ Virtual environment negăsit!"
    echo "   Rulează mai întâi: python3 setup.py"
    exit 1
fi

# Verifică dependențe
if ! .venv/bin/python -c "import streamlit, openai, dotenv" 2>/dev/null; then
    echo "📥 Instalare dependențe..."
    .venv/bin/pip install -r requirements.txt
fi

# Verifică fișiere
if [ ! -f "app/main.py" ]; then
    echo "❌ app/main.py negăsit!"
    exit 1
fi

# Porneste Streamlit
echo "✅ Pornire Streamlit pe http://localhost:8880"
echo "⏹️  Apasă Ctrl+C pentru oprire"
echo "=========================================="

.venv/bin/streamlit run app/main.py --server.port=8880 --server.headless=true

echo ""
echo "⏹️  Streamlit oprit."
