#!/usr/bin/env python3
import os
import json
import pandas as pd
from glob import glob

# Define base directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KISMET_PROC_DIR = os.path.join(BASE_DIR, "Processing", "Kismet")
CONVERTED_DIR = os.path.join(BASE_DIR, "Processing", "Converted")

# Ensure output directory exists
os.makedirs(CONVERTED_DIR, exist_ok=True)

# Recursively find all _processed.json files in subdirectories
json_files = glob(os.path.join(KISMET_PROC_DIR, "**", "*_processed.json"), recursive=True)

if not json_files:
    print(f"Error: No processed JSON files found in {KISMET_PROC_DIR}. Exiting.")
    exit(1)

# Ask user if they want to overwrite existing CSVs
overwrite_choice = input("Overwrite existing CSV files? (y/n): ").strip().lower()
overwrite = overwrite_choice == "y"

# Process each JSON file
for json_file in json_files:
    # Determine output CSV filename
    base_name = os.path.basename(json_file).replace("_processed.json", "_converted.csv")
    output_csv_file = os.path.join(CONVERTED_DIR, base_name)

    # Check if CSV already exists
    if os.path.exists(output_csv_file) and not overwrite:
        print(f"Skipping existing file: {output_csv_file}")
        continue

    print(f"Processing: {json_file}")

    # Load JSON data
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {json_file}: {e}")
        continue

    # Extract relevant fields from each `dot11.device` entry
    records = []
    for entry in data:
        mac = entry.get("kismet.device.base.macaddr", "")
        ssid = entry.get("dot11.device", {}).get("dot11.device.last_beaconed_ssid_record", {}).get("dot11.advertisedssid.ssid", "")
        manufacturer = entry.get("kismet.device.base.manuf", "")
        probed_ssid = entry.get("dot11.device", {}).get("dot11.device.probed_ssid_map", [{}])[0].get("dot11.probedssid.ssid", "")

        # Extract timestamp of detection
        first_time = entry.get("kismet.device.base.first_time", None)
        last_time = entry.get("kismet.device.base.last_time", None)

        # Extract GPS location (checking multiple sources)
        location_data = entry.get("kismet.device.base.location", {}).get("kismet.common.location.avg_loc", {})
        lat = location_data.get("kismet.common.location.geopoint", [None, None])[1]  # Latitude
        lon = location_data.get("kismet.common.location.geopoint", [None, None])[0]  # Longitude
        loc_time = location_data.get("kismet.common.location.time_sec", None)  # Time of location fix

        # Extract RSSI signal strength
        rssi = entry.get("kismet.device.base.signal", {}).get("kismet.common.signal.last_signal", "")

        # Append each detection as a separate row
        records.append([mac, ssid, first_time, last_time, loc_time, rssi, lat, lon, manufacturer, probed_ssid])

    # Convert to DataFrame
    df = pd.DataFrame(records, columns=[
        "MAC", "SSID", "First Time", "Last Time", "Location Time", "RSSI", "Latitude", "Longitude", "Manufacturer", "Probed SSID"
    ])

    # Save to CSV (each detection remains separate)
    df.to_csv(output_csv_file, index=False)
    print(f"Converted {json_file} -> {output_csv_file}")

print("All JSON files have been successfully processed.")
