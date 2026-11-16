import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from turing_machine.tape import Tape


class TapeTests(unittest.TestCase):
    def test_tape_is_infinite_in_both_directions(self) -> None:
        tape = Tape.from_text("ab")
        tape.write(-2, "X")
        tape.write(4, "Y")

        self.assertEqual(tape.read(-2), "X")
        self.assertIsNone(tape.read(-1))
        self.assertEqual(tape.content(), "X_ab__Y")

    def test_writing_blank_removes_a_cell(self) -> None:
        tape = Tape.from_text("abc")
        tape.write(1, None)

        self.assertIsNone(tape.read(1))
        self.assertEqual(tape.content(), "a_c")


if __name__ == "__main__":
    unittest.main()

