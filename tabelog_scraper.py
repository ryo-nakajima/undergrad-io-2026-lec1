"""
食べログスクレイパー
- 一覧ページから店舗URL取得
- 詳細ページから緯度経度・住所・評価等を取得
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
os.makedirs(DATA_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}

# 田町・三田エリア
AREA_CODE = "A1314/A131402"
BASE_URL = "https://tabelog.com/tokyo"


def fetch_page(url, delay=3):
    """ページを取得（レート制限付き）"""
    time.sleep(delay)
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.text


def get_shop_list(genre_code, max_pages=5):
    """
    一覧ページから店舗URLリストを取得
    genre_code: MC0101 (ラーメン), RC011101 (牛丼) etc.
    """
    shops = []
    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/{AREA_CODE}/rstLst/{genre_code}/{page}/"
        print(f"  Fetching list page {page}: {url}")
        try:
            html = fetch_page(url)
        except Exception as e:
            print(f"    Error: {e}")
            break

        soup = BeautifulSoup(html, "html.parser")

        # 店舗リンクを取得
        found = 0
        for a_tag in soup.select("a.list-rst__rst-name-target"):
            name = a_tag.get_text(strip=True)
            href = a_tag.get("href", "")
            if href and name:
                shops.append({"name": name, "url": href})
                found += 1

        print(f"    Found {found} shops")
        if found == 0:
            break

    return shops


def get_shop_detail(url):
    """
    詳細ページから店舗情報を抽出
    - 緯度・経度 (lat, lng)
    - 住所
    - 評価
    - ジャンル
    """
    html = fetch_page(url)
    soup = BeautifulSoup(html, "html.parser")

    info = {"url": url}

    # 店名
    title_tag = soup.select_one("h2.display-name span")
    if title_tag:
        info["name"] = title_tag.get_text(strip=True)

    # 評価
    rating_tag = soup.select_one("b.c-rating__val")
    if not rating_tag:
        rating_tag = soup.select_one("span.rdheader-rating__score-val-dtl")
    if rating_tag:
        try:
            info["rating"] = float(rating_tag.get_text(strip=True))
        except ValueError:
            pass

    # 口コミ数
    review_tag = soup.select_one("a.rdheader-rating__review-target em")
    if review_tag:
        try:
            info["reviews"] = int(review_tag.get_text(strip=True))
        except ValueError:
            pass

    # 住所
    addr_tag = soup.select_one("p.rstinfo-table__address")
    if addr_tag:
        info["address"] = addr_tag.get_text(strip=True)

    # 緯度経度（HTMLソース内のJavaScriptから抽出）
    lat_match = re.search(r"lat['\"]?\s*[:=]\s*([0-9]+\.[0-9]+)", html)
    lng_match = re.search(r"lng['\"]?\s*[:=]\s*([0-9]+\.[0-9]+)", html)
    if lat_match and lng_match:
        info["lat"] = float(lat_match.group(1))
        info["lng"] = float(lng_match.group(1))

    # ジャンル
    genre_tags = soup.select("span.linktree__parent-target-text")
    if genre_tags:
        info["genre"] = ", ".join(t.get_text(strip=True) for t in genre_tags)

    # 閉店フラグ
    if "【閉店】" in html or "閉店" in (info.get("name", "")):
        info["closed"] = True

    return info


def scrape_area(genre_code, genre_name, max_pages=5, cache_file=None):
    """
    エリア内の全店舗データを取得
    """
    # キャッシュチェック
    if cache_file and os.path.exists(cache_file):
        with open(cache_file) as f:
            cached = json.load(f)
        print(f"Loaded {len(cached)} shops from cache: {cache_file}")
        return cached

    print(f"\n=== {genre_name} 一覧取得 ===")
    shop_list = get_shop_list(genre_code, max_pages=max_pages)
    print(f"Total: {len(shop_list)} shops found")

    print(f"\n=== 詳細ページ取得 ===")
    results = []
    for i, shop in enumerate(shop_list):
        print(f"  [{i+1}/{len(shop_list)}] {shop['name']}")
        try:
            detail = get_shop_detail(shop["url"])
            results.append(detail)
            if detail.get("lat"):
                print(f"    → ({detail['lat']:.6f}, {detail['lng']:.6f})")
            else:
                print(f"    → 座標取得失敗")
        except Exception as e:
            print(f"    → ERROR: {e}")
            results.append({"name": shop["name"], "url": shop["url"], "error": str(e)})

    # キャッシュ保存
    if cache_file:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Saved cache: {cache_file}")

    return results


def results_to_csv(results, csv_path):
    """結果をCSV保存"""
    fields = ["name", "address", "lat", "lng", "rating", "reviews", "genre",
              "closed", "url"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    print(f"CSV saved: {csv_path} ({len(results)} shops)")


if __name__ == "__main__":
    # 2026年 ラーメン
    ramen = scrape_area(
        "MC0101", "ラーメン (2026)",
        max_pages=5,
        cache_file=os.path.join(DATA_DIR, "tabelog_ramen_2026.json")
    )
    results_to_csv(ramen, os.path.join(DATA_DIR, "ramen_2026.csv"))

    # 2026年 牛丼
    gyudon = scrape_area(
        "RC011101", "牛丼 (2026)",
        max_pages=2,
        cache_file=os.path.join(DATA_DIR, "tabelog_gyudon_2026.json")
    )
    results_to_csv(gyudon, os.path.join(DATA_DIR, "gyudon_2026.csv"))
