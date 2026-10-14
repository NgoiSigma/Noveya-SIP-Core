"""Оболочка СВЕТ (система векторов единства типологики) — Акт Творения как конечный автомат.

Источник: А. Е. Кашеварова, «Теоретические основы Оболочки СВЕТ», §1.2 (22 шага, рис. 1).
Акт Творения — последовательность шагов создания системы при отсутствии прототипа.
Автомат не позволяет пропускать шаги, хранит результаты (артефакты) и допускает откат
(обратная связь: переоткрыть шаг — значит аннулировать его и все последующие).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Any, Iterable, Optional, Union


@dataclass(frozen=True)
class Step:
    no: int
    letter: str
    key: str
    title: str
    description: str


STEPS: tuple[Step, ...] = (
    Step(1, "а", "wish_unspoken", "Неизреченное Желание", "Побуждение Творца, окружённого Средой."),
    Step(2, "б", "wish_spoken", "Изреченное желание", "«Хочу создать то-то» — приблизительный замысел проекта."),
    Step(3, "в", "task", "Формулировка задачи", "Рассуждения, приводящие к формулировке задачи."),
    Step(4, "г", "conditions_before", "Условия До (Удо)", "Заинтересованное изучение Среды: комплектность условий нулевого уровня."),
    Step(5, "д", "concept", "Общий Замысел", "Главное осознание; утверждается как Концепция Проекта."),
    Step(6, "е", "goals_1", "Цели Ц1", "1-й уровень деления целей."),
    Step(7, "ё", "structure", "Структурирование замысла", "Деление Общего Замысла с учётом Ц1 в соответствии с традицией Среды."),
    Step(8, "ж", "interest_zones", "Зоны Интересов", "Выявление в структурах Зон Интересов (род/вид)."),
    Step(9, "з", "goals_2", "Цели, 2-й уровень", "Распределение Ц1 по Зонам Интересов и кодировка."),
    Step(10, "и", "directions", "Направления Развития", "Деление структур на подструктуры; нумерация."),
    Step(11, "й", "needs_1", "Потребности, 1-й уровень", "Потребности по каждому Направлению Развития."),
    Step(12, "к", "needs_2", "Потребности, 2-й уровень", "Классификация потребностей по Зонам Интересов; кодировка."),
    Step(13, "л", "means_kinds", "Роды Средств (Ср1)", "Смыслы Родов Средств, 1-й уровень; кодировка."),
    Step(14, "м", "means_types", "Виды Средств (Ср2)", "Виды Средств по Направлениям в зависимости от Родов; кодировка."),
    Step(15, "н", "priority_variants", "Варианты приоритетов", "Варианты Приоритетов и Подприоритетов Направлений Развития."),
    Step(16, "о", "priority_course", "Курс Приоритетов (КП)", "Утверждение одного из вариантов."),
    Step(17, "п", "activity_nodes", "Узлы Деятельности", "Низовое координирование и обратная связь Творцу."),
    Step(18, "р", "programs", "Программы по Направлениям",
         "Пояснительная записка: общая часть; условия; концепция; цели и узел обратной связи; "
         "прогноз последствий; мероприятия со сроками и ответственными."),
    Step(19, "с", "significance", "Значимости Показателей (Зн)",
         "Функции «средств от целей» (ОГПО) и «значимости показателей от потребностей» (КРСО) — "
         "между ними ищется обратно-пропорциональная зависимость."),
    Step(20, "т", "efficiency", "Эффективность (Эф)",
         "Функции «затраты средств» (ЗАТР) и «признание решения»; отчёт об Условиях После (Уп)."),
    Step(21, "у", "sign_model", "Знаковая модель системы (М)", "Модель для учёта, управляющих воздействий, результатов и расчётов эффективности."),
    Step(22, "ф", "launch", "Запуск и отладка", "Запуск системы; гарантийное сопровождение Творцом."),
)
_BY_NO = {s.no: s for s in STEPS}
_BY_KEY = {s.key: s for s in STEPS}
_BY_LETTER = {s.letter: s for s in STEPS}


class OrderError(Exception):
    """Нарушен порядок шагов Акта Творения."""


def resolve_step(ref: Union[int, str]) -> Step:
    if isinstance(ref, int) and ref in _BY_NO:
        return _BY_NO[ref]
    if isinstance(ref, str):
        if ref in _BY_KEY:
            return _BY_KEY[ref]
        if ref in _BY_LETTER:
            return _BY_LETTER[ref]
    raise KeyError(f"Неизвестный шаг: {ref!r}")


def inverse_proportionality_score(pairs: Iterable[tuple[float, float]]) -> float:
    """Коэффициент вариации произведений x·y. Чем ближе к 0, тем ближе связь к y = k/x."""
    prods = []
    for x, y in pairs:
        if x <= 0 or y <= 0:
            raise ValueError("Для проверки обратной пропорциональности нужны положительные значения")
        prods.append(x * y)
    if len(prods) < 2:
        raise ValueError("Нужно минимум две пары значений")
    return pstdev(prods) / mean(prods)


class ActOfCreation:
    def __init__(self, title: str, creator: str = "", tolerance: float = 0.25):
        self.title = title
        self.creator = creator
        self.tolerance = tolerance
        self.artifacts: dict[str, Any] = {}
        self.warnings: list[str] = []

    # --- состояние ---
    def next_step(self) -> Optional[Step]:
        return next((s for s in STEPS if s.key not in self.artifacts), None)

    @property
    def progress(self) -> tuple[int, int]:
        return len(self.artifacts), len(STEPS)

    @property
    def finished(self) -> bool:
        return self.next_step() is None

    # --- действия ---
    def complete(self, step: Union[int, str], payload: Any) -> Optional[Step]:
        s = resolve_step(step)
        nxt = self.next_step()
        if nxt is None:
            raise OrderError("Акт Творения завершён; для правок используйте reopen().")
        if s.no != nxt.no:
            raise OrderError(f"Сейчас шаг {nxt.no} ({nxt.letter}) «{nxt.title}», а не {s.no} ({s.letter}).")
        if payload in (None, "", [], {}, ()):
            raise ValueError("Пустой результат шага не принимается.")
        self._validate(s, payload)
        self.artifacts[s.key] = payload
        return self.next_step()

    def reopen(self, step: Union[int, str]) -> list[str]:
        """Обратная связь: аннулировать шаг и все последующие. Возвращает ключи удалённых артефактов."""
        s = resolve_step(step)
        removed = [t.key for t in STEPS if t.no >= s.no and t.key in self.artifacts]
        for k in removed:
            del self.artifacts[k]
        return removed

    def _validate(self, s: Step, payload: Any) -> None:
        if s.key == "priority_course":
            variants = self.artifacts.get("priority_variants")
            if payload not in variants:
                raise ValueError("Курс Приоритетов должен быть выбран из утверждённых вариантов (шаг 15).")
        if s.key in ("significance", "efficiency") and isinstance(payload, dict) and "pairs" in payload:
            score = inverse_proportionality_score(payload["pairs"])
            payload["inverse_score"] = round(score, 4)
            if score > self.tolerance:
                self.warnings.append(
                    f"Шаг {s.no}: обратная пропорциональность не подтверждена (CV произведений = {score:.2f} > {self.tolerance}).")

    # --- вывод ---
    def report(self) -> str:
        done, total = self.progress
        lines = [f"Акт Творения: «{self.title}» — {done}/{total}"]
        for s in STEPS:
            mark = "✔" if s.key in self.artifacts else "·"
            lines.append(f" {mark} {s.no:>2} ({s.letter}) {s.title}")
        lines += [f" ! {w}" for w in self.warnings]
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps({"title": self.title, "creator": self.creator,
                           "artifacts": self.artifacts, "warnings": self.warnings},
                          ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, raw: str) -> "ActOfCreation":
        data = json.loads(raw)
        act = cls(data["title"], data.get("creator", ""))
        keys = [s.key for s in STEPS]
        got = list(data["artifacts"])
        if got != keys[:len(got)]:
            raise ValueError("Артефакты не образуют непрерывной цепочки шагов с начала Акта.")
        act.artifacts = data["artifacts"]
        act.warnings = data.get("warnings", [])
        return act
