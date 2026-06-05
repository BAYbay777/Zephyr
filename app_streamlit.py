import streamlit as st
import json
import os
from datetime import datetime

# 1. Atur konfigurasi halaman agar penuh dan bersih tanpa bumbu Streamlit
st.set_page_config(page_title="Zephyr Workspace", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background: transparent !important; }
    iframe { width: 100%; border: none; background: transparent !important; }
    </style>
""", unsafe_allow_html=True)

# 2. Sinkronisasi Database JSON tunggal (Aman & tervalidasi)
USERS_FILE = "users_data.json"

def load_data():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_data(data):
    with open(USERS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

db = load_data()

# Inisialisasi Session Pengguna
if 'user' not in st.session_state:
    st.session_state['user'] = None

# Menerima instruksi data kiriman balik dari Javascript HTML lewat URL parameter
query_params = st.query_params

# A. Handle Aksi Login & Register dari HTML
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

# B. Handle Aksi Simpan Tugas & Checklist dari HTML
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

# ==========================================
# 3. RENDER PEMBACAAN FILE HTML ASLI KAMU
# ==========================================
if st.session_state['user'] is None:
    # JIKA BELUM LOGIN: Baca file Product.html dan paksa tampilkan card Login/Register di awal
    if os.path.exists("templates/Product.html"):
        with open("templates/Product.html", "r", encoding="utf-8") as f:
            html_content = f.read()
            
        # Suntikan Javascript agar modal login langsung terbuka otomatis di awal secara terpisah
        injection = """
        <script>
        window.addEventListener('DOMContentLoaded', () => {
            if(typeof showAuthModal === 'function') { showAuthModal(); }
            else { document.getElementById('authModal').style.display = 'flex'; }
        });
        </script>
        """
        st.components.v1.html(html_content + injection, height=800, scroller=True)
else:
    # JIKA SUDAH LOGIN: Lempar data list tugas dan riwayat mood user ke dalam HTML asli kamu
    current_user = st.session_state['user']
    user_data = db.get(current_user, {"tasks": [], "mood_history": {}})
    
    if os.path.exists("templates/Product.html"):
        with open("templates/Product.html", "r", encoding="utf-8") as f:
            html_content = f.read()
            
        # Kirim data Python ke variabel Javascript di HTML agar To-Do List & Mood terisi realtime
        data_injection = f"""
        <script>
            window.current_user = "{current_user}";
            window.initial_tasks = {json.dumps(user_data.get("tasks", []))};
            window.initial_moods = {json.dumps(user_data.get("mood_history", {{}}))};
        </script>
        """
        # Gabungkan data dan tampilkan halaman dashboard aslimu
        full_html = html_content.replace("<head>", f"<head>{data_injection}")
        st.components.v1.html(full_html, height=1200, scroller=True)
