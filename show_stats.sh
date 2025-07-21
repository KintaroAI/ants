#!/bin/bash

# Show statistics visualization for ant colony simulation
# This script runs the show_stats.py script to visualize food preferences over time

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Ant Colony Statistics Visualizer${NC}"
echo "=================================="

# Check if stats.txt exists
if [ ! -f "stats.txt" ]; then
    echo -e "${RED}Error: stats.txt not found!${NC}"
    echo -e "${YELLOW}Please run the simulation with statistics first:${NC}"
    echo "  make run-stats"
    echo "  or"
    echo "  python src/colony.py --stats"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    make venv
    make install
fi

# Run the visualization
echo -e "${GREEN}Running statistics visualization...${NC}"
venv/bin/python src/show_stats.py "$@"
echo -e "${GREEN}Visualization complete!${NC}" 