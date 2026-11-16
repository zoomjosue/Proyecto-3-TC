"""Punto de entrada alternativo para ejecutar el proyecto sin instalarlo."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from turing_machine.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())

