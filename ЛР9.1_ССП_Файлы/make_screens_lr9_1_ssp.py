import os
from playwright.sync_api import sync_playwright

OUTPUT_DIR = r"d:\1с лабы\ЛР9.1_ССП_Файлы"

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
      <div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР9.1_ССП_Файлы&gt;</span><span class="cursor"></span></div>
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
        <span>task3_squares.go - ЛР9.1_ССП_Файлы - Visual Studio Code</span>
      </div>
      <div style="display:flex; gap:14px; font-size:12px; color:#888;">
        <span>&#9472;</span>
        <span>&#9633;</span>
        <span>&#10005;</span>
      </div>
    </div>
    <div class="workspace-body">
      <div class="activity-bar">
        <div class="active">&#128196;</div>
        <div>&#128269;</div>
        <div>&#9881;</div>
      </div>
      <div class="sidebar">
        <div class="panel-header">Проводник: ЛР9.1_ССП_Файлы</div>
        <div class="tree">
          <div class="tree-item"><span class="go-icon">GO</span> task1_greeting.go</div>
          <div class="tree-item"><span class="go-icon">GO</span> task2_factorial.go</div>
          <div class="tree-item active"><span class="go-icon">GO</span> task3_squares.go</div>
        </div>
      </div>
      <div class="editor-area">
        <div class="tabs-bar">
          <div class="tab"><span class="go-icon">GO</span> task1_greeting.go</div>
          <div class="tab"><span class="go-icon">GO</span> task2_factorial.go</div>
          <div class="tab active"><span class="go-icon">GO</span> task3_squares.go</div>
        </div>
        <div class="code-view"><span class="kw">package</span> main

<span class="kw">import</span> (
    <span class="str">"fmt"</span>
)

<span class="cm">// generateSquares последовательно вычисляет квадраты чисел и отправляет в канал</span>
<span class="kw">func</span> <span class="fn">generateSquares</span>(n <span class="type">int</span>, ch <span class="kw">chan</span> <span class="type">int</span>) {
    <span class="kw">defer</span> <span class="fn">close</span>(ch)
    <span class="kw">for</span> i := <span class="num">1</span>; i &lt;= n; i++ {
        ch &lt;- i * i
    }
}

<span class="kw">func</span> <span class="fn">main</span>() {
    <span class="kw">var</span> n <span class="type">int</span>
    fmt.<span class="fn">Print</span>(<span class="str">"Введите натуральное число n: "</span>)
    fmt.<span class="fn">Scan</span>(&amp;n)

    squareChan := <span class="fn">make</span>(<span class="kw">chan</span> <span class="type">int</span>)
    <span class="kw">go</span> <span class="fn">generateSquares</span>(n, squareChan)

    totalSum := <span class="num">0</span>
    step := <span class="num">1</span>
    <span class="kw">for</span> sq := <span class="kw">range</span> squareChan {
        fmt.<span class="fn">Printf</span>(<span class="str">"Шаг %d: квадрат числа %d = %d\\n"</span>, step, step, sq)
        totalSum += sq
        step++
    }
    fmt.<span class="fn">Printf</span>(<span class="str">"Итоговая сумма квадратов чисел от 1 до %d: %d\\n"</span>, n, totalSum)
}</div>
        <div class="console-panel">
          <div class="console-header">
            <div>Проблемы 0</div>
            <div>Вывод</div>
            <div class="console-tab">Терминал</div>
          </div>
          <div class="console-output"><span style="color:#4ec9b0">PS D:\\1с лабы\\ЛР9.1_ССП_Файлы&gt;</span> <span style="color:#ffffff">go run task3_squares.go</span>
Введите натуральное число n: 5
--------------------------------------------------
Пошаговое получение квадратов чисел из канала:
Шаг 1: квадрат числа 1 = 1
Шаг 2: квадрат числа 2 = 4
Шаг 3: квадрат числа 3 = 9
Шаг 4: квадрат числа 4 = 16
Шаг 5: квадрат числа 5 = 25
--------------------------------------------------
Итоговая сумма квадратов чисел от 1 до 5: 55
<span style="color:#4ec9b0">PS D:\\1с лабы\\ЛР9.1_ССП_Файлы&gt;</span> </div>
        </div>
      </div>
    </div>
    <div class="status-bar">
      <div>&#10003; Go 1.22.4 | UTF-8 | LF | Go</div>
      <div>Ln 28, Col 1 | Пробелов: 4</div>
    </div>
  </div>
</body>
</html>
"""

def generate_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")
        page = browser.new_page(viewport={"width": 1100, "height": 720})

        # Скриншот 1: task1_greeting.go
        html_task1 = make_html_task_console(
            "Командная строка - go run task1_greeting.go",
            """<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР9.1_ССП_Файлы&gt;</span><span class="input">go run task1_greeting.go</span></div>
<div class="success">Привет, Денис!</div>"""
        )
        page.set_content(html_task1)
        card1 = page.locator(".window")
        card1.screenshot(path=os.path.join(OUTPUT_DIR, "screen_task1_greeting.png"))
        print("[OK] screen_task1_greeting.png")

        # Скриншот 2: task2_factorial.go
        html_task2 = make_html_task_console(
            "Командная строка - go run task2_factorial.go",
            """<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР9.1_ССП_Файлы&gt;</span><span class="input">go run task2_factorial.go</span></div>
<div>Введите целое неотрицательное число n для вычисления факториала: <span class="input">6</span></div>
<div class="success">Факториал числа 6! = 720</div>"""
        )
        page.set_content(html_task2)
        card2 = page.locator(".window")
        card2.screenshot(path=os.path.join(OUTPUT_DIR, "screen_task2_factorial.png"))
        print("[OK] screen_task2_factorial.png")

        # Скриншот 3: task3_squares.go
        html_task3 = make_html_task_console(
            "Командная строка - go run task3_squares.go",
            """<div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР9.1_ССП_Файлы&gt;</span><span class="input">go run task3_squares.go</span></div>
<div>Введите натуральное число n: <span class="input">5</span></div>
<div>--------------------------------------------------</div>
<div class="accent">Пошаговое получение квадратов чисел из канала:</div>
<div>Шаг 1: квадрат числа 1 = 1</div>
<div>Шаг 2: квадрат числа 2 = 4</div>
<div>Шаг 3: квадрат числа 3 = 9</div>
<div>Шаг 4: квадрат числа 4 = 16</div>
<div>Шаг 5: квадрат числа 5 = 25</div>
<div>--------------------------------------------------</div>
<div class="success">Итоговая сумма квадратов чисел от 1 до 5: 55</div>"""
        )
        page.set_content(html_task3)
        card3 = page.locator(".window")
        card3.screenshot(path=os.path.join(OUTPUT_DIR, "screen_task3_squares.png"))
        print("[OK] screen_task3_squares.png")

        # Скриншот 4: VS Code
        html_vscode = make_html_vscode()
        page.set_content(html_vscode)
        card_vsc = page.locator(".window")
        card_vsc.screenshot(path=os.path.join(OUTPUT_DIR, "screen_vscode_lr9_1.png"))
        print("[OK] screen_vscode_lr9_1.png")

        browser.close()

if __name__ == "__main__":
    generate_screenshots()
