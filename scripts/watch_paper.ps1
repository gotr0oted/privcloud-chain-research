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
$lastPushAttempt = [DateTime]::UtcNow

while ($true) {
    Start-Sleep -Seconds $PollSeconds
    $current = (Get-Item -LiteralPath $paper).LastWriteTimeUtc
    if ($current -ne $lastObserved) {
        $lastObserved = $current
        $changedAt = [DateTime]::UtcNow
    }
    if ($null -ne $changedAt -and ([DateTime]::UtcNow - $changedAt).TotalSeconds -ge $QuietSeconds) {
        $changedAt = $null
        Invoke-Git @('add', '--', 'PrivCloud-Chain_IEEE_Research_Paper.docx') | Out-Null
        $diff = & git -C $repo diff --cached --quiet -- 'PrivCloud-Chain_IEEE_Research_Paper.docx'
        if ($LASTEXITCODE -eq 1) {
            $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'
            Invoke-Git @('commit', '-m', "Update research paper ($stamp)") | Out-Null
        } elseif ($LASTEXITCODE -ne 0) {
            Write-Warning 'Could not inspect staged paper changes; will retry.'
        }
    }

    if (([DateTime]::UtcNow - $lastPushAttempt).TotalSeconds -ge 30) {
        $lastPushAttempt = [DateTime]::UtcNow
        $ahead = & git -C $repo rev-list --count '@{u}..HEAD' 2>$null
        if ($LASTEXITCODE -eq 0 -and [int]$ahead -gt 0) {
            try { Invoke-Git @('push', '-u', 'origin', 'HEAD') | Write-Host }
            catch { Write-Warning "Push failed; local commit retained and will be retried: $_" }
        }
    }
}
