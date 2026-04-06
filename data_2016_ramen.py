"""
2016年 田町・三田エリアのラーメン店データ
食べログの閉店ページ・現存ページから復元した店舗リスト
住所 → ジオコーディングで緯度経度を取得
"""
import csv
import json
import os
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 2016年時点で営業していたと推定されるラーメン店
# ソース: 食べログ閉店ページ + 現存ページ + PDF画像
# ============================================================
RAMEN_2016_SHOPS = [
    # --- A) 現在も営業中 ---
    {"name": "ラーメン二郎 三田本店", "address": "港区三田2-16-4", "rating_2016": 3.68,
     "status": "営業中", "source": "PDF+tabelog"},
    {"name": "むらさき山", "address": "港区芝5-23-8", "rating_2016": 3.55,
     "status": "営業中", "source": "PDF+tabelog"},
    {"name": "横浜家系らーめん 武源家", "address": "港区三田3-1-2", "rating_2016": 3.55,
     "status": "営業中", "source": "PDF(武蔵家表記)+tabelog"},
    {"name": "やっとこ 三田店", "address": "港区三田3-1-1", "rating_2016": 3.52,
     "status": "営業中", "source": "PDF+tabelog"},
    {"name": "博多一瑞亭 三田店", "address": "港区芝5-25-11", "rating_2016": 3.54,
     "status": "営業中", "source": "tabelog"},
    {"name": "三田製麺所 三田本店", "address": "港区芝5-22-8", "rating_2016": 3.31,
     "status": "営業中", "source": "tabelog"},
    {"name": "壱角家 田町店", "address": "港区芝浦3-7-15", "rating_2016": 3.08,
     "status": "営業中", "source": "tabelog(2015/7開業)"},
    {"name": "麻布ラーメン 芝四丁目店", "address": "港区芝4-5-15", "rating_2016": 3.29,
     "status": "営業中", "source": "tabelog"},
    {"name": "豚骨醤油らーめん 學虎", "address": "港区芝5-31-7", "rating_2016": 3.06,
     "status": "営業中", "source": "tabelog"},
    {"name": "香家 三田店", "address": "港区芝5-29-18", "rating_2016": 3.41,
     "status": "営業中", "source": "tabelog"},

    # --- B) 現在は閉店（食べログにページ残存） ---
    {"name": "麺屋武蔵 芝浦店", "address": "港区芝浦3-12-5", "rating_2016": 3.54,
     "status": "閉店", "source": "PDF+tabelog"},
    {"name": "ますたにラーメン 田町店", "address": "港区芝5-25-9", "rating_2016": 3.50,
     "status": "閉店", "source": "tabelog"},
    {"name": "麻布ラーメン 芝浦店", "address": "港区芝浦3-12-4", "rating_2016": 3.30,
     "status": "閉店", "source": "tabelog(2007/11開業)"},
    {"name": "麻布ラーメン 慶應三田店", "address": "港区芝5-14-14", "rating_2016": 3.20,
     "status": "閉店", "source": "tabelog"},
    {"name": "太陽のトマト麺 三田店", "address": "港区三田3-3-3", "rating_2016": 3.15,
     "status": "閉店", "source": "tabelog(2012/1開業)"},
    {"name": "てるぼうず", "address": "港区芝5-21-15", "rating_2016": 3.20,
     "status": "閉店", "source": "tabelog(2012/2開業)"},
    {"name": "太龍軒 田町店", "address": "港区芝5-17-11", "rating_2016": 3.10,
     "status": "閉店", "source": "tabelog(2013/1開業)"},
    {"name": "壱角家 三田店", "address": "港区三田3-1-13", "rating_2016": 3.05,
     "status": "閉店", "source": "tabelog(2014/7開業)"},
    {"name": "麺屋武蔵 芝浦別巻", "address": "港区芝浦3-6-8", "rating_2016": 3.40,
     "status": "閉店", "source": "tabelog(2015/1開業)"},
    {"name": "北の大地 三田店", "address": "港区芝5-25-7", "rating_2016": 3.10,
     "status": "閉店", "source": "tabelog"},
    {"name": "天下一品 田町店", "address": "港区芝5-17-11", "rating_2016": 3.05,
     "status": "閉店", "source": "tabelog(2016/1開業)"},
    {"name": "らぁめん 丸", "address": "港区芝5-30-5", "rating_2016": 3.10,
     "status": "閉店", "source": "tabelog(2008/2開業)"},
    {"name": "四天王 田町店", "address": "港区芝5-31-15", "rating_2016": 3.00,
     "status": "閉店", "source": "tabelog"},
    {"name": "げんこつ屋 三田店", "address": "港区芝5-31-7", "rating_2016": 3.00,
     "status": "閉店", "source": "tabelog"},
    {"name": "麺処こぶし 慶應通り店", "address": "港区芝5-24-12", "rating_2016": 3.10,
     "status": "閉店", "source": "tabelog(2010/11開業)"},
    {"name": "日の出らーめん 田町分店", "address": "港区芝5-11-13", "rating_2016": 3.05,
     "status": "閉店", "source": "tabelog(2010/11開業)"},
    {"name": "天空", "address": "港区三田3-3-6", "rating_2016": 3.10,
     "status": "閉店(移転)", "source": "tabelog"},
]


def geocode_shops(shops, cache_path=None):
    """住所からジオコーディングで緯度経度を取得（キャッシュ付き）"""
    cache = {}
    if cache_path and os.path.exists(cache_path):
        with open(cache_path) as f:
            cache = json.load(f)

    geolocator = Nominatim(user_agent="undergradi_research_2026", timeout=10)
    results = []

    for shop in shops:
        name = shop["name"]
        addr = shop["address"]
        full_addr = f"東京都{addr}"

        if name in cache:
            lat, lng = cache[name]["lat"], cache[name]["lng"]
            print(f"  [cache] {name}: ({lat}, {lng})")
        else:
            try:
                location = geolocator.geocode(full_addr)
                if location:
                    lat, lng = location.latitude, location.longitude
                    print(f"  [geocode] {name}: ({lat:.6f}, {lng:.6f})")
                else:
                    # 住所を短縮して再試行
                    short_addr = "東京都" + addr.split("-")[0] if "-" in addr else full_addr
                    location = geolocator.geocode(short_addr)
                    if location:
                        lat, lng = location.latitude, location.longitude
                        print(f"  [geocode-short] {name}: ({lat:.6f}, {lng:.6f})")
                    else:
                        lat, lng = None, None
                        print(f"  [FAIL] {name}: geocoding failed for {full_addr}")
                cache[name] = {"lat": lat, "lng": lng, "address": addr}
                time.sleep(1.5)  # rate limit
            except GeocoderTimedOut:
                lat, lng = None, None
                print(f"  [TIMEOUT] {name}")
                time.sleep(3)

        result = dict(shop)
        result["lat"] = lat
        result["lng"] = lng
        results.append(result)

    if cache_path:
        with open(cache_path, "w") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)

    return results


def save_csv(results, path):
    """結果をCSV保存"""
    fields = ["name", "address", "lat", "lng", "rating_2016", "status", "source"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k) for k in fields})
    print(f"Saved {len(results)} shops to {path}")


if __name__ == "__main__":
    print(f"=== 2016年ラーメン店 ジオコーディング ({len(RAMEN_2016_SHOPS)}店) ===\n")

    cache_path = os.path.join(BASE_DIR, "data", "geocode_cache.json")
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

    results = geocode_shops(RAMEN_2016_SHOPS, cache_path=cache_path)

    csv_path = os.path.join(BASE_DIR, "data", "ramen_2016_complete.csv")
    save_csv(results, csv_path)

    # サマリー
    geocoded = sum(1 for r in results if r["lat"] is not None)
    failed = sum(1 for r in results if r["lat"] is None)
    print(f"\n=== 結果: {geocoded} 成功, {failed} 失敗 (全{len(results)}店) ===")
