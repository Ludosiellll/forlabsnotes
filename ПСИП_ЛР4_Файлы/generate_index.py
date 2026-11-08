# -*- coding: utf-8 -*-
import os

work_dir = r"d:\1с лабы\ПСИП_ЛР4_Файлы"

index_html = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Бобруйск — Туристический гид | Лабораторная работа №4</title>
    <!-- Способ 1: Подключение внешней таблицы стилей -->
    <link rel="stylesheet" href="style.css">
    <!-- Способ 2: Внутренние стили (демонстрация механизма приоритетов) -->
    <style>
        .priority-box-internal {
            background-color: #fef3c7;
            border-left: 5px solid #f59e0b;
            padding: 12px 16px;
            margin-top: 10px;
            border-radius: 4px;
        }
        .cascade-demo {
            font-size: 15px;
            color: #1e40af; /* Задано во внутреннем стиле */
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Шапка страницы -->
        <header class="site-header">
            <div class="header-brand">
                <img src="emblem.png" alt="Герб Бобруйска" class="header-logo">
                <div class="header-content">
                    <h1>Туристический гид по Бобруйску</h1>
                    <p class="subtitle">Культурно-исторический и гостиничный путеводитель</p>
                </div>
            </div>
            <div class="header-badge">
                <strong>ЛР №4 | ПСИП</strong><br>
                Студент: Лабынцев Д. Я.<br>
                Группа: РС02-23 (Вар. 14)
            </div>
        </header>

        <!-- Навигационное меню (Задание 2: стилизация ссылок) -->
        <nav class="main-nav">
            <a href="#typography">Оформление текста</a>
            <a href="#links-section">Состояния ссылок</a>
            <a href="#lists-section">Стили списков</a>
            <a href="#form-section">Форма заявки</a>
            <a href="#table-section">Гостиницы (Таблица)</a>
        </nav>

        <!-- Основной контент страницы -->
        <main class="main-content">
            
            <!-- Секция 1: Оформление шрифтов, фонов, отступов и демонстрация приоритетов CSS -->
            <section id="typography" class="content-section">
                <h2 class="section-title">1. Оформление текста, фона и демонстрация приоритетов CSS</h2>
                <p class="description">
                    Бобруйск — старейший и колоритный город Беларуси на реке Березине с богатым историческим прошлым. 
                    В данном блоке применены свойства CSS: семейство шрифта <code>font-family</code>, насыщенность <code>font-weight</code>, 
                    курсивное начертание <code>font-style</code>, цвет текста <code>color</code>, интервалы <code>word-spacing</code> 
                    и фоновые текстуры.
                </p>

                <!-- Демонстрация приоритетов CSS (Внешний -> Внутренний -> Строковый) -->
                <div class="priority-demo-box">
                    <strong>Демонстрация механизма приоритетов и каскадности:</strong>
                    <div class="priority-box-internal">
                        <p class="cascade-demo">
                            1. Текст с классом <code>cascade-demo</code> окрашен синим цветом из внутреннего блока <code>&lt;style&gt;</code>.
                        </p>
                        <!-- Способ 3: Строковый стиль (inline style) -->
                        <p class="cascade-demo" style="color: #b91c1c; font-weight: 700; text-decoration: underline;">
                            2. Тот же класс, но переопределен строковым стилем <code>style=&quot;color: #b91c1c;&quot;</code> (наивысший приоритет).
                        </p>
                    </div>
                </div>
            </section>

            <!-- Секция 2: Стилизация ссылок во всех 4 состояниях -->
            <section id="links-section" class="content-section">
                <h2 class="section-title">2. Стилизация ссылок (4 состояния: :link, :visited, :hover, :active)</h2>
                <p class="description">
                    Каждое состояние гиперссылок оформлено с помощью соответствующих псевдоклассов. Ссылки имеют плавные переходы <code>transition</code>, подсветку фона и динамическое изменение цвета при наведении курсора:
                </p>
                <div class="links-demo-card">
                    <p>
                        Исследуйте ключевые ресурсы: 
                        <a href="https://bobruisk.by" class="text-link" target="_blank">Официальный сайт горисполкома</a> | 
                        <a href="#visited-link-demo" class="text-link">Посещенная ссылка архива</a> | 
                        <a href="#book-tour" class="text-link">Забронировать тур онлайн</a>
                    </p>
                </div>
            </section>

            <!-- Секция 3: Стилизованные списки -->
            <section id="lists-section" class="content-section">
                <h2 class="section-title">3. Стилизация нумерованных и маркированных списков</h2>
                <div class="lists-grid">
                    <!-- Нумерованный список с ведущими нулями (decimal-leading-zero) -->
                    <div>
                        <h3 style="font-size: 16px; margin-bottom: 10px; color: var(--primary-color);">Главные этапы экскурсии:</h3>
                        <ol class="custom-num-list">
                            <li><span>Посещение Бобруйской крепости XIX века</span></li>
                            <li><span>Прогулка по пешеходной Социалистической улице</span></li>
                            <li><span>Фотосессия у знаменитой скульптуры Бобра</span></li>
                            <li><span>Осмотр исторического собора Николая Чудотворца</span></li>
                        </ol>
                    </div>

                    <!-- Маркированный список с кастомными псевдоэлементами -->
                    <div>
                        <h3 style="font-size: 16px; margin-bottom: 10px; color: var(--secondary-color);">Услуги и удобства для туристов:</h3>
                        <ul class="custom-bullet-list">
                            <li>Индивидуальное и групповое экскурсионное сопровождение</li>
                            <li>Трансфер от железнодорожного вокзала</li>
                            <li>Дегустация знаменитого бобруйского зефира «Красный пищевик»</li>
                            <li>Бронирование номеров в центральных отелях</li>
                        </ul>
                    </div>
                </div>
            </section>

            <!-- Секция 4: Стилизация формы обратной связи / бронирования -->
            <section id="form-section" class="content-section">
                <h2 class="section-title">4. Стилизованная форма бронирования экскурсии</h2>
                <div class="form-wrapper">
                    <form action="#" method="post" onsubmit="return false;">
                        <div class="form-row">
                            <div class="form-group">
                                <label for="tourist_name">Ваше имя и фамилия:</label>
                                <input type="text" id="tourist_name" name="tourist_name" placeholder="Иван Иванов" required>
                            </div>
                            <div class="form-group">
                                <label for="tourist_email">Контактный E-mail:</label>
                                <input type="email" id="tourist_email" name="tourist_email" placeholder="ivan@example.com" required>
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="tour_type">Выберите формат тура:</label>
                                <select id="tour_type" name="tour_type">
                                    <option value="history">Исторический (Бобруйская крепость)</option>
                                    <option value="culture">Культурно-гастрономический</option>
                                    <option value="weekend">Тур выходного дня (2 дня / 1 ночь)</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Количество гостей:</label>
                                <div class="radio-checkbox-group">
                                    <label><input type="radio" name="guests" value="1" checked> 1-2 чел.</label>
                                    <label><input type="radio" name="guests" value="3"> 3-5 чел.</label>
                                    <label><input type="radio" name="guests" value="group"> Группа (6+)</label>
                                </div>
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="comments">Пожелания к бронированию:</label>
                            <textarea id="comments" name="comments" rows="3" placeholder="Укажите дату прибытия и особые пожелания..."></textarea>
                        </div>

                        <button type="submit" class="btn-submit">Отправить заявку на бронирование</button>
                    </form>
                </div>
            </section>

            <!-- Секция 5 и 6: Стилизованная таблица с зебровым эффектом -->
            <section id="table-section" class="content-section">
                <h2 class="section-title">5–6. Стилизованная таблица гостиниц Бобруйска с зебровым эффектом</h2>
                <p class="description">
                    Таблица оформлена с объединенными границами <code>border-collapse: collapse</code>, отступами ячеек <code>padding</code>, 
                    выравниванием текста по горизонтали и вертикали. Четные и нечетные строки стилизованы с помощью псевдоклассов 
                    <code>:nth-child(odd)</code> и <code>:nth-child(even)</code> для создания полосатого эффекта («зебра»), а при наведении мыши 
                    строка подсвечивается через <code>:hover</code>:
                </p>

                <div class="table-container">
                    <table class="hotels-table">
                        <thead>
                            <tr>
                                <th class="col-id">№</th>
                                <th>Название отеля</th>
                                <th>Категория</th>
                                <th>Адрес в Бобруйске</th>
                                <th>Количество номеров</th>
                                <th class="col-price">Стоимость (руб/сутки)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="col-id">1</td>
                                <td><strong>Отель «Турист»</strong></td>
                                <td class="col-stars">★★★</td>
                                <td>ул. Войкова, д. 20</td>
                                <td style="text-align: center;">198</td>
                                <td class="col-price">от 95 BYN</td>
                            </tr>
                            <tr>
                                <td class="col-id">2</td>
                                <td><strong>Гостиница «Бобруйск»</strong></td>
                                <td class="col-stars">★★★</td>
                                <td>ул. Советская, д. 97/26</td>
                                <td style="text-align: center;">120</td>
                                <td class="col-price">от 80 BYN</td>
                            </tr>
                            <tr>
                                <td class="col-id">3</td>
                                <td><strong>Гостиничный комплекс «Юбилейный»</strong></td>
                                <td class="col-stars">★★</td>
                                <td>ул. 50 лет ВЛКСМ, д. 26</td>
                                <td style="text-align: center;">85</td>
                                <td class="col-price">от 65 BYN</td>
                            </tr>
                            <tr>
                                <td class="col-id">4</td>
                                <td><strong>Усадьба «Березинская заводь»</strong></td>
                                <td class="col-stars">Агроусадьба</td>
                                <td>пригородная зона, р. Березина</td>
                                <td style="text-align: center;">12</td>
                                <td class="col-price">от 140 BYN</td>
                            </tr>
                            <tr>
                                <td class="col-id">5</td>
                                <td><strong>Апарт-отель «Центральный»</strong></td>
                                <td class="col-stars">Апартаменты</td>
                                <td>ул. Социалистическая, д. 84</td>
                                <td style="text-align: center;">24</td>
                                <td class="col-price">от 110 BYN</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

        </main>

        <!-- Подвал страницы -->
        <footer class="site-footer">
            <p>© 2026 Информационно-туристический портал города Бобруйска</p>
            <p>Выполнил: учащийся группы РС02-23 Лабынцев Денис Янушевич | Вариант 14</p>
        </footer>
    </div>
</body>
</html>
'''

with open(os.path.join(work_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)
print("index.html successfully written!")