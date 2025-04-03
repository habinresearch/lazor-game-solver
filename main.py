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
    # Ensure proper usage.
    if len(sys.argv) < 2:
        print("Usage: python main.py <bff_file>")
        sys.exit(1)

    bff_file = sys.argv[1]
    data = parse_bff_file(bff_file)

    # Create logs and output directories if they don't exist.
    if not os.path.exists("logs"):
        os.makedirs("logs")
    if not os.path.exists("output"):
        os.makedirs("output")

    bff_basename = os.path.basename(bff_file)
    bff_name, _ = os.path.splitext(bff_basename)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    log_filename = f"logs/solver_debug_{bff_name}_{timestamp}.log"
    logging.basicConfig(
        filename=log_filename,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info("Started solver for file: %s", bff_file)

    visual_log_filename = f"logs/solver_visual_{bff_name}_{timestamp}.log"
    visual_logger = logging.getLogger("visual")
    visual_logger.propagate = False
    visual_logger.setLevel(logging.DEBUG)
    visual_handler = logging.FileHandler(visual_log_filename)
    visual_formatter = logging.Formatter("%(asctime)s - %(message)s")
    visual_handler.setFormatter(visual_formatter)
    visual_logger.addHandler(visual_handler)
    logging.info("Visual logger initialized with file: %s", visual_log_filename)

    board = Board(data)

    # Optionally, reduce Matplotlib's font manager logging to avoid 'findfont' messages.
    logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)

    # Time the solver.
    start_time = time.perf_counter()
    solution = solve(board)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    logging.info("Solver finished in %.4f seconds", elapsed_time)

    if solution is not None:
        print("Solution found!")
        with open(f"output/solution_{bff_name}_{timestamp}.txt", "w") as f:
            f.write(str(solution))
        visual = visualize_board(board)
        print(visual)
        with open(f"output/solution_visual_{bff_name}_{timestamp}.txt", "w") as f:
            f.write(visual)
        image_filename = f"output/solution_visual_{bff_name}_{timestamp}.png"
        save_laser_image(board, solution, image_filename)
        print(f"Solution saved to {image_filename}")
    else:
        print("No solution found.")

    print(f"Solver finished in {elapsed_time:.4f} seconds")  # Print to console.


if __name__ == "__main__":
    main()
