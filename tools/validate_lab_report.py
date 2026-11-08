#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/validate_lab_report.py
----------------------------
Comprehensive validator for Lab Reports adhering strictly to Denis's college
standard (Group PC02-23).

Invariants enforced:
  1. Pure Plain Text: Zero markdown headings (#), bold (**), italics (*), pipes (|).
  2. Clean Header: Required fields present; BANNED: 'Учащийся', 'Студент', 'Специальность', 'Вариант'.
  3. Task Headings: Strictly single-line 'Задание N. <Text>' without line breaks.
  4. Strict No-Dot Invariant:
     - Introductory reference sentences to figures (... на рисунке N) must NEVER end with a dot.
     - Introductory reference sentences to tables (... в таблице N) must NEVER end with a dot.
     - Introductory reference sentences to listings (... в листинге N) must NEVER end with a dot.
     - Captions ('Рисунок N – ...', 'Таблица N – ...', 'Листинг N – ...') must NEVER end with a dot.
  5. Tables: Columns delimited by tabs; exact line '(таблица из N столбцов и M строк)' required
     immediately under table, with actual row & column counts strictly matching.
     Code listings ('Листинг N') are ignored during table checks.
  6. Dashed Lists: First char lowercase, intermediate items end with ';', final item ends with '.'.
  7. Control Questions: Numbered question followed by 'Ответ: ...'.
  8. Conclusion: Starts with 'Вывод: ', 1 sentence, 1st person past tense verb, no filler phrases.
"""

import sys
import re
import os
from dataclasses import dataclass
from typing import List, Optional, Tuple

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

@dataclass
class ValidationError:
    line_number: int
    rule: str
    message: str
    offending_text: str

class ReportValidator:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.lines: List[str] = []

    def load_file(self) -> bool:
        if not os.path.isfile(self.file_path):
            self.errors.append(ValidationError(0, "FILE_NOT_FOUND", f"Файл не найден: {self.file_path}", ""))
            return False
        
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.lines = f.readlines()
        except UnicodeDecodeError:
            try:
                with open(self.file_path, "r", encoding="cp1251") as f:
                    self.lines = f.readlines()
            except Exception as e:
                self.errors.append(ValidationError(0, "ENCODING_ERROR", f"Не удалось прочитать файл: {e}", ""))
                return False
        return True

    def validate(self) -> Tuple[List[ValidationError], List[ValidationError]]:
        if not self.load_file():
            return self.errors, self.warnings

        self._check_no_markdown()
        self._check_header()
        self._check_task_headings()
        self._check_no_dot_invariants()
        self._check_tables()
        self._check_dashed_lists()
        self._check_control_questions()
        self._check_conclusion()
        self._check_ai_tells()

        return self.errors, self.warnings

    def _check_no_markdown(self):
        """Rule 1: Pure plain text without markdown markup."""
        for idx, line in enumerate(self.lines, start=1):
            stripped = line.strip()
            # Check for markdown headers #, ##, ### (not inside 1C directives like #Область)
            if re.match(r'^#{1,6}\s+', stripped) and not stripped.startswith("#Область") and not stripped.startswith("#КонецОбласти"):
                self.errors.append(ValidationError(
                    idx, "NO_MARKDOWN_HEADERS",
                    "Запрещены Markdown-заголовки (#). Отчёт должен быть в чистом plain text для Word.",
                    stripped
                ))
            
            # Check for bold syntax **text** (excluding code comments like /** or **/)
            if re.search(r'(?<![/\*])\*\*[^\*\s][^\*]*\*\*(?![/\*])', stripped):
                self.errors.append(ValidationError(
                    idx, "NO_MARKDOWN_BOLD",
                    "Запрещено Markdown-выделение жирным (**). Используйте чистый текст.",
                    stripped
                ))
            
            # Check for markdown table delimiters |---|
            if re.search(r'\|[-:]+\|', stripped):
                self.errors.append(ValidationError(
                    idx, "NO_MARKDOWN_TABLES",
                    "Запрещены Markdown-таблицы с разделителями '|'. Таблицы оформляются через табуляцию.",
                    stripped
                ))

    def _check_header(self):
        """Rule 2: Header formatting and banned words."""
        header_limit = min(35, len(self.lines))
        header_text = "".join(self.lines[:header_limit])

        # Check required fields
        required_patterns = [
            (r'Лабораторная\s+работа\s+№\s*\d+', "Лабораторная работа №N"),
            (r'Номер\s+учебной\s+группы:\s*(?:РС02-23|РС\s*02-23|PC02-23)', "Номер учебной группы: РС02-23"),
            (r'Дата\s+выполнения\s+работы:\s*\d{2}\.\d{2}\.\d{4}', "Дата выполнения работы: ДД.ММ.ГГГГ"),
            (r'Тема:\s*.+', "Тема: <название темы>"),
            (r'Цель:\s*.+', "Цель: <формулировка цели>"),
            (r'Оснащение:\s*.+', "Оснащение: <описание оборудования>"),
        ]

        for pattern, label in required_patterns:
            if not re.search(pattern, header_text, re.IGNORECASE):
                self.errors.append(ValidationError(
                    1, "HEADER_MISSING_FIELD",
                    f"В шапке отчёта отсутствует обязательное поле: '{label}'",
                    ""
                ))

        # Check banned words in header metadata lines
        banned_labels = [
            (r'^\s*(?:Учащийся|учащийся)\s*:', "Учащийся"),
            (r'^\s*(?:Студент|студент)\s*:', "Студент"),
            (r'^\s*(?:Специальность|специальность)\s*:', "Специальность"),
            (r'^\s*(?:Вариант|вариант)\s*:', "Вариант"),
        ]
        for idx in range(header_limit):
            line = self.lines[idx].strip()
            for pattern, name in banned_labels:
                if re.search(pattern, line):
                    self.errors.append(ValidationError(
                        idx + 1, "HEADER_BANNED_WORD",
                        f"В шапке отчёта категорически запрещено указывать '{name}' по стандарту РС02-23.",
                        line
                    ))

    def _check_task_headings(self):
        """Rule 3: Task headings strictly single line and strictly sequential (no 'Дополнительное задание')."""
        expected_num = 1
        for idx, line in enumerate(self.lines, start=1):
            stripped = line.strip()
            if re.match(r'^(?:Дополнительн\w*\s+задани\w*|Задани\w*\s+для\s+самостоятельн\w*)', stripped, re.IGNORECASE):
                self.errors.append(ValidationError(
                    idx, "FORBIDDEN_ADDITIONAL_TASK_HEADING",
                    "СТРОГИЙ ЗАПРЕТ: Дополнительные задания считаются продолжением основных заданий со сквозной нумерацией ('Задание N. ...'). Запрещено писать 'Дополнительное задание'!",
                    stripped
                ))
                continue

            match = re.match(r'^Задание\s+(\d+)\.\s*(.*)$', stripped)
            if match:
                task_num = int(match.group(1))
                task_title = match.group(2).strip()
                if task_num != expected_num:
                    self.errors.append(ValidationError(
                        idx, "TASK_NUMBER_SEQUENCE_ERROR",
                        f"Нарушена сквозная нумерация заданий: ожидалось 'Задание {expected_num}.', получено 'Задание {task_num}.'",
                        stripped
                    ))
                expected_num = task_num + 1

                if not task_title:
                    # Look ahead to see if the next line is the continuation of the task title
                    if idx < len(self.lines):
                        next_line = self.lines[idx].strip()
                        if next_line and not next_line.startswith("Задание") and not next_line.startswith("В "):
                            self.errors.append(ValidationError(
                                idx, "TASK_HEADING_BROKEN_LINE",
                                f"Заголовок Задания {task_num} разорван на несколько строк. Должен быть строго в одну строку!",
                                f"{stripped} \\n {next_line}"
                            ))

    def _check_no_dot_invariants(self):
        """Rule 4: Zero trailing dots on references and captions."""
        # References to figures
        ref_fig_pattern = re.compile(r'(?:(?:представлен\w*|показан\w*|приведен\w*|см\.)\s+.*)?\b(?:на\s+рисунк[а-я]+|рисунк[а-я]+)\s+[\d,\sи–\-]+(\.)\s*$', re.IGNORECASE)
        # References to tables
        ref_tab_pattern = re.compile(r'(?:(?:приведен\w*|показан\w*|представлен\w*|см\.)\s+.*)?\b(?:в\s+таблиц[а-я]+|таблиц[а-я]+)\s+[\d,\sи–\-]+(\.)\s*$', re.IGNORECASE)
        # References to listings
        ref_list_pattern = re.compile(r'(?:(?:приведен\w*|показан\w*|представлен\w*|см\.)\s+.*)?\b(?:в\s+листинг[а-я]+|листинг[а-я]+)\s+[\d,\sи–\-]+(\.)\s*$', re.IGNORECASE)

        # Captions
        caption_fig_pattern = re.compile(r'^Рисунок\s+\d+\s*[–—-]\s*.*(\.)\s*$', re.IGNORECASE)
        caption_tab_pattern = re.compile(r'^Таблица\s+\d+\s*[–—-]\s*.*(\.)\s*$', re.IGNORECASE)
        caption_list_pattern = re.compile(r'^Листинг\s+\d+\s*[–—-]\s*.*(\.)\s*$', re.IGNORECASE)

        for idx, line in enumerate(self.lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("Задание "):
                continue

            if ref_fig_pattern.search(stripped):
                self.errors.append(ValidationError(
                    idx, "FORBIDDEN_TRAILING_DOT_FIGURE_REF",
                    "СТРОГИЙ ЗАПРЕТ: Строка-подводка / ссылка на рисунок оканчивается точкой. Точка на конце запрещена!",
                    stripped
                ))
            elif ref_tab_pattern.search(stripped):
                self.errors.append(ValidationError(
                    idx, "FORBIDDEN_TRAILING_DOT_TABLE_REF",
                    "СТРОГИЙ ЗАПРЕТ: Строка-подводка / ссылка на таблицу оканчивается точкой. Точка на конце запрещена!",
                    stripped
                ))
            elif ref_list_pattern.search(stripped):
                self.errors.append(ValidationError(
                    idx, "FORBIDDEN_TRAILING_DOT_LISTING_REF",
                    "СТРОГИЙ ЗАПРЕТ: Строка-подводка / ссылка на листинг оканчивается точкой. Точка на конце запрещена!",
                    stripped
                ))

            if caption_fig_pattern.match(stripped):
                self.errors.append(ValidationError(
                    idx, "FORBIDDEN_TRAILING_DOT_FIGURE_CAPTION",
                    "СТРОГИЙ ЗАПРЕТ: Подпись к рисунку 'Рисунок N – ...' оканчивается точкой. Точка на конце запрещена!",
                    stripped
                ))
            elif caption_tab_pattern.match(stripped):
                self.errors.append(ValidationError(
                    idx, "FORBIDDEN_TRAILING_DOT_TABLE_CAPTION",
                    "СТРОГИЙ ЗАПРЕТ: Подпись к таблице 'Таблица N – ...' оканчивается точкой. Точка на конце запрещена!",
                    stripped
                ))
            elif caption_list_pattern.match(stripped):
                self.errors.append(ValidationError(
                    idx, "FORBIDDEN_TRAILING_DOT_LISTING_CAPTION",
                    "СТРОГИЙ ЗАПРЕТ: Подпись к листингу 'Листинг N – ...' оканчивается точкой. Точка на конце запрещена!",
                    stripped
                ))

    def _check_tables(self):
        """Rule 5: Table tab formatting and row/col counter verification. Excludes code listings."""
        in_table = False
        in_listing = False
        table_start_line = 0
        table_rows = 0
        col_counts = []

        counter_pattern = re.compile(r'^\(таблица\s+из\s+(\d+)\s+столбц\w+\s+и\s+(\d+)\s+строк\w*\)$', re.IGNORECASE)

        for idx, line in enumerate(self.lines, start=1):
            stripped = line.strip()

            # Detect listing start
            if re.match(r'^Листинг\s+\d+\s*[–—-]', stripped):
                in_listing = True
                continue

            # Detect listing end (blank line followed by normal paragraph or next heading)
            if in_listing:
                if stripped.startswith("Задание ") or stripped.startswith("В ") or stripped.startswith("Рисунок ") or stripped.startswith("Таблица "):
                    in_listing = False
                elif not stripped and idx < len(self.lines) and not self.lines[idx].startswith("\t") and not self.lines[idx].startswith(" "):
                    # Next line is non-indented text
                    next_s = self.lines[idx].strip()
                    if next_s and not next_s.startswith("#") and not next_s.startswith("Процедура") and not next_s.startswith("Функция") and not next_s.startswith("Если"):
                        in_listing = False

            if in_listing:
                # Do not treat tabs in code listing as tables
                continue

            # If line contains tab character
            if "\t" in line and not stripped.startswith("(") and not stripped.startswith("Таблица "):
                if not in_table:
                    in_table = True
                    table_start_line = idx
                    table_rows = 0
                    col_counts = []
                
                parts = line.rstrip("\r\n").split("\t")
                col_counts.append(len(parts))
                table_rows += 1
            else:
                if in_table:
                    # Table just finished, check if current line is the counter
                    counter_match = counter_pattern.match(stripped)
                    if counter_match:
                        declared_cols = int(counter_match.group(1))
                        declared_rows = int(counter_match.group(2))
                        actual_cols = max(col_counts) if col_counts else 0
                        actual_rows = table_rows

                        if declared_cols != actual_cols:
                            self.errors.append(ValidationError(
                                idx, "TABLE_COL_COUNT_MISMATCH",
                                f"Несоответствие столбцов таблицы: заявлено {declared_cols}, фактически найдено {actual_cols}",
                                stripped
                            ))
                        if declared_rows != actual_rows:
                            self.errors.append(ValidationError(
                                idx, "TABLE_ROW_COUNT_MISMATCH",
                                f"Несоответствие строк таблицы: заявлено {declared_rows}, фактически найдено {actual_rows}",
                                stripped
                            ))
                    else:
                        self.errors.append(ValidationError(
                            idx, "TABLE_MISSING_COUNTER",
                            "Под таблицей отсутствует обязательная строка подсчёта: '(таблица из N столбцов и M строк)'",
                            f"Таблица строк {table_start_line}-{idx-1}"
                        ))
                    in_table = False

    def _check_dashed_lists(self):
        """Rule 6: Dashed lists syntax (lowercase start, intermediate ;, final .)."""
        idx = 0
        total = len(self.lines)
        while idx < total:
            line = self.lines[idx].strip()
            if line.startswith("- "):
                list_items = []
                while idx < total and self.lines[idx].strip().startswith("- "):
                    list_items.append((idx + 1, self.lines[idx].strip()))
                    idx += 1

                for pos, (item_line_num, item_text) in enumerate(list_items):
                    is_last = (pos == len(list_items) - 1)
                    content = item_text[2:].strip()
                    if not content:
                        continue

                    # Check trailing punctuation
                    if not is_last:
                        if item_text.endswith("."):
                            self.errors.append(ValidationError(
                                item_line_num, "LIST_INTERMEDIATE_HAS_DOT",
                                "Промежуточный пункт списка оканчивается точкой вместо точки с запятой ';'",
                                item_text
                            ))
                        elif not item_text.endswith(";"):
                            self.warnings.append(ValidationError(
                                item_line_num, "LIST_INTERMEDIATE_NO_SEMICOLON",
                                "Промежуточный пункт списка должен оканчиваться на точку с запятой ';'",
                                item_text
                            ))
                    else:
                        # If this last item is a reference to a figure/table/listing, it shouldn't be in a dashed list!
                        if "в листинге" in item_text or "на рисунке" in item_text or "в таблице" in item_text:
                            self.errors.append(ValidationError(
                                item_line_num, "LIST_ITEM_CONTAINS_REFERENCE",
                                "Ссылка на листинг/рисунок/таблицу находится внутри пункта списка. По регламенту РС02-23 строка-подводка оформляется отдельным абзацем без дефиса, строго без точки в конце!",
                                item_text
                            ))
                        elif not item_text.endswith("."):
                            self.errors.append(ValidationError(
                                item_line_num, "LIST_FINAL_NO_DOT",
                                "Последний пункт списка обязан оканчиваться точкой '.'",
                                item_text
                            ))
            else:
                idx += 1

    def _check_control_questions(self):
        """Rule 7: Control questions format and ultra-brief answer length."""
        q_pattern = re.compile(r'^\d+\.\s+.*\?')
        for idx, line in enumerate(self.lines, start=1):
            stripped = line.strip()
            if q_pattern.match(stripped):
                if idx < len(self.lines):
                    next_line = self.lines[idx].strip()
                    if not next_line.startswith("Ответ:"):
                        if idx + 1 < len(self.lines) and self.lines[idx + 1].strip().startswith("Ответ:"):
                            pass
                        else:
                            self.warnings.append(ValidationError(
                                idx, "QUESTION_MISSING_ANSWER",
                                "После контрольного вопроса ожидается строка 'Ответ: ...'",
                                stripped
                            ))
            if stripped.startswith("Ответ:"):
                ans_body = stripped[6:].strip()
                word_count = len(ans_body.split())
                if len(ans_body) > 165 or word_count > 22:
                    self.errors.append(ValidationError(
                        idx, "ANSWER_TOO_LONG",
                        f"Ответ на контрольный вопрос слишком длинный ({word_count} слов, {len(ans_body)} симв.). По правилу Дениса ответы должны быть максимально краткими (5–18 слов) для записи в тетрадь!",
                        stripped
                    ))

        # Also check that figure/listing captions derive from their introductory sentence
        caption_re = re.compile(r'^(Рисунок|Листинг)\s+(\d+)\s*[–—-]\s*(.+)$')
        for idx, line in enumerate(self.lines, start=1):
            stripped = line.strip()
            m = caption_re.match(stripped)
            if m:
                cap_type, cap_num, cap_title = m.group(1), m.group(2), m.group(3).strip()
                # Find preceding non-empty line that is not [Вставить скриншот ...]
                prev_idx = idx - 2
                intro_line = ""
                while prev_idx >= 0:
                    cand = self.lines[prev_idx].strip()
                    if cand and not cand.startswith("[Вставить"):
                        intro_line = cand
                        break
                    prev_idx -= 1
                if intro_line and ("представлен" in intro_line.lower() or "показан" in intro_line.lower() or "приведен" in intro_line.lower()):
                    cap_words = cap_title.lower().split()[:2]
                    intro_words = intro_line.lower().split()[:2]
                    if cap_words and intro_words and cap_words != intro_words:
                        self.errors.append(ValidationError(
                            idx, "CAPTION_MISMATCH_INTRO",
                            f"Подпись '{cap_type} {cap_num} – {cap_title}' не совпадает с началом верхнего предложения-подводки ('{intro_line}'). Подпись должна формироваться напрямую из верхнего предложения!",
                            stripped
                        ))

    def _check_conclusion(self):
        """Rule 8: Conclusion format matching goal, 1 sentence, past tense."""
        found_conclusion = False
        for idx, line in enumerate(self.lines, start=1):
            stripped = line.strip()
            if stripped.startswith("Вывод:"):
                found_conclusion = True
                conclusion_text = stripped[6:].strip()

                if not conclusion_text.endswith("."):
                    self.errors.append(ValidationError(
                        idx, "CONCLUSION_NO_DOT",
                        "Вывод обязан оканчиваться точкой.",
                        stripped
                    ))

                banned_fillers = [
                    "В ходе выполнения",
                    "В результате выполнения",
                    "В ходе работы",
                    "В данной лабораторной работе",
                    "Были выполнены",
                ]
                for filler in banned_fillers:
                    if filler.lower() in conclusion_text.lower():
                        self.errors.append(ValidationError(
                            idx, "CONCLUSION_BANNED_FILLER",
                            f"В выводе запрещено использовать вводные фразы вроде '{filler}'. Пишите строго от 1-го лица по цели работы.",
                            stripped
                        ))

                first_word_match = re.match(r'^([А-ЯЁ][а-яё]+)\b', conclusion_text)
                if first_word_match:
                    verb = first_word_match.group(1)
                    allowed_past_verbs = [
                        "Сформировал", "Исследовал", "Освоил", "Изучил", "Создал",
                        "Разработал", "Получил", "Закрепил", "Применил", "Настроил",
                        "Приобрел", "Ознакомился"
                    ]
                    if verb not in allowed_past_verbs:
                        self.warnings.append(ValidationError(
                            idx, "CONCLUSION_VERB_CHECK",
                            f"Первое слово вывода '{verb}' должно быть глаголом в прошедшем времени 1-го лица (например: Сформировал, Исследовал, Освоил).",
                            stripped
                        ))

        if not found_conclusion:
            self.errors.append(ValidationError(
                len(self.lines), "CONCLUSION_MISSING",
                "В отчёте отсутствует блок 'Вывод: ...'",
                ""
            ))

    def _check_ai_tells(self):
        """Rule 9: Strict Anti-Detection (Zero AI tells, robotic phrasing, or rubric mentions)."""
        banned_stems = [
            ("сгенерир", "Запрещено слово 'сгенерировано/сгенерировать' (палево ИИ). Используйте 'создано', 'разработано', 'сконструировано'."),
            ("генерац", "Запрещено слово 'генерация' (палево ИИ). Используйте 'создание', 'формирование'."),
            ("на оценку", "Запрещено упоминание критериев оценивания ('на оценку 9-10'). Студенты так не пишут."),
            ("повышенного уровня", "Запрещено шаблонное выражение 'повышенного уровня сложности'."),
            ("нейросеть", "Упоминание нейросетей в отчёте недопустимо."),
            ("chatgpt", "Упоминание ChatGPT в отчёте недопустимо."),
            ("языковая модель", "AI-маркер недопустим."),
            ("в данном отчете рассмотрен", "Запрещена канцеляристская преамбула ИИ 'В данном отчете рассмотрен...'."),
            ("пожалуйста", "Запрещено слово 'пожалуйста' в тексте и листингах отчёта (маркер искусственного интеллекта)."),
            ("показатьпредупреждение", "Запрещено 'ПоказатьПредупреждение' в отчёте. В учебных работах 1С используется классическое модальное 'Предупреждение(...)'.")
        ]
        for idx, line in enumerate(self.lines, start=1):
            lower = line.lower()
            for stem, msg in banned_stems:
                if stem in lower:
                    self.errors.append(ValidationError(
                        idx, "AI_TELL_DETECTED",
                        msg,
                        line.strip()
                    ))

def format_report(file_path: str, errors: List[ValidationError], warnings: List[ValidationError]) -> str:
    out = []
    out.append("=" * 70)
    out.append(f"  ВАЛИДАЦИЯ ОТЧЁТА: {os.path.basename(file_path)}")
    out.append("=" * 70)

    if not errors and not warnings:
        out.append("\n  [PASS] ВСЕ ИНВАРИАНТЫ СОБЛЮДЕНЫ НА 100%! ОШИБОК НЕ НАЙДЕНО.")
        out.append("  Текст отчёта полностью готов для копирования в Word по стандарту РС02-23.\n")
        out.append("=" * 70)
        return "\n".join(out)

    if errors:
        out.append(f"\n  [FAIL] ОБНАРУЖЕНО КРИТИЧЕСКИХ ОШИБОК: {len(errors)}")
        for err in errors:
            out.append(f"    - Строка {err.line_number} [{err.rule}]:")
            out.append(f"      {err.message}")
            if err.offending_text:
                out.append(f"      Текст: \"{err.offending_text}\"")

    if warnings:
        out.append(f"\n  [WARN] ПРЕДУПРЕЖДЕНИЙ: {len(warnings)}")
        for warn in warnings:
            out.append(f"    - Строка {warn.line_number} [{warn.rule}]:")
            out.append(f"      {warn.message}")
            if warn.offending_text:
                out.append(f"      Текст: \"{warn.offending_text}\"")

    out.append("\n" + "=" * 70)
    return "\n".join(out)

def main():
    if len(sys.argv) < 2:
        print("Использование: python validate_lab_report.py <путь_к_файлу_отчета>")
        sys.exit(2)

    report_path = sys.argv[1]
    validator = ReportValidator(report_path)
    errors, warnings = validator.validate()

    result_text = format_report(report_path, errors, warnings)
    print(result_text)

    if errors:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
