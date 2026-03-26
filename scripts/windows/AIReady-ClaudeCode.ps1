#Requires -Version 5.1
# AIReady - Claude Code Installer for Windows (PowerShell)
# =========================================================
# Version: 0.1.0

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# i18n string tables
$Strings = @{
    ko = @{
        Welcome     = 'AIReady - Claude Code 설치 도우미'
        Checking    = '시스템 확인 중...'
        InstallGit  = 'Git 설치 중...'
        InstallTool = 'Claude Code 설치 중...'
        Verifying   = '설치 확인 중...'
        AuthMsg     = '브라우저에서 Claude 계정으로 로그인이 필요합니다.'
        AuthSub     = 'Pro/Max/Teams/Enterprise 구독이 필요합니다.'
        AuthPerm    = '권한을 허용하세요.'
        Success     = 'Claude Code가 성공적으로 설치되었습니다!'
        RunCmd      = '시작하려면: claude'
        NewTerm     = '새 터미널을 열어야 할 수 있습니다.'
        Failed      = '설치 실패. 오류를 확인하세요.'
        GitFound    = 'Git 발견됨'
        GitInstalled = 'Git 설치 완료'
        GitFail     = 'Git 다운로드 실패'
        ClaudeFound = 'Claude Code 발견됨'
        ClaudeInstalled = 'Claude Code 설치 완료'
        ClaudeFail  = 'Claude Code 설치 실패'
        VerifyOk    = '확인 완료'
        VerifyFail  = '확인 실패'
    }
    en = @{
        Welcome     = 'AIReady - Claude Code Setup Helper'
        Checking    = 'Checking system...'
        InstallGit  = 'Installing Git...'
        InstallTool = 'Installing Claude Code...'
        Verifying   = 'Verifying installation...'
        AuthMsg     = 'Browser login required with your Claude account.'
        AuthSub     = 'Pro/Max/Teams/Enterprise subscription required.'
        AuthPerm    = 'Grant the requested permissions.'
        Success     = 'Claude Code installed successfully!'
        RunCmd      = 'To start: claude'
        NewTerm     = 'You may need to open a new terminal.'
        Failed      = 'Installation failed. Check errors above.'
        GitFound    = 'Git found'
        GitInstalled = 'Git installed'
        GitFail     = 'Git download failed'
        ClaudeFound = 'Claude Code found'
        ClaudeInstalled = 'Claude Code installed'
        ClaudeFail  = 'Claude Code installation failed'
        VerifyOk    = 'Verified'
        VerifyFail  = 'Verification failed'
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

# Step 2: Check/install Git
Write-Info 'Checking Git...'
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    Write-Info $S.InstallGit
    $gitInstaller = Join-Path $env:TEMP 'git-install.exe'
    try {
        Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/latest/download/Git-64-bit.exe' `
            -OutFile $gitInstaller -UseBasicParsing
        Start-Process -FilePath $gitInstaller -ArgumentList '/VERYSILENT', '/NORESTART', '/SUPPRESSMSGBOXES' -Wait
        Remove-Item $gitInstaller -Force -ErrorAction SilentlyContinue
        $env:PATH = "C:\Program Files\Git\cmd;$env:PATH"
        Write-Ok $S.GitInstalled
    } catch {
        Write-Fail $S.GitFail
        exit 1
    }
} else {
    Write-Ok $S.GitFound
}

# Step 3: Install Claude Code
Write-Info $S.InstallTool
$claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
if (-not $claudeCmd) {
    $claudeInstaller = Join-Path $env:TEMP 'claude-install.cmd'
    try {
        Invoke-WebRequest -Uri 'https://claude.ai/install.cmd' `
            -OutFile $claudeInstaller -UseBasicParsing
        $result = Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $claudeInstaller -Wait -PassThru
        Remove-Item $claudeInstaller -Force -ErrorAction SilentlyContinue
        $env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"
        if ($result.ExitCode -ne 0) {
            throw 'Installer returned non-zero exit code'
        }
        Write-Ok $S.ClaudeInstalled
    } catch {
        Write-Fail $S.ClaudeFail
        exit 1
    }
} else {
    Write-Ok $S.ClaudeFound
}

# Step 4: Verify
Write-Info $S.Verifying
$verifyCmd = Get-Command claude -ErrorAction SilentlyContinue
if ($verifyCmd) {
    Write-Ok $S.VerifyOk
} else {
    Write-Fail $S.VerifyFail
    exit 1
}

# Step 5: Auth guide
Write-Host ""
Write-Host "  $($S.AuthMsg)"
Write-Host "  $($S.AuthSub)"
Write-Host "  $($S.AuthPerm)"
Write-Host ""
Write-Host "  Opening claude.ai in your browser..."
Start-Process 'https://claude.ai'

# Step 6: Success
Write-Host ""
Write-Host "  ========================================"
Write-Ok $S.Success
Write-Host ""
Write-Host "  $($S.RunCmd)"
Write-Host ""
Write-Warn $S.NewTerm
Write-Host ""
Read-Host "  Press Enter to exit"
