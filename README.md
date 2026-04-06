# 田町駅周辺 飲食店分布マッピング (2016 vs 2026)

田町駅・三田駅周辺のラーメン屋と牛丼屋の分布を2016年と2026年で比較するプロジェクト。
食べログ（Tabelog）のデータを独自の地図上にマッピングし、10年間の変遷を可視化する。

## 概要

- **2016年データ**: 食べログの地図検索スクリーンショット（PDF）から画像処理でピン座標を抽出 + 食べログの閉店ページから住所・座標を復元
- **2026年データ**: 食べログから直接スクレイピング（店名・評価・座標）
- **可視化**: foliumによるインタラクティブ地図（レイヤー切り替えで比較可能）

## ディレクトリ構成

```
code/
├── README.md                    # このファイル
├── NOTES.md                     # データ作成の詳細メモ
├── tamachi_restaurant_map.ipynb # メインのJupyterノートブック（地図表示）
├── data/                        # データファイル
│   ├── ramen_2016.csv           # 2016年ラーメン店（27店）
│   ├── gyudon_2016.csv          # 2016年牛丼店（5店）
│   ├── ramen_2026.csv           # 2026年ラーメン店（スクレイピング）
│   ├── gyudon_2026.csv          # 2026年牛丼店（スクレイピング）
│   └── *.json                   # キャッシュファイル
├── extract_map_regions.py       # PDF → 地図画像切り出し
├── detect_pins.py               # OpenCVによるピン検出
├── georef.py                    # ジオリファレンシング（ピクセル→緯度経度）
├── tabelog_scraper.py           # 食べログスクレイパー
├── build_2016_dataset.py        # 2016年データ構築
└── geocode_2016_from_tabelog.py # 食べログページからの座標取得
```

## データ作成手順

### 2016年データ

1. `extract_map_regions.py`: PDFから地図画像を切り出し
2. `detect_pins.py`: OpenCV (HSV色空間) でオレンジピンを自動検出
3. `georef.py`: 4参照点（三田駅・田町駅西口・JR田町・三田通り交差前）でアフィン変換を計算。座標精度 ≈ 15m (RMS)
4. `geocode_2016_from_tabelog.py` / `build_2016_dataset.py`: 食べログの閉店ページ等から住所・座標を取得し補完

### 2026年データ

1. `tabelog_scraper.py`: 食べログの一覧ページ (`/rstLst/MC0101/` 等) から店舗URL取得
2. 各店舗の詳細ページHTMLから `lat`, `lng` を正規表現で抽出

## 使い方

### ローカル実行

```bash
# 依存パッケージ
pip install folium pandas requests beautifulsoup4 opencv-python geopy pdf2image

# Jupyter Notebookで実行
jupyter notebook tamachi_restaurant_map.ipynb
```

### Google Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/)

`tamachi_restaurant_map.ipynb` をColabにアップロードして実行。
`data/` ディレクトリも合わせてアップロードが必要。

## 主な結果

| | 2016年 | 2026年 | 変化 |
|---|---|---|---|
| ラーメン店 | 27店 | 36店 | +9 |
| 牛丼店 | 5店 | 4店 | -1 |
| ラーメン存続店 | - | 8店 | - |

10年間でラーメン店の入れ替わりが激しく（19店閉店、28店新規開店）、牛丼店は大きな変動なし。
