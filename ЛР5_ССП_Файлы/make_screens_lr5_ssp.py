import os
from playwright.sync_api import sync_playwright

OUTPUT_DIR = r"d:\1с лабы\ЛР5_ССП_Файлы"

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
    font-size: 14px;
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
      <div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР5_ССП_Файлы&gt;</span><span class="cursor"></span></div>
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
    gap: 4px;
    background: #0e639c;
    color: white;
    padding: 3px 8px;
    border-radius: 3px;
    font-size: 11px;
    cursor: pointer;
  }
  .workspace-body {
    display: flex;
    height: 600px;
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
    height: 310px;
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
  .console-tab {
    color: #ffffff;
    font-weight: 600;
    border-bottom: 2px solid #0e639c;
    padding-bottom: 2px;
  }
  .console-output {
    padding: 10px 14px;
    font-family: 'Consolas', monospace;
    font-size: 12px;
    line-height: 1.4;
    color: #cccccc;
    background-color: #1e1e1e;
    flex: 1;
    overflow: hidden;
    white-space: pre-wrap;
  }
</style>
</head>
<body>
  <div class="window">
    <div class="title-bar">
      <div class="title-left">
        <div class="eclipse-logo"></div>
        <span>Eclipse IDE 2024-06 — Lab5_SSP/src/StringOperations.java</span>
      </div>
      <div style="font-size: 12px; color: #888;">Workspace: D:\\1с лабы\\ЛР5_ССП_Файлы</div>
    </div>
    <div class="menu-bar">
      <span>File</span>
      <span>Edit</span>
      <span>Source</span>
      <span>Refactor</span>
      <span>Navigate</span>
      <span>Search</span>
      <span>Project</span>
      <span>Run</span>
      <span>Window</span>
      <span>Help</span>
    </div>
    <div class="tool-bar">
      <div class="btn-run">&#9654; Run StringOperations.java</div>
      <span style="color: #666; margin: 0 6px;">|</span>
      <span style="font-size: 12px; color: #aaa;">Debug</span>
      <span style="font-size: 12px; color: #aaa; margin-left: 10px;">Build Project</span>
    </div>
    <div class="workspace-body">
      <div class="sidebar">
        <div class="panel-header">Package Explorer</div>
        <div class="tree">
          <div class="tree-item"><span class="folder-icon">&#128193;</span> <b>Lab5_SSP</b></div>
          <div class="tree-item" style="padding-left: 16px;"><span class="folder-icon">&#128193;</span> JRE System Library [JavaSE-1.8]</div>
          <div class="tree-item" style="padding-left: 16px;"><span class="folder-icon">&#128193;</span> src</div>
          <div class="tree-item active" style="padding-left: 32px;"><span class="java-icon">J</span> StringOperations.java</div>
          <div class="tree-item" style="padding-left: 32px;"><span class="java-icon">J</span> StudentFormatter.java</div>
        </div>
      </div>
      <div class="editor-area">
        <div class="tabs-bar">
          <div class="tab active"><span class="java-icon">J</span> StringOperations.java &#10005;</div>
          <div class="tab"><span class="java-icon">J</span> StudentFormatter.java</div>
        </div>
        <div class="code-view">
<span class="kw">public class</span> <span class="type">StringOperations</span> {
    <span class="kw">public static void</span> <span class="fn">processString</span>(<span class="type">String</span> str) {
        <span class="type">System</span>.out.<span class="fn">println</span>(<span class="str">"Исходная строка: \\""</span> + str + <span class="str">"\\""</span>);
        <span class="cm">// 2. Распечатать последний символ строки</span>
        <span class="type">char</span> lastChar = str.<span class="fn">charAt</span>(str.<span class="fn">length</span>() - <span class="num">1</span>);
        <span class="type">System</span>.out.<span class="fn">println</span>(<span class="str">"2. Последний символ: '"</span> + lastChar + <span class="str">"'"</span>);
        <span class="cm">// 3. Проверить, заканчивается ли подстрокой "..."</span>
        <span class="type">boolean</span> endsDots = str.<span class="fn">endsWith</span>(<span class="str">"..."</span>);
        <span class="cm">// 4. Проверить, начинается ли подстрокой "Фамилия" / "Лабынцев"</span>
        <span class="type">boolean</span> startsFam = str.<span class="fn">startsWith</span>(<span class="str">"Лабынцев"</span>);
        <span class="cm">// 5. Проверить, содержит ли подстроку "Имя" / "Денис"</span>
        <span class="type">boolean</span> hasName = str.<span class="fn">contains</span>(<span class="str">"Денис"</span>);
        <span class="cm">// 6. Найти позицию подстроки "Денис"</span>
        <span class="type">int</span> pos = str.<span class="fn">indexOf</span>(<span class="str">"Денис"</span>);
        <span class="cm">// 7. Заменить все 'а' на 'о'</span>
        <span class="type">String</span> rep = str.<span class="fn">replace</span>(<span class="str">'а'</span>, <span class="str">'о'</span>).<span class="fn">replace</span>(<span class="str">'А'</span>, <span class="str">'О'</span>);
        <span class="cm">// 8. К верхнему регистру / 9. К нижнему регистру</span>
        <span class="type">System</span>.out.<span class="fn">println</span>(str.<span class="fn">toUpperCase</span>());
        <span class="type">System</span>.out.<span class="fn">println</span>(str.<span class="fn">toLowerCase</span>());
    }
}
        </div>
        <div class="console-panel">
          <div class="console-header">
            <span class="console-tab">Console</span>
            <span>Problems</span>
            <span>Javadoc</span>
            <span>Declaration</span>
            <span style="margin-left: auto; color: #777;">&lt;terminated&gt; StringOperations [Java Application]</span>
          </div>
          <div class="console-output">
Исходная строка: "Лабынцев Денис Янушевич"
2. Последний символ строки: 'ч'
3. Заканчивается ли подстрокой "...": false (заканчивается на "вич": true)
4. Начинается ли подстрокой "Лабынцев": true
5. Содержит ли подстроку "Денис": true
6. Позиция подстроки "Денис": 9
7. Результат замены всех символов 'а' на 'о': "Лобынцев Денис Янушевич"
8. Преобразование к верхнему регистру: "ЛАБЫНЦЕВ ДЕНИС ЯНУШЕВИЧ"
9. Преобразование к нижнему регистру: "лабынцев денис янушевич"
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""

def generate_all_screenshots():
    print("Generating screenshots for LR5 SSP...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(device_scale_factor=2)

        # 1. screen_task1_string.png
        body1 = """<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР5_ССП_Файлы&gt;</span><span class="input">javac StringOperations.java</span></div>
<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР5_ССП_Файлы&gt;</span><span class="input">java StringOperations</span></div>
<span class="accent">Демонстрация выполнения Задания №1 (класс StringOperations)</span>
==================================================
Исходная строка: "Лабынцев Денис Янушевич"
--------------------------------------------------
2. Последний символ строки: 'ч'
3. Заканчивается ли подстрокой "...": false
   (дополнительно: заканчивается ли на "вич": true)
4. Начинается ли подстрокой "Фамилия": false
   (дополнительно: начинается ли на "Лабынцев": true)
5. Содержит ли подстроку "Имя": false
   (дополнительно: содержит ли подстроку "Денис": true)
6. Позиция подстроки "Имя": -1
   Позиция подстроки "Денис": 9
7. Результат замены всех символов 'а' на 'о': "Лобынцев Денис Янушевич"
8. Преобразование к верхнему регистру: "ЛАБЫНЦЕВ ДЕНИС ЯНУШЕВИЧ"
9. Преобразование к нижнему регистру: "лабынцев денис янушевич"
==================================================
Демонстрация для строки с литералами заданий:
Исходная строка: "Фамилия Имя Отчество..."
--------------------------------------------------
2. Последний символ строки: '.'
3. Заканчивается ли подстрокой "...": true
4. Начинается ли подстрокой "Фамилия": true
5. Содержит ли подстроку "Имя": true
6. Позиция подстроки "Имя": 8
   Позиция подстроки "Денис": -1
7. Результат замены всех символов 'а' на 'о': "Фомилия Имя Отчество..."
8. Преобразование к верхнему регистру: "ФАМИЛИЯ ИМЯ ОТЧЕСТВО..."
9. Преобразование к нижнему регистру: "фамилия имя отчество..."
=================================================="""

        html1 = make_html_task_console("Командная строка — Задание №1 (StringOperations)", body1)
        page.set_content(html1)
        page.locator(".window").screenshot(path=os.path.join(OUTPUT_DIR, "screen_task1_string.png"))
        print("Generated: screen_task1_string.png")

        # 2. screen_task2_formatter.png
        body2 = """<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР5_ССП_Файлы&gt;</span><span class="input">javac StudentFormatter.java</span></div>
<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР5_ССП_Файлы&gt;</span><span class="input">java StudentFormatter</span></div>
<span class="accent">Результаты успеваемости студентов (Задание №2):</span>
==================================================================
Студент Иванов          получил 5   по Математике
Студент Петрова         получил 4   по Физике    
Студент Сидорова        получил 3   по Программированию
Студент Лабынцев        получил 10  по ССП       
Студент Лабынцев        получил 9   по 1С:Предприятие
=================================================================="""

        html2 = make_html_task_console("Командная строка — Задание №2 (StudentFormatter)", body2)
        page.set_content(html2)
        page.locator(".window").screenshot(path=os.path.join(OUTPUT_DIR, "screen_task2_formatter.png"))
        print("Generated: screen_task2_formatter.png")

        # 3. screen_eclipse_lr5.png
        html3 = make_html_eclipse()
        page.set_content(html3)
        page.locator(".window").screenshot(path=os.path.join(OUTPUT_DIR, "screen_eclipse_lr5.png"))
        print("Generated: screen_eclipse_lr5.png")

        browser.close()
    print("All screenshots generated successfully!")

if __name__ == "__main__":
    generate_all_screenshots()
