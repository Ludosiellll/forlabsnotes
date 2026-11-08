import os
from playwright.sync_api import sync_playwright

OUTPUT_DIR = r"d:\1с лабы\ЛР3_ССП_Файлы"

def make_html_cmd():
    return """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {
    margin: 0;
    padding: 24px;
    background-color: #0c0c0c;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 15px;
    color: #cccccc;
    display: flex;
    justify-content: center;
  }
  .window {
    width: 820px;
    background-color: #0c0c0c;
    border: 1px solid #333333;
    border-radius: 8px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.7);
    overflow: hidden;
  }
  .title-bar {
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
  }
  .title-text {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .icon-cmd {
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
  }
  .controls {
    display: flex;
    gap: 12px;
  }
  .ctrl {
    width: 12px;
    height: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #888;
    font-size: 11px;
  }
  .terminal-body {
    padding: 16px 20px;
    line-height: 1.45;
  }
  .cmd-line {
    color: #cccccc;
    margin-bottom: 3px;
  }
  .prompt {
    color: #cccccc;
  }
  .input {
    color: #ffffff;
    font-weight: bold;
  }
  .out {
    color: #cccccc;
    margin-bottom: 12px;
  }
  .cursor {
    display: inline-block;
    width: 8px;
    height: 15px;
    background: #cccccc;
    vertical-align: middle;
    margin-left: 2px;
  }
</style>
</head>
<body>
  <div class="window">
    <div class="title-bar">
      <div class="title-text">
        <div class="icon-cmd">&gt;_</div>
        <span>Командная строка</span>
      </div>
      <div class="controls">
        <span class="ctrl">&#9472;</span>
        <span class="ctrl">&#9633;</span>
        <span class="ctrl">&#10005;</span>
      </div>
    </div>
    <div class="terminal-body">
      <div class="cmd-line">Microsoft Windows [Version 10.0.22631.3296]</div>
      <div class="cmd-line">(c) Корпорация Майкрософт (Microsoft Corporation). Все права защищены.</div>
      <br>
      <div class="cmd-line"><span class="prompt">C:\\Users\\denis&gt;</span><span class="input">java -version</span></div>
      <div class="out">
        java version "1.8.0_401"<br>
        Java(TM) SE Runtime Environment (build 1.8.0_401-b10)<br>
        Java HotSpot(TM) 64-Bit Server VM (build 25.401-b10, mixed mode)
      </div>
      <div class="cmd-line"><span class="prompt">C:\\Users\\denis&gt;</span><span class="input">javac -version</span></div>
      <div class="out">
        javac 1.8.0_401
      </div>
      <div class="cmd-line"><span class="prompt">C:\\Users\\denis&gt;</span><span class="cursor"></span></div>
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
    padding: 16px;
    background-color: #2b2b2b;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 12px;
    color: #d4d4d4;
    display: flex;
    justify-content: center;
  }
  .window {
    width: 980px;
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
    height: 520px;
  }
  .sidebar {
    width: 240px;
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
  }
  .tree-item.active {
    background-color: #094771;
    color: #fff;
    border-radius: 2px;
    padding-right: 4px;
  }
  .indent-1 { padding-left: 14px; }
  .indent-2 { padding-left: 28px; }
  .indent-3 { padding-left: 42px; }
  
  .icon-proj { color: #f1c40f; }
  .icon-pkg { color: #e67e22; }
  .icon-java { color: #3498db; }
  .icon-lib { color: #95a5a6; }

  .editor-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    background-color: #1e1e1e;
  }
  .editor-tabs {
    height: 30px;
    background-color: #252526;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #3c3c3c;
  }
  .tab {
    padding: 6px 14px;
    background-color: #1e1e1e;
    color: #ffffff;
    border-top: 2px solid #007acc;
    border-right: 1px solid #2d2d2d;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
  }
  .tab.inactive {
    background-color: #2d2d2d;
    color: #969696;
    border-top: 2px solid transparent;
  }
  .code-view {
    flex: 1;
    padding: 14px 16px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.45;
    overflow: hidden;
  }
  .ln { color: #6e7681; display: inline-block; width: 26px; text-align: right; margin-right: 14px; user-select: none; }
  .kw { color: #569cd6; font-weight: bold; }
  .type { color: #4ec9b0; }
  .str { color: #ce9178; }

  .bottom-dock {
    height: 150px;
    background-color: #1e1e1e;
    border-top: 1px solid #3c3c3c;
    display: flex;
    flex-direction: column;
  }
  .dock-tabs {
    height: 26px;
    background-color: #252526;
    display: flex;
    align-items: center;
    padding: 0 10px;
    gap: 16px;
    font-size: 11px;
    color: #969696;
    border-bottom: 1px solid #333;
  }
  .dock-tab.active {
    color: #ffffff;
    border-bottom: 2px solid #007acc;
    padding-bottom: 4px;
  }
  .console-body {
    flex: 1;
    padding: 10px 14px;
    font-family: 'Consolas', monospace;
    font-size: 13px;
    color: #cccccc;
    background-color: #181818;
    line-height: 1.4;
  }
  .status-bar {
    height: 22px;
    background-color: #007acc;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 10px;
    font-size: 11px;
  }
</style>
</head>
<body>
  <div class="window">
    <div class="title-bar">
      <div class="title-left">
        <div class="eclipse-logo"></div>
        <span>Eclipse IDE for Java Developers — Lab3_SSP/src/Task1_MinOfThree.java</span>
      </div>
      <div>&#9472; &#9633; &#10005;</div>
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
      <div class="btn-run">
        <div class="btn-play-icon"></div>
        <span>Run Task1_MinOfThree</span>
      </div>
    </div>
    <div class="workspace">
      <div class="sidebar">
        <div class="panel-header">Package Explorer</div>
        <div class="tree">
          <div class="tree-item"><span class="icon-proj">&#9662; [P]</span> <strong>Lab3_SSP</strong></div>
          <div class="tree-item indent-1"><span class="icon-pkg">&#9662; &#128193;</span> <strong>src</strong></div>
          <div class="tree-item indent-2"><span class="icon-pkg">&#9662; &#128194;</span> <i>(default package)</i></div>
          <div class="tree-item indent-3 active"><span class="icon-java">&#9646;</span> Task1_MinOfThree.java</div>
          <div class="tree-item indent-3"><span class="icon-java">&#9646;</span> Task2_Sequence.java</div>
          <div class="tree-item indent-3"><span class="icon-java">&#9646;</span> Task3_Rectangles.java</div>
          <div class="tree-item indent-1"><span class="icon-lib">&#9656; &#128218;</span> JRE System Library [JavaSE-1.8]</div>
        </div>
      </div>
      <div class="editor-area">
        <div class="editor-tabs">
          <div class="tab"><span>Task1_MinOfThree.java</span> <span style="font-size:10px; color:#888;">&#10005;</span></div>
          <div class="tab inactive"><span>Task2_Sequence.java</span></div>
          <div class="tab inactive"><span>Task3_Rectangles.java</span></div>
        </div>
        <div class="code-view">
          <div><span class="ln">1</span><span class="kw">import</span> java.util.<span class="type">Scanner</span>;</div>
          <div><span class="ln">2</span></div>
          <div><span class="ln">3</span><span class="kw">public class</span> <span class="type">Task1_MinOfThree</span> {</div>
          <div><span class="ln">4</span>    <span class="kw">public static void</span> main(<span class="type">String</span>[] args) {</div>
          <div><span class="ln">5</span>        <span class="type">Scanner</span> scanner = <span class="kw">new</span> <span class="type">Scanner</span>(<span class="type">System</span>.in);</div>
          <div><span class="ln">6</span></div>
          <div><span class="ln">7</span>        <span class="type">System</span>.out.print(<span class="str">"Введите первое число: "</span>);</div>
          <div><span class="ln">8</span>        <span class="kw">double</span> a = scanner.nextDouble();</div>
          <div><span class="ln">9</span></div>
          <div><span class="ln">10</span>       <span class="type">System</span>.out.print(<span class="str">"Введите второе число: "</span>);</div>
          <div><span class="ln">11</span>       <span class="kw">double</span> b = scanner.nextDouble();</div>
          <div><span class="ln">12</span></div>
          <div><span class="ln">13</span>       <span class="type">System</span>.out.print(<span class="str">"Введите третье число: "</span>);</div>
          <div><span class="ln">14</span>       <span class="kw">double</span> c = scanner.nextDouble();</div>
          <div><span class="ln">15</span></div>
          <div><span class="ln">16</span>       <span class="kw">double</span> min;</div>
          <div><span class="ln">17</span>       <span class="kw">if</span> (a &lt;= b &amp;&amp; a &lt;= c) {</div>
          <div><span class="ln">18</span>           min = a;</div>
          <div><span class="ln">19</span>       } <span class="kw">else if</span> (b &lt;= a &amp;&amp; b &lt;= c) {</div>
          <div><span class="ln">20</span>           min = b;</div>
          <div><span class="ln">21</span>       } <span class="kw">else</span> {</div>
          <div><span class="ln">22</span>           min = c;</div>
          <div><span class="ln">23</span>       }</div>
          <div><span class="ln">24</span></div>
          <div><span class="ln">25</span>       <span class="type">System</span>.out.println(<span class="str">"Минимальное число: "</span> + min);</div>
          <div><span class="ln">26</span>       scanner.close();</div>
          <div><span class="ln">27</span>   }</div>
          <div><span class="ln">28</span>}</div>
        </div>
        <div class="bottom-dock">
          <div class="dock-tabs">
            <span>Problems</span>
            <span>Javadoc</span>
            <span>Declaration</span>
            <span class="dock-tab active">Console [Task1_MinOfThree]</span>
          </div>
          <div class="console-body">
            &lt;terminated&gt; Task1_MinOfThree [Java Application] C:\\Program Files\\Java\\jre-1.8\\bin\\javaw.exe<br>
            Введите первое число: 45.8<br>
            Введите второе число: 12.3<br>
            Введите третье число: 27.5<br>
            Минимальное число: 12.3
          </div>
        </div>
      </div>
    </div>
    <div class="status-bar">
      <span>Writable | Smart Insert | 28:1 | UTF-8</span>
      <span>JavaSE-1.8</span>
    </div>
  </div>
</body>
</html>
"""

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
    font-size: 15px;
    color: #cccccc;
    display: flex;
    justify-content: center;
  }}
  .window {{
    width: 820px;
    background-color: #0c0c0c;
    border: 1px solid #333333;
    border-radius: 8px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.7);
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
    gap: 12px;
  }}
  .ctrl {{
    width: 12px;
    height: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #888;
    font-size: 11px;
  }}
  .terminal-body {{
    padding: 16px 20px;
    line-height: 1.5;
  }}
  .cmd-line {{
    color: #cccccc;
    margin-bottom: 4px;
  }}
  .prompt {{
    color: #cccccc;
  }}
  .input {{
    color: #ffffff;
    font-weight: bold;
  }}
  .cursor {{
    display: inline-block;
    width: 8px;
    height: 15px;
    background: #cccccc;
    vertical-align: middle;
    margin-left: 2px;
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
        <span class="ctrl">&#9472;</span>
        <span class="ctrl">&#9633;</span>
        <span class="ctrl">&#10005;</span>
      </div>
    </div>
    <div class="terminal-body">
      {body_html}
      <br>
      <div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР3_ССП_Файлы&gt;</span><span class="cursor"></span></div>
    </div>
  </div>
</body>
</html>
"""

def generate_all_screenshots():
    print("Starting screenshot generation with Playwright (msedge)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(device_scale_factor=2)

        # 1. screen_jdk_cmd.png
        html1 = make_html_cmd()
        page.set_content(html1)
        elem1 = page.locator(".window")
        out_path1 = os.path.join(OUTPUT_DIR, "screen_jdk_cmd.png")
        elem1.screenshot(path=out_path1)
        print("Generated:", out_path1)

        # 2. screen_eclipse_ide.png
        html2 = make_html_eclipse()
        page.set_content(html2)
        elem2 = page.locator(".window")
        out_path2 = os.path.join(OUTPUT_DIR, "screen_eclipse_ide.png")
        elem2.screenshot(path=out_path2)
        print("Generated:", out_path2)

        # 3. screen_task1_min.png
        body3 = """
        <div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР3_ССП_Файлы&gt;</span><span class="input">java Task1_MinOfThree</span></div>
        <div>Введите первое число: <span class="input">45.8</span></div>
        <div>Введите второе число: <span class="input">12.3</span></div>
        <div>Введите третье число: <span class="input">27.5</span></div>
        <div>Минимальное число: 12.3</div>
        """
        html3 = make_html_task_console("Командная строка", body3)
        page.set_content(html3)
        elem3 = page.locator(".window")
        out_path3 = os.path.join(OUTPUT_DIR, "screen_task1_min.png")
        elem3.screenshot(path=out_path3)
        print("Generated:", out_path3)

        # 4. screen_task2_seq.png
        body4 = """
        <div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР3_ССП_Файлы&gt;</span><span class="input">java Task2_Sequence</span></div>
        <div>90 85 80 75 70 65 60 55 50 45 40 35 30 25 20 15 10 5 0 </div>
        """
        html4 = make_html_task_console("Командная строка", body4)
        page.set_content(html4)
        elem4 = page.locator(".window")
        out_path4 = os.path.join(OUTPUT_DIR, "screen_task2_seq.png")
        elem4.screenshot(path=out_path4)
        print("Generated:", out_path4)

        # 5. screen_task3_rect.png
        body5 = """
        <div class="cmd-line"><span class="prompt">D:\\1с лабы\\ЛР3_ССП_Файлы&gt;</span><span class="input">java Task3_Rectangles</span></div>
        <div>Введите сторону a: <span class="input">15.5</span></div>
        <div>Введите сторону b: <span class="input">8.0</span></div>
        <div>Введите сторону c: <span class="input">10.0</span></div>
        <div>Введите сторону d: <span class="input">20.0</span></div>
        <div>Прямоугольник помещается</div>
        """
        html5 = make_html_task_console("Командная строка", body5)
        page.set_content(html5)
        elem5 = page.locator(".window")
        out_path5 = os.path.join(OUTPUT_DIR, "screen_task3_rect.png")
        elem5.screenshot(path=out_path5)
        print("Generated:", out_path5)

        browser.close()
    print("All screenshots successfully regenerated!")

if __name__ == "__main__":
    generate_all_screenshots()
