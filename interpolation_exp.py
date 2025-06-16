import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
import sys

# --- 設定項目 ---
# データファイルのパス
DATA_FILES = ['./data/log_RH.csv', './data/log_KH.csv']
# 地図画像のパス
MAP_IMAGE_PATH = './data/komabamap.png'
# ヒートマップの解像度（数値を大きくすると高精細になるが計算時間が増加）
GRID_RESOLUTION = 200

# ★★★ 最も重要なパラメータ ★★★
# 影響範囲の大きさ。データ点間の距離に応じて調整してください。
# まずは100や200など大きめの値で試し、結果を見ながら調整するのがおすすめです。
SIGMA = 50

# --- メイン処理 ---
try:
    map_image = Image.open(MAP_IMAGE_PATH)
except FileNotFoundError:
    print(f"エラー: 地図ファイルが見つかりません: {MAP_IMAGE_PATH}", file=sys.stderr)
    sys.exit(1)

data_frames = []
for file_path in DATA_FILES:
    try:
        data_frames.append(pd.read_csv(file_path))
    except FileNotFoundError:
        print(f"警告: データファイルが見つかりません: {file_path}", file=sys.stderr)
        continue

if not data_frames:
    print("エラー: 読み込むデータがありません。", file=sys.stderr)
    sys.exit(1)

data = pd.concat(data_frames, axis=0, ignore_index=True)

# 緯度経度がピクセル座標として記録されているため、列名を分かりやすいものに変更
# 元の列名が 'Latitude', 'Longitude' の場合
data.rename(columns={'Latitude': 'pixel_x', 'Longitude': 'pixel_y'}, inplace=True)
# もし元の列名が違う場合は、ここを修正してください (例: {'lat': 'pixel_x', 'lon': 'pixel_y'})

map_width, map_height = map_image.size

# --- ヒートマップ計算 ---
def estimate_strength(grid_x, grid_y, data_points, sigma):
    ap_x = data_points['pixel_x'].values
    ap_y = data_points['pixel_y'].values
    ap_strength = data_points['Download_Mbps'].values

    grid_points_x_flat = grid_x.flatten().reshape(-1, 1)
    grid_points_y_flat = grid_y.flatten().reshape(-1, 1)

    distances = np.sqrt((grid_points_x_flat - ap_x)**2 + (grid_points_y_flat - ap_y)**2)
    ap_influence = ap_strength * np.exp(-distances**2 / (2 * sigma**2))
    max_influence = np.max(ap_influence, axis=1)
    return max_influence.reshape(grid_x.shape)

x_coords = np.linspace(0, map_width, GRID_RESOLUTION)
y_coords = np.linspace(0, map_height, GRID_RESOLUTION)
X, Y = np.meshgrid(x_coords, y_coords)

Z = estimate_strength(X, Y, data, sigma=SIGMA)

# --- 描画 ---
plt.figure(figsize=(12, 10))
plt.imshow(map_image, extent=(0, map_width, 0, map_height), origin='lower')
heatmap = plt.imshow(Z, extent=(0, map_width, 0, map_height), origin='lower', cmap='hot', alpha=0.6)
cbar = plt.colorbar(heatmap)
cbar.set_label('Estimated Signal Strength (RSSI)')
plt.scatter(data['pixel_x'], data['pixel_y'], c='blue', s=15, edgecolor='white', label='Data Points')
plt.legend()
plt.title('WiFi Signal Strength Heatmap')
plt.xlabel('X-coordinate (pixels)')
plt.ylabel('Y-coordinate (pixels)')
plt.xlim(0, map_width)
plt.ylim(0, map_height)
plt.gca().invert_yaxis()
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()