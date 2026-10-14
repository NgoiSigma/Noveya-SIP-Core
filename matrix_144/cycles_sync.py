"""Синхронизатор природных и экономических осцилляторов — Дифференциальная модель НОВЕЯ.

Переведен с линейных порогов на анализ производных (скоростей изменения векторов).
Связывает первую производную солнечной активности (dSS/dt) по Чижевскому с локальным 
градиентом падения энергетической рентабельности (EROI) в конкретной координатной ячейке.

Формула динамического трения (Friction):
    Friction = (dSS/dt · (1 + |sin(2π · Δt / 84)|) - K_wave · 50) · (1 + |eroi_gradient|)
"""
from __future__ import annotations

import json
import math

GLEISSBERG_PERIOD = 84.0  # Условный период векового цикла Глайсберга, лет


class CyclesSynchronizer:
    def __init__(self, 
                 epoch_year: int = 2026, 
                 current_sun_spots: float = 120.0,
                 previous_sun_spots: float = 105.0,  # Нужен для расчета первой производной dSS/dt
                 dt: float = 1.0,                     # Шаг времени (обычно 1 год или доля года)
                 kondratiev_phase: float = -0.5, 
                 eroi_gradient: float = 0.15,         # Градиент падения EROI ячейки (от 0.0 до 1.0)
                 threshold: float = 50.0,             # Перекалиброванный дифференциальный порог
                 phase_year: float = 0.0, 
                 period: float = GLEISSBERG_PERIOD):
        
        if current_sun_spots < 0 or previous_sun_spots < 0:
            raise ValueError("Число пятен на Солнце не может быть отрицательным")
        if dt <= 0:
            raise ValueError("Интервал времени dt должен быть строго больше нуля")
        if not -1.0 <= kondratiev_phase <= 1.0:
            raise ValueError("kondratiev_phase должна быть в диапазоне [-1, 1]")
        if not 0.0 <= eroi_gradient <= 1.0:
            raise ValueError("Градиент падения EROI должен быть в диапазоне [0, 1] (доля деградации)")
            
        self.year = epoch_year
        self.ss_index = current_sun_spots
        self.prev_ss = previous_sun_spots
        self.dt = dt
        self.k_wave = kondratiev_phase
        self.eroi_grad = eroi_gradient
        self.threshold = threshold
        self.phase_year = phase_year
        self.period = period

    def evaluate(self) -> dict:
        # 1. Расчет первой производной солнечной активности (dSS/dt)
        dSS_dt = (self.ss_index - self.prev_ss) / self.dt
        
        # 2. Фаза векового цикла Глайсберга (всплеск возбуждения среды)
        angle = 2 * math.pi * ((self.year - self.phase_year) / self.period)
        gleissberg_excitation = math.sin(angle)
        
        # 3. Солярная дифференциальная компонента (импульс Чижевского)
        # Если солнце идет на спад (dSS_dt <= 0), биологическое давление падает
        solar_impulse = max(0.0, dSS_dt) * 1.25
        
        # 4. Расчет индекса трения с учетом локального градиента деградации EROI ячейки
        # Чем быстрее падает EROI в координате, тем сильнее среда реагирует на солнечный удар
        base_friction = solar_impulse * (1.0 + abs(gleissberg_excitation)) - self.k_wave * 50.0
        dynamic_friction = base_friction * (1.0 + self.eroi_grad)
        
        # 5. Квантование статуса сессии СИП
        session_status = "ACTIVE_SYNTHESIS" if dynamic_friction > self.threshold else "AUTONOMOUS"
        
        return {
            "epoch_year": self.year,
            "dSS_dt": round(dSS_dt, 4),
            "eroi_gradient": round(self.eroi_grad, 4),
            "gleissberg_excitation": round(gleissberg_excitation, 4),
            "friction_index": round(dynamic_friction, 2),
            "threshold": self.threshold,
            "session_status": session_status,
            "note": "Дифференциальный индекс детерминированного слоя метода НОВЕЯ. Пороги откалиброваны по скоростям векторов.",
        }

    evaluate_planetary_friction = evaluate  # Совместимость с интерфейсом прежней версии ядра


if __name__ == "__main__":
    # Тестовый запуск: 2026 год, Солнце резко идет вверх (со 105 до 120), К-волна в депрессии, EROI падает на 15%
    sync = CyclesSynchronizer(
        epoch_year=2026,
        current_sun_spots=120.0,
        previous_sun_spots=105.0,
        dt=1.0,
        kondratiev_phase=-0.5,
        eroi_gradient=0.15,
        threshold=50.0
    )
    print(json.dumps(sync.evaluate(), ensure_ascii=False, indent=2))
