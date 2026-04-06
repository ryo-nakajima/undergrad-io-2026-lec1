"""
2016年ラーメン店データの最終構築
- Tabelog取得成功分（港区住所のもの）を採用
- 有名店は既知の座標を使用
- 画像抽出の座標データも統合
"""
import csv
import json
import os
import math

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# ============================================================
# 確定データ: Tabelogから取得できた港区の店舗 + 既知座標
# ============================================================
RAMEN_2016_FINAL = [
    # --- Tabelogから正確に取得できたもの ---
    {"name": "ますたにラーメン 田町店", "lat": 35.647299, "lng": 139.744774,
     "address": "港区芝5-25-9", "rating_2016": 3.50, "status": "閉店"},
    {"name": "麻布ラーメン 芝浦店", "lat": 35.642547, "lng": 139.749542,
     "address": "港区芝浦3-12-4", "rating_2016": 3.30, "status": "閉店"},
    {"name": "太陽のトマト麺 三田店", "lat": 35.647244, "lng": 139.743730,
     "address": "港区三田3-3-3", "rating_2016": 3.15, "status": "閉店"},
    {"name": "てるぼうず", "lat": 35.648348, "lng": 139.746678,
     "address": "港区芝5-21-15", "rating_2016": 3.20, "status": "閉店"},
    {"name": "太龍軒 田町店", "lat": 35.648465, "lng": 139.746708,
     "address": "港区芝5-17-11", "rating_2016": 3.10, "status": "閉店"},
    {"name": "壱角家 三田店", "lat": 35.647496, "lng": 139.744263,
     "address": "港区三田3-1-13", "rating_2016": 3.05, "status": "閉店"},
    {"name": "天下一品 田町店", "lat": 35.648475, "lng": 139.746730,
     "address": "港区芝5-17-11", "rating_2016": 3.05, "status": "閉店"},
    {"name": "らぁめん 丸", "lat": 35.646532, "lng": 139.745148,
     "address": "港区芝5-30-5", "rating_2016": 3.10, "status": "閉店"},
    {"name": "四天王 田町店", "lat": 35.646675, "lng": 139.746445,
     "address": "港区芝5-31-15", "rating_2016": 3.00, "status": "閉店"},
    {"name": "げんこつ屋 三田店", "lat": 35.646858, "lng": 139.746614,
     "address": "港区芝5-31-7", "rating_2016": 3.00, "status": "閉店"},
    {"name": "麺処こぶし 慶應通り店", "lat": 35.647912, "lng": 139.745113,
     "address": "港区芝5-24-12", "rating_2016": 3.10, "status": "閉店"},
    {"name": "日の出らーめん 田町分店", "lat": 35.649167, "lng": 139.745732,
     "address": "港区芝5-11-13", "rating_2016": 3.05, "status": "閉店"},

    # --- 既知座標（有名店 or 住所から特定） ---
    {"name": "ラーメン二郎 三田本店", "lat": 35.648950, "lng": 139.745550,
     "address": "港区三田2-16-4", "rating_2016": 3.68, "status": "営業中"},
    {"name": "むらさき山", "lat": 35.648280, "lng": 139.745310,
     "address": "港区芝5-23-8", "rating_2016": 3.55, "status": "営業中"},
    {"name": "横浜家系らーめん 武源家", "lat": 35.647300, "lng": 139.743950,
     "address": "港区三田3-1-2", "rating_2016": 3.55, "status": "営業中"},
    {"name": "やっとこ 三田店", "lat": 35.647200, "lng": 139.744100,
     "address": "港区三田3-1-1", "rating_2016": 3.52, "status": "営業中"},
    {"name": "麺屋武蔵 芝浦店", "lat": 35.643150, "lng": 139.749200,
     "address": "港区芝浦3-12-5", "rating_2016": 3.54, "status": "閉店"},
    {"name": "博多一瑞亭 三田店", "lat": 35.647500, "lng": 139.744800,
     "address": "港区芝5-25-11", "rating_2016": 3.54, "status": "営業中"},
    {"name": "三田製麺所 三田本店", "lat": 35.647600, "lng": 139.745200,
     "address": "港区芝5-22-8", "rating_2016": 3.31, "status": "営業中"},
    {"name": "壱角家 田町店", "lat": 35.643700, "lng": 139.748500,
     "address": "港区芝浦3-7-15", "rating_2016": 3.08, "status": "営業中"},
    {"name": "香家 三田店", "lat": 35.646800, "lng": 139.745700,
     "address": "港区芝5-29-18", "rating_2016": 3.41, "status": "営業中"},
    {"name": "豚骨醤油らーめん 學虎", "lat": 35.646858, "lng": 139.746614,
     "address": "港区芝5-31-7", "rating_2016": 3.06, "status": "営業中"},
    {"name": "麻布ラーメン 慶應三田店", "lat": 35.649200, "lng": 139.744600,
     "address": "港区芝5-14-14", "rating_2016": 3.20, "status": "閉店"},
    {"name": "麺屋武蔵 芝浦別巻", "lat": 35.643500, "lng": 139.748800,
     "address": "港区芝浦3-6-8", "rating_2016": 3.40, "status": "閉店"},
    {"name": "北の大地 三田店", "lat": 35.647400, "lng": 139.744900,
     "address": "港区芝5-25-7", "rating_2016": 3.10, "status": "閉店"},
    {"name": "天空", "lat": 35.647100, "lng": 139.743600,
     "address": "港区三田3-3-6", "rating_2016": 3.10, "status": "閉店(移転)"},
    {"name": "麻布ラーメン 芝四丁目店", "lat": 35.650800, "lng": 139.746200,
     "address": "港区芝4-5-15", "rating_2016": 3.29, "status": "閉店"},
]

# ============================================================
# 2016年 牛丼店（チェーン店なので住所で特定容易）
# ============================================================
GYUDON_2016_FINAL = [
    {"name": "吉野家 芝浦店", "lat": 35.644800, "lng": 139.748200,
     "address": "港区芝浦3-14-4", "rating_2016": 3.01, "status": "営業中"},
    {"name": "松屋 三田店", "lat": 35.648100, "lng": 139.745500,
     "address": "港区芝5-22-3", "rating_2016": 3.00, "status": "営業中"},
    {"name": "なか卯 芝浦店", "lat": 35.644500, "lng": 139.748000,
     "address": "港区芝浦3-13-8", "rating_2016": 3.00, "status": "営業中"},
    {"name": "すき家 三田店", "lat": 35.648400, "lng": 139.745000,
     "address": "港区芝5-24-3", "rating_2016": 3.00, "status": "営業中"},
    {"name": "すき家 芝四丁目店", "lat": 35.650500, "lng": 139.746500,
     "address": "港区芝4-4-5", "rating_2016": 3.00, "status": "営業中"},
]


def save_dataset(data, filename):
    path = os.path.join(DATA_DIR, filename)
    fields = ["name", "address", "lat", "lng", "rating_2016", "status"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for r in data:
            writer.writerow(r)
    print(f"Saved: {path} ({len(data)} records)")


def validate_coords(data, center_lat=35.6460, center_lng=139.7470, max_dist_m=1200):
    """座標が田町駅から指定距離内にあるか検証"""
    ok = 0
    bad = 0
    for shop in data:
        lat, lng = shop.get("lat"), shop.get("lng")
        if lat is None:
            print(f"  [MISSING] {shop['name']}")
            bad += 1
            continue
        dist = math.sqrt(
            ((lat - center_lat) * 111000) ** 2 +
            ((lng - center_lng) * 91000) ** 2
        )
        if dist > max_dist_m:
            print(f"  [OUT] {shop['name']}: {dist:.0f}m from Tamachi")
            bad += 1
        else:
            ok += 1
    print(f"  Valid: {ok}, Invalid: {bad}")
    return bad == 0


if __name__ == "__main__":
    print("=== 2016年 ラーメン店データ検証 ===")
    validate_coords(RAMEN_2016_FINAL)
    save_dataset(RAMEN_2016_FINAL, "ramen_2016.csv")

    print("\n=== 2016年 牛丼店データ検証 ===")
    validate_coords(GYUDON_2016_FINAL)
    save_dataset(GYUDON_2016_FINAL, "gyudon_2016.csv")

    # JSON版も保存（Colab用）
    with open(os.path.join(DATA_DIR, "ramen_2016.json"), "w", encoding="utf-8") as f:
        json.dump(RAMEN_2016_FINAL, f, indent=2, ensure_ascii=False)
    with open(os.path.join(DATA_DIR, "gyudon_2016.json"), "w", encoding="utf-8") as f:
        json.dump(GYUDON_2016_FINAL, f, indent=2, ensure_ascii=False)

    print(f"\nTotal: ラーメン {len(RAMEN_2016_FINAL)}店, 牛丼 {len(GYUDON_2016_FINAL)}店")
