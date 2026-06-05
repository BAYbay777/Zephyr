import streamlit as st
import json
import os
import time
from datetime import datetime

# 1. Konfigurasi Dasar Halaman (Wajib di bagian paling atas)
st.set_page_config(page_title="Zephyr Workspace", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# CUSTOM CSS: MEROMBAK TOTAL STREAMLIT MENJADI DESAIN LAMA
# ==========================================
st.markdown("""
    <style>
    /* Menyembunyikan elemen bawaan Streamlit agar bersih */
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { 
        background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%) !important; 
        padding-top: 0px;
    }
    
    /* Font global menggunakan Plus Jakarta Sans/Inter */
    * {
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
    }

    /* Mengubah gaya container box (Kartu Putih Estetik) */
    .zephyr-card {
        background-color: white !important;
        border-radius: 20px !important;
        padding: 35px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        margin-bottom: 25px;
    }

    /* Mengubah gaya input teks */
    .stTextInput>div>div>input {
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 12px !important;
        color: #334155 !important;
    }
    
    /* Mengubah gaya tombol utama (Biru Muda Lembut) */
    .stButton>button {
        background: #38bdf8 !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2) !important;
    }
    .stButton>button:hover {
        background: #0ea5e9 !important;
        transform: translateY(-1px) !important;
    }

    /* Tombol Merah/Reset */
    div.stButton > button[key^="reset_"] {
        background: #fca5a5 !important;
        box-shadow: 0 4px 12px rgba(252, 165, 165, 0.2) !important;
    }

    /* Judul dan Teks */
    h2, h3 {
        color: #1e293b !important;
        font-weight: 700 !important;
    }
    
    /* Gaya Angka Timer Raksasa */
    .timer-display {
        font-size: 80px !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        text-align: center;
        margin: 20px 0;
        font-family: monospace !important;
        letter-spacing: -2px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Manajemen Database JSON
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

# Sesi state aplikasi
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'
if 'timer_done' not in st.session_state:
    st.session_state['timer_done'] = False

# ==========================================
# HALAMAN 1: PROSES AUTENTIKASI (LOGIN / REGISTER SEPARATE)
# ==========================================
if st.session_state['user'] is None:
    col_space1, col_box, col_space2 = st.columns([1, 1.2, 1])
    
    with col_box:
        st.write("<div style='margin-top: 80px;'></div>", unsafe_allow_html=True)
        
        if st.session_state['page'] == 'login':
            st.markdown('<div class="zephyr-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center; margin-bottom: 25px;'>Masuk ke Zephyr</h2>", unsafe_allow_html=True)
            
            login_user = st.text_input("Username", key="lin_user").strip().lower()
            login_pass = st.text_input("Password", type="password", key="lin_pass")
            
            st.write("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            if st.button("Masuk", use_container_width=True):
                if login_user in db and db[login_user]["password"] == login_pass:
                    st.session_state['user'] = login_user
                    st.rerun()
                else:
                    st.error("Username atau password salah.")
            
            st.markdown("<p style='text-align: center; margin-top: 20px; font-size: 14px;'>Belum punya akun? </p>", unsafe_allow_html=True)
            if st.button("Daftar Akun Baru di Sini", use_container_width=True):
                st.session_state['page'] = 'register'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        elif st.session_state['page'] == 'register':
            st.markdown('<div class="zephyr-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center; margin-bottom: 25px;'>Buat Akun Zephyr</h2>", unsafe_allow_html=True)
            
            reg_user = st.text_input("Buat Username", key="reg_user").strip().lower()
            reg_pass = st.text_input("Buat Password", type="password", key="reg_pass")
            
            st.write("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            if st.button("Daftar Sekarang", use_container_width=True):
                if not reg_user or not reg_pass:
                    st.error("Data tidak boleh kosong!")
                elif reg_user in db:
                    st.error("Username sudah digunakan!")
                else:
                    db[reg_user] = {"password": reg_pass, "tasks": [], "mood_history": {}}
                    save_data(db)
                    st.success("Akun berhasil didaftarkan!")
                    st.session_state['page'] = 'login'
                    time.sleep(1)
                    st.rerun()
                    
            if st.button("Kembali ke Login", use_container_width=True):
                st.session_state['page'] = 'login'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# HALAMAN 2: DASHBOARD UTAMA (PERSIS DESAIN LAMA)
# ==========================================
else:
    user = st.session_state['user']
    
    # Bar Atas Informasi Akun
    col_title, col_logout = st.columns([0.85, 0.15])
    col_title.markdown(f"<p style='font-size: 14px; color: #64748b;'>Workspace Pengguna: <b>{user.upper()}</b></p>", unsafe_allow_html=True)
    if col_logout.button("Keluar Akun", key="btn_logout"):
        st.session_state['user'] = None
        st.session_state['timer_done'] = False
        st.rerun()

    # Layout Dua Kolom Sejajar (Persis Screenshot 211732)
    col_kiri, col_kanan = st.columns([1, 1])
    
    # --- KOLOM KIRI: TIMER & MUSIK ---
    with col_kiri:
        st.markdown('<div class="zephyr-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0;'>⏱️ Timer & Musik</h3>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 13px; color: #94a3b8; margin-top: -10px;'>Fokus selembut embusan angin.</p>", unsafe_allow_html=True)
        
        # Pilihan Waktu Fokus
        duration_option = st.selectbox("Atur waktu fokus:", ["25:00 (Pomodoro)", "50:00", "00:05 (Uji Coba Quick)"])
        if "25:00" in duration_option: seconds = 25 * 60
        elif "50:00" in duration_option: seconds = 50 * 60
        else: seconds = 5
        
        # Pemutar Musik
        st.markdown("<p style='font-size: 14px; font-weight:600; margin-bottom:5px;'>🎵 Musik Pengiring:</p>", unsafe_allow_html=True)
        music_choice = st.radio("Genre Audio Loop:", ["Relaxing Ambient Rain", "Soft Lofi Focus Beats"], horizontal=True, label_visibility="collapsed")
        
        if music_choice == "Relaxing Ambient Rain":
            st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
        else:
            st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3")
            
        # Tampilan Angka Countdown Digital Murni
        timer_placeholder = st.empty()
        mins, secs = divmod(seconds, 60)
        timer_placeholder.markdown(f'<div class="timer-display">{mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("Mulai Sesi", use_container_width=True):
            st.session_state['timer_done'] = False
            for t in range(seconds, -1, -1):
                m, s = divmod(t, 60)
                timer_placeholder.markdown(f'<div class="timer-display">{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
                time.sleep(1)
            st.session_state['timer_done'] = True
            st.balloons()
            st.rerun()
            
        if col_btn2.button("Reset", key="reset_timer", use_container_width=True):
            st.session_state['timer_done'] = False
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

    # --- KOLOM KANAN: LIST TUGAS (TO-DO LIST) ---
    with col_kanan:
        st.markdown('<div class="zephyr-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0;'>📝 List Tugas</h3>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 13px; color: #94a3b8; margin-top: -10px;'>Catat dan bersihkan tugas yang sudah selesai.</p>", unsafe_allow_html=True)
        
        # Kolom Tambah Tugas
        col_inp, col_add = st.columns([0.75, 0.25])
        new_task = col_inp.text_input("Input tugas", placeholder="Ketik tugas baru di sini...", label_visibility="collapsed")
        if col_add.button("Tambah", use_container_width=True):
            if new_task:
                db[user]["tasks"].append(new_task)
                save_data(db)
                st.rerun()
                
        # Menampilkan Barisan List Tugas
        st.write("")
        user_tasks = db[user].get("tasks", [])
        if user_tasks:
            for idx, task in enumerate(user_tasks):
                col_t1, col_t2 = st.columns([0.85, 0.15])
                col_t1.markdown(f"<div style='padding: 5px 0; color:#475569;'>⬜ &nbsp; {task}</div>", unsafe_allow_html=True)
                if col_t2.button("🗑️", key=f"del_{idx}"):
                    db[user]["tasks"].pop(idx)
                    save_data(db)
                    st.rerun()
        else:
            st.markdown("<p style='color:#94a3b8; font-size:14px; font-style:italic;'>Tidak ada tugas pending.</p>", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

    # --- BAGIAN BAWAH: EVALUASI & RIWAYAT MOOD BULANAN ---
    st.markdown('<div class="zephyr-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>📊 Rangkuman Riwayat Mood Bulan Ini</h3>", unsafe_allow_html=True)
    
    # Trigger evaluasi jika sesi fokus baru saja diselesaikan
    if st.session_state['timer_done']:
        st.markdown("<div style='background-color:#f0fdf4; padding:15px; border-radius:10px; margin-bottom:15px;'>", unsafe_allow_html=True)
        st.markdown("🎯 <b>Sesi Fokus Selesai!</b> Bagaimana kondisi emosimu sekarang?", unsafe_allow_html=True)
        ev_mood = st.selectbox("Pilih Status Emosi:", ["😊 Bahagia & Produktif", "😐 Biasa Saja", "😢 Lelah/Sedih", "😡 Stres/Lelah"], key="sel_ev")
        if st.button("Simpan Data Mood"):
            today_str = datetime.today().strftime('%Y-%m-%d')
            db[user]["mood_history"][today_str] = ev_mood
            save_data(db)
            st.session_state['timer_done'] = False
            st.success("Mood terekam!")
            time.sleep(0.5)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Tampilan Laporan Bulanan (Grafik & Log)
    history = db[user].get("mood_history", {})
    if history:
        col_graph, col_logs = st.columns([0.6, 0.4])
        
        with col_graph:
            mood_counts = {"😊 Bahagia & Produktif": 0, "😐 Biasa Saja": 0, "😢 Lelah/Sedih": 0, "😡 Stres/Lelah": 0}
            for emosi in history.values():
                if emosi in mood_counts: mood_counts[emosi] += 1
            st.bar_chart(mood_counts)
            
        with col_logs:
            st.markdown("<p style='font-size:14px; font-weight:600;'>Jurnal harian:</p>", unsafe_allow_html=True)
            for tanggal, emosi in sorted(history.items(), reverse=True)[:5]:
                st.markdown(f"🗓️ <small>{tanggal}</small> : <b>{emosi}</b>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#94a3b8; font-size:14px;'>Belum ada data masuk. Selesaikan pengukur waktu fokus di atas untuk membuat laporan mood pertamamu.</p>", unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
