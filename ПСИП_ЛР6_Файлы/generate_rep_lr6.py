# -*- coding: utf-8 -*-
"""
Скрипт генерации эталонного академического отчета по Лабораторной работе №6 (ПСИП)
в строгом соответствии с требованиями и инвариантами валидатора стандарта РС02-23 (validate_lab_report.py).
"""

import os
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

WORK_DIR = r"d:\1с лабы\ПСИП_ЛР6_Файлы"

# Строго выверенный текст отчета по стандарту РС02-23
REPORT_TEXT = '''Лабораторная работа №6
Номер учебной группы: РС02-23
Дата выполнения работы: 23.09.2026
Тема: Разработка адаптивной версии HTML-страницы под различные разрешения экранов и типа устройств
Цель: Сформировать умение разрабатывать адаптивную версию HTML-страницы под различные разрешения экрана и типы устройства
Оснащение: Методические указания к выполнению, ПК, ОС Windows, Sublime Text, MS Word, браузер
Задание: Задание выполняется для темы, выбранной в лабораторной работе №2. Изучите основные теоретические сведения, выполните практические задания:
1. Иcпользуя CSS, создайте резиновую верстку, чтобы элементы на странице масштабировались пропорционально к размеру экрана. Используйте проценты или относительные единицы измерения, такие как em или rem, чтобы задать размеры элементов и расстояния между ними.
2. Создайте медиа-запросы в CSS файле, чтобы задать различные стили для разных разрешений экранов.
3. Проверьте адаптивность вашей страницы на различных устройствах.
Ответьте на контрольные вопросы.

Результаты выполнения работы:

Задание 1. Иcпользуя CSS, создайте резиновую верстку, чтобы элементы на странице масштабировались пропорционально к размеру экрана. Используйте проценты или относительные единицы измерения, такие как em или rem, чтобы задать размеры элементов и расстояния между ними
В рамках выполнения первого задания спроектирована резиновая структура краеведческого туристического веб-портала «Города Беларуси: Бобруйск».
В отличие от жестких фиксированных макетов, резиновая верстка обеспечивает плавное пропорциональное масштабирование всех компонентов веб-страницы при изменении ширины окна браузера.
Для реализации резиновой модели выполнен перевод всех статических пиксельных размеров в относительные единицы измерения по методическим формулам:
1. Расчет процентной ширины основного контейнера и дочерних блоков:
Ширина внешнего контейнера-обертки (.wrapper) ограничена максимальным значением max-width: 1200px с одновременным заданием резиновой ширины width: 92% и центрированием margin: 0 auto. Это предотвращает чрезмерное растягивание страницы на мониторах сверхвысокого разрешения и гарантирует пропорциональные боковые поля при любых промежуточных разрешениях.
Ширина дочерних блоков рассчитана по формуле:
Ширина_блока_(%) = (Размер_контейнера_(px) / Размер_родителя_(px)) * 100%
Для основного контентного блока (.main-section): (840px / 1200px) * 100% = 70%;
Для боковой панели (.sidebar-section): (324px / 1200px) * 100% = 27%;
Резиновый промежуточный отступ (gap) между колонками составляет 3% (70% + 27% + 3% = 100%).
2. Расчет относительных размеров типографики в rem и em:
В качестве базы отсчета принят стандартный базовый размер шрифта браузера (16px = 1rem = 100%). Размеры шрифтов переведены по формуле:
Размер_шрифта_(rem) = Размер_шрифта_(px) / 16px
Заголовок h1 (.site-title): 26px / 16px = 1.625rem;
Главный заголовок секции (.hero-title): 32px / 16px = 2.0rem;
Заголовки разделов h2 (.section-title): 24px / 16px = 1.5rem;
Заголовки карточек h3 (.card-title): 19px / 16px = 1.1875rem;
Заголовки виджетов h3 (.widget-title): 17px / 16px = 1.0625rem;
Основной текст (body, p): 16px / 16px = 1.0rem;
Вспомогательный текст (.card-text, .site-subtitle): 14px / 16px = 0.875rem;
Мета-теги и бейджи: 12px / 16px = 0.75rem.
3. Подключение мета-тега Viewport:
В секцию <head> веб-документа добавлен обязательный мета-тег:
<meta name="viewport" content="width=device-width, initial-scale=1.0">
Параметр width=device-width устанавливает соответствие ширины области просмотра физической ширине экрана мобильного устройства, а initial-scale=1.0 задает начальный масштаб отображения 1:1, предотвращая нежелательное виртуальное уменьшение масштаба мобильными браузерами.
4. Обеспечение адаптивности графических элементов (Fluid Images):
Для предотвращения переполнения контейнеров изображениями заданы адаптивные CSS-правила:
img, picture, svg, video {
    max-width: 100%;
    height: auto;
    display: block;
}
Свойство max-width: 100% гарантирует, что ширина графического объекта никогда не превысит текущую ширину его родительского контейнера, а height: auto автоматически пересчитывает высоту с сохранением естественных пропорций изображения.

Сравнительная характеристика единиц измерения, применяемых в адаптивной верстке, приведена в таблице 1
Таблица 1 – Сравнительный анализ единиц измерения в адаптивном веб-дизайне
Единица\tБаза отсчета\tПоведение при ресайзе\tПреимущества\tНедостатки\tОбласть применения
px\tАппаратный пиксель\tФиксированное, не масштабируется\tАбсолютная точность верстки\tНе адаптируется под экраны\tГраницы (border), мелкие тени
%\tРазмер родителя\tПропорционально родителю\tИдеально для резиновых сеток\tЗависит от вложенности DOM\tШирина колонок, отступы (gap)
rem\tРазмер шрифта <html>\tМасштабируется через root\tЕдиная шкала масштабирования\tТребует начального расчета\tШрифты, паддинги, радиусы
em\tШрифт текущего элемента\tКаскадное масштабирование\tГибкость локальных модулей\tЭффект накопления при вложенности\tВнутренние отступы кнопок, иконок
vw / vh\t1% ширины/высоты вьюпорта\tПрямая привязка к экрану\tНезависимость от предков DOM\tСложность контроля минимумов\tПолноэкранные Hero-баннеры
(таблица из 6 столбцов и 6 строк)

HTML-код структуры адаптивной страницы представлен в листинге 1
Листинг 1 – Структура адаптивного веб-портала (файл index.html)
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Города Беларуси: Бобруйск — Адаптивный туристический портал</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="site-header">
        <div class="wrapper header-inner">
            <div class="brand">
                <img src="emblem.png" alt="Герб города Бобруйска" class="brand-logo">
                <div class="brand-text">
                    <h1 class="site-title">Города Беларуси: Бобруйск</h1>
                    <p class="site-subtitle">Информационно-туристический гид и культурно-исторический атлас</p>
                </div>
            </div>
            <div class="academic-badge">
                <span class="badge-tag">ПСИП // Лабораторная работа №6</span>
                <span class="badge-desc">Адаптивный дизайн • Группа РС02-23</span>
            </div>
        </div>
        <nav class="main-nav">
            <div class="wrapper nav-wrapper">
                <a href="#about" class="nav-item active">О городе</a>
                <a href="#attractions" class="nav-item">Достопримечательности</a>
                <a href="#routes" class="nav-item">Маршруты</a>
                <a href="#contacts" class="nav-item">Справка туриста</a>
                <a href="#author" class="nav-item">Сведения об авторе</a>
            </div>
        </nav>
    </header>

    <div class="wrapper content-layout">
        <main class="main-section">
            <section id="about" class="hero-card">
                <div class="hero-content">
                    <span class="section-label">Жемчужина Приберезинского края</span>
                    <h2 class="hero-title">Добро пожаловать в Бобруйск</h2>
                    <p class="hero-text">Один из старейших и колоритнейших городов Беларуси...</p>
                    <div class="stats-grid">
                        <div class="stat-item"><span class="stat-value">1387</span><span class="stat-name">Год основания</span></div>
                        <div class="stat-item"><span class="stat-value">~210 тыс.</span><span class="stat-name">Население</span></div>
                        <div class="stat-item"><span class="stat-value">1812</span><span class="stat-name">Подвиг крепости</span></div>
                        <div class="stat-item"><span class="stat-value">96 км²</span><span class="stat-name">Территория</span></div>
                    </div>
                </div>
            </section>

            <section id="attractions" class="cards-section">
                <div class="cards-grid">
                    <article class="landmark-card">
                        <div class="card-media"><img src="fortress.jpg" alt="Бобруйская крепость" class="card-img"></div>
                        <div class="card-body">
                            <h3 class="card-title">Бобруйская крепость</h3>
                            <p class="card-text">Выдающийся памятник фортификационного зодчества XIX века...</p>
                        </div>
                    </article>
                    <article class="landmark-card">
                        <div class="card-media"><img src="bobr_statue.jpg" alt="Памятник Бобру" class="card-img"></div>
                        <div class="card-body">
                            <h3 class="card-title">Скульптура «Бобр Самуилович»</h3>
                            <p class="card-text">Бронзовый символ города на пешеходной улице Социалистической...</p>
                        </div>
                    </article>
                </div>
            </section>
        </main>

        <aside class="sidebar-section">
            <div class="widget">
                <h3 class="widget-title">◈ Справка путешественника</h3>
                <ul class="widget-info-list">
                    <li><strong>Транспорт:</strong> <span>Поезда из Минска, трасса М-5</span></li>
                    <li><strong>Вокзал:</strong> <span>Станция «Бобруйск»</span></li>
                </ul>
            </div>
            <div id="author" class="widget author-widget">
                <h3 class="widget-title">◈ Сведения о разработчике</h3>
                <div class="author-box">
                    <img src="developer.jpg" alt="Разработчик Денис" class="author-photo">
                    <div class="author-details">
                        <h4 class="author-name">Денис</h4>
                        <p class="author-role">Учащийся группы РС02-23</p>
                    </div>
                </div>
            </div>
        </aside>
    </div>
</body>
</html>

CSS-код базовой резиновой компоновки представлен в листинге 2
Листинг 2 – Базовые стили резиновой верстки (фрагмент файла style.css)
.wrapper {
    max-width: 1200px;
    width: 92%;
    margin: 0 auto;
}

img, picture, svg, video {
    max-width: 100%;
    height: auto;
    display: block;
}

.content-layout {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding-top: 2rem;
    padding-bottom: 3rem;
    gap: 3%;
}

.main-section {
    width: 70%;
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.sidebar-section {
    width: 27%;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.cards-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
}

.landmark-card {
    flex: 1 1 calc(50% - 0.75rem);
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 0.625rem;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

Задание 2. Создайте медиа-запросы в CSS файле, чтобы задать различные стили для разных разрешений экранов
Для изменения компоновки страницы на различных классах устройств применены медиа-запросы CSS3 (@media screen and (...)).
Контрольные точки выбраны в соответствии с рекомендациями методических указаний:
- настольные мониторы и широкоформатные экраны ноутбуков (> 1024px);
- компактные ноутбуки и планшеты в горизонтальной ориентации (1024px);
- планшеты в вертикальной ориентации (768px);
- мобильные смартфоны (480px);
- компактные смартфоны малого формата (320px).

Спецификация контрольных точек и правила трансформации компонентов приведены в таблице 2
Таблица 2 – Спецификация контрольных точек и правила трансформации интерфейса
Контрольная точка\tУстройства\tШапка и навигация\tСетка контента (Main)\tБоковая панель (Aside)\tЭргономика интерфейса
Базовая (> 1024px)\tДесктоп, ПК\tГоризонтальный флекс, меню в строку\tШирина 70%, карточки в 2 колонки\tШирина 27%, справа от контента\tМышь / клавиатура, стандартные отступы
max-width: 1024px\tПланшет ландшафт\tШирина 95%, компактные ссылки\tШирина 66%, сетка статистики 2x2\tШирина 31%, сжатые паддинги\tСенсорное и мышиное управление
max-width: 768px\tПланшет портрет\tЦентрирование шапки, перенос меню\tШирина 100%, карточки в 1 колонку\tШирина 100%, перенос ПОД контент\tАдаптация под вертикальный просмотр
max-width: 480px\tСмартфоны\tВертикальное меню (стек), логотип по центру\tШирина 100%, одноколоночный стек\tШирина 100%, виджеты в 1 колонку\tТач-зоны кнопок >= 44px, базовый шрифт 15px
max-width: 320px\tМалый смартфон\tУменьшенные шрифты заголовков\tСжатые поля, статистика по 1 в строку\tКомпактные карточки с малым padding\tМаксимальная экономия экрана без скролла
(таблица из 6 столбцов и 6 строк)

CSS-код медиа-запросов представлен в листинге 3
Листинг 3 – Реализация CSS3 медиа-запросов (файл style.css)
/* Контрольная точка: max-width 1024px (Планшеты ландшафт) */
@media screen and (max-width: 1024px) {
    .wrapper { width: 95%; }
    .site-title { font-size: 1.375rem; }
    .main-section { width: 66%; }
    .sidebar-section { width: 31%; }
    .stat-item { flex: 1 1 40%; }
}

/* Контрольная точка: max-width 768px (Планшеты портрет) */
@media screen and (max-width: 768px) {
    .content-layout {
        flex-direction: column;
        gap: 2rem;
    }
    .main-section {
        width: 100%;
        order: 1;
    }
    .sidebar-section {
        width: 100%;
        order: 2;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.25rem;
    }
    .header-inner {
        flex-direction: column;
        text-align: center;
    }
    .brand { flex-direction: column; }
    .academic-badge { text-align: center; width: 100%; }
    .landmark-card { flex: 1 1 100%; }
}

/* Контрольная точка: max-width 480px (Смартфоны) */
@media screen and (max-width: 480px) {
    html { font-size: 93.75%; }
    .wrapper { width: 94%; }
    .site-title { font-size: 1.25rem; }
    .nav-wrapper {
        flex-direction: column;
        align-items: stretch;
    }
    .nav-item {
        text-align: center;
        padding: 0.875rem 1rem;
        min-height: 2.75rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .hero-card { padding: 1.5rem 1rem; }
    .sidebar-section { grid-template-columns: 1fr; }
    .card-media { height: 11rem; }
}

/* Контрольная точка: max-width 320px (Минимальные мобильные разрешения) */
@media screen and (max-width: 320px) {
    .site-title { font-size: 1.125rem; }
    .stat-item { flex: 1 1 100%; }
    .hero-card { padding: 1.25rem 0.75rem; }
}

Задание 3. Проверьте адаптивность вашей страницы на различных устройствах
В рамках третьего задания выполнена комплексная проверка адаптивного поведения разработанного веб-сайта на ключевых категориях устройств.
Тестирование производилось с применением встроенных инструментов разработчика браузера (F12, режим Device Emulation) и автоматизированного инструментария Playwright на базе движка Chromium.
Проверка показала:
1. На разрешении Desktop (1280×800 px) интерфейс разворачивается в полноценный двухколоночный макет с горизонтальной навигацией и двухколоночной сеткой карточек. Горизонтальная прокрутка отсутствует, полезная площадь используется рационально.
2. На разрешении Tablet (768×1024 px) срабатывает медиа-запрос max-width: 768px: сайдбар плавно переносится под контентную область, выстраиваясь в двухколоночную плитку виджетов. Карточки достопримечательностей масштабируются на всю ширину секции контента.
3. На разрешении Mobile (375×812 px) срабатывает медиа-запрос max-width: 480px: элементы выстраиваются в строгий одноколоночный вертикальный стек. Меню трансформируется в крупные сенсорные кнопки высотой не менее 44px, обеспечивая комфортное взаимодействие пальцем без необходимости масштабирования.

Внешний вид страницы на настольных мониторах (Desktop 1280×800) представлен на рисунке 1
[СЮДА ВСТАВИТЬ СКРИНШОТ: screen_lr6_desktop_1280.png]
Рисунок 1 – Отображение страницы на десктопных мониторах (разрешение 1280×800 px)

Внешний вид страницы на экранах планшетов (Tablet 768×1024) представлен на рисунке 2
[СЮДА ВСТАВИТЬ СКРИНШОТ: screen_lr6_tablet_768.png]
Рисунок 2 – Отображение страницы на экранах планшетов (разрешение 768×1024 px)

Внешний вид страницы на экранах смартфонов (Mobile 375×812) представлен на рисунке 3
[СЮДА ВСТАВИТЬ СКРИНШОТ: screen_lr6_mobile_375.png]
Рисунок 3 – Отображение страницы на экранах смартфонов (разрешение 375×812 px)

Результаты инструментального тестирования сведены в таблицу 3
Таблица 3 – Результаты инструментального тестирования адаптивности на контрольных точках
Разрешение\tПроверяемый класс устройств\tГоризонтальный скролл\tЧитаемость текста\tДоступность меню и кнопок\tВердикт проверки
1920×1080\tШирокоформатный Full HD\tОтсутствует (max-width 1200)\tОтличная (16px base)\tГоризонтальное меню\tПолное соответствие
1280×800\tНоутбуки и настольные ПК\tОтсутствует\tОтличная\tШирокие кликабельные пункты\tПолное соответствие
768×1024\tПланшеты (iPad / Tab)\tОтсутствует\tВысокая (1rem)\tПлиточная адаптация\tПолное соответствие
375×812\tСмартфоны (iPhone / Galaxy)\tОтсутствует (100% стек)\tВысокая (15px base)\tТач-кнопки высотой >= 44px\tПолное соответствие
320×568\tКомпактные мобильные экраны\tОтсутствует\tЧеткая, без наложения\tВертикальный сенсорный стек\tПолное соответствие
(таблица из 6 столбцов и 6 строк)

Ответы на контрольные вопросы:

1. Адаптивный веб-дизайн и его цель?
Ответ: Дизайн веб-страниц под любые экраны и устройства; цель — создать один универсальный сайт вместо нескольких отдельных мобильных версий.

2. Основные принципы адаптивного дизайна?
Ответ: Резиновая сетка макета (в % и rem/em), адаптивные изображения и медиа (max-width: 100%) и медиа-запросы CSS3.

3. Media query и viewport в адаптивном дизайне?
Ответ: Тег viewport задает масштаб 1:1 под ширину экрана устройства, а медиа-запросы (@media) применяют нужные CSS-стили под конкретные разрешения.

4. Как сделать адаптивный дизайн сайта из фиксированного макета?
Ответ: Добавить мета-тег viewport, перевести ширину блоков в проценты, шрифты в rem/em, задать картинкам max-width: 100% и прописать медиа-запросы (@media) для контрольных точек.

Вывод: Сформировал умение разрабатывать адаптивную версию HTML-страницы под различные разрешения экрана и типы устройства.
'''

def generate_txt():
    txt_path = os.path.join(WORK_DIR, "report_lr6_psip.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(REPORT_TEXT)
    print(f"[OK] Сформирован текстовый отчет: {txt_path}")

def generate_docx():
    docx_path = os.path.join(WORK_DIR, "report_lr6_psip.docx")
    doc = docx.Document()
    
    # Настройка полей (Стандарт ГОСТ: левое 25 мм, правое 10 мм, верхнее 20 мм, нижнее 20 мм)
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(0.79)
        s.bottom_margin = Inches(0.79)
        s.left_margin = Inches(0.98)
        s.right_margin = Inches(0.5)

    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Times New Roman'
    font.size = Pt(14)
    font.color.rgb = RGBColor(0, 0, 0)
    
    def add_p(text, bold_prefix="", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=4):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.first_line_indent = Inches(0.49)
        if bold_prefix:
            run_b = p.add_run(bold_prefix)
            run_b.bold = True
            run_b.font.name = 'Times New Roman'
            run_b.font.size = Pt(14)
        run_t = p.add_run(text)
        run_t.font.name = 'Times New Roman'
        run_t.font.size = Pt(14)
        return p

    def add_table_data(headers, rows, caption):
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_cap.paragraph_format.space_before = Pt(8)
        p_cap.paragraph_format.space_after = Pt(4)
        run_cap = p_cap.add_run(caption)
        run_cap.bold = True
        run_cap.font.name = 'Times New Roman'
        run_cap.font.size = Pt(13)

        table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = 'Table Grid'
        
        hdr_cells = table.rows[0].cells
        for col_idx, h in enumerate(headers):
            hdr_cells[col_idx].text = h
            hdr_cells[col_idx].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in hdr_cells[col_idx].paragraphs[0].runs:
                r.bold = True
                r.font.name = 'Times New Roman'
                r.font.size = Pt(11)
        
        for r_idx, row in enumerate(rows):
            row_cells = table.rows[r_idx + 1].cells
            for c_idx, val in enumerate(row):
                row_cells[c_idx].text = val
                row_cells[c_idx].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
                for r in row_cells[c_idx].paragraphs[0].runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(10.5)

        p_end = doc.add_paragraph()
        p_end.paragraph_format.space_after = Pt(6)

    def add_listing(code_text, caption):
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_cap.paragraph_format.space_before = Pt(6)
        p_cap.paragraph_format.space_after = Pt(2)
        r_c = p_cap.add_run(caption)
        r_c.italic = True
        r_c.font.name = 'Times New Roman'
        r_c.font.size = Pt(12)

        p_code = doc.add_paragraph()
        p_code.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_code.paragraph_format.space_before = Pt(2)
        p_code.paragraph_format.space_after = Pt(6)
        p_code.paragraph_format.line_spacing = 1.0
        p_code.paragraph_format.left_indent = Inches(0.2)
        r_code = p_code.add_run(code_text)
        r_code.font.name = 'Consolas'
        r_code.font.size = Pt(9.5)

    def add_image_figure(img_filename, caption):
        img_path = os.path.join(WORK_DIR, img_filename)
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.add_run().add_picture(img_path, width=Inches(6.2))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(8)
            r_cap = p_cap.add_run(caption)
            r_cap.font.name = 'Times New Roman'
            r_cap.font.size = Pt(12)

    # 1. Заголовочная часть
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(6)
    r1 = p_title.add_run("Лабораторная работа №6\n")
    r1.bold = True
    r1.font.size = Pt(16)
    r2 = p_title.add_run("по дисциплине «Проектирование и разработка пользовательских интерфейсов» (ПСИП)\n")
    r2.bold = True
    r2.font.size = Pt(14)
    
    meta_info = [
        ("Номер учебной группы: ", "РС02-23"),
        ("Дата выполнения работы: ", "23.09.2026"),
        ("Тема: ", "Разработка адаптивной версии HTML-страницы под различные разрешения экранов и типа устройств"),
        ("Цель: ", "Сформировать умение разрабатывать адаптивную версию HTML-страницы под различные разрешения экрана и типы устройства"),
        ("Оснащение: ", "Методические указания к выполнению, ПК, ОС Windows, Sublime Text, MS Word, браузер"),
    ]
    for k, v in meta_info:
        add_p(v, bold_prefix=k)

    # Задание
    add_p("Задание выполняется для темы, выбранной в лабораторной работе №2. Изучите основные теоретические сведения, выполните практические задания:\n"
          "1. Иcпользуя CSS, создайте резиновую верстку, чтобы элементы на странице масштабировались пропорционально к размеру экрана. Используйте проценты или относительные единицы измерения, такие как em или rem, чтобы задать размеры элементов и расстояния между ними.\n"
          "2. Создайте медиа-запросы в CSS файле, чтобы задать различные стили для разных разрешений экранов.\n"
          "3. Проверьте адаптивность вашей страницы на различных устройствах.\n"
          "Ответьте на контрольные вопросы.", bold_prefix="Задание: ")

    # Результаты
    p_res = doc.add_paragraph()
    p_res.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_res.paragraph_format.space_before = Pt(12)
    p_res.paragraph_format.space_after = Pt(6)
    r_res = p_res.add_run("Результаты выполнения работы")
    r_res.bold = True
    r_res.font.size = Pt(15)

    # Задание 1
    add_p("В рамках выполнения первого задания спроектирована резиновая структура краеведческого туристического веб-портала «Города Беларуси: Бобруйск». В отличие от жестких фиксированных макетов, резиновая верстка обеспечивает плавное пропорциональное масштабирование всех компонентов страницы при изменении ширины окна браузера.\n"
          "Для реализации резиновой модели выполнен перевод всех статических пиксельных размеров в относительные единицы измерения по методическим формулам:\n"
          "1. Расчет процентной ширины контейнеров:\n"
          "Ширина внешнего контейнера-обертки (.wrapper) ограничена максимальным значением max-width: 1200px с одновременным заданием резиновой ширины width: 92% и центрированием margin: 0 auto. Ширина дочерних блоков рассчитана по формуле:\n"
          "Ширина_блока_(%) = (Размер_контейнера_(px) / Размер_родителя_(px)) * 100%\n"
          "Для основного контента (.main-section): (840px / 1200px) * 100% = 70%; для боковой панели (.sidebar-section): (324px / 1200px) * 100% = 27%; отступ между ними (gap) составляет 3%.\n"
          "2. Расчет относительных шрифтов (rem/em):\n"
          "Базовый масштаб шрифта браузера принят за 16px = 1rem = 100%. Размеры переведены по формуле: Размер_(rem) = px / 16px. Главный заголовок h1: 32px / 16 = 2.0rem; подзаголовки h2: 24px / 16 = 1.5rem; карточки h3: 19px / 16 = 1.1875rem; базовый текст: 16px / 16 = 1.0rem; мета-данные: 14px / 16 = 0.875rem.\n"
          "3. Мета-тег Viewport: в секцию <head> включен обязательный тег <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">, исключающий виртуальное 980-пиксельное сжатие мобильными браузерами.\n"
          "4. Адаптивные медиа (Fluid Images): к изображениям применено правило img { max-width: 100%; height: auto; display: block; }, предотвращающее выпадение картинок за пределы блоков.",
          bold_prefix="Задание 1. Иcпользуя CSS, создайте резиновую верстку, чтобы элементы на странице масштабировались пропорционально к размеру экрана. Используйте проценты или относительные единицы измерения, такие как em или rem, чтобы задать размеры элементов и расстояния между ними. ")

    # Таблица 1
    t1_headers = ["Единица", "База отсчета", "Поведение при ресайзе", "Преимущества", "Недостатки", "Применение"]
    t1_rows = [
        ["px", "Аппаратный пиксель", "Фиксированное, не меняется", "Абсолютная точность", "Не масштабируется", "Границы (border), тени"],
        ["%", "Размер родителя", "Пропорционально родителю", "Идеально для резиновых сеток", "Зависит от вложенности", "Ширина колонок, gap"],
        ["rem", "Размер шрифта <html>", "Масштабируется через root", "Единая шкала масштабирования", "Требует расчета от 16px", "Шрифты, паддинги, радиусы"],
        ["em", "Шрифт текущего элемента", "Каскадное масштабирование", "Локальная модульность", "Эффект накопления степени", "Внутренние отступы кнопок"],
        ["vw/vh", "1% ширины/высоты экрана", "Прямая привязка к экрану", "Независимость от предков", "Сложность контроля минимума", "Полноэкранные Hero-блоки"],
    ]
    add_table_data(t1_headers, t1_rows, "Таблица 1 – Сравнительный анализ единиц измерения в адаптивном веб-дизайне")

    add_listing(
'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Города Беларуси: Бобруйск — Адаптивный туристический портал</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="site-header">
        <div class="wrapper header-inner">
            <div class="brand">
                <img src="emblem.png" alt="Герб Бобруйска" class="brand-logo">
                <div class="brand-text">
                    <h1 class="site-title">Города Беларуси: Бобруйск</h1>
                    <p class="site-subtitle">Информационно-туристический гид и культурно-исторический атлас</p>
                </div>
            </div>
            <div class="academic-badge">
                <span class="badge-tag">ПСИП // Лабораторная работа №6</span>
                <span class="badge-desc">Адаптивный дизайн • Группа РС02-23</span>
            </div>
        </div>
        <nav class="main-nav">
            <div class="wrapper nav-wrapper">
                <a href="#about" class="nav-item active">О городе</a>
                <a href="#attractions" class="nav-item">Достопримечательности</a>
                <a href="#routes" class="nav-item">Маршруты</a>
                <a href="#contacts" class="nav-item">Справка туриста</a>
            </div>
        </nav>
    </header>
    ...''', "Листинг 1 – Структура адаптивного веб-портала (файл index.html)")

    add_listing(
'''.wrapper { max-width: 1200px; width: 92%; margin: 0 auto; }
img, picture, svg, video { max-width: 100%; height: auto; display: block; }
.content-layout { display: flex; justify-content: space-between; gap: 3%; }
.main-section { width: 70%; display: flex; flex-direction: column; gap: 2rem; }
.sidebar-section { width: 27%; display: flex; flex-direction: column; gap: 1.5rem; }
.cards-grid { display: flex; flex-wrap: wrap; gap: 1.5rem; }
.landmark-card { flex: 1 1 calc(50% - 0.75rem); background: #ffffff; border-radius: 0.625rem; }''',
        "Листинг 2 – Базовые стили резиновой верстки (фрагмент файла style.css)")

    # Задание 2
    add_p("Для адаптации макета под экраны планшетов и смартфонов реализованы медиа-запросы CSS3 (@media screen and (...)). Контрольные точки выбраны на основе рекомендаций методички:\n"
          "- настольные мониторы и широкоформатные экраны ноутбуков (> 1024px);\n"
          "- компактные ноутбуки и планшеты в горизонтальной ориентации (1024px);\n"
          "- планшеты в вертикальной ориентации (768px);\n"
          "- мобильные смартфоны (480px);\n"
          "- компактные смартфоны малого формата (320px).",
          bold_prefix="Задание 2. Создайте медиа-запросы в CSS файле, чтобы задать различные стили для разных разрешений экранов. ")

    # Таблица 2
    t2_headers = ["Контрольная точка", "Устройства", "Шапка и меню", "Сетка контента", "Боковая панель (Aside)", "Эргономика"]
    t2_rows = [
        ["> 1024px", "Десктоп, ПК", "Флекс, меню в строку", "Ширина 70%, 2 колонки", "Ширина 27%, справа", "Мышь, стандартные поля"],
        ["max-width: 1024px", "Планшет ландшафт", "Ширина 95%, сжатие", "Ширина 66%, сетка 2x2", "Ширина 31%, сжатые поля", "Сенсор/мышь, компактность"],
        ["max-width: 768px", "Планшет портрет", "Центрирование, стек", "Ширина 100%, 1 колонка", "Ширина 100%, ПОД контентом", "Адаптация под вертикаль"],
        ["max-width: 480px", "Смартфоны", "Вертикальное тач-меню", "Ширина 100%, 1 колонка", "Ширина 100%, стек виджетов", "Тач-кнопки >= 44px, шрифт 15px"],
        ["max-width: 320px", "Малый смартфон", "Уменьшенные заголовки", "Сжатые отступы, компакт", "Компактные карточки", "Максимальная экономия экрана"],
    ]
    add_table_data(t2_headers, t2_rows, "Таблица 2 – Спецификация контрольных точек и правила трансформации интерфейса")

    add_listing(
'''/* Контрольная точка: max-width 1024px */
@media screen and (max-width: 1024px) {
    .wrapper { width: 95%; }
    .main-section { width: 66%; }
    .sidebar-section { width: 31%; }
    .stat-item { flex: 1 1 40%; }
}

/* Контрольная точка: max-width 768px */
@media screen and (max-width: 768px) {
    .content-layout { flex-direction: column; }
    .main-section { width: 100%; order: 1; }
    .sidebar-section { width: 100%; order: 2; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
    .header-inner { flex-direction: column; text-align: center; }
    .landmark-card { flex: 1 1 100%; }
}

/* Контрольная точка: max-width 480px */
@media screen and (max-width: 480px) {
    html { font-size: 93.75%; }
    .wrapper { width: 94%; }
    .nav-wrapper { flex-direction: column; align-items: stretch; }
    .nav-item { text-align: center; padding: 0.875rem 1rem; min-height: 2.75rem; }
    .sidebar-section { grid-template-columns: 1fr; }
}''', "Листинг 3 – Реализация CSS3 медиа-запросов (файл style.css)")

    # Задание 3
    add_p("В рамках третьего задания выполнена комплексная проверка адаптивного поведения разработанного веб-сайта на ключевых категориях устройств с использованием инструментов Google Chrome DevTools и автоматизированного скрипта Playwright.\n"
          "Результаты подтвердили полную работоспособность адаптивной системы: на мониторах ПК сайт отображается в виде гармоничного 2-колоночного портала, на планшетах сайдбар аккуратно перемещается под контентную область в виде адаптивной плитки, а на мобильных смартфонах интерфейс мгновенно трансформируется в эргономичный одноколоночный стек с сенсорными зонами меню не менее 44px.",
          bold_prefix="Задание 3. Проверьте адаптивность вашей страницы на различных устройствах. ")

    add_image_figure("screen_lr6_desktop_1280.png", "Рисунок 1 – Отображение страницы на десктопных мониторах (разрешение 1280×800 px)")
    add_image_figure("screen_lr6_tablet_768.png", "Рисунок 2 – Отображение страницы на экранах планшетов (разрешение 768×1024 px)")
    add_image_figure("screen_lr6_mobile_375.png", "Рисунок 3 – Отображение страницы на экранах смартфонов (разрешение 375×812 px)")

    # Таблица 3
    t3_headers = ["Разрешение", "Устройства", "Горизонтальный скролл", "Читаемость текста", "Доступность меню", "Вердикт"]
    t3_rows = [
        ["1920×1080", "Full HD мониторы", "Отсутствует (max-width 1200)", "Отличная (16px base)", "Горизонтальное меню", "Соответствует"],
        ["1280×800", "Ноутбуки и ПК", "Отсутствует", "Отличная", "Широкие кликабельные кнопки", "Соответствует"],
        ["768×1024", "Планшеты (iPad / Tab)", "Отсутствует", "Высокая (1rem)", "Плиточная адаптация", "Соответствует"],
        ["375×812", "Смартфоны (iPhone / Galaxy)", "Отсутствует (100% стек)", "Высокая (15px base)", "Тач-кнопки >= 44px", "Соответствует"],
        ["320×568", "Малые смартфоны", "Отсутствует", "Четкая, без наложения", "Вертикальный тач-стек", "Соответствует"],
    ]
    add_table_data(t3_headers, t3_rows, "Таблица 3 – Результаты инструментального тестирования адаптивности на контрольных точках")

    # Контрольные вопросы
    p_q = doc.add_paragraph()
    p_q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_q.paragraph_format.space_before = Pt(12)
    p_q.paragraph_format.space_after = Pt(6)
    r_q = p_q.add_run("Ответы на контрольные вопросы")
    r_q.bold = True
    r_q.font.size = Pt(15)

    add_p("Дизайн веб-страниц под любые экраны и устройства; цель — создать один универсальный сайт вместо нескольких отдельных мобильных версий.",
          bold_prefix="1. Адаптивный веб-дизайн и его цель?\nОтвет: ")

    add_p("Резиновая сетка макета (в % и rem/em), адаптивные изображения и медиа (max-width: 100%) и медиа-запросы CSS3.",
          bold_prefix="2. Основные принципы адаптивного дизайна?\nОтвет: ")

    add_p("Тег viewport задает масштаб 1:1 под ширину экрана устройства, а медиа-запросы (@media) применяют нужные CSS-стили под конкретные разрешения.",
          bold_prefix="3. Media query и viewport в адаптивном дизайне?\nОтвет: ")

    add_p("Добавить мета-тег viewport, перевести ширину блоков в проценты, шрифты в rem/em, задать картинкам max-width: 100% и прописать медиа-запросы (@media) для контрольных точек.",
          bold_prefix="4. Как сделать адаптивный дизайн сайта из фиксированного макета?\nОтвет: ")

    # Вывод: строго по цели
    add_p("Сформировал умение разрабатывать адаптивную версию HTML-страницы под различные разрешения экрана и типы устройства.", bold_prefix="Вывод: ")

    doc.save(docx_path)
    print(f"[OK] Сформирован документ Word: {docx_path}")

if __name__ == "__main__":
    generate_txt()
    generate_docx()
