"""Lectura y validacion de la estructura YAML indicada en el enunciado."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

from .errors import ConfigurationError
from .models import Direction, MachineDefinition, Symbol, Transition


def load_machine(path: str | Path) -> MachineDefinition:
    source = Path(path)
    try:
        with source.open("r", encoding="utf-8") as stream:
            data = yaml.safe_load(stream)
    except OSError as error:
        raise ConfigurationError(f"No se pudo leer {source}: {error}") from error
    except yaml.YAMLError as error:
        raise ConfigurationError(f"YAML invalido en {source}: {error}") from error
    return parse_machine(data)


def parse_machine(data: Any) -> MachineDefinition:
    root = _mapping(data, "raiz")
    q_states = _mapping(_required(root, "q_states", "raiz"), "q_states")

    states = frozenset(
        _state(value, "q_states.q_list")
        for value in _sequence(_required(q_states, "q_list", "q_states"), "q_states.q_list")
    )
    if not states:
        raise ConfigurationError("q_states.q_list no puede estar vacia")

    initial = _state(_required(q_states, "initial", "q_states"), "q_states.initial")
    final_raw = _required(q_states, "final", "q_states")
    if _is_sequence(final_raw):
        final_states = frozenset(
            _state(value, "q_states.final")
            for value in _sequence(final_raw, "q_states.final")
        )
    else:
        final_states = frozenset({_state(final_raw, "q_states.final")})
    if not final_states:
        raise ConfigurationError("q_states.final debe contener al menos un estado")

    if initial not in states:
        raise ConfigurationError(f"El estado inicial {initial!r} no aparece en q_list")
    unknown_finals = final_states - states
    if unknown_finals:
        raise ConfigurationError(
            f"Estados finales no declarados en q_list: {_render_set(unknown_finals)}"
        )

    input_alphabet = frozenset(
        _nonblank_symbol(value, "alphabet")
        for value in _sequence(_required(root, "alphabet", "raiz"), "alphabet")
    )
    tape_alphabet = frozenset(
        _symbol(value, "tape_alphabet")
        for value in _sequence(_required(root, "tape_alphabet", "raiz"), "tape_alphabet")
    )
    if None not in tape_alphabet:
        raise ConfigurationError("tape_alphabet debe incluir null como simbolo blanco")
    if not input_alphabet.issubset(tape_alphabet):
        missing = input_alphabet - tape_alphabet
        raise ConfigurationError(
            f"tape_alphabet no contiene todo alphabet: {_render_set(missing)}"
        )

    transition_map: dict[tuple[str, Symbol, Symbol], Transition] = {}
    delta = _sequence(_required(root, "delta", "raiz"), "delta")
    for index, raw_transition in enumerate(delta):
        location = f"delta[{index}]"
        item = _mapping(raw_transition, location)
        params = _mapping(_required(item, "params", location), f"{location}.params")
        output = _mapping(_required(params, "output", f"{location}.params"), f"{location}.params.output")

        state = _state(_required(params, "initial_state", f"{location}.params"), f"{location}.params.initial_state")
        cache = _symbol(params.get("mem_cache_value"), f"{location}.params.mem_cache_value")
        read = _symbol(_required(params, "tape_input", f"{location}.params"), f"{location}.params.tape_input")
        next_state = _state(_required(output, "final_state", f"{location}.params.output"), f"{location}.params.output.final_state")
        next_cache = _symbol(output.get("mem_cache_value"), f"{location}.params.output.mem_cache_value")
        write = _symbol(_required(output, "tape_output", f"{location}.params.output"), f"{location}.params.output.tape_output")
        raw_direction = str(_required(output, "tape_displacement", f"{location}.params.output")).upper()
        try:
            direction = Direction(raw_direction)
        except ValueError as error:
            raise ConfigurationError(
                f"{location}.params.output.tape_displacement debe ser L, R o S"
            ) from error

        if state not in states or next_state not in states:
            raise ConfigurationError(f"{location} usa un estado no declarado")
        for value, label in (
            (cache, "mem_cache_value de entrada"),
            (read, "tape_input"),
            (next_cache, "mem_cache_value de salida"),
            (write, "tape_output"),
        ):
            if value not in tape_alphabet:
                raise ConfigurationError(
                    f"{location}: {label}={value!r} no pertenece a tape_alphabet"
                )

        key = (state, cache, read)
        if key in transition_map:
            raise ConfigurationError(
                f"{location} duplica la transicion determinista para {key!r}"
            )
        transition_map[key] = Transition(next_state, next_cache, write, direction)

    strings = tuple(
        _simulation_string(value, index)
        for index, value in enumerate(
            _sequence(_required(root, "simulation_strings", "raiz"), "simulation_strings")
        )
    )
    for text in strings:
        invalid = set(text) - input_alphabet
        if invalid:
            raise ConfigurationError(
                f"La cadena {text!r} usa simbolos fuera de alphabet: {_render_set(invalid)}"
            )

    return MachineDefinition(
        states=states,
        initial_state=initial,
        final_states=final_states,
        input_alphabet=input_alphabet,
        tape_alphabet=tape_alphabet,
        transitions=transition_map,
        simulation_strings=strings,
    )


def _required(mapping: Mapping[str, Any], key: str, location: str) -> Any:
    if key not in mapping:
        raise ConfigurationError(f"Falta el campo obligatorio {location}.{key}")
    return mapping[key]


def _mapping(value: Any, location: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ConfigurationError(f"{location} debe ser un objeto YAML")
    return value


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes))


def _sequence(value: Any, location: str) -> Sequence[Any]:
    if not _is_sequence(value):
        raise ConfigurationError(f"{location} debe ser una lista YAML")
    return value


def _state(value: Any, location: str) -> str:
    if value is None or isinstance(value, (Mapping, Sequence)) and not isinstance(value, str):
        raise ConfigurationError(f"{location} debe ser un estado escalar")
    rendered = str(value)
    if not rendered:
        raise ConfigurationError(f"{location} no puede estar vacio")
    return rendered


def _symbol(value: Any, location: str) -> Symbol:
    if value is None:
        return None
    if isinstance(value, (Mapping, Sequence)) and not isinstance(value, str):
        raise ConfigurationError(f"{location} debe ser un simbolo escalar o null")
    rendered = str(value)
    if len(rendered) != 1:
        raise ConfigurationError(f"{location}={rendered!r} debe tener exactamente un caracter")
    return rendered


def _nonblank_symbol(value: Any, location: str) -> str:
    symbol = _symbol(value, location)
    if symbol is None:
        raise ConfigurationError(f"{location} no puede contener null")
    return symbol


def _simulation_string(value: Any, index: int) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    raise ConfigurationError(f"simulation_strings[{index}] debe ser una cadena")


def _render_set(values: set[Any] | frozenset[Any]) -> str:
    return ", ".join(sorted(repr(value) for value in values))

