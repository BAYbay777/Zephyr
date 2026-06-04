import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
from datetime import datetime, timedelta

try:
    import pygame
except:
    pygame = None

MOOD_FILE = "mood_data.json"


# =========================
# MOOD DATA
# =========================

def load_moods():
    if not os.path.exists(MOOD_FILE):
        return []

    with open(MOOD_FILE, "r") as f:
        return json.load(f)


def save_mood(mood):
    moods = load_moods()

    moods.append({
        "mood": mood,
        "date": datetime.now().strftime("%Y-%m-%d")
    })

    with open(MOOD_FILE, "w") as f:
        json.dump(moods, f, indent=4)


def get_month_stats():

    moods = load_moods()

    limit = datetime.now() - timedelta(days=30)

    senang = 0
    biasa = 0
    buruk = 0

    for item in moods:

        date = datetime.strptime(
            item["date"],
            "%Y-%m-%d"
        )

        if date >= limit:

            if item["mood"] == "Senang":
                senang += 1

            elif item["mood"] == "Biasa":
                biasa += 1

            elif item["mood"] == "Buruk":
                buruk += 1

    return senang, biasa, buruk


# =========================
# APP
# =========================

class ZephyrApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Zephyr Study Assistant")
        self.root.geometry("600x500")

        self.running = False

        if pygame:
            pygame.mixer.init()

        title = tk.Label(
            root,
            text="ZEPHYR",
            font=("Arial", 24, "bold")
        )

        title.pack(pady=10)

        subtitle = tk.Label(
            root,
            text="Study Timer & Mood Tracker"
        )

        subtitle.pack()

        tk.Label(
            root,
            text="Durasi Belajar (menit)"
        ).pack(pady=5)

        self.minutes_entry = tk.Entry(root)
        self.minutes_entry.pack()

        tk.Label(
            root,
            text="Pilih Musik"
        ).pack(pady=5)

        self.music_choice = ttk.Combobox(
            root,
            values=[
                "focus1.mp3",
                "focus2.mp3",
                "focus3.mp3"
            ]
        )

        self.music_choice.pack()
        self.music_choice.current(0)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=15)

        self.start_btn = tk.Button(
            btn_frame,
            text="Mulai",
            command=self.start_timer,
            bg="lightgreen"
        )

        self.start_btn.grid(
            row=0,
            column=0,
            padx=10
        )

        self.stop_btn = tk.Button(
            btn_frame,
            text="Stop",
            command=self.stop_timer,
            bg="salmon"
        )

        self.stop_btn.grid(
            row=0,
            column=1,
            padx=10
        )

        self.timer_label = tk.Label(
            root,
            text="00:00",
            font=("Arial", 40)
        )

        self.timer_label.pack(pady=20)

        self.stats_label = tk.Label(
            root,
            text="",
            font=("Arial", 12)
        )

        self.stats_label.pack()

        self.update_stats()

    # =========================

    def play_music(self):

        if not pygame:
            return

        song = self.music_choice.get()

        if os.path.exists(song):

            pygame.mixer.music.load(song)
            pygame.mixer.music.play(-1)

    def stop_music(self):

        if pygame:
            pygame.mixer.music.stop()

    # =========================

    def start_timer(self):

        if self.running:
            return

        try:
            minutes = int(
                self.minutes_entry.get()
            )

        except:
            messagebox.showerror(
                "Error",
                "Masukkan angka!"
            )
            return

        self.running = True

        self.play_music()

        threading.Thread(
            target=self.countdown,
            args=(minutes * 60,),
            daemon=True
        ).start()

    # =========================

    def stop_timer(self):

        self.running = False
        self.stop_music()

    # =========================

    def countdown(self, seconds):

        while seconds >= 0 and self.running:

            mins = seconds // 60
            secs = seconds % 60

            self.timer_label.config(
                text=f"{mins:02}:{secs:02}"
            )

            time.sleep(1)

            seconds -= 1

        if self.running:

            self.stop_music()

            self.root.after(
                0,
                self.ask_mood
            )

        self.running = False

    # =========================

    def ask_mood(self):

        mood_window = tk.Toplevel(self.root)

        mood_window.title("Mood Hari Ini")

        tk.Label(
            mood_window,
            text="Bagaimana perasaanmu setelah belajar?"
        ).pack(pady=10)

        def choose(mood):

            save_mood(mood)

            self.update_stats()

            mood_window.destroy()

            messagebox.showinfo(
                "Tersimpan",
                "Mood berhasil disimpan!"
            )

        tk.Button(
            mood_window,
            text="😊 Senang",
            command=lambda: choose("Senang")
        ).pack(fill="x")

        tk.Button(
            mood_window,
            text="😐 Biasa",
            command=lambda: choose("Biasa")
        ).pack(fill="x")

        tk.Button(
            mood_window,
            text="☹️ Buruk",
            command=lambda: choose("Buruk")
        ).pack(fill="x")

    # =========================

    def update_stats(self):

        senang, biasa, buruk = get_month_stats()

        self.stats_label.config(
            text=
            f"Statistik 30 Hari Terakhir\n\n"
            f"😊 Senang : {senang}\n"
            f"😐 Biasa : {biasa}\n"
            f"☹️ Buruk : {buruk}"
        )


# =========================
# MAIN
# =========================

root = tk.Tk()

app = ZephyrApp(root)

root.mainloop()