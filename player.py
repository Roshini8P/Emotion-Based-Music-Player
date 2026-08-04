"""
A Tkinter GUI application that plays music and shows inspirational quotes
based on your selected mood. Uses pandas for data management, numpy for
random selection, and pygame for audio playback.

"""
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import numpy as np
import pygame
import os
import sys

CSV_FILE = "songs_data.csv"
MOOD_ICONS = {
    "happy":     "😊",
    "sad":       "😢",
    "calm":      "😌",
    "energetic": "⚡",
    "love":  "💖",
}
MOOD_COLORS = {
    "happy":     "#F4D03F",   # sunny yellow
    "sad":       "#85C1E9",   # soft blue
    "calm":      "#A9DFBF",   # mint green
    "energetic": "#F1948A",   # warm coral
    "love":  "#F1A7C7",   # blush pink
}
BG_COLOR      = "#1A1A2E"   # deep navy background
PANEL_COLOR   = "#16213E"   # slightly lighter panel
CARD_COLOR    = "#0F3460"   # card / display area
TEXT_COLOR    = "#E0E0E0"   # primary text
MUTED_COLOR   = "#8899AA"   # secondary / label text
ACCENT_COLOR  = "#E94560"   # red accent for control buttons

def load_data(csv_path: str) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Data file '{csv_path}' not found.\n"
            "Make sure songs_data.csv is in the same folder as player.py."
        )
    df = pd.read_csv(csv_path)

    # Validate required columns exist
    required_columns = {"mood", "song_path", "quote"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {missing}")

    # Strip whitespace from string columns
    df["mood"]      = df["mood"].str.strip().str.lower()
    df["song_path"] = df["song_path"].str.strip()
    df["quote"]     = df["quote"].str.strip()

    # Pandas: add a derived column with the display name (filename without extension)
    df["song_name"] = df["song_path"].apply(
        lambda p: os.path.splitext(os.path.basename(p))[0].replace("_", " ").title()
    )

    # Numpy: compute mood distribution as percentages (shown in status bar)
    mood_counts = df["mood"].value_counts()
    df["mood_share"] = df["mood"].map(
        lambda m: round((mood_counts.get(m, 0) / len(df)) * 100, 1)
    )

    return df


def get_random_entry(df: pd.DataFrame, mood: str) -> pd.Series:
    """
    Filter the DataFrame by mood, then use numpy to pick a random row.
    Returns a pandas Series (one row).
    """
    # pandas: filter rows matching the chosen mood
    mood_df = df[df["mood"] == mood].reset_index(drop=True)

    if mood_df.empty:
        raise ValueError(f"No entries found for mood: '{mood}'")

    # numpy: pick a random integer index
    random_index = np.random.randint(0, len(mood_df))
    return mood_df.iloc[random_index]


def get_mood_stats(df: pd.DataFrame) -> str:
    """
    Use pandas aggregation to build a one-line stats summary.
    E.g.: '15 songs across 5 moods'
    """
    total_songs  = len(df)
    unique_moods = df["mood"].nunique()
    return f"{total_songs} songs across {unique_moods} moods"


# ─────────────────────────────────────────────
#  AUDIO LAYER  (pygame)
# ─────────────────────────────────────────────

def init_audio():
    """Initialise the pygame mixer. Called once at startup."""
    pygame.mixer.init()


def play_song(song_path: str):
    """
    Stop any currently playing music, then load and play the new file.
    song_path is relative to the script's directory.
    """
    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), song_path)

    if not os.path.exists(full_path):
        messagebox.showwarning(
            "File Not Found",
            f"Audio file not found:\n{full_path}\n\n"
            "Add real .wav / .mp3 files in the songs/ subfolders."
        )
        return

    pygame.mixer.music.stop()
    pygame.mixer.music.load(full_path)
    pygame.mixer.music.play()


def stop_music():
    """Stop playback immediately."""
    pygame.mixer.music.stop()


# ─────────────────────────────────────────────
#  GUI  (Tkinter)
# ─────────────────────────────────────────────

class EmotionMusicPlayer:
    """
    Main application class.
    Builds and manages the Tkinter window, widgets, and event callbacks.
    """

    def __init__(self, root: tk.Tk, df: pd.DataFrame):
        self.root = root
        self.df   = df

        # Track the currently active mood so Shuffle knows what to re-roll
        self.current_mood: str | None = None

        self._configure_window()
        self._build_ui()

    # ── Window setup ──────────────────────────

    def _configure_window(self):
        """Set window title, size, background, and make it non-resizable."""
        self.root.title("🎵 Emotion Based Music Player")
        self.root.geometry("620x700")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        # Center on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - 620) // 2
        y = (self.root.winfo_screenheight() - 700) // 2
        self.root.geometry(f"+{x}+{y}")

    # ── UI construction ───────────────────────

    def _build_ui(self):
        """Assemble every widget section top-to-bottom."""
        self._build_header()
        self._build_mood_buttons()
        self._build_display_card()
        self._build_control_buttons()
        self._build_status_bar()

    def _build_header(self):
        """App title and subtitle."""
        header = tk.Frame(self.root, bg=BG_COLOR, pady=20)
        header.pack(fill="x")

        tk.Label(
            header,
            text="🎵 Emotion Music Player",
            font=("Georgia", 22, "bold"),
            fg=TEXT_COLOR,
            bg=BG_COLOR,
        ).pack()

        tk.Label(
            header,
            text="Choose a mood and let the music flow",
            font=("Helvetica", 11),
            fg=MUTED_COLOR,
            bg=BG_COLOR,
        ).pack()

    def _build_mood_buttons(self):
        """One button per mood, arranged in a centred row."""
        section = tk.Frame(self.root, bg=BG_COLOR, pady=8)
        section.pack()

        tk.Label(
            section,
            text="— SELECT YOUR MOOD —",
            font=("Helvetica", 9, "bold"),
            fg=MUTED_COLOR,
            bg=BG_COLOR,
        ).pack(pady=(0, 10))

        btn_row = tk.Frame(section, bg=BG_COLOR)
        btn_row.pack()

        for mood in MOOD_ICONS:
            color = MOOD_COLORS[mood]
            btn = tk.Button(
                btn_row,
                text=f"{MOOD_ICONS[mood]}\n{mood.capitalize()}",
                font=("Helvetica", 10, "bold"),
                fg="#1A1A2E",
                bg=color,
                activebackground=color,
                activeforeground="#1A1A2E",
                relief="flat",
                bd=0,
                padx=14,
                pady=10,
                cursor="hand2",
                # lambda default-arg trick to capture the loop variable correctly
                command=lambda m=mood: self._on_mood_selected(m),
            )
            btn.pack(side="left", padx=6)

    def _build_display_card(self):
        """Card showing current mood, song name, and quote."""
        outer = tk.Frame(self.root, bg=BG_COLOR, pady=20)
        outer.pack(fill="x", padx=30)

        card = tk.Frame(outer, bg=CARD_COLOR, padx=24, pady=24)
        card.pack(fill="x")

        # ── Mood label ──────────────────────────
        mood_row = tk.Frame(card, bg=CARD_COLOR)
        mood_row.pack(fill="x", pady=(0, 12))

        tk.Label(
            mood_row,
            text="CURRENT MOOD",
            font=("Helvetica", 8, "bold"),
            fg=MUTED_COLOR,
            bg=CARD_COLOR,
        ).pack(anchor="w")

        self.mood_label = tk.Label(
            mood_row,
            text="— None selected —",
            font=("Georgia", 18, "bold"),
            fg=TEXT_COLOR,
            bg=CARD_COLOR,
        )
        self.mood_label.pack(anchor="w")

        # ── Separator ──────────────────────────
        tk.Frame(card, bg=ACCENT_COLOR, height=2).pack(fill="x", pady=8)

        # ── Song name ──────────────────────────
        song_row = tk.Frame(card, bg=CARD_COLOR)
        song_row.pack(fill="x", pady=(8, 12))

        tk.Label(
            song_row,
            text="NOW PLAYING",
            font=("Helvetica", 8, "bold"),
            fg=MUTED_COLOR,
            bg=CARD_COLOR,
        ).pack(anchor="w")

        self.song_label = tk.Label(
            song_row,
            text="♪  —",
            font=("Helvetica", 13),
            fg=TEXT_COLOR,
            bg=CARD_COLOR,
        )
        self.song_label.pack(anchor="w")

        # ── Quote ──────────────────────────────
        tk.Frame(card, bg=PANEL_COLOR, height=2).pack(fill="x", pady=8)

        tk.Label(
            card,
            text="QUOTE OF THE MOMENT",
            font=("Helvetica", 8, "bold"),
            fg=MUTED_COLOR,
            bg=CARD_COLOR,
        ).pack(anchor="w")

        self.quote_label = tk.Label(
            card,
            text='" Pick a mood to begin… "',
            font=("Georgia", 12, "italic"),
            fg=TEXT_COLOR,
            bg=CARD_COLOR,
            wraplength=520,
            justify="left",
        )
        self.quote_label.pack(anchor="w", pady=(6, 0))

    def _build_control_buttons(self):
        """Shuffle, Stop, and Exit buttons."""
        controls = tk.Frame(self.root, bg=BG_COLOR, pady=18)
        controls.pack()

        btn_cfg = dict(
            font=("Helvetica", 11, "bold"),
            relief="flat",
            bd=0,
            padx=22,
            pady=11,
            cursor="hand2",
        )

        # Shuffle – rolls a new song + quote for the current mood
        self.shuffle_btn = tk.Button(
            controls,
            text="⟳  Shuffle",
            fg="white",
            bg="#2ECC71",
            activebackground="#27AE60",
            activeforeground="white",
            command=self._on_shuffle,
            state="disabled",       # enabled only after a mood is chosen
            **btn_cfg,
        )
        self.shuffle_btn.pack(side="left", padx=8)

        # Stop – halts playback without clearing the display
        tk.Button(
            controls,
            text="◼  Stop",
            fg="white",
            bg=ACCENT_COLOR,
            activebackground="#C0392B",
            activeforeground="white",
            command=self._on_stop,
            **btn_cfg,
        ).pack(side="left", padx=8)

        # Exit – stop audio then close the window
        tk.Button(
            controls,
            text="✕  Exit",
            fg="white",
            bg="#555577",
            activebackground="#333355",
            activeforeground="white",
            command=self._on_exit,
            **btn_cfg,
        ).pack(side="left", padx=8)

    def _build_status_bar(self):
        """Thin bar at the bottom showing dataset info."""
        stats_text = get_mood_stats(self.df)
        bar = tk.Frame(self.root, bg=PANEL_COLOR, pady=6)
        bar.pack(fill="x", side="bottom")

        tk.Label(
            bar,
            text=f"📂 {stats_text} ",
            font=("Helvetica", 9),
            fg=MUTED_COLOR,
            bg=PANEL_COLOR,
        ).pack()

    # ── Event handlers ────────────────────────

    def _on_mood_selected(self, mood: str):
        """Called when a mood button is clicked."""
        self.current_mood = mood
        self._play_entry(mood)
        # Enable Shuffle now that a mood is active
        self.shuffle_btn.config(state="normal")

    def _on_shuffle(self):
        """Pick a new random song + quote for the current mood."""
        if self.current_mood:
            self._play_entry(self.current_mood)

    def _on_stop(self):
        """Stop music playback."""
        stop_music()
        self.song_label.config(text="♪  — stopped —")

    def _on_exit(self):
        """Gracefully quit the application."""
        stop_music()
        pygame.mixer.quit()
        self.root.destroy()

    # ── Core playback logic ───────────────────

    def _play_entry(self, mood: str):
        """
        Fetch a random entry for `mood`, update the display labels,
        and start audio playback.
        """
        try:
            entry = get_random_entry(self.df, mood)
        except ValueError as e:
            messagebox.showerror("Data Error", str(e))
            return

        # Update the display card
        icon = MOOD_ICONS.get(mood, "🎵")
        self.mood_label.config(
            text=f"{icon}  {mood.capitalize()}",
            fg=MOOD_COLORS.get(mood, TEXT_COLOR),
        )
        self.song_label.config(text=f"♪  {entry['song_name']}")
        self.quote_label.config(text=f'" {entry["quote"]} "')

        # Start playing the audio file
        play_song(entry["song_path"])


def main():
    # 1. Load and validate the dataset
    try:
        df = load_data(CSV_FILE)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    # 2. Initialise pygame audio
    init_audio()

    # 3. Build and run the Tkinter application
    root = tk.Tk()
    app  = EmotionMusicPlayer(root, df)

    # Handle the window's X button the same as our Exit button
    root.protocol("WM_DELETE_WINDOW", app._on_exit)

    root.mainloop()


if __name__ == "__main__":
    main()
