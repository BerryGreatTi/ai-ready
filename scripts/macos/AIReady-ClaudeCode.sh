#!/usr/bin/env bash
set -euo pipefail

# AIReady - Claude Code Installer for macOS
# ==========================================

SCRIPT_VERSION="0.1.0"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

# Status indicators
step_ok()   { printf "  ${GREEN}[OK]${NC}   %s\n" "$1"; }
step_fail() { printf "  ${RED}[FAIL]${NC} %s\n" "$1"; }
step_info() { printf "  ${BLUE}[..]${NC}  %s\n" "$1"; }
step_warn() { printf "  ${YELLOW}[!!]${NC}  %s\n" "$1"; }

# i18n
LANG_ID="en"
msg() {
    local key="$1"
    case "${LANG_ID}_${key}" in
        ko_welcome)      echo "AIReady - Claude Code 설치 도우미" ;;
        ko_lang_select)  echo "언어를 선택하세요" ;;
        ko_checking)     echo "시스템 확인 중..." ;;
        ko_installing)   echo "Claude Code 설치 중..." ;;
        ko_verifying)    echo "설치 확인 중..." ;;
        ko_auth_title)   echo "Claude Code 인증" ;;
        ko_auth_step1)   echo "1. 브라우저에서 Claude 계정으로 로그인하세요" ;;
        ko_auth_step2)   echo "2. Pro/Max/Teams/Enterprise 구독이 필요합니다" ;;
        ko_auth_step3)   echo "3. 권한을 허용하세요" ;;
        ko_auth_open)    echo "브라우저를 열겠습니까? (Y/n)" ;;
        ko_success)      echo "Claude Code가 성공적으로 설치되었습니다!" ;;
        ko_run_cmd)      echo "시작하려면 터미널에서 다음을 실행하세요:" ;;
        ko_new_terminal) echo "새 터미널을 열어야 할 수 있습니다." ;;
        en_welcome)      echo "AIReady - Claude Code Setup Helper" ;;
        en_lang_select)  echo "Select your language" ;;
        en_checking)     echo "Checking system..." ;;
        en_installing)   echo "Installing Claude Code..." ;;
        en_verifying)    echo "Verifying installation..." ;;
        en_auth_title)   echo "Claude Code Authentication" ;;
        en_auth_step1)   echo "1. Log in with your Claude account in the browser" ;;
        en_auth_step2)   echo "2. Pro/Max/Teams/Enterprise subscription required" ;;
        en_auth_step3)   echo "3. Grant the requested permissions" ;;
        en_auth_open)    echo "Open browser? (Y/n)" ;;
        en_success)      echo "Claude Code installed successfully!" ;;
        en_run_cmd)      echo "To start, run in your terminal:" ;;
        en_new_terminal) echo "You may need to open a new terminal." ;;
        *) echo "$key" ;;
    esac
}

# Language selection
echo ""
echo "  1. 한국어"
echo "  2. English"
printf "  Select / 선택 (1/2): "
read -r choice
case "$choice" in
    1) LANG_ID="ko" ;;
    *) LANG_ID="en" ;;
esac

echo ""
echo "$(msg welcome)"
echo "========================================"

# Step 1: System check
step_info "$(msg checking)"
if [[ "$(uname -s)" != "Darwin" ]]; then
    step_fail "This script is for macOS only"
    exit 1
fi
step_ok "macOS $(sw_vers -productVersion)"

# Step 2: Install Claude Code
step_info "$(msg installing)"
if command -v claude &>/dev/null; then
    step_ok "Claude Code $(claude --version 2>/dev/null || echo 'installed')"
else
    curl -fsSL https://claude.ai/install.sh | bash
    export PATH="$HOME/.local/bin:$PATH"
    if command -v claude &>/dev/null; then
        step_ok "Claude Code installed"
    else
        step_fail "Installation failed"
        exit 1
    fi
fi

# Step 3: Verify
step_info "$(msg verifying)"
if claude --version &>/dev/null; then
    step_ok "claude --version OK"
else
    step_fail "claude --version failed"
fi

# Step 4: Authentication guide
echo ""
echo "$(msg auth_title)"
echo "----------------------------------------"
echo "$(msg auth_step1)"
echo "$(msg auth_step2)"
echo "$(msg auth_step3)"
echo ""
printf "%s " "$(msg auth_open)"
read -r auth_choice
if [[ "$auth_choice" != "n" && "$auth_choice" != "N" ]]; then
    open "https://claude.ai" 2>/dev/null || true
fi

# Step 5: Success
echo ""
echo "========================================"
printf "  ${GREEN}%s${NC}\n" "$(msg success)"
echo ""
echo "  $(msg run_cmd)"
echo "    claude"
echo ""
step_warn "$(msg new_terminal)"
