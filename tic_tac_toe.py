"""
Tic Tac Toe - GUI Version with Minimax AI + Sound Effects (tkinter)

Features:
- Main menu: Player vs Player, Vs Computer (Easy/Random), Vs Computer (Unbeatable/Minimax)
- Minimax algorithm for the unbeatable AI opponent
- Hover effects, AI "thinking" delay, winning-line highlight, scoreboard
- Sound effects for moves, win, and draw (synthesized in-memory, no audio files needed)
- Mute/unmute toggle

Requires: pip install pygame   (only needed for sound; game still runs without it)
"""

import tkinter as tk
from tkinter import messagebox
import math
import random
import io
import wave
import struct

# Sound is optional - the game still works fine if pygame isn't installed
try:
    import pygame
    SOUND_LIBRARY_AVAILABLE = True
except ImportError:
    SOUND_LIBRARY_AVAILABLE = False

# ---------- Colors / Theme ----------
BG_COLOR = "#1e272e"
PANEL_COLOR = "#2f3640"
ACCENT_X = "#e74c3c"
ACCENT_O = "#3498db"
CELL_BG = "#353b48"
CELL_HOVER = "#4b5366"
CELL_WIN = "#27ae60"
TEXT_COLOR = "#f5f6fa"
BTN_COLOR = "#4a69bd"
BTN_HOVER = "#6a89cc"

WINNING_COMBINATIONS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6)              # diagonals
]


def check_winner_static(board):
    """Returns 'X', 'O' if there's a winner on this board, else None."""
    for a, b, c in WINNING_COMBINATIONS:
        if board[a] != "" and board[a] == board[b] == board[c]:
            return board[a]
    return None


class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.mode = None          # "pvp", "easy", "minimax"
        self.board = [""] * 9
        self.buttons = []
        self.current_player = "X"
        self.human_symbol = "X"
        self.computer_symbol = "O"
        self.scores = {"X": 0, "O": 0, "Draw": 0}
        self.game_active = False
        self.winning_cells = ()

        self.sound_on = True
        self.audio_ready = False
        self.sounds = {}
        self.setup_sounds()

        self.show_menu()

    # ---------------------------------------------------------------
    # SOUND SETUP
    # ---------------------------------------------------------------
    def setup_sounds(self):
        """
        Synthesizes every sound effect in memory using simple sine waves -
        no external .wav/.mp3 files needed. Fails silently (no sound) if
        pygame isn't installed or there's no audio device available.
        """
        if not SOUND_LIBRARY_AVAILABLE:
            return
        try:
            pygame.mixer.init()
            self.sounds = {
                "x_move": self.generate_tone(523.25, 0.08),                    # C5 - short click
                "o_move": self.generate_tone(392.00, 0.08),                    # G4 - short click
                "win":    self.generate_tone([523.25, 659.25, 783.99], 0.12),  # C-E-G ascending jingle
                "draw":   self.generate_tone([330.0, 277.0], 0.18),            # neutral descending tone
                "click":  self.generate_tone(440.0, 0.05),                     # generic UI click
            }
            self.audio_ready = True
        except Exception:
            # No audio device, or pygame mixer failed to start - game still works, just silent
            self.audio_ready = False

    def generate_tone(self, frequencies, note_duration=0.12, volume=0.5, sample_rate=44100):
        """
        Builds a short WAV clip purely with math (sine waves) and returns it as a
        pygame.mixer.Sound. `frequencies` can be a single number (one note) or a
        list (a short played-in-sequence melody, e.g. a win jingle).
        A fade-out envelope is applied to each note so it doesn't 'click' at the end.
        """
        if isinstance(frequencies, (int, float)):
            frequencies = [frequencies]

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)        # mono
            wav_file.setsampwidth(2)        # 16-bit samples
            wav_file.setframerate(sample_rate)

            frames = bytearray()
            n_samples = int(sample_rate * note_duration)
            for freq in frequencies:
                for i in range(n_samples):
                    t = i / sample_rate
                    fade = 1.0 - (i / n_samples) ** 2        # smooth fade-out envelope
                    sample = volume * fade * math.sin(2 * math.pi * freq * t)
                    frames += struct.pack("<h", int(sample * 32767))
            wav_file.writeframes(frames)

        buffer.seek(0)
        return pygame.mixer.Sound(buffer)

    def play_sound(self, name):
        if self.audio_ready and self.sound_on and name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception:
                pass

    def toggle_sound(self):
        self.sound_on = not self.sound_on
        self.sound_btn.config(text=("🔊 Sound: On" if self.sound_on else "🔇 Sound: Off"))
        if self.sound_on:
            self.play_sound("click")

    # ---------------------------------------------------------------
    # MENU SCREEN
    # ---------------------------------------------------------------
    def show_menu(self):
        self.play_sound("click")
        self.clear_window()
        self.menu_frame = tk.Frame(self.root, bg=BG_COLOR, padx=40, pady=40)
        self.menu_frame.pack()

        tk.Label(
            self.menu_frame, text="Tic Tac Toe", font=("Helvetica", 28, "bold"),
            bg=BG_COLOR, fg=TEXT_COLOR
        ).pack(pady=(0, 5))

        tk.Label(
            self.menu_frame, text="Choose a game mode", font=("Helvetica", 12),
            bg=BG_COLOR, fg="#b2bec3"
        ).pack(pady=(0, 20))

        self.make_menu_button("Player vs Player", lambda: self.start_game("pvp")).pack(pady=6, fill="x")
        self.make_menu_button("Vs Computer (Easy)", lambda: self.start_game("easy")).pack(pady=6, fill="x")
        self.make_menu_button("Vs Computer (Unbeatable - Minimax)", lambda: self.start_game("minimax")).pack(pady=6, fill="x")

        if not SOUND_LIBRARY_AVAILABLE:
            tk.Label(
                self.menu_frame, text="(Install 'pygame' for sound effects: pip install pygame)",
                font=("Helvetica", 9), bg=BG_COLOR, fg="#7f8c8d"
            ).pack(pady=(15, 0))

    def make_menu_button(self, text, command):
        def wrapped():
            self.play_sound("click")
            command()
        btn = tk.Button(
            self.menu_frame, text=text, font=("Helvetica", 13, "bold"),
            bg=BTN_COLOR, fg=TEXT_COLOR, activebackground=BTN_HOVER,
            activeforeground=TEXT_COLOR, bd=0, padx=20, pady=12,
            cursor="hand2", command=wrapped
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=BTN_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=BTN_COLOR))
        return btn

    # ---------------------------------------------------------------
    # GAME SCREEN
    # ---------------------------------------------------------------
    def start_game(self, mode):
        self.mode = mode
        self.scores = {"X": 0, "O": 0, "Draw": 0}
        self.clear_window()
        self.build_game_screen()
        self.new_round()

    def build_game_screen(self):
        container = tk.Frame(self.root, bg=BG_COLOR, padx=20, pady=20)
        container.pack()

        mode_text = {
            "pvp": "Player vs Player",
            "easy": "You (X) vs Computer (O) - Easy",
            "minimax": "You (X) vs Computer (O) - Unbeatable"
        }[self.mode]
        tk.Label(
            container, text=mode_text, font=("Helvetica", 13, "bold"),
            bg=BG_COLOR, fg="#b2bec3"
        ).pack(pady=(0, 5))

        self.status_label = tk.Label(
            container, text="", font=("Helvetica", 16, "bold"),
            bg=BG_COLOR, fg=TEXT_COLOR, pady=8
        )
        self.status_label.pack()

        self.score_label = tk.Label(
            container, text=self.get_score_text(), font=("Helvetica", 11),
            bg=BG_COLOR, fg="#b2bec3"
        )
        self.score_label.pack(pady=(0, 10))

        board_frame = tk.Frame(container, bg=BG_COLOR)
        board_frame.pack()

        self.buttons = []
        for i in range(9):
            btn = tk.Button(
                board_frame, text="", font=("Helvetica", 28, "bold"),
                width=4, height=2, bg=CELL_BG, fg=TEXT_COLOR,
                activebackground=CELL_HOVER, bd=0, cursor="hand2",
                command=lambda i=i: self.on_click(i)
            )
            btn.grid(row=i // 3, column=i % 3, padx=4, pady=4)
            btn.bind("<Enter>", lambda e, b=btn: self.on_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self.on_hover(b, False))
            self.buttons.append(btn)

        btn_row = tk.Frame(container, bg=BG_COLOR)
        btn_row.pack(pady=(15, 0), fill="x")

        restart_btn = tk.Button(
            btn_row, text="Restart Round", font=("Helvetica", 11, "bold"),
            bg=BTN_COLOR, fg=TEXT_COLOR, activebackground=BTN_HOVER,
            bd=0, padx=10, pady=8, cursor="hand2",
            command=lambda: (self.play_sound("click"), self.new_round())
        )
        restart_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        restart_btn.bind("<Enter>", lambda e: restart_btn.config(bg=BTN_HOVER))
        restart_btn.bind("<Leave>", lambda e: restart_btn.config(bg=BTN_COLOR))

        menu_btn = tk.Button(
            btn_row, text="Main Menu", font=("Helvetica", 11, "bold"),
            bg=PANEL_COLOR, fg=TEXT_COLOR, activebackground=CELL_HOVER,
            bd=0, padx=10, pady=8, cursor="hand2", command=self.show_menu
        )
        menu_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))
        menu_btn.bind("<Enter>", lambda e: menu_btn.config(bg=CELL_HOVER))
        menu_btn.bind("<Leave>", lambda e: menu_btn.config(bg=PANEL_COLOR))

        self.sound_btn = tk.Button(
            container, text=("🔊 Sound: On" if self.sound_on else "🔇 Sound: Off"),
            font=("Helvetica", 10), bg=PANEL_COLOR, fg=TEXT_COLOR,
            activebackground=CELL_HOVER, bd=0, padx=10, pady=6,
            cursor="hand2", command=self.toggle_sound
        )
        self.sound_btn.pack(pady=(10, 0), fill="x")
        self.sound_btn.bind("<Enter>", lambda e: self.sound_btn.config(bg=CELL_HOVER))
        self.sound_btn.bind("<Leave>", lambda e: self.sound_btn.config(bg=PANEL_COLOR))

    def on_hover(self, btn, entering):
        idx = self.buttons.index(btn)
        if self.game_active and self.board[idx] == "":
            btn.config(bg=CELL_HOVER if entering else CELL_BG)

    def get_score_text(self):
        label_x = "You" if self.mode != "pvp" else "X"
        label_o = "Computer" if self.mode != "pvp" else "O"
        return f"{label_x}: {self.scores['X']}    {label_o}: {self.scores['O']}    Draws: {self.scores['Draw']}"

    # ---------------------------------------------------------------
    # GAME LOGIC
    # ---------------------------------------------------------------
    def new_round(self):
        self.board = [""] * 9
        self.current_player = "X"
        self.game_active = True
        self.winning_cells = ()
        for btn in self.buttons:
            btn.config(text="", state="normal", bg=CELL_BG)
        self.status_label.config(text="Player X's turn", fg=ACCENT_X)

    def on_click(self, index):
        if not self.game_active or self.board[index] != "":
            return
        if self.mode != "pvp" and self.current_player == self.computer_symbol:
            return

        self.place_mark(index, self.current_player)

        if self.finish_if_game_over():
            return

        self.switch_turn()

        if self.mode != "pvp" and self.current_player == self.computer_symbol:
            self.root.after(450, self.computer_move)

    def place_mark(self, index, player):
        self.board[index] = player
        color = ACCENT_X if player == "X" else ACCENT_O
        self.buttons[index].config(text=player, fg=color, bg=CELL_BG)
        self.play_sound("x_move" if player == "X" else "o_move")

    def switch_turn(self):
        self.current_player = "O" if self.current_player == "X" else "X"
        color = ACCENT_X if self.current_player == "X" else ACCENT_O
        if self.mode != "pvp":
            who = "Your" if self.current_player == self.human_symbol else "Computer's"
            self.status_label.config(text=f"{who} turn", fg=color)
        else:
            self.status_label.config(text=f"Player {self.current_player}'s turn", fg=color)

    def finish_if_game_over(self):
        winner = check_winner_static(self.board)
        if winner:
            self.scores[winner] += 1
            self.score_label.config(text=self.get_score_text())
            self.highlight_winning_cells()
            self.game_active = False
            for btn in self.buttons:
                btn.config(state="disabled")
            self.play_sound("win")
            if self.mode != "pvp":
                msg = "You win! 🎉" if winner == self.human_symbol else "Computer wins!"
            else:
                msg = f"Player {winner} wins! 🎉"
            self.status_label.config(text=msg, fg=ACCENT_X if winner == "X" else ACCENT_O)
            self.root.after(150, lambda: messagebox.showinfo("Game Over", msg))
            return True

        if "" not in self.board:
            self.scores["Draw"] += 1
            self.score_label.config(text=self.get_score_text())
            self.game_active = False
            self.play_sound("draw")
            self.status_label.config(text="It's a draw!", fg=TEXT_COLOR)
            self.root.after(150, lambda: messagebox.showinfo("Game Over", "It's a draw!"))
            return True

        return False

    def highlight_winning_cells(self):
        for a, b, c in WINNING_COMBINATIONS:
            if self.board[a] != "" and self.board[a] == self.board[b] == self.board[c]:
                for i in (a, b, c):
                    self.buttons[i].config(bg=CELL_WIN)
                break

    # ---------------------------------------------------------------
    # COMPUTER AI (Easy = random, Minimax = unbeatable)
    # ---------------------------------------------------------------
    def computer_move(self):
        if not self.game_active:
            return

        if self.mode == "easy":
            move = self.random_move()
        else:
            move = self.best_move()

        if move is not None:
            self.place_mark(move, self.computer_symbol)

        if self.finish_if_game_over():
            return

        self.switch_turn()

    def random_move(self):
        empty_cells = [i for i, v in enumerate(self.board) if v == ""]
        return random.choice(empty_cells) if empty_cells else None

    def best_move(self):
        """Uses the Minimax algorithm to find the optimal move for the computer (O)."""
        best_score = -math.inf
        move = None
        for i in range(9):
            if self.board[i] == "":
                self.board[i] = self.computer_symbol
                score = self.minimax(self.board, 0, False)
                self.board[i] = ""
                if score > best_score:
                    best_score = score
                    move = i
        return move

    def minimax(self, board, depth, is_maximizing):
        """
        Recursively scores every possible game outcome.
        Computer (O) tries to MAXIMIZE the score, human (X) tries to MINIMIZE it.
        Depth is factored in so the AI prefers faster wins / slower losses.
        """
        winner = check_winner_static(board)
        if winner == self.computer_symbol:
            return 10 - depth
        if winner == self.human_symbol:
            return depth - 10
        if "" not in board:
            return 0

        if is_maximizing:
            best = -math.inf
            for i in range(9):
                if board[i] == "":
                    board[i] = self.computer_symbol
                    best = max(best, self.minimax(board, depth + 1, False))
                    board[i] = ""
            return best
        else:
            best = math.inf
            for i in range(9):
                if board[i] == "":
                    board[i] = self.human_symbol
                    best = min(best, self.minimax(board, depth + 1, True))
                    board[i] = ""
            return best

    # ---------------------------------------------------------------
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
