# Import required libraries
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import csv
from datetime import datetime
import os
import subprocess
import threading
import re

# Map image and CSV log file names
MAP_IMAGE = './data/komabamap.png'  # Place your map image in the same folder
CSV_FILE = 'wifi_survey_log.csv'

# Function to get WiFi RSSI (signal strength) in dBm
def get_wifi_rssi():
    try:
        # Run netsh command to get WiFi info
        output_bytes = subprocess.check_output(["netsh", "wlan", "show", "interfaces"])
        encodings = ['utf-8', 'shift-jis', 'cp932']
        output = None
        # Try decoding with different encodings
        for encoding in encodings:
            try:
                output = output_bytes.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        if output is None:
            print("Error: Could not decode netsh output with any known encoding")
            return None
        # Parse output to find signal strength
        for line in output.splitlines():
            if any(keyword in line for keyword in ["シグナル", "Signal", "信号"]):
                digits = ''.join(filter(str.isdigit, line))
                if not digits:
                    continue
                signal_percent = int(digits)
                # Convert percentage to dBm
                rssi = ((signal_percent / 100.0) * 50) - 100
                return round(rssi, 2)
    except Exception as e:
        print(f"Error getting RSSI: {e}")
    return None

# Function to run a speed test and return download, upload, and ping
def run_speedtest():
    """Run speedtest-cli via subprocess and parse the results."""
    import subprocess
    import re
    import sys
    try:
        # Use python -m speedtest for Windows compatibility
        result = subprocess.run([sys.executable, "-m", "speedtest", "--simple"], capture_output=True, text=True, check=True)
        output = result.stdout
        ping = download = upload = None
        for line in output.splitlines():
            if line.startswith("Ping:"):
                ping = float(re.search(r"([\d.]+)", line).group(1))
            elif line.startswith("Download:"):
                download = float(re.search(r"([\d.]+)", line).group(1))
            elif line.startswith("Upload:"):
                upload = float(re.search(r"([\d.]+)", line).group(1))
        if None in (ping, download, upload):
            raise ValueError("Could not parse speedtest-cli output: " + output)
        return download, upload, ping
    except subprocess.CalledProcessError as e:
        print(f"Error running speedtest-cli: {e}\nOutput: {e.output}\nStderr: {e.stderr}")
        return 0.0, 0.0, 0.0
    except Exception as e:
        print(f"Error running speedtest-cli: {e}")
        return 0.0, 0.0, 0.0

# Function to log data to CSV file
def log_to_csv(timestamp, download, upload, ping, rssi, lat, lon, note):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        # Write header if file does not exist
        if not file_exists:
            writer.writerow([
                "Timestamp", "Download_Mbps", "Upload_Mbps", "Ping_ms",
                "RSSI_dBm", "Latitude", "Longitude", "Note"
            ])
        # Write measurement data
        writer.writerow([
            timestamp, f"{download:.2f}", f"{upload:.2f}", f"{ping:.2f}",
            rssi if rssi is not None else "", lat, lon, note
        ])

# Main GUI class for map selection and logging
class MapSelector(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WiFi Speedtest Logger - Map Selector (Komaba Campus)")
        self.map_img = Image.open(MAP_IMAGE)
        self.tk_img = ImageTk.PhotoImage(self.map_img)
        self.canvas = tk.Canvas(self, width=self.map_img.width, height=self.map_img.height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_img)
        self.canvas.bind("<Button-1>", self.on_click)
        self.selected_coords = None
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        messagebox.showinfo("Instructions", "Click on the map to select a location.")

    # Handle map click event
    def on_click(self, event):
        self.selected_coords = (event.x, event.y)
        self.canvas.create_oval(event.x-5, event.y-5, event.x+5, event.y+5, outline='red', width=2)
        self.after(500, self.collect_note_and_log)

    # Collect note, run tests, and log data
    def collect_note_and_log(self):
        note = simpledialog.askstring("Location Note", "Enter location note (e.g. 'Building A, Room 101'):")
        if note is None:
            return
        lat, lon = self.selected_coords
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rssi = get_wifi_rssi()
        # Disable map clicks during testing
        self.canvas.unbind("<Button-1>")
        # Create a label for the animation
        self.status_label = tk.Label(self, text="Running test", font=("Arial", 14))
        self.status_label.pack(pady=10)
        self.running = True
        self.period_count = 0
        self.animate_caption()
        # Run the speedtest in a separate thread to avoid freezing
        threading.Thread(target=self.run_test_and_log, args=(timestamp, rssi, lat, lon, note), daemon=True).start()

    def animate_caption(self):
        if not hasattr(self, 'running') or not self.running:
            return
        periods = '.' * (self.period_count % 4)
        self.status_label.config(text=f"Running test{periods}")
        self.period_count += 1
        self.after(500, self.animate_caption)

    def run_test_and_log(self, timestamp, rssi, lat, lon, note):
        download, upload, ping = run_speedtest()
        log_to_csv(timestamp, download, upload, ping, rssi, lat, lon, note)
        self.running = False
        self.status_label.destroy()
        messagebox.showinfo("Logged", f"Logged: {note} @ {timestamp}\nCoords: {lat}, {lon}")
        self.destroy()

    # Handle window close event
    def on_close(self):
        self.destroy()

# Main entry point
if __name__ == "__main__":
    if not os.path.isfile(MAP_IMAGE):
        print(f"Map image '{MAP_IMAGE}' not found. Please add it to the folder.")
    else:
        app = MapSelector()
        app.mainloop()
