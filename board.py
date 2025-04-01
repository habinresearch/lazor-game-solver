# board.py

from blocks import ReflectBlock, OpaqueBlock, RefractBlock
import copy


class Board:
    def __init__(self, data):
        """
        data: dictionary with keys:
          - "grid": 2D list of characters (e.g. "x", "o", "A", "B", "C")
          - "blocks_available": dictionary of counts for free blocks.
          - "lasers": list of (x, y, vx, vy) in simulation coordinates.
          - "points": list of (x, y) target coordinates.
        """
        self.orig_grid = data["grid"]
        self.blocks_available = data["blocks_available"]
        self.lasers = data["lasers"]
        self.points = data["points"]

        self.orig_height = len(self.orig_grid)
        self.orig_width = len(self.orig_grid[0]) if self.orig_height > 0 else 0

        # Build fixed blocks.
        self.fixed_blocks = []
        for i in range(self.orig_height):
            for j in range(self.orig_width):
                cell = self.orig_grid[i][j]
                if cell in ["A", "B", "C"]:
                    top = 2 * i
                    left = 2 * j
                    bottom = top + 2
                    right = left + 2
                    if cell == "A":
                        block = ReflectBlock(fixed=True)
                    elif cell == "B":
                        block = OpaqueBlock(fixed=True)
                    elif cell == "C":
                        block = RefractBlock(fixed=True)
                    block.set_boundaries(top, left, bottom, right)
                    # Also store the original grid position.
                    block.orig_pos = (i, j)
                    self.fixed_blocks.append(block)

        # Candidate free positions: any cell that is not "x".
        self.free_positions = []
        for i in range(self.orig_height):
            for j in range(self.orig_width):
                if self.orig_grid[i][j] not in ["x", "A", "B", "C"]:
                    self.free_positions.append((i, j))

        # Free blocks placed during solving.
        self.free_blocks_placed = []

    def get_placed_blocks(self):
        """Return all placed blocks (fixed and free)."""
        return self.fixed_blocks + self.free_blocks_placed

    def is_placeable(self, i, j):
        """Return True if no free block is already placed at original cell (i, j)."""
        for block in self.free_blocks_placed:
            if block.orig_pos == (i, j):
                return False
        return True

    def place_free_block(self, i, j, block):
        """Place a free block at original cell (i, j) by computing its boundaries."""
        top = 2 * i
        left = 2 * j
        bottom = top + 2
        right = left + 2
        block.set_boundaries(top, left, bottom, right)
        block.orig_pos = (i, j)
        self.free_blocks_placed.append(block)

    def remove_free_block(self, i, j):
        """Remove the free block placed at original cell (i, j)."""
        for idx, block in enumerate(self.free_blocks_placed):
            if block.orig_pos == (i, j):
                del self.free_blocks_placed[idx]
                return

    def clone(self):
        """
        Create and return a deep copy of the board, ensuring that mutable state
        (like block states) is completely independent.
        """
        return copy.deepcopy(self)
