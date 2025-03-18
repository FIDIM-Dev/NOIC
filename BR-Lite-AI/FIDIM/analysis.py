#!/usr/bin/env python3
import os
import pandas as pd

# Define base directory and subdirectories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # Moves up to BR-Lite
INPUT_DIR = os.path.join(BASE_DIR, "Processing", "Converted")  # Corrected input directory
OUTPUT_DIR = os.path.join(BASE_DIR, "Outputs")  # Destination for analyzed CSVs
WHITELIST_PATH = os.path.join(BASE_DIR, "Whitelist.csv")  # Whitelist file path

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load whitelist if available
whitelisted_macs = set()
whitelisted_ssids = set()

if os.path.exists(WHITELIST_PATH):
    try:
        whitelist_df = pd.read_csv(WHITELIST_PATH, dtype=str)  # Force all columns as strings

        # Extract MAC and SSID columns safely
        if "Wifi MAC Address" in whitelist_df.columns:
            whitelist_df["Wifi MAC Address"] = whitelist_df["Wifi MAC Address"].fillna("").astype(str).str.upper().str.strip()
            whitelisted_macs = set(whitelist_df["Wifi MAC Address"])
        else:
            print("Warning: Whitelist.csv does not contain 'Wifi MAC Address' column. MAC matching skipped.")

        if "Device Name" in whitelist_df.columns:
            whitelist_df["Device Name"] = whitelist_df["Device Name"].fillna("").astype(str).str.upper().str.strip()
            whitelisted_ssids = set(whitelist_df["Device Name"])
        else:
            print("Warning: Whitelist.csv does not contain 'Device Name' column. SSID matching skipped.")

    except Exception as e:
        print(f"Error loading Whitelist.csv: {e}")

else:
    print("Warning: Whitelist.csv not found. CoTraveler tagging will be skipped.")

# Check if the input directory exists
if not os.path.exists(INPUT_DIR):
    print(f"Error: Converted directory not found at {INPUT_DIR}. Exiting.")
    exit(1)

# Get list of all CSV files in the directory
csv_files = [f for f in os.listdir(INPUT_DIR) if f.endswith("_converted.csv")]

if not csv_files:
    print(f"Error: No converted CSV files found in {INPUT_DIR}. Exiting.")
    exit(1)

# Process each CSV file
for csv_file in csv_files:
    input_path = os.path.join(INPUT_DIR, csv_file)
    output_path = os.path.join(OUTPUT_DIR, csv_file.replace("_converted.csv", "_analyzed.csv"))

    print(f"Processing: {csv_file}")

    # Load CSV data
    try:
        df = pd.read_csv(input_path, dtype=str)  # Read all columns as strings to prevent .str errors
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        continue

    # Ensure "Last Time" exists and use it as "Time"
    if "Last Time" in df.columns:
        df["Time"] = pd.to_datetime(df["Last Time"], unit='s', errors='coerce')
    else:
        raise KeyError("No valid timestamp column found in the CSV data!")

    # Convert all timestamps to human-readable format if they exist
    for time_col in ["First Time", "Last Time", "Location Time"]:
        if time_col in df.columns:
            df[time_col + " (Readable)"] = pd.to_datetime(df[time_col], unit='s', errors='coerce')

    # Sorting data based on Time
    df = df.sort_values(by="Time")

    # Time-based feature engineering (if applicable)
    if "Time" in df.columns:
        df["Time Delta"] = df["Time"].diff()

    # **Co-Traveler Analysis - Match by MAC or SSID**
    if "MAC" in df.columns and "SSID" in df.columns:
        df["MAC"] = df["MAC"].fillna("").astype(str).str.upper().str.strip()  # Normalize MAC addresses
        df["SSID"] = df["SSID"].fillna("").astype(str).str.upper().str.strip()  # Normalize SSIDs

        df["CoTraveler"] = df.apply(
            lambda row: "1" if row["MAC"] in whitelisted_macs or row["SSID"] in whitelisted_ssids else "",
            axis=1
        )

    # Save processed file
    df.to_csv(output_path, index=False)
    print(f"Saved analyzed file: {output_path}")

print("Analysis completed successfully.")
