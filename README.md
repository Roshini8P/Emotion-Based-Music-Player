# 🎵 Emotion-Based Music Player with Quotes

A desktop music player that matches songs and inspirational quotes to your current mood.
Built with **Tkinter**, **pandas**, **numpy**, and **pygame** — no machine learning required.

---

## ✨ Features

| Feature | Details |
|---|---|
| **5 moods** | Happy 😊 · Sad 😢 · Calm 😌 · Energetic ⚡ · Romantic 💖 |
| **Smart shuffle** | Uses `numpy.random.randint` for truly random selection |
| **Live quotes** | Inspirational quote updates with every song change |
| **Music controls** | Shuffle · Stop · Exit |
| **Dark themed GUI** | Clean, colour-coded per mood |

---

## 📁 Project Structure

```
emotion_music_player/
│
├── player.py           ← Main application (run this)
├── songs_data.csv      ← Data: mood, song_path, quote columns
├── requirements.txt    ← pip dependencies
├── README.md           ← This file
│
└── songs/              ← Audio files, one sub-folder per mood
    ├── happy/
    │   ├── happy_1.wav
    │   └── ...
    ├── sad/
    ├── calm/
    ├── energetic/
    └── romantic/
```

---

## 🚀 Quick Start

### 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### 2 — Add your own music *(optional but recommended)*
Drop `.wav` or `.mp3` files into the matching mood folder, then update `songs_data.csv`:

```csv
mood,song_path,quote
happy,songs/happy/my_song.mp3,"Your quote here."
```

### 3 — Run the player
```bash
python player.py
```

---

## 📊 How pandas & numpy are used

| Library | Where | Purpose |
|---|---|---|
| **pandas** | `load_data()` | Read CSV, validate columns, clean strings, derive `song_name` column, compute `mood_share` per row |
| **pandas** | `get_random_entry()` | Filter DataFrame by mood with boolean indexing |
| **pandas** | `get_mood_stats()` | Aggregate total rows and unique mood count |
| **numpy** | `get_random_entry()` | `np.random.randint(0, len(mood_df))` for unbiased random index selection |

---

## 🎨 Mood Color Palette

| Mood | Color |
|---|---|
| Happy | Sunny Yellow `#F4D03F` |
| Sad | Soft Blue `#85C1E9` |
| Calm | Mint Green `#A9DFBF` |
| Energetic | Warm Coral `#F1948A` |
| Romantic | Blush Pink `#F1A7C7` |

---

## 🛠️ Customisation

**Add a new mood:**
1. Create `songs/new_mood/` and add audio files
2. Add rows in `songs_data.csv` with `mood = new_mood`
3. In `player.py`, add the mood to `MOOD_ICONS` and `MOOD_COLORS`

**Change the theme:**
Edit the colour constants near the top of `player.py` (all caps variables under `# UI palette`).

---

## 🐛 Troubleshooting

| Issue | Fix |
|---|---|
| `pygame.error: Failed to load audio` | Ensure the file path in CSV matches the actual file location |
| `FileNotFoundError: songs_data.csv` | Run the script from inside the `emotion_music_player/` folder |
| No sound on Linux | `sudo apt install libsdl2-mixer-2.0-0` |
| No sound on macOS | Grant microphone/audio permissions in System Settings |
