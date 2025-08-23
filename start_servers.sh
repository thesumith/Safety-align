#!/bin/bash

echo "Starting Flask backend server..."
python3 app_flask.py &
FLASK_PID=$!

echo "Waiting for Flask server to start..."
sleep 3

echo "Starting React development server..."
cd temp-react-app
npm start &
REACT_PID=$!

echo "Servers started!"
echo "Flask server PID: $FLASK_PID"
echo "React server PID: $REACT_PID"
echo ""
echo "Flask server should be running on: http://localhost:8000"
echo "React app should be running on: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
wait
