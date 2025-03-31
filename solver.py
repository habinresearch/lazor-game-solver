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
    Returns a list of free block placements (their original positions and types) or None.
    """
    targets = set(board.points)
    # Create free blocks list from board.blocks_available.
    free_blocks = []
    free_blocks += [ReflectBlock() for _ in range(board.blocks_available.get("A", 0))]
    free_blocks += [OpaqueBlock() for _ in range(board.blocks_available.get("B", 0))]
    free_blocks += [RefractBlock() for _ in range(board.blocks_available.get("C", 0))]

    # Candidate positions are those stored in board.free_positions.
    positions = board.free_positions

    def backtrack(i, pos_index):
        logging.debug(
            "Backtracking: free block index = %d, candidate pos index = %d",
            i,
            pos_index,
        )
        log_board_state(board, f"After {i} placements, candidate index {pos_index}")

        if i == len(free_blocks):
            logging.debug("All free blocks placed; checking solution.")
            if test_solution(board, targets):
                sol = [
                    (block.orig_pos, type(block).__name__)
                    for block in board.free_blocks_placed
                ]
                logging.info("Solution found: %s", sol)
                log_board_state(board, "Final solution board state")
                return sol
            else:
                logging.debug("Solution check failed with current full placement.")
            return None

        if pos_index >= len(positions):
            logging.debug("No more candidate positions for free block index = %d.", i)
            return None

        # Option 1: Skip the current candidate position.
        result = backtrack(i, pos_index + 1)
        if result is not None:
            return result

        # Option 2: Try placing a free block at positions[pos_index].
        i_pos, j_pos = positions[pos_index]
        if board.is_placeable(i_pos, j_pos):
            block = free_blocks[i]
            board.place_free_block(i_pos, j_pos, block)
            logging.debug(
                "Placed %s at original cell (%d, %d)",
                type(block).__name__,
                i_pos,
                j_pos,
            )
            log_board_state(board, f"After placing free block {i} at ({i_pos},{j_pos})")
            result = backtrack(i + 1, pos_index + 1)
            if result is not None:
                return result
            board.remove_free_block(i_pos, j_pos)
            logging.debug(
                "Removed %s from original cell (%d, %d) during backtracking",
                type(block).__name__,
                i_pos,
                j_pos,
            )
            log_board_state(
                board, f"After removing free block {i} from ({i_pos},{j_pos})"
            )
        return None

    return backtrack(0, 0)


def test_solution(board, targets):
    """
    Simulate laser paths on the simulation board.
    For each beam, check if its next position lies within any placed block's boundaries.
    Uses a beam queue; if a collision is detected, the block's interact() is used to compute the new direction.
    Returns True if all targets are hit; otherwise, False.
    """
    remaining_targets = set(targets)
    max_steps = 200

    blocks = board.get_placed_blocks()
    beam_queue = []
    for lx, ly, vx, vy in board.lasers:
        beam_queue.append((lx, ly, lx, ly, vx, vy, 0))
        logging.debug(
            "Starting beam from (%d, %d) with direction (%d, %d)", lx, ly, vx, vy
        )

    while beam_queue:
        sx, sy, x, y, dx, dy, steps = beam_queue.pop(0)
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
            0 <= next_x < board.orig_width * 2 + 1
            and 0 <= next_y < board.orig_height * 2 + 1
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
                (dx, dy), (sx, sy), (next_x, next_y)
            )
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
                    beam_queue.append(
                        (sx, sy, next_x, next_y, new_dx, new_dy, steps + 1)
                    )
        else:
            beam_queue.append((sx, sy, next_x, next_y, dx, dy, steps + 1))
    return len(remaining_targets) == 0
