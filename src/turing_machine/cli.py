"""Interfaz de linea de comandos del simulador."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .errors import ConfigurationError
from .formatter import format_result
from .parser import load_machine
from .simulator import HaltReason, TuringMachine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tm-sim",
        description="Simula una Maquina de Turing determinista de una cinta.",
    )
    parser.add_argument("archivo", type=Path, help="archivo YAML con la definicion de la MT")
    parser.add_argument(
        "--input",
        dest="inputs",
        action="append",
        help="cadena a simular; puede repetirse y reemplaza simulation_strings",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=10_000,
        help="limite de seguridad por cadena (predeterminado: 10000)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        definition = load_machine(arguments.archivo)
        inputs = tuple(arguments.inputs) if arguments.inputs is not None else definition.simulation_strings
        if not inputs:
            raise ConfigurationError("No hay cadenas configuradas para simular")

        machine = TuringMachine(definition)
        results = [machine.simulate(text, arguments.max_steps) for text in inputs]
    except (ConfigurationError, ValueError) as error:
        print(f"Error de configuracion: {error}", file=sys.stderr)
        return 2

    print(f"Maquina cargada: {arguments.archivo}")
    print(
        f"Estados: {len(definition.states)} | Transiciones: "
        f"{len(definition.transitions)} | Cadenas: {len(results)}"
    )
    for index, result in enumerate(results):
        if index:
            print("\n" + "=" * 72 + "\n")
        print(format_result(result))

    return 3 if any(item.halt_reason is HaltReason.STEP_LIMIT for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
