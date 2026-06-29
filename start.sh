#!/bin/bash
echo "============================================"
echo "  Smart Voice Analyzer - Starting Server"
echo "============================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt -q

# Open browser
sleep 2 && open "http://localhost:8000" 2>/dev/null || \
           xdg-open "http://localhost:8000" 2>/dev/null &

# Start server
echo ""
echo "Starting server at http://localhost:8000"
echo "Press Ctrl+C to stop."
echo ""
python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
