import streamlit as st
import json
import os
from datetime import datetime

# 1. Seting dasar halaman agar full screen dan bersih tanpa komponen bawaan Streamlit
st.set_page_config(page_title="Zephyr Workspace", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background: transparent !important; }
    iframe { width: 100%; border: none; background: transparent !important; }
    </style>
""", unsafe_allow_html=True)

# 2. Kelola database JSON lokal otomatis (Anti-Error)
DATA_FILE = "users_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

db = load_data()

# Session State Pengguna Aktif
if 'user' not in st.session_state:
    st.session_state['user'] = None

# 3. Tangkap kiriman data balik dari JavaScript HTML melalui URL Parameter
query_params = st.query_params

if "action" in query_params:
    action = query_params["action"]
    u = query_params.get("u", "").strip().lower()
    p = query_params.get("p", "")
    
    if action == "login":
        if u in db and db[u]["password"] == p:
            st.session_state['user'] = u
        st.query_params.clear()
        st.rerun()
        
    elif action == "register":
        if u and p and u not in db:
            db[u] = {"password": p, "tasks": [], "mood_history": {}}
            save_data(db)
        st.query_params.clear()
        st.rerun()

if st.session_state['user']:
    current_user = st.session_state['user']
    
    if "save_tasks" in query_params:
        raw_tasks = query_params.get("tasks_data", "[]")
        try:
            db[current_user]["tasks"] = json.loads(raw_tasks)
            save_data(db)
        except: pass
        st.query_params.clear()
        st.rerun()
        
    if "save_mood" in query_params:
        selected_mood = query_params.get("mood", "biasa")
        today_str = datetime.today().strftime('%Y-%m-%d')
        db[current_user]["mood_history"][today_str] = selected_mood
        save_data(db)
        st.query_params.clear()
        st.rerun()
        
    if "logout" in query_params:
        st.session_state['user'] = None
        st.query_params.clear()
        st.rerun()

# 4. JEMBATAN RENDER: Menampilkan File HTML Asli Kamu Secara Hidup!
html_path = "templates/Product.html"

if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    # Ambil data spesifik user jika sudah berhasil masuk ke aplikasi
    current_user = st.session_state['user'] if st.session_state['user'] else ""
    user_data = db.get(current_user, {"tasks": [], "mood_history": {}})
    
    # Suntikkan variabel Python ke memori JavaScript browser agar dibaca otomatis oleh Product.html
    data_injection = f"""
    <script>
        window.current_user = "{current_user}";
        window.initial_tasks = {json.dumps(user_data.get("tasks", []))};
        window.initial_moods = {json.dumps(user_data.get("mood_history", {{}}))};
    </script>
    """
    full_live_html = html_content.replace("<head>", f"<head>{data_injection}")
    
    # PERBAIKAN UTAMA: Menggunakan komponen html murni agar tidak ternder sebagai teks biasa!
    st.components.v1.html(full_live_html, height=1000, scroller=True)
else:
    st.error("File 'templates/Product.html' tidak ditemukan! Pastikan foldernya sudah benar di VS Code.")
