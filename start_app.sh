#!/bin/bash

echo "Starting Flask backend server..."
cd /Users/sumith/Documents/GitHub/Safety-align
python3 app_flask.py &
FLASK_PID=$!

echo "Flask server started with PID: $FLASK_PID"
echo "Waiting for Flask server to initialize..."
sleep 3

echo "Starting React development server..."
cd temp-react-app
DANGEROUSLY_DISABLE_HOST_CHECK=true npm start &
REACT_PID=$!

echo "React server started with PID: $REACT_PID"
echo ""
echo "Both servers are starting..."
echo "Flask backend: http://localhost:8000"
echo "React frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo "Stopping servers..."
    kill $FLASK_PID 2>/dev/null
    kill $REACT_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
