@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

:: AIReady - Claude Code Installer for Windows
:: ============================================
:: Version: 0.1.0

:: Language selection
echo.
echo   1. Korean (한국어)
echo   2. English
set /p "LANG_CHOICE=  Select / 선택 (1/2): "

if "%LANG_CHOICE%"=="1" (
    set "MSG_WELCOME=AIReady - Claude Code 설치 도우미"
    set "MSG_CHECKING=시스템 확인 중..."
    set "MSG_INSTALL_GIT=Git 설치 중..."
    set "MSG_INSTALL_TOOL=Claude Code 설치 중..."
    set "MSG_VERIFYING=설치 확인 중..."
    set "MSG_SUCCESS=Claude Code가 성공적으로 설치되었습니다!"
    set "MSG_AUTH=브라우저에서 Claude 계정으로 로그인이 필요합니다."
    set "MSG_AUTH_SUB=Pro/Max/Teams/Enterprise 구독이 필요합니다."
    set "MSG_AUTH_PERM=권한을 허용하세요."
    set "MSG_RUN=시작하려면: claude"
    set "MSG_NEW_TERM=새 터미널을 열어야 할 수 있습니다."
    set "MSG_FAIL=설치 실패. 오류를 확인하세요."
) else (
    set "MSG_WELCOME=AIReady - Claude Code Setup Helper"
    set "MSG_CHECKING=Checking system..."
    set "MSG_INSTALL_GIT=Installing Git..."
    set "MSG_INSTALL_TOOL=Installing Claude Code..."
    set "MSG_VERIFYING=Verifying installation..."
    set "MSG_SUCCESS=Claude Code installed successfully!"
    set "MSG_AUTH=Browser login required with your Claude account."
    set "MSG_AUTH_SUB=Pro/Max/Teams/Enterprise subscription required."
    set "MSG_AUTH_PERM=Grant the requested permissions."
    set "MSG_RUN=To start: claude"
    set "MSG_NEW_TERM=You may need to open a new terminal."
    set "MSG_FAIL=Installation failed. Check errors above."
)

echo.
echo   !MSG_WELCOME!
echo   ========================================

:: Step 1: System check
echo   [..] !MSG_CHECKING!
ver >nul 2>&1
if errorlevel 1 (
    echo   [FAIL] Windows detection failed
    goto :end_fail
)
echo   [OK] Windows detected

:: Step 2: Check curl availability
where curl >nul 2>&1
if errorlevel 1 (
    echo   [FAIL] curl not found. Please install curl or use Windows 10 1803+
    goto :end_fail
)
echo   [OK] curl available

:: Step 3: Check/install Git
echo   [..] Checking Git...
where git >nul 2>&1
if errorlevel 1 (
    echo   [..] !MSG_INSTALL_GIT!
    curl -fSL -o "%TEMP%\git-install.exe" "https://github.com/git-for-windows/git/releases/latest/download/Git-64-bit.exe"
    if errorlevel 1 (
        echo   [FAIL] Git download failed
        goto :end_fail
    )
    "%TEMP%\git-install.exe" /VERYSILENT /NORESTART /SUPPRESSMSGBOXES
    del /f /q "%TEMP%\git-install.exe" >nul 2>&1
    :: Refresh PATH with Git
    set "PATH=C:\Program Files\Git\cmd;%PATH%"
    where git >nul 2>&1
    if errorlevel 1 (
        echo   [FAIL] Git installation failed
        goto :end_fail
    )
    echo   [OK] Git installed
) else (
    echo   [OK] Git found
)

:: Step 4: Install Claude Code
echo   [..] !MSG_INSTALL_TOOL!
where claude >nul 2>&1
if errorlevel 1 (
    curl -fsSL "https://claude.ai/install.cmd" -o "%TEMP%\claude-install.cmd"
    if errorlevel 1 (
        echo   [FAIL] Claude Code download failed
        goto :end_fail
    )
    call "%TEMP%\claude-install.cmd"
    del /f /q "%TEMP%\claude-install.cmd" >nul 2>&1
    :: Refresh PATH
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
    where claude >nul 2>&1
    if errorlevel 1 (
        echo   [FAIL] Claude Code installation failed
        goto :end_fail
    )
)
echo   [OK] Claude Code installed

:: Step 5: Verify
echo   [..] !MSG_VERIFYING!
claude --version >nul 2>&1
if errorlevel 1 (
    echo   [FAIL] Verification failed
    goto :end_fail
)
echo   [OK] Verified

:: Step 6: Auth guide
echo.
echo   !MSG_AUTH!
echo   !MSG_AUTH_SUB!
echo   !MSG_AUTH_PERM!
echo.
echo   Opening claude.ai in your browser...
start "" "https://claude.ai"

:: Step 7: Success
echo.
echo   ========================================
echo   !MSG_SUCCESS!
echo.
echo   !MSG_RUN!
echo.
echo   !MSG_NEW_TERM!
echo.
pause
goto :eof

:end_fail
echo.
echo   !MSG_FAIL!
pause
goto :eof
