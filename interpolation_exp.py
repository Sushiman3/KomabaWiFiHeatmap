#Generate Heatmap with Exponential
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image

windows1 = pd.read_csv('./data/log_RH.csv')
windows2 = pd.read_csv('./data/log_KH.csv')

# Connect Data
data = pd.concat([windows1, windows2], axis=0, ignore_index=True)

def estimate_strength(x, y, data, sigma=1.0):
    ap_x = data['Latitude'].values
    ap_y = data['Longitude'].values
    ap_strength = data['RSSI_dBm'].values
    # Calculate distances from point (x,y) to all access points
    # Reshape arrays for broadcasting
    x_reshaped = np.array(x).reshape(-1, 1)
    y_reshaped = np.array(y).reshape(-1, 1)
    
    # Calculate distances using broadcasting
    distances = np.sqrt((x_reshaped - ap_x)**2 + (y_reshaped - ap_y)**2)

    # Calculate strength using Gaussian function
    ap = ap_strength * np.exp(-distances**2 / (2 * sigma**2))

    #Return the maximum strength at each point
    return np.max(ap, axis=0)


# Plot on map
MAP_IMAGE = Image.open('./data/komabamap.png')

width, height = MAP_IMAGE.size
x = np.linspace(0, width, 100)
y = np.linspace(0, height, 100)
X, Y = np.meshgrid(x, y)
Z = estimate_strength(X, Y, data)

plt.figure(figsize=(10, 10))
plt.imshow(Z, extent=(0, width, 0, height), origin='lower', cmap='hot', alpha=0.5)