# blocks.py


class Block:
    def __init__(self, fixed=False):
        self.fixed = fixed
        self.top = None
        self.left = None
        self.bottom = None
        self.right = None
        self.orig_pos = None  # (i, j) in original grid.

    def set_boundaries(self, top, left, bottom, right):
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right

    def within_boundaries(self, x, y):
        """Return True if (x, y) lies within the block's area."""
        return self.left <= x <= self.right and self.top <= y <= self.bottom

    def reflect_beam(self, beam_position, beam_direction):
        """
        Compute the reflection based on the beam's intersection point.
        Calculate distances to each face of the block and flip the component corresponding to the nearest face.
        """
        x, y = beam_position
        dx, dy = beam_direction
        dist_left = abs(x - self.left)
        dist_right = abs(x - self.right)
        dist_top = abs(y - self.top)
        dist_bottom = abs(y - self.bottom)
        dmin = min(dist_left, dist_right, dist_top, dist_bottom)
        if dmin == dist_left or dmin == dist_right:
            # Flip horizontal component.
            return (-dx, dy)
        else:
            # Flip vertical component.
            return (dx, -dy)

    def interact(self, beam_direction, beam_position):
        """Default: do nothing."""
        return [beam_direction]


class ReflectBlock(Block):
    def interact(self, beam_direction, beam_position):
        new_dir = self.reflect_beam(beam_position, beam_direction)
        return [new_dir]


class OpaqueBlock(Block):
    def interact(self, beam_direction, beam_position):
        # Stop the beam.
        return []


class RefractBlock(Block):
    def __init__(self, fixed=False):
        super().__init__(fixed)
        self.has_refracted = False

    def interact(self, beam_direction, beam_position):
        # On the first interaction, generate both beams.
        if not self.has_refracted:
            self.has_refracted = True
            cont = beam_direction
            refl = self.reflect_beam(beam_position, beam_direction)
            return [cont, refl]
        else:
            # On subsequent interactions, only the beam that continues.
            return [beam_direction]
