"""Motor determinista de simulacion paso a paso."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .errors import ConfigurationError
from .models import MachineDefinition, Symbol
from .tape import Tape


class HaltReason(str, Enum):
    ACCEPTED = "accepted"
    NO_TRANSITION = "no_transition"
    STEP_LIMIT = "step_limit"


@dataclass(frozen=True, slots=True)
class InstantaneousDescription:
    step: int
    state: str
    cache: Symbol
    head: int
    cells: dict[int, str]


@dataclass(frozen=True, slots=True)
class SimulationResult:
    input_text: str
    accepted: bool
    halt_reason: HaltReason
    steps: int
    final_state: str
    final_cache: Symbol
    head: int
    final_tape: str
    descriptions: tuple[InstantaneousDescription, ...]


class TuringMachine:
    def __init__(self, definition: MachineDefinition) -> None:
        self.definition = definition

    def simulate(self, input_text: str, max_steps: int = 10_000) -> SimulationResult:
        if max_steps < 1:
            raise ValueError("max_steps debe ser mayor que cero")

        invalid = sorted(set(input_text) - self.definition.input_alphabet)
        if invalid:
            rendered = ", ".join(repr(value) for value in invalid)
            raise ConfigurationError(
                f"La cadena {input_text!r} contiene simbolos fuera del alfabeto: {rendered}"
            )

        tape = Tape.from_text(input_text)
        state = self.definition.initial_state
        cache: Symbol = None
        head = 0
        step = 0
        history = [self._description(step, state, cache, head, tape)]

        while state not in self.definition.final_states and step < max_steps:
            key = (state, cache, tape.read(head))
            transition = self.definition.transitions.get(key)
            if transition is None:
                return self._result(
                    input_text, False, HaltReason.NO_TRANSITION, step,
                    state, cache, head, tape, history,
                )

            tape.write(head, transition.write_symbol)
            cache = transition.next_cache
            state = transition.next_state
            head += transition.direction.offset
            step += 1
            history.append(self._description(step, state, cache, head, tape))

        accepted = state in self.definition.final_states
        reason = HaltReason.ACCEPTED if accepted else HaltReason.STEP_LIMIT
        return self._result(
            input_text, accepted, reason, step, state, cache, head, tape, history
        )

    @staticmethod
    def _description(
        step: int, state: str, cache: Symbol, head: int, tape: Tape
    ) -> InstantaneousDescription:
        return InstantaneousDescription(step, state, cache, head, tape.snapshot())

    @staticmethod
    def _result(
        input_text: str,
        accepted: bool,
        reason: HaltReason,
        steps: int,
        state: str,
        cache: Symbol,
        head: int,
        tape: Tape,
        history: list[InstantaneousDescription],
    ) -> SimulationResult:
        return SimulationResult(
            input_text=input_text,
            accepted=accepted,
            halt_reason=reason,
            steps=steps,
            final_state=state,
            final_cache=cache,
            head=head,
            final_tape=tape.content(),
            descriptions=tuple(history),
        )
