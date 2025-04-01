#!/usr/bin/env python3
"""
main.py

Main entry point for the Lazors solver.
"""

import sys
import os
import datetime
import logging
from parser_bff import parse_bff_file
from board import Board
from solver import solve
from visualization import visualize_board
from visualization_image import save_laser_image


def main():
    # Ensure proper usage.
    if len(sys.argv) < 2:
        print("Usage: python main.py <bff_file>")
        sys.exit(1)

    bff_file = sys.argv[1]
    data = parse_bff_file(bff_file)

    # Create logs directory if it doesn't exist.
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Extract the bff file name (without path or extension) and timestamp.
    bff_basename = os.path.basename(bff_file)  # e.g., dark_1.bff
    bff_name, _ = os.path.splitext(bff_basename)  # e.g., dark_1
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/solver_debug_{bff_name}_{timestamp}.log"

    # Configure logging here so all modules share this configuration.
    logging.basicConfig(
        filename=log_filename,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info("Started solver for file: %s", bff_file)

    # Initialize board and solve.
    board = Board(data)
    solution = solve(board)

    if solution is not None:
        print("Solution found!")
        with open("output/solution.txt", "w") as f:
            f.write(str(solution))
        #visual = visualize_board(board)

        f = "output/solution_visual.png"
        save_laser_image(board, solution, f)
        print(f'Solution saved to {f}')
        #print(visual)
        #with open("output/solution_visual.txt", "w") as f:
            #f.write(visual)
    else:
        print("No solution found.")


if __name__ == "__main__":
    main()

    
