#!/bin/bash

echo "Starting Redis..."
sudo systemctl start redis

echo "Starting FastAPI..."
source venv/bin/activate
uvicorn app.main:app --reload
