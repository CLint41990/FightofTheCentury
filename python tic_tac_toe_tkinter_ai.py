import tkinter as tk
from tkinter import messagebox, simpledialog
import math
import time
import pickle
import random

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.current_player = "<3"
        self.cyrus_wins = 0
        self.kalaban_wins = 0
        self.difficulty = self.select_difficulty()  # Select difficulty level
        self.update_background_color()  # Update the background color based on difficulty
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.create_scoreboard()
        self.create_board()
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.state_action_values = self.load_learning_data()

    def select_difficulty(self):
        difficulty = simpledialog.askstring("Select Difficulty", "Choose difficulty: Easy, Medium, Hard")
        if difficulty and difficulty.lower() in ["easy", "medium", "hard"]:
            return difficulty.lower()
        else:
            return "medium"  # Default to medium if no valid input

    def update_background_color(self):
        if self.difficulty == "easy":
            self.root.configure(bg="#90EE90")  # Light Green
        elif self.difficulty == "medium":
            self.root.configure(bg="#FFFFE0")  # Light Yellow
        elif self.difficulty == "hard":
            self.root.configure(bg="#FFCCCB")  # Light Red

    def create_scoreboard(self):
        self.scoreboard = tk.Label(self.root, text=f"Cyrus: {self.cyrus_wins} | Kalaban: {self.kalaban_wins}", 
                                   font=('normal', 15), bg=self.root.cget('bg'), fg="black")
        self.scoreboard.grid(row=3, column=0, columnspan=3)

    def update_scoreboard(self):
        self.scoreboard.config(text=f"Cyrus: {self.cyrus_wins} | Kalaban: {self.kalaban_wins}")

    def check_champion(self):
        if self.cyrus_wins >= 3:
            messagebox.showinfo("Champion!", "Congratulations! Cyrus is the champion!")
            self.reset_game()
        elif self.kalaban_wins >= 3:
            messagebox.showinfo("Champion!", "Kalaban is the champion! Better luck next time, Cyrus!")
            self.reset_game()

    def reset_game(self):
        self.cyrus_wins = 0
        self.kalaban_wins = 0
        self.update_scoreboard()
        self.reset_board()

    def create_board(self):
        for row in range(3):
            for col in range(3):
                button = tk.Button(self.root, text="", font=('normal', 20), width=5, height=2,
                                   command=lambda r=row, c=col: self.on_button_click(r, c),
                                   bg="black", fg="white")
                button.grid(row=row, column=col, padx=5, pady=5)
                self.buttons[row][col] = button

    def animate_button(self, button):
        for size in range(20, 26):
            button.config(font=('normal', size))
            self.root.update()
            time.sleep(0.02)
        for size in range(26, 20, -1):
            button.config(font=('normal', size))
            self.root.update()
            time.sleep(0.02)

    def on_button_click(self, row, col):
        if self.buttons[row][col]["text"] == "" and not self.check_winner():
            self.buttons[row][col]["text"] = self.current_player
            self.animate_button(self.buttons[row][col])
            if self.check_winner():
                self.highlight_winner()
                if self.current_player == "<3":
                    self.cyrus_wins += 1
                else:
                    self.kalaban_wins += 1
                self.update_scoreboard()
                self.show_winner(f"Player {self.current_player} wins!")
                self.check_champion()
            elif self.is_draw():
                self.show_winner("It's a draw!")
            else:
                self.current_player = ":<" if self.current_player == "<3" else "<3"
                if self.current_player == ":<":
                    self.ai_move()

    def ai_move(self):
        if self.difficulty == "easy":
            self.random_move()
        elif self.difficulty == "medium":
            self.minimax_move(max_depth=2)
        else:
            self.minimax_move()

    def random_move(self):
        available_moves = [(row, col) for row in range(3) for col in range(3) if self.buttons[row][col]["text"] == ""]
        if available_moves:
            row, col = random.choice(available_moves)
            self.buttons[row][col]["text"] = ":<"
            self.animate_button(self.buttons[row][col])
            if self.check_winner():
                self.highlight_winner()
                self.kalaban_wins += 1
                self.update_scoreboard()
                self.show_winner("Player :< wins!")
                self.check_champion()
            elif self.is_draw():
                self.show_winner("It's a draw!")
            else:
                self.current_player = "<3"

    def minimax_move(self, max_depth=None):
        best_score = -math.inf
        best_moves = []
        current_state = self.get_state()

        for row in range(3):
            for col in range(3):
                if self.buttons[row][col]["text"] == "":
                    self.buttons[row][col]["text"] = ":<"
                    move_value = self.minimax(0, False, max_depth)
                    self.buttons[row][col]["text"] = ""
                    if move_value > best_score:
                        best_score = move_value
                        best_moves = [(row, col)]
                    elif move_value == best_score:
                        best_moves.append((row, col))

        if best_moves:
            random.shuffle(best_moves)
            row, col = random.choice(best_moves)
            self.buttons[row][col]["text"] = ":<"
            self.animate_button(self.buttons[row][col])
            if self.check_winner():
                self.update_state_action_value(current_state, (row, col), 1)
                self.highlight_winner()
                self.kalaban_wins += 1
                self.update_scoreboard()
                self.show_winner("Player :< wins!")
                self.check_champion()
            elif self.is_draw():
                self.update_state_action_value(current_state, (row, col), 0.5)
                self.show_winner("It's a draw!")
            else:
                self.current_player = "<3"

    def minimax(self, depth, is_maximizing, max_depth=None):
        if self.check_winner():
            return 1 if self.current_player == ":<" else -1
        if self.is_draw():
            return 0

        if max_depth is not None and depth >= max_depth:
            return 0

        if is_maximizing:
            best_score = -math.inf
            for row in range(3):
                for col in range(3):
                    if self.buttons[row][col]["text"] == "":
                        self.buttons[row][col]["text"] = ":<"
                        score = self.minimax(depth + 1, False, max_depth)
                        self.buttons[row][col]["text"] = ""
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = math.inf
            for row in range(3):
                for col in range(3):
                    if self.buttons[row][col]["text"] == "":
                        self.buttons[row][col]["text"] = "<3"
                        score = self.minimax(depth + 1, True, max_depth)
                        self.buttons[row][col]["text"] = ""
                        best_score = min(score, best_score)
            return best_score

    def check_winner(self):
        for row in range(3):
            if self.buttons[row][0]["text"] == self.buttons[row][1]["text"] == self.buttons[row][2]["text"] != "":
                self.winning_combo = [(row, 0), (row, 1), (row, 2)]
                return True
        for col in range(3):
            if self.buttons[0][col]["text"] == self.buttons[1][col]["text"] == self.buttons[2][col]["text"] != "":
                self.winning_combo = [(0, col), (1, col), (2, col)]
                return True
        if self.buttons[0][0]["text"] == self.buttons[1][1]["text"] == self.buttons[2][2]["text"] != "":
            self.winning_combo = [(0, 0), (1, 1), (2, 2)]
            return True
        if self.buttons[0][2]["text"] == self.buttons[1][1]["text"] == self.buttons[2][0]["text"] != "":
            self.winning_combo = [(0, 2), (1, 1), (2, 0)]
            return True
        return False

    def is_draw(self):
        for row in range(3):
            for col in range(3):
                if self.buttons[row][col]["text"] == "":
                    return False
        return True

    def highlight_winner(self):
        for row, col in self.winning_combo:
            self.buttons[row][col].config(bg="darkgreen")
        self.root.update()
        time.sleep(1)

    def show_winner(self, message):
        messagebox.showinfo("Game Over", message)
        self.reset_board()

    def reset_board(self):
        self.current_player = "<3"
        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(text="", bg="black", fg="white")

    def get_state(self):
        return tuple(tuple(self.buttons[row][col]["text"] for col in range(3)) for row in range(3))

    def get_state_action_value(self, state, action):
        if (state, action) not in self.state_action_values:
            self.state_action_values[(state, action)] = 0.5
        return self.state_action_values[(state, action)]

    def update_state_action_value(self, state, action, reward):
        previous_value = self.get_state_action_value(state, action)
        self.state_action_values[(state, action)] = previous_value + self.learning_rate * (reward - previous_value)

    def save_learning_data(self):
        with open("tic_tac_toe_learning_data.pkl", "wb") as f:
            pickle.dump(self.state_action_values, f)

    def load_learning_data(self):
        try:
            with open("tic_tac_toe_learning_data.pkl", "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {}

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
    game.save_learning_data()
