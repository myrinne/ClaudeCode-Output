$ErrorActionPreference = 'Continue'
$dir = $PSScriptRoot
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'
Get-ChildItem "$dir\q*.txt" | Sort-Object Name | ForEach-Object {
    $out = Join-Path $dir ($_.BaseName + '.json')
    if ((Test-Path $out) -and ((Get-Item $out).Length -gt 500)) { return }
    "$(Get-Date -Format HH:mm:ss) asking $($_.BaseName)" | Out-File -Append -Encoding utf8 "$dir\log.txt"
    $res = notebooklm ask -n 69c334e1-aacb-4c77-8038-f48e588a0468 --prompt-file $_.FullName --json --timeout 600
    $res | Out-File -Encoding utf8 $out
    "$(Get-Date -Format HH:mm:ss) done $($_.BaseName) bytes=$((Get-Item $out).Length)" | Out-File -Append -Encoding utf8 "$dir\log.txt"
}
"ALL DONE" | Out-File -Append -Encoding utf8 "$dir\log.txt"
