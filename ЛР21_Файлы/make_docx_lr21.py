#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_docx_lr21.py
------------------
Compiles report_lr21.docx from report_lr21.txt, embeds screenshots, and cleans Word metadata.
"""

import os
import sys
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

sys.path.append(r"d:\1с лабы\tools")
from clean_docx_metadata import clean_docx_metadata

def create_docx():
    doc = Document()
    base_dir = r'd:\1с лабы\ЛР21_Файлы'

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

    report_path = os.path.join(base_dir, 'report_lr21.txt')
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
                if c_strip.startswith('Рисунок ') or c_strip.startswith('Результат ') or c_strip.startswith('Задание ') or c_strip.startswith('[Вставить') or c_strip.startswith('Окно '):
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
            code_run.font.size = Pt(9.5)
            
            pPr = code_p._p.get_or_add_pPr()
            bdr_xml = f'<w:pBdr {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="2" w:color="CCCCCC"/><w:left w:val="single" w:sz="4" w:space="2" w:color="CCCCCC"/><w:bottom w:val="single" w:sz="4" w:space="2" w:color="CCCCCC"/><w:right w:val="single" w:sz="4" w:space="2" w:color="CCCCCC"/></w:pBdr>'
            pPr.append(parse_xml(bdr_xml))
            shd_xml = f'<w:shd {nsdecls("w")} w:fill="F8F9FA"/>'
            pPr.append(parse_xml(shd_xml))
            continue

        if stripped.startswith('[Вставить скриншот '):
            img_name = stripped.replace('[Вставить скриншот ', '').replace(']', '').strip()
            img_path = os.path.join(base_dir, img_name)
            if os.path.exists(img_path):
                img_p = doc.add_paragraph()
                img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                img_p.paragraph_format.space_before = Pt(6)
                img_p.paragraph_format.space_after = Pt(4)
                img_run = img_p.add_run()
                img_run.add_picture(img_path, width=Inches(6.2))
            else:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.2)
                run = p.add_run(stripped)
                run.font.name = 'Times New Roman'
                run.font.size = Pt(11)
                run.font.italic = True
                run.font.color.rgb = RGBColor(100, 100, 100)
            idx += 1
            continue

        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(4)
        
        if stripped.startswith('Лабораторная работа') or stripped.startswith('Выполнение заданий') or stripped.startswith('Задание '):
            p.paragraph_format.space_before = Pt(8)
            run = p.add_run(stripped)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
            run.font.bold = True
        elif stripped.startswith('Рисунок '):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(stripped)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
            run.font.bold = True
        elif stripped.startswith('Вывод:'):
            p.paragraph_format.space_before = Pt(10)
            run = p.add_run(stripped)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
            run.font.bold = True
        elif stripped.startswith('- '):
            p.paragraph_format.left_indent = Inches(0.4)
            run = p.add_run(stripped)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
        else:
            if not (stripped.startswith('Номер учебной группы:') or stripped.startswith('Дата выполнения работы:') or stripped.startswith('Тема:') or stripped.startswith('Цель:') or stripped.startswith('Оснащение:')):
                p.paragraph_format.first_line_indent = Inches(0.49)
            run = p.add_run(stripped)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
            
        idx += 1

    out_path = os.path.join(base_dir, 'report_lr21.docx')
    doc.save(out_path)
    print(f"DOCX created: {out_path} ({os.path.getsize(out_path)} bytes)")
    
    clean_docx_metadata(out_path, student_name="Лабынцев Денис")

if __name__ == '__main__':
    create_docx()
