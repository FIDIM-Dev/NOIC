#!/bin/bash
#
# Updated BR-Lite Source Data Processing Script (process_source.sh)
#
# This script processes Kismet files by converting them only to JSON format.
# The processed files will be named with "_processed.json" appended to the base filename.
#

# Set the BR-Lite base directory as the parent of FIDIM using an absolute path.
BASE_DIR="$(realpath "$(dirname "$0")/../")"
echo "BR-Lite base directory: $BASE_DIR"

# 1. Update permissions for all files in the Input_Data directory
echo "Updating permissions in Input_Data..."
sudo chmod -R u+rw "$BASE_DIR/Input_Data"

# 2. Process Kismet Files (Convert only to JSON)
echo "Processing Kismet files..."
KISMET_SRC_DIR="$BASE_DIR/Input_Data/Kismetdb"
KISMET_PROC_DIR="$BASE_DIR/Processing/Kismet"

if [ -d "$KISMET_SRC_DIR" ]; then
    for kismet_file in "$KISMET_SRC_DIR"/*.kismet; do
        if [ -f "$kismet_file" ]; then
            base=$(basename "$kismet_file" .kismet)
            dest_dir="$KISMET_PROC_DIR/$base"
            mkdir -p "$dest_dir"
            
            output_json="$dest_dir/${base}_processed.json"
            
            echo "Processing Kismet file: $kismet_file"
            
            # Convert to JSON format
            if [ ! -f "$output_json" ]; then
                echo "Converting to JSON: $output_json"
                sudo kismetdb_dump_devices --in "$kismet_file" --out "$output_json"
            else
                echo "Skipping conversion for $kismet_file as $output_json already exists."
            fi

            echo "Finished processing Kismet file: $kismet_file"
        fi
    done
else
    echo "Kismet source directory ($KISMET_SRC_DIR) does not exist. Skipping Kismet processing."
fi

echo "Source data processing complete."
