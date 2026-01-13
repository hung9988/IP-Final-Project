#!/bin/bash
# Launcher script for the Network Topology Editor

cd "$(dirname "$0")"

# Check for required dependencies
echo "Checking dependencies..."

# Check if matplotlib and networkx are installed
python3 -c "import matplotlib, networkx" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required dependencies..."
    pip3 install matplotlib networkx --user
fi

echo "Starting Network Topology Editor..."
python3 topology_editor.py
