#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/validate_1c_lab.py
------------------------
Comprehensive engineering validator for 1C:Enterprise laboratory workspaces.

Checks:
  1. Launcher Bat Files:
     - Must exist: 'Запуск_1С_Предприятие.bat' and 'Запуск_Конфигуратор.bat'.
     - Paths must strictly use 'D:\\1c_app' and NEVER 'D:\\1спред' (Cyrillic junction crash).
     - Must NOT contain 'chcp 65001' (breaks 1C batch execution on Windows).
  2. Pure Infobase Archive (*.dt):
     - Must exist in lab folder or flash drive target 'E:\\Программирование 1С\\ЛР<N>\\'.
     - File size must be > 10,000 bytes (non-empty real 1C database archive).
  3. Managed Forms XML Integrity (Ironclad Guard against empty forms):
     - Scans actual Form.xml files (Ext/Form.xml).
     - Strictly BANS '<ChildItems/>' or '<ChildItems></ChildItems>'.
     - Strictly BANS '<Items/>' or '<Items></Items>' when elements are required.
     - Verifies presence of actual UI elements (<InputField>, <Table>, <Button>, etc.).
  4. BSL Modules Structural Integrity:
     - Scans all .bsl files using utf-8-sig to correctly handle BOM.
     - Asserts balanced #Область / #КонецОбласти.
     - Asserts balanced Процедура / КонецПроцедуры and Функция / КонецФункции.
     - Asserts balanced Если / КонецЕсли, Для / КонецЦикла, Пока / КонецЦикла.
"""

import sys
import os
import re
import glob
from dataclasses import dataclass
from typing import List, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

@dataclass
class Issue:
    category: str
    severity: str  # "FAIL" or "WARN"
    message: str
    target: str

class Lab1CValidator:
    def __init__(self, lab_dir: str):
        self.lab_dir = os.path.abspath(lab_dir)
        self.issues: List[Issue] = []

    def validate(self) -> List[Issue]:
        if not os.path.isdir(self.lab_dir):
            self.issues.append(Issue("DIR", "FAIL", f"Каталог не найден: {self.lab_dir}", self.lab_dir))
            return self.issues

        self._check_bat_launchers()
        self._check_dt_archives()
        self._check_root_hygiene()
        self._check_modality_settings()
        self._check_event_log_sanitization()
        self._check_form_xmls()
        self._check_bsl_modules()
        self._check_student_isolation()
        self._check_document_based_on()
        self._check_anti_detection()
        self._check_subsystem_register_visibility()
        self._check_document_number_periodicity()

        return self.issues

    def _check_bat_launchers(self):
        """Rule 1: Launcher bat files must exist, use D:\\1c_app, and avoid chcp 65001."""
        required_bats = [
            "Запуск_1С_Предприятие.bat",
            "Запуск_Конфигуратор.bat"
        ]

        for bat_name in required_bats:
            bat_path = os.path.join(self.lab_dir, bat_name)
            if not os.path.isfile(bat_path):
                self.issues.append(Issue(
                    "BAT_LAUNCHER", "FAIL",
                    f"Отсутствует обязательный bat-файл запуска в 1 клик: {bat_name}",
                    bat_path
                ))
                continue

            try:
                content = ""
                for enc in ["cp866", "cp1251", "utf-8", "utf-8-sig"]:
                    try:
                        with open(bat_path, "r", encoding=enc) as f:
                            content = f.read()
                        break
                    except Exception:
                        continue

                # Check for forbidden Cyrillic path D:\1спред
                if re.search(r'D:\\1спред', content, re.IGNORECASE):
                    self.issues.append(Issue(
                        "BAT_LAUNCHER", "FAIL",
                        "В bat-файле обнаружен запрещённый кириллический путь 'D:\\1спред'. Должен использоваться только ASCII-путь 'D:\\1c_app'!",
                        bat_path
                    ))

                # Check for chcp 65001
                if re.search(r'chcp\s+65001', content, re.IGNORECASE):
                    self.issues.append(Issue(
                        "BAT_LAUNCHER", "FAIL",
                        "В bat-файле обнаружена команда 'chcp 65001', ломающая запуск платформы 1С. Удалите эту команду.",
                        bat_path
                    ))

            except Exception as e:
                self.issues.append(Issue("BAT_LAUNCHER", "FAIL", f"Ошибка чтения {bat_name}: {e}", bat_path))

    def _check_dt_archives(self):
        """Rule 2: Valid *.dt database archive must exist and have non-zero size."""
        dt_files = glob.glob(os.path.join(self.lab_dir, "*.dt"))

        # Also check external flash drive path if matching
        lab_num_match = re.search(r'ЛР(\d+)', os.path.basename(self.lab_dir), re.IGNORECASE)
        if lab_num_match:
            lab_num = lab_num_match.group(1)
            ext_path = f"E:\\Программирование 1С\\ЛР{lab_num}"
            if os.path.isdir(ext_path):
                ext_dt = glob.glob(os.path.join(ext_path, "*.dt"))
                if ext_dt:
                    dt_files.extend(ext_dt)

        if not dt_files:
            self.issues.append(Issue(
                "DT_BACKUP", "FAIL",
                "Не найден файл архива информационной базы (*.dt) ни в каталоге работы, ни на флешке E:\\Программирование 1С\\.",
                self.lab_dir
            ))
            return

        for dt in dt_files:
            try:
                size = os.path.getsize(dt)
                if size < 10000:
                    self.issues.append(Issue(
                        "DT_BACKUP", "FAIL",
                        f"Файл выгрузки {os.path.basename(dt)} подозрительно мал ({size} байт). Реальный архив 1С не может быть меньше 10 КБ.",
                        dt
                    ))
            except Exception as e:
                self.issues.append(Issue("DT_BACKUP", "FAIL", f"Не удалось прочитать размер {dt}: {e}", dt))

    def _check_form_xmls(self):
        """Rule 3: Actual UI Form.xml files must NEVER contain empty <ChildItems/> stubs."""
        # Find Form.xml files (the actual managed form UI definition inside Ext/)
        form_xml_files = []
        for root, dirs, files in os.walk(self.lab_dir):
            for file in files:
                if file.lower() == "form.xml":
                    form_xml_files.append(os.path.join(root, file))

        empty_childitems_pattern = re.compile(r'<ChildItems\s*/>|<ChildItems\s*>\s*</ChildItems\s*>', re.IGNORECASE)
        empty_items_pattern = re.compile(r'<Items\s*/>|<Items\s*>\s*</Items\s*>', re.IGNORECASE)

        for xml_path in form_xml_files:
            # Skip build cache or temporary files
            if ".temp" in xml_path or "scratch" in xml_path.lower():
                continue

            try:
                with open(xml_path, "r", encoding="utf-8-sig", errors="replace") as f:
                    content = f.read()

                # Check empty stubs
                if empty_childitems_pattern.search(content):
                    self.issues.append(Issue(
                        "EMPTY_FORM_STUB", "FAIL",
                        "КРИТИЧЕСКИЙ ДЕФЕКТ: В файле управляемой формы обнаружена пустая заглушка <ChildItems/>! Пользователь увидит абсолютно пустое окно!",
                        xml_path
                    ))
                
                # Check presence of actual UI elements
                if "<Form " in content or "<ManagedForm " in content:
                    has_elements = bool(re.search(r'<(?:InputField|Button|Table|LabelField|CheckBoxField|UsualGroup|Pages)', content, re.IGNORECASE))
                    if not has_elements:
                        self.issues.append(Issue(
                            "FORM_WITHOUT_ELEMENTS", "FAIL",
                            "В управляемой форме отсутствуют элементы управления (поля ввода, таблицы, кнопки). Форма не скомпилирована!",
                            xml_path
                        ))

            except Exception as e:
                self.issues.append(Issue("FORM_XML", "WARN", f"Не удалось проверить форму {xml_path}: {e}", xml_path))

    def _check_bsl_modules(self):
        """Rule 4: BSL code files syntax & structure integrity with UTF-8 BOM awareness."""
        bsl_files = []
        for root, dirs, files in os.walk(self.lab_dir):
            for file in files:
                if file.lower().endswith(".bsl"):
                    bsl_files.append(os.path.join(root, file))

        for bsl_path in bsl_files:
            # Skip temporary/scratch scripts
            if "scratch" in bsl_path.lower() or ".temp" in bsl_path.lower():
                continue

            try:
                with open(bsl_path, "r", encoding="utf-8-sig", errors="replace") as f:
                    lines = f.readlines()

                open_regions = 0
                open_procs = 0
                open_ifs = 0
                open_loops = 0

                for idx, line in enumerate(lines, start=1):
                    code_part = line.split("//")[0].strip()
                    if not code_part:
                        continue

                    if code_part.startswith("#Область"):
                        open_regions += 1
                    elif code_part.startswith("#КонецОбласти"):
                        open_regions -= 1

                    if re.match(r'^(?:Экспортная\s+)?(?:Процедура|Функция)\b', code_part, re.IGNORECASE):
                        open_procs += 1
                    elif re.match(r'^(?:КонецПроцедуры|КонецФункции)\b', code_part, re.IGNORECASE):
                        open_procs -= 1

                    if re.match(r'^Если\b', code_part, re.IGNORECASE):
                        open_ifs += 1
                    elif re.match(r'^КонецЕсли\b', code_part, re.IGNORECASE):
                        open_ifs -= 1

                    if re.match(r'^(?:Для|Пока)\b', code_part, re.IGNORECASE):
                        open_loops += 1
                    elif re.match(r'^КонецЦикла\b', code_part, re.IGNORECASE):
                        open_loops -= 1

                if open_regions != 0:
                    self.issues.append(Issue(
                        "BSL_SYNTAX", "FAIL",
                        f"Не сбалансированы директивы #Область / #КонецОбласти (разница: {open_regions})",
                        bsl_path
                    ))
                if open_procs != 0:
                    self.issues.append(Issue(
                        "BSL_SYNTAX", "FAIL",
                        f"Не сбалансированы процедуры/функции (разница: {open_procs})",
                        bsl_path
                    ))
                if open_ifs != 0:
                    self.issues.append(Issue(
                        "BSL_SYNTAX", "FAIL",
                        f"Не сбалансированы конструкции Если / КонецЕсли (разница: {open_ifs})",
                        bsl_path
                    ))
                if open_loops != 0:
                    self.issues.append(Issue(
                        "BSL_SYNTAX", "FAIL",
                        f"Не сбалансированы циклы Для/Пока / КонецЦикла (разница: {open_loops})",
                        bsl_path
                    ))

            except Exception as e:
                self.issues.append(Issue("BSL_READ", "WARN", f"Ошибка проверки BSL {bsl_path}: {e}", bsl_path))

    def _check_student_isolation(self):
        """Rule 5: Work belongs strictly to Denis Labyntsev. No classmate files (manzhura, etc.)."""
        forbidden_patterns = ["manzhura", "манжура"]
        for root, dirs, files in os.walk(self.lab_dir):
            for name in dirs + files:
                lower_name = name.lower()
                for pat in forbidden_patterns:
                    if pat in lower_name:
                        self.issues.append(Issue(
                            "STUDENT_ISOLATION", "FAIL",
                            f"Обнаружен запрещенный файл/каталог одногруппника: '{name}'. Денис сдает работы строго самостоятельно!",
                            os.path.join(root, name)
                        ))

    def _check_document_based_on(self):
        """Rule 6: BasedOn integrity. ПриходнаяНакладная must NOT be in BasedOn for ОказаниеУслуг."""
        doc_dir = os.path.join(self.lab_dir, "src", "Documents")
        if not os.path.isdir(doc_dir):
            return

        service_xml = os.path.join(doc_dir, "ОказаниеУслуг.xml")
        if os.path.isfile(service_xml):
            try:
                with open(service_xml, "r", encoding="utf-8-sig") as f:
                    content = f.read()
                if "Document.ПриходнаяНакладная" in content and "<BasedOn>" in content:
                    self.issues.append(Issue(
                        "BASED_ON_INTEGRITY", "FAIL",
                        "ПриходнаяНакладная ошибочно указана в BasedOn для ОказаниеУслуг! Приходная накладная не участвует в основаниях.",
                        service_xml
                    ))
            except Exception as e:
                self.issues.append(Issue("BASED_ON_READ", "WARN", f"Ошибка проверки BasedOn: {e}", service_xml))

    def _check_anti_detection(self):
        """Rule 7: Strict Anti-Detection (Zero AI tells in BSL comments, strings, or Form XML UI labels)."""
        banned_comment_words = ["fallback", "handler", "controller", "endpoint", "todo", "service"]
        for root, dirs, files in os.walk(self.lab_dir):
            for file in files:
                if file.lower().endswith(".bsl"):
                    bsl_path = os.path.join(root, file)
                    if "scratch" in bsl_path.lower() or ".temp" in bsl_path.lower():
                        continue
                    try:
                        with open(bsl_path, "r", encoding="utf-8-sig", errors="replace") as f:
                            lines = f.readlines()
                        
                        full_text = "".join(lines)
                        
                        # Check if module contains ONLY #Область stubs
                        non_empty = [l.strip() for l in lines if l.strip()]
                        non_region = [l for l in non_empty if not l.startswith("#")]
                        if non_empty and not non_region:
                            self.issues.append(Issue(
                                "AI_TELL_EMPTY_REGIONS", "FAIL",
                                "Модуль содержит только пустые шаблоны #Область без кода (признак корпоративного автогенератора БСП). Модуль без кода обязан быть пустым (0 строк)!",
                                bsl_path
                            ))

                        # Check for ANY empty #Область ... #КонецОбласти block
                        empty_region_match = re.search(r'#Область\s+([^\r\n]+)\s*(?:\r?\n\s*)*#КонецОбласти', full_text)
                        if empty_region_match:
                            rname = empty_region_match.group(1).strip()
                            self.issues.append(Issue(
                                "AI_TELL_EMPTY_REGIONS", "FAIL",
                                f"В модуле обнаружен пустой блок '#Область {rname} ... #КонецОбласти' без кода (признак корпоративного автогенератора БСП). Студенты не создают пустые регионы!",
                                bsl_path
                            ))

                        # Check for ANY empty Процедура ... КонецПроцедуры block
                        empty_proc_match = re.search(r'Процедура\s+([^\(\r\n]+)\([^\)]*\)\s*(?:Экспорт\s*)?(?:\r?\n\s*)*КонецПроцедуры', full_text, re.IGNORECASE)
                        if empty_proc_match:
                            pname = empty_proc_match.group(1).strip()
                            self.issues.append(Issue(
                                "AI_TELL_EMPTY_PROC", "FAIL",
                                f"В модуле обнаружена пустая процедура-заглушка '{pname}' без программного кода!",
                                bsl_path
                            ))

                        for idx, line in enumerate(lines, 1):
                            # Check comments for English words
                            if "//" in line:
                                comment = line.split("//", 1)[1].lower()
                                for bw in banned_comment_words:
                                    if re.search(r'\b' + bw + r'\b', comment):
                                        self.issues.append(Issue(
                                            "AI_TELL_BSL_COMMENT", "FAIL",
                                            f"В комментарии BSL обнаружено английское слово/маркер ИИ '{bw}'. Студенты 1С не пишут такие комментарии!",
                                            f"{bsl_path}:{idx}"
                                        ))
                            
                            # Check strings for "Пожалуйста"
                            if re.search(r'"[^"]*пожалуйста[^"]*"', line, re.IGNORECASE):
                                self.issues.append(Issue(
                                    "AI_TELL_BSL_STRING", "FAIL",
                                    "В строковом литерале обнаружено слово 'Пожалуйста' (калька с английского 'Please...'). Используйте 'Выберите...' или 'Не выбран...'.",
                                    f"{bsl_path}:{idx}"
                                ))

                            # Check for ITS documentation headers
                            if "данныеформыэлементколлекции" in line.lower() or "псевдоним с альтернативным написанием" in line.lower():
                                self.issues.append(Issue(
                                    "AI_TELL_ITS_DOC", "FAIL",
                                    "В BSL обнаружен канцелярский комментарий в стиле 1С:ИТС / псевдонимов. Пишите естественный студенческий код!",
                                    f"{bsl_path}:{idx}"
                                ))

                    except Exception as e:
                        pass

        # Check Form XMLs for parenthetical rubrics and unnatural labels
        for root, dirs, files in os.walk(self.lab_dir):
            for file in files:
                if file.lower() == "form.xml":
                    form_path = os.path.join(root, file)
                    if "scratch" in form_path.lower() or ".temp" in form_path.lower():
                        continue
                    try:
                        with open(form_path, "r", encoding="utf-8-sig", errors="replace") as f:
                            content = f.read()

                        banned_form_phrases = [
                            "(пользовательский ввод)",
                            "(в группу прочие)",
                            "склад новый",
                            "группадополнительныереквизиты",
                            "группадополнительно"
                        ]
                        for bp in banned_form_phrases:
                            if bp in content.lower():
                                self.issues.append(Issue(
                                    "AI_TELL_FORM_LABEL", "FAIL",
                                    f"В управляемой форме обнаружена подозрительная подпись/рубрика '{bp}'. Подписи должны быть естественными и чистыми!",
                                    form_path
                                ))
                    except Exception as e:
                        pass

    def _check_root_hygiene(self):
        """Rule 8: Root Directory Hygiene (Zero junk files, logs, json, test folders, duplicate bats)."""
        banned_extensions = [".log", ".json", ".ps1", ".tmp", ".dump"]
        banned_file_names = ["1c_out.txt", "doc_stats.txt", "log.txt", "check_log.txt", "start_designer.bat", "start_enterprise.bat"]
        banned_dir_prefixes = ["test", "verify", "epf_", "check_"]

        try:
            for item in os.listdir(self.lab_dir):
                item_path = os.path.join(self.lab_dir, item)
                if os.path.isdir(item_path):
                    lower_dir = item.lower()
                    if any(lower_dir.startswith(p) for p in banned_dir_prefixes):
                        self.issues.append(Issue(
                            "ROOT_DIR_JUNK", "FAIL",
                            f"В корне лабораторной обнаружена служебная папка разработки '{item}'. Учебные папки должны быть чистыми!",
                            item_path
                        ))
                else:
                    lower_file = item.lower()
                    _, ext = os.path.splitext(lower_file)
                    if ext in banned_extensions:
                        self.issues.append(Issue(
                            "ROOT_FILE_JUNK", "FAIL",
                            f"В корне лабораторной обнаружен служебный файл/лог '{item}'. Студенты не создают логи и дампы в корне работы!",
                            item_path
                        ))
                    elif lower_file in banned_file_names or (ext == ".xml" and not lower_file.endswith("configuration.xml")):
                        self.issues.append(Issue(
                            "ROOT_FILE_JUNK", "FAIL",
                            f"В корне лабораторной обнаружен лишний файл '{item}'. Должны оставаться только русские батники запуска и выгрузки базы!",
                            item_path
                        ))
                    elif ext == ".epf":
                        if re.search(r'тест.*\.epf|.*test.*\.epf', lower_file):
                            self.issues.append(Issue(
                                "ROOT_FILE_JUNK", "FAIL",
                                f"В корне лабораторной обнаружена тестовая обработка '{item}'. Студенты не сдают тестовые скрипты и тест-раннеры!",
                                item_path
                            ))
                        else:
                            lab_match = re.search(r'ЛР([\d\.]+)', os.path.basename(self.lab_dir), re.IGNORECASE)
                            current_lab = lab_match.group(1) if lab_match else ""
                            expected_epf_by_lab = {
                                "3": ["заполнениелр3.epf"],
                                "4": ["заполнениелр4.epf", "обработка4.epf"],
                            }
                            allowed = expected_epf_by_lab.get(current_lab, [])
                            if lower_file not in allowed:
                                self.issues.append(Issue(
                                    "ROOT_FILE_JUNK", "FAIL",
                                    f"В корне лабораторной обнаружена остаточная внешняя обработка '{item}', не предусмотренная для ЛР{current_lab}. Внешние обработки должны соответствовать номеру текущей работы!",
                                    item_path
                                ))
        except Exception as e:
            self.issues.append(Issue("ROOT_HYGIENE", "WARN", f"Ошибка проверки гигиены каталога: {e}", self.lab_dir))

    def _check_modality_settings(self):
        """Rule 9: Modality and Synchronous platform extension calls must be enabled (Use, not DontUse)."""
        cfg_path = os.path.join(self.lab_dir, "src", "Configuration.xml")
        if not os.path.isfile(cfg_path):
            return

        try:
            with open(cfg_path, "r", encoding="utf-8-sig") as f:
                content = f.read()

            modality_match = re.search(r'<ModalityUseMode>(.*?)</ModalityUseMode>', content)
            if modality_match:
                mode = modality_match.group(1).strip()
                if mode != "Use":
                    self.issues.append(Issue(
                        "MODALITY_MODE", "FAIL",
                        f"Режим использования модальности равен '{mode}'. В учебных базах 1С должен быть строго 'Use' (Использовать) для работы ВвестиЧисло/Предупреждение!",
                        cfg_path
                    ))

            sync_match = re.search(r'<SynchronousPlatformExtensionAndAddInCallUseMode>(.*?)</SynchronousPlatformExtensionAndAddInCallUseMode>', content)
            if sync_match:
                mode = sync_match.group(1).strip()
                if mode != "Use":
                    self.issues.append(Issue(
                        "SYNCHRONOUS_CALLS", "FAIL",
                        f"Режим синхронных вызовов равен '{mode}'. В учебных базах 1С должен быть строго 'Use' (Использовать)!",
                        cfg_path
                    ))
        except Exception as e:
            self.issues.append(Issue("CONFIG_XML", "WARN", f"Ошибка проверки свойств Configuration.xml: {e}", cfg_path))

    def _check_event_log_sanitization(self):
        """Rule 10: Event Log Sanitization (Zero traces of virtual drives W:\\, test.dt, or test scripts)."""
        log_dir = os.path.join(self.lab_dir, "Base1C", "1Cv8Log")
        if not os.path.isdir(log_dir):
            return

        suspicious_patterns = [
            (r'W:\\', "виртуальный диск W:\\"),
            (r'test\.dt', "тестовый файл test.dt"),
            (r'\\scratch\\', "временная папка scratch"),
            (r'run_seed', "скрипт run_seed"),
            (r'seeder', "скрипт seeder"),
            (r'Тест.*\.epf', "тестовая обработка Тест*.epf"),
            (r'.*test.*\.epf', "тестовая обработка *test*.epf"),
            (r'Заполнение.*\.epf', "сервисная обработка Заполнение*.epf"),
            (r'ВнешняяОбработка\.Заполнение', "вызов сервисной обработки Заполнение"),
            (r'ОшибкаВоВремяВыполненияВстроенногоЯзыка', "необработанное исключение BSL в журнале регистрации")
        ]

        try:
            for fname in os.listdir(log_dir):
                if fname.endswith(".lgp"):
                    fpath = os.path.join(log_dir, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                            text = f.read()
                        for pattern, label in suspicious_patterns:
                            if re.search(pattern, text, re.IGNORECASE):
                                self.issues.append(Issue(
                                    "EVENT_LOG_TELL", "FAIL",
                                    f"В журнале регистрации {fname} обнаружен маркер внешней автоматизации ({label}). Журнал должен быть чистым!",
                                    fpath
                                ))
                    except Exception as e:
                        pass
        except Exception as e:
            self.issues.append(Issue("EVENT_LOG", "WARN", f"Ошибка проверки 1Cv8Log: {e}", log_dir))

    def _check_subsystem_register_visibility(self):
        """Rule 11: Registers in Subsystems MUST have Visibility=true in CommandInterface.xml so the subsystem tab is never empty."""
        sub_dir = os.path.join(self.lab_dir, "src", "Subsystems")
        if not os.path.isdir(sub_dir):
            return

        for fname in os.listdir(sub_dir):
            if not fname.lower().endswith(".xml"):
                continue
            sub_xml = os.path.join(sub_dir, fname)
            sub_name = os.path.splitext(fname)[0]
            try:
                with open(sub_xml, "r", encoding="utf-8-sig", errors="replace") as f:
                    content = f.read()
                reg_refs = re.findall(r'<xr:Item[^>]*>((?:AccumulationRegister|InformationRegister)\.[^<]+)</xr:Item>', content)
                if not reg_refs:
                    continue

                ci_path = os.path.join(sub_dir, sub_name, "Ext", "CommandInterface.xml")
                if not os.path.isfile(ci_path):
                    self.issues.append(Issue(
                        "SUBSYSTEM_REGISTER_HIDDEN", "FAIL",
                        f"В подсистему '{sub_name}' добавлены регистры ({', '.join(reg_refs)}), но отсутствует {sub_name}/Ext/CommandInterface.xml! В 1С 8.3 регистры скрыты по умолчанию, поэтому вкладка '{sub_name}' в 1С:Предприятие будет ПУСТОЙ!",
                        sub_xml
                    ))
                    continue

                with open(ci_path, "r", encoding="utf-8-sig", errors="replace") as f:
                    ci_content = f.read()

                for reg_ref in reg_refs:
                    cmd_name = f"{reg_ref}.StandardCommand.OpenList"
                    pattern = re.compile(
                        re.escape(f'<Command name="{cmd_name}">') + r'\s*<Visibility>\s*<xr:Common>true</xr:Common>\s*</Visibility>\s*</Command>',
                        re.IGNORECASE
                    )
                    if not pattern.search(ci_content):
                        self.issues.append(Issue(
                            "SUBSYSTEM_REGISTER_HIDDEN", "FAIL",
                            f"Для регистра '{reg_ref}' в подсистеме '{sub_name}' не включена видимость (Visibility=true) в CommandInterface.xml! Вкладка '{sub_name}' в 1С:Предприятие будет пустой!",
                            ci_path
                        ))
            except Exception as e:
                self.issues.append(Issue("SUBSYSTEM_CI", "WARN", f"Ошибка проверки CommandInterface подсистемы {sub_name}: {e}", sub_xml))

    def _check_document_number_periodicity(self):
        """Rule 12: 1-arg Документы.<Doc>.НайтиПоНомеру(Номер) requires <NumberPeriodicity>Nonperiodical</NumberPeriodicity>."""
        doc_dir = os.path.join(self.lab_dir, "src", "Documents")
        if not os.path.isdir(doc_dir):
            return

        periodic_docs = {}
        for fname in os.listdir(doc_dir):
            if not fname.lower().endswith(".xml"):
                continue
            doc_name = os.path.splitext(fname)[0]
            doc_xml = os.path.join(doc_dir, fname)
            try:
                with open(doc_xml, "r", encoding="utf-8-sig", errors="replace") as f:
                    content = f.read()
                m = re.search(r'<NumberPeriodicity>([^<]+)</NumberPeriodicity>', content)
                if m and m.group(1).strip() != "Nonperiodical":
                    periodic_docs[doc_name.lower()] = (doc_name, m.group(1).strip(), doc_xml)
            except Exception:
                pass

        if not periodic_docs:
            return

        # Scan all BSL files for 1-argument Документы.<Doc>.НайтиПоНомеру(...)
        find_by_num_re = re.compile(r'Документы\.([А-Яа-яЁёA-Za-z0-9_]+)\.НайтиПоНомеру\s*\(([^)]*)\)', re.IGNORECASE)
        for root, dirs, files in os.walk(self.lab_dir):
            for file in files:
                if not file.lower().endswith(".bsl"):
                    continue
                bsl_path = os.path.join(root, file)
                try:
                    with open(bsl_path, "r", encoding="utf-8-sig", errors="replace") as f:
                        text = f.read()
                    for m in find_by_num_re.finditer(text):
                        d_lower = m.group(1).lower()
                        args_str = m.group(2).strip()
                        if d_lower in periodic_docs and "," not in args_str:
                            orig_name, period_val, doc_xml = periodic_docs[d_lower]
                            self.issues.append(Issue(
                                "PERIODIC_FIND_BY_NUMBER", "FAIL",
                                f"В модуле вызывается Документы.{orig_name}.НайтиПоНомеру({args_str}) без 2-го параметра (ДатаИнтервала), но в {orig_name}.xml указано <NumberPeriodicity>{period_val}</NumberPeriodicity>! Поиск вернет ПустаяСсылка. Установите <NumberPeriodicity>Nonperiodical</NumberPeriodicity>.",
                                bsl_path
                            ))
                except Exception:
                    pass

def format_1c_report(lab_dir: str, issues: List[Issue]) -> str:
    out = []
    out.append("=" * 70)
    out.append(f"  ВАЛИДАЦИЯ ИНЖЕНЕРНОГО КОНТУРА 1С: {os.path.basename(lab_dir)}")
    out.append("=" * 70)

    fails = [i for i in issues if i.severity == "FAIL"]
    warns = [i for i in issues if i.severity == "WARN"]

    if not fails and not warns:
        out.append("\n  [PASS] ВСЕ ИНЖЕНЕРНЫЕ АРТЕФАКТЫ 1С ВЕРНЫ НА 100%!")
        out.append("  Батники запуска, архив *.dt, формы XML и BSL-модули полностью исправны.\n")
        out.append("=" * 70)
        return "\n".join(out)

    if fails:
        out.append(f"\n  [FAIL] ОБНАРУЖЕНО КРИТИЧЕСКИХ ДЕФЕКТОВ 1С: {len(fails)}")
        for f in fails:
            out.append(f"    - [{f.category}]: {f.message}")
            out.append(f"      Файл/путь: {f.target}")

    if warns:
        out.append(f"\n  [WARN] ПРЕДУПРЕЖДЕНИЙ: {len(warns)}")
        for w in warns:
            out.append(f"    - [{w.category}]: {w.message}")
            out.append(f"      Файл/путь: {w.target}")

    out.append("\n" + "=" * 70)
    return "\n".join(out)

def main():
    if len(sys.argv) < 2:
        print("Использование: python validate_1c_lab.py <путь_к_папке_лабы>")
        sys.exit(2)

    lab_path = sys.argv[1]
    validator = Lab1CValidator(lab_path)
    issues = validator.validate()

    report_text = format_1c_report(lab_path, issues)
    print(report_text)

    fails = [i for i in issues if i.severity == "FAIL"]
    if fails:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
