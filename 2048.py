import tkinter as tk
import random
import os
import copy

root = tk.Tk()
root.title("2048 Pro")
root.geometry("500x650")
root.configure(bg="#faf8ef")

SIZE = 4
CELL = 100
GAP = 10

board = [[0]*SIZE for _ in range(SIZE)]
score = 0
best = 0
previous = None
game_over = False
won = False

colors = {
    0:"#cdc1b4", 2:"#eee4da", 4:"#ede0c8",
    8:"#f2b179", 16:"#f59563", 32:"#f67c5f",
    64:"#f65e3b", 128:"#edcf72",
    256:"#edcc61", 512:"#edc850",
    1024:"#edc53f", 2048:"#edc22e"
}

if os.path.exists("best_score.txt"):
    try:
        best = int(open("best_score.txt").read())
    except ValueError:
        best = 0

title = tk.Label(root, text="2048 PRO",
                 font=("Arial", 30, "bold"),
                 bg="#faf8ef")
title.pack()

info = tk.Label(root, font=("Arial", 16),
                bg="#faf8ef")
info.pack()

canvas = tk.Canvas(root, width=460, height=460,
                   bg="#bbada0", highlightthickness=0)
canvas.pack(pady=10)

def save_best():
    global best
    if score > best:
        best = score
        with open("best_score.txt", "w") as f:
            f.write(str(best))

def add_tile():
    empty = [(r,c) for r in range(4)
             for c in range(4) if board[r][c] == 0]
    if empty:
        r,c = random.choice(empty)
        board[r][c] = random.choice([2,2,2,2,2,2,2,2,2,4])

def new_game():
    global board, score, previous, game_over, won
    board = [[0]*4 for _ in range(4)]
    score = 0
    previous = None
    game_over = won = False
    add_tile()
    add_tile()
    draw_game()

def merge_line(line):
    global score
    a = [x for x in line if x != 0]
    result = []
    i = 0
    while i < len(a):
        if i+1 < len(a) and a[i] == a[i+1]:
            result.append(a[i]*2)
            score += a[i]*2
            i += 2
        else:
            result.append(a[i])
            i += 1
    return result + [0]*(4-len(result))

def can_move():
    for r in range(4):
        for c in range(4):
            if board[r][c] == 0:
                return True
            if c < 3 and board[r][c] == board[r][c+1]:
                return True
            if r < 3 and board[r][c] == board[r+1][c]:
                return True
    return False

def move(direction):
    global board, previous, game_over, won

    if game_over or won:
        return

    old = copy.deepcopy(board)
    old_score = score

    for i in range(4):
        if direction == "LEFT":
            board[i] = merge_line(board[i])
        elif direction == "RIGHT":
            board[i] = merge_line(board[i][::-1])[::-1]
        else:
            col = [board[r][i] for r in range(4)]
            if direction == "DOWN":
                col = col[::-1]
            col = merge_line(col)
            if direction == "DOWN":
                col = col[::-1]
            for r in range(4):
                board[r][i] = col[r]

    if board != old:
        previous = (old, old_score)
        add_tile()
        save_best()
        if any(2048 in row for row in board):
            won = True
        if not can_move():
            game_over = True

    draw_game()

def undo():
    global board, score, previous, game_over, won
    if previous:
        board, score = previous
        board = copy.deepcopy(board)
        previous = None
        game_over = won = False
        draw_game()

def draw_game():
    canvas.delete("all")
    info.config(text=f"Score: {score}     Best: {best}")

    for r in range(4):
        for c in range(4):
            value = board[r][c]
            x = 10 + c*112
            y = 10 + r*112

            canvas.create_rectangle(
                x, y, x+100, y+100,
                fill=colors.get(value, "#3c3a32"),
                outline=""
            )

            if value:
                canvas.create_text(
                    x+50, y+50,
                    text=str(value),
                    font=("Arial", 25, "bold"),
                    fill="#776e65" if value <= 4 else "white"
                )

    if game_over or won:
        msg = "GAME OVER!" if game_over else "YOU WON!"
        canvas.create_text(230, 230, text=msg,
                           font=("Arial", 25, "bold"),
                           fill="red")

def key_press(event):
    keys = {
        "Left":"LEFT", "Right":"RIGHT",
        "Up":"UP", "Down":"DOWN"
    }
    if event.keysym in keys:
        move(keys[event.keysym])
    elif event.keysym == "r":
        new_game()
    elif event.keysym == "u":
        undo()

tk.Button(root, text="NEW GAME",
          command=new_game).pack(side="left", padx=120)

tk.Button(root, text="UNDO",
          command=undo).pack(side="left")

root.bind("<Key>", key_press)

new_game()
root.mainloop()