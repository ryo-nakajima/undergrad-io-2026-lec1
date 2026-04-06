# undergrad-io-2026-lec1

学部ゼミ（2026年度）Lecture 1 用のノートブック・処理スクリプト集。
田町駅周辺の飲食店データを題材に、データ収集・可視化・分析を行う。

データは [undergrad-io-2026-data](https://github.com/ryo-nakajima/undergrad-io-2026-data) リポジトリに格納し、各ノートブックからGitHub経由で読み込む。

## ノートブック一覧

### 1. tamachi_restaurant_map.ipynb — 田町駅周辺 ラーメン・牛丼 分布マップ

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ryo-nakajima/undergrad-io-2026-lec1/blob/main/tamachi_restaurant_map.ipynb)

田町駅・三田駅周辺のラーメン屋と牛丼屋の分布を **2016年と2026年で比較** するインタラクティブ地図。

- foliumによるレイヤー切替マップ（ラーメン2016/2026、牛丼2016/2026）
- 田町駅から800m圏内のフィルタリング
- 店舗数の変遷分析（存続・閉店・新規開店）
- 2026年ラーメン店には「2016年からの存続フラグ」と「開店日」を付与

### 2. jirou_price_visualization.ipynb — ラーメン二郎 各店舗の価格可視化

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ryo-nakajima/undergrad-io-2026-lec1/blob/main/jirou_price_visualization.ipynb)

ラーメン二郎の全店舗（45店）のメニュー別価格を可視化。

- 絶対価格ヒートマップ（店舗×メニュー）
- 「小」の価格ランキング棒グラフ
- 総合スコア棒グラフ（メニュー別中央値との乖離）

### 3. gyuudon_price.ipynb — 牛丼チェーン並盛価格の推移

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ryo-nakajima/undergrad-io-2026-lec1/blob/main/gyuudon_price.ipynb)

すき家・吉野家・松屋の牛丼並盛価格の推移（2000〜2026年）を時系列グラフで比較。

- 価格改定イベント単位のステップチャート
- BSE問題による販売休止期間の表示
- 松屋のプレミアム牛めし統一（2021年）のアノテーション

## データリポジトリ

データは [ryo-nakajima/undergrad-io-2026-data](https://github.com/ryo-nakajima/undergrad-io-2026-data) に格納：

```
undergrad-io-2026-data/
├── data/
│   ├── ramen_2016.csv                  # 2016年ラーメン店（27店）
│   ├── ramen_2026.csv                  # 2026年ラーメン店（30店）
│   ├── gyudon_2016.csv                 # 2016年牛丼店（5店）
│   ├── gyudon_2026.csv                 # 2026年牛丼店（6店）
│   └── jirou_prices_tidy_long.csv      # ラーメン二郎価格データ
└── gyudon_chain_standard_bowl_price_changes_2000_2026.csv  # 牛丼チェーン価格改定履歴
```

各ノートブックはローカル実行時は `data/` フォルダから、Google Colab実行時はGitHub raw URLから自動的にデータを読み込む。

## 処理スクリプト（ローカル用）

田町レストランマップのデータ作成に使用したスクリプト群：

| スクリプト | 機能 |
|-----------|------|
| `extract_map_regions.py` | PDFから地図画像を切り出し |
| `detect_pins.py` | OpenCV (HSV色空間) で食べログのオレンジピンを自動検出 |
| `georef.py` | 4参照点によるアフィン変換でピクセル座標→緯度経度変換（精度≈15m） |
| `tabelog_scraper.py` | 食べログ一覧・詳細ページのスクレイパー |
| `clean_2026_data.py` | 2026年データのクリーニング（主ジャンルフィルタ、欠落チェーン補完） |
| `build_2016_dataset.py` | 2016年データの最終構築（座標統合・検証） |
| `geocode_2016_from_tabelog.py` | 食べログ閉店ページからの座標取得 |
| `data_2016_ramen.py` | 2016年店舗リスト定義・ジオコーディング |

## 開発の経緯

### 2016年データの復元

2016年のデータは食べログの地図検索画面のスクリーンショット（PDF）しか残っていなかった。以下のパイプラインで店舗座標を復元した：

1. **画像処理によるピン検出**: PDFを300dpiで画像化し、OpenCVのHSV色空間フィルタでオレンジ色のピンマーカーを検出。道路の黄色と区別するため彩度・コンパクト度でフィルタリング
2. **ジオリファレンシング**: 地図上の既知ランドマーク4点（三田駅・田町駅西口・JR田町・三田通り交差前）のピクセル座標と緯度経度の対応から、最小二乗法でアフィン変換を推定
3. **食べログ閉店ページからの補完**: 食べログでは閉店した店舗のページが住所・座標付きで残存している。これを利用して27店舗の座標を復元（PDF記載の全31店中87%）

### 2026年データのスクレイピング

食べログの一覧ページ (`tabelog.com/tokyo/A1314/A131402/rstLst/MC0101/`) から店舗URLを取得し、各詳細ページのHTML内に埋め込まれた `lat`, `lng` を正規表現で抽出。robots.txt上、対象ページはDisallowされていない。

取得後のクリーニングで以下を実施：
- ラーメン: 主ジャンルがラーメン/つけ麺/担々麺でない店舗（中華料理、焼き鳥等）を除外（42→30店）
- 牛丼: ジャンルに「牛丼」を含まない店舗（居酒屋等）を除外（23→3店）+ 欠落チェーン店を個別検索で補完（→6店）

### Colab対応

全ノートブックをローカル/Google Colab両対応に修正：
- ローカル: `data/` フォルダからCSV読み込み
- Colab: `undergrad-io-2026-data` リポジトリのGitHub raw URLから自動ダウンロード
- 日本語フォント: macOS (Hiragino Sans) / Colab (japanize-matplotlib) を自動判定

## 実行日

- 2026年4月6日
- 2016年データ元: 食べログ2016年時点のスクリーンショットPDF
- 2026年データ: 食べログ2026年4月時点のスクレイピング
