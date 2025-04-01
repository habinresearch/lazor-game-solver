import unittest
import glob
import os
import tempfile
import shutil
import matplotlib

matplotlib.use("Agg")  # Use a non-interactive backend for testing

from parser_bff import parse_bff_file
from board import Board
import solver
from blocks import ReflectBlock, OpaqueBlock, RefractBlock
from visualization import visualize_board
from visualization_image import save_laser_image


class TestBFFFiles(unittest.TestCase):
    def test_all_bff_files(self):
        # Get a list of all .bff files in the data folder.
        bff_files = glob.glob(os.path.join("data", "*.bff"))
        self.assertGreater(len(bff_files), 0, "No .bff files found in the data folder.")
        for file in bff_files:
            with self.subTest(file=file):
                data = parse_bff_file(file)
                # Check that essential keys exist.
                self.assertIn("grid", data)
                self.assertIn("blocks_available", data)
                self.assertIn("lasers", data)
                self.assertIn("points", data)


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.data = {
            "grid": [["o", "o"], ["x", "o"]],
            "blocks_available": {"A": 1, "B": 0, "C": 0},
            "lasers": [(0, 0, 1, 0)],
            "points": [(1, 0)],
        }
        self.board = Board(self.data)

    def test_free_positions(self):
        # In our grid, cells (0,0), (0,1), and (1,1) should be candidate free positions.
        expected_free_positions = {(0, 0), (0, 1), (1, 1)}
        self.assertEqual(set(self.board.free_positions), expected_free_positions)

    def test_is_placeable(self):
        # NOTE: The current Board.is_placeable only checks for an already placed free block.
        # To fully reflect the grid restrictions (e.g. "x" cells are disallowed),
        # update is_placeable in board.py as follows:
        #
        #     def is_placeable(self, i, j):
        #         if self.orig_grid[i][j] == "x":
        #             return False
        #         for block in self.free_blocks_placed:
        #             if block.orig_pos == (i, j):
        #                 return False
        #         return True
        #
        # For now, we expect:
        self.assertTrue(self.board.is_placeable(0, 0))
        self.assertFalse(self.board.is_placeable(1, 0))

    def test_place_and_remove_free_block(self):
        # Initially, no free block has been placed.
        self.assertEqual(len(self.board.free_blocks_placed), 0)
        # Place a free block at (0,0)
        block = ReflectBlock()
        self.board.place_free_block(0, 0, block)
        self.assertFalse(self.board.is_placeable(0, 0))
        self.assertEqual(len(self.board.free_blocks_placed), 1)
        # Remove the block.
        self.board.remove_free_block(0, 0)
        self.assertTrue(self.board.is_placeable(0, 0))
        self.assertEqual(len(self.board.free_blocks_placed), 0)


class TestBlocks(unittest.TestCase):
    def setUp(self):
        # Create a ReflectBlock with boundaries: top=2, left=2, bottom=4, right=4.
        self.reflect_block = ReflectBlock()
        self.reflect_block.set_boundaries(2, 2, 4, 4)

    def test_reflect_beam_left(self):
        # Beam coming from left: position (2.1, 3) with direction (1, 0)
        new_dir = self.reflect_block.reflect_beam((2.1, 3), (1, 0))
        self.assertEqual(new_dir, (-1, 0))

    def test_reflect_beam_top(self):
        # Beam coming from top: position (3, 2.1) with direction (0, 1)
        new_dir = self.reflect_block.reflect_beam((3, 2.1), (0, 1))
        self.assertEqual(new_dir, (0, -1))

    def test_opaque_block_interaction(self):
        opaque = OpaqueBlock()
        result = opaque.interact((1, 1), (3, 3))
        self.assertEqual(result, [])

    def test_refract_block_interaction_first(self):
        refract = RefractBlock()
        # Set boundaries so that reflect_beam works.
        refract.set_boundaries(2, 2, 4, 4)
        result = refract.interact((1, 1), (3, 3))
        # On the first interaction, it should produce both a continuing and a reflected beam.
        self.assertEqual(len(result), 2, "First interaction should produce two beams.")

    def test_refract_block_interaction_subsequent(self):
        refract = RefractBlock()
        refract.set_boundaries(2, 2, 4, 4)
        _ = refract.interact((1, 1), (3, 3))
        # Subsequent interactions should only produce the continuing beam.
        result = refract.interact((1, 1), (3, 3))
        self.assertEqual(
            len(result), 1, "Subsequent interactions should produce one beam."
        )


class TestSolver(unittest.TestCase):
    def setUp(self):
        # Create a simple 2x2 board that is known to be solvable.
        self.data = {
            "grid": [["o", "o"], ["o", "o"]],
            "blocks_available": {"A": 1, "B": 0, "C": 0},
            # Laser starting from left side at (0, 1) moving right.
            "lasers": [(0, 1, 1, 0)],
            # Target is on the right border of cell (0,1) (i.e. coordinate (2, 1)).
            "points": [(2, 1)],
        }
        self.board = Board(self.data)

    def test_solver_finds_solution(self):
        solution = solver.solve(self.board)
        self.assertIsNotNone(
            solution, "Solver failed to find a solution on a simple board."
        )
        # Verify that the solution results in all targets being hit.
        self.assertTrue(solver.test_solution(self.board, set(self.data["points"])))


class TestVisualizationImage(unittest.TestCase):
    def setUp(self):
        # Create a simple board for visualization testing.
        self.data = {
            "grid": [["o", "o"], ["o", "o"]],
            "blocks_available": {"A": 1, "B": 0, "C": 0},
            "lasers": [(0, 1, 1, 0)],
            "points": [(2, 1)],
        }
        self.board = Board(self.data)
        # Place a free block as part of the solution.
        self.board.place_free_block(0, 0, ReflectBlock())

    def test_visualization_image_creation(self):
        # Create a temporary directory to save the image.
        temp_dir = tempfile.mkdtemp()
        try:
            filename = os.path.join(temp_dir, "test_solution.png")
            # The solution is a list of tuples: (position, block type name)
            solution = [
                (block.orig_pos, type(block).__name__)
                for block in self.board.free_blocks_placed
            ]
            save_laser_image(self.board, solution=solution, filename=filename)
            self.assertTrue(
                os.path.exists(filename), "Visualization image was not created."
            )
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
