# -*- coding: utf-8 -*-
import os

work_dir = r"d:\1с лабы\ПСИП_ЛР5_Файлы"

# 1. index.html - Табличная сетка макета (Задание 1)
index_html = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Главная страница | Табличная сетка макета Бобруйск</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f1f5f9;
            color: #1e293b;
            padding: 20px;
        }
        /* Главная таблица-сетка макета */
        table.layout-grid {
            width: 1000px;
            margin: 0 auto;
            border-collapse: collapse;
            background-color: #ffffff;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            border: 2px solid #1e3a8a;
        }
        /* Заголовок таблицы */
        caption.grid-caption {
            caption-side: top;
            font-size: 14px;
            font-weight: 700;
            color: #1e3a8a;
            padding-bottom: 8px;
            text-align: left;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        /* Шапка страницы (Row 1) */
        th.header-cell {
            background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
            color: #ffffff;
            padding: 24px;
            text-align: left;
            border-bottom: 3px solid #0f766e;
        }
        .header-content {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .header-brand {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .header-brand img {
            width: 60px;
            height: 60px;
            object-fit: contain;
        }
        .header-titles h1 {
            font-size: 26px;
            margin-bottom: 4px;
        }
        .header-titles p {
            font-size: 14px;
            color: #cbd5e1;
        }
        .header-tag {
            background-color: rgba(255, 255, 255, 0.2);
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 13px;
            text-align: right;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        /* Панель навигации (Row 2) */
        td.nav-bar-cell {
            background-color: #0f172a;
            padding: 10px 24px;
            border-bottom: 1px solid #334155;
        }
        .nav-links {
            display: flex;
            gap: 20px;
        }
        .nav-links a {
            color: #e2e8f0;
            text-decoration: none;
            font-size: 14px;
            font-weight: 600;
            padding: 6px 12px;
            border-radius: 4px;
            transition: background-color 0.2s;
        }
        .nav-links a:hover, .nav-links a.active {
            background-color: #3b82f6;
            color: #ffffff;
        }
        /* Боковая колонка слева (Sidebar) */
        td.sidebar-cell {
            width: 260px;
            vertical-align: top;
            background-color: #f8fafc;
            padding: 20px;
            border-right: 1px solid #e2e8f0;
        }
        .sidebar-box {
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 14px;
            margin-bottom: 16px;
        }
        .sidebar-box h3 {
            font-size: 15px;
            color: #1e3a8a;
            margin-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 6px;
        }
        .sidebar-box ul {
            list-style-type: none;
            font-size: 13px;
        }
        .sidebar-box ul li {
            padding: 5px 0;
            border-bottom: 1px dashed #e2e8f0;
        }
        /* Основной контент (Main Content) */
        td.content-cell {
            vertical-align: top;
            padding: 24px;
        }
        .content-heading {
            font-size: 20px;
            color: #1e3a8a;
            margin-bottom: 12px;
            border-left: 4px solid #3b82f6;
            padding-left: 10px;
        }
        .content-text {
            font-size: 14px;
            line-height: 1.6;
            color: #334155;
            margin-bottom: 20px;
            text-align: justify;
        }
        /* Внутренняя таблица карточек достопримечательностей в виде сетки */
        table.cards-grid {
            width: 100%;
            border-collapse: separate;
            border-spacing: 16px;
        }
        td.card-col {
            width: 50%;
            vertical-align: top;
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
        .card-img-wrap img {
            width: 100%;
            height: 180px;
            object-fit: cover;
            display: block;
        }
        .card-body {
            padding: 14px;
        }
        .card-body h4 {
            font-size: 16px;
            color: #1e3a8a;
            margin-bottom: 6px;
        }
        .card-body p {
            font-size: 13px;
            color: #475569;
            line-height: 1.5;
        }
        /* Подвал таблицы (Row 4) */
        td.footer-cell {
            background-color: #0f172a;
            color: #94a3b8;
            padding: 16px 24px;
            text-align: center;
            font-size: 13px;
            border-top: 2px solid #1e3a8a;
        }
    </style>
</head>
<body>

    <!-- Задание 1: Главная страница сайта с табличной сеткой для размещения элементов -->
    <table class="layout-grid">
        <caption class="grid-caption">Табличная сетка размещения элементов страницы (Задание 1)</caption>
        
        <!-- Строка 1: Шапка сайта (объединение колонок colspan=2) -->
        <thead>
            <tr>
                <th colspan="2" class="header-cell">
                    <div class="header-content">
                        <div class="header-brand">
                            <img src="emblem.png" alt="Герб Бобруйска">
                            <div class="header-titles">
                                <h1>Города Беларуси: Бобруйск</h1>
                                <p>Официальный путеводитель и культурно-исторический атлас</p>
                            </div>
                        </div>
                        <div class="header-tag">
                            <strong>ЛР №5 | ПСИП</strong><br>
                            Табличная сетка макета
                        </div>
                    </div>
                </th>
            </tr>
            <!-- Строка 2: Навигационная строка -->
            <tr>
                <td colspan="2" class="nav-bar-cell">
                    <div class="nav-links">
                        <a href="index.html" class="active">Главная (Сетка)</a>
                        <a href="positioning.html">Точное позиционирование (CSS position)</a>
                        <a href="#about">О городе</a>
                        <a href="#sights">Достопримечательности</a>
                    </div>
                </td>
            </tr>
        </thead>

        <!-- Строка 3: Основная часть с двумя столбцами (Sidebar + Content) -->
        <tbody>
            <tr>
                <!-- Столбец 1: Боковое меню и справочные данные -->
                <td class="sidebar-cell">
                    <div class="sidebar-box">
                        <h3>Навигация по разделам</h3>
                        <ul>
                            <li>Бобруйская крепость</li>
                            <li>Скульптура Бобра</li>
                            <li>Социалистическая улица</li>
                            <li>Зефир «Красный пищевик»</li>
                            <li>Гостиничный фонд</li>
                        </ul>
                    </div>
                    <div class="sidebar-box">
                        <h3>Справка о городе</h3>
                        <ul>
                            <li>Основан: 1387 год</li>
                            <li>Население: ~210 000 чел.</li>
                            <li>Река: Березина</li>
                            <li>Статус: Город областного подчинения</li>
                        </ul>
                    </div>
                </td>

                <!-- Столбец 2: Основное содержимое и галерея элементов в сетке -->
                <td class="content-cell">
                    <h2 class="content-heading">Историко-культурный потенциал Бобруйска</h2>
                    <p class="content-text">
                        Бобруйск — один из древнейших и колоритнейших городов Могилёвской области, расположенный на живописных берегах реки Березины. Город известен богатым историческим прошлым, мощным крепостным комплексом начала XIX века и неповторимой архитектурой пешеходных кварталов.
                    </p>

                    <!-- Вложенная сеточная таблица из 2 столбцов с карточками объектов -->
                    <table class="cards-grid">
                        <tr>
                            <!-- Карточка 1: Скульптура Бобра -->
                            <td class="card-col">
                                <div class="card-img-wrap">
                                    <img src="bobr_statue.jpg" alt="Памятник Бобру в Бобруйске">
                                </div>
                                <div class="card-body">
                                    <h4>Скульптура Бобра</h4>
                                    <p>
                                        Бронзовый символ города высотой 1,7 метра, открытый в 2006 году на пересечении улиц Карла Маркса и Социалистической.
                                    </p>
                                </div>
                            </td>

                            <!-- Карточка 2: Бобруйская крепость -->
                            <td class="card-col">
                                <div class="card-img-wrap">
                                    <img src="fortress.jpg" alt="Бобруйская крепость">
                                </div>
                                <div class="card-body">
                                    <h4>Бобруйская крепость</h4>
                                    <p>
                                        Памятник фортификационной архитектуры Российской империи первой половины XIX века, сыгравший ключевую роль в войне 1812 года.
                                    </p>
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </tbody>

        <!-- Строка 4: Подвал таблицы (объединение колонок colspan=2) -->
        <tfoot>
            <tr>
                <td colspan="2" class="footer-cell">
                    <p>© 2026 Информационно-туристический гид по Бобруйску | Лабораторная работа №5 по дисциплине «ПСИП»</p>
                </td>
            </tr>
        </tfoot>
    </table>

</body>
</html>
'''

# 2. positioning.html - Точное позиционирование элементов (Задание 2)
positioning_html = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Точное позиционирование CSS position | Задание 2</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 960px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid #e2e8f0;
            padding: 30px;
            position: relative; /* Контекст позиционирования */
        }
        header.page-header {
            margin-bottom: 24px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 16px;
        }
        header.page-header h1 {
            font-size: 24px;
            color: #1e3a8a;
            margin-bottom: 6px;
        }
        header.page-header p {
            font-size: 14px;
            color: #64748b;
        }

        /* ------------------------------------------------------------------
           Задание 2: Использование CSS position (relative, absolute, fixed) 
           с координатами top, bottom, left, right
           ------------------------------------------------------------------ */

        /* Родительский блок карточки: position: relative */
        .showcase-card {
            position: relative; /* Базовый контейнер для абсолютных координат */
            width: 100%;
            height: 380px;
            border-radius: 10px;
            overflow: hidden;
            border: 2px solid #cbd5e1;
            margin-bottom: 28px;
            box-shadow: 0 6px 16px rgba(0,0,0,0.1);
        }
        
        /* Фоновое полноразмерное изображение */
        .showcase-card img.main-photo {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }

        /* Элемент 1: Абсолютный бейдж категории (top + left) */
        .badge-category {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(30, 58, 138, 0.9);
            color: #ffffff;
            font-size: 13px;
            font-weight: 700;
            padding: 8px 16px;
            border-radius: 20px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.3);
            z-index: 2;
        }

        /* Элемент 2: Абсолютная плашка рейтинга (top + right) */
        .badge-rating {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(15, 23, 42, 0.85);
            color: #f59e0b;
            font-size: 14px;
            font-weight: 700;
            padding: 8px 16px;
            border-radius: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            border: 1px solid rgba(245, 158, 11, 0.4);
            z-index: 2;
        }

        /* Элемент 3: Нижняя полупрозрачная информационная панель (bottom + left + right) */
        .overlay-caption {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(to top, rgba(15, 23, 42, 0.95) 0%, rgba(15, 23, 42, 0.6) 70%, transparent 100%);
            color: #ffffff;
            padding: 40px 24px 18px 24px;
            z-index: 2;
        }
        .overlay-caption h2 {
            font-size: 20px;
            margin-bottom: 4px;
            color: #ffffff;
        }
        .overlay-caption p {
            font-size: 13px;
            color: #e2e8f0;
            line-height: 1.5;
        }

        /* Элемент 4: Фиксированная кнопка быстрого действия (position: fixed, bottom + right) */
        .fixed-action-btn {
            position: fixed;
            bottom: 25px;
            right: 25px;
            background: linear-gradient(135deg, #0f766e 0%, #0d9488 100%);
            color: #ffffff;
            font-size: 14px;
            font-weight: 600;
            padding: 12px 20px;
            border-radius: 30px;
            box-shadow: 0 6px 18px rgba(15, 118, 110, 0.4);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 8px;
            border: 1px solid rgba(255,255,255,0.3);
            z-index: 1000;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .fixed-action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 22px rgba(15, 118, 110, 0.5);
        }

        /* Информационный текстовый блок */
        .info-section {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
        }
        .info-section h3 {
            font-size: 16px;
            color: #1e3a8a;
            margin-bottom: 10px;
        }
        .info-section p {
            font-size: 14px;
            color: #475569;
            margin-bottom: 10px;
            text-align: justify;
        }
        .code-pill {
            font-family: Consolas, monospace;
            background-color: #e2e8f0;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 13px;
            color: #0f172a;
        }
    </style>
</head>
<body>

    <div class="container">
        <header class="page-header">
            <h1>Задание 2. Точное позиционирование элементов (CSS position)</h1>
            <p>Использование свойств position (relative, absolute, fixed) в сочетании с координатами top, bottom, left и right</p>
        </header>

        <!-- Карточка-витрина с позиционированием поверх изображения -->
        <div class="showcase-card">
            <!-- Фоновое изображение памятника Бобру -->
            <img src="bobr_statue.jpg" alt="Памятник Бобру" class="main-photo">
            
            <!-- 1. Абсолютное позиционирование: верхний левый угол (top: 20px, left: 20px) -->
            <div class="badge-category">Памятник архитектуры</div>

            <!-- 2. Абсолютное позиционирование: верхний правый угол (top: 20px, right: 20px) -->
            <div class="badge-rating">★ ТОП-1 Достопримечательность</div>

            <!-- 3. Абсолютное позиционирование: нижняя панель (bottom: 0, left: 0, right: 0) -->
            <div class="overlay-caption">
                <h2>Скульптура Бобра — визитная карточка города</h2>
                <p>
                    Установлена на улице Социалистической в историческом центре Бобруйска. Бронзовая скульптура символизирует достаток, гостеприимство и добродушие жителей города.
                </p>
            </div>
        </div>

        <!-- Текстовое описание технологии позиционирования -->
        <div class="info-section">
            <h3>Использованные правила позиционирования CSS:</h3>
            <p>
                1. Для родительского блока <span class="code-pill">.showcase-card</span> установлено <span class="code-pill">position: relative</span>, что создаёт локальную систему координат для всех дочерних элементов.
            </p>
            <p>
                2. Для верхнего бейджа категории применены свойства <span class="code-pill">position: absolute; top: 20px; left: 20px;</span>.
            </p>
            <p>
                3. Для плашки рейтинга заданы параметры <span class="code-pill">position: absolute; top: 20px; right: 20px;</span>.
            </p>
            <p>
                4. Для текстовой панели оверлея использована растяжка по нижней грани <span class="code-pill">position: absolute; bottom: 0; left: 0; right: 0;</span> с градиентной подложкой.
            </p>
            <p>
                5. В правом нижнем углу окна браузера зафиксирована кнопка быстрого бронирования <span class="code-pill">position: fixed; bottom: 25px; right: 25px;</span>, остающаяся неподвижной при прокрутке.
            </p>
        </div>
    </div>

    <!-- 4. Фиксированное позиционирование: кнопка в углу экрана (bottom: 25px, right: 25px) -->
    <a href="index.html" class="fixed-action-btn">
        <span>← На главную</span>
    </a>

</body>
</html>
'''

with open(os.path.join(work_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

with open(os.path.join(work_dir, "positioning.html"), "w", encoding="utf-8") as f:
    f.write(positioning_html)

print("index.html and positioning.html generated successfully!")