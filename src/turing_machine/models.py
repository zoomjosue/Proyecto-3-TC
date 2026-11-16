"""Modelos inmutables que describen formalmente una maquina."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

Symbol = str | None
TransitionKey = tuple[str, Symbol, Symbol]


class Direction(str, Enum):
    LEFT = "L"
    RIGHT = "R"
    STAY = "S"

    @property
    def offset(self) -> int:
        return {self.LEFT: -1, self.RIGHT: 1, self.STAY: 0}[self]


@dataclass(frozen=True, slots=True)
class Transition:
    next_state: str
    next_cache: Symbol
    write_symbol: Symbol
    direction: Direction


@dataclass(frozen=True, slots=True)
class MachineDefinition:
    states: frozenset[str]
    initial_state: str
    final_states: frozenset[str]
    input_alphabet: frozenset[str]
    tape_alphabet: frozenset[Symbol]
    transitions: Mapping[TransitionKey, Transition]
    simulation_strings: tuple[str, ...]

    def __post_init__(self) -> None:
        # Evita que codigo cliente modifique accidentalmente la funcion delta.
        object.__setattr__(self, "transitions", MappingProxyType(dict(self.transitions)))

