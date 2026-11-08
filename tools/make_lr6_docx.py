#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import docx
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

sys.path.append(os.path.dirname(__file__))
from clean_docx_metadata import clean_docx_metadata

def create_docx():
    doc = Document()

    # Margins (left 20mm, right 10mm, top 20mm, bottom 20mm)
    for section in doc.sections:
        section.top_margin = Inches(0.79)
        section.bottom_margin = Inches(0.79)
        section.left_margin = Inches(0.79)
        section.right_margin = Inches(0.39)

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(14)
    font.color.rgb = RGBColor(0, 0, 0)

    report_path = r'd:\1с лабы\1С_ЛР6_Файлы\report_lr6_1c.txt'
    with open(report_path, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    idx = 0
    total = len(lines)

    while idx < total:
        line = lines[idx]
        stripped = line.strip()
        
        if not stripped:
            idx += 1
            continue
            
        # Code listings
        if stripped.startswith('Листинг '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(stripped)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(13)
            run.font.bold = True
            idx += 1
            
            code_block = []
            while idx < total:
                c_line = lines[idx]
                c_strip = c_line.strip()
                if c_strip.startswith('Рисунок ') or c_strip.startswith('Таблица ') or c_strip.startswith('Задание ') or c_strip.startswith('[Вставить') or c_strip.startswith('В режиме') or c_strip.startswith('На вкладке') or c_strip.startswith('Вывод:'):
                    break
                code_block.append(c_line)
                idx += 1
                
            code_p = doc.add_paragraph()
            code_p.paragraph_format.left_indent = Inches(0.2)
            code_p.paragraph_format.line_spacing = 1.0
            code_p.paragraph_format.space_before = Pt(2)
            code_p.paragraph_format.space_after = Pt(8)
            code_run = code_p.add_run('\n'.join(code_block).strip())
            code_run.font.name = 'Consolas'
            code_run.font.size = Pt(10)
            
            pPr = code_p._p.get_or_add_pPr()
            bdr_xml = f'<w:pBdr {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="2" w:color="CCCCCC"/><w:left w:val="single" w:sz="4" w:space="2" w:color="CCCCCC"/><w:bottom w:val="single" w:sz="4" w:space="2" w:color="CCCCCC"/><w:right w:val="single" w:sz="4" w:space="2" w:color="CCCCCC"/></w:pBdr>'
            pPr.append(parse_xml(bdr_xml))
            shd_xml = f'<w:shd {nsdecls("w")} w:fill="F8F9FA"/>'
            pPr.append(parse_xml(shd_xml))
            continue

        # Regular headings and paragraphs
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(4)
        
        if stripped.startswith('Лабораторная работа') or stripped.startswith('Выполнение заданий') or stripped.startswith('Задание ') or stripped.startswith('Результаты выполнения работы:'):
            p.paragraph_format.space_before = Pt(8)
            run = p.add_run(stripped)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
            run.font.bold = True
        elif stripped.startswith('Рисунок ') or stripped.startswith('Таблица '):
            run = p.add_run(stripped)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(13)
            run.font.bold = True
        elif stripped.startswith('[Вставить скриншот'):
            p.paragraph_format.left_indent = Inches(0.2)
            run = p.add_run(stripped)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(11)
            run.font.italic = True
            run.font.color.rgb = RGBColor(100, 100, 100)
        elif stripped.startswith('Вывод:'):
            p.paragraph_format.space_before = Pt(10)
            run = p.add_run(stripped)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
            run.font.bold = True
        else:
            p.paragraph_format.first_line_indent = Inches(0.49)
            run = p.add_run(stripped)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
            
        idx += 1

    out_path = r'd:\1с лабы\1С_ЛР6_Файлы\report_lr6_1c.docx'
    doc.save(out_path)
    print(f"DOCX created: {out_path} ({os.path.getsize(out_path)} bytes)")

    clean_docx_metadata(out_path, student_name="Лабынцев Денис")
    print(f"Metadata cleaned for: {out_path}")

if __name__ == '__main__':
    create_docx()
