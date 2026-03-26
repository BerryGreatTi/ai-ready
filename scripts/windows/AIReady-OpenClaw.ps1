#Requires -Version 5.1
# AIReady - OpenClaw Installer for Windows (PowerShell)
# ======================================================
# Version: 0.1.0

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# i18n string tables
$Strings = @{
    ko = @{
        Welcome          = 'AIReady - OpenClaw 설치 도우미'
        Checking         = '시스템 확인 중...'
        InstallNode      = 'Node.js 설치 중...'
        InstallTool      = 'OpenClaw 설치 중...'
        Verifying        = '설치 확인 중...'
        SelectProvider   = 'AI 제공자를 선택하세요:'
        EnterApiKey      = 'API 키를 입력하세요 (입력이 숨겨집니다):'
        Onboarding       = '온보딩 실행 중...'
        Success          = 'OpenClaw이 성공적으로 설치되었습니다!'
        RunCmd           = '시작하려면: openclaw'
        NewTerm          = '새 터미널을 열어야 할 수 있습니다.'
        Failed           = '설치 실패. 오류를 확인하세요.'
        NodeFound        = 'Node.js 발견됨'
        NodeInstalled    = 'Node.js 설치 완료'
        NodeFail         = 'Node.js 설치 실패'
        OpenclawFound    = 'OpenClaw 발견됨'
        OpenclawInstalled = 'OpenClaw 설치 완료'
        OpenclawFail     = 'OpenClaw 설치 실패'
        NoApiKey         = 'API 키 없음. 온보딩 건너뜀.'
        OnboardOk        = '온보딩 완료'
        OnboardWarn      = '온보딩 오류. openclaw onboard 를 수동 실행하세요.'
        VerifyOk         = '확인 완료'
        VerifyFail       = '확인 실패'
        DoctorOk         = 'openclaw doctor OK'
        DoctorWarn       = 'openclaw doctor 문제 발생'
        GatewayOk        = 'openclaw gateway OK'
        GatewayWarn      = 'openclaw gateway 실행 중 아님'
    }
    en = @{
        Welcome          = 'AIReady - OpenClaw Setup Helper'
        Checking         = 'Checking system...'
        InstallNode      = 'Installing Node.js...'
        InstallTool      = 'Installing OpenClaw...'
        Verifying        = 'Verifying installation...'
        SelectProvider   = 'Select your AI provider:'
        EnterApiKey      = 'Enter your API key (input hidden):'
        Onboarding       = 'Running onboarding...'
        Success          = 'OpenClaw installed successfully!'
        RunCmd           = 'To start: openclaw'
        NewTerm          = 'You may need to open a new terminal.'
        Failed           = 'Installation failed. Check errors above.'
        NodeFound        = 'Node.js found'
        NodeInstalled    = 'Node.js installed'
        NodeFail         = 'Node.js installation failed'
        OpenclawFound    = 'OpenClaw found'
        OpenclawInstalled = 'OpenClaw installed'
        OpenclawFail     = 'OpenClaw installation failed'
        NoApiKey         = 'No API key provided. Skipping onboarding.'
        OnboardOk        = 'Onboarding complete'
        OnboardWarn      = 'Onboarding issues. Run openclaw onboard manually.'
        VerifyOk         = 'Verified'
        VerifyFail       = 'Verification failed'
        DoctorOk         = 'openclaw doctor OK'
        DoctorWarn       = 'openclaw doctor reported issues'
        GatewayOk        = 'openclaw gateway OK'
        GatewayWarn      = 'openclaw gateway not running'
    }
}

function Write-Ok   { param($m) Write-Host "  [OK]   $m" -ForegroundColor Green }
function Write-Fail { param($m) Write-Host "  [FAIL] $m" -ForegroundColor Red }
function Write-Info { param($m) Write-Host "  [..]   $m" -ForegroundColor Cyan }
function Write-Warn { param($m) Write-Host "  [!!]   $m" -ForegroundColor Yellow }

# Language selection
Write-Host ""
Write-Host "  1. Korean (한국어)"
Write-Host "  2. English"
$langChoice = Read-Host "  Select / 선택 (1/2)"

$lang = if ($langChoice -eq '1') { 'ko' } else { 'en' }
$S = $Strings[$lang]

Write-Host ""
Write-Host "  $($S.Welcome)"
Write-Host "  ========================================"

# Step 1: System check
Write-Info $S.Checking
if (-not [System.Environment]::OSVersion.Platform.ToString().Contains('Win')) {
    Write-Fail 'This script is for Windows only'
    exit 1
}
Write-Ok "Windows $([System.Environment]::OSVersion.Version)"

# Step 2: Check/install Node.js
Write-Info 'Checking Node.js...'
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeCmd) {
    Write-Info $S.InstallNode
    $nodeInstaller = Join-Path $env:TEMP 'node-installer.msi'
    try {
        Invoke-WebRequest -Uri 'https://nodejs.org/dist/latest-v20.x/node-v20.18.1-x64.msi' `
            -OutFile $nodeInstaller -UseBasicParsing
        $msiArgs = @('/i', $nodeInstaller, '/quiet', '/norestart')
        $result = Start-Process -FilePath 'msiexec.exe' -ArgumentList $msiArgs -Wait -PassThru
        Remove-Item $nodeInstaller -Force -ErrorAction SilentlyContinue
        if ($result.ExitCode -ne 0) {
            throw "msiexec returned exit code $($result.ExitCode)"
        }
        # Refresh PATH
        $machinePath = [System.Environment]::GetEnvironmentVariable('PATH', 'Machine')
        $userPath = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
        $env:PATH = "$machinePath;$userPath"
        Write-Ok $S.NodeInstalled
    } catch {
        Write-Fail $S.NodeFail
        exit 1
    }
} else {
    $nodeVer = & node --version 2>$null
    Write-Ok "$($S.NodeFound): $nodeVer"
}

# Step 3: Install OpenClaw
Write-Info $S.InstallTool
$openclawCmd = Get-Command openclaw -ErrorAction SilentlyContinue
if (-not $openclawCmd) {
    # Try official installer first
    $openclawInstaller = Join-Path $env:TEMP 'openclaw-install.cmd'
    $installedViaScript = $false
    try {
        Invoke-WebRequest -Uri 'https://openclaw.ai/install.cmd' `
            -OutFile $openclawInstaller -UseBasicParsing -ErrorAction SilentlyContinue
        Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $openclawInstaller -Wait
        Remove-Item $openclawInstaller -Force -ErrorAction SilentlyContinue
        $openclawCmd = Get-Command openclaw -ErrorAction SilentlyContinue
        if ($openclawCmd) {
            $installedViaScript = $true
        }
    } catch {
        $installedViaScript = $false
    }

    if (-not $installedViaScript) {
        # Fallback: npm install
        try {
            $result = Start-Process -FilePath 'npm' -ArgumentList 'install', '-g', 'openclaw@latest' `
                -Wait -PassThru -NoNewWindow
            if ($result.ExitCode -ne 0) {
                throw 'npm install failed'
            }
        } catch {
            Write-Fail $S.OpenclawFail
            exit 1
        }
    }

    $openclawCmd = Get-Command openclaw -ErrorAction SilentlyContinue
    if (-not $openclawCmd) {
        Write-Fail $S.OpenclawFail
        exit 1
    }
    Write-Ok $S.OpenclawInstalled
} else {
    Write-Ok $S.OpenclawFound
}

# Step 4: Provider selection
Write-Host ""
Write-Host "  $($S.SelectProvider)"
Write-Host "  1. OpenAI"
Write-Host "  2. Anthropic"
Write-Host "  3. Google (Gemini)"
Write-Host "  4. Other"
$providerChoice = Read-Host "  Select (1-4)"

$provider = switch ($providerChoice) {
    '1' { 'openai' }
    '2' { 'anthropic' }
    '3' { 'google' }
    default { 'custom' }
}

# Step 5: API key input (hidden)
Write-Host ""
Write-Host "  $($S.EnterApiKey)"
$apiKeySecure = Read-Host "  API Key" -AsSecureString
$apiKeyBstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKeySecure)
$apiKey = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($apiKeyBstr)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($apiKeyBstr)

if ([string]::IsNullOrEmpty($apiKey)) {
    Write-Warn $S.NoApiKey
} else {
    # Step 6: Onboarding
    Write-Info $S.Onboarding
    $env:OPENCLAW_API_KEY = $apiKey
    try {
        $result = Start-Process -FilePath 'openclaw' `
            -ArgumentList 'onboard', '--provider', $provider, '--install-daemon' `
            -Wait -PassThru -NoNewWindow
        if ($result.ExitCode -eq 0) {
            Write-Ok $S.OnboardOk
        } else {
            Write-Warn $S.OnboardWarn
        }
    } catch {
        Write-Warn $S.OnboardWarn
    } finally {
        $env:OPENCLAW_API_KEY = ''
    }
}

# Step 7: Verify
Write-Info $S.Verifying
$finalCheck = Get-Command openclaw -ErrorAction SilentlyContinue
if ($finalCheck) {
    Write-Ok $S.VerifyOk
} else {
    Write-Fail $S.VerifyFail
    exit 1
}

try {
    $result = Start-Process -FilePath 'openclaw' -ArgumentList 'doctor' -Wait -PassThru -NoNewWindow
    if ($result.ExitCode -eq 0) { Write-Ok $S.DoctorOk } else { Write-Warn $S.DoctorWarn }
} catch { Write-Warn $S.DoctorWarn }

try {
    $result = Start-Process -FilePath 'openclaw' -ArgumentList 'gateway', 'status' -Wait -PassThru -NoNewWindow
    if ($result.ExitCode -eq 0) { Write-Ok $S.GatewayOk } else { Write-Warn $S.GatewayWarn }
} catch { Write-Warn $S.GatewayWarn }

# Step 8: Success
Write-Host ""
Write-Host "  ========================================"
Write-Ok $S.Success
Write-Host ""
Write-Host "  $($S.RunCmd)"
Write-Host ""
Write-Warn $S.NewTerm
Write-Host ""
Read-Host "  Press Enter to exit"
