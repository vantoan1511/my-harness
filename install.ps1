# my-harness installer for Windows PowerShell
param (
    [string]$Command = "init",
    [string]$Scope = "",
    [string]$Target = ".",
    [string]$Pack = "",
    [switch]$DryRun
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$harnessPy = Join-Path $scriptDir "harness.py"

if (-not (Test-Path $harnessPy)) {
    Write-Error "harness.py not found at $harnessPy"
    exit 1
}

if ($Command.ToLower() -eq "fix") {
    $argsList = @($harnessPy, "fix", $Target)
    if ($DryRun) {
        $argsList += "--dry-run"
    }
    python @argsList
    exit $LASTEXITCODE
}

# Prompt user interactively if scope is not provided and running interactively
if ([string]::IsNullOrWhiteSpace($Scope)) {
    $isInteractive = [Environment]::UserInteractive -and (-not [Console]::IsInputRedirected)
    if ($isInteractive) {
        Write-Host "`n========================================================" -ForegroundColor Cyan
        Write-Host " my-harness Installer - Choose Installation Scope" -ForegroundColor Cyan
        Write-Host "========================================================" -ForegroundColor Cyan
        Write-Host "  [1] Project (Default) - Install .agents in project directory ($Target)"
        Write-Host "  [2] Global            - Install .agents in ~/.agents and register 'harness' CLI"
        Write-Host "  [3] Fix               - Repair project .agents and deduplicate global items"
        Write-Host "--------------------------------------------------------"
        $choice = Read-Host "Select option [1/2/3] (default: 1)"
        if ($choice -eq "2" -or $choice -eq "global") {
            $Scope = "global"
        } elseif ($choice -eq "3" -or $choice -eq "fix") {
            $argsList = @($harnessPy, "fix", $Target)
            python @argsList
            exit $LASTEXITCODE
        } else {
            $Scope = "project"
        }
    } else {
        $Scope = "project"
    }
}

if ($Scope.ToLower() -eq "global") {
    $argsList = @($harnessPy, "init", "--scope", "global")
} else {
    $argsList = @($harnessPy, "init", $Target, "--scope", "project")
}

if ($Pack -ne "") {
    $argsList += @("--pack", $Pack)
}

python @argsList

