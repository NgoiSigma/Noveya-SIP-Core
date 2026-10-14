"""Оператор Солидарных Игровых Практик (СИП): триада ролей и баланс 49–49–2.

ЛОГОС — связь/инициатор, ХАОС — анализ/генерация, КОСМОС — баланс/распределение.
КОСМОС удерживает плавающий баланс долей усилий 49–49–2 (допуск настраивается).
Интегрирован с дифференциальными датчиками среды и геодезической сеткой 144.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

# Импортируем переписанные дифференциальные модули
from matrix_144.grid_allocator import GridAllocator
from matrix_144.cycles_sync import CyclesSynchronizer


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
    """Фильтр «внимания как ресурса»: диалог без общей цели и прикладного предмета закрывается.
    Предотвращает манипулятивные практики и отток энергии на пустые споры.
    """
    def admit(self, goal: str, research_object: str) -> Decision:
        if not (goal or "").strip():
            return Decision(False, "Нет общей цели: сформулируйте предметную цель или закройте диалог.")
        if not (research_object or "").strip():
            return Decision(False, "Нет прикладного предмета: отказ во внимании. Исключите пустую софистику.")
        return Decision(True, "Допущен: есть цель и предмет.")


@dataclass
class SipSession:
    lat: float
    lon: float
    mode: str = "AUTONOMOUS"
    cell_id: int = field(init=False)
    local_eroi_grad: float = field(init=False)
    triad: Triad = field(default_factory=Triad)
    gate: DialogGate = field(default_factory=DialogGate)
    buffer: list = field(default_factory=list)
    
    # Инициализация геодезического затвора НОВЕЯ
    _allocator: GridAllocator = field(default_factory=lambda: GridAllocator(default_depth=3), repr=False)

    def __post_init__(self):
        # Автоматическая рекурсивная локализация ячейки при создании сессии
        context = self._allocator.locate(self.lat, self.lon)
        self.cell_id = context["base_cell_id"]
        self.local_eroi_grad = context["local_eroi_gradient"]

    def sync_environmental_factors(self, 
                                   epoch_year: int = 2026, 
                                   current_sun_spots: float = 120.0, 
                                   previous_sun_spots: float = 105.0,
                                   kondratiev_phase: float = -0.5) -> dict:
        """Динамический переключатель режимов ядра. 
        Считывает производную солнечной активности и сопоставляет с градиентом EROI ячейки.
        """
        synchronizer = CyclesSynchronizer(
            epoch_year=epoch_year,
            current_sun_spots=current_sun_spots,
            previous_sun_spots=previous_sun_spots,
            kondratiev_phase=kondratiev_phase,
            eroi_gradient=self.local_eroi_grad,
            threshold=50.0
        )
        
        metrics = synchronizer.evaluate()
        self.mode = metrics["session_status"]
        
        # Если включился режим ACTIVE_SYNTHESIS, КОСМОС сжимает толерантность к дрейфу долей
        if self.mode == "ACTIVE_SYNTHESIS":
            self.triad.tolerance = 1.5  # Жесткий затвор, не позволяющий забалтывать ресурсы
            self.note(f"[SYSTEM] Внимание: Запуск СИП сессии в ячейке {self.cell_id}. Толерантность зажата.")
        else:
            self.triad.tolerance = 5.0
            
        return metrics

    def note(self, text: str) -> None:
        self.buffer.append(text)

    def clear_buffer(self) -> int:
        """Протокол очистки («Сердце Чисто»): сбросить рабочий буфер. Возвращает число удалённых записей."""
        n = len(self.buffer)
        self.buffer.clear()
        return n


if __name__ == "__main__":
    # Тест интеграции: Инициализация сессии для Николаева
    print("=== Запуск инициализации ядра НОВЕЯ-СИП ===")
    session = SipSession(lat=46.97, lon=31.99)
    print(f"Локализация завершена. Базовая ячейка: {session.cell_id}, Локальный градиент EROI: {session.local_eroi_grad}")
    
    # Моделируем резкий скачок активности Солнца (с 105 до 125 пятен) при депрессии Кондратьева
    print("\n=== Синхронизация с датчиками космической среды ===")
    environment_status = session.sync_environmental_factors(
        epoch_year=2026,
        current_sun_spots=125.0,
        previous_sun_spots=105.0,
        kondratiev_phase=-0.5
    )
    
    print(f"Текущий режим сессии: {session.mode}")
    print(f"Допуск дрейфа долей Триады: ±{session.triad.tolerance}%")
    
    # Проверка работы волнового фильтра внимания (DialogGate)
    print("\n=== Проверка фильтра внимания DialogGate ===")
    bad_decision = session.gate.admit(goal="поспорить о психологии по Фрейду", research_object="")
    print(f"Пустой диалог: Допуск = {bad_decision.admitted} -> Причина: {bad_decision.reason}")
    
    good_decision = session.gate.admit(
        goal="Нормирование распределения чистой воды в промзоне", 
        research_object="Скважины кристаллического фундамента"
    )
    print(f"Предметный диалог: Допуск = {good_decision.admitted} -> Причина: {good_decision.reason}")
