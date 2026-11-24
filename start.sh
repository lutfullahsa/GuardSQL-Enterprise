#!/usr/bin/env bash
set -e
echo "Starting GuardSQL Enterprise..."
export NO_PROXY="127.0.0.1,localhost"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
trap "kill $BACKEND_PID 2>/dev/null || true" EXIT
sleep 2
python -m streamlit run frontend/streamlit_app.py --server.port 8501