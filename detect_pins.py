"""
地図画像からTabelogのオレンジピン（Google Maps上のマーカー）を検出する
"""
import cv2
import numpy as np
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def detect_orange_pins(image_path, output_path=None, debug=False):
    """
    オレンジ色のピンを検出し、中心座標（ピクセル）のリストを返す
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    h_img, w_img = img.shape[:2]

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Tabelog/Google Mapsのオレンジピンマーカー
    # 道路の黄色と区別するため、より彩度の高いオレンジに限定
    lower_orange = np.array([8, 160, 180])
    upper_orange = np.array([22, 255, 255])

    # 赤寄りのマーカーも対象
    lower_red = np.array([0, 170, 190])
    upper_red = np.array([8, 255, 255])

    mask1 = cv2.inRange(hsv, lower_orange, upper_orange)
    mask2 = cv2.inRange(hsv, lower_red, upper_red)
    mask = cv2.bitwise_or(mask1, mask2)

    # ノイズ除去
    kernel = np.ones((2, 2), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    if debug:
        cv2.imwrite(os.path.join(BASE_DIR, "debug_mask.png"), mask)

    # 輪郭検出
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    pins = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # ピンは小〜中サイズ（50〜800ピクセル程度）
        if 30 < area < 800:
            # 形状フィルタ: コンパクトさ（circularity）で細長い道路を除外
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            # ピンはある程度コンパクト（>0.2）、道路は細長い（<0.1）
            if circularity < 0.15:
                continue

            M = cv2.moments(cnt)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                # 画像端のUI要素を除外（マージン5%）
                margin_x = int(w_img * 0.03)
                margin_y = int(h_img * 0.03)
                if cx < margin_x or cx > w_img - margin_x:
                    continue
                if cy < margin_y or cy > h_img - margin_y:
                    continue

                pins.append({
                    "x": cx, "y": cy,
                    "area": int(area),
                    "circularity": round(circularity, 3)
                })

    # 近接するピンを統合
    merged = merge_nearby_pins(pins, threshold=20)

    if output_path:
        result_img = img.copy()
        for i, p in enumerate(merged):
            cv2.circle(result_img, (p["x"], p["y"]), 15, (0, 255, 0), 2)
            cv2.putText(result_img, str(i+1), (p["x"]+18, p["y"]+5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.imwrite(output_path, result_img)

    return merged


def merge_nearby_pins(pins, threshold=20):
    """距離がthreshold以下のピンを統合"""
    if not pins:
        return []

    used = [False] * len(pins)
    merged = []

    for i in range(len(pins)):
        if used[i]:
            continue
        group = [pins[i]]
        used[i] = True
        for j in range(i + 1, len(pins)):
            if used[j]:
                continue
            dist = np.sqrt((pins[i]["x"] - pins[j]["x"])**2 +
                           (pins[i]["y"] - pins[j]["y"])**2)
            if dist < threshold:
                group.append(pins[j])
                used[j] = True

        avg_x = int(np.mean([p["x"] for p in group]))
        avg_y = int(np.mean([p["y"] for p in group]))
        total_area = sum(p["area"] for p in group)
        merged.append({"x": avg_x, "y": avg_y, "area": total_area})

    return merged


if __name__ == "__main__":
    for name in ["map_ramen_2016", "map_gyudon_2016"]:
        img_path = os.path.join(BASE_DIR, f"{name}.png")
        out_path = os.path.join(BASE_DIR, f"{name}_detected.png")

        pins = detect_orange_pins(img_path, output_path=out_path,
                                  debug=(name == "map_ramen_2016"))
        print(f"\n{name}: {len(pins)} pins detected")
        for i, p in enumerate(pins):
            print(f"  Pin {i+1}: pixel=({p['x']}, {p['y']}), "
                  f"area={p['area']}")

        json_path = os.path.join(BASE_DIR, f"{name}_pins.json")
        with open(json_path, "w") as f:
            json.dump(pins, f, indent=2)
