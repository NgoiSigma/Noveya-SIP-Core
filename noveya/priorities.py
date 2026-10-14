"""24 Направления Развития и матрица Курса Приоритетов 6×6 (Формальная диалогика, табл. 3.Н и 4.Н).

24 направления разбиты на 6 групп по 4. Матрица приоритетов — циклический сдвиг групп
(латинский квадрат): в ПРi по шагу j в фокусе группа (i-1+j) mod 6.
Названия направлений здесь НЕ зашиты — подгружайте из config/directions.json.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

DEFAULT_GROUPS: tuple[tuple[int, ...], ...] = (
    (1, 3, 5, 11),
    (7, 10, 15, 24),
    (2, 9, 20, 23),
    (4, 13, 16, 18),
    (8, 12, 21, 22),
    (6, 14, 17, 19),
)


def load_direction_names(path: Optional[str] = None) -> dict[int, str]:
    names = {n: f"Направление {n}" for n in range(1, 25)}
    if path and Path(path).exists():
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        names.update({int(k): v for k, v in raw.items() if v})
    return names


class PriorityCourse:
    def __init__(self, groups=DEFAULT_GROUPS):
        self.groups = tuple(tuple(g) for g in groups)
        self.validate()

    def validate(self) -> None:
        flat = [d for g in self.groups for d in g]
        if sorted(flat) != list(range(1, 25)):
            raise ValueError("Группы должны разбивать направления 1..24 без пропусков и повторов.")
        if len(self.groups) != 6 or any(len(g) != 4 for g in self.groups):
            raise ValueError("Нужно 6 групп по 4 направления.")

    def focus(self, priority: int, step: int) -> tuple[int, ...]:
        """priority: 1..6 (ПР1..ПР6); step: 0 — базовая группа, 1..6 — шаги."""
        if not (1 <= priority <= 6 and 0 <= step <= 6):
            raise ValueError("priority 1..6, step 0..6")
        return self.groups[(priority - 1 + step) % 6]

    def matrix(self) -> list[list[tuple[int, ...]]]:
        return [[self.focus(p, s) for s in range(0, 7)] for p in range(1, 7)]

    def is_latin(self) -> bool:
        m = [[self.focus(p, s) for s in range(1, 7)] for p in range(1, 7)]
        rows = all(len(set(r)) == 6 for r in m)
        cols = all(len({m[r][c] for r in range(6)}) == 6 for c in range(6))
        return rows and cols
