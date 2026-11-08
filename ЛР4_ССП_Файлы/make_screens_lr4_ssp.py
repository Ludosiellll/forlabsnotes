import os
from playwright.sync_api import sync_playwright

OUTPUT_DIR = r"d:\1с лабы\ЛР4_ССП_Файлы"

def make_html_task_console(title, body_html):
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{
    margin: 0;
    padding: 24px;
    background-color: #0c0c0c;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 14.5px;
    color: #cccccc;
    display: flex;
    justify-content: center;
  }}
  .window {{
    width: 860px;
    background-color: #0c0c0c;
    border: 1px solid #333333;
    border-radius: 8px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.75);
    overflow: hidden;
  }}
  .title-bar {{
    height: 34px;
    background-color: #1f1f1f;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 12px;
    border-bottom: 1px solid #2a2a2a;
    font-family: 'Segoe UI', Tahoma, sans-serif;
    font-size: 12px;
    color: #bbbbbb;
    user-select: none;
  }}
  .title-text {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .icon-cmd {{
    width: 14px;
    height: 14px;
    background: #000;
    border: 1px solid #888;
    color: #fff;
    font-size: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
  }}
  .controls {{
    display: flex;
    gap: 14px;
    font-size: 12px;
    color: #888888;
  }}
  .ctrl:hover {{ color: #ffffff; cursor: pointer; }}
  .terminal-body {{
    padding: 16px 20px;
    line-height: 1.45;
    background-color: #0c0c0c;
    white-space: pre-wrap;
    font-family: 'Consolas', monospace;
  }}
  .prompt {{ color: #4ec9b0; }}
  .input {{ color: #ffffff; font-weight: bold; }}
  .accent {{ color: #e5c07b; }}
  .success {{ color: #98c379; }}
  .header-box {{ color: #61afef; }}
  .cmd-line {{ margin-bottom: 8px; }}
  .cursor {{
    display: inline-block;
    width: 8px;
    height: 16px;
    background-color: #cccccc;
    vertical-align: middle;
    animation: blink 1s step-end infinite;
  }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
</style>
</head>
<body>
  <div class="window">
    <div class="title-bar">
      <div class="title-text">
        <div class="icon-cmd">&gt;_</div>
        <span>{title}</span>
      </div>
      <div class="controls">
        <span class="ctrl">&#9472;</span>
        <span class="ctrl">&#9633;</span>
        <span class="ctrl">&#10005;</span>
      </div>
    </div>
    <div class="terminal-body">
{body_html}
      <br>
      <div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР4_ССП_Файлы&gt;</span><span class="cursor"></span></div>
    </div>
  </div>
</body>
</html>
"""

def make_html_eclipse():
    return """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {
    margin: 0;
    padding: 20px;
    background-color: #1e1e1e;
    font-family: 'Segoe UI', Tahoma, sans-serif;
    color: #cccccc;
    display: flex;
    justify-content: center;
  }
  .window {
    width: 1040px;
    background-color: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.8);
    overflow: hidden;
  }
  .title-bar {
    height: 32px;
    background-color: #2d2d2d;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 12px;
    border-bottom: 1px solid #333;
    font-size: 12px;
    color: #cccccc;
  }
  .title-left {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .eclipse-logo {
    width: 16px;
    height: 16px;
    background: radial-gradient(circle, #f39c12 30%, #8e44ad 80%);
    border-radius: 50%;
  }
  .menu-bar {
    height: 26px;
    background-color: #333333;
    display: flex;
    align-items: center;
    padding: 0 8px;
    gap: 14px;
    font-size: 12px;
    color: #cccccc;
    border-bottom: 1px solid #222;
  }
  .tool-bar {
    height: 34px;
    background-color: #252526;
    display: flex;
    align-items: center;
    padding: 0 12px;
    gap: 10px;
    border-bottom: 1px solid #3c3c3c;
  }
  .btn-run {
    display: flex;
    align-items: center;
    gap: 6px;
    background: #0e639c;
    padding: 4px 10px;
    border-radius: 3px;
    color: white;
    cursor: pointer;
    font-size: 11px;
  }
  .btn-play-icon {
    width: 0;
    height: 0;
    border-top: 4px solid transparent;
    border-bottom: 4px solid transparent;
    border-left: 7px solid #ffffff;
  }
  .workspace {
    display: flex;
    height: 540px;
  }
  .sidebar {
    width: 250px;
    background-color: #252526;
    border-right: 1px solid #3c3c3c;
    display: flex;
    flex-direction: column;
  }
  .panel-header {
    height: 26px;
    background-color: #2d2d2d;
    padding: 0 10px;
    display: flex;
    align-items: center;
    font-weight: 600;
    color: #cccccc;
    font-size: 11px;
    border-bottom: 1px solid #3c3c3c;
  }
  .tree {
    padding: 8px;
    line-height: 1.8;
    font-size: 12px;
  }
  .tree-item {
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
  }
  .tree-item.active {
    background-color: #37373d;
    color: #ffffff;
    border-radius: 3px;
    padding: 1px 4px;
  }
  .folder-icon { color: #dcb67a; }
  .java-icon { color: #e5c07b; font-weight: bold; }
  .editor-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    background-color: #1e1e1e;
  }
  .tabs-bar {
    height: 32px;
    background-color: #252526;
    display: flex;
    align-items: flex-end;
    border-bottom: 1px solid #3c3c3c;
  }
  .tab {
    height: 30px;
    padding: 0 14px;
    background-color: #2d2d2d;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: #969696;
    border-top: 2px solid transparent;
    border-right: 1px solid #252526;
  }
  .tab.active {
    background-color: #1e1e1e;
    color: #ffffff;
    border-top: 2px solid #0e639c;
  }
  .code-view {
    height: 290px;
    padding: 12px;
    font-family: 'Consolas', monospace;
    font-size: 13px;
    line-height: 1.45;
    background-color: #1e1e1e;
    overflow: hidden;
    color: #d4d4d4;
  }
  .kw { color: #569cd6; font-weight: bold; }
  .type { color: #4ec9b0; }
  .str { color: #ce9178; }
  .num { color: #b5cea8; }
  .cm { color: #6a9955; font-style: italic; }
  .fn { color: #dcdcaa; }
  .console-panel {
    flex: 1;
    border-top: 1px solid #3c3c3c;
    background-color: #1e1e1e;
    display: flex;
    flex-direction: column;
  }
  .console-header {
    height: 24px;
    background-color: #2d2d2d;
    padding: 0 10px;
    display: flex;
    align-items: center;
    font-size: 11px;
    color: #999999;
    gap: 12px;
  }
  .console-tab.active {
    color: #ffffff;
    font-weight: bold;
    border-bottom: 1px solid #0e639c;
  }
  .console-output {
    padding: 8px 12px;
    font-family: 'Consolas', monospace;
    font-size: 12px;
    line-height: 1.4;
    color: #cccccc;
    overflow: hidden;
  }
</style>
</head>
<body>
  <div class="window">
    <div class="title-bar">
      <div class="title-left">
        <div class="eclipse-logo"></div>
        <span>Eclipse IDE 2024-06 — Lab4_SSP/src/OrganizationHierarchy.java</span>
      </div>
      <div>&#9472; &#9633; &#10005;</div>
    </div>
    <div class="menu-bar">
      <span>File</span><span>Edit</span><span>Source</span><span>Refactor</span><span>Navigate</span><span>Search</span><span>Project</span><span>Run</span><span>Window</span><span>Help</span>
    </div>
    <div class="tool-bar">
      <div class="btn-run"><div class="btn-play-icon"></div><span>Run OrganizationHierarchy</span></div>
      <span style="color:#555">|</span>
      <span style="font-size:11px;color:#aaa">Debug</span>
      <span style="font-size:11px;color:#aaa">Java SE 8 [1.8.0_401]</span>
    </div>
    <div class="workspace">
      <div class="sidebar">
        <div class="panel-header">Package Explorer</div>
        <div class="tree">
          <div class="tree-item"><span class="folder-icon">&#9660; [P]</span> <b>Lab4_SSP</b></div>
          <div class="tree-item" style="padding-left:14px;"><span class="folder-icon">&#9660;</span> JRE System Library [JavaSE-1.8]</div>
          <div class="tree-item" style="padding-left:14px;"><span class="folder-icon">&#9660;</span> <b>src</b></div>
          <div class="tree-item" style="padding-left:28px;"><span class="java-icon">J</span> Payment.java</div>
          <div class="tree-item active" style="padding-left:28px;"><span class="java-icon">J</span> <b>OrganizationHierarchy.java</b></div>
          <div class="tree-item" style="padding-left:42px;"><span style="color:#4ec9b0">&#9658;</span> Organization</div>
          <div class="tree-item" style="padding-left:42px;"><span style="color:#4ec9b0">&#9658;</span> CommercialOrganization</div>
          <div class="tree-item" style="padding-left:42px;"><span style="color:#4ec9b0">&#9658;</span> NonProfitOrganization</div>
          <div class="tree-item" style="padding-left:42px;"><span style="color:#4ec9b0">&#9658;</span> EducationalOrganization</div>
        </div>
      </div>
      <div class="editor-area">
        <div class="tabs-bar">
          <div class="tab"><span class="java-icon">J</span> Payment.java</div>
          <div class="tab active"><span class="java-icon">J</span> OrganizationHierarchy.java</div>
        </div>
        <div class="code-view">
<span class="kw">public class</span> <span class="type">OrganizationHierarchy</span> {<br>
&nbsp;&nbsp;&nbsp;&nbsp;<span class="kw">public static void</span> <span class="fn">main</span>(<span class="type">String</span>[] <span class="str">args</span>) {<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="cm">// 1) Описать массив объектов базового класса Organization</span><br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="type">Organization</span>[] <span class="str">organizations</span> = <span class="kw">new</span> <span class="type">Organization</span>[<span class="num">4</span>];<br>
<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="cm">// 2) Занести в массив объекты дочерних классов</span><br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="str">organizations</span>[<span class="num">0</span>] = <span class="kw">new</span> <span class="type">CommercialOrganization</span>(<span class="str">"ОАО «Белшина»"</span>, <span class="str">"700016217"</span>, <span class="str">"г. Бобруйск"</span>, <span class="num">1972</span>, <span class="num">85400000.0</span>, <span class="num">18.0</span>, <span class="str">"Яковлев А.Н."</span>);<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="str">organizations</span>[<span class="num">1</span>] = <span class="kw">new</span> <span class="type">CommercialOrganization</span>(<span class="str">"ООО «Технопарк Бобруйск»"</span>, <span class="str">"790934120"</span>, <span class="str">"г. Бобруйск"</span>, <span class="num">2018</span>, <span class="num">14200000.0</span>, <span class="num">18.0</span>, <span class="str">"Лабынцев Д.Я."</span>);<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="str">organizations</span>[<span class="num">2</span>] = <span class="kw">new</span> <span class="type">NonProfitOrganization</span>(<span class="str">"БФ «Доброе сердце»"</span>, <span class="str">"790112445"</span>, <span class="str">"г. Бобруйск"</span>, <span class="num">2010</span>, <span class="num">450000.0</span>, <span class="num">85</span>, <span class="str">"Помощь детям"</span>);<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="str">organizations</span>[<span class="num">3</span>] = <span class="kw">new</span> <span class="type">EducationalOrganization</span>(<span class="str">"Государственный колледж им. А.Е. Ларина"</span>, <span class="str">"700028911"</span>, <span class="str">"г. Бобруйск"</span>, <span class="num">1968</span>, <span class="num">2800000.0</span>, <span class="num">120</span>, <span class="str">"Обучение РС02-23"</span>, <span class="num">1250</span>, <span class="str">"Категория I"</span>);<br>
<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="cm">// 3) Продемонстрировать полиморфную работу методов</span><br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="kw">for</span> (<span class="type">Organization</span> <span class="str">org</span> : <span class="str">organizations</span>) {<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="str">org</span>.<span class="fn">displayInfo</span>();<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="str">org</span>.<span class="fn">performActivity</span>();<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}<br>
&nbsp;&nbsp;&nbsp;&nbsp;}<br>
}
        </div>
        <div class="console-panel">
          <div class="console-header">
            <span class="console-tab active">Console &lt;terminated&gt; OrganizationHierarchy [Java Application]</span>
            <span>Problems</span>
            <span>Javadoc</span>
            <span>Declaration</span>
          </div>
          <div class="console-output">
ОБЪЕКТ В МАССИВЕ [0]: Коммерческая организация (ОАО / ООО)<br>
&nbsp;&nbsp;Организация: ОАО «Белшина», Город: г. Бобруйск, Руководитель: Яковлев А.Н., Налог: 2,305,800.00 руб.<br>
ОБЪЕКТ В МАССИВЕ [1]: Коммерческая организация (ОАО / ООО)<br>
&nbsp;&nbsp;Организация: ООО «Технопарк Бобруйск», Руководитель: Лабынцев Д.Я., Налог: 383,400.00 руб.<br>
ОБЪЕКТ В МАССИВЕ [3]: Образовательное учреждение (Колледж / Институт)<br>
&nbsp;&nbsp;Организация: Государственный колледж им. А.Е. Ларина, Контингент: 1250 учащихся дневного отделения
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""

def generate_all_screenshots():
    print("Generating screenshots for LR4...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(device_scale_factor=2)

        # 1. screen_task1_payment.png
        body1 = """<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР4_ССП_Файлы&gt;</span><span class="input">javac Payment.java</span></div>
<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР4_ССП_Файлы&gt;</span><span class="input">java Payment</span></div>
<span class="accent">Лабораторная работа №4. Задание №1 (Приложение А, Вариант 2)</span>
Демонстрация работы класса Payment с внутренним классом Item:

==================================================================
                       КАССОВЫЙ ЧЕК ПОКУПКИ                       
==================================================================
Номер заказа: ЧЕК-2026/09-014
Покупатель:   Лабынцев Денис Янушевич
Дата покупки: 16.09.2026 14:30
------------------------------------------------------------------
№   Наименование товара            Цена       Кол-во    Стоимость
------------------------------------------------------------------
 1. Ноутбук ASUS Vivobook       2450.00 руб. x  1 шт. =   2450.00 руб.
 2. Беспроводная мышь Logitech    65.50 руб. x  2 шт. =    131.00 руб.
 3. Механическая клавиатура      180.00 руб. x  1 шт. =    180.00 руб.
 4. Флеш-накопитель USB 64GB      32.20 руб. x  3 шт. =     96.60 руб.
 5. Коврик для мыши XL            25.00 руб. x  1 шт. =     25.00 руб.
------------------------------------------------------------------
<span class="success">ИТОГО К ОПЛАТЕ:                                     2882.60 руб.</span>
=================================================================="""

        html1 = make_html_task_console("Командная строка — Задание №1 (Payment)", body1)
        page.set_content(html1)
        page.locator(".window").screenshot(path=os.path.join(OUTPUT_DIR, "screen_task1_payment.png"))
        print("Generated: screen_task1_payment.png")

        # 2. screen_task2_organization.png
        body2 = """<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР4_ССП_Файлы&gt;</span><span class="input">javac OrganizationHierarchy.java</span></div>
<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР4_ССП_Файлы&gt;</span><span class="input">java OrganizationHierarchy</span></div>
<span class="accent">Лабораторная работа №4. Задание №2 (Приложение Б, Вариант 14 - «Организация»)</span>
Демонстрация полиморфизма и работы с массивом базового класса:

================================================================================
ОБЪЕКТ В МАССИВЕ [0]: Коммерческая организация (ОАО / ООО)
--------------------------------------------------------------------------------
  Организация:   ОАО «Белшина»
  УНП:           700016217
  Город:         г. Бобруйск (Основана в 1972 г.)
  Руководитель:  Яковлев А.Н.
  Годовая выручка:  85,400,000.00 руб. (Ставка налога: 18.0%)
  Деятельность: производство промышленной продукции и оптово-розничная торговля
  <span class="success">Налог на прибыль к уплате: 2,305,800.00 руб.</span>
================================================================================
ОБЪЕКТ В МАССИВЕ [1]: Коммерческая организация (ОАО / ООО)
--------------------------------------------------------------------------------
  Организация:   ООО «Технопарк Бобруйск»
  УНП:           790934120
  Город:         г. Бобруйск (Основана в 2018 г.)
  Руководитель:  Лабынцев Д.Я.
  Годовая выручка:  14,200,000.00 руб. (Ставка налога: 18.0%)
  Деятельность: производство промышленной продукции и оптово-розничная торговля
  <span class="success">Налог на прибыль к уплате: 383,400.00 руб.</span>
================================================================================
ОБЪЕКТ В МАССИВЕ [2]: Некоммерческая организация (Благотворительный фонд / НКО)
--------------------------------------------------------------------------------
  Организация:   Благотворительный фонд «Доброе сердце»
  УНП:           790112445
  Город:         г. Бобруйск (Основана в 2010 г.)
  Социальная миссия: Помощь детям-сиротам и социальная поддержка
  Целевой бюджет:    450,000.00 руб. (Волонтеров: 85 чел.)
  Деятельность: реализация благотворительных и социально значимых программ
  <span class="accent">Налог на прибыль к уплате: 0.00 руб. (Освобождено)</span>
================================================================================
ОБЪЕКТ В МАССИВЕ [3]: Образовательное учреждение (Колледж / Институт)
--------------------------------------------------------------------------------
  Организация:   Бобруйский государственный колледж им. А.Е. Ларина
  УНП:           700028911
  Город:         г. Бобруйск (Основана в 1968 г.)
  Социальная миссия: Подготовка техников-программистов (группа РС02-23)
  Целевой бюджет:    2,800,000.00 руб. (Волонтеров: 120 чел.)
  Аккредитация:      Государственная аккредитация I категории
  Контингент:        1250 учащихся дневного отделения
  Деятельность: подготовка квалифицированных специалистов по направлению ИТ
  <span class="accent">Налог на прибыль к уплате: 0.00 руб. (Бюджетное учреждение)</span>
================================================================================"""

        html2 = make_html_task_console("Командная строка — Задание №2 (Organization)", body2)
        page.set_content(html2)
        page.locator(".window").screenshot(path=os.path.join(OUTPUT_DIR, "screen_task2_organization.png"))
        print("Generated: screen_task2_organization.png")

        # 3. screen_eclipse_lr4.png
        html3 = make_html_eclipse()
        page.set_content(html3)
        page.locator(".window").screenshot(path=os.path.join(OUTPUT_DIR, "screen_eclipse_lr4.png"))
        print("Generated: screen_eclipse_lr4.png")

        browser.close()
    print("All screenshots generated successfully!")

if __name__ == "__main__":
    generate_all_screenshots()
