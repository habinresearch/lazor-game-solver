from blocks import ReflectBlock, OpaqueBlock, RefractBlock
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def find_lazor_endpoint(lazor_grid, x, y, vx, vy, grid_size_x, grid_size_y):
    """
    Trace a lazor's path until it exits the grid or interacts with a block.

    Args:
        lazor_grid (Board): The current board configuration.
        x, y (int): Starting coordinates of the lazor.
        vx, vy (int): Lazor direction vector.
        grid_size_x (int): Width of the lazor grid.
        grid_size_y (int): Height of the lazor grid.

    Returns:
        tuple: (end_x, end_y, [list of new direction vectors])
    """
    is_first_turn = True
    new_directions = []  # Default: no new directions

    while (0 <= x <= grid_size_x and 0 <= y <= grid_size_y) or is_first_turn:
        x += vx
        y += vy
        found_collision = False

        blocks = lazor_grid.get_placed_blocks()
        for block in blocks:
            if block.within_boundaries(x, y):
                # Get new beam directions from block's interaction.
                new_directions = block.interact((vx, vy), (x, y))
                if new_directions:
                    # Ensure we have a list of direction vectors.
                    if isinstance(new_directions[0], (list, tuple)):
                        new_directions = [
                            list(direction) for direction in new_directions
                        ]
                    else:
                        new_directions = [list(new_directions)]
                found_collision = True
                break  # Stop at the first collision

        if found_collision:
            # Only return new directions if still within bounds
            if 0 <= x <= grid_size_x and 0 <= y <= grid_size_y:
                return x, y, new_directions
            else:
                # Beam already out-of-bound; do not propagate further.
                return x, y, []

        if is_first_turn:
            is_first_turn = False

    # If while loop ended (i.e., beam went out-of-bound with no collision),
    # return no new directions.
    return x, y, []


def save_laser_image(lazor_grid, solution=None, filename=None):
    """
    Save a visualization of the Lazor grid, showing blocks, lasers, and target points.

    Args:
        lazor_grid (Board): Board instance with grid, lasers, and blocks.
        solution (list): Optional list of tuples (position, block_type_name) representing placed blocks.
        filename (str): Output file path for saving the image.
    """
    grid = lazor_grid.orig_grid
    x_size_grid = len(grid) * 2
    y_size_grid = len(grid[0]) * 2

    fig, ax = plt.subplots()
    ax.set_xlim(-1, y_size_grid + 1)
    ax.set_ylim(-1, x_size_grid + 1)

    # Add black border around the grid
    ax.add_patch(Rectangle((-1, -1), 1, x_size_grid + 3, color="slategrey"))
    ax.add_patch(Rectangle((y_size_grid, -1), 1, x_size_grid + 3, color="slategrey"))
    ax.add_patch(Rectangle((-1, -1), y_size_grid + 3, 1, color="slategrey"))
    ax.add_patch(Rectangle((-1, x_size_grid), y_size_grid + 3, 1, color="slategrey"))

    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Map block class names to display characters if applying a solution.
    block_type_dict = {"ReflectBlock": "A", "OpaqueBlock": "B", "RefractBlock": "C"}

    if solution is not None:
        for (x, y), block_type in solution:
            grid[x][y] = block_type_dict.get(block_type, "?")

    # Draw the grid: fill squares (if they are not marked as 'o')
    square_size = 2
    for x, row in enumerate(grid):
        for y, col in enumerate(row):
            if col == "o":
                continue
            x_pos = x * 2 + 1
            y_pos = y * 2 + 1
            color = {"x": "slategrey", "A": "green", "B": "black", "C": "blue"}.get(
                col, "white"
            )  # Default to white if unknown
            square = plt.Rectangle(
                (y_pos - square_size / 2, x_pos - square_size / 2),
                square_size,
                square_size,
                color=color,
            )
            ax.add_patch(square)

    # Draw grid lines
    for i in range(0, x_size_grid + 1, 2):
        ax.plot([0, y_size_grid], [i, i], color="black", linewidth=1)
    for i in range(0, y_size_grid + 1, 2):
        ax.plot([i, i], [0, x_size_grid], color="black", linewidth=1)

    # Draw target points
    for px, py in lazor_grid.points:
        circle = plt.Circle((px, py), 0.2, color="black")
        ax.add_patch(circle)

    # Initialize beams with a step counter.
    # Each beam is a tuple: (x, y, vx, vy, steps)
    lazors = [(lx, ly, vx, vy, 0) for lx, ly, vx, vy in lazor_grid.lasers.copy()]

    while lazors:
        x, y, vx, vy, steps = lazors.pop()

        # --- Special handling for beams at their initial position ---
        if steps == 0:
            epsilon = (
                0.1  # small offset to check immediately ahead of the starting position
            )
            init_x = x + epsilon * vx
            init_y = y + epsilon * vy

            collided_block = None
            blocks = lazor_grid.get_placed_blocks()
            for block in blocks:
                if block.within_boundaries(init_x, init_y):
                    collided_block = block
                    break

            if collided_block is not None:
                new_directions = collided_block.interact((vx, vy), (x, y))
                # If the block redirects the beam, queue up the new beams.
                if new_directions:
                    if isinstance(new_directions[0], (list, tuple)):
                        new_dirs_list = [
                            list(direction) for direction in new_directions
                        ]
                    else:
                        new_dirs_list = [list(new_directions)]
                    for new_dir in new_dirs_list:
                        lazors.append((x, y, new_dir[0], new_dir[1], steps + 1))
                # Skip normal propagation for this beam.
                continue
        # --- End of special handling ---

        # Propagate the beam normally using find_lazor_endpoint.
        end_x, end_y, new_dirs = find_lazor_endpoint(
            lazor_grid, x, y, vx, vy, x_size_grid, y_size_grid
        )

        # Draw the beam segment from (x, y) to (end_x, end_y)
        ax.arrow(
            x,
            y,
            end_x - x,
            end_y - y,
            head_width=0.2,
            head_length=0.2,
            fc="red",
            ec="red",
        )

        # If the beam remains within bounds and produces new directions, queue them.
        if 0 <= end_x <= x_size_grid and 0 <= end_y <= y_size_grid:
            if new_dirs:
                if isinstance(new_dirs[0], (list, tuple)):
                    new_dirs_list = [list(direction) for direction in new_dirs]
                else:
                    new_dirs_list = [list(new_dirs)]
                for new_dir in new_dirs_list:
                    lazors.append((end_x, end_y, new_dir[0], new_dir[1], steps + 1))

    ax.axis("off")
    ax.set_aspect("equal")
    plt.gca().invert_yaxis()
    plt.savefig(filename, bbox_inches="tight")
    plt.close()
