"""Оболочка СВЕТ (система векторов единства типологики) — Акт Творения как конечный автомат.

Интегрирован с Триадой ролей (ЛОГОС/ХАОС/КОСМОС) и динамическими допусками баланса 49–49–2.
Автомат блокирует прохождение шагов при нарушении баланса усилий или фазовом смещении среды.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Any, Iterable, Optional, Union

# Импортируем ролевую модель из ядра
from noveya.sip import Role, Triad


@dataclass(frozen=True)
class Step:
    no: int
    letter: str
    key: str
    title: str
    description: str
    responsible_role: Role  # Закрепление ролевой ответственности за шагом по ФДЛ


STEPS: tuple[Step, ...] = (
    Step(1, "а", "wish_unspoken", "Неизреченное Желание", "Побуждение Творца, окружённого Средой.", Role.LOGOS),
    Step(2, "б", "wish_spoken", "Изреченное желание", "«Хочу создать то-то» — приблизительный замысел проекта.", Role.LOGOS),
    Step(3, "в", "task", "Формулировка задачи", "Рассуждения, приводящие к формулировке задачи.", Role.CHAOS),
    Step(4, "г", "conditions_before", "Условия До (Удо)", "Заинтересованное изучение Среды: комплектность условий.", Role.COSMOS),
    Step(5, "д", "concept", "Общий Замысел", "Главное осознание; утверждается как Концепция Проекта.", Role.LOGOS),
    Step(6, "е", "goals_1", "Цели Ц1", "1-й уровень деления целей.", Role.LOGOS),
    Step(7, "ё", "structure", "Структурирование замысла", "Деление Общего Замысла с учётом Ц1.", Role.CHAOS),
    Step(8, "ж", "interest_zones", "Зоны Интересов", "Выявление в структурах Зон Интересов (род/вид).", Role.CHAOS),
    Step(9, "з", "goals_2", "Цели, 2-й уровень", "Распределение Ц1 по Зонам Интересов и кодировка.", Role.LOGOS),
    Step(10, "и", "directions", "Направления Развития", "Деление структур на подструктуры; нумерация.", Role.CHAOS),
    Step(11, "й", "needs_1", "Потребности, 1-й уровень", "Потребности по каждому Направлению Развития.", Role.CHAOS),
    Step(12, "к", "needs_2", "Потребности, 2-й уровень", "Классификация потребностей по Зонам Интересов.", Role.COSMOS),
    Step(13, "л", "means_kinds", "Роды Средств (Ср1)", "Смыслы Родов Средств, 1-й уровень; кодировка.", Role.LOGOS),
    Step(14, "м", "means_types", "Виды Средств (Ср2)", "Виды Средств по Направлениям в зависимости от Родов.", Role.CHAOS),
    Step(15, "н", "priority_variants", "Варианты приоритетов", "Варианты Приоритетов и Подприоритетов.", Role.CHAOS),
    Step(16, "о", "priority_course", "Курс Приоритетов (КП)", "Утверждение одного из вариантов.", Role.COSMOS),
    Step(17, "п", "activity_nodes", "Узлы Деятельности", "Низовое координирование и обратная связь Творцу.", Role.LOGOS),
    Step(18, "р", "programs", "Программы по Направлениям", "Пояснительная записка: условия, концепция, сроки.", Role.CHAOS),
    Step(19, "с", "significance", "Значимости Показателей (Зн)", "Поиск обратно-пропорциональной зависимости (ОГПО/КРСО).", Role.COSMOS),
    Step(20, "т", "efficiency", "Эффективность (Эф)", "Функции «затраты средств» (ЗАТР); отчёт об Условиях После (Уп).", Role.COSMOS),
    Step(21, "у", "sign_model", "Знаковая модель системы (М)", "Модель для учёта, управляющих воздействий и расчётов.", Role.CHAOS),
    Step(22, "ф", "launch", "Запуск и отладка", "Запуск системы; гарантийное сопровождение Творцом.", Role.COSMOS),
)

_BY_NO = {s.no: s for s in STEPS}
_BY_KEY = {s.key: s for s in STEPS}
_BY_LETTER = {s.letter: s for s in STEPS}


class OrderError(Exception):
    """Нарушен порядок шагов Акта Творения или баланс ролей Триады."""


def resolve_step(ref: Union[int, str]) -> Step:
    if isinstance(ref, int) and ref in _BY_NO:
        return _BY_NO[ref]
    if isinstance(ref, str):
        if ref in _BY_KEY:
            return _BY_KEY[ref]
        if ref in _BY_LETTER:
            return _BY_LETTER[ref]
    raise KeyError(f"Неизвестный шаг Оболочки СВЕТ: {ref!r}")


def inverse_proportionality_score(pairs: Iterable[tuple[float, float]]) -> float:
    prods = []
    for x, y in pairs:
        if x <= 0 or y <= 0:
            raise ValueError("Для проверки обратной пропорциональности нужны положительные значения")
        prods.append(x * y)
    if len(prods) < 2:
        raise ValueError("Нужно минимум две пары значений")
    return pstdev(prods) / mean(prods)


class ActOfCreation:
    def __init__(self, title: str, creator: str = "", default_tolerance: float = 0.25):
        self.title = title
        self.creator = creator
        self.inverse_tolerance = default_tolerance
        self.artifacts: dict[str, Any] = {}
        self.warnings: list[str] = []

    def next_step(self) -> Optional[Step]:
        return next((s for s in STEPS if s.key not in self.artifacts), None)

    @property
    def progress(self) -> tuple[int, int]:
        return len(self.artifacts), len(STEPS)

    @property
    def finished(self) -> bool:
        return self.next_step() is None

    def complete(self, step: Union[int, str], payload: Any, triad: Triad, execution_effort: float = 10.0) -> Optional[Step]:
        """Продвижение по конечному автомату Оболочки СВЕТ с проверкой Триады."""
        s = resolve_step(step)
        nxt = self.next_step()
        
        if nxt is None:
            raise OrderError("Акт Творения полностью завершён. Используйте reopen() для правок.")
        if s.no != nxt.no:
            raise OrderError(f"Нарушена последовательность. Сейчас шаг {nxt.no} ({nxt.title}), а не {s.no}.")
        if payload in (None, "", [], {}, ()):
            raise ValueError("Пустой артефакт шага не принимается к нормированию.")
            
        # Автоматическая фиксация мыследеятельности в Триаду перед валидацией шага
        triad.record(s.responsible_role, execution_effort)
        
        # ФДЛ-затвор: Проверка сбалансированности усилий ЛОГОС/ХАОС/КОСМОС перед фиксацией шага
        if not triad.balanced() and s.no > 2:
            # На первых двух шагах («Неизреченное» и «Изреченное») баланс еще не сформирован
            drift_report = triad.drift()
            triad.effort[s.responsible_role] -= execution_effort  # Откат усилия при ошибке
            raise OrderError(
                f"Затвор заблокирован. Триада разбалансирована выше допуска ±{triad.tolerance}%. "
                f"Текущий дрейф векторов: {drift_report}. Сбалансируйте усилия ролей."
            )

        self._validate(s, payload)
        self.artifacts[s.key] = payload
        return self.next_step()

    def reopen(self, step: Union[int, str]) -> list[str]:
        s = resolve_step(step)
        removed = [t.key for t in STEPS if t.no >= s.no and t.key in self.artifacts]
        for k in removed:
            del self.artifacts[k]
        return removed

    def _validate(self, s: Step, payload: Any) -> None:
        if s.key == "conditions_before":
            if not isinstance(payload, dict) or "local_eroi_gradient" not in payload:
                raise ValueError("Шаг 4 (Удо) требует явного указания геодезических параметров локального EROI.")
                
        if s.key == "priority_course":
            variants = self.artifacts.get("priority_variants")
            if payload not in variants:
                raise ValueError("Курс Приоритетов должен быть выбран строго из утверждённых вариантов (шаг 15).")
                
        if s.key in ("significance", "efficiency") and isinstance(payload, dict) and "pairs" in payload:
            score = inverse_proportionality_score(payload["pairs"])
            payload["inverse_score"] = round(score, 4)
            if score > self.inverse_tolerance:
                self.warnings.append(
                    f"Шаг {s.no}: обратная пропорциональность параметров нарушена (CV произведений = {score:.2f} > {self.inverse_tolerance})."
                )

    def report(self) -> str:
        done, total = self.progress
        lines = [f"Оболочка СВЕТ: «{self.title}» — Прогресс: {done}/{total}"]
        for s in STEPS:
            mark = "✔" if s.key in self.artifacts else "·"
            lines.append(f" {mark} {s.no:>2} ({s.letter}) [{s.responsible_role.value}] {s.title}")
        lines += [f" ! Предупреждение: {w}" for w in self.warnings]
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps({
            "title": self.title, 
            "creator": self.creator,
            "artifacts": self.artifacts, 
            "warnings": self.warnings
        }, ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, raw: str) -> "ActOfCreation":
        data = json.loads(raw)
        act = cls(data["title"], data.get("creator", ""))
        keys = [s.key for s in STEPS]
        got = list(data["artifacts"])
        if got != keys[:len(got)]:
            raise ValueError("Цепочка артефактов нарушена или не является непрерывной.")
        act.artifacts = data["artifacts"]
        act.warnings = data.get("warnings", [])
        return act


if __name__ == "__main__":
    # Демонстрация работы затвора автомата СВЕТ
    print("=== Инициализация Акта Творения по методологии НОВЕЯ ===")
    act = ActOfCreation(title="Организация Солидарных Практик", creator="Протоновея")
    
    # Создаем тестовую триаду
    my_triad = Triad(tolerance=5.0)
    
    # Шаг 1: Неизреченное желание (Ответственный: ЛОГОС)
    act.complete(1, payload="Импульс к устранению циклических войн", triad=my_triad, execution_effort=49.0)
    
    # Шаг 2: Изреченное желание (Ответственный: ЛОГОС)
    act.complete(2, payload="Создание платформы НОВЕЯ-СИП", triad=my_triad, execution_effort=49.0)
    
    # Шаг 3: Формулировка задачи (Ответственный: ХАОС). 
    # В этот момент ЛОГОС имеет 98 единиц усилия, ХАОС и КОСМОС по 0. Триада разбалансирована.
    try:
        print("\nПопытка выполнить Шаг 3 без балансировки ролей...")
        act.complete(3, payload="Расчет матрицы 144 ячеек", triad=my_triad, execution_effort=10.0)
    except OrderError as e:
        print(f"Перехват автомата: {e}")
