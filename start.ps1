$ErrorActionPreference = "Stop"
Write-Host "Starting GuardSQL Enterprise..." -ForegroundColor Cyan
$env:NO_PROXY = "127.0.0.1,localhost"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
Start-Sleep -Seconds 3
python -m streamlit run frontend/streamlit_app.py --server.port 8501