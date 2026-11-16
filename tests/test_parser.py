import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from turing_machine.errors import ConfigurationError
from turing_machine.parser import load_machine, parse_machine


ROOT = Path(__file__).resolve().parents[1]


class ParserTests(unittest.TestCase):
    def test_loads_statement_compatible_schema(self) -> None:
        definition = load_machine(ROOT / "examples" / "reconocedor_anbn.yaml")

        self.assertEqual(definition.initial_state, "q_start")
        self.assertEqual(definition.final_states, {"q_accept"})
        self.assertIn(None, definition.tape_alphabet)
        self.assertEqual(len(definition.simulation_strings), 4)

    def test_rejects_non_deterministic_duplicate(self) -> None:
        transition = {
            "params": {
                "initial_state": "q0",
                "mem_cache_value": None,
                "tape_input": "a",
                "output": {
                    "final_state": "qf",
                    "mem_cache_value": None,
                    "tape_output": "a",
                    "tape_displacement": "S",
                },
            }
        }
        data = {
            "q_states": {"q_list": ["q0", "qf"], "initial": "q0", "final": "qf"},
            "alphabet": ["a"],
            "tape_alphabet": ["a", None],
            "delta": [transition, transition],
            "simulation_strings": ["a"],
        }

        with self.assertRaisesRegex(ConfigurationError, "duplica"):
            parse_machine(data)

    def test_rejects_input_outside_alphabet(self) -> None:
        data = {
            "q_states": {"q_list": ["q0", "qf"], "initial": "q0", "final": "qf"},
            "alphabet": ["a"],
            "tape_alphabet": ["a", None],
            "delta": [],
            "simulation_strings": ["ab"],
        }

        with self.assertRaisesRegex(ConfigurationError, "fuera de alphabet"):
            parse_machine(data)


if __name__ == "__main__":
    unittest.main()

