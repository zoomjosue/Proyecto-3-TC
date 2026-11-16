"""Presentacion legible de las descripciones instantaneas y resultados."""

from __future__ import annotations

from .models import Symbol
from .simulator import HaltReason, InstantaneousDescription, SimulationResult

BLANK = "_"


def render_symbol(symbol: Symbol) -> str:
    return BLANK if symbol is None else symbol


def format_description(description: InstantaneousDescription) -> str:
    cells = description.cells
    positions = set(cells) | {description.head}
    left, right = min(positions) - 1, max(positions) + 1
    parts: list[str] = []
    for position in range(left, right + 1):
        if position == description.head:
            parts.append(
                f"<{description.state}, cache={render_symbol(description.cache)}>"
            )
        parts.append(render_symbol(cells.get(position)))
    return f"{description.step:04d} | " + " ".join(parts)


def format_result(result: SimulationResult) -> str:
    if result.halt_reason is HaltReason.ACCEPTED:
        status = "ACEPTADA"
        detail = "se alcanzo un estado final"
    elif result.halt_reason is HaltReason.NO_TRANSITION:
        status = "RECHAZADA"
        detail = "no existe una transicion aplicable"
    else:
        status = "DETENIDA"
        detail = "se alcanzo el limite de pasos"

    input_label = result.input_text if result.input_text else "ε"
    tape_label = result.final_tape if result.final_tape else "ε"
    descriptions = "\n".join(format_description(item) for item in result.descriptions)
    return (
        f"Cadena: {input_label!r}\n"
        f"{descriptions}\n"
        f"Resultado: {status} ({detail})\n"
        f"Pasos: {result.steps} | Estado final: {result.final_state} | "
        f"Cinta final: {tape_label!r}"
    )

