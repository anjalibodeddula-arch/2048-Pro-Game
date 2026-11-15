import pygame
import random
import os
import copy

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 500, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 Pro - Puzzle Challenge")

# Colors
BACKGROUND = (250, 248, 239)
GRID_COLOR = (187, 173, 160)
EMPTY_COLOR = (205, 193, 180)
TEXT_COLOR = (80, 70, 60)

TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46)
}

# Fonts
title_font = pygame.font.SysFont("arial", 42, bold=True)
font = pygame.font.SysFont("arial", 28, bold=True)
small_font = pygame.font.SysFont("arial", 20)

# Game variables
SIZE = 4
CELL = 100
GAP = 10
BOARD_X = 40
BOARD_Y = 190

board = [[0] * SIZE for _ in range(SIZE)]
score = 0
best_score = 0
previous_state = None
game_over = False
won = False

# Load best score
if os.path.exists("best_score.txt"):
    try:
        with open("best_score.txt", "r") as file:
            best_score = int(file.read())
    except ValueError:
        best_score = 0


def save_best():
    global best_score
    if score > best_score:
        best_score = score
        with open("best_score.txt", "w") as file:
            file.write(str(best_score))


def add_tile():
    empty = [
        (r, c)
        for r in range(SIZE)
        for c in range(SIZE)
        if board[r][c] == 0
    ]

    if empty:
        r, c = random.choice(empty)
        board[r][c] = 4 if random.random() < 0.1 else 2


def new_game():
    global board, score, previous_state, game_over, won

    board = [[0] * SIZE for _ in range(SIZE)]
    score = 0
    previous_state = None
    game_over = False
    won = False

    add_tile()
    add_tile()


def merge_line(line):
    global score

    values = [x for x in line if x != 0]
    result = []
    i = 0

    while i < len(values):
        if i + 1 < len(values) and values[i] == values[i + 1]:
            merged = values[i] * 2
            result.append(merged)
            score += merged
            i += 2
        else:
            result.append(values[i])
            i += 1

    return result + [0] * (SIZE - len(result))


def move(direction):
    global board, previous_state, game_over, won

    if game_over or won:
        return

    old_board = copy.deepcopy(board)
    old_score = score

    for i in range(SIZE):

        if direction == "LEFT":
            board[i] = merge_line(board[i])

        elif direction == "RIGHT":
            board[i] = merge_line(board[i][::-1])[::-1]

        elif direction == "UP":
            column = [board[r][i] for r in range(SIZE)]
            column = merge_line(column)

            for r in range(SIZE):
                board[r][i] = column[r]

        elif direction == "DOWN":
            column = [board[r][i] for r in range(SIZE)]
            column = merge_line(column[::-1])[::-1]

            for r in range(SIZE):
                board[r][i] = column[r]

    if board != old_board:
        previous_state = (old_board, old_score)
        add_tile()
        save_best()

        if any(2048 in row for row in board):
            won = True

        if not can_move():
            game_over = True


def can_move():
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                return True

            if c < SIZE - 1 and board[r][c] == board[r][c + 1]:
                return True

            if r < SIZE - 1 and board[r][c] == board[r + 1][c]:
                return True

    return False


def undo():
    global board, score, previous_state, game_over, won

    if previous_state is not None:
        board, score = previous_state
        board = copy.deepcopy(board)
        previous_state = None
        game_over = False
        won = False


def draw_button(text, x, y, width, height):
    pygame.draw.rect(
        screen, (119, 110, 101),
        (x, y, width, height), border_radius=8
    )

    label = small_font.render(text, True, (255, 255, 255))
    screen.blit(
        label,
        (x + (width - label.get_width()) // 2,
         y + (height - label.get_height()) // 2)
    )


def draw_game():
    screen.fill(BACKGROUND)

    # Title
    title = title_font.render("2048 PRO", True, TEXT_COLOR)
    screen.blit(title, (40, 25))

    # Score
    score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
    screen.blit(score_text, (40, 90))

    best_text = small_font.render(
        f"Best: {best_score}", True, TEXT_COLOR
    )
    screen.blit(best_text, (40, 130))

    # Buttons
    draw_button("NEW GAME", 290, 90, 160, 40)
    draw_button("UNDO", 290, 140, 160, 35)

    # Board background
    pygame.draw.rect(
        screen, GRID_COLOR,
        (BOARD_X - GAP, BOARD_Y - GAP,
         4 * CELL + 5 * GAP, 4 * CELL + 5 * GAP),
        border_radius=8
    )

    # Draw tiles
    for r in range(SIZE):
        for c in range(SIZE):

            value = board[r][c]

            x = BOARD_X + c * (CELL + GAP)
            y = BOARD_Y + r * (CELL + GAP)

            color = TILE_COLORS.get(value, (60, 58, 50)) if value else EMPTY_COLOR

            pygame.draw.rect(
                screen, color,
                (x, y, CELL, CELL),
                border_radius=6
            )

            if value:
                text_color = (
                    TEXT_COLOR if value <= 4
                    else (255, 255, 255)
                )

                tile_font = pygame.font.SysFont(
                    "arial", 30 if value < 1000 else 23, bold=True
                )

                text = tile_font.render(
                    str(value), True, text_color
                )

                screen.blit(
                    text,
                    (x + (CELL - text.get_width()) // 2,
                     y + (CELL - text.get_height()) // 2)
                )

    # Game messages
    if game_over or won:
        message = "GAME OVER!" if game_over else "YOU REACHED 2048!"

        text = font.render(message, True, (180, 60, 40))
        screen.blit(
            text,
            ((WIDTH - text.get_width()) // 2, 610)
        )


# Start game
new_game()

clock = pygame.time.Clock()
running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_LEFT:
                move("LEFT")

            elif event.key == pygame.K_RIGHT:
                move("RIGHT")

            elif event.key == pygame.K_UP:
                move("UP")

            elif event.key == pygame.K_DOWN:
                move("DOWN")

            elif event.key == pygame.K_r:
                new_game()

            elif event.key == pygame.K_u:
                undo()

        if event.type == pygame.MOUSEBUTTONDOWN:

            mx, my = event.pos

            if 290 <= mx <= 450 and 90 <= my <= 130:
                new_game()

            elif 290 <= mx <= 450 and 140 <= my <= 175:
                undo()

    draw_game()
    pygame.display.update()
    clock.tick(60)

pygame.quit()