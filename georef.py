"""
地図画像のジオリファレンシング:
既知のランドマークのピクセル座標と緯度経度から、アフィン変換行列を求め、
検出済みピンのピクセル座標を緯度経度に変換する
"""
import numpy as np
import cv2
import json
import os
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 参照点の定義（ピクセル座標 → 緯度経度）
# 地図上の明確に特定可能なランドマークを使用
# ============================================================

# --- ラーメン 2016年地図 (1520 x 1390) ---
# 画像上で目視・色検出で正確に特定した参照点
RAMEN_2016_REF_CANDIDATES = [
    # (name, pixel_x, pixel_y, lat, lng)
    # 三田駅: 緑アイコン中心（色検出で確認済み）
    ("三田駅", 797, 523, 35.64880, 139.74690),
    # 田町駅西口: テキストボックス左端位置
    ("田町駅西口", 575, 692, 35.64600, 139.74620),
    # JR田町: 青い電車アイコン（右下エリアで確認）
    ("JR田町", 668, 812, 35.64540, 139.74760),
    # 三田通り交差前: テキストボックス中心
    ("三田通り交差前", 400, 210, 35.65090, 139.74370),
]


def mark_reference_points(image_path, ref_points, output_path):
    """参照点を画像上にマークして確認用画像を出力"""
    img = cv2.imread(image_path)
    for name, px, py, lat, lng in ref_points:
        cv2.circle(img, (px, py), 10, (255, 0, 0), 3)  # 青い丸
        cv2.drawMarker(img, (px, py), (0, 0, 255), cv2.MARKER_CROSS, 20, 2)
        cv2.putText(img, name, (px + 15, py - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    cv2.imwrite(output_path, img)
    print(f"Reference points marked: {output_path}")


def compute_affine(ref_points):
    """
    参照点リストからアフィン変換行列を最小二乗法で求める
    pixel (x,y) → (lat, lng)
    """
    n = len(ref_points)
    # A * params = b
    # lat = a0 + a1*x + a2*y
    # lng = b0 + b1*x + b2*y
    A = np.zeros((n, 3))
    lat_vec = np.zeros(n)
    lng_vec = np.zeros(n)

    for i, (name, px, py, lat, lng) in enumerate(ref_points):
        A[i] = [1, px, py]
        lat_vec[i] = lat
        lng_vec[i] = lng

    # 最小二乗法
    lat_params, lat_res, _, _ = np.linalg.lstsq(A, lat_vec, rcond=None)
    lng_params, lng_res, _, _ = np.linalg.lstsq(A, lng_vec, rcond=None)

    print(f"Affine transform (lat): {lat_params}")
    print(f"Affine transform (lng): {lng_params}")

    # 残差チェック
    if len(lat_res) > 0:
        print(f"Lat residual: {np.sqrt(lat_res[0]/n):.6f} degrees "
              f"≈ {np.sqrt(lat_res[0]/n)*111000:.1f} m")
    if len(lng_res) > 0:
        print(f"Lng residual: {np.sqrt(lng_res[0]/n):.6f} degrees "
              f"≈ {np.sqrt(lng_res[0]/n)*91000:.1f} m")

    # 各参照点での誤差
    for name, px, py, lat, lng in ref_points:
        pred_lat = lat_params[0] + lat_params[1]*px + lat_params[2]*py
        pred_lng = lng_params[0] + lng_params[1]*px + lng_params[2]*py
        err_m = np.sqrt(((pred_lat-lat)*111000)**2 + ((pred_lng-lng)*91000)**2)
        print(f"  {name}: error = {err_m:.1f} m")

    return lat_params, lng_params


def pixel_to_latlng(px, py, lat_params, lng_params):
    """ピクセル座標を緯度経度に変換"""
    lat = lat_params[0] + lat_params[1]*px + lat_params[2]*py
    lng = lng_params[0] + lng_params[1]*px + lng_params[2]*py
    return lat, lng


def transform_pins(pins_json_path, lat_params, lng_params, output_csv_path):
    """検出済みピンをすべて緯度経度に変換してCSV出力"""
    with open(pins_json_path) as f:
        pins = json.load(f)

    results = []
    for i, pin in enumerate(pins):
        lat, lng = pixel_to_latlng(pin["x"], pin["y"], lat_params, lng_params)
        results.append({
            "id": i + 1,
            "pixel_x": pin["x"],
            "pixel_y": pin["y"],
            "lat": round(lat, 6),
            "lng": round(lng, 6),
        })
        print(f"  Pin {i+1}: ({pin['x']}, {pin['y']}) → "
              f"({lat:.6f}, {lng:.6f})")

    with open(output_csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "pixel_x", "pixel_y", "lat", "lng"])
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved: {output_csv_path}")
    return results


if __name__ == "__main__":
    # Step 1: 参照点を画像上にマークして目視確認
    print("=== Marking reference points ===")
    mark_reference_points(
        os.path.join(BASE_DIR, "map_ramen_2016.png"),
        RAMEN_2016_REF_CANDIDATES,
        os.path.join(BASE_DIR, "map_ramen_2016_refpoints.png")
    )

    # Step 2: アフィン変換を計算
    print("\n=== Computing affine transform (Ramen 2016) ===")
    lat_p, lng_p = compute_affine(RAMEN_2016_REF_CANDIDATES)

    # Step 3: 検出済みピンを変換
    print("\n=== Transforming pins ===")
    transform_pins(
        os.path.join(BASE_DIR, "map_ramen_2016_pins.json"),
        lat_p, lng_p,
        os.path.join(BASE_DIR, "ramen_2016_coords.csv")
    )
