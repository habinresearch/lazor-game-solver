class Block:
    """
    Base class for all block types in the Lazor game.

    Attributes:
        fixed (bool): Whether the block is fixed in place.
        top, left, bottom, right (int): Boundaries of the block on the board.
        orig_pos (tuple): Original (i, j) grid position of the block.
    """

    def __init__(self, fixed=False):
        self.fixed = fixed
        self.top = None
        self.left = None
        self.bottom = None
        self.right = None
        self.orig_pos = None  # (i, j) in original grid.

    def set_boundaries(self, top, left, bottom, right):
        """
        Set the bounding box of the block.

        Args:
            top (int): Top boundary (y-coordinate).
            left (int): Left boundary (x-coordinate).
            bottom (int): Bottom boundary (y-coordinate).
            right (int): Right boundary (x-coordinate).
        """
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right

    def within_boundaries(self, x, y):
        """
        Check if the point (x, y) lies within the block's area.

        Args:
            x (int): x-coordinate.
            y (int): y-coordinate.

        Returns:
            bool: True if (x, y) is inside the block.
        """
        return self.left <= x <= self.right and self.top <= y <= self.bottom

    def reflect_beam(self, beam_position, beam_direction):
        """
        Reflect the beam based on the side it hit.

        Args:
            beam_position (tuple): Current position of the beam (x, y).
            beam_direction (tuple): Direction of the beam (dx, dy).

        Returns:
            tuple: New direction after reflection.
        """
        x, y = beam_position
        dx, dy = beam_direction

        # Calculate distances to each side of the block.
        dist_left = abs(x - self.left)
        dist_right = abs(x - self.right)
        dist_top = abs(y - self.top)
        dist_bottom = abs(y - self.bottom)

        dmin = min(dist_left, dist_right, dist_top, dist_bottom)

        # Reflect off the nearest side.
        if dmin == dist_left or dmin == dist_right:
            return (-dx, dy)  # Flip x-direction (horizontal reflection)
        else:
            return (dx, -dy)  # Flip y-direction (vertical reflection)

    def interact(self, beam_direction, beam_position):
        """
        Default interaction with the beam: no effect.

        Args:
            beam_direction (tuple): Incoming beam direction.
            beam_position (tuple): Beam's current position.

        Returns:
            list: List of resulting beam directions (default: unchanged).
        """
        return [beam_direction]


class ReflectBlock(Block):
    """
    Reflective block that bounces the beam off its surface.
    """

    def interact(self, beam_direction, beam_position):
        new_dir = self.reflect_beam(beam_position, beam_direction)
        return [new_dir]


class OpaqueBlock(Block):
    """
    Opaque block that absorbs the beam, stopping it completely.
    """

    def interact(self, beam_direction, beam_position):
        return []  # No beams continue.


class RefractBlock(Block):
    """
    Refractive block that splits the beam into two on first interaction:
    one continues, the other reflects. On subsequent interactions,
    only the continuing beam remains.
    """

    def __init__(self, fixed=False):
        super().__init__(fixed)
        self.has_refracted = False

    def interact(self, beam_direction, beam_position):
        if not self.has_refracted:
            self.has_refracted = True
            cont = beam_direction
            refl = self.reflect_beam(beam_position, beam_direction)
            return [cont, refl]
        else:
            return [beam_direction]
