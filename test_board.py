# test_board.py
import logging
from board import Board
from solver import test_solution
from visualization import visualize_board

# Set up logging (if not already configured in main.py)
logging.basicConfig(
    filename="logs/test_board.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Create a custom board data dictionary.
# (You can adjust the grid, block counts, lasers, and points as needed.)
data = {
    "grid": [
        ["o", "o", "o", "o"],
        ["o", "o", "o", "o"],
        ["o", "o", "o", "o"],
        ["o", "o", "o", "o"],
    ],
    "blocks_available": {"A": 2, "B": 0, "C": 1},
    "lasers": [(2, 7, 1, -1)],  # x, y, vx, vy (example values)
    "points": [(3, 0), (4, 3), (2, 5), (4, 7)],
}

# Create the board.
board = Board(data)

# (Optional) Manually place fixed blocks or free blocks if you wish.
# For example, to place a free ReflectBlock at cell (1,1):
from blocks import ReflectBlock, RefractBlock

board.place_free_block(2, 0, ReflectBlock())
board.place_free_block(1, 3, ReflectBlock())
board.place_free_block(0, 2, RefractBlock())

# Visualize the board (prints a text version and logs it).
print("Initial board:")
print(visualize_board(board))

# Run test_solution to see if the board (with current placements) is a solution.
result = test_solution(board, board.points)
print("Test solution result:", result)
