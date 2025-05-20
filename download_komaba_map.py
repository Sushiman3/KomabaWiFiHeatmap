# This script downloads a static OSM map of Komaba Campus and saves it as 'komabamap.png'.
# Run this script once before using the GUI logger.
from staticmap import StaticMap, CircleMarker

# Komaba Campus center coordinates
komaba_lat, komaba_lon = 35.6608, 139.6857

# Create a static map
m = StaticMap(800, 600, url_template='http://a.tile.openstreetmap.org/{z}/{x}/{y}.png')
image = m.render(zoom=17, center=(komaba_lon, komaba_lat))
image.save('komabamap.png')

print("Map image 'komabamap.png' saved. You can now use it in your GUI.")
