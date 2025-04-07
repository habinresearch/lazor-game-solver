from blocks import ReflectBlock, OpaqueBlock, RefractBlock


def visualize_board(board):
    """
    Generate a string-based visualization of the board.

    This function renders a simplified view of the game board where:
        - 'x' represents disallowed positions.
        - 'o' represents an empty, placeable cell.
        - 'A', 'B', 'C' represent Reflect, Opaque, and Refract blocks, respectively.
          These include both fixed and placed blocks.

    Args:
        board (Board): The game board to visualize.

    Returns:
        str: A multi-line string representing the board layout.
    """
    lines = []
    for i in range(board.orig_height):
        row = []
        for j in range(board.orig_width):
            if board.orig_grid[i][j] == "x":
                row.append("x")
            else:
                found = None

                # First check if a free block is placed at this position
                for block in board.free_blocks_placed:
                    if block.orig_pos == (i, j):
                        found = block
                        break

                # Then check if a fixed block exists at this position
                if not found:
                    for block in board.fixed_blocks:
                        if block.orig_pos == (i, j):
                            found = block
                            break

                # Determine the character to display
                if found:
                    if isinstance(found, ReflectBlock):
                        row.append("A")
                    elif isinstance(found, OpaqueBlock):
                        row.append("B")
                    elif isinstance(found, RefractBlock):
                        row.append("C")
                    else:
                        row.append("?")  # Unknown block type
                else:
                    row.append("o")  # Empty placeable cell
        lines.append("   ".join(row))
    return "\n".join(lines)
