$ErrorActionPreference = "Stop"

Invoke-RestMethod http://localhost:8000/health/ready
Invoke-RestMethod -Method Post -Uri http://localhost:8000/v1/generate `
  -ContentType "application/json" `
  -Body '{"prompt":"Explain AI observability in one sentence.","max_tokens":64}'
Invoke-WebRequest http://localhost:8000/metrics -UseBasicParsing |
  Select-Object -ExpandProperty Content |
  Select-String "llm_inference_requests_total"
