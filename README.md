# Tic Tac Toe (Python + tkinter)

A graphical Tic Tac Toe game built with Python's `tkinter` library, featuring an unbeatable AI opponent powered by the **Minimax algorithm**, plus sound effects.

## Features
- 🎮 Three game modes: Player vs Player, Vs Computer (Easy), Vs Computer (Unbeatable - Minimax)
- 🧠 Minimax algorithm for optimal AI decision-making
- 🔊 Synthesized sound effects (no external audio files needed)
- 🎨 Modern dark-themed UI with hover effects
- 📊 Live scoreboard

## Requirements
- Python 3.x
- `pygame` (optional, only needed for sound effects)

## Installation
```bash
git clone https://github.com/ayeshajavid91-star/tic-tac-toe-python.git
cd tic-tac-toe-python
pip install -r requirements.txt
```

## How to Run
```bash
python tic_tac_toe.py
```

## How It Works
The AI opponent uses the **Minimax algorithm** — it recursively simulates every possible future move to find the best one, assuming both players play optimally. This makes the "Unbeatable" mode impossible to beat (best case: a draw).

## License
Free to use and modify.
