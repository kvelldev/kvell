#!/bin/bash
echo "Testing health endpoints..."
echo "Note: MongoDB must be running on localhost:27017 for these tests to work"
echo ""

# Start the server in background
echo "Starting FastAPI server..."
cd /home/syuma/ws/kvell/apps/api
uv run fastapi dev src/app/main.py --port 8000 > server.log 2>&1 &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

# Test root endpoint
echo ""
echo "1. Testing root endpoint (GET /):"
curl -s http://localhost:8000/ | jq '.' || echo "Failed"

# Test health echo endpoint
echo ""
echo "2. Testing health echo endpoint (POST /api/health/echo):"
curl -s -X POST http://localhost:8000/api/health/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from health check!"}' | jq '.' || echo "Failed"

# Test health latest endpoint
echo ""
echo "3. Testing health latest endpoint (GET /api/health/latest):"
curl -s http://localhost:8000/api/health/latest | jq '.' || echo "Failed"

# Cleanup
echo ""
echo "Stopping server..."
kill $SERVER_PID
wait $SERVER_PID 2>/dev/null

echo ""
echo "Test complete. Check server.log for details."
