import os
import sys
import base64
import json
import sqlite3
import io
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    load_providers_config, get_available_models, get_client_for_model,
    stream_chat, get_fallback_chain,
    generate_image, edit_image, b64_to_image,
    create_image_mask, resize_image_for_api  ### NOU ###
)

st.set_page_config(page_title="Chatty Nemotron", layout="centered")

# ============================================================
# CAILE
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG_DIR = os.path.join(BASE_DIR, "static", "backgrounds")
DB_PATH = os.path.join(BASE_DIR, "chat_history.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
EDIT_DIR = os.path.join(BASE_DIR, "edits")  ### NOU ###

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EDIT_DIR, exist_ok=True)  ### NOU ###

# ============================================================
# CONFIGURATIE TEME
# ============================================================
THEME_MAP = {
    # === TEME EXISTENTE ===
    "Minimal Light": {
        "file": "white.png",
        "text": "#2a2522",
        "chat_bg": "rgba(255, 255, 255, 0.55)",
        "chat_border": "rgba(200, 190, 175, 0.6)",
        "input_bg": "rgba(255, 255, 255, 0.8)",
        "accent": "#8b7355"
    },
    "Cyber Dark": {
        "file": "dark.jpeg",
        "text": "#e0e0e0",
        "chat_bg": "rgba(0, 0, 0, 0.45)",
        "chat_border": "rgba(0, 255, 255, 0.25)",
        "input_bg": "rgba(0, 0, 0, 0.6)",
        "accent": "#00ffff"
    },
    "Crimson Style": {
        "file": "crimson.jpeg",
        "text": "#ffffff",
        "chat_bg": "rgba(40, 0, 0, 0.5)",
        "chat_border": "rgba(220, 20, 60, 0.4)",
        "input_bg": "rgba(30, 0, 0, 0.6)",
        "accent": "#dc143c"
    },
    "Angelic White": {
        "file": "white 2.png",
        "text": "#2a2522",
        "chat_bg": "rgba(255, 255, 255, 0.6)",
        "chat_border": "rgba(220, 210, 195, 0.7)",
        "input_bg": "rgba(255, 255, 255, 0.85)",
        "accent": "#8b7355"
    },
    "Deep Purple": {
        "file": "purple.jpeg",
        "text": "#f0e6ff",
        "chat_bg": "rgba(30, 0, 50, 0.5)",
        "chat_border": "rgba(180, 100, 255, 0.35)",
        "input_bg": "rgba(20, 0, 35, 0.6)",
        "accent": "#b464ff"
    },
    
    # === TEME NOI PROFESIONALE ===
    "Midnight Navy": {
        "file": "navy.jpeg",
        "text": "#e8eaf6",           # Albastru foarte deschis
        "chat_bg": "rgba(15, 25, 50, 0.55)",      # Navy transparent
        "chat_border": "rgba(100, 149, 237, 0.35)",  # Cornflower blue
        "input_bg": "rgba(20, 30, 60, 0.7)",      # Navy mai inchis
        "accent": "#6495ed"          # Cornflower blue
    },
    "Forest Sage": {
        "file": "sage.jpeg",
        "text": "#f1f8e9",           # Verde foarte deschis
        "chat_bg": "rgba(30, 50, 35, 0.5)",       # Verde padure transparent
        "chat_border": "rgba(129, 199, 132, 0.4)",   # Sage green
        "input_bg": "rgba(35, 55, 40, 0.65)",     # Verde mai inchis
        "accent": "#81c784"          # Sage green
    },
    "Solar Gold": {
        "file": "gold.jpeg",
        "text": "#fff8e1",            # Crem-auriu
        "chat_bg": "rgba(30, 20, 5, 0.55)",       # Negru-auriu transparent
        "chat_border": "rgba(255, 193, 7, 0.3)",   # Amber gold
        "input_bg": "rgba(40, 25, 5, 0.7)",       # Maro-inchis
        "accent": "#ffc107"           # Amber gold
    }
}

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
                        if len(part["text"]) > 50:
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
    
    # Text files
    if file_ext in ['.txt', '.py', '.md', '.json', '.yaml', '.yml', '.csv', '.log', '.sh', '.bat', '.ps1', '.js', '.html', '.css', '.xml', '.sql']:
        content = read_text_file(temp_path)
        if content:
            return {
                "type": "text",
                "content": f"📄 **Fisier:** `{uploaded_file.name}`\n\n```\n{content[:8000]}{'...' if len(content) > 8000 else ''}\n```",
                "raw": content,
                "path": temp_path
            }
    
    # Images
    elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']:
        b64_img = read_image_base64(temp_path)
        return {
            "type": "image",
            "content": f"🖼️ **Imagine:** `{uploaded_file.name}`",
            "raw": b64_img,
            "mime": f"image/{'png' if file_ext == '.png' else 'jpeg' if file_ext in ['.jpg', '.jpeg'] else 'webp'}",
            "path": temp_path
        }
    
    # Documents
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
        bg_css = f"background: linear-gradient(135deg, {cfg['chat_bg']} 0%, #000000 100%);"
    else:
        bg_css = f"background-image: url('{img_b64}'); background-size: cover; background-position: center; background-attachment: fixed;"
    
    return f"""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
        {bg_css}
        color: {cfg['text']} !important;
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
    }}
    .stButton button:hover {{
        background: {cfg['input_bg']} !important;
        border-color: {cfg['accent']} !important;
        color: {cfg['accent']} !important;
        box-shadow: 0 0 12px {cfg['accent']}40;
    }}
    
    /* ========== DRAG & DROP ZONE ========== */  ### NOU ###
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
image_models = [m for m in available_models if m["provider_type"] == "image_generation"]

model_labels = ["Auto (Fallback automat)"] + [m["label"] for m in text_models]
model_lookup = {m["label"]: m for m in text_models}
image_model_lookup = {m["label"]: m for m in image_models}

# ============================================================
# INITIALIZARE SESIUNE
# ============================================================
init_db()

if "theme" not in st.session_state:
    st.session_state.theme = "Crimson Style"
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
if "generated_images" not in st.session_state:
    st.session_state.generated_images = []
if "pending_file" not in st.session_state:  ### NOU ###
    st.session_state.pending_file = None

st.markdown(get_custom_css(st.session_state.theme), unsafe_allow_html=True)

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
            st.session_state.generated_images = []
            st.session_state.pending_file = None  ### NOU ###
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
    # TAB: GENERARE IMAGINI  ### NOU ###
    # ============================================================
    if image_models:
        st.markdown("---")
        
        # Tab selector
        img_tab = st.radio(
            "🎨 Mod imagine:",
            ["Generare", "Editare"],
            horizontal=True,
            key="img_tab"
        )
        
        img_model_label = st.selectbox(
            "Model imagine:",
            options=[m["label"] for m in image_models],
            key="img_model_select"
        )
        
        if img_tab == "Generare":
            # === GENERARE ===
            img_prompt = st.text_area(
                "Prompt imagine:",
                placeholder="Descrie imaginea dorita...",
                key="img_prompt_gen"
            )
            img_size = st.selectbox(
                "Dimensiune:",
                ["1024x1024", "512x512", "256x256"],
                key="img_size_gen"
            )
            
            if st.button("🖼️ Generează", use_container_width=True, key="gen_img_btn"):
                if img_prompt.strip():
                    with st.spinner("Generez imaginea..."):
                        try:
                            model_cfg = image_model_lookup[img_model_label]
                            client = get_client_for_model(model_cfg)
                            images_b64 = generate_image(client, model_cfg, img_prompt, size=img_size)
                            
                            for idx, img_b64 in enumerate(images_b64):
                                st.session_state.generated_images.append({
                                    "prompt": img_prompt,
                                    "model": img_model_label,
                                    "b64": img_b64,
                                    "type": "generated"
                                })
                                st.image(b64_to_image(img_b64), caption=f"🎨 {img_prompt[:50]}...")
                            
                            st.success("✅ Imagine generată!")
                        except Exception as e:
                            st.error(f"❌ Eroare generare: {str(e)[:200]}")
                else:
                    st.warning("Scrie un prompt mai întâi.")
        
        else:
            # === EDITARE ===
            st.caption("🖌️ Upload imagine + descrie ce vrei schimbat")
            
            edit_image_file = st.file_uploader(
                "Alege imaginea:",
                type=["png", "jpg", "jpeg"],
                key="edit_img_upload"
            )
            
            edit_prompt = st.text_area(
                "Prompt editare:",
                placeholder="Ex: Schimba cerul in apus de soare, Adauga un dragon...",
                key="edit_prompt"
            )
            
            use_mask = st.checkbox("Folosește mască (selectează zona de editat)", key="use_mask")
            
            if use_mask:
                st.info("💡 Masca implicită editează întreaga imagine. Pentru selecție fină, folosește un editor extern.")
            
            if st.button("🖌️ Editează", use_container_width=True, key="edit_img_btn"):
                if not edit_image_file:
                    st.warning("Upload o imagine mai întâi.")
                elif not edit_prompt.strip():
                    st.warning("Scrie un prompt de editare.")
                else:
                    with st.spinner("Editez imaginea..."):
                        try:
                            # Salvează imaginea uploadată
                            edit_path = os.path.join(EDIT_DIR, edit_image_file.name)
                            with open(edit_path, "wb") as f:
                                f.write(edit_image_file.getvalue())
                            
                            # Redimensionează dacă e prea mare
                            resized_path = resize_image_for_api(edit_path)
                            
                            model_cfg = image_model_lookup[img_model_label]
                            client = get_client_for_model(model_cfg)
                            
                            # Generează mască dacă e necesar
                            mask_path = None
                            if use_mask:
                                _, mask = create_image_mask(resized_path)
                                mask_path = resized_path.replace(".", "_mask.")
                                mask.save(mask_path)
                            
                            # Editează
                            images_b64 = edit_image(
                                client, model_cfg, resized_path, edit_prompt, mask_path
                            )
                            
                            for idx, img_b64 in enumerate(images_b64):
                                st.session_state.generated_images.append({
                                    "prompt": edit_prompt,
                                    "model": img_model_label,
                                    "b64": img_b64,
                                    "type": "edited",
                                    "original": edit_image_file.name
                                })
                                st.image(b64_to_image(img_b64), caption=f"🖌️ {edit_prompt[:50]}...")
                            
                            st.success("✅ Imagine editată!")
                            
                            # Curăță fișiere temporare
                            for temp in [resized_path, mask_path]:
                                if temp and os.path.exists(temp):
                                    os.remove(temp)
                                    
                        except Exception as e:
                            st.error(f"❌ Eroare editare: {str(e)[:200]}")
        
        # Afișează istoric imagini
        if st.session_state.generated_images:
            st.markdown("---")
            st.caption(f"📸 {len(st.session_state.generated_images)} imagini")
            
            for i, img_data in enumerate(reversed(st.session_state.generated_images[-5:])):
                icon = "🎨" if img_data.get("type") == "generated" else "🖌️"
                with st.expander(f"{icon} #{len(st.session_state.generated_images) - i}"):
                    st.image(b64_to_image(img_data["b64"]), caption=img_data["prompt"][:80])
                    if img_data.get("original"):
                        st.caption(f"Original: {img_data['original']}")

# ============================================================
# AFISARE MESAJE
# ============================================================
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            # Conținut text sau multimodal
            if isinstance(message["content"], str):
                st.write(message["content"])
            elif isinstance(message["content"], list):
                for part in message["content"]:
                    if part.get("type") == "text":
                        st.write(part["text"])
                    elif part.get("type") == "image_url":
                        st.image(part["image_url"]["url"], caption="🖼️ Imagine uploadată")
            
            # Imagini generate atașate mesajului
            if message.get("image_b64"):
                st.image(b64_to_image(message["image_b64"]), caption="🎨 Imagine generată")

# ============================================================
# DRAG & DROP ZONE + UPLOAD  ### NOU ###
# ============================================================

st.markdown("---")

# Zona de drag & drop (file uploader stilizat)
col_drag, col_info = st.columns([1, 3])

with col_drag:
    # File uploader principal (acceptă drag & drop nativ Streamlit)
    uploaded_file = st.file_uploader(
        "📎 Drag & Drop sau click pentru fișier",
        type=["txt", "py", "md", "json", "yaml", "csv", "png", "jpg", "jpeg", "gif", "webp", "pdf", "docx"],
        label_visibility="collapsed",
        key="main_file_uploader"
    )

# Procesează fișierul uploadat
file_context = ""
file_data = None

if uploaded_file is not None:
    file_data = process_uploaded_file(uploaded_file)
    st.session_state.pending_file = file_data  # Salvează pentru când trimite mesaj
    
    # Preview în expander
    with st.expander(f"📎 {uploaded_file.name} - Preview (va fi trimis cu următorul mesaj)", expanded=True):
        if file_data["type"] == "image":
            st.image(f"data:{file_data['mime']};base64,{file_data['raw']}", caption=uploaded_file.name)
            st.caption("💡 Această imagine va fi analizată de modelul AI selectat.")
        elif file_data["type"] == "text":
            st.markdown(file_data["content"])
            st.caption(f"📊 {len(file_data['raw'])} caractere")
        else:
            st.markdown(file_data["content"])
        
        # Buton pentru eliminare
        if st.button("❌ Elimină fișierul", key="remove_file"):
            st.session_state.pending_file = None
            st.rerun()

# Afișează indicator dacă există fișier pending
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

    # Construiește mesajul final
    final_input = user_input
    pending = st.session_state.get("pending_file")
    
    with st.chat_message("user"):
        st.write(user_input)
        if pending:
            st.caption(f"📎 Cu fișier: `{pending.get('path', 'upload').split('/')[-1] if isinstance(pending.get('path'), str) else 'upload'}`")
    
    # Construiește mesajul pentru API
    if pending and pending["type"] == "image":
        # Mesaj multimodal (text + imagine) pentru modele vision
        message_content = [
            {"type": "text", "text": user_input},
            {"type": "image_url", "image_url": {"url": f"data:{pending['mime']};base64,{pending['raw']}"}}
        ]
        st.session_state.messages.append({
            "role": "user",
            "content": message_content
        })
    elif pending and pending["type"] == "text":
        # Anexează conținutul textului la prompt
        final_input = f"{user_input}\n\n[Fișier atașat]\n```\n{pending['raw'][:3000]}\n```"
        st.session_state.messages.append({"role": "user", "content": final_input})
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Reset pending file
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
    
    # Auto-save
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