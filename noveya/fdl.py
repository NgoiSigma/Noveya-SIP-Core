"""Формальная диалектическая логика (ФДЛ) — исполняемое ядро НОВЕЯ.

Опора: А. Е. Кашеварова, «Теоретические основы Оболочки СВЕТ» (2019), §1.4–1.6.
Реализован метод комбинаторного поиска антитезисов и расчет матрицы пограничных
состояний для динамической коррекции плавающего баланса триады 49–49–2.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Iterable, Mapping, Optional

CREDIBLE_THRESHOLD = 0.6  # порог достоверности (рабочая настройка)


class Modality(IntEnum):
    FANTASY = 1      # фантазийные — придуманные предметы мысли
    PROJECTING = 2   # проектирующие — целеполагание
    SUPPOSITION = 3  # предположения — прогноз, надежда на получение знаний
    PROBABLE = 4     # вероятные — знание недостоверное по количеству/качеству
    DESCRIPTIVE = 5  # описательные — наблюдаемое знание
    DETECTION = 6    # обнаружения — новое знание, не следующее с необходимостью
    EXISTENCE = 7    # существования — знание о наличии предмета мысли
    NECESSITY = 8    # необходимости — следствие существующих оснований


def _freeze(cond) -> tuple:
    if not cond:
        return ()
    items = cond.items() if isinstance(cond, Mapping) else cond
    return tuple(sorted((str(k), str(v)) for k, v in items))


@dataclass(frozen=True)
class Judgement:
    subject: str
    predicate: str
    affirmed: bool = True
    modality: Modality = Modality.DESCRIPTIVE
    conditions: tuple = ()          # пары (параметр, значение): {"масштаб": "громада"}
    credibility: float = 0.5        # достоверность 0..1
    valid: bool = True              # логическая истинность вывода
    source: str = ""

    def __post_init__(self):
        if not 0.0 <= self.credibility <= 1.0:
            raise ValueError("credibility должна быть в диапазоне 0..1")
        object.__setattr__(self, "conditions", _freeze(self.conditions))

    @property
    def cond(self) -> dict:
        return dict(self.conditions)

    @property
    def is_correct(self) -> bool:
        return self.valid and self.credibility >= CREDIBLE_THRESHOLD

    @property
    def verdict(self) -> str:
        if self.is_correct:
            return "правильное"
        if self.valid:
            return "логически истинное, но недостоверное → неправильное"
        return "логически неверное"

    def text(self) -> str:
        neg = "" if self.affirmed else "не "
        c = ", ".join(f"{k}={v}" for k, v in self.conditions)
        return f"{self.subject} {neg}{self.predicate}" + (f" [{c}]" if c else "")

    def to_dict(self) -> dict:
        return {
            "subject": self.subject, "predicate": self.predicate,
            "affirmed": self.affirmed, "modality": self.modality.name,
            "conditions": self.cond, "credibility": self.credibility,
            "valid": self.valid, "source": self.source, "verdict": self.verdict,
        }


class Relation(Enum):
    UNRELATED = "не связаны"
    COMPATIBLE = "совместимы"
    CONDITIONAL = "различаются условиями"
    CONTRARY = "противоположность (возможно третье)"
    CONTRADICTORY = "противоречие (третье исключено)"


class ContraryRegistry:
    def __init__(self, pairs: Iterable[tuple[str, str]] = ()):
        self._pairs = {frozenset(p) for p in pairs}

    def add(self, a: str, b: str) -> None:
        self._pairs.add(frozenset((a, b)))

    def are_contrary(self, a: str, b: str) -> bool:
        return frozenset((a, b)) in self._pairs


def conditions_conflict(a: Judgement, b: Judgement) -> bool:
    da, db = a.cond, b.cond
    return any(k in db and db[k] != v for k, v in da.items())


def generate_boundary_matrix(a: Judgement, b: Judgement) -> dict:
    """Комбинаторный поиск антитезисов и пересечений условий.
    Выстраивает матрицу пограничных состояний на стыке конфликтующих параметров.
    """
    da, db = a.cond, b.cond
    boundary_matrix = {}
    
    for key, val_a in da.items():
        if key in db and db[key] != val_a:
            boundary_matrix[key] = {
                "state_alpha": val_a,
                "state_beta": db[key],
                "intersection_node": f"граница_{val_a}_vs_{db[key]}",
                "friction_weight": round(abs(a.credibility - b.credibility) + 0.5, 2)
            }
    return boundary_matrix


class SynthesisKind(Enum):
    NONE = "синтез не требуется"
    CONDITIONAL_SPLIT = "разделение по условиям"
    BRIDGE = "единство (третье)"
    PROVISIONAL = "предварительный приоритет"


@dataclass
class Synthesis:
    kind: SynthesisKind
    relation: Relation
    thesis: Judgement
    antithesis: Judgement
    statement: str
    resolved: bool
    new_quality: Optional[str] = None
    open_tasks: list[str] = field(default_factory=list)
    boundary_matrix: dict = field(default_factory=dict)
    triad_coefficients: dict = field(default_factory=dict)  # Корректирующие коэффициенты для sip.py

    def render(self) -> str:
        lines = [
            f"Тезис:     {self.thesis.text()}  ({self.thesis.verdict})",
            f"Антитезис: {self.antithesis.text()}  ({self.antithesis.verdict})",
            f"Связь:     {self.relation.value}",
            f"Синтез:    {self.statement}",
            f"Статус:    {'СНЯТ' if self.resolved else 'ОТКРЫТ'} — {self.kind.value}",
            f"Коэффициенты Триады: {self.triad_coefficients}"
        ]
        if self.boundary_matrix:
            lines.append(f"Матрица пограничных состояний: {json.dumps(self.boundary_matrix, ensure_ascii=False)}")
        lines += [f"  ▸ задача: {t}" for t in self.open_tasks]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "kind": self.kind.name, "relation": self.relation.name,
            "thesis": self.thesis.to_dict(), "antithesis": self.antithesis.to_dict(),
            "statement": self.statement, "resolved": self.resolved,
            "new_quality": self.new_quality, "open_tasks": self.open_tasks,
            "boundary_matrix": self.boundary_matrix,
            "triad_coefficients": self.triad_coefficients
        }


def _strength(j: Judgement) -> float:
    return float(j.modality) + j.credibility


class DialecticCycle:
    def __init__(self, contraries: Optional[ContraryRegistry] = None):
        self.contraries = contraries or ContraryRegistry()
        self.ledger: list[Synthesis] = []

    def run(self, thesis: Judgement, antithesis: Judgement, bridge: Optional[str] = None) -> Synthesis:
        rel = classify(thesis, antithesis, self.contraries)
        matrix = generate_boundary_matrix(thesis, antithesis)
        
        # Базовая матрица коэффициентов Триады (по умолчанию - эталонный лад)
        coeffs = {"logos_weight": 49.0, "chaos_weight": 49.0, "cosmos_tolerance": 5.0}

        if rel in (Relation.COMPATIBLE, Relation.UNRELATED):
            s = Synthesis(SynthesisKind.NONE, rel, thesis, antithesis,
                          "Противоречия нет: суждения можно удерживать вместе.", True,
                          boundary_matrix=matrix, triad_coefficients=coeffs)
                          
        elif rel is Relation.CONDITIONAL:
            keys = sorted({k for k, _ in thesis.conditions} | {k for k, _ in antithesis.conditions})
            # Наличие разделения условий требует калибровки ХАОСА и ЛОГОСА
            coeffs["logos_weight"] = 40.0
            coeffs["chaos_weight"] = 58.0  # Усиление ХАОСа для проработки границ
            s = Synthesis(
                SynthesisKind.CONDITIONAL_SPLIT, rel, thesis, antithesis,
                f"Оба суждения верны в своих условиях. Граница применимости проходит по: {', '.join(keys)}.",
                True, new_quality="область применимости", boundary_matrix=matrix, triad_coefficients=coeffs)
                
        elif rel in (Relation.CONTRARY, Relation.CONTRADICTORY):
            if bridge:
                # Синтез найден (Третье единство) -> Восстановление эталона
                s = Synthesis(
                    SynthesisKind.BRIDGE, rel, thesis, antithesis,
                    f"Противоречие снято через новое качество (Единство): «{bridge}».",
                    True, new_quality=bridge, boundary_matrix=matrix, triad_coefficients=coeffs)
            else:
                # Критический затык: противоречие ОТКРЫТО. Системный сбой.
                # Накапливается паразитное двоецентрие (Дьявол/Dia-Vol). Зажимаем КОСМОС, выводим ХАОС на максимум.
                coeffs["logos_weight"] = 10.0
                coeffs["chaos_weight"] = 88.0  # Экстренное требование аналитической мыследеятельности
                coeffs["cosmos_tolerance"] = 1.0  # Допуск дрейфа сужается до предела
                
                tasks = [f"Найти синтезирующий мост (bridge) для предикатов и пограничной матрицы: {list(matrix.keys())}"]
                s = Synthesis(
                    SynthesisKind.BRIDGE, rel, thesis, antithesis,
                    "Система заблокирована противоречием. Требуется внесение нового качества оператором.",
                    False, open_tasks=tasks, boundary_matrix=matrix, triad_coefficients=coeffs)
                    
        self.ledger.append(s)
        return s


if __name__ == "__main__":
    # Демонстрация комбинаторного поиска антитезисов и расчета пограничной матрицы
    print("=== Тестирование ФДЛ-ядра НОВЕЯ ===")
    
    # Регистрируем противоположность предикатов
    reg = ContraryRegistry([("централизована", "децентрализована")])
    cycle = DialecticCycle(contraries=reg)
    
    # Задаем Тезис (Координация на уровне страны) и Антитезис (Координация на уровне громады)
    t = Judgement("координация", "централизована", conditions={"масштаб": "страна"}, credibility=0.8)
    a = Judgement("координация", "децентрализована", conditions={"масштаб": "громада"}, credibility=0.7)
    
    print("\n1. Запуск цикла БЕЗ моста (Противоречие открыто):")
    res_open = cycle.run(t, a)
    print(res_open.render())
    
print("\n2. Запуск цикла С МОСТОМ (Внесение нового качества - Солидарная Сеть):")
res_resolved = cycle.run(t, a, bridge="Децентрализованная Mesh-сеть 144 ячеек с единым Логосом нормирования")
print(res_resolved.render())
