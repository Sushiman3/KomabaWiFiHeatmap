import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from PIL import Image

# === Parameters ===
ROOT = 'KomabaWiFiHeatmap'
CSV_FILE = 'wifi_survey_log.csv'
MAP_IMAGE_FILE = 'komabamap.png'
VALUE_COLUMN = 'Download_Mbps'  # Change to 'Download_Mbps' or 'Upload_Mbps' as needed
INTERPOLATION_METHOD = 'cubic'  # Options: 'linear', 'cubic', 'nearest'

# === Load data ===
df = pd.read_csv(f"{ROOT}/{CSV_FILE}")

# Drop rows with missing values
df = df.dropna(subset=['Latitude', 'Longitude', VALUE_COLUMN])

# Get coordinates and values
x = df['Latitude'].values  # These are X pixel values from GUI
y = df['Longitude'].values  # These are Y pixel values from GUI
z = df[VALUE_COLUMN].values  # Measured value (e.g., RSSI or speed)

# === Interpolation grid ===
grid_x, grid_y = np.mgrid[0:800:300j, 0:600:300j]  # Match map resolution

# Interpolate
grid_z = griddata((x, y), z, (grid_x, grid_y), method=INTERPOLATION_METHOD)

# === Load background map ===
map_img = Image.open(f"{ROOT}/{MAP_IMAGE_FILE}").convert("RGBA")

# === Plot ===
plt.figure(figsize=(10, 7))
plt.imshow(map_img, extent=(0, 800, 600, 0))  # Note: Y-axis flipped
plt.imshow(grid_z.T, extent=(0, 800, 600, 0), cmap='viridis', alpha=0.6)

# Overlay measurement points
"""
plt.scatter(x, y, c=z, cmap='viridis', edgecolor='white', linewidth=0.5)
"""
cbar = plt.colorbar(label=VALUE_COLUMN)

plt.title(f"{VALUE_COLUMN} Heatmap")
plt.xlabel("X (pixels)")
plt.ylabel("Y (pixels)")
plt.tight_layout()
plt.savefig(f"heatmap_{VALUE_COLUMN}.png", dpi=300)
plt.show()
