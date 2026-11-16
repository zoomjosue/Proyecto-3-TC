import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from turing_machine.parser import load_machine, parse_machine
from turing_machine.simulator import HaltReason, TuringMachine


ROOT = Path(__file__).resolve().parents[1]


class SimulatorTests(unittest.TestCase):
    def test_recognizer_accepts_and_rejects_required_cases(self) -> None:
        definition = load_machine(ROOT / "examples" / "reconocedor_anbn.yaml")
        machine = TuringMachine(definition)

        results = [machine.simulate(text) for text in definition.simulation_strings]

        self.assertEqual([result.accepted for result in results], [True, True, False, False])
        self.assertTrue(all(len(result.input_text) >= 5 for result in results))
        self.assertEqual(results[2].halt_reason, HaltReason.NO_TRANSITION)

    def test_altering_machine_duplicates_all_four_inputs(self) -> None:
        definition = load_machine(ROOT / "examples" / "alterador_duplicador.yaml")
        machine = TuringMachine(definition)

        for text in definition.simulation_strings:
            with self.subTest(text=text):
                result = machine.simulate(text)
                self.assertTrue(result.accepted)
                self.assertEqual(result.final_tape, f"{text}#{text}")
                self.assertGreaterEqual(len(text), 5)
                self.assertEqual(len(result.descriptions), result.steps + 1)

    def test_step_limit_stops_a_loop_without_claiming_rejection(self) -> None:
        data = {
            "q_states": {"q_list": ["loop", "accept"], "initial": "loop", "final": "accept"},
            "alphabet": ["a"],
            "tape_alphabet": ["a", None],
            "delta": [{
                "params": {
                    "initial_state": "loop",
                    "mem_cache_value": None,
                    "tape_input": "a",
                    "output": {
                        "final_state": "loop",
                        "mem_cache_value": None,
                        "tape_output": "a",
                        "tape_displacement": "S",
                    },
                }
            }],
            "simulation_strings": ["a"],
        }

        result = TuringMachine(parse_machine(data)).simulate("a", max_steps=3)

        self.assertFalse(result.accepted)
        self.assertEqual(result.halt_reason, HaltReason.STEP_LIMIT)
        self.assertEqual(result.steps, 3)


if __name__ == "__main__":
    unittest.main()
