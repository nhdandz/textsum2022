#!/bin/bash
# Script để chạy production server với Gunicorn
echo "Starting Gunicorn production server on port 9980..."
gunicorn --config gunicorn_config.py app_process:app
