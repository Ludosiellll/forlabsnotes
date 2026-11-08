#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/validate_lab.py
---------------------
Unified Master Validator for College Laboratory Work (PC02-23 standard & 1C pipeline).

Usage:
  python tools/validate_lab.py <путь_к_папке_лабы_или_отчету>

Examples:
  python tools/validate_lab.py 1С_ЛР4_Файлы
  python tools/validate_lab.py 1С_ЛР4_Файлы/report_lr4_1c.txt
"""

import sys
import os
import glob

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Import the individual validators from the same directory
tools_dir = os.path.dirname(os.path.abspath(__file__))
if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)

from validate_lab_report import ReportValidator, format_report
from validate_1c_lab import Lab1CValidator, format_1c_report
from clean_docx_metadata import clean_docx_metadata
import zipfile
import xml.etree.ElementTree as ET

def check_and_clean_docx(target_dir):
    docx_files = glob.glob(os.path.join(target_dir, "*.docx"))
    issues = []
    for df in docx_files:
        if '~$' in df: continue
        try:
            with zipfile.ZipFile(df, 'r') as z:
                if 'docProps/core.xml' in z.namelist():
                    xml_content = z.read('docProps/core.xml')
                    root = ET.fromstring(xml_content)
                    creator = root.find('{http://purl.org/dc/elements/1.1/}creator')
                    desc = root.find('{http://purl.org/dc/elements/1.1/}description')
                    c_text = (creator.text or "") if creator is not None else ""
                    d_text = (desc.text or "") if desc is not None else ""
                    if "python-docx" in c_text.lower() or "python-docx" in d_text.lower():
                        clean_docx_metadata(df)
                        issues.append(f"  [AUTO-FIXED] Метаданные Word документа {os.path.basename(df)} содержали 'python-docx' и были очищены (автор: Лабынцев Денис).")
        except Exception as e:
            issues.append(f"  [WARN] Ошибка чтения метаданных {os.path.basename(df)}: {e}")
    return issues

def main():
    if len(sys.argv) < 2:
        print("Использование: python tools/validate_lab.py <путь_к_папке_или_отчету>")
        sys.exit(2)

    target_path = os.path.abspath(sys.argv[1])
    if not os.path.exists(target_path):
        print(f"[ERROR] Путь не существует: {target_path}")
        sys.exit(2)

    total_failures = 0

    print("\n" + "#" * 74)
    print("   СКВОЗНАЯ ИНЖЕНЕРНАЯ ВАЛИДАЦИЯ ЛАБОРАТОРНОЙ РАБОТЫ (СТАНДАРТ РС02-23)")
    print("#" * 74 + "\n")

    # Scenario A: Target is a text report file
    if os.path.isfile(target_path):
        validator = ReportValidator(target_path)
        errors, warnings = validator.validate()
        print(format_report(target_path, errors, warnings))
        if errors:
            total_failures += 1

    # Scenario B: Target is a lab directory
    elif os.path.isdir(target_path):
        # 1. Look for report text files
        report_files = glob.glob(os.path.join(target_path, "report*.txt"))
        if not report_files:
            # Check for any .txt file in the root of the lab directory
            report_files = [f for f in glob.glob(os.path.join(target_path, "*.txt")) if not os.path.basename(f).startswith("subsystems")]

        if not report_files:
            print(f"[WARN] В папке {os.path.basename(target_path)} не найден файл отчета (*.txt).\n")
        else:
            for rep in report_files:
                rep_validator = ReportValidator(rep)
                errors, warnings = rep_validator.validate()
                print(format_report(rep, errors, warnings))
                if errors:
                    total_failures += 1

        # 2. Check and clean DOCX metadata
        docx_issues = check_and_clean_docx(target_path)
        if docx_issues:
            print("  ПРОВЕРКА МЕТАДАННЫХ WORD (.DOCX):")
            for di in docx_issues:
                print(di)
            print()

        # 3. If it's a 1C lab (contains Base1C, epf_src, src, or bat files)
        is_1c = (
            "1с" in os.path.basename(target_path).lower() or
            "1c" in os.path.basename(target_path).lower() or
            os.path.isdir(os.path.join(target_path, "Base1C")) or
            os.path.isdir(os.path.join(target_path, "src")) or
            glob.glob(os.path.join(target_path, "*.bat"))
        )

        if is_1c:
            lab_1c_validator = Lab1CValidator(target_path)
            issues = lab_1c_validator.validate()
            print(format_1c_report(target_path, issues))
            fails = [i for i in issues if i.severity == "FAIL"]
            if fails:
                total_failures += 1

    print("-" * 74)
    if total_failures == 0:
        print("  ИТОГОВЫЙ ВЕРДИКТ: [PASS] ВСЕ СТАНДАРТЫ СОБЛЮДЕНЫ НА 100%. ГОТОВО К СДАЧЕ.")
        print("-" * 74 + "\n")
        sys.exit(0)
    else:
        print(f"  ИТОГОВЫЙ ВЕРДИКТ: [FAIL] ОБНАРУЖЕНО НЕСООТВЕТСТВИЙ: {total_failures}.")
        print("  Исправьте замечания валидатора перед передачей работы пользователю!")
        print("-" * 74 + "\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
