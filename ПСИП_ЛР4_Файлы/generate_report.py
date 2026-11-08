# -*- coding: utf-8 -*-
import os

work_dir = r"d:\1с лабы\ПСИП_ЛР4_Файлы"

report_text = '''Лабораторная работа №4
Номер учебной группы: РС02-23
Дата выполнения работы: 15.09.2026
Тема работы: Подключение таблиц CSS к HTML-документу, использование различных видов селекторов
Цель работы: Научить подключать таблицы CSS к HTML-документу различными способами, использовать различные виды селекторов, свойства CSS для стилистического оформления HTML-страниц, механизм приоритетов при переопределении значений свойств CSS, переменные и математические функции при определении значений свойств CSS
Оснащение: Методические указания к выполнению, ПК, ОС Windows, Sublime Text, MS Word, браузер
Задание: Задание выполняется для темы, выбранной в лабораторной работе №2. Изучите основные теоретические сведения, выполните практические задания, ответьте на контрольные вопросы.

Результаты выполнения работы:

Задание 1. Изменение цвета фона, шрифта, размера, свойств текста и демонстрация приоритетов CSS
В рамках выполнения задания разработан веб-документ туристического гида по городу Бобруйску. Были применены три способа подключения стилей CSS к HTML-странице: внешний файл стилей style.css через тег link, внутренние стили в заголовке страницы через тег style, а также строковые стили через атрибут style тега.
В стилях определены пользовательские CSS-переменные в псевдоклассе :root для централизованного управления палитрой, шрифтами и отступами, а также математическая функция calc() для расчета адаптивных интервалов. Настроены свойства оформления текста: семейство шрифта font-family, размер font-size, насыщенность font-weight, курсив font-style, цвет текста color в форматах HEX и RGB, межбуквенные и межсловные интервалы letter-spacing и word-spacing, цвет и фиксация фона background-color, background-image, background-size, background-attachment: fixed.
Для демонстрации механизма приоритетов (каскадности) один и тот же элемент был последовательно стилизован через внешний стиль, переопределен внутренним стилем и окончательно модифицирован строковым стилем с наивысшим приоритетом.

В таблице 1 представлены способы подключения CSS и их приоритеты
Таблица 1 – Способы подключения каскадных таблиц стилей
Способ подключения	Тег или атрибут	Область действия	Приоритет
Внешний файл стилей	Тег <link rel=\"stylesheet\" href=\"style.css\">	Весь веб-сайт и любые страницы	Базовый
Внутренние стили страницы	Тег <style> в блоке <head>	Только текущий HTML-документ	Средний (выше внешнего)
Строковый стиль (inline)	Атрибут style=\"...\" конкретного тега	Только данный одиночный элемент	Наивысший
(таблица из 4 столбцов и 4 строк)

CSS-код базового оформления страницы, переменных и типографики представлен в листинге 1
Листинг 1 – CSS-код базового оформления и типографики (фрагмент style.css)
:root {
    --primary-color: #1e3a8a;
    --primary-light: #3b82f6;
    --secondary-color: #0f766e;
    --text-main: #1f2937;
    --bg-page: #f8fafc;
    --font-heading: 'Segoe UI', Arial, sans-serif;
    --font-body: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    --base-padding: 16px;
}

body {
    background-color: var(--bg-page);
    background-image: radial-gradient(#cbd5e1 1px, transparent 1px);
    background-size: 24px 24px;
    background-attachment: fixed;
    color: var(--text-main);
    font-family: var(--font-body);
    font-size: 15px;
    line-height: 1.6;
    padding: 20px;
}

header.site-header {
    background: linear-gradient(135deg, var(--primary-color) 0%, #1d4ed8 100%);
    color: #ffffff;
    padding: calc(var(--base-padding) * 1.5) calc(var(--base-padding) * 2);
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 4px solid var(--secondary-color);
}

Внешний вид шапки сайта, оформления текста и демонстрации приоритетов стилей представлен на рисунке 1
[СЮДА ВСТАВИТЬ СКРИНШОТ: screen_lr4_typography.png]
Рисунок 1 – Оформление шапки сайта, типографики и демонстрация приоритетов CSS

Задание 2. Создание стилей ссылок во всех четырех состояниях
В соответствии с заданием оформлены гиперссылки в навигационном меню сайта и в теле документа. Для стилизации использованы псевдоклассы всех четырех состояний ссылки:
a:link для обычной непосещенной ссылки
a:visited для ссылки, ранее посещенной пользователем
a:hover для ссылки при наведении указателя мыши
a:active для ссылки в момент клика левой кнопкой мыши
Для ссылок навигационного меню настроены фоновые кнопки со скруглением border-radius, плавным переходом transition, подсветкой box-shadow и сдвигом transform при нажатии. Для текстовых ссылок реализовано изменение цвета, подчеркивание и акцентная подсветка фона при наведении курсора.

CSS-код стилизации ссылок представлен в листинге 2
Листинг 2 – Правила стилизации четырех состояний гиперссылок
nav.main-nav a {
    text-decoration: none;
    font-size: 14px;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 6px;
    transition: all 0.25s ease-in-out;
}
nav.main-nav a:link { color: #e2e8f0; background-color: transparent; }
nav.main-nav a:visited { color: #cbd5e1; }
nav.main-nav a:hover {
    color: #ffffff;
    background-color: var(--primary-light);
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
}
nav.main-nav a:active {
    color: #ffffff;
    background-color: var(--primary-color);
    transform: translateY(1px);
}

.text-link:link { color: #2563eb; text-decoration: underline; font-weight: 600; }
.text-link:visited { color: #7c3aed; }
.text-link:hover {
    color: #dc2626;
    text-decoration: none;
    background-color: #fee2e2;
    padding: 2px 4px;
    border-radius: 4px;
}
.text-link:active { color: #991b1b; background-color: #fecaca; }

Внешний вид навигационного меню и стилизованных ссылок с эффектом наведения курсора представлен на рисунке 2
[СЮДА ВСТАВИТЬ СКРИНШОТ: screen_lr4_links.png]
Рисунок 2 – Стилизация состояний гиперссылок и эффект подсветки при наведении курсора

Задание 3. Создание стилизованных списков
В разделе туристической информации настроена стилизация списков двух типов: нумерованного и маркированного.
Для нумерованного списка этапов экскурсии использовано свойство list-style-type со значением decimal-leading-zero, формирующее двузначные номера с ведущими нулями (01, 02, 03, 04), а также акцентный цвет номеров и выравнивание.
Для маркированного списка туристических услуг отключены стандартные маркеры (list-style-type: none) и создан декоративный элемент маркера с помощью псевдоэлемента ::before с абсолютным позиционированием, символом ромбовидной звезды и изумрудным цветом.

CSS-код стилизации списков представлен в листинге 3
Листинг 3 – Правила стилизации нумерованных и маркированных списков
ol.custom-num-list {
    list-style-type: decimal-leading-zero;
    padding-left: 28px;
    color: var(--primary-color);
    font-weight: 600;
}
ol.custom-num-list li { margin-bottom: 10px; padding-left: 6px; }
ol.custom-num-list li span { color: var(--text-main); font-weight: 400; }

ul.custom-bullet-list {
    list-style-type: none;
    padding-left: 0;
}
ul.custom-bullet-list li {
    position: relative;
    padding-left: 30px;
    margin-bottom: 12px;
    color: var(--text-main);
}
ul.custom-bullet-list li::before {
    content: \"✦\";
    position: absolute;
    left: 4px;
    top: 0px;
    color: var(--secondary-color);
    font-size: 16px;
    font-weight: bold;
}

Внешний вид стилизованных списков представлен на рисунке 3
[СЮДА ВСТАВИТЬ СКРИНШОТ: screen_lr4_lists.png]
Рисунок 3 – Внешний вид стилизованных нумерованных и маркированных списков

Задание 4. Стилизация веб-формы
Создана и стилизована форма бронирования экскурсионного тура по городу Бобруйску.
Форма скомпонована в двухколоночную сетку. Настроены стили для однострочных текстовых полей input[type=\"text\"], input[type=\"email\"], выпадающего списка select, группы радиокнопок input[type=\"radio\"] и многострочной области ввода textarea.
Для элементов ввода заданы внутренние отступы padding, скругление border-radius, границы и состояние псевдокласса :focus, активирующее фокусную рамку и мягкую тень box-shadow без стандартного контура outline.
Кнопка отправки заявки стилизована линейным градиентом, полужирным шрифтом, скруглением, тенью и динамическими реакциями на псевдоклассы :hover и :active.

CSS-код стилизации формы представлен в листинге 4
Листинг 4 – Правила оформления элементов формы и кнопки отправки
.form-wrapper {
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 24px;
}
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.form-group { margin-bottom: 18px; }
.form-group label {
    display: block;
    font-size: 14px;
    font-weight: 600;
    color: #334155;
    margin-bottom: 6px;
}
.form-group input[type=\"text\"],
.form-group input[type=\"email\"],
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 10px 14px;
    font-size: 14px;
    border: 1.5px solid #cbd5e1;
    border-radius: 6px;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
    outline: none;
    border-color: var(--primary-light);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}
button.btn-submit {
    background: linear-gradient(135deg, var(--secondary-color) 0%, #0d9488 100%);
    color: #ffffff;
    font-size: 15px;
    font-weight: 600;
    padding: 12px 28px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    box-shadow: 0 4px 10px rgba(15, 118, 110, 0.25);
    transition: all 0.2s ease-in-out;
}
button.btn-submit:hover {
    background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%);
    transform: translateY(-1px);
}

Внешний вид стилизованной формы представлен на рисунке 4
[СЮДА ВСТАВИТЬ СКРИНШОТ: screen_lr4_form.png]
Рисунок 4 – Стилизованная форма бронирования экскурсии с эффектами фокуса и кнопкой

Задание 5. Изменение стилей таблицы, включая цвет фона, шрифта, выравнивание текста и границы ячеек
Создана таблица перечня гостиниц и туристических комплексов города Бобруйска.
К элементам таблицы применены следующие свойства CSS:
ширина таблицы width: 100% для адаптивного заполнения области контента
объединение двойных границ border-collapse: collapse для формирования единой сетки
граница border: 1px solid #cbd5e1 вокруг таблицы и между ячейками
темно-синий фон шапки таблицы thead и ячеек заголовков th
белый полужирный шрифт font-weight: 600 в заголовках колонок
внутренние отступы padding: 10px 16px в ячейках для читаемости текста
горизонтальное выравнивание text-align по левому краю для названий и адресов, по центру для номеров и категорий, по правому краю для стоимости
вертикальное выравнивание vertical-align: middle для центрирования содержимого по высоте строки

В таблице 2 представлены гостиницы города Бобруйска
Таблица 2 – Перечень гостиниц города Бобруйска
№	Название отеля	Категория	Адрес в Бобруйске	Количество номеров	Стоимость (руб/сутки)
1	Отель «Турист»	★★★	ул. Войкова, д. 20	198	от 95 BYN
2	Гостиница «Бобруйск»	★★★	ул. Советская, д. 97/26	120	от 80 BYN
3	Гостиничный комплекс «Юбилейный»	★★	ул. 50 лет ВЛКСМ, д. 26	85	от 65 BYN
4	Усадьба «Березинская заводь»	Агроусадьба	пригородная зона, р. Березина	12	от 140 BYN
5	Апарт-отель «Центральный»	Апартаменты	ул. Социалистическая, д. 84	24	от 110 BYN
(таблица из 6 столбцов и 6 строк)

CSS-код базовой стилизации таблицы, ячеек и границ представлен в листинге 5
Листинг 5 – Правила оформления таблицы, границ и выравнивания ячеек
table.hotels-table {
    width: 100%;
    border-collapse: collapse;
    border: 1px solid #cbd5e1;
    font-size: 14px;
}
table.hotels-table thead {
    background-color: var(--primary-color);
    color: #ffffff;
}
table.hotels-table th {
    padding: 12px 16px;
    font-weight: 600;
    border: 1px solid #1e40af;
    text-align: center;
    vertical-align: middle;
}
table.hotels-table td {
    padding: 10px 16px;
    border: 1px solid #cbd5e1;
    vertical-align: middle;
}
table.hotels-table td.col-id { text-align: center; font-weight: 600; }
table.hotels-table td.col-stars { text-align: center; color: #f59e0b; }
table.hotels-table td.col-price { text-align: right; font-weight: 600; }

Внешний вид стилизованной таблицы представлен на рисунке 5
[СЮДА ВСТАВИТЬ СКРИНШОТ: screen_lr4_table_base.png]
Рисунок 5 – Стилизованная таблица гостиниц города Бобруйска

Задание 6. Создание полосатого (зебрового) эффекта в таблице
Для улучшения визуального восприятия и построчного чтения данных применен полосатый (зебровый) эффект чередования строк.
Оформление реализовано с использованием структурных псевдоклассов :nth-child:
нечетные строки tbody tr:nth-child(odd) имеют белый фон #ffffff
четные строки tbody tr:nth-child(even) имеют светло-серый фон #f1f5f9
Для интерактивного взаимодействия добавлен псевдокласс tbody tr:hover, плавно подсвечивающий строку нежно-голубым оттенком #e0f2fe при наведении курсора мыши.

CSS-код реализации полосатого эффекта и динамической подсветки строк представлен в листинге 6
Листинг 6 – Правила создания полосатого фона строк и подсветки при наведении
table.hotels-table tbody tr:nth-child(odd) {
    background-color: #ffffff;
}
table.hotels-table tbody tr:nth-child(even) {
    background-color: #f1f5f9;
}
table.hotels-table tbody tr:hover {
    background-color: #e0f2fe;
    transition: background-color 0.2s ease-in-out;
}

Внешний вид таблицы с полосатым эффектом и подсветкой строки курсором представлен на рисунке 6
[СЮДА ВСТАВИТЬ СКРИНШОТ: screen_lr4_table_zebra.png]
Рисунок 6 – Полосатый (зебровый) эффект строк таблицы и интерактивная подсветка при наведении

Ответы на контрольные вопросы:

1. Что такое CSS, правило, селектор? Примеры
Ответ: CSS (Cascading Style Sheets) — язык описания внешнего вида веб-страницы. CSS-правило состоит из селектора и блока объявлений { свойство: значение; }. Селектор указывает элемент для применения стилей. Пример: p { color: blue; } (селектор p, свойство color, значение blue).

2. Каков синтаксис каскадных таблиц стилей? Примеры
Ответ: Синтаксис правила: селектор { свойство: значение; свойство2: значение2; }. Блок объявлений заключается в фигурные скобки, пары разделяются точкой с запятой, а имя свойства от значения отделяется двоеточием. Пример: h1 { font-size: 20px; text-align: center; }.

3. Типы каскадных таблиц стилей по способу их определения (подключения). Пример
Ответ: Существует три типа: внешние стили через файл <link rel=\"stylesheet\" href=\"style.css\">, внутренние стили страницы в теге <style>...</style> внутри блока <head>, и строковые (встроенные) стили через атрибут тега style=\"...\".

4. Какие есть способы задания цвета текста?
Ответ: По ключевому имени цвета (red, green), по шестнадцатеричному HEX-коду (#1e3a8a), через цветовую модель RGB/RGBA (rgb(30, 58, 138), rgba(0, 0, 0, 0.5)) и модель HSL/HSLA (hsl(210, 60%, 40%)).

5. Создания шрифта и его значения
Ответ: Шрифт определяется свойствами: font-family (гарнитура шрифта), font-size (размер в px, em, rem, pt, %), font-weight (жирность от 100 до 900 или normal, bold), font-style (начертание: normal, italic, oblique).

6. Создание фона
Ответ: Фон настраивается свойствами: background-color (цвет), background-image (изображение через url()), background-repeat (повтор: repeat, no-repeat, repeat-x, repeat-y), background-position (позиция: top, center, bottom, left, right) и background-attachment (прокрутка: scroll или fixed).

7. Свойство list-style-type и его характеристики
Ответ: Свойство задает тип маркера списка. Для нумерованных списков: decimal (1, 2...), decimal-leading-zero (01, 02...), lower-roman (i, ii...), upper-roman (I, II...). Для маркированных списков: disc (диск), circle (окружность), square (квадрат), none (без маркера).

8. Оформление ссылок
Ответ: Ссылки стилизуются через 4 псевдокласса: a:link (непосещенная), a:visited (посещенная), a:hover (при наведении курсора), a:active (при клике). Настраиваются цвет color, подчеркивание text-decoration, фон и плавность переходов.

9. Создание таблиц
Ответ: Таблица создается в HTML тегами <table>, <tr>, <th>, <td>. В CSS настраивается объединение рамок border-collapse: collapse, границы border, внутренние отступы padding, выравнивание содержимого text-align и vertical-align, а также чередование строк через :nth-child.

Вывод: В ходе выполнения лабораторной работы научился подключать таблицы CSS к HTML-документу различными способами, использовать различные виды селекторов, свойства CSS для стилистического оформления HTML-страниц, механизм приоритетов при переопределении значений свойств CSS, переменные и математические функции при определении значений свойств CSS.
'''

with open(os.path.join(work_dir, "report_lr4_psip.txt"), "w", encoding="utf-8") as f:
    f.write(report_text)
print("Updated report_lr4_psip.txt successfully!")