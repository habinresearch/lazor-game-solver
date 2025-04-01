from blocks import ReflectBlock, OpaqueBlock, RefractBlock
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def find_lazor_endpoint(lazor_grid, x, y, vx, vy, grid_size_x, grid_size_y):
    # while in bounds
    is_first_turn = True
    # print(f'grid_size_x: {grid_size_x}, grid_size_y: {grid_size_y}')
    while (0 < x < grid_size_x and 0 < y < grid_size_y) or is_first_turn:
        # move lazor
        # print(f'before: x: {x}, y: {y}')
        x += vx
        y += vy

        found_collision = False

        blocks = lazor_grid.get_placed_blocks()
        for block in blocks:
            if block.within_boundaries(x, y):
                collided_block = block
                if collided_block is not None:
                    new_directions = collided_block.interact((vx, vy), (x, y))
                    # format new_directions
                    if new_directions:  # if not opaque block, reformat it
                        new_directions = list(new_directions[0])
                    found_collision = True
                    break  # only care about first possible collision
        if found_collision:
            # print('hi', x, y, new_directions)
            if 0 < x < grid_size_x and 0 < y < grid_size_y:
                return x, y, new_directions
        # print(f'after: x: {x}, y: {y}')
        if is_first_turn:
            is_first_turn = False

    directions = [vx, vy]
    return x, y, directions


def save_laser_image(lazor_grid, solution=None, filename=None):
    grid = lazor_grid.orig_grid

    x_size_grid = len(grid) * 2
    y_size_grid = len(grid[0]) * 2

    fig, ax = plt.subplots()

    # make grid a little wider so we can see the points
    ax.set_xlim(-1, y_size_grid + 1)
    ax.set_ylim(-1, x_size_grid + 1)

    # make the borders black like the X blocks are
    ax.add_patch(Rectangle((-1, -1), 1, x_size_grid + 3, color="black"))
    ax.add_patch(Rectangle((y_size_grid, -1), 1, x_size_grid + 3, color="black"))
    ax.add_patch(Rectangle((-1, -1), y_size_grid + 3, 1, color="black"))
    ax.add_patch(Rectangle((-1, x_size_grid), y_size_grid + 3, 1, color="black"))

    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # place blocks on grid
    block_type_dict = {"ReflectBlock": "A", "OpaqueBlock": "B", "RefractBlock": "C"}

    if solution is not None:
        for block in solution:
            x, y = block[0]
            block_type = block[1]
            grid[x][y] = block_type_dict[block_type]

    square_size = 2
    for x, row in enumerate(grid):
        for y, col in enumerate(row):
            # place blocks on plot
            block_type = grid[x][y]
            if block_type == "o":
                continue
            x_pos = x * 2 + 1
            y_pos = y * 2 + 1

            if block_type == "x":
                square = plt.Rectangle(
                    (y_pos - square_size / 2, x_pos - square_size / 2),
                    square_size,
                    square_size,
                    color="black",
                )
                ax.add_patch(square)

            elif block_type == "A":
                square = plt.Rectangle(
                    (y_pos - square_size / 2, x_pos - square_size / 2),
                    square_size,
                    square_size,
                    color="green",
                )
                ax.add_patch(square)

            elif block_type == "B":
                square = plt.Rectangle(
                    (y_pos - square_size / 2, x_pos - square_size / 2),
                    square_size,
                    square_size,
                    color="grey",
                )
                ax.add_patch(square)

            elif block_type == "C":
                square = plt.Rectangle(
                    (y_pos - square_size / 2, x_pos - square_size / 2),
                    square_size,
                    square_size,
                    color="red",
                )
                ax.add_patch(square)

    # draw horizontal lines
    for i in range(0, x_size_grid + 1, 2):
        ax.plot([0, y_size_grid], [i, i], color="black", linewidth=1)

    # draw vertical lines
    for i in range(0, y_size_grid + 1, 2):
        ax.plot([i, i], [0, x_size_grid], color="black", linewidth=1)

    # plot points
    points = lazor_grid.points
    for point in points:
        px, py = point
        circle = plt.Circle((px, py), 0.2, color="black")
        ax.add_patch(circle)

    # draw lazors
    lazors = lazor_grid.lasers
    while lazors:
        lazor = lazors.pop()
        start_x = lazor[0]
        start_y = lazor[1]
        vx = lazor[2]
        vy = lazor[3]

        end_x, end_y, directions = find_lazor_endpoint(
            lazor_grid, start_x, start_y, vx, vy, x_size_grid, y_size_grid
        )

        if directions and directions != [vx, vy]:  # if it bounced
            lazors.append([end_x, end_y, directions[0], directions[1]])

        # get length of lazor in x and y dir
        lazor_length_x = end_x - start_x
        lazor_length_y = end_y - start_y

        ax.arrow(
            start_x,
            start_y,
            lazor_length_x,
            lazor_length_y,
            head_width=0.2,
            head_length=0.2,
            fc="red",
            ec="red",
        )

    ax.axis("off")
    ax.set_aspect("equal")
    plt.gca().invert_yaxis()
    plt.savefig(filename, bbox_inches="tight")
    plt.close()
