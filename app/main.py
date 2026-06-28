import os
import sys
import base64
import json
import sqlite3
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    load_providers_config, get_available_models, get_client_for_model,
    stream_chat, get_fallback_chain
)

st.set_page_config(page_title="Chatty Nemotron", layout="centered")

# ============================================================
# CAILE
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG_DIR = os.path.join(BASE_DIR, "static", "backgrounds")
DB_PATH = os.path.join(BASE_DIR, "chat_history.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

# ============================================================
# CONFIGURATIE TEME
# ============================================================
THEME_MAP = {
    "Minimal Light": {
        "file": "white.png",
        "text": "#2a2522",
        "chat_bg": "rgba(255, 255, 255, 0.55)",
        "chat_border": "rgba(200, 190, 175, 0.6)",
        "input_bg": "rgba(255, 255, 255, 0.8)",
        "accent": "#8b7355",
        "overlay": "rgba(255,255,255,0.08)",
        "text_shadow": "0 1px 2px rgba(0,0,0,0.1)"
    },
    "Cyber Dark": {
        "file": "dark.jpeg",
        "text": "#e0e0e0",
        "chat_bg": "rgba(0, 0, 0, 0.45)",
        "chat_border": "rgba(0, 255, 255, 0.25)",
        "input_bg": "rgba(0, 0, 0, 0.6)",
        "accent": "#00ffff",
        "overlay": "rgba(0,0,0,0.40)",
        "text_shadow": "0 1px 3px rgba(0,0,0,0.5)"
    },
    "Deep Purple": {
        "file": "purple.jpeg",
        "text": "#f0e6ff",
        "chat_bg": "rgba(30, 0, 50, 0.5)",
        "chat_border": "rgba(180, 100, 255, 0.35)",
        "input_bg": "rgba(20, 0, 35, 0.6)",
        "accent": "#b464ff",
        "overlay": "rgba(0,0,0,0.35)",
        "text_shadow": "0 1px 3px rgba(0,0,0,0.5)"
    },
    "Cybertron": {
        "file": "cybertron.jpeg",
        "text": "#e0f7fa",
        "chat_bg": "rgba(0, 20, 40, 0.6)",
        "chat_border": "rgba(0, 200, 255, 0.35)",
        "input_bg": "rgba(0, 25, 50, 0.75)",
        "accent": "#00c8ff",
        "overlay": "rgba(0,0,0,0.40)",
        "text_shadow": "0 1px 3px rgba(0,0,0,0.5)"
    },
    "Midnight Navy": {
        "file": "navy.jpeg",
        "text": "#e8eaf6",
        "chat_bg": "rgba(15, 25, 50, 0.55)",
        "chat_border": "rgba(100, 149, 237, 0.35)",
        "input_bg": "rgba(20, 30, 60, 0.7)",
        "accent": "#6495ed",
        "overlay": "rgba(0,0,0,0.35)",
        "text_shadow": "0 1px 3px rgba(0,0,0,0.5)"
    },
    "Forest Sage": {
        "file": "sage.jpeg",
        "text": "#f1f8e9",
        "chat_bg": "rgba(30, 50, 35, 0.5)",
        "chat_border": "rgba(129, 199, 132, 0.4)",
        "input_bg": "rgba(35, 55, 40, 0.65)",
        "accent": "#81c784",
        "overlay": "rgba(0,0,0,0.30)",
        "text_shadow": "0 1px 3px rgba(0,0,0,0.5)"
    },
    "Solar Gold": {
        "file": "gold.jpeg",
        "text": "#fff8e1",
        "chat_bg": "rgba(30, 20, 5, 0.55)",
        "chat_border": "rgba(255, 193, 7, 0.3)",
        "input_bg": "rgba(40, 25, 5, 0.7)",
        "accent": "#ffc107",
        "overlay": "rgba(0,0,0,0.40)",
        "text_shadow": "0 1px 3px rgba(0,0,0,0.5)"
    }
}

# ============================================================
# HEADER CU LOGO CYBERTRON + INDICATOR ANIMAT (SMIL)
# ============================================================

def get_header_html(theme_name):
    cfg = THEME_MAP[theme_name]
    accent = cfg["accent"]
    cyber_b64 = get_image_base64("cybertron.jpeg")
    
    if theme_name == "Minimal Light":
        logo_color = "#2a2522"
        subtitle_color = "#5a5248"
    else:
        logo_color = "#ffffff"
        subtitle_color = "rgba(255,255,255,0.75)"
    
    if cyber_b64:
        logo_html = (
            f'<img src="{cyber_b64}" '
            f'style="width:56px;height:56px;border-radius:50%;object-fit:cover;'
            f'border:2px solid {accent};'
            f'box-shadow:0 0 16px {accent}90,0 0 32px {accent}40;'
            f'margin-right:14px;vertical-align:middle;'
            f'transition:transform 0.3s;">'
        )
    else:
        logo_html = (
            f'<span style="font-size:42px;margin-right:12px;'
            f'filter:drop-shadow(0 0 10px {accent}70);'
            f'vertical-align:middle;">🤖</span>'
        )
    
    # Indicator pulsant SVG (SMIL animation)
    pulse_svg = (
        f'<svg width="20" height="20" viewBox="0 0 20 20" '
        f'style="vertical-align:middle;margin-left:10px;">'
        f'<circle cx="10" cy="10" r="5" fill="{accent}" opacity="0.9">'
        f'<animate attributeName="r" values="5;8;5" dur="1.4s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0.9;0.3;0.9" dur="1.4s" repeatCount="indefinite"/>'
        f'</circle></svg>'
    )
    
    return f"""
    <div style="text-align: center; padding: 10px 0 4px 0; margin-bottom: 0px;">
        <div style="font-size: 34px; font-weight: 800; color: {logo_color}; text-shadow: 0 0 20px {accent}60, 0 2px 4px rgba(0,0,0,0.3); letter-spacing: 2px; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; line-height: 1.1; margin: 0; display: flex; align-items: center; justify-content: center; flex-wrap: wrap;">
            {logo_html}
            CHATTY NEMOTRON
            {pulse_svg}
        </div>
        <div style="font-size: 11px; color: {subtitle_color}; margin-top: 5px; letter-spacing: 4px; text-transform: uppercase; font-weight: 600; font-family: 'Segoe UI', system-ui, sans-serif; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
            Multi-Model AI DevOps Assistant
        </div>
        <div style="width: 100px; height: 2px; background: linear-gradient(90deg, transparent, {accent}, transparent); margin: 10px auto; border-radius: 2px; opacity: 0.8;"></div>
    </div>
    """

# ============================================================
# DATABASE
# ============================================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            model TEXT,
            theme TEXT,
            messages TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_conversation(title, model, theme, messages, conv_id=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    messages_json = json.dumps(messages)
    
    if conv_id:
        c.execute('''
            UPDATE history SET title=?, model=?, theme=?, messages=?, updated_at=?
            WHERE id=?
        ''', (title, model, theme, messages_json, now, conv_id))
    else:
        c.execute('''
            INSERT INTO history (title, model, theme, messages, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, model, theme, messages_json, now, now))
        conv_id = c.lastrowid
    
    conn.commit()
    conn.close()
    return conv_id

def get_all_conversations():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT id, title, model, theme, created_at, updated_at 
        FROM history 
        ORDER BY updated_at DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return rows

def get_conversation(conv_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM history WHERE id=?', (conv_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'title': row[1],
            'model': row[2],
            'theme': row[3],
            'messages': json.loads(row[4]),
            'created_at': row[5],
            'updated_at': row[6]
        }
    return None

def delete_conversation(conv_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM history WHERE id=?', (conv_id,))
    conn.commit()
    conn.close()

def generate_title(messages):
    for msg in messages:
        if msg["role"] == "user":
            content = msg["content"]
            if isinstance(content, str):
                title = content[:50]
                if len(content) > 50:
                    title += "..."
                return title
            elif isinstance(content, list):
                for part in content:
                    if part.get("type") == "text":
                        title = part["text"][:50]
                        if len(part['text']) > 50:
                            title += "..."
                        return title
    return f"Chat {datetime.now().strftime('%H:%M %d/%m')}"

# ============================================================
# FUNCTII FISIERE
# ============================================================

def read_text_file(file_path):
    encodings = ['utf-8', 'latin-1', 'cp1252']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.read()
        except:
            continue
    return None

def read_image_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def process_uploaded_file(uploaded_file):
    file_ext = Path(uploaded_file.name).suffix.lower()
    
    temp_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    if file_ext in ['.txt', '.py', '.md', '.json', '.yaml', '.yml', '.csv', '.log', '.sh', '.bat', '.ps1', '.js', '.html', '.css', '.xml', '.sql']:
        content = read_text_file(temp_path)
        if content:
            return {
                "type": "text",
                "content": f"📄 **Fisier:** `{uploaded_file.name}`\n\n```\n{content[:8000]}{'...' if len(content) > 8000 else ''}\n```",
                "raw": content,
                "path": temp_path
            }
    
    elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']:
        b64_img = read_image_base64(temp_path)
        return {
            "type": "image",
            "content": f"🖼️ **Imagine:** `{uploaded_file.name}`",
            "raw": b64_img,
            "mime": f"image/{'png' if file_ext == '.png' else 'jpeg' if file_ext in ['.jpg', '.jpeg'] else 'webp'}",
            "path": temp_path
        }
    
    elif file_ext in ['.pdf', '.docx', '.doc', '.xlsx', '.pptx']:
        size_kb = len(uploaded_file.getvalue()) / 1024
        return {
            "type": "document",
            "content": f"📎 **Document:** `{uploaded_file.name}` ({size_kb:.1f} KB)\n\n*Documentul a fost atasat. Poti cere analiza continutului.*",
            "raw": None,
            "path": temp_path
        }
    
    else:
        return {
            "type": "unknown",
            "content": f"📎 **Fisier:** `{uploaded_file.name}`\n\n*Tip de fisier necunoscut. Poti descrie continutul manual.*",
            "raw": None,
            "path": temp_path
        }

# ============================================================
# IMAGINI BASE64
# ============================================================
@st.cache_data
def get_image_base64(filename):
    filepath = os.path.join(BG_DIR, filename)
    if not os.path.exists(filepath):
        return None
    with open(filepath, "rb") as f:
        data = f.read()
    ext = os.path.splitext(filename)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"

# ============================================================
# CSS CUSTOM
# ============================================================
def get_custom_css(theme_name):
    cfg = THEME_MAP[theme_name]
    img_b64 = get_image_base64(cfg["file"])
    
    if img_b64 is None:
        bg_css = f"background: linear-gradient(135deg, {cfg['chat_bg']} 0%, #1a1a2e 100%);"
    else:
        bg_css = f"background-image: url('{img_b64}'); background-size: cover; background-position: center; background-attachment: fixed;"
    
    return f"""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
        {bg_css}
        color: {cfg['text']} !important;
    }}
    
    [data-testid="stAppViewContainer"] > .main {{
        background: {cfg['overlay']} !important;
    }}
    
    [data-testid="stHeader"],
    [data-testid="stHeader"] > div,
    [data-testid="stHeader"] > div > div,
    header, .stAppHeader,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stTopBar"] {{
        background-color: transparent !important;
        background-image: none !important;
        background: transparent !important;
    }}
    
    [data-testid="stBottom"], [data-testid="stBottom"] > div {{
        background-color: transparent !important;
        background-image: none !important;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {cfg['chat_bg']} !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid {cfg['chat_border']};
    }}
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] span {{
        color: {cfg['text']} !important;
    }}
    
    .stChatMessage {{
        background: {cfg['chat_bg']} !important;
        backdrop-filter: blur(12px);
        border: 1px solid {cfg['chat_border']};
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        color: {cfg['text']} !important;
    }}
    
    .stChatMessage [data-testid="stMarkdownContainer"] p {{
        color: {cfg['text']} !important;
    }}
    
    p, h1, h2, h3, h4, h5, span, 
    .stMarkdown, .stSelectbox label,
    div[data-testid="stMarkdownContainer"] p {{
        color: {cfg['text']} !important;
        text-shadow: {cfg['text_shadow']};
    }}
    
    div[data-baseweb="select"] > div {{
        background-color: {cfg['input_bg']} !important;
        color: {cfg['text']} !important;
        border: 1px solid {cfg['chat_border']} !important;
    }}
    
    div[data-testid="stChatInput"] {{
        background-color: {cfg['input_bg']} !important;
        border: 1px solid {cfg['chat_border']} !important;
    }}
    
    div[data-testid="stChatInput"] textarea {{
        color: {cfg['text']} !important;
    }}
    
    .stButton button {{
        background: {cfg['chat_bg']} !important;
        border: 1px solid {cfg['chat_border']} !important;
        color: {cfg['text']} !important;
        border-radius: 8px;
        transition: all 0.2s ease;
        text-shadow: {cfg['text_shadow']};
    }}
    
    .stButton button:hover {{
        background: {cfg['input_bg']} !important;
        border-color: {cfg['accent']} !important;
        color: {cfg['accent']} !important;
        box-shadow: 0 0 12px {cfg['accent']}40;
    }}
    
    .drag-drop-zone {{
        border: 2px dashed {cfg['accent']}60;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        background: {cfg['chat_bg']};
        transition: all 0.3s ease;
        cursor: pointer;
    }}
    
    .drag-drop-zone:hover {{
        border-color: {cfg['accent']};
        background: {cfg['input_bg']};
    }}
    
    .drag-drop-zone.dragover {{
        border-color: {cfg['accent']};
        background: {cfg['accent']}20;
        transform: scale(1.02);
    }}
    
    ::-webkit-scrollbar {{ width: 8px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: {cfg['accent']}80; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {cfg['accent']}; }}
    </style>
    """

# ============================================================
# INCARCA CONFIG MODELE
# ============================================================
config = load_providers_config()
available_models = get_available_models(config)

if not available_models:
    st.error("🔴 Nicio cheie API configurată! Verifică `.env` și `config/providers.json`")
    st.stop()

text_models = [m for m in available_models if m["provider_type"] != "image_generation"]

model_labels = ["Auto (Fallback automat)"] + [m["label"] for m in text_models]
model_lookup = {m["label"]: m for m in text_models}

# ============================================================
# INITIALIZARE SESIUNE
# ============================================================
init_db()

if "theme" not in st.session_state:
    st.session_state.theme = "Cybertron"
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Ești un asistent DevOps de elită. Răspunzi clar și tehnic."}
    ]
if "current_conv_id" not in st.session_state:
    st.session_state.current_conv_id = None
if "history_refresh" not in st.session_state:
    st.session_state.history_refresh = 0
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "pending_file" not in st.session_state:
    st.session_state.pending_file = None

st.markdown(get_custom_css(st.session_state.theme), unsafe_allow_html=True)
st.markdown(get_header_html(st.session_state.theme), unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.title("🎨 Setări Vizuale")
    
    tema_aleasa = st.selectbox(
        "Alege tema:", 
        options=list(THEME_MAP.keys()),
        index=list(THEME_MAP.keys()).index(st.session_state.theme)
    )
    
    if tema_aleasa != st.session_state.theme:
        st.session_state.theme = tema_aleasa
        st.rerun()
        
    st.markdown("---")
    
    if st.session_state.current_conv_id:
        st.caption(f"💾 Conversație #{st.session_state.current_conv_id}")
    else:
        st.caption("📝 Conversație nouă (nesalvată)")
    
    st.caption(f"🖼️ Fundal: `{THEME_MAP[st.session_state.theme]['file']}`")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Chat", use_container_width=True):
            st.session_state.messages = [
                {"role": "system", "content": "Ești un asistent DevOps de elită. Răspunzi clar și tehnic."}
            ]
            st.session_state.current_conv_id = None
            st.session_state.uploaded_files = []
            st.session_state.pending_file = None
            st.rerun()
    
    with col2:
        if st.button("💾 Save Now", use_container_width=True):
            if len(st.session_state.messages) > 1:
                title = generate_title(st.session_state.messages)
                conv_id = save_conversation(
                    title=title,
                    model=st.session_state.get("last_model_used", "Auto"),
                    theme=st.session_state.theme,
                    messages=st.session_state.messages,
                    conv_id=st.session_state.current_conv_id
                )
                st.session_state.current_conv_id = conv_id
                st.session_state.history_refresh += 1
                st.toast(f"✅ Salvat: *{title}*")
                st.rerun()
            else:
                st.warning("Nimic de salvat încă.")
    
    st.markdown("---")
    
    # ============================================================
    # HISTORY
    # ============================================================
    st.subheader("📜 History")
    
    conversations = get_all_conversations()
    
    if not conversations:
        st.info("Nu există conversații salvate încă.")
    else:
        for conv in conversations:
            conv_id, title, model, theme, created_at, updated_at = conv
            
            with st.container():
                col_title, col_load, col_del = st.columns([3, 1, 1])
                
                with col_title:
                    st.markdown(f"**{title}**")
                    st.caption(f"{updated_at[:16]} | {model}")
                
                with col_load:
                    if st.button("📂", key=f"load_{conv_id}", help="Încarcă conversația"):
                        data = get_conversation(conv_id)
                        if data:
                            st.session_state.messages = data['messages']
                            st.session_state.theme = data['theme']
                            st.session_state.current_conv_id = data['id']
                            st.rerun()
                
                with col_del:
                    if st.button("🗑️", key=f"del_{conv_id}", help="Șterge conversația"):
                        delete_conversation(conv_id)
                        if st.session_state.current_conv_id == conv_id:
                            st.session_state.current_conv_id = None
                        st.session_state.history_refresh += 1
                        st.rerun()
                
                st.markdown("<hr style='margin: 8px 0; opacity: 0.3;'>", unsafe_allow_html=True)

# ============================================================
# AFISARE MESAJE
# ============================================================
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            if isinstance(message["content"], str):
                st.write(message["content"])
            elif isinstance(message["content"], list):
                for part in message["content"]:
                    if part.get("type") == "text":
                        st.write(part["text"])
                    elif part.get("type") == "image_url":
                        st.image(part["image_url"]["url"], caption="🖼️ Imagine uploadată")

# ============================================================
# DRAG & DROP ZONE + UPLOAD
# ============================================================

st.markdown("---")

col_drag, col_info = st.columns([1, 3])

with col_drag:
    uploaded_file = st.file_uploader(
        "📎 Drag & Drop sau click pentru fișier",
        type=["txt", "py", "md", "json", "yaml", "csv", "png", "jpg", "jpeg", "gif", "webp", "pdf", "docx"],
        label_visibility="collapsed",
        key="main_file_uploader"
    )

file_context = ""
file_data = None

if uploaded_file is not None:
    file_data = process_uploaded_file(uploaded_file)
    st.session_state.pending_file = file_data
    
    with st.expander(f"📎 {uploaded_file.name} - Preview (va fi trimis cu următorul mesaj)", expanded=True):
        if file_data["type"] == "image":
            st.image(f"data:{file_data['mime']};base64,{file_data['raw']}", caption=uploaded_file.name)
            st.caption("💡 Această imagine va fi analizată de modelul AI selectat.")
        elif file_data["type"] == "text":
            st.markdown(file_data["content"])
            st.caption(f"📊 {len(file_data['raw'])} caractere")
        else:
            st.markdown(file_data["content"])
        
        if st.button("❌ Elimină fișierul", key="remove_file"):
            st.session_state.pending_file = None
            st.rerun()

if st.session_state.pending_file:
    st.info(f"📎 Fișier pregătit: `{uploaded_file.name if uploaded_file else '...'}`. Scrie un mesaj și apasă Enter pentru a trimite.")

# ============================================================
# SELECTOR MODEL
# ============================================================
mod_selectat = st.selectbox(
    "🤖 Selectează modelul AI:",
    options=model_labels,
    format_func=lambda x: x if x == "Auto (Fallback automat)" else f"{model_lookup[x]['label']} — {model_lookup[x]['description']}"
)

# ============================================================
# LOGICA CHAT
# ============================================================
if user_input := st.chat_input("Cu ce te pot ajuta în infrastructura azi?"):

    final_input = user_input
    pending = st.session_state.get("pending_file")
    
    with st.chat_message("user"):
        st.write(user_input)
        if pending:
            st.caption(f"📎 Cu fișier: `{pending.get('path', 'upload').split('/')[-1] if isinstance(pending.get('path'), str) else 'upload'}`")
    
    if pending and pending["type"] == "image":
        message_content = [
            {"type": "text", "text": user_input},
            {"type": "image_url", "image_url": {"url": f"data:{pending['mime']};base64,{pending['raw']}"}}
        ]
        st.session_state.messages.append({
            "role": "user",
            "content": message_content
        })
    elif pending and pending["type"] == "text":
        final_input = f"{user_input}\n\n[Fișier atașat]\n```\n{pending['raw'][:3000]}\n```"
        st.session_state.messages.append({"role": "user", "content": final_input})
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
    
    st.session_state.pending_file = None

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        full_reasoning = ""
        generare_reusita = False
        
        fallback_models = get_fallback_chain(text_models, mod_selectat)
        st.session_state.last_model_used = mod_selectat
        
        for model_cfg in fallback_models:
            try:
                client = get_client_for_model(model_cfg)
                
                for chunk_type, text in stream_chat(client, model_cfg, st.session_state.messages):
                    if chunk_type == "reasoning":
                        full_reasoning += text
                    else:
                        full_response += text
                    
                    display = ""
                    if full_reasoning:
                        display += f"🧠 *Thinking...*\n\n{full_reasoning}\n\n---\n\n"
                    display += full_response
                    response_placeholder.markdown(display + " ▌")
                
                response_placeholder.empty()
                if full_reasoning:
                    with st.expander("🧠 Chain of Thought"):
                        st.markdown(full_reasoning)
                    st.markdown(full_response)
                else:
                    response_placeholder.markdown(full_response)
                
                generare_reusita = True
                st.session_state.last_successful_model = model_cfg["label"]
                break
                
            except Exception as e:
                st.warning(f"⚠️ Eroare la `{model_cfg['label']}` ({model_cfg['provider']}): {str(e)[:120]}")
                continue
        
        if not generare_reusita:
            st.error("❌ Toate modelele au eșuat. Verifică conexiunea sau limitele API.")
            full_response = "Eroare: Nu s-a putut genera un răspuns."
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    title = generate_title(st.session_state.messages)
    conv_id = save_conversation(
        title=title,
        model=st.session_state.get("last_successful_model", mod_selectat),
        theme=st.session_state.theme,
        messages=st.session_state.messages,
        conv_id=st.session_state.current_conv_id
    )
    st.session_state.current_conv_id = conv_id
    st.session_state.history_refresh += 1