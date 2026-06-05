import streamlit as st
import json
import os
import time
from datetime import datetime

# 1. Konfigurasi Dasar Halaman Streamlit
st.set_page_config(page_title="Zephyr Dashboard", layout="centered")

# Custom CSS agar tema menyatu dengan "Angin Lembut" (Hijau muda & Biru muda pastel)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%); }
    h1, h2, h3, p, label, span { color: #0f172a !important; font-family: 'Plus Jakarta Sans', sans-serif; }
    .stButton>button { background-color: #38bdf8; color: white; border-radius: 8px; border: none; width: 100%; }
    .stButton>button:hover { background-color: #0ea5e9; }
    .css-1r6g72d { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# 2. Database JSON Tunggal untuk Menampung Semua Data User
DATA_FILE = "zephyr_master_data.json"

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

# Inisialisasi Session State Streamlit
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'timer_done' not in st.session_state:
    st.session_state['timer_done'] = False

# ==========================================
# SEKSYEN A: AUTENTIKASI (LOGIN & REGISTER)
# ==========================================
if st.session_state['user'] is None:
    st.title("🍃 Zephyr Workspace Login")
    menu = st.radio("Pilih Aksi:", ["Masuk (Login)", "Daftar Akun Baru"], horizontal=True)
    
    username = st.text_input("Username").strip().lower()
    password = st.text_input("Password", type="password")
    
    if menu == "Daftar Akun Baru":
        if st.button("Buat Akun"):
            if username in db:
                st.error("Username sudah terdaftar!")
            elif username and password:
                # Struktur lengkap data per user baru
                db[username] = {
                    "password": password,
                    "tasks": [],
                    "mood_history": {} # Format: {"YYYY-MM-DD": "Mood"}
                }
                save_data(db)
                st.success("Akun sukses dibuat! Silakan pilih menu Masuk.")
    else:
        if st.button("Masuk"):
            if username in db and db[username]["password"] == password:
                st.session_state['user'] = username
                st.rerun()
            else:
                st.error("Username atau password salah.")

# ==========================================
# SEKSYEN B: HALAMAN UTAMA WORKSPACE USER
# ==========================================
else:
    user = st.session_state['user']
    
    # Header & Log Out
    col_head, col_logo = st.columns([0.8, 0.2])
    col_head.header(f"Selamat Datang, {user.capitalize()}!")
    if col_logo.button("Keluar"):
        st.session_state['user'] = None
        st.session_state['timer_done'] = False
        st.rerun()
        
    st.write("---")

    # 1. FITUR TIMER FOKUS & LAGU (Saling Terintegrasi)
    st.subheader("⏱️ Focus Timer & 🎵 Ambient Music")
    
    # Pilihan durasi timer
    duration_option = st.selectbox("Pilih Waktu Fokus:", ["5 Detik (Uji Coba)", "25 Menit (Pomodoro)", "50 Menit"])
    if duration_option == "5 Detik (Uji Coba)":
        seconds = 5
    elif duration_option == "25 Menit (Pomodoro)":
        seconds = 25 * 60
    else:
        seconds = 50 * 60

    # Fitur Lagu Pengiring menggunakan Embed Audio Publik Gratis
    st.write("🎵 **Pilih Musik Pengiring Fokus:**")
    music_choice = st.radio("Pilih Genre:", ["Relaxing Rain", "Lofi Beats (No Copyright)"], horizontal=True)
    
    if music_choice == "Relaxing Rain":
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3") # Contoh audio stream link 1
    else:
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3") # Contoh audio stream link 2

    # Logika Tombol Jalankan Timer
    if st.button("⏱️ Mulai Sesi Fokus"):
        st.session_state['timer_done'] = False
        timer_placeholder = st.empty()
        
        # Proses hitung mundur realtime
        for t in range(seconds, -1, -1):
            mins, secs = divmod(t, 60)
            timer_placeholder.metric(label="Waktu Tersisa", value=f"{mins:02d}:{secs:02d}")
            time.sleep(1)
            
        st.session_state['timer_done'] = True
        st.balloons()
        st.success("Sesi fokus selesai! Kerja bagus!")

    # 2. LAPORAN MOOD SETELAH TIMER SELESAI (Muncul otomatis jika timer_done = True)
    if st.session_state['timer_done']:
        st.info("💡 **Sesi fokus selesai! Bagaimana perasaan/mood kamu sekarang?**")
        mood_after_timer = st.selectbox(
            "Catat evaluasi mood-mu:", 
            ["😊 Bahagia & Produktif", "😐 Biasa Saja", "😢 Lelah/Sedih", "😡 Stres Berat"],
            key="mood_timer_key"
        )
        if st.button("Simpan Evaluasi Mood"):
            today_str = datetime.today().strftime('%Y-%m-%d')
            db[user]["mood_history"][today_str] = mood_after_timer
            save_data(db)
            st.success("Mood berhasil direkam ke riwayat bulanan!")
            st.session_state['timer_done'] = False # Reset state
            st.rerun()

    st.write("---")

    # 3. FITUR TO-DO LIST
    st.subheader("📝 Zephyr To-Do List")
    new_task = st.text_input("Ketik tugas baru kamu di sini...", placeholder="Contoh: Belajar UTBK Matematika")
    if st.button("Tambah ke Daftar"):
        if new_task:
            db[user]["tasks"].append(new_tasks_list := new_task)
            save_data(db)
            st.rerun()
            
    # Tampilkan Tugas yang Ada
    user_tasks = db[user].get("tasks", [])
    if user_tasks:
        for idx, task in enumerate(user_tasks):
            col_t1, col_t2 = st.columns([0.85, 0.15])
            col_t1.write(f"⬜ {task}")
            if col_t2.button("🗑️", key=f"del_{idx}"):
                db[user]["tasks"].pop(idx)
                save_data(db)
                st.rerun()
    else:
        st.caption("Belum ada tugas tersimpan. Kamu bebas hari ini!")

    st.write("---")

    # 4. LAPORAN MOOD BULANAN (GRAFIK)
    st.subheader("📊 Laporan Riwayat Mood Bulanan")
    history = db[user].get("mood_history", {})
    
    if history:
        st.write("Berikut adalah daftar rekam jejak emosimu bulan ini:")
        
        # Hitung akumulasi statistik mood
        mood_counts = {"😊 Bahagia & Produktif": 0, "😐 Biasa Saja": 0, "😢 Lelah/Sedih": 0, "😡 Stres Berat": 0}
        for date, emosi in history.items():
            if emosi in mood_counts:
                mood_counts[emosi] += 1
            st.text(f"📅 Tanggal {date} -> Status: {emosi}")
            
        # Tampilkan Grafik Batang Sederhana Bawaan Streamlit
        st.write("📈 **Grafik Distribusi Mood:**")
        st.bar_chart(mood_counts)
    else:
        st.info("Belum ada riwayat mood yang tercatat bulan ini. Selesaikan sesi timer fokusmu untuk mengisinya!")
