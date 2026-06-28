FROM python:3.11-slim

WORKDIR /app

# Instalează dependențe sistem
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiază și instalează dependențe Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiază aplicația
COPY . .

# Creează directoare necesare
RUN mkdir -p uploads edits static/backgrounds

# Port
EXPOSE 8880

# Pornire
CMD [".venv/bin/streamlit", "run", "app/main.py", "--server.port=8880", "--server.address=0.0.0.0"]
