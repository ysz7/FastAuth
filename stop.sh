#!/bin/bash

echo "Stopping FastAPI..."
pkill -f "uvicorn app.main:app"

echo "Stopping Redis..."
sudo systemctl stop redis

echo "Done."
