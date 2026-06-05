from flask import Flask, render_template, request, jsonify, redirect, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = "ZEPHYR_SUPER_SECRET_KEY"

MOOD_FILE = 'mood_data.json'
TASKS_FILE = 'tasks_data.json'

# --- KONFIGURASI SPOTIFY API ---
SPOTIFY_CLIENT_ID = 'MASUKKAN_CLIENT_ID_SPOTIFY_KAMU'
SPOTIFY_CLIENT_SECRET = 'MASUKKAN_CLIENT_SECRET_SPOTIFY_KAMU'
SPOTIFY_REDIRECT_URI = 'http://localhost:5000/callback'
SCOPE = 'user-modify-playback-state user-read-playback-state'

def load_json_data(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_json_data(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# ==================== ROUTING HALAMAN WEB ====================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/design')
def design():
    return render_template('design.html')

@app.route('/product')
def product():
    tasks = load_json_data(TASKS_FILE)
    return render_template('Product.html', tasks=tasks)

# ==================== INTEGRASI API SPOTIFY ====================

@app.route('/login-spotify')
def login_spotify():
    sp_oauth = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                            client_secret=SPOTIFY_CLIENT_SECRET,
                            redirect_uri=SPOTIFY_REDIRECT_URI,
                            scope=SCOPE)
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                            client_secret=SPOTIFY_CLIENT_SECRET,
                            redirect_uri=SPOTIFY_REDIRECT_URI,
                            scope=SCOPE)
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect('/product')

@app.route('/api/spotify/play', methods=['POST'])
def play_music():
    if "token_info" not in session:
        return jsonify({"status": "error", "message": "Spotify tidak terhubung"}), 401
    try:
        sp = spotipy.Spotify(auth=session["token_info"]['access_token'])
        sp.start_playback()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==================== API MOOD & TASKS ====================

@app.route('/api/mood/save', methods=['POST'])
def save_mood():
    data = request.json
    mood = data.get('mood')
    mood_records = load_json_data(MOOD_FILE)
    today = datetime.now().strftime('%Y-%m-%d')
    mood_records[today] = mood
    save_json_data(MOOD_FILE, mood_records)
    return jsonify({"status": "success"})

@app.route('/api/mood/report', methods=['GET'])
def mood_report():
    mood_records = load_json_data(MOOD_FILE)
    return jsonify(mood_records)

@app.route('/api/tasks/save', methods=['POST'])
def save_tasks():
    tasks_data = request.json
    save_json_data(TASKS_FILE, tasks_data)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)