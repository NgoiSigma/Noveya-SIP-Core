"""Оператор Солидарных Игровых Практик (СИП): триада ролей и баланс 49–49–2.

ЛОГОС — связь/инициатор, ХАОС — анализ/генерация, КОСМОС — баланс/распределение.
КОСМОС удерживает плавающий баланс долей усилий 49–49–2 (допуск настраивается).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class Role(str, Enum):
    LOGOS = "ЛОГОС"
    CHAOS = "ХАОС"
    COSMOS = "КОСМОС"


DEFAULT_TARGET = {Role.LOGOS: 49.0, Role.CHAOS: 49.0, Role.COSMOS: 2.0}


class Triad:
    def __init__(self, target: Optional[dict] = None, tolerance: float = 5.0):
        self.target = dict(target or DEFAULT_TARGET)
        if abs(sum(self.target.values()) - 100.0) > 1e-9:
            raise ValueError("Целевые доли должны давать в сумме 100")
        self.tolerance = tolerance
        self.effort = {r: 0.0 for r in Role}

    @classmethod
    def from_manifesto(cls, path: str) -> "Triad":
        b = json.loads(Path(path).read_text(encoding="utf-8"))["balance"]
        return cls({Role.LOGOS: b["logos"], Role.CHAOS: b["chaos"], Role.COSMOS: b["cosmos"]},
                   b.get("tolerance", 5.0))

    def record(self, role: Role, effort: float) -> None:
        if effort < 0:
            raise ValueError("effort >= 0")
        self.effort[Role(role)] += effort

    def shares(self) -> dict:
        total = sum(self.effort.values())
        if total == 0:
            return {r: 0.0 for r in Role}
        return {r: 100.0 * v / total for r, v in self.effort.items()}

    def drift(self) -> dict:
        s = self.shares()
        return {r: round(s[r] - self.target[r], 2) for r in Role}

    def balanced(self) -> bool:
        return sum(self.effort.values()) > 0 and all(abs(d) <= self.tolerance for d in self.drift().values())

    def hint(self) -> Optional[Role]:
        """Роль, которой сильнее всего не хватает усилий (None, если баланс в допуске)."""
        if self.balanced() or sum(self.effort.values()) == 0:
            return None
        d = self.drift()
        return min(d, key=d.get)


@dataclass
class Decision:
    admitted: bool
    reason: str


class DialogGate:
    """Фильтр «внимания как ресурса»: диалог без общей цели и прикладного предмета закрывается."""

    def admit(self, goal: str, research_object: str) -> Decision:
        if not (goal or "").strip():
            return Decision(False, "Нет общей цели: сформулируйте цель или закройте диалог.")
        if not (research_object or "").strip():
            return Decision(False, "Нет прикладного предмета исследования: назовите, что именно изучается/делается.")
        return Decision(True, "Допущен: есть цель и предмет.")


@dataclass
class SipSession:
    cell_id: int
    mode: str = "AUTONOMOUS"            # или ACTIVE_SYNTHESIS (см. matrix_144.cycles_sync)
    triad: Triad = field(default_factory=Triad)
    gate: DialogGate = field(default_factory=DialogGate)
    buffer: list = field(default_factory=list)

    def note(self, text: str) -> None:
        self.buffer.append(text)

    def clear_buffer(self) -> int:
        """Протокол очистки («Сердце Чисто»): сбросить рабочий буфер. Возвращает число удалённых записей."""
        n = len(self.buffer)
        self.buffer.clear()
        return n
