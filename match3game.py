import pygame
import sys
import random
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, MOUSEBUTTONDOWN

# Constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400
GRID_SIZE = 8
CELL_SIZE = min(WINDOW_WIDTH // GRID_SIZE, WINDOW_HEIGHT // GRID_SIZE)
SCREEN_SIZE = GRID_SIZE * CELL_SIZE
MARGIN = 5
NUM_COLORS = 5
ANIMATION_SPEED = 200
EMPTY = 0
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT_COLOR = (255, 253, 208)
COLORS = [
    None,  # No color with index 0
    (255, 128, 128),  # Red
    (0, 255, 0),  # Green
    (0, 0, 255),  # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255)  # Magenta
]

# Initialize Pygame
pygame.init()

# Initialize the screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Create game board
def create_board():
    board = []
    for y in range(GRID_SIZE):
        row = []
        for x in range(GRID_SIZE):
            available_colors = set(range(1, len(COLORS)))

            if x > 0:
                left_color = row[x - 1][0]
                if x > 1 and row[x - 2][0] == left_color:
                    available_colors.discard(left_color)
            
            if y > 0:
                above_color = board[y - 1][x][0]
                if y > 1 and board[y - 2][x][0] == above_color:
                    available_colors.discard(above_color)

            color = random.choice(list(available_colors))
            row.append((color, False))

        board.append(row)
    return board


# Draw game board
def draw_board(board, selected_candy=None):
    screen.fill(BLACK)

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            color_index = board[y][x][0]
            if 0 <= color_index < len(COLORS):
                color = COLORS[color_index]
                if color is not None:
                    pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            if board[y][x][1]:
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

    if selected_candy:
        x, y = selected_candy
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

    pygame.display.flip()

# Swap candies
def swap_candies(board, x1, y1, x2, y2):
    if (abs(x1 - x2) == 1 and y1 == y2) or (abs(y1 - y2) == 1 and x1 == x2):
        board[y1][x1], board[y2][x2] = board[y2][x2], board[y1][x1]
        return True
    return False

# Check for matches
def check_matches(board):
    matched_coords = set()

    # Check for horizontal matches
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE - 2):
            if (board[y][x][0] == board[y][x + 1][0] == board[y][x + 2][0]) and (board[y][x][0] != EMPTY):
                matched_coords.update({(x, y), (x + 1, y), (x + 2, y)})

    # Check for vertical matches
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE - 2):
            if (board[y][x][0] == board[y + 1][x][0] == board[y + 2][x][0]) and (board[y][x][0] != EMPTY):
                matched_coords.update({(x, y), (x, y + 1), (x, y + 2)})

    return matched_coords


# Remove matched candies
def remove_matches(board, matched_coords):
    print(f"Removing matches: {matched_coords}")
    for x, y in matched_coords:
        board[y][x] = (EMPTY, False)

    for x in range(GRID_SIZE):
        empty_cells = 0
        for y in range(GRID_SIZE - 1, -1, -1):
            if board[y][x][0] == EMPTY:
                empty_cells += 1
            elif empty_cells > 0:
                board[y + empty_cells][x] = board[y][x]
                board[y][x] = (EMPTY, False)

        for y in range(empty_cells):
            board[y][x] = (random.randint(1, len(COLORS) - 1), False)

    return board, matched_coords


def clear_matched_cells(matched_coords):
    for x, y in matched_coords:
        pygame.draw.rect(screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.display.update()

def pause_and_clear_matches(matched_coords, pause_time=500):
    clear_matched_cells(matched_coords)
    pygame.time.delay(pause_time)
    matched_coords.clear()

def get_cell_at_pixel(pixel):
    x, y = pixel
    if x < 0 or x >= GRID_SIZE * CELL_SIZE or y < 0 or y >= GRID_SIZE * CELL_SIZE:
        return None
    return x // CELL_SIZE, y // CELL_SIZE


# Game loop
def main():
    pygame.init()
    pygame.display.set_caption('Candy Crush Clone')
    global screen, clock
    screen = pygame.display.set_mode((GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE))
    clock = pygame.time.Clock()

    board = create_board()
    draw_board(board)

    selected_cell = None
    matched_coords = set()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if selected_cell is None:
                    selected_cell = get_cell_at_pixel(event.pos)
                else:
                    target_cell = get_cell_at_pixel(event.pos)
                    if target_cell and are_cells_adjacent(selected_cell, target_cell):
                        board, selected_cell, target_cell = try_swap_cells(board, selected_cell, target_cell)
                        matched_coords = check_matches(board)
                        if not matched_coords:
                            # Invalid swap, revert
                            board, selected_cell, target_cell = try_swap_cells(board, selected_cell, target_cell)
                    selected_cell = None

        if matched_coords:
            pause_and_clear_matches(matched_coords)
            board, matched_coords = remove_matches(board, matched_coords)

            while True:
                new_matched_coords = check_matches(board)
                if not new_matched_coords:
                    break
                pause_and_clear_matches(new_matched_coords)
                board, _ = remove_matches(board, new_matched_coords)

        draw_board(board)
        clock.tick(FPS)

if __name__ == "__main__":
    main()
