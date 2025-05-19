import speedtest
import csv
from datetime import datetime
import os
import subprocess

def get_wifi_rssi():
    """Gets RSSI in dBm on Windows using netsh"""
    try:
        # Get the output as bytes first
        output_bytes = subprocess.check_output(["netsh", "wlan", "show", "interfaces"])
        
        # Try different encodings
        encodings = ['utf-8', 'shift-jis', 'cp932']
        output = None
        
        for encoding in encodings:
            try:
                output = output_bytes.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
                
        if output is None:
            print("Error: Could not decode netsh output with any known encoding")
            return None
            
        print("Debug - Full netsh output:")
        print(output)
        
        # Parse the output line by line
        for line in output.splitlines():
            # 日本語環境では "シグナル" を探す
            if any(keyword in line for keyword in ["シグナル", "Signal", "信号"]):
                print("Debug - Found signal line:", line)
                # Extract the percentage value - get all digits
                digits = ''.join(filter(str.isdigit, line))
                if not digits:
                    continue
                    
                signal_percent = int(digits)
                print("Debug - Signal percentage:", signal_percent)
                
                # Convert percentage to dBm
                # Common conversion formula: 
                # -100 dBm = 0% and -50 dBm = 100%
                rssi = ((signal_percent / 100.0) * 50) - 100
                
                return round(rssi, 2)
                
        print("Debug - No signal strength line found in output")
    except subprocess.CalledProcessError as e:
        print(f"Error executing netsh command: {e}")
        print(f"Error output: {e.output if hasattr(e, 'output') else 'No output'}")
    except Exception as e:
        print(f"Error getting RSSI: {e}")
        import traceback
        print(traceback.format_exc())
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
