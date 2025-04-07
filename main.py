"""
main.py

Entry point for running the Lazor puzzle solver.

Usage:
    python main.py <path_to_bff_file>

This script:
  - Parses the .bff puzzle file.
  - Initializes logging.
  - Solves the board using a backtracking search.
  - Outputs the solution as a visual and text file if successful.
"""

import sys
import os
import datetime
import logging
import time
from parser_bff import parse_bff_file
from board import Board
from solver import solve
from visualization import visualize_board
from visualization_image import save_laser_image


def main():
    """
    Main function to run the Lazor solver. Handles:
        - Parsing .bff input
        - Logging setup
        - Board initialization
        - Backtracking solver execution
        - Outputting solution files and visualizations
    """
    # Ensure a .bff file is passed as an argument.
    if len(sys.argv) < 2:
        print("Usage: python main.py <bff_file>")
        sys.exit(1)

    bff_file = sys.argv[1]
    data = parse_bff_file(bff_file)

    # Create log and output directories if missing
    os.makedirs("logs", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    bff_basename = os.path.basename(bff_file)
    bff_name, _ = os.path.splitext(bff_basename)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Setup logging
    log_filename = f"logs/solver_debug_{bff_name}_{timestamp}.log"
    logging.basicConfig(
        filename=log_filename,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info("Started solver for file: %s", bff_file)

    # Visual logger (separate for board visual steps)
    visual_log_filename = f"logs/solver_visual_{bff_name}_{timestamp}.log"
    visual_logger = logging.getLogger("visual")
    visual_logger.propagate = False
    visual_logger.setLevel(logging.DEBUG)
    visual_handler = logging.FileHandler(visual_log_filename)
    visual_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    visual_logger.addHandler(visual_handler)
    logging.info("Visual logger initialized with file: %s",
                 visual_log_filename)

    # Reduce clutter from matplotlib font warnings
    logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)

    # Initialize the board
    board = Board(data)

    # Solve the puzzle
    start_time = time.perf_counter()
    solution = solve(board)
    elapsed_time = time.perf_counter() - start_time
    logging.info("Solver finished in %.4f seconds", elapsed_time)

    # Output solution if found
    if solution is not None:
        print("Solution found!")

        # Save text representation of the solution
        with open(f"output/solution_{bff_name}.txt", "w") as f:
            f.write(str(solution))

        # Generate and print visual text-based board
        visual = visualize_board(board)
        print(visual)
        with open(f"output/solution_visual_{bff_name}.txt", "w") as f:
            f.write(visual)

        # Save laser path visualization image
        image_filename = f"output/solution_visual_{bff_name}.png"
        save_laser_image(board, solution, image_filename)
        print(f"Solution saved to {image_filename}")
    else:
        print("No solution found.")

    # Always show how long the solver took
    print(f"Solver finished in {elapsed_time:.4f} seconds")


if __name__ == "__main__":
    main()
