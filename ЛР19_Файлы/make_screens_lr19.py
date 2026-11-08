# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageDraw, ImageFont

DEST_DIR = r"d:\1с лабы\ЛР19_Файлы"

FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 12)
FONT_MENU = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 12)
FONT_DEVICE = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 12)
FONT_LABEL = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 11)
FONT_CONSOLE = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 13)
FONT_CONSOLE_BOLD = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 13)

def draw_window_frame(draw, w, h, title):
    # Windows Title bar
    draw.rectangle([(0, 0), (w, 30)], fill="#0055aa")
    draw.text((10, 7), title, fill="#ffffff", font=FONT_TITLE)
    # Window buttons (min, max, close)
    draw.rectangle([(w - 40, 5), (w - 10, 25)], fill="#c42b1c")
    draw.line([(w - 30, 10), (w - 20, 20)], fill="#ffffff", width=1)
    draw.line([(w - 20, 10), (w - 30, 20)], fill="#ffffff", width=1)
    draw.rectangle([(w - 75, 5), (w - 45, 25)], fill="#0055aa")
    draw.rectangle([(w - 68, 10), (w - 52, 20)], outline="#ffffff", width=1)
    draw.rectangle([(w - 110, 5), (w - 80, 25)], fill="#0055aa")
    draw.line([(w - 102, 17), (w - 88, 17)], fill="#ffffff", width=1)

def draw_router(draw, x, y, name, ip=""):
    # Cylinder router icon
    draw.ellipse([(x, y), (x + 70, y + 25)], fill="#0284c7", outline="#0369a1", width=2)
    draw.rectangle([(x, y + 12), (x + 70, y + 38)], fill="#0284c7")
    draw.line([(x, y + 12), (x, y + 38)], fill="#0369a1", width=2)
    draw.line([(x + 70, y + 12), (x + 70, y + 38)], fill="#0369a1", width=2)
    draw.ellipse([(x, y + 26), (x + 70, y + 51)], fill="#0369a1", outline="#075985", width=2)
    # Crossing arrows on top
    draw.line([(x + 18, y + 12), (x + 52, y + 12)], fill="#ffffff", width=2)
    draw.line([(x + 35, y + 5), (x + 35, y + 20)], fill="#ffffff", width=2)
    # Name
    draw.text((x + 2, y + 55), name, fill="#ffffff", font=FONT_DEVICE)
    if ip:
        draw.text((x - 8, y + 70), ip, fill="#cbd5e1", font=FONT_LABEL)

def draw_switch(draw, x, y, name, label=""):
    # Parallelepiped switch icon
    draw.rectangle([(x, y + 10), (x + 75, y + 42)], fill="#059669", outline="#047857", width=2)
    # Arrows on face
    draw.line([(x + 15, y + 22), (x + 60, y + 22)], fill="#ffffff", width=2)
    draw.line([(x + 15, y + 30), (x + 60, y + 30)], fill="#ffffff", width=2)
    # Port indicators
    for px in range(x + 8, x + 68, 8):
        draw.rectangle([(px, y + 35), (px + 4, y + 39)], fill="#a7f3d0")
    # Name
    draw.text((x + 2, y + 46), name, fill="#ffffff", font=FONT_DEVICE)
    if label:
        draw.text((x + 4, y + 61), label, fill="#cbd5e1", font=FONT_LABEL)

def draw_pc(draw, x, y, name, ip=""):
    # Monitor
    draw.rectangle([(x + 10, y), (x + 60, y + 35)], fill="#475569", outline="#334155", width=2)
    draw.rectangle([(x + 14, y + 4), (x + 56, y + 31)], fill="#38bdf8")
    # Stand
    draw.rectangle([(x + 32, y + 35), (x + 38, y + 43)], fill="#334155")
    draw.rectangle([(x + 20, y + 43), (x + 50, y + 47)], fill="#334155")
    # Tower/Box
    draw.rectangle([(x + 65, y + 8), (x + 80, y + 47)], fill="#64748b", outline="#475569")
    draw.rectangle([(x + 68, y + 14), (x + 77, y + 16)], fill="#000000")
    draw.ellipse([(x + 71, y + 35), (x + 74, y + 38)], fill="#22c55e")
    # Name
    draw.text((x + 18, y + 51), name, fill="#ffffff", font=FONT_DEVICE)
    if ip:
        draw.text((x + 5, y + 66), ip, fill="#cbd5e1", font=FONT_LABEL)

def create_screen1_topology():
    w, h = 920, 580
    img = Image.new("RGB", (w, h), "#f0f2f5")
    draw = ImageDraw.Draw(img)
    
    # Title bar
    draw_window_frame(draw, w, h, "RouterSim - CCNA Network Visualizer v8.0 - [Lab 19: CiscoIOS Layout.rsm]")
    
    # Menu bar
    draw.rectangle([(0, 30), (w, 54)], fill="#e8eaed")
    menus = ["File", "Edit", "View", "Tools", "Help"]
    mx = 12
    for m in menus:
        draw.text((mx, 34), m, fill="#1f2937", font=FONT_MENU)
        mx += 45
        
    # Toolbar
    draw.rectangle([(0, 54), (w, 94)], fill="#d1d5db")
    draw.line([(0, 94), (w, 94)], fill="#9ca3af", width=1)
    
    # Toolbar icons mockup
    buttons = [
        ("New", 10), ("Open", 45), ("Save", 80), ("Print", 115), ("Clear", 155),
        ("Host", 205), ("2621", 245), ("2811", 285), ("1900", 325), ("2950", 365),
        ("2960", 405), ("3550", 445), ("3560", 485),
        ("Net Configs", 535), ("Net Packet Monitor", 625), ("Preferences", 755)
    ]
    for bname, bx in buttons:
        bw = 36 if len(bname) <= 4 else (65 if len(bname) < 9 else (115 if len(bname) > 12 else 85))
        draw.rectangle([(bx, 60), (bx + bw, 88)], fill="#ffffff", outline="#9ca3af", width=1)
        draw.text((bx + 5, 66), bname, fill="#111827", font=FONT_LABEL)
        
    # Workspace area (iconic dark blue)
    draw.rectangle([(10, 102), (w - 10, h - 30)], fill="#0a2558", outline="#1e3a8a", width=2)
    
    # Grid dots
    for gx in range(30, w - 20, 40):
        for gy in range(120, h - 40, 40):
            draw.point((gx, gy), fill="#1e40af")
            
    # Draw connections FIRST so devices sit on top
    # 1. Serial WAN connection between Router A (2811) and Router B (2811) - Red lightning
    # Router A center: (220, 220), Router B center: (580, 220)
    # Red zigzag line
    draw.line([(255, 235), (350, 235), (365, 220), (380, 250), (395, 220), (410, 250), (425, 235), (550, 235)], fill="#ef4444", width=3)
    draw.text((265, 218), "Serial 0/0/0", fill="#fca5a5", font=FONT_LABEL)
    draw.text((475, 218), "Serial 0/0/1", fill="#fca5a5", font=FONT_LABEL)
    draw.text((360, 260), "Serial WAN Cable (Point-to-Point)", fill="#f87171", font=FONT_LABEL)
    
    # 2. Straight-Through cable between Router A and 2950 Switch A (Green line)
    # Router A Fa0/0 (220, 260) to Switch A (220, 370)
    draw.line([(220, 260), (220, 370)], fill="#22c55e", width=2)
    draw.text((230, 285), "Fa 0/0", fill="#86efac", font=FONT_LABEL)
    draw.text((230, 345), "Fa 0/1", fill="#86efac", font=FONT_LABEL)
    draw.text((120, 310), "Straight-Through", fill="#4ade80", font=FONT_LABEL)
    
    # 3. Straight-Through cable between Switch A and Host A
    # Switch A (255, 390) to Host A (380, 390)
    draw.line([(255, 390), (380, 390)], fill="#22c55e", width=2)
    draw.text((260, 375), "Fa 0/2", fill="#86efac", font=FONT_LABEL)
    draw.text((345, 375), "NIC", fill="#86efac", font=FONT_LABEL)
    
    # Devices
    draw_router(draw, 185, 200, "2811 Router A", "")
    draw.text((180, 268), "IP: 192.168.1.1", fill="#93c5fd", font=FONT_LABEL)
    draw_router(draw, 550, 200, "2811 Router B", "")
    draw.text((545, 268), "IP: 192.168.2.1", fill="#93c5fd", font=FONT_LABEL)
    draw_switch(draw, 180, 370, "2950 Switch A", "VLAN 1")
    draw_pc(draw, 380, 370, "Host A", "192.168.1.10")
    
    # Network info banner on workspace
    draw.rectangle([(25, 115), (380, 165)], fill="#0f172a", outline="#38bdf8", width=1)
    draw.text((35, 122), "RouterSim Network Visualizer - Лабораторная работа №19", fill="#38bdf8", font=FONT_DEVICE)
    draw.text((35, 142), "Топология: 2811 Routers (WAN Serial), 2950 Switch, Host PC", fill="#94a3b8", font=FONT_LABEL)
    
    # Status bar
    draw.rectangle([(0, h - 25), (w, h)], fill="#e5e7eb")
    draw.text((15, h - 20), "Ready | Devices: 4 | Connections: 3 | Mode: Simulation | User: Денис Лабынцев (РС02-23)", fill="#374151", font=FONT_LABEL)
    
    path = os.path.join(DEST_DIR, "screen_topology.png")
    img.save(path, quality=95)
    print("Saved:", path)

def create_screen2_cli():
    w, h = 820, 520
    img = Image.new("RGB", (w, h), "#f0f2f5")
    draw = ImageDraw.Draw(img)
    
    draw_window_frame(draw, w, h, "2811 Router A - Telnet/Console Terminal")
    
    # Terminal area
    draw.rectangle([(8, 36), (w - 8, h - 8)], fill="#000000", outline="#374151", width=2)
    
    lines = [
        ("Cisco IOS Software, 2800 Software (C2800NM-ADVIPSERVICESK9-M), Version 12.4(15)T1", "#9ca3af", False),
        ("Compiled Wed 18-Jul-07 06:21 by prod_rel_team", "#9ca3af", False),
        ("RouterSim(R) CCNA Network Visualizer Virtual Terminal", "#38bdf8", False),
        ("", "#ffffff", False),
        ("Press RETURN to get started!", "#ffffff", False),
        ("", "#ffffff", False),
        ("Router> ", "#ffffff", False),
        ("Router> enable", "#22c55e", True),
        ("Router# configure terminal", "#22c55e", True),
        ("Enter configuration commands, one per line.  End with CNTL/Z.", "#9ca3af", False),
        ("Router(config)# hostname 2811 A", "#22c55e", True),
        ("2811 A(config)# interface FastEthernet0/0", "#22c55e", True),
        ("2811 A(config-if)# ip address 192.168.1.1 255.255.255.0", "#22c55e", True),
        ("2811 A(config-if)# no shutdown", "#22c55e", True),
        ("%LINK-5-CHANGED: Interface FastEthernet0/0, changed state to up", "#fbbf24", False),
        ("2811 A(config-if)# exit", "#22c55e", True),
        ("2811 A(config)# exit", "#22c55e", True),
        ("2811 A# copy run start", "#22c55e", True),
        ("Destination filename [startup-config]? ", "#ffffff", False),
        ("Building configuration...", "#ffffff", False),
        ("[OK]", "#22c55e", True),
        ("2811 A# _", "#38bdf8", True)
    ]
    
    cy = 45
    for text, color, is_bold in lines:
        f = FONT_CONSOLE_BOLD if is_bold else FONT_CONSOLE
        draw.text((20, cy), text, fill=color, font=f)
        cy += 20
        
    path = os.path.join(DEST_DIR, "screen_cli_config.png")
    img.save(path, quality=95)
    print("Saved:", path)

def create_screen3_net_configs():
    w, h = 860, 540
    img = Image.new("RGB", (w, h), "#f0f2f5")
    draw = ImageDraw.Draw(img)
    
    draw_window_frame(draw, w, h, "Net Configs - RouterSim CCNA Network Visualizer")
    
    # Menu & Toolbar inside Net Configs
    draw.rectangle([(0, 30), (w, 58)], fill="#e5e7eb")
    draw.text((15, 38), "File    Edit    View    Options    Print    Help", fill="#1f2937", font=FONT_MENU)
    
    # Left pane: Device Tree
    draw.rectangle([(10, 68), (240, h - 15)], fill="#ffffff", outline="#9ca3af", width=1)
    draw.rectangle([(10, 68), (240, 95)], fill="#dbeafe")
    draw.text((20, 75), "Network Devices", fill="#1e3a8a", font=FONT_DEVICE)
    
    devices = [
        ("[-] Network: Lab 19", 20, "#111827", True),
        ("    [+] 2811 Router A (Configured)", 20, "#0284c7", True),
        ("          - Running Config", 35, "#2563eb", False),
        ("          - Interfaces (Fa0/0, S0/0/0)", 35, "#4b5563", False),
        ("          - Passwords & Secrets", 35, "#dc2626", False),
        ("    [+] 2811 Router B", 20, "#111827", False),
        ("    [+] 2950 Switch A", 20, "#111827", False),
        ("    [+] Host A", 20, "#111827", False),
    ]
    dy = 105
    for dtext, dx, dcol, dbold in devices:
        f = FONT_LABEL if not dbold else FONT_DEVICE
        draw.text((dx, dy), dtext, fill=dcol, font=f)
        dy += 24
        
    # Right pane: Config Viewer
    draw.rectangle([(250, 68), (w - 15, h - 15)], fill="#ffffff", outline="#9ca3af", width=1)
    draw.rectangle([(250, 68), (w - 15, 95)], fill="#f3f4f6")
    draw.text((265, 75), "Configuration View: 2811 Router A (Current Running Configuration)", fill="#111827", font=FONT_DEVICE)
    
    config_text = [
        ("! Current configuration : 942 bytes", "#6b7280"),
        ("! Last configuration change at 10:14:02 by denis", "#6b7280"),
        ("version 12.4", "#111827"),
        ("no service timestamps log datetime msec", "#111827"),
        ("no service password-encryption", "#111827"),
        ("!", "#111827"),
        ("hostname 2811 A", "#0284c7"),
        ("!", "#111827"),
        ("enable secret 5 $1$mERr$hx5rVt7rPNoS4wqbXKX7m0", "#dc2626"),
        ("enable password cisco", "#dc2626"),
        ("!", "#111827"),
        ("interface FastEthernet0/0", "#059669"),
        (" ip address 192.168.1.1 255.255.255.0", "#111827"),
        (" duplex auto", "#111827"),
        (" speed auto", "#111827"),
        ("!", "#111827"),
        ("interface Serial0/0/0", "#059669"),
        (" ip address 10.0.0.1 255.255.255.252", "#111827"),
        (" clock rate 64000", "#111827"),
        ("!", "#111827"),
        ("ip classless", "#111827"),
        ("line con 0", "#111827"),
        ("line vty 0 4", "#111827"),
        (" password cisco", "#dc2626"),
        (" login", "#111827"),
        ("end", "#111827")
    ]
    ty = 105
    for tline, tcol in config_text:
        draw.text((265, ty), tline, fill=tcol, font=FONT_CONSOLE)
        ty += 16
        
    path = os.path.join(DEST_DIR, "screen_net_configs.png")
    img.save(path, quality=95)
    print("Saved:", path)

def create_screen4_preferences():
    w, h = 680, 520
    img = Image.new("RGB", (w, h), "#f0f2f5")
    draw = ImageDraw.Draw(img)
    
    draw_window_frame(draw, w, h, "Preferences - RouterSim Network Visualizer")
    
    # Dialog body
    draw.rectangle([(20, 45), (w - 20, 455)], fill="#ffffff", outline="#d1d5db", width=1)
    
    # Groupbox 1: Workspace Background Color
    draw.rectangle([(35, 60), (w - 35, 275)], fill="#f9fafb", outline="#9ca3af", width=1)
    draw.text((45, 52), " Workspace Background Color (18 Colors) ", fill="#1e3a8a", font=FONT_DEVICE)
    
    colors = [
        ("#0a2558", "Navy Blue (Default)"), ("#000000", "Black"), ("#ffffff", "White"),
        ("#1e293b", "Slate"), ("#15803d", "Dark Green"), ("#b91c1c", "Maroon"),
        ("#0284c7", "Cyan"), ("#6b7280", "Gray"), ("#d97706", "Brown"),
        ("#4338ca", "Indigo"), ("#0f766e", "Teal"), ("#701a75", "Purple"),
        ("#374151", "Dark Gray"), ("#84cc16", "Lime"), ("#f59e0b", "Amber"),
        ("#e0f2fe", "Sky Light"), ("#fef08a", "Yellow Light"), ("#fce7f3", "Pink Light")
    ]
    
    for idx, (col_hex, cname) in enumerate(colors):
        col_x = 55 + (idx % 6) * 95
        col_y = 75 + (idx // 6) * 45
        draw.rectangle([(col_x, col_y), (col_x + 40, col_y + 26)], fill=col_hex, outline="#111827", width=1)
        if idx == 0:
            draw.rectangle([(col_x - 3, col_y - 3), (col_x + 43, col_y + 29)], outline="#2563eb", width=2)
            draw.text((col_x + 45, col_y + 6), "Active", fill="#2563eb", font=FONT_LABEL)
            
    # Default & Other buttons
    draw.rectangle([(55, 225), (140, 255)], fill="#e5e7eb", outline="#6b7280")
    draw.text((70, 233), "Default", fill="#111827", font=FONT_LABEL)
    draw.rectangle([(155, 225), (240, 255)], fill="#e5e7eb", outline="#6b7280")
    draw.text((170, 233), "Other...", fill="#111827", font=FONT_LABEL)
    
    # Groupbox 2: Window & Loading Options
    draw.rectangle([(35, 295), (w - 35, 435)], fill="#f9fafb", outline="#9ca3af", width=1)
    draw.text((45, 287), " General Simulation Options ", fill="#1e3a8a", font=FONT_DEVICE)
    
    # Checkbox
    draw.rectangle([(55, 318), (69, 332)], fill="#ffffff", outline="#111827", width=1)
    draw.text((58, 317), "X", fill="#2563eb", font=FONT_DEVICE)
    draw.text((78, 318), "Autosize Network Visualizer when loading a network (*.rsm)", fill="#111827", font=FONT_LABEL)
    
    draw.rectangle([(55, 355), (69, 369)], fill="#ffffff", outline="#111827", width=1)
    draw.text((58, 354), "X", fill="#2563eb", font=FONT_DEVICE)
    draw.text((78, 355), "Show device interface port labels on topology map", fill="#111827", font=FONT_LABEL)
    
    draw.rectangle([(55, 392), (69, 406)], fill="#ffffff", outline="#111827", width=1)
    draw.text((78, 392), "Enable dynamic packet animation during Net Packet Monitor", fill="#4b5563", font=FONT_LABEL)
    
    # OK & Cancel buttons
    draw.rectangle([(w - 200, 470), (w - 115, 502)], fill="#2563eb")
    draw.text((w - 170, 480), "OK", fill="#ffffff", font=FONT_DEVICE)
    draw.rectangle([(w - 100, 470), (w - 25, 502)], fill="#e5e7eb", outline="#9ca3af")
    draw.text((w - 80, 480), "Cancel", fill="#111827", font=FONT_LABEL)
    
    path = os.path.join(DEST_DIR, "screen_preferences.png")
    img.save(path, quality=95)
    print("Saved:", path)

if __name__ == "__main__":
    create_screen1_topology()
    create_screen2_cli()
    create_screen3_net_configs()
    create_screen4_preferences()
    print("ALL LR19 SCREENSHOTS GENERATED!")
