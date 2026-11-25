# One-click installer for the WhatsApp sales agent (Windows 10/11).
# Run it by double-clicking install_windows.bat in the same folder.

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

function Step($text) { Write-Host ""; Write-Host "==> $text" -ForegroundColor Cyan }
function Fail($text) {
    Write-Host ""; Write-Host "ERROR: $text" -ForegroundColor Red
    Read-Host "Press Enter to close"; exit 1
}
function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}
function Has-Command($name) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    # The "python" in WindowsApps is only a shortcut to the Microsoft Store, not real Python.
    return ($cmd -ne $null) -and ($cmd.Source -notlike "*WindowsApps*")
}
function Install-WithWinget($id, $label) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Fail "$label is not installed and 'winget' is missing. Install $label manually, then run this installer again."
    }
    Write-Host "Installing $label (this can take a few minutes)..."
    winget install -e --id $id --accept-package-agreements --accept-source-agreements --silent
    Refresh-Path
}

Write-Host "=============================================" -ForegroundColor Green
Write-Host "   WhatsApp Sales Agent - installer" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# 1. Python
Step "Checking Python"
if (-not (Has-Command "python")) { Install-WithWinget "Python.Python.3.12" "Python" }
if (-not (Has-Command "python")) { Fail "Python was installed but Windows can't find it yet. Restart the computer and run this installer again." }
python --version

# 2. Node.js
Step "Checking Node.js"
if (-not (Has-Command "node")) { Install-WithWinget "OpenJS.NodeJS.LTS" "Node.js" }
if (-not (Has-Command "node")) { Fail "Node.js was installed but Windows can't find it yet. Restart the computer and run this installer again." }
node --version

# 3. Python libraries
Step "Installing Python libraries"
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { Fail "Installing Python libraries failed (see the messages above)." }

# 4. WhatsApp Web bridge (also downloads its own Chrome)
Step "Installing the WhatsApp Web connector (downloads a browser, can take a few minutes)"
Push-Location bridge
npm install --no-audit --no-fund
$npmCode = $LASTEXITCODE
Pop-Location
if ($npmCode -ne 0) { Fail "npm install failed (see the messages above)." }

# 5. Settings (.env)
Step "Settings"
if (-not (Test-Path ".env")) {
    $key = ""
    while (-not $key.StartsWith("sk-ant-")) {
        $key = (Read-Host "Paste your Claude API key (starts with sk-ant-, get it from console.anthropic.com)").Trim()
    }
    $cc = (Read-Host "Country code for numbers in your list without a code (Egypt 20, Sudan 249, Saudi 966, UAE 971) [20]").Trim()
    if (-not $cc) { $cc = "20" }
    $secret = -join ((48..57) + (97..122) | Get-Random -Count 24 | ForEach-Object { [char]$_ })
    $content = Get-Content ".env.example" -Raw -Encoding UTF8
    $content = $content -replace "(?m)^ANTHROPIC_API_KEY=.*$", "ANTHROPIC_API_KEY=$key"
    $content = $content -replace "(?m)^DEFAULT_COUNTRY_CODE=.*$", "DEFAULT_COUNTRY_CODE=$cc"
    $content = $content -replace "(?m)^BRIDGE_SECRET=.*$", "BRIDGE_SECRET=$secret"
    [IO.File]::WriteAllText((Join-Path $PSScriptRoot ".env"), $content, (New-Object Text.UTF8Encoding $false))
    Write-Host "Saved settings to .env"
} else {
    Write-Host ".env already exists - keeping your settings."
}

# 6. Desktop shortcut
Step "Creating a desktop shortcut"
try {
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut((Join-Path ([Environment]::GetFolderPath("Desktop")) "WhatsApp Sales Agent.lnk"))
    $shortcut.TargetPath = Join-Path $PSScriptRoot "start_windows.bat"
    $shortcut.WorkingDirectory = $PSScriptRoot
    $shortcut.Save()
    Write-Host "Shortcut 'WhatsApp Sales Agent' added to your desktop."
} catch {
    Write-Host "Could not create the shortcut (not a problem): $($_.Exception.Message)"
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host " Done! Before sending to real clients, edit business_profile.md" -ForegroundColor Green
Write-Host " (your services, prices, portfolio link)." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
$answer = Read-Host "Start the agent now? (Y/n)"
if ($answer -eq "" -or $answer -match "^[yY]") {
    Start-Process -FilePath (Join-Path $PSScriptRoot "start_windows.bat") -WorkingDirectory $PSScriptRoot
}
