$ErrorActionPreference = "Stop"

$url = "http://127.0.0.1:8010/agent/chat"
$body = @{
    message = "你好，请用三句话介绍你能如何帮助我优化简历。"
    history = @()
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method Post -Uri $url -ContentType "application/json" -Body $body
