param(
    [int]$PollSeconds = 3,
    [int]$QuietSeconds = 8
)

$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$paper = Join-Path $repo 'PrivCloud-Chain_IEEE_Research_Paper.docx'

function Invoke-Git([string[]]$GitArgs) {
    $output = & git -C $repo @GitArgs 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') failed: $output"
    }
    return ($output -join "`n")
}

if (-not (Test-Path -LiteralPath $paper)) { throw "Paper not found: $paper" }
Write-Host "Watching $paper for saved changes. Press Ctrl+C to stop."
$lastObserved = (Get-Item -LiteralPath $paper).LastWriteTimeUtc
$changedAt = $null

while ($true) {
    Start-Sleep -Seconds $PollSeconds
    $current = (Get-Item -LiteralPath $paper).LastWriteTimeUtc
    if ($current -ne $lastObserved) {
        $lastObserved = $current
        $changedAt = [DateTime]::UtcNow
    }
    if ($null -eq $changedAt -or ([DateTime]::UtcNow - $changedAt).TotalSeconds -lt $QuietSeconds) { continue }
    $changedAt = $null

    $remote = Invoke-Git @('remote', 'get-url', 'origin')
    if ([string]::IsNullOrWhiteSpace($remote)) { throw 'Git remote origin is empty.' }
    Invoke-Git @('add', '--', 'PrivCloud-Chain_IEEE_Research_Paper.docx') | Out-Null
    $diff = & git -C $repo diff --cached --quiet -- 'PrivCloud-Chain_IEEE_Research_Paper.docx'
    if ($LASTEXITCODE -eq 0) { continue }
    if ($LASTEXITCODE -ne 1) { throw 'Could not inspect staged paper changes.' }

    $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'
    Invoke-Git @('commit', '-m', "Update research paper ($stamp)") | Out-Null
    Invoke-Git @('push', '-u', 'origin', 'HEAD') | Write-Host
}
