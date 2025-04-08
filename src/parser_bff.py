def parse_bff_file(filename):
    """
    Parse a .bff file and extract the game setup.

    Args:
        filename (str): Path to the .bff file.

    Returns:
        dict: A dictionary containing:
            - grid (list of list of str): 2D grid layout with elements like 'o', 'x', 'A', 'B', 'C'
            - blocks_available (dict): Available free blocks, keys are 'A', 'B', 'C', values are int counts
            - lasers (list of tuples): List of lasers, each as (x, y, dx, dy)
            - points (list of tuples): Target points, each as (x, y)
    """
    grid = []
    blocks_available = {'A': 0, 'B': 0, 'C': 0}
    lasers = []
    points = []

    # Read and clean lines (ignore comments and blank lines)
    with open(filename, 'r') as f:
        lines = [
            line.strip()
            for line in f
            if not line.strip().startswith('#') and line.strip() != ''
        ]

    reading_grid = False  # Flag for when we're reading grid rows

    for line in lines:
        # Start and stop of grid section
        if line.upper().startswith("GRID START"):
            reading_grid = True
            continue
        if line.upper().startswith("GRID STOP"):
            reading_grid = False
            continue

        # Reading the grid layout
        if reading_grid:
            row = line.split()  # e.g., ['o', 'o', 'o', 'A']
            grid.append(row)
            continue

        # Parse block counts, lasers, and target points
        parts = line.split()

        # Free block declaration, e.g., "A 2"
        if parts[0] in ['A', 'B', 'C'] and len(parts) == 2:
            block_type = parts[0]
            count = int(parts[1])
            blocks_available[block_type] = count

        # Laser line, e.g., "L 2 7 1 -1"
        elif parts[0] == 'L' and len(parts) == 5:
            x, y, vx, vy = map(int, parts[1:])
            lasers.append((x, y, vx, vy))

        # Point line, e.g., "P 3 0"
        elif parts[0] == 'P' and len(parts) == 3:
            x, y = map(int, parts[1:])
            points.append((x, y))

    return {
        'grid': grid,
        'blocks_available': blocks_available,
        'lasers': lasers,
        'points': points
    }
