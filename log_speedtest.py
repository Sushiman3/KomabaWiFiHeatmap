import speedtest
import csv
from datetime import datetime
import os
import subprocess

def get_wifi_rssi():
    """Gets RSSI in dBm on Windows using netsh"""
    try:
        output = subprocess.check_output("netsh wlan show interfaces", shell=True).decode()
        for line in output.splitlines():
            if "Signal" in line:
                percent = int(line.split(":")[1].strip().replace("%", ""))
                # Approximate dBm conversion
                rssi = (percent / 2) - 100
                return round(rssi, 2)
    except Exception as e:
        print("Error getting RSSI:", e)
    return None

def get_gps_location():
    """Use GPSD, serial module, or stub; here we mock it for simplicity"""
    # TODO: Replace this with real GPS serial input if using GPS module
    # For now, return None or dummy lat/lon
    return (35.662, 139.683)  # Komaba Campus dummy coordinates

# Manual note input
note = input("Enter location note (e.g. 'Building A, Room 101'): ")

# Run speed test
print("Running speedtest...")
s = speedtest.Speedtest()
s.get_best_server()
download = s.download() / 1e6
upload = s.upload() / 1e6
ping = s.results.ping

# Get other data
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
rssi = get_wifi_rssi()
lat, lon = get_gps_location()

# CSV log
csv_file = 'wifi_survey_log.csv'
file_exists = os.path.isfile(csv_file)

with open(csv_file, mode='a', newline='') as file:
    writer = csv.writer(file)
    if not file_exists:
        writer.writerow([
            "Timestamp", "Download_Mbps", "Upload_Mbps", "Ping_ms",
            "RSSI_dBm", "Latitude", "Longitude", "Note"
        ])
    writer.writerow([
        timestamp, f"{download:.2f}", f"{upload:.2f}", f"{ping:.2f}",
        rssi if rssi is not None else "", lat, lon, note
    ])

print(f"Logged: {note} @ {timestamp}")
