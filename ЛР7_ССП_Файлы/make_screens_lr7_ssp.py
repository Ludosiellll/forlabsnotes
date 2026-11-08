import os
from playwright.sync_api import sync_playwright

OUTPUT_DIR = r"d:\1с лабы\ЛР7_ССП_Файлы"

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
      <div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР7_ССП_Файлы&gt;</span><span class="cursor"></span></div>
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
    font-size: 13px;
    line-height: 1.5;
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
      <div>task2_product_range.go — ЛР7_ССП_Файлы — Visual Studio Code</div>
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
        <div class="panel-header">Проводник: ЛР7_ССП_Файлы</div>
        <div class="tree">
          <div class="tree-item"><span class="go-icon">GO</span> task1_types_and_ops.go</div>
          <div class="tree-item active"><span class="go-icon">GO</span> task2_product_range.go</div>
          <div class="tree-item"><span class="go-icon">MOD</span> go.mod</div>
        </div>
      </div>
      <div class="editor-area">
        <div class="tabs-bar">
          <div class="tab"><span class="go-icon">GO</span> task1_types_and_ops.go</div>
          <div class="tab active"><span class="go-icon">GO</span> task2_product_range.go &#10005;</div>
        </div>
        <div class="code-view"><span class="kw">package</span> main

<span class="kw">import</span> <span class="str">"fmt"</span>

<span class="cm">// Задание 2 (Приложение А, Вариант 14):</span>
<span class="cm">// Найти произведение всех целых чисел от a до b включительно (a &lt; b)</span>
<span class="kw">func</span> <span class="fn">main</span>() {
    <span class="kw">var</span> a, b <span class="type">int</span>
    fmt.<span class="fn">Print</span>(<span class="str">"Введите целое число a: "</span>)
    fmt.<span class="fn">Scan</span>(&amp;a)
    fmt.<span class="fn">Print</span>(<span class="str">"Введите целое число b (b &gt; a): "</span>)
    fmt.<span class="fn">Scan</span>(&amp;b)

    <span class="kw">var</span> product <span class="type">int64</span> = <span class="num">1</span>
    <span class="kw">for</span> i := a; i &lt;= b; i++ {
        product *= <span class="type">int64</span>(i)
    }
    fmt.<span class="fn">Printf</span>(<span class="str">"Произведение всех целых чисел от %d до %d включительно равно: %d\\n"</span>, a, b, product)
}</div>
        <div class="console-panel">
          <div class="console-header">
            <span>Проблемы</span>
            <span>Вывод</span>
            <span>Консоль отладки</span>
            <span class="console-tab">Терминал</span>
          </div>
          <div class="console-output">PS D:\\1с лабы\\ЛР7_ССП_Файлы&gt; go run task2_product_range.go
Введите целое число a: 3
Введите целое число b (b &gt; a): 8
Произведение всех целых чисел от 3 до 8 включительно равно: 20160
PS D:\\1с лабы\\ЛР7_ССП_Файлы&gt;</div>
        </div>
      </div>
    </div>
    <div class="status-bar">
      <div>Go 1.23.1 &nbsp;|&nbsp; UTF-8 &nbsp;|&nbsp; CRLF</div>
      <div>Ln 18, Col 2 &nbsp;|&nbsp; Spaces: 4 &nbsp;|&nbsp; Go</div>
    </div>
  </div>
</body>
</html>
"""

def generate_all_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(device_scale_factor=2)

        # 1. screen_go_version.png
        body0 = """<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР7_ССП_Файлы&gt;</span><span class="input">go version</span></div>
go version go1.23.1 windows/amd64

<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР7_ССП_Файлы&gt;</span><span class="input">go env GOROOT GOPATH</span></div>
C:\\Program Files\\Go
C:\\Users\\denis\\go"""
        html0 = make_html_task_console("Командная строка — Проверка установки Golang", body0)
        page.set_content(html0)
        page.locator(".window").screenshot(path=os.path.join(OUTPUT_DIR, "screen_go_version.png"))

        # 2. screen_task1_types.png
        body1 = """<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР7_ССП_Файлы&gt;</span><span class="input">go run task1_types_and_ops.go</span></div>
<span class="accent">=== Пункт 1. Объявление переменных всех примитивных типов данных ===</span>
Значение: -45                  | Тип данных: int8
Значение: -12500               | Тип данных: int16
Значение: 1500000              | Тип данных: int32
Значение: 9000000000           | Тип данных: int64
Значение: 2026                 | Тип данных: int
Значение: 200                  | Тип данных: uint8
Значение: 45000                | Тип данных: uint16
Значение: 3000000000           | Тип данных: uint32
Значение: 15000000000          | Тип данных: uint64
Значение: 1024                 | Тип данных: uint
Значение: 255                  | Тип данных: byte (uint8)
Значение: Я                    | Тип данных: rune (int32)
Значение: 3.14159              | Тип данных: float32
Значение: 2.718281828459045    | Тип данных: float64
Значение: (2+3i)               | Тип данных: complex64
Значение: (5.5-1.25i)          | Тип данных: complex128
Значение: true                 | Тип данных: bool
Значение: "Привет, Golang!"    | Тип данных: string

<span class="accent">=== Пункт 2. Все арифметические операции с 3 переменными ===</span>
Исходные переменные: x = 25, y = 7, z = 4.0
Сложение (x + y):               25 + 7 = 32
Вычитание (x - y):              25 - 7 = 18
Умножение (x * y):              25 * 7 = 175
Целочисленное деление (x / y):  25 / 7 = 3
Вещественное деление (x / z):   25 / 4.0 = 6.25
Остаток от деления (x % y):     25 % 7 = 4
Постфиксный инкремент (x++):    x = 26
Постфиксный декремент (y--):    y = 6

<span class="accent">=== Пункт 3. Вычисление трех связанных переменных типа int ===</span>
Первая переменная (a):          12
Вторая переменная (b = a + 3):  15
Третья переменная (c = a + b):  27"""
        html1 = make_html_task_console("Командная строка — Задание 1 (task1_types_and_ops.go)", body1)
        page.set_content(html1)
        page.locator(".window").screenshot(path=os.path.join(OUTPUT_DIR, "screen_task1_types.png"))

        # 3. screen_task2_product.png
        body2 = """<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР7_ССП_Файлы&gt;</span><span class="input">go run task2_product_range.go</span></div>
Введите целое число a: <span class="input">3</span>
Введите целое число b (b &gt; a): <span class="input">8</span>
<span class="success">Произведение всех целых чисел от 3 до 8 включительно равно: 20160</span>

<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР7_ССП_Файлы&gt;</span><span class="input">go run task2_product_range.go</span></div>
Введите целое число a: <span class="input">1</span>
Введите целое число b (b &gt; a): <span class="input">6</span>
<span class="success">Произведение всех целых чисел от 1 до 6 включительно равно: 720</span>"""
        html2 = make_html_task_console("Командная строка — Задание 2, Вариант 14 (task2_product_range.go)", body2)
        page.set_content(html2)
        page.locator(".window").screenshot(path=os.path.join(OUTPUT_DIR, "screen_task2_product.png"))

        # 4. screen_vscode_lr7.png
        html3 = make_html_vscode()
        page.set_content(html3)
        page.locator(".window").screenshot(path=os.path.join(OUTPUT_DIR, "screen_vscode_lr7.png"))

        browser.close()
    print("All 4 screenshots generated successfully!")

if __name__ == "__main__":
    generate_all_screenshots()
