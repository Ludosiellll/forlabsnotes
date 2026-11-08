# -*- coding: utf-8 -*-
import os
import math
import struct
import wave
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

DEST_DIR = r"d:\1с лабы\ПСИП_ЛР2_Файлы"

def create_bg_pattern():
    img = Image.new("RGB", (60, 60), "#f0f4f8")
    draw = ImageDraw.Draw(img)
    draw.line([(0, 0), (60, 60)], fill="#e2e8f0", width=1)
    draw.line([(60, 0), (0, 60)], fill="#e2e8f0", width=1)
    draw.rectangle([(28, 28), (32, 32)], fill="#cbd5e1")
    path = os.path.join(DEST_DIR, "bg_pattern.png")
    img.save(path)
    print("Created:", path)

def create_emblem():
    img = Image.new("RGB", (180, 220), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([(10, 10), (170, 210)], radius=20, outline="#1a365d", width=4, fill="#f8fafc")
    draw.rectangle([(85, 30), (95, 180)], fill="#78350f")
    draw.rectangle([(55, 60), (125, 70)], fill="#78350f")
    draw.line([(35, 175), (145, 125)], fill="#92400e", width=12)
    draw.line([(35, 125), (145, 175)], fill="#b45309", width=12)
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 14)
    draw.text((45, 188), "БОБРУЙСК", fill="#1e293b", font=font)
    path = os.path.join(DEST_DIR, "emblem.png")
    img.save(path)
    print("Created:", path)

def create_bobr_statue():
    img = Image.new("RGB", (360, 270), "#1e293b")
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (360, 160)], fill="#93c5fd")
    draw.rectangle([(0, 160), (360, 270)], fill="#94a3b8")
    draw.rectangle([(130, 170), (230, 260)], fill="#475569")
    draw.ellipse([(150, 70), (210, 140)], fill="#b45309")
    draw.ellipse([(140, 110), (220, 200)], fill="#92400e")
    draw.rectangle([(145, 50), (215, 75)], fill="#1c1917")
    draw.rectangle([(135, 70), (225, 76)], fill="#1c1917")
    draw.line([(140, 140), (135, 230)], fill="#fbbf24", width=4)
    
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 15)
    draw.rectangle([(0, 230), (360, 270)], fill="#0f172a")
    draw.text((30, 240), "Памятник Бобру (ул. Социалистическая)", fill="#f8fafc", font=font)
    
    path = os.path.join(DEST_DIR, "bobr_statue.jpg")
    img.save(path, quality=92)
    print("Created:", path)

def create_fortress():
    img = Image.new("RGB", (360, 270), "#0f172a")
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (360, 150)], fill="#cbd5e1")
    draw.polygon([(0, 180), (100, 140), (260, 140), (360, 180), (360, 270), (0, 270)], fill="#4d7c0f")
    draw.rectangle([(80, 90), (280, 190)], fill="#991b1b")
    for x in range(80, 280, 25):
        draw.rectangle([(x, 75), (x + 15, 90)], fill="#991b1b")
    draw.ellipse([(150, 130), (210, 200)], fill="#1e1b4b")
    draw.rectangle([(150, 160), (210, 200)], fill="#1e1b4b")
    
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 15)
    draw.rectangle([(0, 230), (360, 270)], fill="#0f172a")
    draw.text((45, 240), "Бобруйская крепость (XIX век)", fill="#f8fafc", font=font)
    
    path = os.path.join(DEST_DIR, "fortress.jpg")
    img.save(path, quality=92)
    print("Created:", path)

def create_developer_photo():
    img = Image.new("RGB", (200, 240), "#e2e8f0")
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (200, 240)], fill="#1e293b")
    draw.rectangle([(8, 8), (192, 232)], fill="#334155")
    
    draw.ellipse([(65, 45), (135, 115)], fill="#f1f5f9")
    draw.rectangle([(65, 75), (135, 88)], fill="#0284c7")
    draw.ellipse([(55, 38), (145, 65)], fill="#0f172a")
    draw.ellipse([(30, 120), (170, 250)], fill="#0284c7")
    draw.polygon([(85, 125), (100, 165), (115, 125)], fill="#ffffff")
    
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 13)
    draw.rectangle([(0, 195), (200, 240)], fill="#0f172a")
    draw.text((25, 202), "Лабынцев Денис", fill="#38bdf8", font=font)
    font_sub = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 11)
    draw.text((42, 220), "Программист (РС02-23)", fill="#94a3b8", font=font_sub)
    
    path = os.path.join(DEST_DIR, "developer.jpg")
    img.save(path, quality=95)
    print("Created:", path)

def create_video_poster():
    img = Image.new("RGB", (480, 270), "#0f172a")
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (480, 180)], fill="#1e3a8a")
    draw.polygon([(0, 200), (120, 150), (280, 150), (480, 200), (480, 270), (0, 270)], fill="#065f46")
    
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
    draw.text((70, 70), "Бобруйск — Город над Березиной", fill="#ffffff", font=font)
    
    draw.ellipse([(210, 110), (270, 170)], fill="#ef4444")
    draw.polygon([(230, 125), (230, 155), (255, 140)], fill="#ffffff")
    
    font_sub = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
    draw.text((150, 225), "Видеоэкскурсия по городу (mp4)", fill="#cbd5e1", font=font_sub)
    
    path = os.path.join(DEST_DIR, "video_poster.jpg")
    img.save(path, quality=92)
    print("Created:", path)

def create_audio():
    path = os.path.join(DEST_DIR, "audio_bobruisk.wav")
    sample_rate = 22050
    duration = 2.5
    num_samples = int(sample_rate * duration)
    
    with wave.open(path, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        frames = []
        for i in range(num_samples):
            t = float(i) / sample_rate
            env = math.exp(-2.0 * t)
            s = 0.5 * math.sin(2 * math.pi * 440.0 * t) + \
                0.3 * math.sin(2 * math.pi * 554.37 * t) + \
                0.2 * math.sin(2 * math.pi * 659.25 * t)
            val = int(s * env * 25000.0)
            val = max(-32767, min(32767, val))
            frames.append(struct.pack('<h', val))
        wav_file.writeframes(b''.join(frames))
    print("Created audio:", path)

def create_video():
    path = os.path.join(DEST_DIR, "bobruisk_video.mp4")
    w, h = 480, 270
    fps = 20
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, fps, (w, h))
    
    for frame_idx in range(fps * 2):
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:] = (138, 58, 30)
        frame[180:h, :] = (40, 100, 30)
        cv2.putText(frame, "Bobruisk 1387 - 2026", (60, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        cv2.putText(frame, "Welcome to Bobruisk!", (120, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 220, 255), 2)
        cx = int(80 + (frame_idx * 7) % 320)
        cv2.circle(frame, (cx, 220), 12, (0, 255, 255), -1)
        out.write(frame)
    out.release()
    print("Created video:", path)

if __name__ == "__main__":
    create_bg_pattern()
    create_emblem()
    create_bobr_statue()
    create_fortress()
    create_developer_photo()
    create_video_poster()
    create_audio()
    create_video()
    print("ALL MEDIA ASSETS GENERATED!")
