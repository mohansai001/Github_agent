#!/bin/bash

echo "Checking environment variable..."
echo "Azure_Secrets_URL=$Azure_Secrets_URL"

echo "Starting GitHub MCP Server..."
npx @modelcontextprotocol/server-github &

echo "Starting FastAPI..."
uvicorn main:app --host 0.0.0.0 --port 8000
