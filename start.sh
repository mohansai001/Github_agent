#!/bin/bash

echo "===== ENVIRONMENT VARIABLES ====="
env | sort
echo "================================"

sleep 300

echo "Starting GitHub MCP Server..."
npx @modelcontextprotocol/server-github &

echo "Starting FastAPI..."
uvicorn main:app --host 0.0.0.0 --port 8000
