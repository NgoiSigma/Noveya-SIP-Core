"""Общая модель созидания (СВЕТ, §1.3.1): октаэдр в сфере.

Шесть вершин: Дух (Д) и Творение (Т) — полюса оси РАБОТЫ; на экваторе Сила (С), Вера (В),
Искусство (И), Наука (Н). Радиус вершины 1.0 = вершина на поверхности идеальной сферы.
Противоположные вершины — диалектические пары: Сила↔Вера, Искусство↔Наука, Дух↔Творение.
Полная урегулированность даёт «белый цвет гармонии»; обнуление потенциала труда/духа — «темень».
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

ELEMENTS = {"D": "Дух", "T": "Творение", "S": "Сила", "V": "Вера", "I": "Искусство", "N": "Наука"}
OPPOSITES = (("S", "V"), ("I", "N"), ("D", "T"))


@dataclass
class Octahedron:
    radii: dict[str, float]

    def __post_init__(self):
        if set(self.radii) != set(ELEMENTS):
            raise ValueError(f"Нужны ровно вершины: {sorted(ELEMENTS)}")
        if any(not 0.0 <= r <= 1.0 for r in self.radii.values()):
            raise ValueError("Радиусы должны быть в диапазоне 0..1")

    def balance(self) -> float:
        hi, lo = max(self.radii.values()), min(self.radii.values())
        return 0.0 if hi == 0 else lo / hi

    def harmony(self) -> float:
        return mean(self.radii.values()) * self.balance()

    def state(self) -> str:
        if min(self.radii["D"], self.radii["T"]) < 0.05:
            return "темень: потенциал труда или духа ≈ 0"
        h = self.harmony()
        if h >= 0.9:
            return "белый: гармония"
        if h >= 0.6:
            return "окрашенный: заметные перекосы"
        return "искажённый: сильные перекосы"

    def tensions(self) -> list[tuple[str, str, float]]:
        """Пары (сильная, слабая, разрыв), от большего разрыва к меньшему."""
        out = []
        for a, b in OPPOSITES:
            ra, rb = self.radii[a], self.radii[b]
            strong, weak = (a, b) if ra >= rb else (b, a)
            out.append((strong, weak, round(abs(ra - rb), 4)))
        return sorted(out, key=lambda t: -t[2])

    def suggest_cycles(self, min_gap: float = 0.2) -> list[dict]:
        """Перекосы, достойные цикла ФДЛ: что удерживает перекос и при каких условиях он оправдан."""
        return [{"strong": ELEMENTS[s], "weak": ELEMENTS[w], "gap": g,
                 "question": f"Что удерживает перевес «{ELEMENTS[s]}» над «{ELEMENTS[w]}» и при каких условиях он оправдан?"}
                for s, w, g in self.tensions() if g >= min_gap]
