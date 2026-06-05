import streamlit as st
import json
import os

# Setingan dasar halaman agar responsif saat dimasukkan ke HTML
st.set_page_config(page_title="Zephyr Features", layout="centered")

# --- CUSTOM CSS AGAR COCOK DENGAN TEMA ANGIN LEMBUT KAMU ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%); }
    h1, h2, h3, p, label { color: #0f172a !important; font-family: 'Plus Jakarta Sans', sans-serif; }
    .stButton>button { background-color: #38bdf8; color: white; border-radius: 8px; border: none; }
    .stButton>button:hover { background-color: #0ea5e9; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- DATABASE SEDERHANA MENGGUNAKAN JSON ---
DATA_FILE = "streamlit_workspace_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

db = load_data()

# --- SISTEM LOGIN & REGISTER MULTI-USER ---
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None

if st.session_state['current_user'] is None:
    st.title("🍃 Masuk ke Workspace Zephyr")
    menu = st.radio("Pilih Menu:", ["Login", "Daftar Akun"], horizontal=True)
    
    username = st.text_input("Username (Huruf Kecil)").strip().lower()
    password = st.text_input("Password", type="password")
    
    if menu == "Daftar Akun":
        if st.button("Buat Akun Baru"):
            if username in db:
                st.error("Username sudah terdaftar, gunakan nama lain!")
            elif username and password:
                # Membuat struktur data kosong khusus untuk user baru ini
                db[username] = {"password": password, "tasks": [], "mood": "Biasa Saja"}
                save_data(db)
                st.success("Akun berhasil dibuat! Silakan pindah ke menu Login.")
    else:
        if st.button("Masuk"):
            if username in db and db[username]["password"] == password:
                st.session_state['current_user'] = username
                st.rerun()
            else:
                st.error("Username atau password salah.")
else:
    user = st.session_state['current_user']
    
    # Tombol Logout di pojok atas
    col_user, col_logout = st.columns([0.8, 0.2])
    col_user.write(f"Login sebagai: **{user}**")
    if col_logout.button("Log Out"):
        st.session_state['current_user'] = None
        st.rerun()
        
    st.write("---")

    # --- 1. FITUR MOOD TRACKER ---
    st.subheader("📊 Mood Tracker")
    current_mood = db[user].get("mood", "Biasa Saja")
    mood_options = ["😊 Bahagia", "😐 Biasa Saja", "😢 Sedih", "😡 Lelah/Stres"]
    
    try:
        default_idx = mood_options.index(current_mood)
    except:
        default_idx = 1
        
    chosen_mood = st.selectbox("Bagaimana perasaanmu saat ini?", mood_options, index=default_idx)
    
    if chosen_mood != current_mood:
        db[user]["mood"] = chosen_mood
        save_data(db)
        st.toast(f"Mood kamu disimpan: {chosen_mood}")

    st.write("---")

    # --- 2. FITUR TO-DO LIST ---
    st.subheader("📝 Daftar Tugas")
    
    # Form Input Tugas Baru
    new_task = st.text_input("Tulis tugas baru di sini...")
    if st.button("Tambah Tugas"):
        if new_task:
            db[user]["tasks"].append(new_task)
            save_data(db)
            st.rerun()
            
    # Menampilkan daftar tugas milik user terkait
    user_tasks = db[user].get("tasks", [])
    if user_tasks:
        st.write("Daftar tugasmu (Klik tombol 🗑️ jika sudah selesai):")
        for idx, task in enumerate(user_tasks):
            t_col1, t_col2 = st.columns([0.85, 0.15])
            t_col1.write(f"⬜ {task}")
            if t_col2.button("🗑️", key=f"delete_{idx}"):
                db[user]["tasks"].pop(idx)
                save_data(db)
                st.rerun()
    else:
        st.info("Belum ada tugas. Nikmati harimu!")