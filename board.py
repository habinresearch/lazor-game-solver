from blocks import ReflectBlock, OpaqueBlock, RefractBlock
import copy


class Board:
    """
    Represents the Lazor game board, including fixed and placeable blocks, lasers, and target points.
    """
    def __init__(self, data):
        """
        Initialize the board using the provided configuration.

        Args:
            data (dict): Dictionary with keys:
                - "grid": 2D list of characters (e.g., "x", "o", "A", "B", "C").
                - "blocks_available": dict of available blocks by type.
                - "lasers": list of tuples (x, y, dx, dy) for initial lazor positions and directions.
                - "points": list of target (x, y) coordinates to hit.
        """
        self.orig_grid = data["grid"]
        self.blocks_available = data["blocks_available"]
        self.lasers = data["lasers"]
        self.points = data["points"]

        self.orig_height = len(self.orig_grid)
        self.orig_width = len(self.orig_grid[0]) if self.orig_height > 0 else 0

        # Fixed blocks on the board, determined from "A", "B", "C" in the grid.
        self.fixed_blocks = []
        for i in range(self.orig_height):
            for j in range(self.orig_width):
                cell = self.orig_grid[i][j]
                if cell in ["A", "B", "C"]:
                    top = 2 * i
                    left = 2 * j
                    bottom = top + 2
                    right = left + 2

                    # Instantiate the correct block type.
                    if cell == "A":
                        block = ReflectBlock(fixed=True)
                    elif cell == "B":
                        block = OpaqueBlock(fixed=True)
                    elif cell == "C":
                        block = RefractBlock(fixed=True)

                    block.set_boundaries(top, left, bottom, right)
                    block.orig_pos = (i, j)
                    self.fixed_blocks.append(block)

        # Free positions are all grid cells that are not marked as "x", "A", "B", or "C".
        self.free_positions = []
        for i in range(self.orig_height):
            for j in range(self.orig_width):
                if self.orig_grid[i][j] not in ["x", "A", "B", "C"]:
                    self.free_positions.append((i, j))

        # Tracks free blocks that are dynamically placed during solving.
        self.free_blocks_placed = []

    def get_placed_blocks(self):
        """
        Return a combined list of all currently placed blocks.

        Returns:
            list: All blocks, both fixed and free.
        """
        return self.fixed_blocks + self.free_blocks_placed

    def is_placeable(self, i, j):
        """
        Check if a free block can be placed at grid location (i, j).

        Args:
            i (int): Row index in the grid.
            j (int): Column index in the grid.

        Returns:
            bool: True if the position is valid for placing a free block.
        """
        # Cannot place on invalid cell or where a block is already placed.
        if self.orig_grid[i][j] == "x":
            return False
        for block in self.free_blocks_placed:
            if block.orig_pos == (i, j):
                return False
        return True

    def place_free_block(self, i, j, block):
        """
        Place a free block at grid cell (i, j).

        Args:
            i (int): Row index in the grid.
            j (int): Column index in the grid.
            block (Block): The block object to place.
        """
        top = 2 * i
        left = 2 * j
        bottom = top + 2
        right = left + 2
        block.set_boundaries(top, left, bottom, right)
        block.orig_pos = (i, j)
        self.free_blocks_placed.append(block)

    def remove_free_block(self, i, j):
        """
        Remove the free block placed at grid cell (i, j), if any.

        Args:
            i (int): Row index in the grid.
            j (int): Column index in the grid.
        """
        for idx, block in enumerate(self.free_blocks_placed):
            if block.orig_pos == (i, j):
                del self.free_blocks_placed[idx]
                return

    def clone(self):
        """
        Create a deep copy of the board, useful for exploring new configurations during solving.

        Returns:
            Board: A new, independent copy of this board instance.
        """
        return copy.deepcopy(self)
