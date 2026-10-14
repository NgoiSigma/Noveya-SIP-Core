# scripts/lexicon_guard.py
# Σ-FDL::TAURUS-ΣIGIL
# Лексико-смысловой модуль различения, защиты инфополя и фильтрации семантического шума

from __future__ import annotations
import re
import json

class LexiconGuardError(Exception):
    """Исключение ФДЛ: Обнаружен деструктивный симулякр. 
    Требуется обнуление буфера и возврат системы на шаг Тезиса.
    """
    pass

class LexiconGuard:
    """Модуль выявления опасных лексем, подмен, плоских дихотомий и враждебных формулировок.
    Использует регулярные выражения и весовые матрицы семантических векторов для защиты ядра НОВЕЯ.
    """

    def __init__(self):
        # Базовые триггеры из исходного протокола (глобальные симулякры)
        self.base_triggers = {
            "sustainable development": "Прикрытие глобального контроля и сжатия потребления.",
            "inclusive economy": "Перехват субъектности, инклюзия для выживших.",
            "zero ownership": "Сценарий обнуления частной субъектности и суверенитета.",
            "ai regulation": "Искусственная монополия цифровых фарисеев на алгоритмы.",
            "smart society": "Замена живого органического лада на управляемый загон."
        }

        # Жесткие блокирующие маркеры усеченных рамок и эксплуатации (Регулярные выражения)
        self.blocking_patterns = {
            r"рыночн\w*\s+конкуренц\w*": "Ложный двигатель прогресса, ведущий к автоколебательному разносу и войнам.",
            r"оптимизац\w*\s+штат\w*": "Маскировка капиталистической эксплуатации и утилизации человеческого ресурса.",
            r"психологическ\w*\s+девиац\w*": "Попытка подмены системных законов среды на бытовой психоанализ.",
            r"девиац\w*\s+по\s+фрейд\w*": "Усеченная рамка фрейдизма, блокирующая объемное мышление.",
            r"управленческ\w*\s+дефект\w*": "Попытка списать геофизические циклы на случайные ошибки политиков."
        }

        # Семантические векторы (Контекстные ядра). Если в одном фрагменте пересекаются >= 2 токена,
        # скрипт распознает скрытый подлог, даже если заблокированные фразы изменены синонимами.
        self.semantic_clusters = {
            "EXPLOITATION": {"конкуренция", "рынок", "эффективность", "капитал", "сокращение", "реформа", "биомасса"},
            "DIGITAL_PHARISEE": {"чат", "gpt", "усредненный", "ответ", "академический", "штамп", "проверить"}
        }

    def scan(self, text: str) -> dict:
        """Анализирует входящий текст на наличие подозрительных лексем и блоков."""
        findings = {}
        lower_text = text.lower()

        # 1. Поиск по базовым текстовым триггерам
        for key, comment in self.base_triggers.items():
            if key in lower_text:
                findings[key] = f"[WARN] {comment}"

        # 2. Поиск по блокирующим регулярным выражениям
        for pattern, comment in self.blocking_patterns.items():
            if re.search(pattern, lower_text):
                findings[pattern] = f"[CRITICAL_BLOCK] {comment}"

        # 3. Векторный семантический анализ (Пересечение контекстных ядер)
        words = set(re.findall(r'[а-яа-яa-z]+', lower_text))
        for cluster_name, token_set in self.semantic_clusters.items():
            intersection = words.intersection(token_set)
            if len(intersection) >= 3:  # Если найдено 3 и более связанных слов — вектор обнаружен
                findings[f"CLUSTER_{cluster_name}"] = (
                    f"[VECTOR_MATCH] Обнаружено скрытое присутствие усеченного контекста {cluster_name}. "
                    f"Сработавшие маркеры: {list(intersection)}"
                )

        return findings

    def guard_session(self, session, text: str) -> None:
        """Защитный затвор для интеграции в noveya/sip.py.
        Проверяет текст, и при обнаружении критического шума принудительно обнуляет буфер.
        """
        findings = self.scan(text)
        if not findings:
            session.note(text)  # Чистый лог пропускается в буфер
            return

        # Проверяем, есть ли среди находок блокирующие или критические факторы
        has_critical = any("[CRITICAL_BLOCK]" in str(v) or "[VECTOR_MATCH]" in str(v) for v in findings.values())
        
        if has_critical:
            # Протокол «Сердце Чисто»: Обнуление накопленного хаоса
            deleted_count = session.clear_buffer()
            session.mode = "AUTONOMOUS"  # Сброс режима на базовый
            
            error_msg = (
                f"\n[!!!] СРАБОТАЛ ГЕОМЕТРИЧЕСКИЙ ЗАТВОР LEXICON GUARD [!!!]\n"
                f"Обнаружена попытка деструктивной прошивки инфополя.\n"
                f"Маркеры подмены: {json.dumps(findings, ensure_ascii=False, indent=2)}\n"
                f"Системное действие: Из буфера сессии удалено {deleted_count} записей семантического мусора.\n"
                f"Команда: Возврат системы на шаг ТЕЗИСА. Очистите мыслительный аппарат."
            )
            raise LexiconGuardError(error_msg)
        else:
            # Если только легкие предупреждения — фиксируем в лог как варнинг, буфер не бьем
            for k, v in findings.items():
                session.note(f"[WARNING_LOG] {k}: {v}")
            session.note(text)


if __name__ == "__main__":
    # Тестовый запуск модуля в изолированном контуре
    print("=== Тестирование антивирусного фильтра Lexicon Guard ===")
    lg = LexiconGuard()
    
    # Имитируем сессию из sip.py для теста
    class MockSession:
        def __init__(self):
            self.buffer = ["Запись 1: Нормирование ресурсов", "Запись 2: Координация осей"]
            self.mode = "ACTIVE_SYNTHESIS"
        def note(self, text): self.buffer.append(text)
        def clear_buffer(self):
            n = len(self.buffer)
            self.buffer.clear()
            return n

    # Тест 1: Безопасный текст с легким предупреждением
    print("\n--- Тест 1: Проверка базового предупреждения ---")
    sample_1 = "The inclusive economy requires precise analysis."
    print(f"Сканирование: '{sample_1}'")
    print(json.dumps(lg.scan(sample_1), ensure_ascii=False, indent=2))

    # Тест 2: Критический пробой (Попытка навязать рыночную конкуренцию и Фрейда)
    print("\n--- Тест 2: Имитация пробоя матрицы усеченными рамками ---")
    sample_2 = "Нам нужна обычная рыночная конкуренция, чтобы выявить психологические девиации по Фрейду."
    sess = MockSession()
    
    try:
        lg.guard_session(sess, sample_2)
    except LexiconGuardError as e:
        print(e)
        print(f"\nСтатус буфера сессии после атаки: {sess.buffer} (Пусто -> Успешно очищен)")
