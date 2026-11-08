# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = r"d:\1с лабы\ЛР18_Файлы"
os.makedirs(OUT_DIR, exist_ok=True)

FONT_REG_13 = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
FONT_BOLD_13 = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 13)
FONT_REG_12 = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 12)
FONT_BOLD_12 = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 12)
FONT_REG_14 = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
FONT_BOLD_14 = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 14)
FONT_BOLD_16 = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 16)
FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 18)
FONT_CODE = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 12)
FONT_CODE_BOLD = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 12)

def draw_window_frame(draw, w, h, title="The Wireshark Network Analyzer"):
    draw.rectangle([0, 0, w, h], fill="#f0f0f0")
    # Title bar
    draw.rectangle([0, 0, w, 32], fill="#0078d7")
    draw.text((14, 6), title, fill="#ffffff", font=FONT_BOLD_13)
    
    # Window controls: minimize, maximize, close
    # Minimize
    draw.line([(w - 90, 18), (w - 80, 18)], fill="#ffffff", width=2)
    # Maximize
    draw.rectangle([(w - 60, 11), (w - 50, 21)], outline="#ffffff", width=2)
    # Close
    draw.line([(w - 30, 11), (w - 20, 21)], fill="#ffffff", width=2)
    draw.line([(w - 20, 11), (w - 30, 21)], fill="#ffffff", width=2)
    
    # Menu bar
    draw.rectangle([0, 32, w, 56], fill="#ffffff")
    menus = ["File", "Edit", "View", "Go", "Capture", "Analyze", "Statistics", "Telephony", "Wireless", "Tools", "Help"]
    mx = 14
    for m in menus:
        draw.text((mx, 36), m, fill="#1e1e1e", font=FONT_REG_12)
        bbox = draw.textbbox((mx, 36), m, font=FONT_REG_12)
        mx = bbox[2] + 16
    draw.line([0, 56, w, 56], fill="#d0d0d0", width=1)
    
    # Toolbar
    draw.rectangle([0, 57, w, 88], fill="#f8f9fa")
    # 1. Shark fin (Start capture)
    draw.polygon([(16, 63), (16, 81), (28, 72)], fill="#005fb8")
    # 2. Stop capture (Red square)
    draw.rectangle([(38, 65), (50, 77)], fill="#d13438")
    # 3. Restart capture (Green circular arrow)
    draw.ellipse([(60, 64), (74, 78)], outline="#107c41", width=2)
    draw.polygon([(72, 63), (76, 68), (70, 68)], fill="#107c41")
    # 4. Capture options (Gear/dialog)
    draw.rectangle([(84, 65), (98, 77)], outline="#555555", width=1)
    draw.line([(88, 71), (94, 71)], fill="#555555", width=1)
    
    draw.line([(108, 62), (108, 83)], fill="#cccccc", width=1)
    
    # 5. Open file (folder icon)
    draw.polygon([(118, 67), (124, 67), (126, 69), (134, 69), (134, 79), (118, 79)], fill="#e8a838", outline="#c08020")
    # 6. Save file (diskette icon)
    draw.rectangle([(144, 65), (158, 79)], fill="#0078d7")
    draw.rectangle([(147, 65), (155, 70)], fill="#ffffff")
    draw.rectangle([(147, 74), (155, 79)], fill="#ffffff")
    # 7. Close file
    draw.line([(168, 67), (176, 75)], fill="#666666", width=2)
    draw.line([(176, 67), (168, 75)], fill="#666666", width=2)
    # 8. Reload file
    draw.ellipse([(186, 65), (198, 77)], outline="#0078d7", width=2)
    draw.polygon([(196, 64), (200, 69), (194, 69)], fill="#0078d7")
    
    draw.line([(208, 62), (208, 83)], fill="#cccccc", width=1)
    
    # 9. Find packet
    draw.ellipse([(218, 66), (228, 74)], outline="#444444", width=2)
    draw.line([(226, 73), (232, 79)], fill="#444444", width=2)
    # 10. Go back / forward
    draw.polygon([(248, 71), (254, 66), (254, 76)], fill="#0078d7")
    draw.polygon([(268, 71), (262, 66), (262, 76)], fill="#0078d7")
    
    draw.line([(278, 62), (278, 83)], fill="#cccccc", width=1)
    
    # Zoom buttons
    draw.text((290, 65), "Zoom +", fill="#444444", font=FONT_REG_12)
    draw.text((345, 65), "Zoom -", fill="#444444", font=FONT_REG_12)
    draw.text((400, 65), "100%", fill="#444444", font=FONT_REG_12)
    draw.line([(0, 88), (w, 88)], fill="#d0d0d0", width=1)

def draw_filter_bar(draw, w, filter_text="", valid=True):
    draw.rectangle([(0, 89), (w, 118)], fill="#ffffff")
    
    # Bookmark badge
    draw.rectangle([(12, 95), (26, 111)], fill="#e8f0fe", outline="#0078d7")
    draw.polygon([(16, 98), (22, 98), (22, 108), (19, 105), (16, 108)], fill="#0078d7")
    
    # Filter input box
    box_x1, box_x2 = 36, w - 80
    if filter_text:
        bg_col = "#c5ffd0" if valid else "#ffd0d0"
        border_col = "#27ae60" if valid else "#e74c3c"
    else:
        bg_col = "#ffffff"
        border_col = "#7a7a7a"
        
    draw.rectangle([(box_x1, 93), (box_x2, 113)], fill=bg_col, outline=border_col, width=1)
    
    if filter_text:
        draw.text((box_x1 + 10, 96), filter_text, fill="#000000", font=FONT_CODE_BOLD)
    else:
        draw.text((box_x1 + 10, 96), "Apply a display filter ... <Ctrl-/>", fill="#888888", font=FONT_REG_12)
        
    # Buttons on right of filter
    # Arrow Apply
    draw.rectangle([(box_x2 + 6, 93), (box_x2 + 30, 113)], fill="#f5f5f5", outline="#cccccc")
    draw.polygon([(box_x2 + 14, 98), (box_x2 + 22, 103), (box_x2 + 14, 108)], fill="#0078d7")
    # Clear X
    draw.rectangle([(box_x2 + 36, 93), (box_x2 + 56, 113)], fill="#f5f5f5", outline="#cccccc")
    draw.line([(box_x2 + 42, 99), (box_x2 + 50, 107)], fill="#666666", width=2)
    draw.line([(box_x2 + 50, 99), (box_x2 + 42, 107)], fill="#666666", width=2)
    draw.line([(0, 118), (w, 118)], fill="#d0d0d0", width=1)

def draw_status_bar(draw, w, h, text="Packets: 64 • Displayed: 64 (100.0%) • Profile: Default"):
    draw.rectangle([(0, h - 24), (w, h)], fill="#f0f0f0")
    draw.line([(0, h - 24), (w, h - 24)], fill="#cccccc", width=1)
    draw.text((14, h - 20), text, fill="#333333", font=FONT_REG_12)

# ==========================================
# 1. screen_1_wireshark_interfaces.png
# ==========================================
def make_screen_1():
    w, h = 1100, 680
    img = Image.new("RGB", (w, h), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, w, h, "Wireshark • Welcome to Wireshark")
    draw_filter_bar(draw, w, "")
    draw.text((40, 138), "Welcome to Wireshark", fill="#005fb8", font=FONT_TITLE)
    draw.text((40, 185), "Capture", fill="#1e1e1e", font=FONT_BOLD_16)
    draw.text((40, 215), "using this filter:", fill="#555555", font=FONT_REG_13)
    draw.rectangle([(140, 212), (600, 234)], fill="#ffffff", outline="#a0a0a0")
    draw.text((148, 215), "Enter a capture filter ...", fill="#999999", font=FONT_REG_12)
    
    iy = 250
    draw.rectangle([(40, iy), (750, iy + 28)], fill="#e8f0fe")
    draw.text((50, iy + 6), "Interface Name", fill="#003366", font=FONT_BOLD_13)
    draw.text((420, iy + 6), "Traffic", fill="#003366", font=FONT_BOLD_13)
    draw.text((550, iy + 6), "IP Address", fill="#003366", font=FONT_BOLD_13)
    
    interfaces = [
        ("Wi-Fi (Intel(R) Wi-Fi 6 AX201 160MHz)", True, "192.168.1.105", "#e1f5fe"),
        ("Ethernet (Realtek PCIe GbE Family Controller)", False, "Unassigned", "#ffffff"),
        ("Adapter for loopback traffic capture", False, "127.0.0.1", "#f9f9f9"),
        ("Local Area Connection* 1", False, "Unassigned", "#ffffff"),
        ("Local Area Connection* 2", False, "Unassigned", "#f9f9f9"),
        ("Bluetooth Network Connection", False, "Unassigned", "#ffffff")
    ]
    row_y = iy + 28
    for name, has_traffic, ip, row_bg in interfaces:
        draw.rectangle([(40, row_y), (750, row_y + 36)], fill=row_bg, outline="#e0e0e0")
        # Draw small clean badge
        badge_text = "[Wi-Fi]" if "Wi-Fi" in name else ("[Loop]" if "loopback" in name else "[Eth]")
        draw.rectangle([(48, row_y + 8), (92, row_y + 26)], fill="#d0e2ff", outline="#005fb8")
        draw.text((52, row_y + 10), badge_text, fill="#003366", font=FONT_CODE_BOLD)
        draw.text((102, row_y + 9), name, fill="#1e1e1e", font=FONT_REG_13)
        if has_traffic:
            spark_x = 420
            points = [(spark_x, row_y + 24), (spark_x + 10, row_y + 20), (spark_x + 20, row_y + 12),
                      (spark_x + 30, row_y + 22), (spark_x + 40, row_y + 8), (spark_x + 50, row_y + 16),
                      (spark_x + 60, row_y + 22), (spark_x + 70, row_y + 14), (spark_x + 80, row_y + 24)]
            draw.line(points, fill="#0078d7", width=2)
        else:
            draw.line([(420, row_y + 24), (500, row_y + 24)], fill="#aaaaaa", width=1)
        draw.text((550, row_y + 9), ip, fill="#333333", font=FONT_CODE)
        row_y += 36
        
    draw.rectangle([(780, 185), (1060, 480)], fill="#fbfbfb", outline="#e0e0e0")
    draw.text((800, 200), "Ready to Capture", fill="#005fb8", font=FONT_BOLD_14)
    info_lines = [
        "Double-click on an interface",
        "to start capturing live packets.",
        "",
        "Selected Interface:",
        "- Wi-Fi (Active 802.11ax)",
        "- IP: 192.168.1.105 / 24",
        "- Promiscuous mode: Enabled",
        "",
        "Supported PDU Layers:",
        "- Frame / Ethernet II",
        "- IPv4 / IPv6",
        "- TCP / UDP",
        "- HTTP, DNS, TLS"
    ]
    ny = 230
    for line in info_lines:
        font = FONT_BOLD_12 if line.startswith("-") or line.startswith("Selected") or line.startswith("Supported") else FONT_REG_12
        draw.text((800, ny), line, fill="#333333", font=font)
        ny += 18
        
    draw_status_bar(draw, w, h, "Ready to capture on Wi-Fi • Profile: Default")
    img.save(os.path.join(OUT_DIR, "screen_1_wireshark_interfaces.png"), quality=95)
    print("Saved screen_1_wireshark_interfaces.png")

# ==========================================
# 2. screen_2_wireshark_capture_pdu.png
# ==========================================
def make_screen_2():
    w, h = 1100, 680
    img = Image.new("RGB", (w, h), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, w, h, "Wireshark • Capturing from Wi-Fi [PKT 6 selected]")
    draw_filter_bar(draw, w, "")
    
    py = 120
    draw.rectangle([(0, py), (w, py + 22)], fill="#f0f0f0")
    draw.line([(0, py + 22), (w, py + 22)], fill="#c0c0c0")
    cols = [(10, "No."), (55, "Time"), (140, "Source"), (270, "Destination"), (400, "Protocol"), (470, "Length"), (530, "Info")]
    for cx, ch in cols:
        draw.text((cx, py + 3), ch, fill="#333333", font=FONT_BOLD_12)
        
    packets = [
        ("1", "0.000000", "192.168.1.105", "192.168.1.1", "DNS", "78", "Standard query 0x1a2b A example.com", "#daeeff", False),
        ("2", "0.014210", "192.168.1.1", "192.168.1.105", "DNS", "94", "Standard query response 0x1a2b A 93.184.216.34", "#daeeff", False),
        ("3", "0.021054", "192.168.1.105", "93.184.216.34", "TCP", "66", "54128 -> 80 [SYN] Seq=0 Win=64240 Len=0 MSS=1460", "#e6e6ff", False),
        ("4", "0.052140", "93.184.216.34", "192.168.1.105", "TCP", "66", "80 -> 54128 [SYN, ACK] Seq=0 Ack=1 Win=65535 Len=0", "#e6e6ff", False),
        ("5", "0.052210", "192.168.1.105", "93.184.216.34", "TCP", "54", "54128 -> 80 [ACK] Seq=1 Ack=1 Win=64240 Len=0", "#e6e6ff", False),
        ("6", "0.053890", "192.168.1.105", "93.184.216.34", "HTTP", "434", "GET /index.html HTTP/1.1", "#0b3c5d", True),
        ("7", "0.098420", "93.184.216.34", "192.168.1.105", "TCP", "60", "80 -> 54128 [ACK] Seq=1 Ack=381 Win=65155 Len=0", "#e6e6ff", False),
        ("8", "0.104230", "93.184.216.34", "192.168.1.105", "HTTP", "1024", "HTTP/1.1 200 OK  (text/html)", "#c1ffc1", False),
        ("9", "0.104310", "192.168.1.105", "93.184.216.34", "TCP", "54", "54128 -> 80 [ACK] Seq=381 Ack=971 Win=63270 Len=0", "#e6e6ff", False)
    ]
    ry = py + 23
    for no, tm, src, dst, proto, ln, info, bg, is_sel in packets:
        fg = "#ffffff" if is_sel else "#000000"
        draw.rectangle([(0, ry), (w, ry + 18)], fill=bg)
        draw.text((10, ry + 2), no, fill=fg, font=FONT_REG_12)
        draw.text((55, ry + 2), tm, fill=fg, font=FONT_REG_12)
        draw.text((140, ry + 2), src, fill=fg, font=FONT_REG_12)
        draw.text((270, ry + 2), dst, fill=fg, font=FONT_REG_12)
        draw.text((400, ry + 2), proto, fill=fg, font=FONT_BOLD_12 if is_sel else FONT_REG_12)
        draw.text((470, ry + 2), ln, fill=fg, font=FONT_REG_12)
        draw.text((530, ry + 2), info, fill=fg, font=FONT_REG_12)
        ry += 19
    draw.line([(0, ry + 2), (w, ry + 2)], fill="#005fb8", width=2)
    
    dy = ry + 6
    draw.rectangle([(0, dy), (w, dy + 215)], fill="#ffffff")
    tree_items = [
        ("> Frame 6: 434 bytes on wire (3472 bits), 434 bytes captured (3472 bits) on interface Wi-Fi", "#333333", False),
        ("> Ethernet II, Src: Intel_5a:27:14 (00:01:6c:be:5a:27), Dst: Router_3b:12:4a (00:1a:2b:3b:12:4a), Type: IPv4 (0x0800)", "#004080", True),
        ("> Internet Protocol Version 4, Src: 192.168.1.105, Dst: 93.184.216.34, Protocol: TCP (6)", "#004080", True),
        ("> Transmission Control Protocol, Src Port: 54128, Dst Port: 80, Seq: 1, Ack: 1, Len: 380", "#004080", True),
        ("v Hypertext Transfer Protocol", "#003366", True),
        ("    GET /index.html HTTP/1.1", "#222222", False),
        ("    Host: example.com", "#222222", False),
        ("    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "#222222", False),
        ("    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "#222222", False),
        ("    Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7", "#222222", False),
        ("    Connection: keep-alive", "#222222", False),
        ("    [Full request URI: http://example.com/index.html]", "#666666", False)
    ]
    ty = dy + 4
    for line, color, is_bold in tree_items:
        draw.text((16, ty), line, fill=color, font=FONT_BOLD_12 if is_bold else FONT_REG_12)
        ty += 16
    draw.line([(0, ty + 4), (w, ty + 4)], fill="#cccccc", width=1)
    
    by = ty + 8
    draw.rectangle([(0, by), (w, h - 24)], fill="#fdfdfd")
    hex_lines = [
        ("0000", "00 1a 2b 3b 12 4a 00 01  6c be 5a 27 08 00 45 00", "..+;.J..l.Z'..E."),
        ("0010", "01 a4 e4 2b 40 00 80 06  b2 8f c0 a8 01 69 5d b8", "...+@........i]."),
        ("0020", "d8 22 d3 70 00 50 12 34  56 78 9a bc de f0 50 18", ".\".p.P.4Vx....P."),
        ("0030", "fa f0 4f 12 00 00 47 45  54 20 2f 69 6e 64 65 78", "..O...GET /index"),
        ("0040", "2e 68 74 6d 6c 20 48 54  54 50 2f 31 2e 31 0d 0a", ".html HTTP/1.1.."),
        ("0050", "48 6f 73 74 3a 20 65 78  61 6d 70 6c 65 2e 63 6f", "Host: example.co"),
        ("0060", "6d 0d 0a 55 73 65 72 2d  41 67 65 6e 74 3a 20 4d", "m..User-Agent: M")
    ]
    hy = by + 4
    for offset, hex_bytes, ascii_chars in hex_lines:
        draw.text((16, hy), offset, fill="#555555", font=FONT_CODE_BOLD)
        draw.text((70, hy), hex_bytes, fill="#111111", font=FONT_CODE)
        draw.text((460, hy), ascii_chars, fill="#005fb8", font=FONT_CODE)
        hy += 16
        
    draw_status_bar(draw, w, h, "Packets: 9 • Displayed: 9 (100.0%) • Selected: Frame 6 (434 bytes)")
    img.save(os.path.join(OUT_DIR, "screen_2_wireshark_capture_pdu.png"), quality=95)
    print("Saved screen_2_wireshark_capture_pdu.png")

# ==========================================
# 3. screen_3_wireshark_tcp_filter.png
# ==========================================
def make_screen_3():
    w, h = 1100, 680
    img = Image.new("RGB", (w, h), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, w, h, "Wireshark • Display Filter: tcp")
    draw_filter_bar(draw, w, "tcp", valid=True)
    
    py = 120
    draw.rectangle([(0, py), (w, py + 22)], fill="#f0f0f0")
    draw.line([(0, py + 22), (w, py + 22)], fill="#c0c0c0")
    cols = [(10, "No."), (55, "Time"), (140, "Source"), (270, "Destination"), (400, "Protocol"), (470, "Length"), (530, "Info")]
    for cx, ch in cols:
        draw.text((cx, py + 3), ch, fill="#333333", font=FONT_BOLD_12)
        
    packets = [
        ("3", "0.021054", "192.168.1.105", "93.184.216.34", "TCP", "66", "54128 -> 80 [SYN] Seq=0 Win=64240 Len=0 MSS=1460", "#e6e6ff", False),
        ("4", "0.052140", "93.184.216.34", "192.168.1.105", "TCP", "66", "80 -> 54128 [SYN, ACK] Seq=0 Ack=1 Win=65535 Len=0", "#e6e6ff", False),
        ("5", "0.052210", "192.168.1.105", "93.184.216.34", "TCP", "54", "54128 -> 80 [ACK] Seq=1 Ack=1 Win=64240 Len=0", "#e6e6ff", False),
        ("6", "0.053890", "192.168.1.105", "93.184.216.34", "TCP", "434", "54128 -> 80 [PSH, ACK] Seq=1 Ack=1 Win=64240 Len=380", "#0b3c5d", True),
        ("7", "0.098420", "93.184.216.34", "192.168.1.105", "TCP", "60", "80 -> 54128 [ACK] Seq=1 Ack=381 Win=65155 Len=0", "#e6e6ff", False),
        ("8", "0.104230", "93.184.216.34", "192.168.1.105", "TCP", "1024", "80 -> 54128 [PSH, ACK] Seq=1 Ack=381 Win=65155 Len=970", "#e6e6ff", False),
        ("9", "0.104310", "192.168.1.105", "93.184.216.34", "TCP", "54", "54128 -> 80 [ACK] Seq=381 Ack=971 Win=63270 Len=0", "#e6e6ff", False)
    ]
    ry = py + 23
    for no, tm, src, dst, proto, ln, info, bg, is_sel in packets:
        fg = "#ffffff" if is_sel else "#000000"
        draw.rectangle([(0, ry), (w, ry + 18)], fill=bg)
        draw.text((10, ry + 2), no, fill=fg, font=FONT_REG_12)
        draw.text((55, ry + 2), tm, fill=fg, font=FONT_REG_12)
        draw.text((140, ry + 2), src, fill=fg, font=FONT_REG_12)
        draw.text((270, ry + 2), dst, fill=fg, font=FONT_REG_12)
        draw.text((400, ry + 2), proto, fill=fg, font=FONT_BOLD_12 if is_sel else FONT_REG_12)
        draw.text((470, ry + 2), ln, fill=fg, font=FONT_REG_12)
        draw.text((530, ry + 2), info, fill=fg, font=FONT_REG_12)
        ry += 19
    draw.line([(0, ry + 2), (w, ry + 2)], fill="#005fb8", width=2)
    
    dy = ry + 6
    draw.rectangle([(0, dy), (w, dy + 230)], fill="#ffffff")
    tcp_tree = [
        ("> Frame 6: 434 bytes on wire (3472 bits), 434 bytes captured on interface Wi-Fi", "#333333", False),
        ("> Ethernet II, Src: Intel_5a:27:14 (00:01:6c:be:5a:27), Dst: Router_3b:12:4a (00:1a:2b:3b:12:4a)", "#333333", False),
        ("> Internet Protocol Version 4, Src: 192.168.1.105, Dst: 93.184.216.34", "#333333", False),
        ("v Transmission Control Protocol, Src Port: 54128, Dst Port: 80, Seq: 1, Ack: 1, Len: 380", "#003366", True),
        ("    Source Port: 54128 (54128)", "#004080", False),
        ("    Destination Port: 80 (80)", "#004080", False),
        ("    [TCP Segment Len: 380]", "#555555", False),
        ("    Sequence Number: 1    (relative sequence number)", "#004080", False),
        ("    [Next Sequence Number: 381    (relative sequence number)]", "#555555", False),
        ("    Acknowledgment Number: 1    (relative ack number)", "#004080", False),
        ("    0101 .... = Header Length: 20 bytes (5)", "#222222", False),
        ("    Flags: 0x018 (PSH, ACK)", "#004080", True),
        ("        000. .... .... = Reserved: Set to 0", "#555555", False),
        ("        ...0 0001 1000 = Acknowledgment: Set, Push: Set", "#222222", False),
        ("    Window: 64240", "#004080", False),
        ("    [Calculated window size: 64240]", "#555555", False),
        ("    Checksum: 0x4f12 [unverified, validation disabled]", "#004080", False),
        ("    Urgent Pointer: 0", "#222222", False)
    ]
    ty = dy + 4
    for line, color, is_bold in tcp_tree:
        draw.text((16, ty), line, fill=color, font=FONT_BOLD_12 if is_bold else FONT_REG_12)
        ty += 15
    draw.line([(0, ty + 4), (w, ty + 4)], fill="#cccccc", width=1)
    
    by = ty + 8
    draw.rectangle([(0, by), (w, h - 24)], fill="#fdfdfd")
    hex_lines = [
        ("0020", "d8 22 d3 70 00 50 12 34  56 78 9a bc de f0 50 18", ".\".p.P.4Vx....P."),
        ("0030", "fa f0 4f 12 00 00 47 45  54 20 2f 69 6e 64 65 78", "..O...GET /index"),
        ("0040", "2e 68 74 6d 6c 20 48 54  54 50 2f 31 2e 31 0d 0a", ".html HTTP/1.1..")
    ]
    hy = by + 4
    for offset, hex_bytes, ascii_chars in hex_lines:
        draw.text((16, hy), offset, fill="#555555", font=FONT_CODE_BOLD)
        draw.text((70, hy), hex_bytes, fill="#111111", font=FONT_CODE)
        draw.text((460, hy), ascii_chars, fill="#005fb8", font=FONT_CODE)
        hy += 16
        
    draw_status_bar(draw, w, h, "Packets: 24 • Displayed: 7 (29.2%) • Filter: tcp")
    img.save(os.path.join(OUT_DIR, "screen_3_wireshark_tcp_filter.png"), quality=95)
    print("Saved screen_3_wireshark_tcp_filter.png")

# ==========================================
# 4. screen_4_wireshark_udp_filter.png
# ==========================================
def make_screen_4():
    w, h = 1100, 680
    img = Image.new("RGB", (w, h), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, w, h, "Wireshark • Display Filter: udp")
    draw_filter_bar(draw, w, "udp", valid=True)
    
    py = 120
    draw.rectangle([(0, py), (w, py + 22)], fill="#f0f0f0")
    draw.line([(0, py + 22), (w, py + 22)], fill="#c0c0c0")
    cols = [(10, "No."), (55, "Time"), (140, "Source"), (270, "Destination"), (400, "Protocol"), (470, "Length"), (530, "Info")]
    for cx, ch in cols:
        draw.text((cx, py + 3), ch, fill="#333333", font=FONT_BOLD_12)
        
    packets = [
        ("1", "0.000000", "192.168.1.105", "192.168.1.1", "DNS", "78", "Standard query 0x1a2b A click.yandex.ru", "#0b3c5d", True),
        ("2", "0.014210", "192.168.1.1", "192.168.1.105", "DNS", "94", "Standard query response 0x1a2b A click.yandex.ru A 95.25.203.168", "#daeeff", False),
        ("11", "1.251020", "192.168.1.105", "192.168.1.1", "DNS", "73", "Standard query 0x3f41 A ya.ru", "#daeeff", False),
        ("12", "1.265430", "192.168.1.1", "192.168.1.105", "DNS", "89", "Standard query response 0x3f41 A ya.ru A 87.250.250.242", "#daeeff", False),
        ("15", "2.105400", "192.168.1.105", "239.255.255.250", "SSDP", "175", "M-SEARCH * HTTP/1.1 (UDP 1900)", "#ffe0b2", False)
    ]
    ry = py + 23
    for no, tm, src, dst, proto, ln, info, bg, is_sel in packets:
        fg = "#ffffff" if is_sel else "#000000"
        draw.rectangle([(0, ry), (w, ry + 18)], fill=bg)
        draw.text((10, ry + 2), no, fill=fg, font=FONT_REG_12)
        draw.text((55, ry + 2), tm, fill=fg, font=FONT_REG_12)
        draw.text((140, ry + 2), src, fill=fg, font=FONT_REG_12)
        draw.text((270, ry + 2), dst, fill=fg, font=FONT_REG_12)
        draw.text((400, ry + 2), proto, fill=fg, font=FONT_BOLD_12 if is_sel else FONT_REG_12)
        draw.text((470, ry + 2), ln, fill=fg, font=FONT_REG_12)
        draw.text((530, ry + 2), info, fill=fg, font=FONT_REG_12)
        ry += 19
    draw.line([(0, ry + 2), (w, ry + 2)], fill="#005fb8", width=2)
    
    dy = ry + 6
    draw.rectangle([(0, dy), (w, dy + 230)], fill="#ffffff")
    udp_tree = [
        ("> Frame 1: 78 bytes on wire (624 bits), 78 bytes captured on interface Wi-Fi", "#333333", False),
        ("> Ethernet II, Src: Intel_5a:27:14 (00:01:6c:be:5a:27), Dst: Router_3b:12:4a (00:1a:2b:3b:12:4a)", "#333333", False),
        ("> Internet Protocol Version 4, Src: 192.168.1.105, Dst: 192.168.1.1, Protocol: UDP (17)", "#333333", False),
        ("v User Datagram Protocol, Src Port: 58214, Dst Port: 53", "#003366", True),
        ("    Source Port: 58214 (58214)", "#004080", False),
        ("    Destination Port: 53 (53) [Domain Name Server]", "#004080", False),
        ("    Length: 44", "#004080", True),
        ("    Checksum: 0x2b84 [unverified]", "#004080", False),
        ("    [UDP payload (36 bytes)]", "#555555", False),
        ("v Domain Name System (query)", "#003366", True),
        ("    Transaction ID: 0x1a2b", "#222222", False),
        ("    Flags: 0x0100 Standard query", "#222222", False),
        ("    Questions: 1", "#222222", False),
        ("    Answer RRs: 0", "#222222", False),
        ("    Authority RRs: 0", "#222222", False),
        ("    Additional RRs: 0", "#222222", False),
        ("    v Queries", "#003366", False),
        ("        v click.yandex.ru: type A, class IN", "#222222", False),
        ("            Name: click.yandex.ru", "#222222", False),
        ("            Type: A (Host Address) (1)", "#222222", False),
        ("            Class: IN (0x0001)", "#222222", False)
    ]
    ty = dy + 4
    for line, color, is_bold in udp_tree:
        draw.text((16, ty), line, fill=color, font=FONT_BOLD_12 if is_bold else FONT_REG_12)
        ty += 15
    draw.line([(0, ty + 4), (w, ty + 4)], fill="#cccccc", width=1)
    
    by = ty + 8
    draw.rectangle([(0, by), (w, h - 24)], fill="#fdfdfd")
    hex_lines = [
        ("0020", "01 e3 56 00 35 00 2c 2b  84 1a 2b 01 00 00 01 00", "..V.5.,+..+....."),
        ("0030", "00 00 00 00 00 05 63 6c  69 63 6b 06 79 61 6e 64", "......click.yand"),
        ("0040", "65 78 02 72 75 00 00 01  00 01", "ex.ru....")
    ]
    hy = by + 4
    for offset, hex_bytes, ascii_chars in hex_lines:
        draw.text((16, hy), offset, fill="#555555", font=FONT_CODE_BOLD)
        draw.text((70, hy), hex_bytes, fill="#111111", font=FONT_CODE)
        draw.text((460, hy), ascii_chars, fill="#005fb8", font=FONT_CODE)
        hy += 16
        
    draw_status_bar(draw, w, h, "Packets: 24 • Displayed: 5 (20.8%) • Filter: udp")
    img.save(os.path.join(OUT_DIR, "screen_4_wireshark_udp_filter.png"), quality=95)
    print("Saved screen_4_wireshark_udp_filter.png")

# ==========================================
# 5. screen_5_wireshark_http_filter.png
# ==========================================
def make_screen_5():
    w, h = 1100, 680
    img = Image.new("RGB", (w, h), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, w, h, "Wireshark • Display Filter: http")
    draw_filter_bar(draw, w, "http", valid=True)
    
    py = 120
    draw.rectangle([(0, py), (w, py + 22)], fill="#f0f0f0")
    draw.line([(0, py + 22), (w, py + 22)], fill="#c0c0c0")
    cols = [(10, "No."), (55, "Time"), (140, "Source"), (270, "Destination"), (400, "Protocol"), (470, "Length"), (530, "Info")]
    for cx, ch in cols:
        draw.text((cx, py + 3), ch, fill="#333333", font=FONT_BOLD_12)
        
    packets = [
        ("6", "0.053890", "192.168.1.105", "93.184.216.34", "HTTP", "434", "GET /index.html HTTP/1.1", "#c1ffc1", False),
        ("8", "0.104230", "93.184.216.34", "192.168.1.105", "HTTP", "1024", "HTTP/1.1 200 OK  (text/html)", "#0b3c5d", True),
        ("14", "1.420110", "192.168.1.105", "93.184.216.34", "HTTP", "390", "GET /favicon.ico HTTP/1.1", "#c1ffc1", False),
        ("16", "1.482930", "93.184.216.34", "192.168.1.105", "HTTP", "240", "HTTP/1.1 404 Not Found  (text/html)", "#c1ffc1", False)
    ]
    ry = py + 23
    for no, tm, src, dst, proto, ln, info, bg, is_sel in packets:
        fg = "#ffffff" if is_sel else "#000000"
        draw.rectangle([(0, ry), (w, ry + 18)], fill=bg)
        draw.text((10, ry + 2), no, fill=fg, font=FONT_REG_12)
        draw.text((55, ry + 2), tm, fill=fg, font=FONT_REG_12)
        draw.text((140, ry + 2), src, fill=fg, font=FONT_REG_12)
        draw.text((270, ry + 2), dst, fill=fg, font=FONT_REG_12)
        draw.text((400, ry + 2), proto, fill=fg, font=FONT_BOLD_12 if is_sel else FONT_REG_12)
        draw.text((470, ry + 2), ln, fill=fg, font=FONT_REG_12)
        draw.text((530, ry + 2), info, fill=fg, font=FONT_REG_12)
        ry += 19
    draw.line([(0, ry + 2), (w, ry + 2)], fill="#005fb8", width=2)
    
    dy = ry + 6
    draw.rectangle([(0, dy), (w, dy + 230)], fill="#ffffff")
    tree_items = [
        ("> Frame 8: 1024 bytes on wire (8192 bits), 1024 bytes captured on interface Wi-Fi", "#333333", False),
        ("> Ethernet II, Src: Router_3b:12:4a (00:1a:2b:3b:12:4a), Dst: Intel_5a:27:14 (00:01:6c:be:5a:27)", "#333333", False),
        ("> Internet Protocol Version 4, Src: 93.184.216.34, Dst: 192.168.1.105", "#333333", False),
        ("> Transmission Control Protocol, Src Port: 80, Dst Port: 54128, Seq: 1, Ack: 381", "#333333", False),
        ("v Hypertext Transfer Protocol", "#003366", True),
        ("    HTTP/1.1 200 OK", "#004080", True),
        ("        [Expert Info (Chat/Sequence): HTTP/1.1 200 OK]", "#555555", False),
        ("        Response Version: HTTP/1.1", "#222222", False),
        ("        Status Code: 200", "#004080", True),
        ("        [Status Code Description: OK]", "#555555", False),
        ("        Response Phrase: OK", "#222222", False),
        ("    Age: 512340", "#222222", False),
        ("    Cache-Control: max-age=604800", "#222222", False),
        ("    Content-Type: text/html; charset=UTF-8", "#004080", True),
        ("    Date: Wed, 09 Sep 2026 08:45:00 GMT", "#222222", False),
        ("    Server: ECS (dcb/7ea2)", "#222222", False),
        ("    Content-Length: 648", "#004080", True),
        ("    [HTTP response 1/1]", "#555555", False),
        ("    [Time since request: 0.050340 seconds]", "#555555", False),
        ("v Line-based text data: text/html (648 bytes)", "#003366", False),
        ("    <!doctype html><html><head><title>Example Domain</title>...</head>...</html>", "#222222", False)
    ]
    ty = dy + 4
    for line, color, is_bold in tree_items:
        draw.text((16, ty), line, fill=color, font=FONT_BOLD_12 if is_bold else FONT_REG_12)
        ty += 15
    draw.line([(0, ty + 4), (w, ty + 4)], fill="#cccccc", width=1)
    
    by = ty + 8
    draw.rectangle([(0, by), (w, h - 24)], fill="#fdfdfd")
    hex_lines = [
        ("0000", "48 54 54 50 2f 31 2e 31  20 32 30 30 20 4f 4b 0d", "HTTP/1.1 200 OK."),
        ("0010", "0a 41 67 65 3a 20 35 31  32 33 34 30 0d 0a 43 61", ".Age: 512340..Ca"),
        ("0020", "63 68 65 2d 43 6f 6e 74  72 6f 6c 3a 20 6d 61 78", "che-Control: max"),
        ("0030", "2d 61 67 65 3d 36 30 34  38 30 30 0d 0a 43 6f 6e", "-age=604800..Con")
    ]
    hy = by + 4
    for offset, hex_bytes, ascii_chars in hex_lines:
        draw.text((16, hy), offset, fill="#555555", font=FONT_CODE_BOLD)
        draw.text((70, hy), hex_bytes, fill="#111111", font=FONT_CODE)
        draw.text((460, hy), ascii_chars, fill="#005fb8", font=FONT_CODE)
        hy += 16
        
    draw_status_bar(draw, w, h, "Packets: 24 • Displayed: 4 (16.7%) • Filter: http")
    img.save(os.path.join(OUT_DIR, "screen_5_wireshark_http_filter.png"), quality=95)
    print("Saved screen_5_wireshark_http_filter.png")

if __name__ == "__main__":
    make_screen_1()
    make_screen_2()
    make_screen_3()
    make_screen_4()
    make_screen_5()
    print("SUCCESS: All 5 Wireshark screenshots updated perfectly!")
