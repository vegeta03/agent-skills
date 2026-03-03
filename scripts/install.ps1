param(
    [ValidateSet("cursor", "copilot", "augment", "all")]
    [string]$Target = "all",

    [ValidateSet("auto", "manual", "both")]
    [string]$Invocation = "both",

    [string]$Workspace = ".",
    [string]$Skills = "",
    [string]$Ref = "master",
    [string]$Repo = "vegeta03/agent-skills",

    [switch]$DryRun,
    [switch]$Check,
    [switch]$Force,
    [switch]$Prune
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-Python {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @("py", "-3")
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @("python")
    }
    if (Get-Command python3 -ErrorAction SilentlyContinue) {
        return @("python3")
    }
    throw "Python is required but was not found."
}

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("agent-skills-install-" + [System.Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null

try {
    $archivePath = Join-Path $tempRoot "repo.zip"
    $archiveUrl = "https://github.com/$Repo/archive/$Ref.zip"
    Write-Host "Downloading $archiveUrl"
    Invoke-WebRequest -Uri $archiveUrl -OutFile $archivePath

    Expand-Archive -Path $archivePath -DestinationPath $tempRoot -Force
    $repoDir = Get-ChildItem -Path $tempRoot -Directory | Where-Object { $_.Name -notlike "__*" } | Select-Object -First 1
    if (-not $repoDir) {
        throw "Failed to extract repository archive."
    }

    $syncScript = Join-Path $repoDir.FullName "scripts/sync.py"
    if (-not (Test-Path $syncScript)) {
        throw "sync.py not found in downloaded archive."
    }

    $pythonCmd = Resolve-Python
    $pythonExe = $pythonCmd[0]
    $pythonPrefix = @()
    if ($pythonCmd.Count -gt 1) {
        $pythonPrefix = $pythonCmd[1..($pythonCmd.Count - 1)]
    }

    $args = @()
    $args += $pythonPrefix
    $args += $syncScript
    $args += "--target"; $args += $Target
    $args += "--invocation"; $args += $Invocation
    $args += "--workspace"; $args += $Workspace

    if (-not [string]::IsNullOrWhiteSpace($Skills)) { $args += "--skills"; $args += $Skills }
    if ($DryRun) { $args += "--dry-run" }
    if ($Check) { $args += "--check" }
    if ($Force) { $args += "--force" }
    if ($Prune) { $args += "--prune" }

    & $pythonExe @args
    if ($LASTEXITCODE -ne 0) {
        throw "sync.py failed with exit code $LASTEXITCODE."
    }
}
finally {
    if (Test-Path $tempRoot) {
        Remove-Item -Path $tempRoot -Recurse -Force
    }
}
