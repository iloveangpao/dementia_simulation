#!/bin/bash

# Dementia Simulation Platform Startup Script

echo "Starting Dementia Simulation Platform..."

# Start FastAPI backend
echo "Starting FastAPI backend on port 8000..."
cd /home/runner/work/dementia_simulation/dementia_simulation
python backend/api.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start Streamlit frontend
echo "Starting Streamlit frontend on port 8501..."
streamlit run frontend/app.py --server.headless true --server.port 8501 &
FRONTEND_PID=$!

echo "Platform started successfully!"
echo "FastAPI backend: http://localhost:8000"
echo "Streamlit frontend: http://localhost:8501"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop the platform, kill these processes:"
echo "kill $BACKEND_PID $FRONTEND_PID"