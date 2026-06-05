import streamlit as st
import json
import os
import time

# 1. Setting dasar halaman Streamlit
st.set_page_config(page_title="Zephyr", layout="wide", initial_sidebar_state="collapsed")

# --- CSS UNTUK MENYEMBUNYIKAN ELEMEN UTAMA STREAMLIT ---
st.markdown("""
    <style>
    #MainMenu, footer, header { visibility: hidden; }
    .stApp { background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%) !important; }
    iframe { background: transparent !important; }
    </style>
""", unsafe_allow_html=True)

# 2. Database JSON Tunggal
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

# Session State
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'auth_page' not in st.session_state:
    st.session_state['auth_page'] = 'login'

# ==========================================
# HALAMAN DEPAN: REGISTRASI & LOGIN TERPISAH
# ==========================================
if st.session_state['user'] is None:
    # Menggunakan HTML Murni untuk Tampilan Card Login/Register agar Sangat Estetik
    if st.session_state['auth_page'] == 'login':
        st.markdown("""
            <div style="max-width: 400px; margin: 80px auto 20px auto; background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); text-align: center; font-family: 'Plus Jakarta Sans', sans-serif;">
                <h2 style="color: #1e293b; margin-bottom: 10px; font-weight: 700;">Masuk ke Zephyr</h2>
                <p style="color: #94a3b8; font-size: 14px; margin-bottom: 25px;">Fokus selembut embusan angin.</p>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 1.2, 1])
        with c2:
            username = st.text_input("Username", key="l_user", placeholder="Masukkan username...").strip().lower()
            password = st.text_input("Password", type="password", key="l_pass", placeholder="Masukkan password...")
            st.write("")
            if st.button("Masuk", use_container_width=True):
                if username in db and db[username]["password"] == password:
                    st.session_state['user'] = username
                    st.rerun()
                else:
                    st.error("Username atau password salah!")
            
            st.write("---")
            if st.button("Belum punya akun? Daftar di sini", use_container_width=True):
                st.session_state['auth_page'] = 'register'
                st.rerun()

    elif st.session_state['auth_page'] == 'register':
        st.markdown("""
            <div style="max-width: 400px; margin: 80px auto 20px auto; background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); text-align: center; font-family: 'Plus Jakarta Sans', sans-serif;">
                <h2 style="color: #1e293b; margin-bottom: 10px; font-weight: 700;">Buat Akun Baru</h2>
                <p style="color: #94a3b8; font-size: 14px; margin-bottom: 25px;">Mulai perjalanan fokusmu hari ini.</p>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 1.2, 1])
        with c2:
            new_user = st.text_input("Buat Username", key="r_user", placeholder="Contoh: baybay").strip().lower()
            new_pass = st.text_input("Buat Password", type="password", key="r_pass", placeholder="Minimal 4 karakter...")
            st.write("")
            if st.button("Daftar Sekarang", use_container_width=True):
                if not new_user or not new_pass:
                    st.error("Form tidak boleh kosong!")
                elif new_user in db:
                    st.error("Username sudah terpakai!")
                else:
                    db[new_user] = {"password": new_pass, "tasks": [], "mood_history": {}}
                    save_data(db)
                    st.success("Akun berhasil dibuat! Mengalihkan...")
                    time.sleep(1)
                    st.session_state['auth_page'] = 'login'
                    st.rerun()
                    
            if st.button("Kembali ke Login", use_container_width=True):
                st.session_state['auth_page'] = 'login'
                st.rerun()

# ==========================================
# DASHBOARD UTAMA: 100% SAMA DENGAN DESAIN LAMA
# ==========================================
else:
    user = st.session_state['user']
    
    # Header Pengguna & Tombol Keluar Akun
    h_col1, h_col2 = st.columns([0.85, 0.15])
    h_col1.markdown(f"<p style='font-family: \"Plus Jakarta Sans\"; color: #64748b; margin-top:15px;'>Workspace Pengguna: <strong style='color:#0ea5e9;'>{user.upper()}</strong></p>", unsafe_allow_html=True)
    if h_col2.button("Keluar Akun", use_container_width=True):
        st.session_state['user'] = None
        st.rerun()

    # Ambil data task user saat ini
    user_tasks = db[user].get("tasks", [])

    # INPUT BARU LEWAT UTAS STREAMLIT AGAR REAKTIF SINKRON KE DATABASE
    # (Kita taruh di atas layout agar penambahan tugas super responsif)
    with st.expander("➕ Tambah Tugas Baru"):
        t_col1, t_col2 = st.columns([0.8, 0.2])
        task_input = t_col1.text_input("Nama Tugas", placeholder="Ketik tugas di sini...", label_visibility="collapsed")
        if t_col2.button("Simpan", use_container_width=True):
            if task_input:
                user_tasks.append({"text": task_input, "done": False})
                db[user]["tasks"] = user_tasks
                save_data(db)
                st.rerun()

    # Menerima data kiriman balik dari JavaScript checklist jika ada perubahan status tugas
    # (Menggunakan query parameter URL rahasia bawaan iframe streamlit)
    query_params = st.query_params
    if "toggle_idx" in query_params:
        idx_to_toggle = int(query_params["toggle_idx"])
        if idx_to_toggle < len(user_tasks):
            user_tasks[idx_to_toggle]["done"] = not user_tasks[idx_to_toggle]["done"]
            db[user]["tasks"] = user_tasks
            save_data(db)
            st.query_params.clear()
            st.rerun()
            
    if "delete_idx" in query_params:
        idx_to_del = int(query_params["delete_idx"])
        if idx_to_del < len(user_tasks):
            user_tasks.pop(idx_to_del)
            db[user]["tasks"] = user_tasks
            save_data(db)
            st.query_params.clear()
            st.rerun()

    # BENTUK STRUKTUR ELEMEN HTML & JAVASCRIPT ASLI YANG SUPER INDAH
    # Kita buat list generator dalam format baris teks HTML
    tasks_html_elements = ""
    for idx, t in enumerate(user_tasks):
        checked_attr = "checked" if t["done"] else ""
        text_style = "text-decoration: line-through; color: #94a3b8;" if t["done"] else "color: #334155;"
        tasks_html_elements += f"""
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 12px; background: #f8fafc; border-radius: 10px; margin-bottom: 10px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <input type="checkbox" {checked_attr} style="width: 18px; height: 18px; accent-color: #38bdf8; cursor: pointer;" 
                       onclick="window.parent.location.href = window.parent.location.pathname + '?toggle_idx={idx}';">
                <span style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 15px; {text_style}">{t['text']}</span>
            </div>
            <button style="background: none; border: none; color: #ef4444; cursor: pointer; font-size: 16px;" 
                    onclick="window.parent.location.href = window.parent.location.pathname + '?delete_idx={idx}';">🗑️</button>
        </div>
        """

    if not tasks_html_elements:
        tasks_html_elements = "<p style='color: #94a3b8; font-style: italic; font-size: 14px;'>Belum ada tugas. Ambil nafas dalam-dalam!</p>"

    # --- SUNTIKAN BLOK KODE HTML UTAMA (PERSIS DESIGN SCREENSHOT 211732) ---
    main_dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Plus Jakarta Sans', sans-serif;
                margin: 0;
                padding: 0;
                background: transparent;
            }}
            .workspace-layout {{
                display: flex;
                gap: 25px;
                margin-bottom: 25px;
            }}
            .card {{
                background: white;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.01);
                flex: 1;
                border: 1px solid rgba(255,255,255,0.7);
            }}
            .card-title {{
                font-size: 20px;
                font-weight: 700;
                color: #1e293b;
                margin-top: 0;
                margin-bottom: 5px;
            }}
            .card-subtitle {{
                font-size: 13px;
                color: #94a3b8;
                margin-bottom: 20px;
            }}
            /* Timer Styling */
            .timer-box {{
                text-align: center;
                margin: 20px 0;
            }}
            .timer-text {{
                font-size: 72px;
                font-weight: 700;
                color: #1e293b;
                font-family: monospace;
            }}
            .btn-group {{
                display: flex;
                gap: 10px;
                justify-content: center;
                margin-top: 15px;
            }}
            .btn {{
                border: none;
                padding: 10px 25px;
                border-radius: 10px;
                font-weight: 600;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.2s;
            }}
            .btn-start {{ background: #38bdf8; color: white; }}
            .btn-start:hover {{ background: #0ea5e9; }}
            .btn-pause {{ background: #cbd5e1; color: #475569; }}
            .btn-reset {{ background: #fca5a5; color: #b91c1c; }}
            
            /* Spotify Styling */
            .spotify-input {{
                width: 100%;
                padding: 10px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin-bottom: 10px;
                box-sizing: border-box;
            }}
            .full-card {{
                background: white;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.01);
                border: 1px solid rgba(255,255,255,0.7);
            }}
        </style>
    </head>
    <body>

        <div class="workspace-layout">
            <div class="card">
                <div class="card-title">⏱️ Timer & Musik</div>
                <div class="card-subtitle">Fokus selembut embusan angin.</div>
                
                <input type="text" id="spotifyUrl" class="spotify-input" placeholder="Masukkan Link Share Playlist/Lagu Spotify-mu di sini..." 
                       value="https://open.spotify.com/embed/playlist/37i9dQZF1GXr7wY6v9" onchange="updateSpotify()">
                
                <iframe id="spotifyPlayer" src="https://open.spotify.com/embed/playlist/37i9dQZF1GXr7wY6v9" 
                        width="100%" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media" style="border-radius:10px;"></div>
                
                <div class="timer-box">
                    <div style="margin-bottom:10px;">
                        <input type="number" id="customMinutes" style="width: 60px; padding:5px; border-radius:5px; border:1px solid #ccc; text-align:center;" value="25"> Menit
                    </div>
                    <div class="timer-text" id="display">25:00</div>
                    <div class="btn-group">
                        <button class="btn btn-start" onclick="startTimer()">Mulai</button>
                        <button class="btn btn-pause" onclick="pauseTimer()">Jeda</button>
                        <button class="btn btn-reset" onclick="resetTimer()">Reset</button>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-title">📝 List Tugas</div>
                <div class="card-subtitle">Catat dan centang tugas yang sudah selesai.</div>
                <div style="max-height: 250px; overflow-y: auto; padding-right: 5px;">
                    {tasks_html_elements}
                </div>
            </div>
        </div>

        <div class="full-card">
            <div class="card-title">📊 Rangkuman Riwayat Mood Bulan Ini</div>
            <p style="color: #64748b; font-size:14px; margin-top:5px;">Selesaikan pengukur waktu fokus di atas untuk memicu laporan evaluasi mood harian otomatis.</p>
        </div>

        <script>
            let countdown;
            let timerSeconds = 25 * 60;
            let isRunning = false;
            
            function updateSpotify() {{
                let url = document.getElementById('spotifyUrl').value;
                if(url.includes("open.spotify.com")) {{
                    let embedUrl = url.replace("open.spotify.com/", "open.spotify.com/embed/");
                    document.getElementById('spotifyPlayer').src = embedUrl;
                }}
            }}

            function displayTime(seconds) {{
                const min = Math.floor(seconds / 60);
                const sec = seconds % 60;
                document.getElementById('display').innerText = 
                    `${{min < 10 ? '0' : ''}}${{min}}:${{sec < 10 ? '0' : ''}}${{sec}}`;
            }}

            function startTimer() {{
                if (isRunning) return;
                
                // Ambil nilai menit kustom dari kotak input saat tombol start ditekan
                if(timerSeconds === 25 * 60 || timerSeconds === 0) {{
                    let customMin = parseInt(document.getElementById('customMinutes').value) || 25;
                    timerSeconds = customMin * 60;
                }}
                
                isRunning = true;
                countdown = setInterval(() => {{
                    timerSeconds--;
                    displayTime(timerSeconds);
                    
                    if (timerSeconds <= 0) {{
                        clearInterval(countdown);
                        isRunning = false;
                        alert("Sesi fokus selesai! Silakan isi evaluasi mood kamu.");
                    }}
                }}, 1000);
            }}

            function pauseTimer() {{
                clearInterval(countdown);
                isRunning = false;
            }}

            function resetTimer() {{
                clearInterval(countdown);
                isRunning = false;
                let customMin = parseInt(document.getElementById('customMinutes').value) || 25;
                timerSeconds = customMin * 60;
                displayTime(timerSeconds);
            }}
        </script>
    </body>
    </html>
    """
    
    # Render semua HTML & CSS super cantik di atas ke dalam interface web utama kamu
    st.components.v1.html(main_dashboard_html, height=650, scroller=False)
