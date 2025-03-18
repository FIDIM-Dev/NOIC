#!/bin/bash
#
# brl.sh (Updated Master Script for BR-Lite)
#
# This script, when run from the FIDIM directory, performs the following:
#   1. Ensures the file directory exists and is accessible.
#   2. Confirms that all required scripts have executable permissions.
#   3. Runs:
#         a. process.sh
#         b. co_traveler_conversion.sh
#         c. co_traveler_analysis.py (with python3)
#         d. installer.sh (if dependencies are missing)
#

# Determine the BR-Lite base directory (parent of FIDIM)
BASE_DIR="$(realpath "$(dirname "$0")/../")"
FIDIM_DIR="$BASE_DIR/FIDIM"
echo "BR-Lite base directory: $BASE_DIR"
echo "FIDIM directory: $FIDIM_DIR"

# Ensure the directory structure exists
if [ ! -d "$FIDIM_DIR" ]; then
    echo "Error: FIDIM directory does not exist. Exiting."
    exit 1
fi

# Check for necessary dependencies before proceeding
if ! command -v python3 &>/dev/null || ! command -v jq &>/dev/null; then
    echo "Missing dependencies detected. Running installer..."
    "$FIDIM_DIR/installer.sh"
fi

# Confirming permissions for all subordinate scripts
echo "Checking and setting executable permissions for all scripts..."
find "$FIDIM_DIR" -type f \( -iname "*.sh" -o -iname "*.py" \) -exec chmod +x {} \;
echo "All script permissions updated."

# List all required scripts
SCRIPTS=(
    "process.sh"
    "conversion.py"
    "analysis.py"
)

# Confirm scripts exist and are executable
for script in "${SCRIPTS[@]}"; do
    if [ -f "$FIDIM_DIR/$script" ]; then
        chmod +x "$FIDIM_DIR/$script"
        echo "Ensured $script is executable."
    else
        echo "Error: $script not found in the FIDIM directory. Exiting."
        exit 1
    fi
done

echo "All required scripts are confirmed to be present and executable."

# Prompt for data analysis
read -p "Have you uploaded your data for analysis? (y/n): " analyze_choice
if [[ ! "$analyze_choice" =~ ^[Yy]$ ]]; then
    echo "Data analysis skipped. Exiting."
    exit 0
fi

# Run processing and analysis steps
echo "Running process.sh..."
"$FIDIM_DIR/process.sh" || { echo "Processing failed. Exiting."; exit 1; }

echo "Converting processed data to CSV..."
"$FIDIM_DIR/conversion.py" || { echo "Conversion failed. Exiting."; exit 1; }

echo "Analyzing Co Traveler data..."
python3 "$FIDIM_DIR/analysis.py" || { echo "Analysis failed. Exiting."; exit 1; }

echo "BR-Lite main tasks complete."
