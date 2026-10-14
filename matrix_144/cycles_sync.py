"""Синхронизатор природных и экономических осцилляторов — УСЛОВНЫЙ индикатор.

Идея Чижевского о связи солнечной активности с социальными процессами — гипотеза, а не
доказанный закон. Индекс ниже — рабочая эвристика для запуска режима СИП, он НЕ является
прогнозом войн или кризисов, а пороги не откалиброваны по данным. Все параметры — аргументы.

Формула (сохранена из исходной версии):
    friction = ss_index · 1.25 · (1 + |sin(2π · (year − phase_year) / 84)|) − k_wave · 50
"""
from __future__ import annotations

import json
import math

GLEISSBERG_PERIOD = 84.0  # условный период векового цикла, лет


class CyclesSynchronizer:
    def __init__(self, epoch_year: int = 2026, current_sun_spots: float = 120,
                 kondratiev_phase: float = -0.5, threshold: float = 144.0,
                 phase_year: float = 0.0, period: float = GLEISSBERG_PERIOD):
        if current_sun_spots < 0:
            raise ValueError("Число пятен не может быть отрицательным")
        if not -1.0 <= kondratiev_phase <= 1.0:
            raise ValueError("kondratiev_phase должна быть в [-1, 1]")
        self.year, self.ss_index, self.k_wave = epoch_year, current_sun_spots, kondratiev_phase
        self.threshold, self.phase_year, self.period = threshold, phase_year, period

    def evaluate(self) -> dict:
        angle = 2 * math.pi * ((self.year - self.phase_year) / self.period)
        excitation = math.sin(angle)
        solar_term = self.ss_index * 1.25
        friction = solar_term * (1.0 + abs(excitation)) - self.k_wave * 50.0
        return {
            "epoch_year": self.year,
            "gleissberg_excitation": round(excitation, 4),
            "friction_index": round(friction, 2),
            "threshold": self.threshold,
            "session_status": "ACTIVE_SYNTHESIS" if friction > self.threshold else "AUTONOMOUS",
            "note": "Условный индекс, не прогноз; пороги не откалиброваны.",
        }

    evaluate_planetary_friction = evaluate  # совместимость с прежним именем


if __name__ == "__main__":
    print(json.dumps(CyclesSynchronizer().evaluate(), ensure_ascii=False, indent=2))
