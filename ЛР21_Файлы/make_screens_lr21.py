#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_screens_lr21.py
--------------------
Generates high-resolution, realistic screenshots for Computer Networks Lab 21:
Cisco Packet Tracer modeling and configuration.
"""

import os
from playwright.sync_api import sync_playwright

OUTPUT_DIR = r"d:\1с лабы\ЛР21_Файлы"

def make_cisco_pt_frame(title, content_html, active_tab="Logical", time_str="00:15:32"):
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{
    margin: 0;
    padding: 16px;
    background-color: #1a1a1a;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    display: flex;
    justify-content: center;
  }}
  .pt-window {{
    width: 1020px;
    background-color: #f0f0f0;
    border: 1px solid #707070;
    box-shadow: 0 8px 24px rgba(0,0,0,0.6);
    display: flex;
    flex-direction: column;
  }}
  .pt-titlebar {{
    height: 30px;
    background: linear-gradient(to bottom, #ffffff 0%, #e1e1e1 100%);
    border-bottom: 1px solid #b0b0b0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 10px;
    font-size: 12px;
    color: #333333;
    font-weight: 500;
  }}
  .pt-menubar {{
    height: 24px;
    background: #f8f8f8;
    border-bottom: 1px solid #dcdcdc;
    display: flex;
    align-items: center;
    padding: 0 8px;
    font-size: 11px;
    color: #222;
    gap: 14px;
  }}
  .pt-toolbar {{
    height: 36px;
    background: #eaeaea;
    border-bottom: 1px solid #cccccc;
    display: flex;
    align-items: center;
    padding: 0 10px;
    gap: 12px;
    font-size: 11px;
  }}
  .tool-btn {{
    padding: 3px 8px;
    background: #fafafa;
    border: 1px solid #b5b5b5;
    border-radius: 3px;
    cursor: default;
    display: flex;
    align-items: center;
    gap: 4px;
  }}
  .pt-workspace-tabs {{
    height: 28px;
    background: #d8d8d8;
    display: flex;
    align-items: flex-end;
    padding: 0 10px;
    gap: 4px;
    border-bottom: 1px solid #b0b0b0;
  }}
  .ws-tab {{
    padding: 4px 16px;
    font-size: 11px;
    border: 1px solid #b0b0b0;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    background: #e2e2e2;
    color: #555;
  }}
  .ws-tab.active {{
    background: #ffffff;
    color: #000;
    font-weight: bold;
    border-top: 2px solid #0066cc;
  }}
  .pt-canvas {{
    background-color: #ffffff;
    position: relative;
    overflow: hidden;
  }}
  .pt-bottom {{
    height: 110px;
    background: #e6e6e6;
    border-top: 1px solid #b5b5b5;
    display: flex;
  }}
  .pt-devices-catalog {{
    width: 280px;
    border-right: 1px solid #cccccc;
    padding: 6px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-size: 11px;
  }}
  .device-row {{
    display: flex;
    gap: 8px;
  }}
  .device-icon {{
    padding: 3px 6px;
    background: #fff;
    border: 1px solid #ccc;
    border-radius: 2px;
    font-size: 10px;
    display: flex;
    align-items: center;
    gap: 4px;
  }}
  .pt-realtime-box {{
    margin-left: auto;
    padding: 10px 16px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-end;
    font-size: 11px;
    color: #333;
    border-left: 1px solid #ccc;
    background: #f2f2f2;
  }}
  .mode-indicator {{
    font-weight: bold;
    color: #008800;
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .mode-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #00bb00;
  }}
</style>
</head>
<body>
<div class="pt-window">
  <div class="pt-titlebar">
    <div style="display:flex;align-items:center;gap:6px;">
      <span style="font-weight:bold;color:#0055aa;">Cisco Packet Tracer</span>
      <span style="color:#777;">- [Лабораторная_работа_21_РС02-23.pkt]</span>
    </div>
    <div style="font-size:11px;color:#666;">Версия 8.2.1 | Лабынцев Денис</div>
  </div>
  <div class="pt-menubar">
    <span>File</span><span>Edit</span><span>Options</span><span>View</span><span>Tools</span><span>Extensions</span><span>Help</span>
  </div>
  <div class="pt-toolbar">
    <div class="tool-btn">Новый</div>
    <div class="tool-btn">Открыть</div>
    <div class="tool-btn">Сохранить</div>
    <div class="tool-btn">Печать</div>
    <div style="width:1px;height:20px;background:#ccc;margin:0 4px;"></div>
    <div class="tool-btn" style="background:#eef6ff;border-color:#0077dd;color:#0055bb;font-weight:bold;">Логическая топология</div>
    <div class="tool-btn">Физическая топология</div>
    <div style="width:1px;height:20px;background:#ccc;margin:0 4px;"></div>
    <div class="tool-btn">Выделение</div>
    <div class="tool-btn">Удалить</div>
    <div class="tool-btn">Заметка</div>
  </div>
  <div class="pt-workspace-tabs">
    <div class="ws-tab active">Logical Workspace [Root]</div>
    <div class="ws-tab">Physical Workspace</div>
  </div>
  <div class="pt-canvas">
    {content_html}
  </div>
  <div class="pt-bottom">
    <div class="pt-devices-catalog">
      <div style="font-weight:bold;color:#444;">Каталог сетевого оборудования:</div>
      <div class="device-row">
        <div class="device-icon"><b>R</b> Routers (1841)</div>
        <div class="device-icon"><b>SW</b> Switches (2950-24)</div>
        <div class="device-icon"><b>W</b> Wireless (AccessPoint)</div>
      </div>
      <div class="device-row">
        <div class="device-icon"><b>PC</b> End Devices</div>
        <div class="device-icon"><b>SRV</b> Server-PT</div>
        <div class="device-icon"><b>C</b> Connections</div>
      </div>
    </div>
    <div style="padding:10px 14px;font-size:11px;color:#555;display:flex;flex-direction:column;justify-content:center;">
      <div><b>Типы используемых кабелей:</b></div>
      <div style="margin-top:4px;">- Медный прямой кабель (Copper Straight-Through): Хосты &rarr; Коммутаторы</div>
      <div>- Медный кроссовер (Copper Cross-over): Соединение коммутаторов</div>
      <div>- Последовательный кабель (Serial DCE/DTE): Router-Main &harr; Router-Branch (10.0.0.0/30)</div>
    </div>
    <div class="pt-realtime-box">
      <div class="mode-indicator"><span class="mode-dot"></span> Режим: Realtime</div>
      <div style="margin-top:4px;color:#666;">Время работы симуляции: {time_str}</div>
      <div style="margin-top:4px;color:#0066cc;">Simulation Mode [Shift+S]</div>
    </div>
  </div>
</div>
</body>
</html>"""

def make_cli_window(title, terminal_content):
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{
    margin: 0;
    padding: 24px;
    background-color: #121212;
    font-family: 'Segoe UI', Tahoma, sans-serif;
    display: flex;
    justify-content: center;
  }}
  .cli-window {{
    width: 900px;
    background-color: #1e1e1e;
    border: 1px solid #444;
    border-radius: 6px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.75);
    overflow: hidden;
  }}
  .cli-titlebar {{
    height: 32px;
    background: #2d2d2d;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 12px;
    border-bottom: 1px solid #3c3c3c;
    font-size: 12px;
    color: #ddd;
    user-select: none;
  }}
  .cli-tabs {{
    height: 28px;
    background: #252525;
    display: flex;
    border-bottom: 1px solid #3c3c3c;
    padding: 0 10px;
    gap: 4px;
  }}
  .cli-tab {{
    padding: 4px 12px;
    font-size: 11px;
    color: #888;
    background: #252525;
    border: 1px solid transparent;
  }}
  .cli-tab.active {{
    color: #fff;
    background: #1e1e1e;
    border-color: #3c3c3c;
    border-bottom-color: #1e1e1e;
    font-weight: bold;
  }}
  .terminal-area {{
    padding: 16px 20px;
    background: #0c0c0c;
    color: #00ff66;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.45;
    white-space: pre-wrap;
    min-height: 440px;
  }}
</style>
</head>
<body>
<div class="cli-window">
  <div class="cli-titlebar">
    <span><b>{title}</b> - Cisco IOS Command Line Interface</span>
    <span style="color:#aaa;font-size:11px;">Packet Tracer Device Configuration</span>
  </div>
  <div class="cli-tabs">
    <div class="cli-tab">Physical</div>
    <div class="cli-tab">Config</div>
    <div class="cli-tab active">CLI</div>
    <div class="cli-tab">Attributes</div>
  </div>
  <div class="terminal-area">{terminal_content}</div>
</div>
</body>
</html>"""

def generate_screenshots():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")
        page = browser.new_page(viewport={"width": 1100, "height": 850})

        # 1. screen_pt_interface.png
        html1_content = """
        <div style="height:440px;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#fcfcfc;">
          <div style="width:840px;height:360px;border:2px dashed #b0c4de;background:#f8fbff;border-radius:8px;padding:24px;box-sizing:border-box;display:flex;flex-direction:column;align-items:center;justify-content:center;">
            <div style="font-size:20px;font-weight:bold;color:#004488;margin-bottom:12px;">Рабочая область Cisco Packet Tracer (Logical Workspace)</div>
            <div style="font-size:13px;color:#555;text-align:center;max-width:680px;line-height:1.6;">
              Интерфейс эмулятора включает главное меню управления файлами и проектами, верхнюю панель быстрого доступа, переключатель логической и физической топологии, интерактивную рабочую область моделирования, палитру сетевого оборудования (коммутаторы, маршрутизаторы, оконечные устройства, кабельные соединения) и переключатель режимов реального времени (Real-Time) и симуляции (Simulation).
            </div>
            <div style="display:flex;gap:20px;margin-top:28px;">
              <div style="padding:12px 20px;background:#fff;border:1px solid #c0d0e0;border-radius:6px;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,0.05);">
                <div style="font-weight:bold;color:#0066cc;font-size:14px;">1. Главное меню</div>
                <div style="font-size:11px;color:#777;margin-top:4px;">Файлы, настройки, масштабирование</div>
              </div>
              <div style="padding:12px 20px;background:#fff;border:1px solid #c0d0e0;border-radius:6px;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,0.05);">
                <div style="font-weight:bold;color:#008844;font-size:14px;">2. Рабочая область</div>
                <div style="font-size:11px;color:#777;margin-top:4px;">Размещение и монтаж топологии</div>
              </div>
              <div style="padding:12px 20px;background:#fff;border:1px solid #c0d0e0;border-radius:6px;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,0.05);">
                <div style="font-weight:bold;color:#cc5500;font-size:14px;">3. Панель устройств</div>
                <div style="font-size:11px;color:#777;margin-top:4px;">Routers, Switches, End Devices, Cables</div>
              </div>
            </div>
          </div>
        </div>
        """
        html1 = make_cisco_pt_frame("Cisco Packet Tracer - Интерфейс", html1_content, time_str="00:03:15")
        page.set_content(html1)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "screen_pt_interface.png"))
        print("[1/6] Generated screen_pt_interface.png")

        # 2. screen_topology_fig32.png
        html2_content = """
        <div style="height:480px;background:#ffffff;position:relative;padding:20px;box-sizing:border-box;">
          <!-- SVG Connections -->
          <svg style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;">
            <!-- Serial Link Main to Branch -->
            <line x1="340" y1="95" x2="680" y2="95" stroke="#cc0000" stroke-width="3" stroke-dasharray="6,4" />
            <text x="500" y="85" fill="#cc0000" font-size="11" font-weight="bold" text-anchor="middle">Serial0/0/0 (10.0.0.0/30)</text>
            <circle cx="340" cy="95" r="4" fill="#00bb00" />
            <circle cx="680" cy="95" r="4" fill="#00bb00" />

            <!-- Main Office LAN Links -->
            <line x1="300" y1="120" x2="300" y2="210" stroke="#000000" stroke-width="2" />
            <circle cx="300" cy="125" r="4" fill="#00bb00" />
            <circle cx="300" cy="205" r="4" fill="#00bb00" />

            <line x1="280" y1="230" x2="140" y2="340" stroke="#000000" stroke-width="2" />
            <circle cx="275" cy="235" r="4" fill="#00bb00" />
            <circle cx="145" cy="335" r="4" fill="#00bb00" />

            <line x1="290" y1="235" x2="220" y2="340" stroke="#000000" stroke-width="2" />
            <circle cx="288" cy="240" r="4" fill="#00bb00" />
            <circle cx="222" cy="335" r="4" fill="#00bb00" />

            <line x1="310" y1="235" x2="300" y2="340" stroke="#000000" stroke-width="2" />
            <circle cx="310" cy="240" r="4" fill="#00bb00" />
            <circle cx="300" cy="335" r="4" fill="#00bb00" />

            <line x1="320" y1="230" x2="400" y2="340" stroke="#000000" stroke-width="2" />
            <circle cx="325" cy="235" r="4" fill="#00bb00" />
            <circle cx="395" cy="335" r="4" fill="#00bb00" />

            <!-- Branch Office LAN Links -->
            <line x1="720" y1="120" x2="720" y2="210" stroke="#000000" stroke-width="2" />
            <circle cx="720" cy="125" r="4" fill="#00bb00" />
            <circle cx="720" cy="205" r="4" fill="#00bb00" />

            <line x1="700" y1="230" x2="620" y2="340" stroke="#000000" stroke-width="2" />
            <circle cx="695" cy="235" r="4" fill="#00bb00" />
            <circle cx="625" cy="335" r="4" fill="#00bb00" />

            <line x1="710" y1="235" x2="700" y2="340" stroke="#000000" stroke-width="2" />
            <circle cx="710" cy="240" r="4" fill="#00bb00" />
            <circle cx="700" cy="335" r="4" fill="#00bb00" />

            <line x1="730" y1="235" x2="780" y2="340" stroke="#000000" stroke-width="2" />
            <circle cx="730" cy="240" r="4" fill="#00bb00" />
            <circle cx="775" cy="335" r="4" fill="#00bb00" />

            <line x1="740" y1="230" x2="860" y2="340" stroke="#000000" stroke-width="2" />
            <circle cx="745" cy="235" r="4" fill="#00bb00" />
            <circle cx="855" cy="335" r="4" fill="#00bb00" />
          </svg>

          <!-- Main Office Container Box -->
          <div style="position:absolute;left:80px;top:40px;width:380px;height:390px;border:2px dashed #0077cc;border-radius:8px;background:rgba(235,245,255,0.4);padding:8px;">
            <span style="font-weight:bold;color:#0055aa;font-size:12px;background:#fff;padding:2px 8px;border-radius:4px;border:1px solid #0077cc;">Главный офис (192.168.10.0/24)</span>
          </div>

          <!-- Branch Office Container Box -->
          <div style="position:absolute;left:560px;top:40px;width:380px;height:390px;border:2px dashed #009944;border-radius:8px;background:rgba(235,255,240,0.4);padding:8px;">
            <span style="font-weight:bold;color:#007733;font-size:12px;background:#fff;padding:2px 8px;border-radius:4px;border:1px solid #009944;">Дополнительный офис (192.168.20.0/24)</span>
          </div>

          <!-- Router Main -->
          <div style="position:absolute;left:265px;top:70px;text-align:center;">
            <div style="width:70px;height:40px;background:#2b5b84;border-radius:20px;border:2px solid #1a3c5a;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:11px;margin:0 auto;box-shadow:0 3px 6px rgba(0,0,0,0.2);">1841</div>
            <div style="font-size:11px;font-weight:bold;margin-top:2px;">Router-Main</div>
            <div style="font-size:9px;color:#666;">192.168.10.1</div>
          </div>

          <!-- Switch Main -->
          <div style="position:absolute;left:270px;top:200px;text-align:center;">
            <div style="width:60px;height:24px;background:#4a708b;border:1px solid #334e62;color:#fff;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:bold;margin:0 auto;">2950-24</div>
            <div style="font-size:11px;font-weight:bold;margin-top:2px;">Switch-Main</div>
          </div>

          <!-- Main Office Hosts -->
          <div style="position:absolute;left:105px;top:335px;text-align:center;">
            <div style="width:44px;height:36px;background:#e8edf2;border:2px solid #5a7b98;border-radius:4px;margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:10px;">PC</div>
            <div style="font-size:10px;font-weight:bold;">PC0</div>
            <div style="font-size:8.5px;color:#555;">.10.10</div>
          </div>
          <div style="position:absolute;left:190px;top:335px;text-align:center;">
            <div style="width:44px;height:36px;background:#e8edf2;border:2px solid #5a7b98;border-radius:4px;margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:10px;">PC</div>
            <div style="font-size:10px;font-weight:bold;">PC1</div>
            <div style="font-size:8.5px;color:#555;">.10.11</div>
          </div>
          <div style="position:absolute;left:275px;top:335px;text-align:center;">
            <div style="width:44px;height:36px;background:#e8edf2;border:2px solid #5a7b98;border-radius:4px;margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:10px;">PC</div>
            <div style="font-size:10px;font-weight:bold;">PC2-Main</div>
            <div style="font-size:8.5px;color:#555;">.10.12</div>
          </div>
          <div style="position:absolute;left:370px;top:335px;text-align:center;">
            <div style="width:44px;height:44px;background:#dce6f0;border:2px solid #336699;border-radius:4px;margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:9px;">SRV</div>
            <div style="font-size:10px;font-weight:bold;">Server0</div>
            <div style="font-size:8.5px;color:#555;">.10.2 (Главн)</div>
          </div>

          <!-- Router Branch -->
          <div style="position:absolute;left:685px;top:70px;text-align:center;">
            <div style="width:70px;height:40px;background:#2b5b84;border-radius:20px;border:2px solid #1a3c5a;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:11px;margin:0 auto;box-shadow:0 3px 6px rgba(0,0,0,0.2);">1841</div>
            <div style="font-size:11px;font-weight:bold;margin-top:2px;">Router-Branch</div>
            <div style="font-size:9px;color:#666;">192.168.20.1</div>
          </div>

          <!-- Switch Branch -->
          <div style="position:absolute;left:690px;top:200px;text-align:center;">
            <div style="width:60px;height:24px;background:#4a708b;border:1px solid #334e62;color:#fff;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:bold;margin:0 auto;">2950-24</div>
            <div style="font-size:11px;font-weight:bold;margin-top:2px;">Switch-Branch</div>
          </div>

          <!-- Branch Office Hosts -->
          <div style="position:absolute;left:595px;top:335px;text-align:center;">
            <div style="width:44px;height:36px;background:#e8edf2;border:2px solid #5a7b98;border-radius:4px;margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:10px;">PC</div>
            <div style="font-size:10px;font-weight:bold;">PC2-Branch</div>
            <div style="font-size:8.5px;color:#555;">.20.10</div>
          </div>
          <div style="position:absolute;left:675px;top:335px;text-align:center;">
            <div style="width:44px;height:36px;background:#e8edf2;border:2px solid #5a7b98;border-radius:4px;margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:10px;">PC</div>
            <div style="font-size:10px;font-weight:bold;">PC3</div>
            <div style="font-size:8.5px;color:#555;">.20.11</div>
          </div>
          <div style="position:absolute;left:755px;top:335px;text-align:center;">
            <div style="width:44px;height:44px;background:#dce6f0;border:2px solid #336699;border-radius:4px;margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:9px;">DNS</div>
            <div style="font-size:10px;font-weight:bold;">Server1</div>
            <div style="font-size:8.5px;color:#555;">.20.2 (DNS)</div>
          </div>
          <div style="position:absolute;left:835px;top:335px;text-align:center;">
            <div style="width:44px;height:44px;background:#dce6f0;border:2px solid #336699;border-radius:4px;margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:9px;">WEB</div>
            <div style="font-size:10px;font-weight:bold;">Server2</div>
            <div style="font-size:8.5px;color:#555;">.20.3 (HTTP)</div>
          </div>
        </div>
        """
        html2 = make_cisco_pt_frame("Топология сети главного и дополнительного офисов", html2_content, time_str="00:28:40")
        page.set_content(html2)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "screen_topology_fig32.png"))
        print("[2/6] Generated screen_topology_fig32.png")

        # 3. screen_wireless_devices.png
        html3_content = """
        <div style="height:480px;background:#ffffff;position:relative;padding:20px;box-sizing:border-box;">
          <svg style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;">
            <!-- Connection Switch-Main to AccessPoint -->
            <line x1="450" y1="240" x2="320" y2="150" stroke="#000000" stroke-width="2" />
            <circle cx="445" cy="235" r="4" fill="#00bb00" />
            <circle cx="325" cy="155" r="4" fill="#00bb00" />

            <!-- Wired link Server to Switch-Main -->
            <line x1="560" y1="90" x2="470" y2="235" stroke="#000000" stroke-width="2" />
            <circle cx="555" cy="95" r="4" fill="#00bb00" />
            <circle cx="475" cy="230" r="4" fill="#00bb00" />

            <!-- Wireless waves AP to LaptopPT -->
            <path d="M 300 130 A 40 40 0 0 0 250 170" fill="none" stroke="#2299ee" stroke-width="2" stroke-dasharray="4,3" />
            <path d="M 290 120 A 60 60 0 0 0 230 180" fill="none" stroke="#2299ee" stroke-width="2" stroke-dasharray="4,3" />

            <!-- Wireless waves AP to Server -->
            <path d="M 340 130 A 40 40 0 0 1 450 110" fill="none" stroke="#2299ee" stroke-width="2" stroke-dasharray="4,3" />
            <path d="M 350 120 A 60 60 0 0 1 480 95" fill="none" stroke="#2299ee" stroke-width="2" stroke-dasharray="4,3" />

            <!-- Wireless waves AP to PDA-PT -->
            <path d="M 310 160 A 40 40 0 0 1 340 230" fill="none" stroke="#2299ee" stroke-width="2" stroke-dasharray="4,3" />
          </svg>

          <!-- Highlight Box for Wireless Segment -->
          <div style="position:absolute;left:100px;top:40px;width:780px;height:380px;border:2px dashed #0088cc;border-radius:10px;background:rgba(240,248,255,0.4);padding:10px;">
            <span style="font-weight:bold;color:#0066aa;font-size:12px;background:#fff;padding:4px 10px;border-radius:4px;border:1px solid #0088cc;">Беспроводной сегмент сети WLAN (SSID: Default, 192.168.10.0/24)</span>
          </div>

          <!-- Access Point -->
          <div style="position:absolute;left:290px;top:125px;text-align:center;">
            <div style="width:50px;height:30px;background:#3a87ad;border-radius:4px;border:2px solid #205876;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:10px;margin:0 auto;">AP</div>
            <div style="font-size:11px;font-weight:bold;margin-top:2px;">AccessPoint0</div>
            <div style="font-size:9px;color:#555;">Port 0 -> Fa0/6 (Switch)</div>
          </div>

          <!-- Switch Main -->
          <div style="position:absolute;left:435px;top:235px;text-align:center;">
            <div style="width:65px;height:24px;background:#4a708b;border:1px solid #334e62;color:#fff;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:bold;margin:0 auto;">2950-24</div>
            <div style="font-size:11px;font-weight:bold;margin-top:2px;">Switch-Main</div>
            <div style="font-size:9px;color:#666;">(Порт Fa0/6 - AP, Fa0/7 - Server)</div>
          </div>

          <!-- LaptopPT -->
          <div style="position:absolute;left:140px;top:180px;text-align:center;">
            <div style="width:48px;height:36px;background:#eef2f5;border:2px solid #0077cc;border-radius:4px;margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:10px;color:#0077cc;">Laptop</div>
            <div style="font-size:11px;font-weight:bold;color:#0055bb;margin-top:2px;">LaptopPT</div>
            <div style="font-size:9px;color:#444;">WPC300N (Wireless)</div>
            <div style="font-size:9px;color:#008800;font-weight:bold;">192.168.10.51/24</div>
          </div>

          <!-- Dual-Homed Server (Wireless + Wired) -->
          <div style="position:absolute;left:550px;top:70px;text-align:center;">
            <div style="width:54px;height:50px;background:#e6f0fa;border:2px solid #008844;border-radius:6px;margin:0 auto;display:flex;flex-direction:column;align-items:center;justify-content:center;font-weight:bold;font-size:9px;color:#007733;">
              <span>SRV</span>
              <span style="font-size:7px;color:#666;">Wired+WiFi</span>
            </div>
            <div style="font-size:11px;font-weight:bold;color:#007733;margin-top:2px;">Server (Новый)</div>
            <div style="font-size:9px;color:#444;">Проводное: 192.168.10.5</div>
            <div style="font-size:9px;color:#008800;">Беспроводное: 192.168.10.52</div>
          </div>

          <!-- PDA-PT -->
          <div style="position:absolute;left:320px;top:280px;text-align:center;">
            <div style="width:36px;height:44px;background:#f5eef2;border:2px solid #884477;border-radius:6px;margin:0 auto;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:9px;color:#884477;">PDA</div>
            <div style="font-size:11px;font-weight:bold;margin-top:2px;">PDA-PT</div>
            <div style="font-size:9px;color:#444;">192.168.10.50</div>
            <div style="font-size:8.5px;color:#666;">DNS: 192.168.20.2</div>
          </div>
        </div>
        """
        html3 = make_cisco_pt_frame("Схема сети с добавлением беспроводных устройств", html3_content, time_str="00:42:10")
        page.set_content(html3)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "screen_wireless_devices.png"))
        print("[3/6] Generated screen_wireless_devices.png")

        # 4. screen_cli_config.png
        terminal_cli = """Router>enable
Router#configure terminal
Enter configuration commands, one per line.  End with CNTL/Z.
Router(config)#hostname Router-Main
Router-Main(config)#banner motd #
=====================================================
  Cisco 1841 Router - Main Office Gateway
  Authorized Access Only! Network Lab 21 PC02-23
=====================================================
#
Router-Main(config)#enable secret cisco
Router-Main(config)#line con 0
Router-Main(config-line)#password cisco
Router-Main(config-line)#login
Router-Main(config-line)#exit
Router-Main(config)#line vty 0 4
Router-Main(config-line)#password cisco
Router-Main(config-line)#login
Router-Main(config-line)#exit
Router-Main(config)#interface FastEthernet0/0
Router-Main(config-if)#description LAN_Connection_to_Switch-Main
Router-Main(config-if)#ip address 192.168.10.1 255.255.255.0
Router-Main(config-if)#no shutdown
%LINK-5-CHANGED: Interface FastEthernet0/0, changed state to up
%LINEPROTO-5-UPDOWN: Line protocol on Interface FastEthernet0/0, changed state to up
Router-Main(config-if)#exit
Router-Main(config)#interface Serial0/0/0
Router-Main(config-if)#description WAN_Link_to_Branch_Office_Router
Router-Main(config-if)#ip address 10.0.0.1 255.255.255.252
Router-Main(config-if)#clock rate 64000
Router-Main(config-if)#no shutdown
%LINK-5-CHANGED: Interface Serial0/0/0, changed state to up
%LINEPROTO-5-UPDOWN: Line protocol on Interface Serial0/0/0, changed state to up
Router-Main(config-if)#exit
Router-Main(config)#ip route 192.168.20.0 255.255.255.0 10.0.0.2
Router-Main(config)#end
Router-Main#"""
        html4 = make_cli_window("Router-Main (1841) - Конфигурирование параметров узла", terminal_cli)
        page.set_content(html4)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "screen_cli_config.png"))
        print("[4/6] Generated screen_cli_config.png")

        # 5. screen_nvram_save.png
        terminal_nvram = """Router-Main#copy running-config startup-config
Destination filename [startup-config]? 
Building configuration...
[OK]
Router-Main#show running-config
Building configuration...

Current configuration : 1084 bytes
!
version 12.4
no service password-encryption
!
hostname Router-Main
!
enable secret 5 $1$mERr$hx5rVt7rPNoS4wqbXKX7m0
!
banner motd ^C
=====================================================
  Cisco 1841 Router - Main Office Gateway
  Authorized Access Only! Network Lab 21 PC02-23
=====================================================
^C
!
interface FastEthernet0/0
 description LAN_Connection_to_Switch-Main
 ip address 192.168.10.1 255.255.255.0
 duplex auto
 speed auto
!
interface Serial0/0/0
 description WAN_Link_to_Branch_Office_Router
 ip address 10.0.0.1 255.255.255.252
 clock rate 64000
!
ip classless
ip route 192.168.20.0 255.255.255.0 10.0.0.2
!
line con 0
 password cisco
 login
line vty 0 4
 password cisco
 login
!
end

Router-Main#"""
        html5 = make_cli_window("Router-Main - Сохранение в NVRAM и проверка конфигурации", terminal_nvram)
        page.set_content(html5)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "screen_nvram_save.png"))
        print("[5/6] Generated screen_nvram_save.png")

        # 6. screen_test_scenario.png
        terminal_test = """=== ТЕСТ 1: ping от PC1 (Главный офис) до PC2 (Дополнительный офис) ===
PC> ping 192.168.20.10
Pinging 192.168.20.10 with 32 bytes of data:
Reply from 192.168.20.10: bytes=32 time=12ms TTL=126
Reply from 192.168.20.10: bytes=32 time=9ms TTL=126
Reply from 192.168.20.10: bytes=32 time=10ms TTL=126
Reply from 192.168.20.10: bytes=32 time=9ms TTL=126

Ping statistics for 192.168.20.10:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 9ms, Maximum = 12ms, Average = 10ms

=== ТЕСТ 2: ping от PC0 (Главный офис) до Server0 (Главный корпус) ===
PC> ping 192.168.10.2
Pinging 192.168.10.2 with 32 bytes of data:
Reply from 192.168.10.2: bytes=32 time<1ms TTL=128
Reply from 192.168.10.2: bytes=32 time<1ms TTL=128
Reply from 192.168.10.2: bytes=32 time<1ms TTL=128
Reply from 192.168.10.2: bytes=32 time<1ms TTL=128

Ping statistics for 192.168.10.2:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)

=== ТЕСТ 3: ping от PC2 (Главный офис) до Server2 (Дополнительный офис) ===
PC> ping 192.168.20.3
Pinging 192.168.20.3 with 32 bytes of data:
Reply from 192.168.20.3: bytes=32 time=11ms TTL=126
Reply from 192.168.20.3: bytes=32 time=9ms TTL=126
Reply from 192.168.20.3: bytes=32 time=10ms TTL=126
Reply from 192.168.20.3: bytes=32 time=10ms TTL=126

Ping statistics for 192.168.20.3:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)

=== ТЕСТ 4: HTTP-запрос от LaptopPT к Server2 (http://192.168.20.3) ===
Laptop> Web Browser -> URL: http://192.168.20.3
HTTP/1.1 200 OK
Content-Type: text/html
Connection: close

<html>
  <head><title>Корпоративный сервер Server2</title></head>
  <body>
    <h1>Портал дополнительного офиса</h1>
    <p>Связь через беспроводную сеть WLAN и маршрутизатор установлена успешно!</p>
  </body>
</html>

=== ТЕСТ 5: DNS-запрос от PDA-PT к Server1 (DNS-сервер 192.168.20.2) ===
PDA> nslookup server2.corp.local 192.168.20.2
Server: Server1
Address: 192.168.20.2

Name: server2.corp.local
Address: 192.168.20.3
[УСПЕШНО: DNS-запрос разрешил доменное имя в IP-адрес через сервер Server1]"""
        html6 = make_cli_window("Сценарий проверки работоспособности сети (ping, HTTP, DNS)", terminal_test)
        page.set_content(html6)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "screen_test_scenario.png"))
        print("[6/6] Generated screen_test_scenario.png")

        browser.close()
    print("All screenshots generated successfully!")

if __name__ == "__main__":
    generate_screenshots()
