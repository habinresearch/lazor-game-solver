"""
visualization.py

Functions for visualizing the board
"""

from blocks import ReflectBlock, OpaqueBlock, RefractBlock


def visualize_board(board):
    """
    Create a text representation of the board.
    For each cell in the original grid:
      - 'x' if the cell is disallowed.
      - Otherwise, show the block letter if a free block is placed at that cell;
        otherwise 'o'.
      (Fixed blocks could also be visualized similarly if you choose to store their original positions.)
    """
    lines = []
    for i in range(board.orig_height):
        row = []
        for j in range(board.orig_width):
            if board.orig_grid[i][j] == "x":
                row.append("x")
            else:
                found = None
                # Check free blocks.
                for block in board.free_blocks_placed:
                    if block.orig_pos == (i, j):
                        found = block
                        break
                # Check fixed blocks.
                if not found:
                    for block in board.fixed_blocks:
                        if block.orig_pos == (i, j):
                            found = block
                            break
                if found:
                    if isinstance(found, ReflectBlock):
                        row.append("A")
                    elif isinstance(found, OpaqueBlock):
                        row.append("B")
                    elif isinstance(found, RefractBlock):
                        row.append("C")
                    else:
                        row.append("?")
                else:
                    row.append("o")
        lines.append("   ".join(row))
    return "\n".join(lines)
