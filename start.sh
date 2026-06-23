#!/bin/bash

set -e

echo "===== ENVIRONMENT VARIABLES ====="
env | sort
echo "================================"

echo "Starting GitHub MCP Server..."
npx @modelcontextprotocol/server-github &

echo "Starting FastAPI..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
