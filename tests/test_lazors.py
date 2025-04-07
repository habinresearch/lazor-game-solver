"""
test_solver.py

Unit tests for the Lazor game components:
- .bff file parsing
- Board logic and block placement
- Block interaction behavior
- Solver correctness
- Visualization image generation

These tests can be run with:
    python -m unittest test_solver.py
"""

import unittest
import glob
import os
import tempfile
import shutil
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for image generation

from parser_bff import parse_bff_file
from board import Board
import solver
from blocks import ReflectBlock, OpaqueBlock, RefractBlock
from visualization import visualize_board
from visualization_image import save_laser_image


class TestBFFFiles(unittest.TestCase):
    """Test that .bff files can be parsed and contain expected keys."""

    def test_all_bff_files(self):
        bff_files = glob.glob(os.path.join("data", "*.bff"))
        self.assertGreater(len(bff_files), 0, "No .bff files found in the data folder.")

        for file in bff_files:
            with self.subTest(file=file):
                data = parse_bff_file(file)
                self.assertIn("grid", data)
                self.assertIn("blocks_available", data)
                self.assertIn("lasers", data)
                self.assertIn("points", data)


class TestBoard(unittest.TestCase):
    """Test Board initialization, block placement, and free position logic."""

    def setUp(self):
        self.data = {
            "grid": [["o", "o"], ["x", "o"]],
            "blocks_available": {"A": 1, "B": 0, "C": 0},
            "lasers": [(0, 0, 1, 0)],
            "points": [(1, 0)],
        }
        self.board = Board(self.data)

    def test_free_positions(self):
        expected_free_positions = {(0, 0), (0, 1), (1, 1)}
        self.assertEqual(set(self.board.free_positions), expected_free_positions)

    def test_is_placeable(self):
        self.assertTrue(self.board.is_placeable(0, 0))
        self.assertFalse(self.board.is_placeable(1, 0))  # cell marked 'x'

    def test_place_and_remove_free_block(self):
        block = ReflectBlock()
        self.board.place_free_block(0, 0, block)
        self.assertFalse(self.board.is_placeable(0, 0))
        self.assertEqual(len(self.board.free_blocks_placed), 1)

        self.board.remove_free_block(0, 0)
        self.assertTrue(self.board.is_placeable(0, 0))
        self.assertEqual(len(self.board.free_blocks_placed), 0)


class TestBlocks(unittest.TestCase):
    """Test behavior of different block types."""

    def setUp(self):
        self.reflect_block = ReflectBlock()
        self.reflect_block.set_boundaries(2, 2, 4, 4)

    def test_reflect_beam_left(self):
        new_dir = self.reflect_block.reflect_beam((2.1, 3), (1, 0))
        self.assertEqual(new_dir, (-1, 0))

    def test_reflect_beam_top(self):
        new_dir = self.reflect_block.reflect_beam((3, 2.1), (0, 1))
        self.assertEqual(new_dir, (0, -1))

    def test_opaque_block_interaction(self):
        opaque = OpaqueBlock()
        result = opaque.interact((1, 1), (3, 3))
        self.assertEqual(result, [])

    def test_refract_block_interaction_first(self):
        refract = RefractBlock()
        refract.set_boundaries(2, 2, 4, 4)
        result = refract.interact((1, 1), (3, 3))
        self.assertEqual(len(result), 2)

    def test_refract_block_interaction_subsequent(self):
        refract = RefractBlock()
        refract.set_boundaries(2, 2, 4, 4)
        _ = refract.interact((1, 1), (3, 3))  # first call sets has_refracted
        result = refract.interact((1, 1), (3, 3))
        self.assertEqual(len(result), 1)


class TestSolver(unittest.TestCase):
    """Test that the solver finds valid solutions."""

    def setUp(self):
        self.data = {
            "grid": [["o", "o"], ["o", "o"]],
            "blocks_available": {"A": 1, "B": 0, "C": 0},
            "lasers": [(0, 1, 1, 0)],
            "points": [(2, 1)],
        }
        self.board = Board(self.data)

    def test_solver_finds_solution(self):
        solution = solver.solve(self.board)
        self.assertIsNotNone(solution)
        self.assertTrue(solver.test_solution(self.board, set(self.data["points"])))


class TestVisualizationImage(unittest.TestCase):
    """Test that the visualization image gets correctly saved to disk."""

    def setUp(self):
        self.data = {
            "grid": [["o", "o"], ["o", "o"]],
            "blocks_available": {"A": 1, "B": 0, "C": 0},
            "lasers": [(0, 1, 1, 0)],
            "points": [(2, 1)],
        }
        self.board = Board(self.data)
        self.board.place_free_block(0, 0, ReflectBlock())

    def test_visualization_image_creation(self):
        temp_dir = tempfile.mkdtemp()
        try:
            filename = os.path.join(temp_dir, "test_solution.png")
            solution = [
                (block.orig_pos, type(block).__name__)
                for block in self.board.free_blocks_placed
            ]
            save_laser_image(self.board, solution=solution, filename=filename)
            self.assertTrue(os.path.exists(filename))
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
