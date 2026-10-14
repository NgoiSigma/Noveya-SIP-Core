# scripts/logos_compiler.py
# Σ-FDL::LOGOS-COMPILER [GLAGOL_90_RESONATOR]
# Волновой компилятор смысловых метафор в параметры гелиосферной плазмы Кривицкого

from __future__ import annotations
import json
import math


class LogolCompilerError(Exception):
    """Исключение ФДЛ: Ошибка ортогонального сдвига фазы компилятора."""
    pass


class LogosCompiler:
    """Волновой переводчик Глаголя. Осуществляет ортогональный разворот вектора внимания на 90°.
    Пересчитывает заархивированные библейские и коранические метафоры в сухие физические
    показатели плотности плазменных облаков гелиосферы и резонансные частоты ЦНС.
    """

    def __init__(self, config_clock_path: str = "config/paschalia_clock.json"):
        self.config_path = config_clock_path
        self.c_speed = 299792458.0  # Константа скорости света (широта Хефрена)
        self.earth_speed_mph = 66600.0  # Орбитальная скорость Земли в милях/ч

    def _load_axial_delta(self, node_key: str) -> float:
        """Считывает угол прецессионного сдвига из календарных часов Миланковича."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data["solar_calibration_nodes"][node_key]["axial_angle_delta"]
        except Exception:
            # Заглушка эталонного сдвига по умолчанию (если конфиг еще не пушнут)
            defaults = {"august_transfiguration": 243.3, "september_equinox": 270.0}
            return defaults.get(node_key, 90.0)

    def compile_glagol_vector(self, metaphor_key: str, sun_spots: float) -> dict:
        """Осуществляет ортогональное квантование текстового вектора в волновой физический параметр."""
        clean_key = metaphor_key.lower().strip()
        
        # Начальные параметры волнового поля
        plasma_density = 0.0
        fapch_coherence = 1.0
        ion_voltage_kv = 0.0

        if "облако" in clean_key or "нефеле" in clean_key:
            # Метафора «Светлого Облака» Преображения -> Водородно-гелиевый плазменный слой Кривицкого
            delta_angle = self._load_axial_delta("august_transfiguration")
            
            # Физика коронного разряда гелиосферы (ионизация Персеид)
            plasma_density = sun_spots * 1.54 * abs(math.sin(math.radians(delta_angle)))
            ion_voltage_kv = (self.earth_speed_mph / 1000.0) * math.cos(math.radians(delta_angle))
            fapch_coherence = 1.0 / (1.0 + math.log10(1.0 + plasma_density))

            status = "HELIO_PLASMA_COMPRESSION"
            desc = "Вхождение Земли в высоковольтный водородно-гелиевый плазменный шлейф Солнца."

        elif "звезда в сердце" in clean_key or "утренняя звезда" in clean_key:
            # Метафора «Утренней звезды в сердце» Петра -> Фазовая автоподстройка частоты резонатора
            delta_angle = self._load_axial_delta("september_equinox")
            
            # Расчет частоты резонанса Шумана и автоподстройки ЦНС под геомагнитный сдвиг
            fapch_coherence = abs(math.sin(math.radians(delta_angle)) * (1.0 - (sun_spots / 300.0)))
            ion_voltage_kv = 7.83 * (1.0 + fapch_coherence)  # Базовая частота Шумана с модуляцией
            plasma_density = sun_spots * 0.08
            
            status = "BIOMAGNETIC_FAPCH_LOCK"
            desc = "Синхронизация биоэлектрического резонатора (сердца) с внешним импульсом солнечного поля."

        else:
            # Обычный фоновый шум инфополя
            status = "FLAT_BACKGROUND_NOISE"
            desc = "Текст не содержит навигационных волновых меток. Ортогональный сдвиг невозможен."
            fapch_coherence = 0.0

        return {
            "metaphor_processed": metaphor_key,
            "wave_status": status,
            "physical_description": desc,
            "plasma_density_index": round(abs(plasma_density), 4),
            "ion_voltage_kv": round(abs(ion_voltage_kv), 4),
            "fapch_coherence_coefficient": round(fapch_coherence, 4),
            "light_speed_scale": round(self.c_speed / (self.earth_speed_mph * (1.0 + fapch_coherence)), 2)
        }


if __name__ == "__main__":
    print("=== Тестирование волнового компилятора Глаголя ===")
    compiler = LogosCompiler()

    # Моделируем пик солнечной активности (130 пятен Чижевского)
    current_sun_activity = 130.0

    print("\n1. Компиляция метафоры 'Светлого Облака' Преображения:")
    res_plasma = compiler.compile_glagol_vector("Светлое Облако (Нефеле)", current_sun_activity)
    print(json.dumps(res_plasma, ensure_ascii=False, indent=2))

    print("\n2. Компиляция метафоры 'Утренней Звезды в Сердце':")
    res_fapch = compiler.compile_glagol_vector("Утренняя звезда в сердцах ваших", current_sun_activity)
    print(json.dumps(res_fapch, ensure_ascii=False, indent=2))
