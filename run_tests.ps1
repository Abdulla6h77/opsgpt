$API_KEY="2f9a8c7e1b6d4f3a9c0e7b2d6a1f8c4"

Write-Host "Uploading logs..."
curl.exe -X POST http://127.0.0.1:8000/logs/upload `
  -H "X-API-Key: $API_KEY" `
  -F "file=@demo_data/sample_logs.log"

Write-Host ""
Write-Host "Running anomaly detection..."

curl.exe -X POST http://127.0.0.1:8000/anomalies/detect `
  -H "X-API-Key: $API_KEY" `
  -F "file=@demo_data/sample_logs.log"

Write-Host ""
Write-Host "Tests completed."