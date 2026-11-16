"""Implementacion dispersa de una cinta infinita en ambas direcciones."""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import Symbol


@dataclass(slots=True)
class Tape:
    _cells: dict[int, str] = field(default_factory=dict)

    @classmethod
    def from_text(cls, text: str) -> "Tape":
        return cls({index: symbol for index, symbol in enumerate(text)})

    def read(self, position: int) -> Symbol:
        return self._cells.get(position)

    def write(self, position: int, symbol: Symbol) -> None:
        if symbol is None:
            self._cells.pop(position, None)
        else:
            self._cells[position] = symbol

    def nonblank_bounds(self) -> tuple[int, int] | None:
        if not self._cells:
            return None
        return min(self._cells), max(self._cells)

    def visible_bounds(self, head: int, margin: int = 1) -> tuple[int, int]:
        bounds = self.nonblank_bounds()
        if bounds is None:
            return head - margin, head + margin
        return min(bounds[0], head) - margin, max(bounds[1], head) + margin

    def content(self) -> str:
        """Contenido entre el primer y ultimo simbolo no blanco."""
        bounds = self.nonblank_bounds()
        if bounds is None:
            return ""
        left, right = bounds
        return "".join(self.read(index) or "_" for index in range(left, right + 1))

    def snapshot(self) -> dict[int, str]:
        return dict(self._cells)

