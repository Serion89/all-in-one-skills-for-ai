# Sync skills to local environments (Claude Code, Antigravity/Gemini)
param(
    [ValidateSet("claude", "gemini", "all")]
    [string]$Target = "all"
)

$repoRoot = $PSScriptRoot
$skillsSource = Join-Path $repoRoot "skills"

if (-not (Test-Path $skillsSource)) {
    Write-Error "Skills directory not found at $skillsSource"
    exit 1
}

$claudeDir = Join-Path $HOME ".claude\skills"
$geminiDir = Join-Path $HOME ".gemini\config\skills"

if ($Target -eq "claude" -or $Target -eq "all") {
    Write-Host "Syncing to Claude Code: $claudeDir..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Force -Path $claudeDir | Out-Null
    Copy-Item -Path "$skillsSource\*" -Destination $claudeDir -Recurse -Force
    Write-Host "✓ Synced to Claude Code!" -ForegroundColor Green
}

if ($Target -eq "gemini" -or $Target -eq "all") {
    Write-Host "Syncing to Antigravity/Gemini: $geminiDir..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Force -Path $geminiDir | Out-Null
    Copy-Item -Path "$skillsSource\*" -Destination $geminiDir -Recurse -Force
    Write-Host "✓ Synced to Antigravity/Gemini!" -ForegroundColor Green
}

$count = (Get-ChildItem -Path $skillsSource -Directory).Count
Write-Host "Done! $count skills successfully synced." -ForegroundColor Green
