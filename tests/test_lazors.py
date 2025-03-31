import unittest
import glob
import os
from parser_bff import parse_bff_file
from board import Board


class TestBFFFiles(unittest.TestCase):
    def test_all_bff_files(self):
        # Get a list of all .bff files in the data folder.
        bff_files = glob.glob(os.path.join("data", "*.bff"))
        self.assertGreater(len(bff_files), 0, "No .bff files found in the data folder.")

        for file in bff_files:
            with self.subTest(file=file):
                print(f"--- Parsing file: {file} ---")
                data = parse_bff_file(file)

                # Print all key-value pairs from the parsed data.
                for key, value in data.items():
                    print(f"{key}: {value}")
                print()  # Print a blank line for readability

                # Check that the essential keys exist.
                self.assertIn("grid", data)
                self.assertIn("blocks_available", data)
                self.assertIn("lasers", data)
                self.assertIn("points", data)


class TestLazors(unittest.TestCase):
    def test_board(self):
        data = {
            "grid": [["o", "o"], ["x", "o"]],
            "blocks_available": {"A": 1, "B": 0, "C": 0},
            "lasers": [(0, 0, 1, 0)],
            "points": [(1, 0)],
        }
        board = Board(data)

        # Check is_placeable:
        # (0, 0) is allowed because grid[0][0] == "o"
        self.assertTrue(board.is_placeable(0, 0))
        # (1, 0) is not allowed because grid[1][0] == "x"
        self.assertFalse(board.is_placeable(1, 0))

        # Check that free_positions were computed correctly.
        # In our grid, cells (0,0), (0,1), and (1,1) should be candidate free positions.
        expected_free_positions = {(0, 0), (0, 1), (1, 1)}
        self.assertEqual(set(board.free_positions), expected_free_positions)

        # Optionally, check that no free block has been placed initially.
        self.assertEqual(len(board.free_blocks_placed), 0)


if __name__ == "__main__":
    unittest.main()
