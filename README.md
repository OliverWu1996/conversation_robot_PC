# Conversation Robot PC

A conversation robot that has a **life**. It features **VASR** (Voice Activated Speech Recognition) and keeps **learning and growing** with you over time.

---

## Features

| Feature | Description |
|---------|-------------|
| 🎤 **VASR** | Voice Activated Speech Recognition — speak to the robot, it listens and responds via text-to-speech |
| 🧠 **Learning memory** | Stores every conversation in a local SQLite database; learns facts you teach it |
| 💓 **Life system** | The robot has a mood, energy level, happiness and curiosity that evolve with each interaction |
| 📅 **Day cycle** | Energy restores overnight; the robot ages one day each new session |
| 💾 **Persistent state** | Life state and memories are saved to disk and restored on the next run |

---

## Project structure

```
conversation_robot_PC/
├── main.py            # Entry point
├── requirements.txt
├── robot/
│   ├── brain.py       # Conversation logic + sentiment analysis
│   ├── life.py        # Mood / energy / happiness / curiosity
│   ├── memory.py      # SQLite-backed conversation history & learned facts
│   └── voice.py       # VASR — speech-to-text + text-to-speech
└── tests/
    ├── test_brain.py
    ├── test_life.py
    └── test_memory.py
```

---

## Quick start

### 1 — Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `pyaudio` requires system-level libraries.
> macOS: `brew install portaudio`
> Ubuntu/Debian: `sudo apt-get install portaudio19-dev python3-pyaudio`

### 2 — Run in text mode

```bash
python main.py
```

### 3 — Run with voice (VASR)

```bash
python main.py --voice
```

### 4 — Custom data directory

```bash
python main.py --data-dir /path/to/my/data
```

---

## Conversation examples

```
You: Hello!
Robot: Hi there! Great to see you!

You: How are you?
Robot: Feeling curious today. How about you?

You: Remember that Python was created by Guido van Rossum
Robot: That's interesting! I'll remember that.

You: What do you know about Python?
Robot: I know these things about 'Python': Python was created by Guido van Rossum.

You: What is your status?
Robot: I'm curious today. Energy: 94.0, Happiness: 52.5, Age: 1 day(s).
```

---

## Running the tests

```bash
pip install pytest
pytest tests/
```

---

## License

MIT — see [LICENSE](LICENSE).
