#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import docx
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
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

    report_path = r'd:\1с лабы\1С_ЛР4_Файлы\report_lr4_1c.txt'
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
            
        # Table detection
        if '\t' in line and not stripped.startswith('('):
            table_lines = []
            while idx < total and '\t' in lines[idx] and not lines[idx].strip().startswith('('):
                table_lines.append(lines[idx].rstrip('\r\n').split('\t'))
                idx += 1
                
            rows_count = len(table_lines)
            cols_count = max(len(r) for r in table_lines)
            
            table = doc.add_table(rows=rows_count, cols=cols_count)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            
            for r_idx, row_data in enumerate(table_lines):
                row = table.rows[r_idx]
                for c_idx, cell_value in enumerate(row_data):
                    cell = row.cells[c_idx]
                    cell.text = cell_value.strip()
                    p = cell.paragraphs[0]
                    p.paragraph_format.line_spacing = 1.0
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.space_before = Pt(2)
                    for run in p.runs:
                        run.font.name = 'Times New Roman'
                        run.font.size = Pt(11)
                        if r_idx == 0:
                            run.font.bold = True
                            
                    tcPr = cell._tc.get_or_add_tcPr()
                    bdr_xml = f'<w:tcBorders {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/></w:tcBorders>'
                    tcPr.append(parse_xml(bdr_xml))
                    if r_idx == 0:
                        shd_xml = f'<w:shd {nsdecls("w")} w:fill="F2F2F2"/>'
                        tcPr.append(parse_xml(shd_xml))
            
            # Counter line after table
            if idx < total and lines[idx].strip().startswith('('):
                counter_p = doc.add_paragraph(lines[idx].strip())
                counter_p.paragraph_format.line_spacing = 1.15
                counter_p.paragraph_format.space_after = Pt(6)
                counter_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                for run in counter_p.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(10)
                    run.font.italic = True
                    run.font.color.rgb = RGBColor(100, 100, 100)
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
                if not c_strip and idx + 1 < total and (lines[idx+1].startswith('Задание ') or lines[idx+1].startswith('В ') or lines[idx+1].startswith('Таблица ') or lines[idx+1].startswith('Рисунок ')):
                    break
                if c_strip.startswith('Рисунок ') or c_strip.startswith('Таблица ') or c_strip.startswith('Задание ') or c_strip.startswith('[Вставить') or (c_strip.startswith('Информационная база') and not c_line.startswith('    ')):
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
        
        if stripped.startswith('Лабораторная работа') or stripped.startswith('Выполнение заданий') or stripped.startswith('Контрольные вопросы') or stripped.startswith('Задание ') or stripped.startswith('Дополнительные задания'):
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

    out_path = r'd:\1с лабы\1С_ЛР4_Файлы\report_lr4_1c.docx'
    doc.save(out_path)
    print(f"DOCX created: {out_path} ({os.path.getsize(out_path)} bytes)")

    clean_docx_metadata(out_path, student_name="Лабынцев Денис")
    print(f"Metadata cleaned for: {out_path}")

if __name__ == '__main__':
    create_docx()
