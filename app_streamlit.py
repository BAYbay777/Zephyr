import streamlit as st
import json
import os
import time
from datetime import datetime

# 1. Pengaturan Dasar Layout Utama (Wajib di baris paling awal)
st.set_page_config(page_title="Zephyr Workspace", layout="wide", initial_sidebar_state="collapsed")

# --- CUSTOM CSS SUNTIKAN KHUSUS UNTUK MENIRU 100% DESAIN ASLI KAMU ---
st.markdown("""
    <style>
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { 
        background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%) !important; 
    }
    * {
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
    }
    
    /* Box Kartu Putih Bulat Cantik (Sama dengan screenshot pertama kamu) */
    .zephyr-card {
        background: white !important;
        border-radius: 20px !important;
        padding: 30px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.015) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        margin-bottom: 25px;
    }
    
    .card-title {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        margin-bottom: 5px !important;
    }
    
    .card-subtitle {
        font-size: 13px !important;
        color: #94a3b8 !important;
        margin-bottom: 20px !important;
    }

    /* Modifikasi Tombol & Form agar Berwarna Biru Pastel Angin Lembut */
    .stButton>button {
        background: #38bdf8 !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
    }
    .stButton>button:hover {
        background: #0ea5e9 !important;
    }
    
    /* Tombol Keluar / Reset Berwarna Pastel Halus */
    div.stButton > button[key^="logout_"], div.stButton > button[key^="reset_"] {
        background: #cbd5e1 !important;
        color: #475569 !important;
    }
    
    /* Tampilan Angka Digital Timer Fokus */
    .timer-digital {
        font-size: 75px !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        text-align: center;
        margin: 15px 0;
        font-family: monospace !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Pengelola Database JSON Pintar (Mencegah Kebocoran & Konversi Data Lama Otomatis)
DATA_FILE = "zephyr_master_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                data = json.load(f)
                # Validasi struktur otomatis agar akun lama tidak bikin error lagi!
                for username in data:
                    if "tasks" in data[username]:
                        validated_tasks = []
                        for task in data[username]["tasks"]:
                            if isinstance(task, str):
                                validated_tasks.append({"text": task, "done": False})
                            elif isinstance(task, dict):
                                validated_tasks.append(task)
                        data[username]["tasks"] = validated_tasks
                return data
            except:
                return {}
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

db = load_data()

# Inisialisasi State Kontrol Aplikasi
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'auth_page' not in st.session_state:
    st.session_state['auth_page'] = 'login'
if 'timer_seconds' not in st.session_state:
    st.session_state['timer_seconds'] = 25 * 60
if 'timer_active' not in st.session_state:
    st.session_state['timer_active'] = False
if 'trigger_mood' not in st.session_state:
    st.session_state['trigger_mood'] = False

# ==========================================
# SEKSYEN 1: HALAMAN DEPAN EXCLUSIVE (LOGIN & REGISTER SEPARATE)
# ==========================================
if st.session_state['user'] is None:
    st.write("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
    c1, col_center, c3 = st.columns([1, 1.1, 1])
    
    with col_center:
        if st.session_state['auth_page'] == 'login':
            st.markdown('<div class="zephyr-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center; color: #1e293b; margin-bottom: 5px;'>Masuk ke Zephyr</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #94a3b8; font-size:14px; margin-bottom: 25px;'>Fokus selembut embusan angin.</p>", unsafe_allow_html=True)
            
            log_user = st.text_input("Username", key="txt_luser").strip().lower()
            log_pass = st.text_input("Password", type="password", key="txt_lpass")
            
            st.write("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            if st.button("Masuk Aplikasi", use_container_width=True):
                if log_user in db and db[log_user]["password"] == log_pass:
                    st.session_state['user'] = log_user
                    st.rerun()
                else:
                    st.error("Username atau password salah.")
            
            st.write("<p style='text-align:center; margin-top:20px; font-size:13px; color:#64748b;'>Belum memiliki akun?</p>", unsafe_allow_html=True)
            if st.button("Daftar Akun Baru", use_container_width=True, key="go_reg"):
                st.session_state['auth_page'] = 'register'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.markdown('<div class="zephyr-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center; color: #1e293b; margin-bottom: 5px;'>Buat Akun Baru</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #94a3b8; font-size:14px; margin-bottom: 25px;'>Simpan seluruh list tugas dan riwayat mood-mu</p>", unsafe_allow_html=True)
            
            reg_user = st.text_input("Buat Username Baru", key="txt_ruser").strip().lower()
            reg_pass = st.text_input("Buat Password Baru", type="password", key="txt_rpass")
            
            st.write("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            if st.button("Daftar Akun", use_container_width=True):
                if not reg_user or not reg_pass:
                    st.error("Username dan password wajib diisi!")
                elif reg_user in db:
                    st.error("Username sudah terdaftar di sistem!")
                else:
                    db[reg_user] = {"password": reg_pass, "tasks": [], "mood_history": {}}
                    save_data(db)
                    st.success("Registrasi sukses! Silakan login.")
                    st.session_state['auth_page'] = 'login'
                    time.sleep(1)
                    st.rerun()
            
            if st.button("Kembali ke Login", use_container_width=True, key="back_log"):
                st.session_state['auth_page'] = 'login'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# SEKSYEN 2: LIVE DASHBOARD UTAMA (100% STRUKTUR DESAIN LAMA)
# ==========================================
else:
    user = st.session_state['user']
    user_tasks = db[user].get("tasks", [])
    
    # Header Bar Atas Workspace
    col_u1, col_u2 = st.columns([0.8, 0.2])
    col_u1.markdown(f"<p style='color:#64748b; font-size:14px; margin-top:10px;'>Workspace Pengguna: <b style='color:#0ea5e9;'>{user.upper()}</b></p>", unsafe_allow_html=True)
    if col_u2.button("Keluar Akun", key="logout_key", use_container_width=True):
        st.session_state['user'] = None
        st.session_state['trigger_mood'] = False
        st.rerun()

    # PEMBAGIAN LAYOUT DUA KOLOM BERDAMPINGAN (TIMER VS TO-DO LIST)
    col_kiri, col_kanan = st.columns([1, 1])
    
    # ---------------- KOLOM KIRI: TIMER & MUSIK SPOTIFY ----------------
    with col_kiri:
        st.markdown('<div class="zephyr-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⏱️ Timer & Musik</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-subtitle">Fokus selembut embusan angin.</div>', unsafe_allow_html=True)
        
        # FITUR HUBUNGKAN PLAYLIST SPOTIFY SECARA DINAMIS
        spotify_link = st.text_input(
            "🎵 Hubungkan Playlist/Lagu Spotify:", 
            value="https://open.spotify.com/embed/playlist/37i9dQZF1af07cdffba47afbe29cd421dad9eb8",
            placeholder="Salin tautan share spotify kamu di sini..."
        )
        
        # Konversi link share biasa menjadi link embed widget spotify resmi agar lagu berputar langsung
        if "open.spotify.com" in spotify_link and "embed" not in spotify_link:
            spotify_link = spotify_link.replace("open.spotify.com/", "open.spotify.com/embed/")
            
        st.markdown(f"""
            <iframe src="{spotify_link}" width="100%" height="80" frameborder="0" 
            allowtransparency="true" allow="encrypted-media" style="border-radius: 12px; margin-bottom:15px;"></iframe>
        """, unsafe_allow_html=True)
        
        # MEKANISME KUSTOM TIMER FOKUS MENIT REALTIME
        c_set1, c_set2 = st.columns([0.7, 0.3])
        custom_minutes = c_set1.number_input("Atur waktu manual (dalam menit):", min_value=1, max_value=180, value=25)
        if c_set2.button("Terapkan", use_container_width=True):
            st.session_state['timer_seconds'] = custom_minutes * 60
            st.session_state['timer_active'] = False
            
        # Hitung angka mundur realtime
        t_placeholder = st.empty()
        m, s = divmod(st.session_state['timer_seconds'], 60)
        t_placeholder.markdown(f'<div class="timer-digital">{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
        
        # Tombol Kontrol Timer
        ctrl_1, ctrl_2, ctrl_3 = st.columns(3)
        if ctrl_1.button("Mulai", use_container_width=True):
            st.session_state['timer_active'] = True
            
        if ctrl_2.button("Jeda", use_container_width=True):
            st.session_state['timer_active'] = False
            
        if ctrl_3.button("Reset", key="reset_timer", use_container_width=True):
            st.session_state['timer_seconds'] = custom_minutes * 60
            st.session_state['timer_active'] = False
            st.rerun()
            
        # Proses hitung mundur loop aktif
        if st.session_state['timer_active'] and st.session_state['timer_seconds'] > 0:
            time.sleep(1)
            st.session_state['timer_seconds'] -= 1
            if st.session_state['timer_seconds'] == 0:
                st.session_state['timer_active'] = False
                st.session_state['trigger_mood'] = True # Memicu form pertanyaan mood otomatis!
                st.balloons()
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- KOLOM KANAN: LIST TUGAS DENGAN CHECKLIST ----------------
    with col_kanan:
        st.markdown('<div class="zephyr-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📝 List Tugas</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-subtitle">Catat dan centang tugas yang sudah selesai.</div>', unsafe_allow_html=True)
        
        # Form Input Tambah Tugas Baru
        col_t1, col_t2 = st.columns([0.75, 0.25])
        new_txt = col_t1.text_input("Input tugas", placeholder="Ketik tugas baru di sini...", label_visibility="collapsed")
        if col_t2.button("Tambah", use_container_width=True):
            if new_txt:
                user_tasks.append({"text": new_txt, "done": False})
                db[user]["tasks"] = user_tasks
                save_data(db)
                st.rerun()
        
        st.write("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        
        # MENAMPILKAN CHECKLIST INTERAKTIF (MURNI BERBASIS STREAMLIT AGAR RESPONSIF)
        if user_tasks:
            for idx, item in enumerate(user_tasks):
                col_c1, col_c2 = st.columns([0.85, 0.15])
                
                # Checkbox interaktif bawaan Streamlit
                is_checked = col_c1.checkbox(item["text"], value=item["done"], key=f"chk_{idx}")
                
                # Jika ada perubahan status klik checklist oleh user
                if is_checked != item["done"]:
                    user_tasks[idx]["done"] = is_checked
                    db[user]["tasks"] = user_tasks
                    save_data(db)
                    st.rerun()
                    
                # Tombol hapus tugas berlambang sampah
                if col_c2.button("🗑️", key=f"del_{idx}"):
                    user_tasks.pop(idx)
                    db[user]["tasks"] = user_tasks
                    save_data(db)
                    st.rerun()
        else:
            st.markdown("<p style='color:#94a3b8; font-size:14px; font-style:italic;'>Tidak ada tugas pending hari ini.</p>", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

    # ----------------- KARTU BAWAH: LAPORAN & EVALUASI MOOD -----------------
    st.markdown('<div class="zephyr-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Rangkuman Riwayat Mood Bulan Ini</div>', unsafe_allow_html=True)
    
    # Form Evaluasi Mood Otomatis ketika Timer Selesai Mendekati Angka Nol
    if st.session_state['trigger_mood']:
        st.markdown("<div style='background-color:#f0fdf4; padding:18px; border-radius:12px; margin: 10px 0;'>", unsafe_allow_html=True)
        st.markdown("🎯 <b>Sesi Fokus Selesai!</b> Bagaimana perasaan atau emosimu saat ini?", unsafe_allow_html=True)
        mood_selected = st.selectbox("Pilih Evaluasi Mood:", ["😊 Bahagia & Produktif", "😐 Biasa Saja", "😢 Lelah/Sedih", "😡 Stres Berat"])
        if st.button("Simpan Laporan Mood"):
            today_str = datetime.today().strftime('%Y-%m-%d')
            db[user]["mood_history"][today_str] = mood_selected
            save_data(db)
            st.session_state['trigger_mood'] = False
            st.success("Evaluasi mood harian berhasil dicatat!")
            time.sleep(0.5)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Visualisasi Grafik Riwayat Mood Bulanan
    history = db[user].get("mood_history", {})
    if history:
        g_col1, g_col2 = st.columns([0.6, 0.4])
        with g_col1:
            mood_counts = {"😊 Bahagia & Produktif": 0, "😐 Biasa Saja": 0, "😢 Lelah/Sedih": 0, "😡 Stres Berat": 0}
            for emosi in history.values():
                if emosi in mood_counts: 
                    mood_counts[emosi] += 1
            st.bar_chart(mood_counts)
        with g_col2:
            st.markdown("<p style='font-size:14px; font-weight:600; color:#475569; margin:0;'>Catatan Riwayat Terakhir:</p>", unsafe_allow_html=True)
            for tgl, ems in sorted(history.items(), reverse=True)[:4]:
                st.markdown(f"📅 <small>{tgl}</small> — <b>{ems}</b>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#94a3b8; font-size:14px; margin-top:5px;'>Belum ada data masuk. Jalankan timer fokus di atas sampai selesai untuk memicu laporan evaluasi mood pertamamu.</p>", unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
