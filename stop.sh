#!/bin/bash

echo "Stopping FastAPI..."
pkill -f "uvicorn app.main:app"

echo "Stopping Redis..."
sudo systemctl stop redis

echo "Stopping PostgreSQL..."
sudo systemctl stop postgresql

echo "Done."
