#!/bin/bash

# Get the absolute path of the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 1. Activate Virtual Environment
echo "🔌 Activating virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"

# 2. Start Streamlit (Backend)
echo "🚀 Starting Job Hunter AI Backend (Streamlit)..."
# Run in background, suppress standard output but show errors
streamlit run "$SCRIPT_DIR/app.py" --server.port 8501 --server.headless=true > /dev/null 2>&1 &
STREAMLIT_PID=$!

# 3. Start Zocially (Frontend)
echo "🌐 Starting Zocially Website (Port 8080)..."
cd "$SCRIPT_DIR/Zocially"
python3 -m http.server 8080 &
ZOCIALLY_PID=$!

echo "✅ All services started!"
echo "-----------------------------------------------------"
echo "👉 Main Website:      http://localhost:8080"
echo "👉 Job Hunter Tool:   http://localhost:8080/job-hunter.html"
echo "-----------------------------------------------------"
echo "Press CTRL+C to stop all servers."

# 4. Cleanup Function
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $STREAMLIT_PID 2>/dev/null
    kill $ZOCIALLY_PID 2>/dev/null
    echo "Bye!"
    exit
}

# Trap CTRL+C (SIGINT) and call cleanup
trap cleanup SIGINT

# Keep script running to maintain processes
wait
