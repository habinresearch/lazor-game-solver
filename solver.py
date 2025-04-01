# solver.py

import logging
from blocks import ReflectBlock, OpaqueBlock, RefractBlock
from visualization import visualize_board


def log_board_state(board, message="Current board state"):
    state = visualize_board(board)
    logging.debug("%s:\n%s", message, state)


def solve(board):
    """
    Use backtracking to place free blocks into candidate positions until a solution is found.
    This version accounts for permutations by trying each available free block type at every
    candidate position.
    Returns a list of free block placements (their original positions and types) or None.
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
        # If no free blocks remain, check if the board is a solution.
        if all(count == 0 for count in free_counts.values()):
            if test_solution(board, targets):
                sol = [
                    (block.orig_pos, type(block).__name__)
                    for block in board.free_blocks_placed
                ]
                return sol
            else:
                return None

        # If we've exhausted positions, backtrack.
        if pos_index >= len(positions):
            return None

        # Option 1: Skip the current candidate position.
        result = backtrack(pos_index + 1, free_counts)
        if result is not None:
            return result

        # Option 2: Try placing each type of free block at the current position (if available).
        i, j = positions[pos_index]
        if board.is_placeable(i, j):
            for block_type in ["A", "B", "C"]:
                if free_counts.get(block_type, 0) > 0:
                    # Instantiate the block based on type.
                    if block_type == "A":
                        block = ReflectBlock()
                    elif block_type == "B":
                        block = OpaqueBlock()
                    elif block_type == "C":
                        block = RefractBlock()

                    # Place the block and decrement its count.
                    board.place_free_block(i, j, block)
                    free_counts[block_type] -= 1

                    result = backtrack(pos_index + 1, free_counts)
                    if result is not None:
                        return result

                    # Backtrack: remove the block and restore its count.
                    board.remove_free_block(i, j)
                    free_counts[block_type] += 1

        return None

    return backtrack(0, free_blocks_counts.copy())


def test_solution(board, targets):
    """
    Simulate laser paths on a cloned board so that mutable block states (e.g. in RefractBlock)
    do not persist across simulation runs. Returns True if all targets are hit; otherwise, False.
    """
    # Create a fresh copy of the board for the simulation.
    board_copy = board.clone()

    # Log the visual board from the cloned board.
    visual_logger = logging.getLogger("visual")
    visual_board = visualize_board(board_copy)
    visual_logger.debug("Visual board at start of test_solution:\n%s", visual_board)

    remaining_targets = set(targets)
    max_steps = 200

    blocks = board_copy.get_placed_blocks()
    beam_queue = []
    for lx, ly, vx, vy in board_copy.lasers:
        beam_queue.append((lx, ly, vx, vy, 0))
        logging.debug(
            "Starting beam from (%d, %d) with direction (%d, %d)", lx, ly, vx, vy
        )

    while beam_queue:
        x, y, dx, dy, steps = beam_queue.pop(0)
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
        logging.debug("Beam step %d: moving to (%d, %d)", steps + 1, next_x, next_y)

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
            new_directions = collided_block.interact((dx, dy), (next_x, next_y))
            if not new_directions:
                logging.debug("Beam stopped by block at (%d, %d)", next_x, next_y)
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
                    beam_queue.append((next_x, next_y, new_dx, new_dy, steps + 1))
        else:
            beam_queue.append((next_x, next_y, dx, dy, steps + 1))
    return len(remaining_targets) == 0
