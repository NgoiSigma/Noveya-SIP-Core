"""Формальная диалектическая логика (ФДЛ) — исполняемое ядро.

Опора: А. Е. Кашеварова, «Теоретические основы Оболочки СВЕТ» (2019), §1.4–1.6.

Что формализовано:
  * суждение-мнение с видом модальности (8 видов из §1.4.1, пункты «б»–«з»);
  * различие ЛОГИЧЕСКОЙ ИСТИННОСТИ вывода и ДОСТОВЕРНОСТИ (связи с действительностью):
    суждение «правильно» только если верно и то и другое;
  * достоверность зависит от УСЛОВИЙ — условия входят в суждение;
  * различие «противоположности» (между крайностями возможно третье)
    и «противоречия» (третье исключено);
  * цикл Тезис — Антитезис — Синтез с журналом.

Чего движок НЕ делает: он не «изобретает» синтез. Если нужна новая сущность
(единство, породившее новое качество), движок формулирует открытую задачу
и ждёт её от человека (параметр `bridge`).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Iterable, Mapping, Optional

CREDIBLE_THRESHOLD = 0.6  # порог достоверности (рабочая настройка)


class Modality(IntEnum):
    """Виды суждений-мнений. Число — рабочий «вес» при сравнении (настраиваемая эвристика)."""
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
    """Пары предикатов-противоположностей (добро/зло, централизация/децентрализация…)."""

    def __init__(self, pairs: Iterable[tuple[str, str]] = ()):
        self._pairs = {frozenset(p) for p in pairs}

    def add(self, a: str, b: str) -> None:
        self._pairs.add(frozenset((a, b)))

    def are_contrary(self, a: str, b: str) -> bool:
        return frozenset((a, b)) in self._pairs


def conditions_conflict(a: Judgement, b: Judgement) -> bool:
    """Условия конфликтуют, если по общему параметру значения различны."""
    da, db = a.cond, b.cond
    return any(k in db and db[k] != v for k, v in da.items())


def classify(a: Judgement, b: Judgement, contraries: Optional[ContraryRegistry] = None) -> Relation:
    contraries = contraries or ContraryRegistry()
    if a.subject != b.subject:
        return Relation.UNRELATED
    if a.predicate == b.predicate:
        if a.affirmed == b.affirmed:
            return Relation.COMPATIBLE
        return Relation.CONDITIONAL if conditions_conflict(a, b) else Relation.CONTRADICTORY
    if contraries.are_contrary(a.predicate, b.predicate):
        if a.affirmed and b.affirmed:
            return Relation.CONDITIONAL if conditions_conflict(a, b) else Relation.CONTRARY
        return Relation.COMPATIBLE
    return Relation.UNRELATED


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

    def render(self) -> str:
        lines = [
            f"Тезис:     {self.thesis.text()}  ({self.thesis.verdict})",
            f"Антитезис: {self.antithesis.text()}  ({self.antithesis.verdict})",
            f"Связь:     {self.relation.value}",
            f"Синтез:    {self.statement}",
            f"Статус:    {'снят' if self.resolved else 'ОТКРЫТ'} — {self.kind.value}",
        ]
        lines += [f"  ▸ задача: {t}" for t in self.open_tasks]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "kind": self.kind.name, "relation": self.relation.name,
            "thesis": self.thesis.to_dict(), "antithesis": self.antithesis.to_dict(),
            "statement": self.statement, "resolved": self.resolved,
            "new_quality": self.new_quality, "open_tasks": self.open_tasks,
        }


def _strength(j: Judgement) -> float:
    return float(j.modality) + j.credibility  # модальность доминирует, достоверность — тай-брейк


class DialecticCycle:
    """Тезис ↔ Антитезис → Синтез (Δ из CoreSigil Σ-Avatarus)."""

    def __init__(self, contraries: Optional[ContraryRegistry] = None):
        self.contraries = contraries or ContraryRegistry()
        self.ledger: list[Synthesis] = []

    def run(self, thesis: Judgement, antithesis: Judgement, bridge: Optional[str] = None) -> Synthesis:
        rel = classify(thesis, antithesis, self.contraries)
        if rel in (Relation.COMPATIBLE, Relation.UNRELATED):
            s = Synthesis(SynthesisKind.NONE, rel, thesis, antithesis,
                          "Противоречия нет: суждения можно удерживать вместе.", True)
        elif rel is Relation.CONDITIONAL:
            keys = sorted({k for k, _ in thesis.conditions} | {k for k, _ in antithesis.conditions})
            s = Synthesis(
                SynthesisKind.CONDITIONAL_SPLIT, rel, thesis, antithesis,
                f"Оба суждения верны в своих условиях. Граница применимости проходит по: {', '.join(keys)}.",
                True, new_quality="область применимости")
        elif rel is Relation.CONTRARY:
            if bridge:
                s = Synthesis(SynthesisKind.BRIDGE, rel, thesis, antithesis,
                              f"Крайности сняты в единстве: {bridge}", True, new_quality=bridge)
            else:
                s = Synthesis(SynthesisKind.BRIDGE, rel, thesis, antithesis,
                              "Между крайностями возможно третье, но оно не названо.", False,
                              open_tasks=["Назвать единство, стороной которого является каждая крайность "
                                          "(новое качество, которого нет у частей)."])
        else:  # CONTRADICTORY
            if bridge:
                s = Synthesis(SynthesisKind.BRIDGE, rel, thesis, antithesis,
                              f"Противоречие снято уточнением условий/смысла: {bridge}", True, new_quality=bridge)
            else:
                strong, weak = (thesis, antithesis) if _strength(thesis) >= _strength(antithesis) else (antithesis, thesis)
                s = Synthesis(
                    SynthesisKind.PROVISIONAL, rel, thesis, antithesis,
                    f"Предварительно удерживается: «{strong.text()}» (модальность {strong.modality.name}, "
                    f"достоверность {strong.credibility:.2f}); «{weak.text()}» — под сомнением.", False,
                    open_tasks=["Проверить достоверность обоих суждений по обратной связи.",
                                "Найти различающее условие (тогда противоречие станет разделением по условиям)."])
        self.ledger.append(s)
        return s

    def to_json(self) -> str:
        return json.dumps([s.to_dict() for s in self.ledger], ensure_ascii=False, indent=2)
