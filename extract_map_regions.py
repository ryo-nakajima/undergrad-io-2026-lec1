"""
PDFページ画像から地図部分のみを切り出すスクリプト
"""
from PIL import Image
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Page 2 = 2016年 (2400 x 3059 at 300dpi)
img = Image.open(os.path.join(BASE_DIR, "page2.png"))
w, h = img.size
print(f"Page2 full image size: {w} x {h}")

# 2016年 牛丼地図（リスト部分を除外、地図のみ）
gyudon_2016 = img.crop((830, 150, 2350, 1420))
gyudon_2016.save(os.path.join(BASE_DIR, "map_gyudon_2016.png"))
print(f"Gyudon 2016 map: {gyudon_2016.size}")

# 2016年 ラーメン地図
ramen_2016 = img.crop((830, 1560, 2350, 2950))
ramen_2016.save(os.path.join(BASE_DIR, "map_ramen_2016.png"))
print(f"Ramen 2016 map: {ramen_2016.size}")

# Page 1 = 2024年
img1 = Image.open(os.path.join(BASE_DIR, "page1.png"))
print(f"Page1 full image size: {img1.size}")

gyudon_2024 = img1.crop((770, 170, 2350, 1430))
gyudon_2024.save(os.path.join(BASE_DIR, "map_gyudon_2024.png"))
print(f"Gyudon 2024 map: {gyudon_2024.size}")

ramen_2024 = img1.crop((770, 1530, 2350, 2930))
ramen_2024.save(os.path.join(BASE_DIR, "map_ramen_2024.png"))
print(f"Ramen 2024 map: {ramen_2024.size}")

print("Done - map regions extracted")
