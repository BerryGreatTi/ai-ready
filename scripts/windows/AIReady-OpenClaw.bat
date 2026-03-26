@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

:: AIReady - OpenClaw Installer for Windows
:: =========================================
:: Version: 0.1.0

:: Language selection
echo.
echo   1. Korean (한국어)
echo   2. English
set /p "LANG_CHOICE=  Select / 선택 (1/2): "

if "%LANG_CHOICE%"=="1" (
    set "MSG_WELCOME=AIReady - OpenClaw 설치 도우미"
    set "MSG_CHECKING=시스템 확인 중..."
    set "MSG_INSTALL_NODE=Node.js 설치 중..."
    set "MSG_INSTALL_TOOL=OpenClaw 설치 중..."
    set "MSG_VERIFYING=설치 확인 중..."
    set "MSG_SELECT_PROVIDER=AI 제공자를 선택하세요:"
    set "MSG_ENTER_KEY=API 키를 입력하세요:"
    set "MSG_ONBOARDING=온보딩 실행 중..."
    set "MSG_SUCCESS=OpenClaw이 성공적으로 설치되었습니다!"
    set "MSG_RUN=시작하려면: openclaw"
    set "MSG_NEW_TERM=새 터미널을 열어야 할 수 있습니다."
    set "MSG_FAIL=설치 실패. 오류를 확인하세요."
) else (
    set "MSG_WELCOME=AIReady - OpenClaw Setup Helper"
    set "MSG_CHECKING=Checking system..."
    set "MSG_INSTALL_NODE=Installing Node.js..."
    set "MSG_INSTALL_TOOL=Installing OpenClaw..."
    set "MSG_VERIFYING=Verifying installation..."
    set "MSG_SELECT_PROVIDER=Select your AI provider:"
    set "MSG_ENTER_KEY=Enter your API key:"
    set "MSG_ONBOARDING=Running onboarding..."
    set "MSG_SUCCESS=OpenClaw installed successfully!"
    set "MSG_RUN=To start: openclaw"
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

:: Step 2: Check curl
where curl >nul 2>&1
if errorlevel 1 (
    echo   [FAIL] curl not found. Windows 10 1803+ required.
    goto :end_fail
)
echo   [OK] curl available

:: Step 3: Check/install Node.js
echo   [..] Checking Node.js...
where node >nul 2>&1
if errorlevel 1 (
    echo   [..] !MSG_INSTALL_NODE!
    :: Download Node.js LTS MSI (no winget)
    curl -fSL -o "%TEMP%\node-installer.msi" "https://nodejs.org/dist/latest-v20.x/node-v20.18.1-x64.msi"
    if errorlevel 1 (
        echo   [FAIL] Node.js download failed
        goto :end_fail
    )
    msiexec /i "%TEMP%\node-installer.msi" /quiet /norestart
    del /f /q "%TEMP%\node-installer.msi" >nul 2>&1
    :: Refresh PATH
    for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "USER_PATH=%%B"
    set "PATH=%PROGRAMFILES%\nodejs;!USER_PATH!;%PATH%"
    where node >nul 2>&1
    if errorlevel 1 (
        echo   [FAIL] Node.js installation failed
        goto :end_fail
    )
    echo   [OK] Node.js installed
) else (
    for /f "tokens=*" %%V in ('node --version 2^>nul') do set "NODE_VER=%%V"
    echo   [OK] Node.js !NODE_VER! found
)

:: Step 4: Install OpenClaw
echo   [..] !MSG_INSTALL_TOOL!
where openclaw >nul 2>&1
if errorlevel 1 (
    :: Try official installer first
    curl -fsSL "https://openclaw.ai/install.cmd" -o "%TEMP%\openclaw-install.cmd" >nul 2>&1
    if not errorlevel 1 (
        call "%TEMP%\openclaw-install.cmd"
        del /f /q "%TEMP%\openclaw-install.cmd" >nul 2>&1
    )
    :: Fallback: npm install
    where openclaw >nul 2>&1
    if errorlevel 1 (
        npm install -g openclaw@latest
        if errorlevel 1 (
            echo   [FAIL] OpenClaw installation failed
            goto :end_fail
        )
    )
    where openclaw >nul 2>&1
    if errorlevel 1 (
        echo   [FAIL] OpenClaw not found after installation
        goto :end_fail
    )
)
echo   [OK] OpenClaw installed

:: Step 5: Provider selection
echo.
echo   !MSG_SELECT_PROVIDER!
echo   1. OpenAI
echo   2. Anthropic
echo   3. Google (Gemini)
echo   4. Other
set /p "PROVIDER_CHOICE=  Select (1-4): "

if "%PROVIDER_CHOICE%"=="1" set "PROVIDER=openai"
if "%PROVIDER_CHOICE%"=="2" set "PROVIDER=anthropic"
if "%PROVIDER_CHOICE%"=="3" set "PROVIDER=google"
if "%PROVIDER_CHOICE%"=="4" set "PROVIDER=custom"
if not defined PROVIDER set "PROVIDER=custom"

:: Step 6: API key input
echo.
echo   !MSG_ENTER_KEY!
set /p "API_KEY=  API Key: "

if "!API_KEY!"=="" (
    echo   [!!] No API key provided. Skipping onboarding.
) else (
    :: Step 7: Onboarding
    echo   [..] !MSG_ONBOARDING!
    set "OPENCLAW_API_KEY=!API_KEY!"
    openclaw onboard --provider !PROVIDER! --install-daemon >nul 2>&1
    if errorlevel 1 (
        echo   [!!] Onboarding encountered issues. Run 'openclaw onboard' manually.
    ) else (
        echo   [OK] Onboarding complete
    )
)

:: Step 8: Verify
echo   [..] !MSG_VERIFYING!
openclaw --version >nul 2>&1
if errorlevel 1 (
    echo   [FAIL] Verification failed
    goto :end_fail
)
echo   [OK] openclaw --version OK

openclaw doctor >nul 2>&1
if errorlevel 1 (
    echo   [!!] openclaw doctor reported issues
) else (
    echo   [OK] openclaw doctor OK
)

openclaw gateway status >nul 2>&1
if errorlevel 1 (
    echo   [!!] openclaw gateway not running
) else (
    echo   [OK] openclaw gateway OK
)

:: Step 9: Success
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
