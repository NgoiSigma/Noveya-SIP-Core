# noveya/priorities.py
# Σ-FDL::PRIORITIES-OSCILLATOR
# Модуль расчета Курса Приоритетов 6×6 и нормирования векторов развития

from __future__ import annotations
import json
from pathlib import Path
from statistics import mean, pstdev
from typing import Optional, Union


class PriorityMatrixError(Exception):
    """Исключение ФДЛ: Нарушены граничные условия ортогональности матрицы приоритетов."""
    pass


class PriorityOscillator:
    """Управляет Курсом Приоритетов (КП). 
    Трансформирует 24 направления развития в сбалансированную матрицу 6×6.
    Проверяет систему на отсутствие паразитных мод накопления и двоецентрия.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.matrix_size = 6
        self.directions_count = 24
        self.config_path = config_path
        self.directions_names = self._load_directions_config()

    def _load_directions_config(self) -> list[str]:
        """Загрузка названий 24 направлений. Если файла нет — инициализирует эталонную буквенную матрицу."""
        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if len(data.get("directions", [])) == self.directions_count:
                        return data["directions"]
            except Exception:
                pass
        # Эталонный алфавитно-векторный контур по умолчанию
        return [f"Вектор_{i:02d}_Направление_{chr(1072 + (i % 22))}" for i in range(1, self.directions_count + 1)]

    def build_matrix_6x6(self, vector_payloads: list[float]) -> list[list[float]]:
        """Принимает 24 значения весов ресурсов/усилий от направлений развития, 
        достраивает 2 балансирующих вектора КОСМОСА до размера 36 (матрица 6х6).
        """
        if len(vector_payloads) != self.directions_count:
            raise ValueError(f"Требуется строго {self.directions_count} значений весов для направлений развития.")
        if any(v < 0 for v in vector_payloads):
            raise ValueError("Вес ресурса/усилия не может быть отрицательным.")

        # Расчет балансирующих векторов (закрытие контура наковальни среды)
        total_payload = sum(vector_payloads)
        avg_payload = total_payload / self.directions_count if total_payload > 0 else 1.0

        # Формируем полный массив из 36 элементов для матрицы 6х6
        full_payloads = list(vector_payloads)
        while len(full_payloads) < self.matrix_size * self.matrix_size:
            # Два замыкающих элемента работают как демпферы избыточного давления
            full_payloads.append(round(avg_payload * 0.49, 4))

        # Нарезка плоского массива в ортогональную матрицу 6х6
        matrix = [full_payloads[i:i + self.matrix_size] for i in range(0, len(full_payloads), self.matrix_size)]
        return matrix

    def evaluate_harmony(self, matrix: list[list[float]], tolerance: float = 0.3) -> dict:
        """Диагностика матрицы Курса Приоритетов (КП). 
        Вычисляет дисперсию по строкам (продольные оси) и столбцам (поперечные оси).
        """
        row_sums = [sum(row) for row in matrix]
        col_sums = [sum(matrix[r][c] for r in range(self.matrix_size)) for c in range(self.matrix_size)]

        # Вычисление коэффициента вариации (CV) для проверки ортогонального лада
        all_sums = row_sums + col_sums
        m_val = mean(all_sums)
        std_val = pstdev(all_sums)
        
        harmony_index = std_val / m_val if m_val > 0 else 0.0
        
        # Поиск паразитного двоецентрия (Dia-Vol): если две строки или два столбца 
        # стягивают на себя более 66.6% всего ресурса матрицы
        total_matrix_weight = sum(row_sums)
        max_two_rows = sum(sorted(row_sums, reverse=True)[:2])
        max_two_cols = sum(sorted(col_sums, reverse=True)[:2])
        
        has_parasitic_duality = False
        if total_matrix_weight > 0:
            if (max_two_rows / total_matrix_weight > 0.666) or (max_two_cols / total_matrix_weight > 0.666):
                has_parasitic_duality = True

        status = "HARMONIC_BALANCE"
        if harmony_index > tolerance:
            status = "CRITICAL_DRIFT_WAR"
        if has_parasitic_duality:
            status = "PARASITIC_DUALITY_BLOCK"

        return {
            "matrix_structure": matrix,
            "row_vectors_weight": [round(r, 2) for r in row_sums],
            "col_vectors_weight": [round(c, 2) for c in col_sums],
            "harmony_cv_index": round(harmony_index, 4),
            "parasitic_duality_detected": has_parasitic_duality,
            "course_status": status,
            "note": "Параметр гармонии КП. Превышение допуска или двоецентрие ведет к блокировке по ФДЛ."
        }

    def enforce_course_priorities(self, vector_payloads: list[float], tolerance: float = 0.3) -> dict:
        """Затвор шага 16 Оболочки СВЕТ. 
        Принимает веса, строит матрицу и выносит вердикт о допуске Курса Приоритетов.
        """
        matrix = self.build_matrix_6x6(vector_payloads)
        analysis = self.evaluate_harmony(matrix, tolerance)
        
        if analysis["course_status"] == "PARASITIC_DUALITY_BLOCK":
            raise PriorityMatrixError(
                f"Ошибка КП: Обнаружено паразитное двоецентрие (Dia-Vol)! "
                f"Два узла концентрируют более 66.6% ресурсов. Матрица заблокирована."
            )
        if analysis["course_status"] == "CRITICAL_DRIFT_WAR":
            raise PriorityMatrixError(
                f"Ошибка КП: Коэффициент дисперсии осей {analysis['harmony_cv_index']} > {tolerance}. "
                f"Ресурсный перекос ведет к неизбежному конфликту ячеек. Перераспределите нормы."
            )
            
        return analysis


if __name__ == "__main__":
    print("=== Тестирование модуля Курса Приоритетов 6×6 ===")
    oscillator = PriorityOscillator()

    # Тест 1: Сбалансированный ввод (Эквивалентное распределение по 24 направлениям)
    print("\n--- Тест 1: Гармоничный Курс Приоритетов ---")
    balanced_payloads = [10.0 + (i % 3) for i in range(24)]
    res_balanced = oscillator.enforce_course_priorities(balanced_payloads, tolerance=0.3)
    print(f"Статус КП: {res_balanced['course_status']}")
    print(f"Индекс дисперсии осей: {res_balanced['harmony_cv_index']}")
    print(f"Веса продольных осей (строки): {res_balanced['row_vectors_weight']}")

    # Тест 2: Искусственный перекос и двоецентрие (Попытка эксплуатации/накопления)
    print("\n--- Тест 2: Попытка ввода паразитного двоецентрия ---")
    corrupted_payloads = [1.0] * 24
    corrupted_payloads[0] = 500.0  # Резкая концентрация ресурса в одной точке (Идол накопления)
    corrupted_payloads[1] = 450.0  # Вторая паразитная точка
    
    try:
        oscillator.enforce_course_priorities(corrupted_payloads, tolerance=0.3)
    except PriorityMatrixError as e:
        print(f"Затвор ФДЛ сработал безупречно: {e}")
