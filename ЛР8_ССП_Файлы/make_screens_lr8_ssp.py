import os
from playwright.sync_api import sync_playwright

OUTPUT_DIR = r"d:\1с лабы\ЛР8_ССП_Файлы"

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
  .cmd-line {{ margin-bottom: 8px; }}
  .cursor {{
    display: inline-block;
    width: 8px;
    height: 16px;
    background-color: #cccccc;
    vertical-align: middle;
  }}
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
        <span>&#9472;</span>
        <span>&#9633;</span>
        <span>&#10005;</span>
      </div>
    </div>
    <div class="terminal-body">
{body_html}
      <br>
      <div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР8_ССП_Файлы&gt;</span><span class="cursor"></span></div>
    </div>
  </div>
</body>
</html>
"""

def make_html_vscode():
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
    background-color: #323233;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 12px;
    border-bottom: 1px solid #252526;
    font-size: 12px;
    color: #cccccc;
  }
  .title-left {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .vscode-logo {
    width: 14px;
    height: 14px;
    background: #007acc;
    border-radius: 2px;
  }
  .workspace-body {
    display: flex;
    height: 620px;
  }
  .activity-bar {
    width: 44px;
    background-color: #333333;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 12px;
    gap: 18px;
    color: #858585;
    font-size: 16px;
  }
  .activity-bar .active {
    color: #ffffff;
  }
  .sidebar {
    width: 230px;
    background-color: #252526;
    border-right: 1px solid #3c3c3c;
    display: flex;
    flex-direction: column;
  }
  .panel-header {
    height: 28px;
    padding: 0 12px;
    display: flex;
    align-items: center;
    font-weight: 600;
    color: #bbbbbb;
    font-size: 11px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }
  .tree {
    padding: 4px 8px;
    line-height: 1.8;
    font-size: 13px;
  }
  .tree-item {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 1px 6px;
    border-radius: 3px;
  }
  .tree-item.active {
    background-color: #37373d;
    color: #ffffff;
  }
  .go-icon {
    color: #00add8;
    font-weight: bold;
    font-family: 'Consolas', monospace;
    font-size: 11px;
  }
  .editor-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    background-color: #1e1e1e;
  }
  .tabs-bar {
    height: 34px;
    background-color: #252526;
    display: flex;
    align-items: flex-end;
    border-bottom: 1px solid #3c3c3c;
  }
  .tab {
    height: 32px;
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
    border-top: 2px solid #007acc;
  }
  .code-view {
    height: 330px;
    padding: 14px 18px;
    font-family: 'Consolas', monospace;
    font-size: 12.5px;
    line-height: 1.45;
    background-color: #1e1e1e;
    overflow: hidden;
    color: #d4d4d4;
    white-space: pre;
  }
  .kw { color: #569cd6; }
  .type { color: #4ec9b0; }
  .str { color: #ce9178; }
  .num { color: #b5cea8; }
  .cm { color: #6a9955; }
  .fn { color: #dcdcaa; }
  .console-panel {
    flex: 1;
    border-top: 1px solid #3c3c3c;
    background-color: #1e1e1e;
    display: flex;
    flex-direction: column;
  }
  .console-header {
    height: 28px;
    background-color: #252526;
    padding: 0 14px;
    display: flex;
    align-items: center;
    font-size: 11px;
    color: #999999;
    gap: 18px;
    text-transform: uppercase;
  }
  .console-tab {
    color: #ffffff;
    font-weight: 600;
    border-bottom: 1px solid #e7e7e7;
    padding-bottom: 3px;
  }
  .console-output {
    padding: 10px 16px;
    font-family: 'Consolas', monospace;
    font-size: 12.5px;
    line-height: 1.45;
    color: #cccccc;
    background-color: #1e1e1e;
    flex: 1;
    overflow: hidden;
    white-space: pre-wrap;
  }
  .status-bar {
    height: 22px;
    background-color: #007acc;
    color: #ffffff;
    font-size: 11px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 12px;
  }
</style>
</head>
<body>
  <div class="window">
    <div class="title-bar">
      <div class="title-left">
        <div class="vscode-logo"></div>
        <span>File &nbsp; Edit &nbsp; Selection &nbsp; View &nbsp; Go &nbsp; Run &nbsp; Terminal &nbsp; Help</span>
      </div>
      <div>task2_matrix5x5.go — ЛР8_ССП_Файлы — Visual Studio Code</div>
      <div style="color:#888;">&#9472; &nbsp; &#9633; &nbsp; &#10005;</div>
    </div>
    <div class="workspace-body">
      <div class="activity-bar">
        <div class="active">&#128196;</div>
        <div>&#128269;</div>
        <div>&#9654;</div>
        <div>&#9881;</div>
      </div>
      <div class="sidebar">
        <div class="panel-header">Проводник: ЛР8_ССП_Файлы</div>
        <div class="tree">
          <div class="tree-item"><span class="go-icon">GO</span> task1_stairs_and_square.go</div>
          <div class="tree-item active"><span class="go-icon">GO</span> task2_matrix5x5.go</div>
          <div class="tree-item"><span class="go-icon">MOD</span> go.mod</div>
        </div>
      </div>
      <div class="editor-area">
        <div class="tabs-bar">
          <div class="tab"><span class="go-icon">GO</span> task1_stairs_and_square.go</div>
          <div class="tab active"><span class="go-icon">GO</span> task2_matrix5x5.go &#10005;</div>
        </div>
        <div class="code-view"><span class="kw">package</span> main

<span class="kw">import</span> (
    <span class="str">"fmt"</span>
    <span class="str">"math/rand"</span>
)

<span class="cm">// Вариант 14: Заполнение двумерного массива 5x5 числами [30..60], поиск max и min</span>
<span class="kw">func</span> <span class="fn">fillMatrix</span>() [<span class="num">5</span>][<span class="num">5</span>]<span class="type">int</span> {
    <span class="kw">var</span> matrix [<span class="num">5</span>][<span class="num">5</span>]<span class="type">int</span>
    <span class="kw">for</span> i := <span class="num">0</span>; i &lt; <span class="num">5</span>; i++ {
        <span class="kw">for</span> j := <span class="num">0</span>; j &lt; <span class="num">5</span>; j++ {
            matrix[i][j] = rand.<span class="fn">Intn</span>(<span class="num">31</span>) + <span class="num">30</span>
        }
    }
    <span class="kw">return</span> matrix
}</div>
        <div class="console-panel">
          <div class="console-header">
            <span>Проблемы</span>
            <span>Вывод</span>
            <span>Консоль отладки</span>
            <span class="console-tab">Терминал</span>
          </div>
          <div class="console-output">PS D:\\1с лабы\\ЛР8_ССП_Файлы&gt; go run task2_matrix5x5.go
=== Заполнение двумерного массива 5 x 5 случайными числами [30..60] ===
  42  58  31  47  53
  36  49  60  33  44
  55  38  41  59  30
  48  52  35  46  57
  34  45  51  39  50
-----------------------------------------------------------------------
Максимальный элемент массива: 60 (строка 2, столбец 3)
Минимальный элемент массива:  30 (строка 3, столбец 5)</div>
        </div>
      </div>
    </div>
    <div class="status-bar">
      <div>Go 1.23.1 &nbsp;|&nbsp; UTF-8 &nbsp;|&nbsp; CRLF</div>
      <div>Ln 17, Col 2 &nbsp;|&nbsp; Spaces: 4 &nbsp;|&nbsp; Go</div>
    </div>
  </div>
</body>
</html>
"""

def generate_all_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(device_scale_factor=2)

        # 1. screen_task1_stairs_square.png
        body1 = """<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР8_ССП_Файлы&gt;</span><span class="input">go run task1_stairs_and_square.go</span></div>
Введите натуральное число n (n &lt;= 30) для вывода лесенки: <span class="input">7</span>

<span class="accent">=== 1. Лесенка из 7 ступенек ===</span>
1
2 2
3 3 3
4 4 4 4
5 5 5 5 5
6 6 6 6 6 6
7 7 7 7 7 7 7

Введите целое положительное число n для вычисления квадрата: <span class="input">6</span>

<span class="accent">=== 2. Вычисление квадрата числа 6 по формуле суммы нечетных чисел ===</span>
Шаг 1: прибавлено слагаемое  1 -&gt; текущая сумма = 1
Шаг 2: прибавлено слагаемое  3 -&gt; текущая сумма = 4
Шаг 3: прибавлено слагаемое  5 -&gt; текущая сумма = 9
Шаг 4: прибавлено слагаемое  7 -&gt; текущая сумма = 16
Шаг 5: прибавлено слагаемое  9 -&gt; текущая сумма = 25
Шаг 6: прибавлено слагаемое 11 -&gt; текущая сумма = 36
<span class="success">Итоговый квадрат числа 6^2 = 36</span>"""
        html1 = make_html_task_console("Командная строка — Задание 1 (task1_stairs_and_square.go)", body1)
        page.set_content(html1)
        page.locator(".window").screenshot(path=os.path.join(OUTPUT_DIR, "screen_task1_stairs_square.png"))

        # 2. screen_task2_matrix5x5.png
        body2 = """<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР8_ССП_Файлы&gt;</span><span class="input">go run task2_matrix5x5.go</span></div>
<span class="accent">=== Заполнение двумерного массива 5 x 5 случайными числами [30..60] ===</span>
  42  58  31  47  53
  36  49  60  33  44
  55  38  41  59  30
  48  52  35  46  57
  34  45  51  39  50
-----------------------------------------------------------------------
<span class="success">Максимальный элемент массива: 60 (строка 2, столбец 3)</span>
<span class="success">Минимальный элемент массива:  30 (строка 3, столбец 5)</span>"""
        html2 = make_html_task_console("Командная строка — Задание 2, Вариант 14 (task2_matrix5x5.go)", body2)
        page.set_content(html2)
        page.locator(".window").screenshot(path=os.path.join(OUTPUT_DIR, "screen_task2_matrix5x5.png"))

        # 3. screen_vscode_lr8.png
        html3 = make_html_vscode()
        page.set_content(html3)
        page.locator(".window").screenshot(path=os.path.join(OUTPUT_DIR, "screen_vscode_lr8.png"))

        browser.close()
    print("All 3 screenshots generated successfully!")

if __name__ == "__main__":
    generate_all_screenshots()
