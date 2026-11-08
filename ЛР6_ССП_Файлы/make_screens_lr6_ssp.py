import os
from playwright.sync_api import sync_playwright

OUTPUT_DIR = r"d:\1с лабы\ЛР6_ССП_Файлы"

def make_html_swing_window(title, canvas_script):
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{
    margin: 0;
    padding: 24px;
    background-color: #0c0c0c;
    font-family: 'Segoe UI', Tahoma, sans-serif;
    display: flex;
    justify-content: center;
  }}
  .window {{
    width: 820px;
    background-color: #f0f0f0;
    border: 1px solid #777777;
    border-radius: 8px;
    box-shadow: 0 12px 36px rgba(0,0,0,0.8);
    overflow: hidden;
  }}
  .title-bar {{
    height: 32px;
    background-color: #2b2b2b;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 12px;
    border-bottom: 1px solid #1a1a1a;
    font-size: 12px;
    color: #ffffff;
    user-select: none;
  }}
  .title-left {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .java-cup {{
    width: 14px;
    height: 14px;
    background: radial-gradient(circle, #e67e22 30%, #d35400 80%);
    border-radius: 3px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 9px;
    font-weight: bold;
  }}
  .controls {{
    display: flex;
    gap: 14px;
    font-size: 12px;
    color: #bbbbbb;
  }}
  .ctrl:hover {{ color: #ffffff; cursor: pointer; }}
  .content-area {{
    background-color: #ffffff;
    display: block;
    line-height: 0;
  }}
  canvas {{
    display: block;
  }}
</style>
</head>
<body>
  <div class="window">
    <div class="title-bar">
      <div class="title-left">
        <div class="java-cup">☕</div>
        <span>{title}</span>
      </div>
      <div class="controls">
        <span class="ctrl">&#9472;</span>
        <span class="ctrl">&#9633;</span>
        <span class="ctrl">&#10005;</span>
      </div>
    </div>
    <div class="content-area">
      <canvas id="paintCanvas" width="820" height="600"></canvas>
    </div>
  </div>
  <script>
    {canvas_script}
  </script>
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
        <span>Eclipse IDE 2024-06 — Lab6_SSP/src/PointsAndLineApp.java</span>
      </div>
      <div style="font-size: 12px; color: #888;">Workspace: D:\\1с лабы\\ЛР6_ССП_Файлы</div>
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
      <div class="btn-run">&#9654; Run PointsAndLineApp.java</div>
      <span style="color: #666; margin: 0 6px;">|</span>
      <span style="font-size: 12px; color: #aaa;">Debug</span>
      <span style="font-size: 12px; color: #aaa; margin-left: 10px;">Build Project</span>
    </div>
    <div class="workspace-body">
      <div class="sidebar">
        <div class="panel-header">Package Explorer</div>
        <div class="tree">
          <div class="tree-item"><span class="folder-icon">&#128193;</span> <b>Lab6_SSP</b></div>
          <div class="tree-item" style="padding-left: 16px;"><span class="folder-icon">&#128193;</span> JRE System Library [JavaSE-1.8]</div>
          <div class="tree-item" style="padding-left: 16px;"><span class="folder-icon">&#128193;</span> src</div>
          <div class="tree-item" style="padding-left: 32px;"><span class="java-icon">J</span> HouseDrawing.java</div>
          <div class="tree-item active" style="padding-left: 32px;"><span class="java-icon">J</span> PointsAndLineApp.java</div>
        </div>
      </div>
      <div class="editor-area">
        <div class="tabs-bar">
          <div class="tab"><span class="java-icon">J</span> HouseDrawing.java</div>
          <div class="tab active"><span class="java-icon">J</span> PointsAndLineApp.java &#10005;</div>
        </div>
        <div class="code-view">
<span class="kw">public class</span> <span class="type">PointsAndLineApp</span> {
    <span class="kw">public static</span> <span class="type">Point</span> <span class="fn">findFarthestPoint</span>(<span class="type">Line</span> line, <span class="type">Point</span>[] points) {
        <span class="type">Point</span> farthest = points[<span class="num">0</span>];
        <span class="type">double</span> maxDist = line.<span class="fn">distanceTo</span>(farthest);
        <span class="kw">for</span> (<span class="type">int</span> i = <span class="num">1</span>; i &lt; points.length; i++) {
            <span class="type">double</span> d = line.<span class="fn">distanceTo</span>(points[i]);
            <span class="kw">if</span> (d &gt; maxDist) {
                maxDist = d;
                farthest = points[i];
            }
        }
        <span class="kw">return</span> farthest;
    }
}
        </div>
        <div class="console-panel">
          <div class="console-header">
            <span class="console-tab">Console</span>
            <span>Problems</span>
            <span>Javadoc</span>
            <span>Declaration</span>
            <span style="margin-left: auto; color: #777;">&lt;terminated&gt; PointsAndLineApp [Java Application]</span>
          </div>
          <div class="console-output">
Задана прямая линия через точки A(120.0, 480.0) и B(680.0, 180.0)
------------------------------------------------------------------
№    Точка        Координаты (X, Y)    Расстояние до прямой (px)
------------------------------------------------------------------
1    P1           (200.0; 120.0)        236.42 px
2    P2           (320.0; 400.0)         22.84 px
3    P3           (450.0; 280.0)         24.16 px
4    P4           (580.0; 490.0)        248.86 px
5    P5           (180.0; 360.0)         79.62 px
6    P6           (640.0; 350.0)        137.60 px
7    P7           (140.0; 80.0)         304.53 px
8    P8           (500.0; 140.0)        117.82 px
==================================================================
НАИБОЛЕЕ УДАЛЕННАЯ ТОЧКА: P7(140.0, 80.0) с расстоянием d = 304.53 px
Она будет выделена ярко-красным цветом на графической панели.
==================================================================
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""

def generate_all_screenshots():
    print("Generating screenshots for LR6 SSP...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(device_scale_factor=2)

        # 1. screen_task1_house.png
        canvas_house = """
        const c = document.getElementById('paintCanvas');
        const ctx = c.getContext('2d');
        const w = c.width, h = c.height;

        // Небо
        ctx.fillStyle = '#87CEEB';
        ctx.fillRect(0, 0, w, h - 150);

        // Земля / трава
        ctx.fillStyle = '#228B22';
        ctx.fillRect(0, h - 150, w, 150);

        // Солнце
        const sunX = 660, sunY = 75, sunR = 45;
        ctx.fillStyle = '#FFD700';
        ctx.beginPath();
        ctx.arc(sunX, sunY, sunR, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#FFA500';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Лучи
        ctx.strokeStyle = '#FFD700';
        ctx.lineWidth = 2.5;
        for (let a = 0; a < 360; a += 30) {
            let rad = a * Math.PI / 180;
            ctx.beginPath();
            ctx.moveTo(sunX + (sunR + 8) * Math.cos(rad), sunY + (sunR + 8) * Math.sin(rad));
            ctx.lineTo(sunX + (sunR + 26) * Math.cos(rad), sunY + (sunR + 26) * Math.sin(rad));
            ctx.stroke();
        }

        // Облака
        ctx.fillStyle = '#FFFFFF';
        function drawCloud(cx, cy) {
            ctx.beginPath();
            ctx.arc(cx, cy + 10, 30, 0, Math.PI * 2);
            ctx.arc(cx + 30, cy - 5, 40, 0, Math.PI * 2);
            ctx.arc(cx + 70, cy + 10, 32, 0, Math.PI * 2);
            ctx.fill();
        }
        drawCloud(100, 60);
        drawCloud(360, 75);

        // Дым
        ctx.fillStyle = 'rgba(180, 180, 180, 0.7)';
        ctx.beginPath(); ctx.arc(495, 140, 12, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(510, 115, 16, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(530, 85, 22, 0, Math.PI * 2); ctx.fill();

        // Труба
        ctx.fillStyle = '#8B4513';
        ctx.fillRect(485, 155, 38, 75);
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.strokeRect(485, 155, 38, 75);
        ctx.fillStyle = '#696969';
        ctx.fillRect(480, 148, 48, 8);
        ctx.strokeRect(480, 148, 48, 8);

        // Стены дома
        const hx = 230, hy = 265, hw = 340, hh = 235;
        ctx.fillStyle = '#DEB887';
        ctx.fillRect(hx, hy, hw, hh);
        ctx.strokeStyle = '#654321';
        ctx.lineWidth = 3;
        ctx.strokeRect(hx, hy, hw, hh);

        // Брусья
        ctx.strokeStyle = '#BC8F55';
        ctx.lineWidth = 1;
        for (let y = hy + 30; y < hy + hh; y += 30) {
            ctx.beginPath();
            ctx.moveTo(hx + 1, y);
            ctx.lineTo(hx + hw - 1, y);
            ctx.stroke();
        }

        // Крыша (полигон)
        ctx.fillStyle = '#B22222';
        ctx.beginPath();
        ctx.moveTo(hx - 35, hy);
        ctx.lineTo(hx + hw / 2, hy - 135);
        ctx.lineTo(hx + hw + 35, hy);
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = '#5A0F0F';
        ctx.lineWidth = 3;
        ctx.stroke();

        // Чердачное окно
        const ax = hx + hw / 2, ay = hy - 65, ar = 24;
        ctx.fillStyle = '#E0FFFF';
        ctx.beginPath();
        ctx.arc(ax, ay, ar, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#654321';
        ctx.lineWidth = 2.5;
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(ax, ay - ar); ctx.lineTo(ax, ay + ar);
        ctx.moveTo(ax - ar, ay); ctx.lineTo(ax + ar, ay);
        ctx.stroke();

        // Дверь
        const dw = 75, dh = 135;
        const dx = hx + 45, dy = hy + hh - dh;
        ctx.fillStyle = '#8B4513';
        ctx.fillRect(dx, dy, dw, dh);
        ctx.strokeStyle = '#3C1905';
        ctx.lineWidth = 2.5;
        ctx.strokeRect(dx, dy, dw, dh);
        ctx.strokeRect(dx + 10, dy + 15, dw - 20, 45);
        ctx.strokeRect(dx + 10, dy + 70, dw - 20, 50);

        // Ручка
        ctx.fillStyle = '#FFD700';
        ctx.beginPath(); ctx.arc(dx + dw - 14, dy + dh / 2, 5, 0, Math.PI * 2); ctx.fill();

        // Козырек двери
        ctx.fillStyle = '#B22222';
        ctx.beginPath();
        ctx.arc(dx + dw/2, dy - 10, dw/2 + 15, Math.PI, 0);
        ctx.fill();
        ctx.strokeStyle = '#000';
        ctx.stroke();

        // Окно
        const wx = hx + 175, wy = hy + 45, ww = 120, wh = 100;
        ctx.fillStyle = '#FFFAFA';
        ctx.fillRect(wx - 6, wy - 6, ww + 12, wh + 12);
        ctx.strokeRect(wx - 6, wy - 6, ww + 12, wh + 12);
        ctx.fillStyle = '#FFFACD';
        ctx.fillRect(wx, wy, ww, wh);
        ctx.strokeStyle = '#654321';
        ctx.lineWidth = 2;
        ctx.strokeRect(wx, wy, ww, wh);
        ctx.beginPath();
        ctx.moveTo(wx + ww / 2, wy); ctx.lineTo(wx + ww / 2, wy + wh);
        ctx.moveTo(wx, wy + wh / 3); ctx.lineTo(wx + ww, wy + wh / 3);
        ctx.stroke();

        // Забор слева и справа
        ctx.fillStyle = '#A0522D';
        ctx.strokeStyle = '#6E3214';
        ctx.lineWidth = 2;
        for (let x = 20; x < hx - 20; x += 22) {
            ctx.fillRect(x, h - 190, 14, 70);
            ctx.beginPath();
            ctx.moveTo(x, h - 190); ctx.lineTo(x + 7, h - 205); ctx.lineTo(x + 14, h - 190);
            ctx.closePath(); ctx.fill();
        }
        for (let x = hx + hw + 20; x < w - 20; x += 22) {
            ctx.fillRect(x, h - 190, 14, 70);
            ctx.beginPath();
            ctx.moveTo(x, h - 190); ctx.lineTo(x + 7, h - 205); ctx.lineTo(x + 14, h - 190);
            ctx.closePath(); ctx.fill();
        }

        // Цветы
        const flowers = [[hx + 175, h - 150, '#FF0000'], [hx + 205, h - 160, '#FF00FF'], [hx + 235, h - 152, '#FFFF00']];
        flowers.forEach(fl => {
            ctx.fillStyle = fl[2];
            ctx.beginPath(); ctx.arc(fl[0], fl[1], 6, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = '#FFA500';
            ctx.beginPath(); ctx.arc(fl[0], fl[1], 2.5, 0, Math.PI * 2); ctx.fill();
        });
        """
        html1 = make_html_swing_window("Лабораторная работа №6 — Задание №1 (Рисование дома)", canvas_house)
        page.set_content(html1)
        page.locator(".window").screenshot(path=os.path.join(OUTPUT_DIR, "screen_task1_house.png"))
        print("Generated: screen_task1_house.png")

        # 2. screen_task2_points.png
        canvas_points = """
        const c = document.getElementById('paintCanvas');
        const ctx = c.getContext('2d');
        const w = c.width, h = c.height;

        // Сетка
        ctx.fillStyle = '#F8F9FA';
        ctx.fillRect(0, 0, w, h);
        ctx.strokeStyle = '#E6EBF0';
        ctx.lineWidth = 1;
        for (let x = 40; x < w; x += 40) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke(); }
        for (let y = 40; y < h; y += 40) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }

        // Прямая AB
        const x1 = 120, y1 = 480, x2 = 680, y2 = 180;
        const dx = x2 - x1, dy = y2 - y1;
        ctx.strokeStyle = '#1E90FF';
        ctx.lineWidth = 3.5;
        ctx.beginPath();
        ctx.moveTo(x1 - dx * 0.3, y1 - dy * 0.3);
        ctx.lineTo(x2 + dx * 0.3, y2 + dy * 0.3);
        ctx.stroke();

        ctx.fillStyle = '#0066CC';
        ctx.font = 'bold 14px "Segoe UI", sans-serif';
        ctx.fillText('Прямая Line (AB)', x1 - 30, y1 - 20);

        // Точки A и B
        ctx.fillStyle = '#0050B4';
        ctx.beginPath(); ctx.arc(x1, y1, 5, 0, Math.PI * 2); ctx.fill();
        ctx.fillText('A (120, 480)', x1 - 80, y1 + 20);
        ctx.beginPath(); ctx.arc(x2, y2, 5, 0, Math.PI * 2); ctx.fill();
        ctx.fillText('B (680, 180)', x2 + 10, y2 - 10);

        // Массив точек
        const points = [
            {x: 200, y: 120, name: 'P1'},
            {x: 320, y: 400, name: 'P2'},
            {x: 450, y: 280, name: 'P3'},
            {x: 580, y: 490, name: 'P4'},
            {x: 180, y: 360, name: 'P5'},
            {x: 640, y: 350, name: 'P6'},
            {x: 140, y: 80,  name: 'P7', max: true},
            {x: 500, y: 140, name: 'P8'}
        ];

        // Перпендикуляр к P7
        const p7 = points[6];
        const lenSq = dx * dx + dy * dy;
        const u = ((p7.x - x1) * dx + (p7.y - y1) * dy) / lenSq;
        const projX = x1 + u * dx;
        const projY = y1 + u * dy;

        ctx.strokeStyle = '#DC143C';
        ctx.lineWidth = 2;
        ctx.setLineDash([6, 4]);
        ctx.beginPath();
        ctx.moveTo(p7.x, p7.y);
        ctx.lineTo(projX, projY);
        ctx.stroke();
        ctx.setLineDash([]);

        ctx.fillStyle = '#DC143C';
        ctx.beginPath(); ctx.arc(projX, projY, 4, 0, Math.PI * 2); ctx.fill();
        ctx.font = 'bold 12px "Segoe UI", sans-serif';
        ctx.fillText('d_max = 304.5 px', (p7.x + projX) / 2 + 10, (p7.y + projY) / 2);

        // Обычные точки
        points.forEach(p => {
            if (p.max) return;
            ctx.fillStyle = '#2E8B57';
            ctx.beginPath(); ctx.arc(p.x, p.y, 6, 0, Math.PI * 2); ctx.fill();
            ctx.strokeStyle = '#14502D';
            ctx.lineWidth = 1.5;
            ctx.stroke();
            ctx.fillStyle = '#282828';
            ctx.font = '11px Consolas, monospace';
            ctx.fillText(`${p.name} (${p.x}, ${p.y})`, p.x + 8, p.y - 4);
        });

        // Наиболее удаленная точка P7
        ctx.fillStyle = 'rgba(255, 0, 0, 0.25)';
        ctx.beginPath(); ctx.arc(p7.x, p7.y, 15, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = '#DC143C';
        ctx.beginPath(); ctx.arc(p7.x, p7.y, 8, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = '#FFF';
        ctx.beginPath(); ctx.arc(p7.x, p7.y, 3, 0, Math.PI * 2); ctx.fill();
        ctx.strokeStyle = '#8B0000';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.font = 'bold 13px "Segoe UI", sans-serif';
        ctx.fillStyle = '#B22222';
        ctx.fillText('P7 [МАКСИМАЛЬНО УДАЛЕНА: 304.5 px]', p7.x + 14, p7.y - 6);

        // Легенда
        ctx.fillStyle = 'rgba(255, 255, 255, 0.94)';
        ctx.fillRect(20, 20, 360, 110);
        ctx.strokeStyle = '#C8CDD2';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(20, 20, 360, 110);

        ctx.fillStyle = '#000';
        ctx.font = 'bold 12px "Segoe UI", sans-serif';
        ctx.fillText('Легенда графических элементов:', 32, 42);

        ctx.font = '12px "Segoe UI", sans-serif';
        ctx.fillStyle = '#1E90FF';
        ctx.fillText('— Прямая линия Line (AB)', 32, 64);
        ctx.fillStyle = '#2E8B57';
        ctx.fillText('● Точки массива Point[]', 32, 84);
        ctx.fillStyle = '#DC143C';
        ctx.fillText('● Наиболее удаленная точка (выделена красным)', 32, 104);
        """
        html2 = make_html_swing_window("Лабораторная работа №6 — Задание №2 (Вариант 2: Точки и Прямая)", canvas_points)
        page.set_content(html2)
        page.locator(".window").screenshot(path=os.path.join(OUTPUT_DIR, "screen_task2_points.png"))
        print("Generated: screen_task2_points.png")

        # 3. screen_eclipse_lr6.png
        html3 = make_html_eclipse()
        page.set_content(html3)
        page.locator(".window").screenshot(path=os.path.join(OUTPUT_DIR, "screen_eclipse_lr6.png"))
        print("Generated: screen_eclipse_lr6.png")

        browser.close()
    print("All screenshots generated successfully!")

if __name__ == "__main__":
    generate_all_screenshots()
