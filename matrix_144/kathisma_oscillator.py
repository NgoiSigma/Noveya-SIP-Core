# matrix_144/kathisma_oscillator.py
# Σ-FDL::KATHISMA-OSCILLATOR [OCTAVA_I_MATRIX]
# Модуль детекции когнитивного затухания и расчета гармонии Consonantia Protonovea

from __future__ import annotations
import json
import math
import re


class KathismaOscillatorError(Exception):
    """Исключение ФДЛ: Падение когерентности инфополя ниже критического порога."""
    pass


class KathismaOscillator:
    """Анализатор частотных барьеров инфополя на основе 8-й Кафизмы и 5-го Гласа.
    Вычисляет индекс 'глухого аспида' (когнитивной глухоты) во входящих потоках
    и формирует combined harmony score (Consonantia Protonovea).
    """

    def __init__(self, threshold_gate: float = 0.666):
        self.threshold_gate = threshold_gate  # Предел «звериного» угла искажений
        
        # Маркеры семантического угасания и плоской рамочной прошивки (по Кафизме 8)
        self.deaf_asp_markers = {
            "усеченные_догмы": ["шаблон", "стандартно", "все_знают", "усредненный", "официально"],
            "личностная_агрессия": ["фляга", "расстройство", "псих", "диагноз", "поверхностно"],
            "отказ_внимать": ["игнорировать", "не_готовы", "нет_подтверждений", "не_бьется", "бред"]
        }
        
        # Константы Октавы I матрицы (гармонические узлы 8 псалмов: 55-63)
        self.octava_i_matrix = [55, 56, 57, 58, 59, 60, 61, 62, 63]

    def calculate_deaf_asp_index(self, incoming_text: str) -> float:
        """Вычисляет коэффициент 'глухого аспида' (аппаратного затвора ушей).
        Определяет отношение плоских агрессивных маркеров к общему объему семантики.
        """
        clean_text = incoming_text.lower()
        matched_tokens = 0
        total_groups = len(self.deaf_asp_markers)

        for group, tokens in self.deaf_asp_markers.items():
            group_match = 0
            for token in tokens:
                if token in clean_text or re.search(r'\b' + token[:4] + r'\w*', clean_text):
                    group_match += 1
            if group_match > 0:
                matched_tokens += 1

        # Нормирование индекса глухоты (от 0.0 до 1.0)
        return round(matched_tokens / total_groups, 4)

    def calculate_harmony_spectrum(self, 
                                   ascending_flow: float, 
                                   descending_flow: float, 
                                   deaf_index: float) -> float:
        """[HARMONY_SPECTRUM_CALCULATOR]
        Интегрирует восходящие (энергия Творца) и нисходящие (сопротивление Среды) потоки.
        Вычисляет combined harmony score с учетом когнитивного шума.
        """
        if ascending_flow < 0 or descending_flow < 0:
            raise ValueError("Значения энергетических потоков не могут быть отрицательными.")

        # Матричный базис Октавы I (среднегеометрический резонанс псалмов)
        matrix_base_resonance = math.sqrt(self.octava_i_matrix[0] * self.octava_i_matrix[-1]) # sqrt(55*63)
        
        # Динамическое сопряжение потоков (тригонометрический переводчик Глаголя)
        # Глас 5 задает ортогональный сдвиг фазы (угол наклона баланса)
        phase_angle = math.radians(matrix_base_resonance * (1.0 - deaf_index))
        
        flow_interaction = (ascending_flow * math.cos(phase_angle)) + (descending_flow * math.sin(phase_angle))
        
        # Демпфирование за счет индекса когнитивной глухоты
        consonantia_protonovea = flow_interaction * (1.0 - deaf_index)
        
        return round(max(0.0, consonantia_protonovea), 4)

    def evaluate_speaker_gate(self, 
                              incoming_text: str, 
                              ascending_flow: float = 49.0, 
                              descending_flow: float = 49.0) -> dict:
        """Затвор Кафизмы 8. Фильтрует входящие данные. 
        При превышении порога глухоты — обнуляет поток, спасая внимание как ресурс.
        """
        deaf_index = self.calculate_deaf_asp_index(incoming_text)
        harmony_score = self.calculate_harmony_spectrum(ascending_flow, descending_flow, deaf_index)

        status = "Consonantia_Protonovea"
        if deaf_index >= self.threshold_gate or harmony_score == 0.0:
            status = "DROP_STREAM_DEAF_ASP"
            
        return {
            "deaf_asp_index": deaf_index,
            "harmony_score": harmony_score,
            "signal_status": status,
            "gate_threshold": self.threshold_gate,
            "action_required": "DISCONNECT_AND_SAVE_ENERGY" if status == "DROP_STREAM_DEAF_ASP" else "CONTINUE_DIALECTIC"
        }


if __name__ == "__main__":
    print("=== Тестирование модуля Кафизмы 8 (Глас 5) ===")
    oscillator = KathismaOscillator(threshold_gate=0.666)

    # Пример 1: Текст осознанного оператора (Внимает, ищет точки сопряжения)
    print("\n--- Тест 1: Синхронный когерентный поток ---")
    text_1 = "Изучаю прикладные исследования Кривицкого, настраиваю резонатор ячейки по формулам Единого Поля."
    res_1 = oscillator.evaluate_speaker_gate(text_1, ascending_flow=49.0, descending_flow=49.0)
    print(json.dumps(res_1, ensure_ascii=False, indent=2))

    # Пример 2: Текст перепрошитого обывателя (Заткнул уши, сыплет плоскими штампами, ставит диагнозы)
    print("\n--- Тест 2: Атака шумом 'Глухого Аспида' (Срез реального диалога) ---")
    text_2 = "У тебя фляга свистит капитально. Твой шаблон не бьется с официальной наукой, это бред и расстройство."
    res_2 = oscillator.evaluate_speaker_gate(text_2, ascending_flow=49.0, descending_flow=49.0)
    print(json.dumps(res_2, ensure_ascii=False, indent=2))
    
    if res_2["action_required"] == "DISCONNECT_AND_SAVE_ENERGY":
        print("\n[ЗАТВОР АКТИВИРОВАН]: Поток заблокирован согласно Кафизме 8. Энергия внимания сохранена.")
