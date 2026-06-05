import streamlit as st
import json
import os
from datetime import datetime

# ==========================================
# 1. PENGATURAN DASAR LAYOUT UTAMA ZEPHYR
# ==========================================
st.set_page_config(page_title="Zephyr Workspace", layout="wide", initial_sidebar_state="collapsed")

# Menyembunyikan bumbu-bumbu aksesoris default bawaan Streamlit
st.markdown("""
    <style>
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { 
        background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%) !important; 
    }
    * {
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
    }
    
    /* Box Kartu Putih Bulat Cantik Murni Desain Pertama Kamu */
    .zephyr-card {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(16px);
        border-radius: 24px !important;
        padding: 35px !important;
        box-shadow: 0 10px 30px -10px rgba(148, 163, 184, 0.2) !important;
        border: 1px solid #e2e8f0 !important;
        margin-bottom: 25px;
    }
    
    .card-title {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #334155 !important;
        margin-bottom: 6px !important;
    }
    
    .card-subtitle {
        font-size: 13px !important;
        color: #64748b !important;
        margin-bottom: 25px !important;
    }

    /* Style Tombol Pastel Angin Lembut */
    .stButton>button {
        background: #7dd3fc !important;
        color: #0369a1 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: #38bdf8 !important;
        color: white !important;
    }
    
    /* Tombol Keluar / Hapus Trash */
    div.stButton > button[key^="logout_"], div.stButton > button[key^="del_"] {
        background: #f1f5f9 !important;
        color: #ef4444 !important;
    }
    
    /* Angka Digital Timer Fokus */
    .timer-digital {
        font-size: 70px !important;
        font-weight: 700 !important;
        color: #334155 !important;
        text-align: center;
        margin: 20px 0;
        font-family: monospace !important;
        letter-spacing: -1px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. PENGELOLA DATABASE JSON OTOMATIS (ANTI-ERROR)
# ==========================================
DATA_FILE = "zephyr_master_database.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                data = json.load(f)
                # Validasi struktur data lama secara otomatis
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
if 'custom_minutes' not in st.session_state:
    st.session_state['custom_minutes'] = 25

# ==========================================
# 3. INTERFACE HALAMAN DEPAN (LOGIN & REGISTER KARTU TERPISAH)
# ==========================================
if st.session_state['user'] is None:
    st.write("<div style='margin-top: 80px;'></div>", unsafe_allow_html=True)
    c1, col_center, c3 = st.columns([1, 1.2, 1])
    
    with col_center:
        if st.session_state['auth_page'] == 'login':
            st.markdown('<div class="zephyr-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center; color: #334155; margin-bottom: 5px; font-weight:700;'>ZEPHYR</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748b; font-size:13px; margin-bottom: 30px;'>Fokus selembut embusan angin.</p>", unsafe_allow_html=True)
            
            log_user = st.text_input("Username", key="txt_luser", placeholder="Ketik username...").strip().lower()
            log_pass = st.text_input("Password", type="password", key="txt_lpass", placeholder="Ketik password...")
            
            st.write("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            if st.button("Masuk Sekarang", use_container_width=True):
                if log_user in db and db[log_user]["password"] == log_pass:
                    st.session_state['user'] = log_user
                    st.rerun()
                else:
                    st.error("Username atau password salah.")
            
            st.markdown("<p style='text-align:center; margin-top:25px; font-size:12px; color:#64748b;'>Belum memiliki akun?</p>", unsafe_allow_html=True)
            if st.button("Daftar Akun Baru", use_container_width=True, key="go_reg"):
                st.session_state['auth_page'] = 'register'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.markdown('<div class="zephyr-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center; color: #334155; margin-bottom: 5px; font-weight:700;'>Buat Akun Baru</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748b; font-size:13px; margin-bottom: 30px;'>Simpan seluruh list tugas dan riwayat emosimu</p>", unsafe_allow_html=True)
            
            reg_user = st.text_input("Buat Username", key="txt_ruser", placeholder="Contoh: baybay").strip().lower()
            reg_pass = st.text_input("Buat Password", type="password", key="txt_rpass", placeholder="Minimal 4 karakter...")
            
            st.write("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            if st.button("Daftar Akun", use_container_width=True):
                if not reg_user or not reg_pass:
                    st.error("Username dan password wajib diisi!")
                elif reg_user in db:
                    st.error("Username sudah terdaftar!")
                else:
                    db[reg_user] = {"password": reg_pass, "tasks": [], "mood_history": {}}
                    save_data(db)
                    st.success("Registrasi berhasil! Silakan login.")
                    st.session_state['auth_page'] = 'login'
                    st.rerun()
            
            if st.button("Kembali ke Login", use_container_width=True, key="back_log"):
                st.session_state['auth_page'] = 'login'
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. LIVE DASHBOARD WORKSPACE UTAMA
# ==========================================
else:
    user = st.session_state['user']
    user_tasks = db[user].get("tasks", [])
    
    # Navigasi Atas Workspace Murni
    col_u1, col_u2 = st.columns([0.85, 0.15])
    col_u1.markdown(f"<p style='color:#64748b; font-size:15px; margin-top:12px;'>Workspace Pengguna: <span style='color:#38bdf8; font-weight:700;'>{user.upper()}</span></p>", unsafe_allow_html=True)
    if col_u2.button("Keluar Akun", key="logout_key", use_container_width=True):
        st.session_state['user'] = None
        st.rerun()

    # Layout Utama 2 Kolom Berdampingan (Timer vs To-Do List)
    col_kiri, col_kanan = st.columns([1, 1])
    
    # --- KOLOM KIRI: KUSTOM TIMER & MUSIK SPOTIFY ---
    with col_kiri:
        st.markdown('<div class="zephyr-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⏱️ Timer & Musik</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-subtitle">Atur durasi fokus kustom dan dengarkan musik pilihanmu.</div>', unsafe_allow_html=True)
        
        # Pengaturan Waktu Kustom Realtime Menit
        c_set1, c_set2 = st.columns([0.7, 0.3])
        new_min = c_set1.number_input("Atur waktu manual (menit):", min_value=1, max_value=120, value=int(st.session_state['custom_minutes']))
        if c_set2.button("Set Waktu", use_container_width=True):
            st.session_state['custom_minutes'] = new_min
            st.session_state['timer_seconds'] = new_min * 60
            st.session_state['timer_active'] = False
            st.rerun()
            
        # Hitung angka mundur jam digital
        t_placeholder = st.empty()
        m, s = divmod(st.session_state['timer_seconds'], 60)
        t_placeholder.markdown(f'<div class="timer-digital">{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
        
        # Tombol Aksi Kontrol Utama Timer
        ctrl_1, ctrl_2, ctrl_3 = st.columns(3)
        if ctrl_1.button("Mulai", use_container_width=True):
            st.session_state['timer_active'] = True
            
        if ctrl_2.button("Jeda", use_container_width=True):
            st.session_state['timer_active'] = False
            
        if ctrl_3.button("Reset", key="reset_timer", use_container_width=True):
            st.session_state['timer_seconds'] = st.session_state['custom_minutes'] * 60
            st.session_state['timer_active'] = False
            st.rerun()
            
        # Loop hitung mundur detik aktif bawaan Streamlit
        if st.session_state['timer_active'] and st.session_state['timer_seconds'] > 0:
            import time
            time.sleep(1)
            st.session_state['timer_seconds'] -= 1
            if st.session_state['timer_seconds'] == 0:
                st.session_state['timer_active'] = False
                st.balloons()
            st.rerun()
            
        # Embed Widget Musik Spotify Resmi
        st.write("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("""
            <iframe src="https://open.spotify.com/embed/playlist/37i9dQZF1PX8gZp244?utm_source=generator" width="100%" height="80" 
            frameborder="0" allowtransparency="true" allow="encrypted-media" style="border-radius: 12px;"></iframe>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- KOLOM KANAN: LIST TUGAS (BISA DICHECKLIST) ---
    with col_kanan:
        st.markdown('<div class="zephyr-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📝 List Tugas</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-subtitle">Centang tugas yang sukses kamu selesaikan hari ini.</div>', unsafe_allow_html=True)
        
        # Tambah Tugas Baru
        col_t1, col_t2 = st.columns([0.75, 0.25])
        new_txt = col_t1.text_input("Input tugas", placeholder="Ketik tugas barumu di sini...", label_visibility="collapsed")
        if col_t2.button("Tambah", use_container_width=True):
            if new_txt:
                user_tasks.append({"text": new_txt, "done": False})
                db[user]["tasks"] = user_tasks
                save_data(db)
                st.rerun()
        
        st.write("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        
        # Menampilkan Checklist Tugas Secara Reaktif
        if user_tasks:
            for idx, item in enumerate(user_tasks):
                col_c1, col_c2 = st.columns([0.85, 0.15])
                
                # Checkbox interaktif
                is_checked = col_c1.checkbox(item["text"], value=item["done"], key=f"chk_{idx}")
                if is_checked != item["done"]:
                    user_tasks[idx]["done"] = is_checked
                    db[user]["tasks"] = user_tasks
                    save_data(db)
                    st.rerun()
                    
                # Tombol Hapus Tugas Sampah
                if col_c2.button("🗑️", key=f"del_{idx}"):
                    user_tasks.pop(idx)
                    db[user]["tasks"] = user_tasks
                    save_data(db)
                    st.rerun()
        else:
            st.markdown("<p style='color:#64748b; font-size:13px; font-style:italic;'>Belum ada tugas hari ini.</p>", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

    # --- KARTU BAWAH BENAM: PELACAK EMOSI / MOOD TRACKER ---
    st.markdown('<div class="zephyr-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Riwayat Pelacak Mood</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-subtitle">Catat suasana hatimu setelah menyelesaikan sesi belajar harian.</div>', unsafe_allow_html=True)
    
    # Input Catat Jurnal Mood Baru
    m_col1, m_col2 = st.columns([0.7, 0.3])
    mood_input = m_col1.selectbox("Bagaimana perasaanmu saat ini?", ["😊 Bahagia & Produktif", "😐 Biasa Saja", "🙁 Stres / Lelah"])
    if m_col2.button("Simpan Mood", use_container_width=True):
        today_str = datetime.today().strftime('%Y-%m-%d')
        db[user]["mood_history"][today_str] = mood_input
        save_data(db)
        st.success("Mood berhasil dicatat!")
        st.rerun()
        
    # Tampilan Grid Riwayat Mood Bulanan
    history = db[user].get("mood_history", {})
    if history:
        st.write("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        grid_cols = st.columns(min(len(history), 6))
        for idx, (tgl, md) in enumerate(sorted(history.items(), reverse=True)[:6]):
            emoji = "😊" if "Bahagia" in md else "😐" if "Biasa" in md else "🙁"
            with grid_cols[idx % 6]:
                st.markdown(f"""
                    <div style="background: white; padding: 15px; border-radius: 16px; border: 1px solid #e2e8f0; text-align: center;">
                        <div style="font-size: 11px; color: #64748b;">{tgl}</div>
                        <div style="font-size: 24px; margin: 5px 0;">{emoji}</div>
                        <div style="font-weight: 600; font-size: 13px; color:#334155;">{md.split()[1]}</div>
                    </div>
                """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
