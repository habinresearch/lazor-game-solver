"""
parser_bff.py

Functions for reading and parsing .bff files for the Lazors game.
"""

def parse_bff_file(filename):
    """
    Reads the .bff file and returns a dictionary containing:
      - grid: 2D list of 'o', 'x', 'A', 'B', 'C' (or something similar)
      - blocks_available: dict with keys 'A', 'B', 'C' and integer counts
      - lasers: list of (x, y, vx, vy)
      - points: list of (x, y)
    """
    grid = []
    blocks_available = {'A': 0, 'B': 0, 'C': 0}
    lasers = []
    points = []
    
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if not line.strip().startswith('#') and line.strip() != '']
    
    # State machine approach to parse sections
    reading_grid = False
    for line in lines:
        if line.upper().startswith("GRID START"):
            reading_grid = True
            continue
        if line.upper().startswith("GRID STOP"):
            reading_grid = False
            continue
        
        if reading_grid:
            # e.g. "o o o o"
            row = line.split()
            grid.append(row)
            continue
        
        # If not reading grid, look for blocks, lasers, points
        parts = line.split()
        
        # e.g. "A 2" means 2 reflect blocks
        if parts[0] in ['A', 'B', 'C'] and len(parts) == 2:
            block_type = parts[0]
            count = int(parts[1])
            blocks_available[block_type] = count
        
        # e.g. "L 2 7 1 -1" means a laser
        elif parts[0] == 'L' and len(parts) == 5:
            # L x y vx vy
            x, y, vx, vy = map(int, parts[1:])
            lasers.append((x, y, vx, vy))
        
        # e.g. "P 3 0" means a point
        elif parts[0] == 'P' and len(parts) == 3:
            x, y = map(int, parts[1:])
            points.append((x, y))
    
    return {
        'grid': grid,
        'blocks_available': blocks_available,
        'lasers': lasers,
        'points': points
    }
