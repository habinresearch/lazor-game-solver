# test_board.py
from blocks import ReflectBlock, RefractBlock
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
        ["o", "B", "o"],
        ["o", "o", "o"],
        ["o", "o", "o"],
    ],
    "blocks_available": {"A": 3, "B": 0, "C": 1},
    "lasers": [(4, 5, -1, -1)],  # x, y, vx, vy (example values)
    "points": [(1, 2), (6, 3)],
}

# Create the board.
board = Board(data)

# (Optional) Manually place fixed blocks or free blocks if you wish.
# For example, to place a free ReflectBlock at cell (1,1):

board.place_free_block(0, 0, ReflectBlock())
board.place_free_block(0, 2, ReflectBlock())
board.place_free_block(2, 0, ReflectBlock())
board.place_free_block(2, 1, RefractBlock())

# Visualize the board (prints a text version and logs it).
print("Initial board:")
print(visualize_board(board))

# Run test_solution to see if the board (with current placements) is a solution.
result = test_solution(board, board.points)
print("Test solution result:", result)
