# solver.py

import logging
from blocks import ReflectBlock, OpaqueBlock, RefractBlock
from visualization import visualize_board


def log_board_state(board, message="Current board state"):
    """
    Logs a visual representation of the current board.

    Args:
        board (Board): The Lazor game board instance.
        message (str): An optional message to prefix the board state.
    """
    state = visualize_board(board)
    logging.debug("%s:\n%s", message, state)


def solve(board):
    """
    Attempt to solve the Lazor game board using recursive backtracking.

    The function attempts all permutations of available block placements into valid
    free positions until a configuration is found such that all targets are hit
    by lazors.

    Args:
        board (Board): The initialized board containing grid, lasers, targets, and block constraints.

    Returns:
        list of tuple or None:
            If a solution is found, returns a list of tuples:
                (position (i, j), block class name as string).
            If no solution is found, returns None.
    """
    targets = set(board.points)

    # Use a counts dictionary for free blocks available by type.
    free_blocks_counts = {
        "A": board.blocks_available.get("A", 0),
        "B": board.blocks_available.get("B", 0),
        "C": board.blocks_available.get("C", 0),
    }

    positions = board.free_positions

    def backtrack(pos_index, free_counts):
        """
        Recursive helper function to try placing blocks and solving the puzzle.

        Args:
            pos_index (int): The current index in the list of candidate positions.
            free_counts (dict): Remaining counts of each block type.

        Returns:
            list of tuple or None: A valid solution or None if backtracking fails.
        """
        # Base case: no free blocks left to place
        if all(count == 0 for count in free_counts.values()):
            if test_solution(board, targets):
                return [
                    (block.orig_pos, type(block).__name__)
                    for block in board.free_blocks_placed
                ]
            return None

        # Base case: all positions exhausted
        if pos_index >= len(positions):
            return None

        # Option 1: skip current position
        result = backtrack(pos_index + 1, free_counts)
        if result is not None:
            return result

        # Option 2: try placing each block type at current position
        i, j = positions[pos_index]
        if board.is_placeable(i, j):
            for block_type in ["A", "B", "C"]:
                if free_counts.get(block_type, 0) > 0:
                    # Instantiate block of the given type
                    if block_type == "A":
                        block = ReflectBlock()
                    elif block_type == "B":
                        block = OpaqueBlock()
                    elif block_type == "C":
                        block = RefractBlock()

                    board.place_free_block(i, j, block)
                    free_counts[block_type] -= 1

                    result = backtrack(pos_index + 1, free_counts)
                    if result is not None:
                        return result

                    # Undo the move (backtrack)
                    board.remove_free_block(i, j)
                    free_counts[block_type] += 1

        return None

    return backtrack(0, free_blocks_counts.copy())


def test_solution(board, targets):
    """
    Test whether a given board configuration causes all lazors to hit the required target points.

    Lazors are simulated step-by-step, interacting with placed blocks. If all targets are hit
    before the lazors exit or reach the step limit, the function returns True.

    Args:
        board (Board): A Lazor game board.
        targets (set of tuple): Set of (x, y) coordinates that lazors must hit.

    Returns:
        bool: True if all targets are hit, False otherwise.
    """
    board_copy = board.clone()
    visual_logger = logging.getLogger("visual")
    visual_board = visualize_board(board_copy)
    visual_logger.debug(
        "Visual board at start of test_solution:\n%s", visual_board)

    remaining_targets = set(targets)
    max_steps = 200  # Limit beam length to prevent infinite loops

    blocks = board_copy.get_placed_blocks()
    beam_queue = []

    # Initialize lazors
    for lx, ly, vx, vy in board_copy.lasers:
        beam_queue.append((lx, ly, vx, vy, 0))
        logging.debug(
            "Starting beam from (%d, %d) with direction (%d, %d)", lx, ly, vx, vy
        )

    while beam_queue:
        x, y, dx, dy, steps = beam_queue.pop(0)

        # Special handling for beams at their initial position.
        if steps == 0:
            epsilon = 0.1  # a small offset
            # Check slightly ahead in the beam's direction
            initial_check_x = x + epsilon * dx
            initial_check_y = y + epsilon * dy

            collided_block = None
            for block in blocks:
                if block.within_boundaries(initial_check_x, initial_check_y):
                    collided_block = block
                    logging.debug(
                        "Initial beam collision at (%.1f, %.1f) with %s at original cell %s",
                        initial_check_x,
                        initial_check_y,
                        type(block).__name__,
                        block.orig_pos,
                    )
                    break
            if collided_block is not None:
                new_directions = collided_block.interact((dx, dy), (x, y))
                if not new_directions:
                    logging.debug(
                        "Beam stopped immediately by block at initial position."
                    )
                    continue  # Beam stops immediately.
                else:
                    for new_dir in new_directions:
                        new_dx, new_dy = new_dir
                        logging.debug(
                            "Initial beam collision produced new beam with direction (%d, %d)",
                            new_dx,
                            new_dy,
                        )
                        beam_queue.append(
                            (
                                x,
                                y,
                                new_dx,
                                new_dy,
                                steps + 1,
                            )
                        )
                # Skip the normal move since we've handled the initial collision.
                continue

        logging.debug(
            "Beam step %d: current position (%d, %d) with direction (%d, %d)",
            steps,
            x,
            y,
            dx,
            dy,
        )
        if steps >= max_steps:
            continue

        next_x = x + dx
        next_y = y + dy
        logging.debug("Beam step %d: moving to (%d, %d)",
                      steps + 1, next_x, next_y)

        if not (
            0 <= next_x < board_copy.orig_width * 2 + 1
            and 0 <= next_y < board_copy.orig_height * 2 + 1
        ):
            logging.debug("Beam left board from (%d, %d)", next_x, next_y)
            continue

        if (next_x, next_y) in remaining_targets:
            logging.debug("Beam hit target at (%d, %d)", next_x, next_y)
            remaining_targets.remove((next_x, next_y))
            if not remaining_targets:
                logging.debug("All targets hit.")
                return True

        collided_block = None
        for block in blocks:
            if block.within_boundaries(next_x, next_y):
                collided_block = block
                logging.debug(
                    "Beam at (%d, %d) collided with %s at original cell %s (boundaries: top=%d, left=%d, bottom=%d, right=%d)",
                    next_x,
                    next_y,
                    type(block).__name__,
                    block.orig_pos,
                    block.top,
                    block.left,
                    block.bottom,
                    block.right,
                )
                break

        if collided_block is not None:
            new_directions = collided_block.interact(
                (dx, dy), (next_x, next_y))
            if not new_directions:
                logging.debug(
                    "Beam stopped by block at (%d, %d)", next_x, next_y)
            else:
                for new_dir in new_directions:
                    new_dx, new_dy = new_dir
                    logging.debug(
                        "At (%d, %d), beam with direction (%d, %d) produced new beam with direction (%d, %d)",
                        next_x,
                        next_y,
                        dx,
                        dy,
                        new_dx,
                        new_dy,
                    )
                    beam_queue.append(
                        (next_x, next_y, new_dx, new_dy, steps + 1))
        else:
            beam_queue.append((next_x, next_y, dx, dy, steps + 1))
    return len(remaining_targets) == 0
