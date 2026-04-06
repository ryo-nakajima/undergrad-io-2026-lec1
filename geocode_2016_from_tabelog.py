"""
2016年ラーメン店の座標を食べログページから直接取得する
閉店済み店舗もページが残っているため、そこからlat/lngを抽出
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import json
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}

# 2016年の店舗 → 食べログURL（エージェント調査で判明したもの + 検索で特定）
SHOPS_2016 = [
    # 営業中の店舗
    {"name": "ラーメン二郎 三田本店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13000629/",
     "rating_2016": 3.68, "status": "営業中"},
    {"name": "むらさき山",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13007908/",
     "rating_2016": 3.55, "status": "営業中"},
    {"name": "横浜家系らーめん 武源家",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13166543/",
     "rating_2016": 3.55, "status": "営業中"},
    {"name": "やっとこ 三田店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13016879/",
     "rating_2016": 3.52, "status": "営業中"},
    {"name": "博多一瑞亭 三田店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13164693/",
     "rating_2016": 3.54, "status": "営業中"},
    {"name": "三田製麺所 三田本店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13120268/",
     "rating_2016": 3.31, "status": "営業中"},
    {"name": "壱角家 田町店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13185419/",
     "rating_2016": 3.08, "status": "営業中"},
    {"name": "香家 三田店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13200098/",
     "rating_2016": 3.41, "status": "営業中"},
    {"name": "豚骨醤油らーめん 學虎",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13163849/",
     "rating_2016": 3.06, "status": "営業中"},

    # 閉店済み店舗（食べログにページ残存）
    {"name": "麺屋武蔵 芝浦店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13172459/",
     "rating_2016": 3.54, "status": "閉店"},
    {"name": "ますたにラーメン 田町店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13004559/",
     "rating_2016": 3.50, "status": "閉店"},
    {"name": "麻布ラーメン 芝浦店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13045263/",
     "rating_2016": 3.30, "status": "閉店"},
    {"name": "太陽のトマト麺 三田店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13136230/",
     "rating_2016": 3.15, "status": "閉店"},
    {"name": "てるぼうず",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13138169/",
     "rating_2016": 3.20, "status": "閉店"},
    {"name": "太龍軒 田町店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13151567/",
     "rating_2016": 3.10, "status": "閉店"},
    {"name": "壱角家 三田店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13170815/",
     "rating_2016": 3.05, "status": "閉店"},
    {"name": "麺屋武蔵 芝浦別巻",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13181004/",
     "rating_2016": 3.40, "status": "閉店"},
    {"name": "天下一品 田町店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13190910/",
     "rating_2016": 3.05, "status": "閉店"},
    {"name": "らぁめん 丸",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13051388/",
     "rating_2016": 3.10, "status": "閉店"},
    {"name": "四天王 田町店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13024111/",
     "rating_2016": 3.00, "status": "閉店"},
    {"name": "げんこつ屋 三田店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13014005/",
     "rating_2016": 3.00, "status": "閉店"},
    {"name": "麺処こぶし 慶應通り店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13119916/",
     "rating_2016": 3.10, "status": "閉店"},
    {"name": "日の出らーめん 田町分店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13118516/",
     "rating_2016": 3.05, "status": "閉店"},
    {"name": "天空",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13002780/",
     "rating_2016": 3.10, "status": "閉店(移転)"},
    {"name": "麻布ラーメン 芝四丁目店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13175654/",
     "rating_2016": 3.29, "status": "閉店"},
    {"name": "北の大地 三田店",
     "tabelog_url": "https://tabelog.com/tokyo/A1314/A131402/13179668/",
     "rating_2016": 3.10, "status": "閉店"},
]


def extract_coords_from_tabelog(url):
    """食べログ詳細ページからlat/lngを抽出"""
    time.sleep(3)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        html = resp.text

        lat_match = re.search(r"lat['\"]?\s*[:=]\s*([0-9]+\.[0-9]+)", html)
        lng_match = re.search(r"lng['\"]?\s*[:=]\s*([0-9]+\.[0-9]+)", html)

        # 住所も取得
        soup = BeautifulSoup(html, "html.parser")
        addr_tag = soup.select_one("p.rstinfo-table__address")
        address = addr_tag.get_text(strip=True) if addr_tag else ""

        if lat_match and lng_match:
            return float(lat_match.group(1)), float(lng_match.group(1)), address
        return None, None, address
    except Exception as e:
        print(f"    Error: {e}")
        return None, None, ""


if __name__ == "__main__":
    cache_path = os.path.join(DATA_DIR, "tabelog_2016_coords_cache.json")

    # キャッシュ読み込み
    cache = {}
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            cache = json.load(f)

    print(f"=== 2016年ラーメン店 座標取得 ({len(SHOPS_2016)}店) ===\n")

    results = []
    for shop in SHOPS_2016:
        name = shop["name"]
        if name in cache and cache[name].get("lat"):
            lat, lng = cache[name]["lat"], cache[name]["lng"]
            address = cache[name].get("address", "")
            print(f"  [cache] {name}: ({lat}, {lng})")
        else:
            print(f"  [fetch] {name}: {shop['tabelog_url']}")
            lat, lng, address = extract_coords_from_tabelog(shop["tabelog_url"])
            if lat:
                print(f"    → ({lat:.6f}, {lng:.6f}) {address}")
                cache[name] = {"lat": lat, "lng": lng, "address": address}
            else:
                print(f"    → 座標取得失敗 (address: {address})")
                cache[name] = {"lat": None, "lng": None, "address": address}

        result = dict(shop)
        result["lat"] = lat
        result["lng"] = lng
        result["address"] = address
        results.append(result)

    # キャッシュ保存
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

    # CSV保存
    csv_path = os.path.join(DATA_DIR, "ramen_2016_complete.csv")
    fields = ["name", "address", "lat", "lng", "rating_2016", "status"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k) for k in fields})

    geocoded = sum(1 for r in results if r.get("lat"))
    failed = sum(1 for r in results if not r.get("lat"))
    print(f"\n=== 結果: {geocoded} 成功, {failed} 失敗 (全{len(results)}店) ===")
    print(f"CSV saved: {csv_path}")
