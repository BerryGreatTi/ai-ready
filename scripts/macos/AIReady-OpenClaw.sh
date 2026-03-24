#!/usr/bin/env bash
set -euo pipefail

# AIReady - OpenClaw Installer for macOS
# =======================================

SCRIPT_VERSION="0.1.0"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

# Status indicators
step_ok()   { printf "  ${GREEN}[OK]${NC}   %s\n" "$1"; }
step_fail() { printf "  ${RED}[FAIL]${NC} %s\n" "$1"; }
step_info() { printf "  ${BLUE}[..]${NC}  %s\n" "$1"; }
step_warn() { printf "  ${YELLOW}[!!]${NC}  %s\n" "$1"; }

# PATH helper: permanently add to shell config
add_to_path_permanently() {
    local dir_to_add="$1"
    local shell_rc

    if [[ -n "${ZSH_VERSION:-}" ]] || [[ "$(basename "${SHELL:-}")" == "zsh" ]]; then
        shell_rc="$HOME/.zshrc"
    else
        shell_rc="$HOME/.bashrc"
    fi

    export PATH="$dir_to_add:$PATH"

    if [[ -f "$shell_rc" ]] && grep -q "$dir_to_add" "$shell_rc" 2>/dev/null; then
        return 0
    fi

    echo "" >> "$shell_rc"
    echo "# Added by AIReady installer" >> "$shell_rc"
    echo "export PATH=\"$dir_to_add:\$PATH\"" >> "$shell_rc"
}

# i18n
LANG_ID="en"
msg() {
    local key="$1"
    case "${LANG_ID}_${key}" in
        ko_welcome)        echo "AIReady - OpenClaw 설치 도우미" ;;
        ko_checking)       echo "시스템 확인 중..." ;;
        ko_install_node)   echo "Node.js 설치 중..." ;;
        ko_installing)     echo "OpenClaw 설치 중..." ;;
        ko_verifying)      echo "설치 확인 중..." ;;
        ko_select_provider) echo "AI 제공자를 선택하세요:" ;;
        ko_enter_api_key)  echo "API 키를 입력하세요 (입력이 숨겨집니다):" ;;
        ko_onboarding)     echo "온보딩 실행 중..." ;;
        ko_success)        echo "OpenClaw이 성공적으로 설치되었습니다!" ;;
        ko_run_cmd)        echo "시작하려면 터미널에서 다음을 실행하세요:" ;;
        ko_new_terminal)   echo "새 터미널을 열어야 할 수 있습니다." ;;
        ko_node_fail)      echo "Node.js 설치 실패. 수동으로 설치하세요: https://nodejs.org" ;;
        en_welcome)        echo "AIReady - OpenClaw Setup Helper" ;;
        en_checking)       echo "Checking system..." ;;
        en_install_node)   echo "Installing Node.js..." ;;
        en_installing)     echo "Installing OpenClaw..." ;;
        en_verifying)      echo "Verifying installation..." ;;
        en_select_provider) echo "Select your AI provider:" ;;
        en_enter_api_key)  echo "Enter your API key (input hidden):" ;;
        en_onboarding)     echo "Running onboarding..." ;;
        en_success)        echo "OpenClaw installed successfully!" ;;
        en_run_cmd)        echo "To start, run in your terminal:" ;;
        en_new_terminal)   echo "You may need to open a new terminal." ;;
        en_node_fail)      echo "Node.js install failed. Install manually: https://nodejs.org" ;;
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

# Step 2: Check/install Node.js
step_info "$(msg install_node)"
if command -v node &>/dev/null; then
    step_ok "Node.js $(node --version)"
else
    if command -v brew &>/dev/null; then
        brew install node
    else
        # Fallback: download .pkg installer
        NODE_PKG_URL="https://nodejs.org/dist/latest/node-latest.pkg"
        curl -fSL -o /tmp/node-installer.pkg "$NODE_PKG_URL"
        sudo installer -pkg /tmp/node-installer.pkg -target /
        rm -f /tmp/node-installer.pkg
    fi
    if command -v node &>/dev/null; then
        step_ok "Node.js $(node --version)"
    else
        step_fail "$(msg node_fail)"
        exit 1
    fi
fi

# Step 3: Install OpenClaw
step_info "$(msg installing)"
if command -v openclaw &>/dev/null; then
    step_ok "OpenClaw $(openclaw --version 2>/dev/null || echo 'installed')"
else
    if curl -fsSL https://openclaw.ai/install.sh | bash; then
        add_to_path_permanently "$HOME/.local/bin"
    fi
    if ! command -v openclaw &>/dev/null; then
        npm install -g openclaw@latest
        npm_bin="$(npm root -g)/.bin"
        add_to_path_permanently "$npm_bin"
    fi
    if command -v openclaw &>/dev/null; then
        step_ok "OpenClaw installed"
    else
        step_fail "OpenClaw installation failed"
        exit 1
    fi
fi

# Step 4: Provider selection
echo ""
echo "$(msg select_provider)"
echo "  1. OpenAI"
echo "  2. Anthropic"
echo "  3. Google (Gemini)"
echo "  4. Other"
printf "  Select (1-4): "
read -r provider_choice

case "$provider_choice" in
    1) PROVIDER="openai" ;;
    2) PROVIDER="anthropic" ;;
    3) PROVIDER="google" ;;
    *) PROVIDER="custom" ;;
esac

# Step 5: API key input (silent)
echo ""
printf "%s\n" "$(msg enter_api_key)"
printf "  API Key: "
read -rs api_key
echo ""

if [[ -z "$api_key" ]]; then
    step_warn "No API key provided. Skipping onboarding."
else
    # Step 6: Onboarding
    step_info "$(msg onboarding)"
    OPENCLAW_API_KEY="$api_key" openclaw onboard --provider "$PROVIDER" --install-daemon 2>/dev/null || \
        step_warn "Onboarding encountered issues. Run 'openclaw onboard' manually."
fi

# Step 7: Verify
step_info "$(msg verifying)"
if openclaw --version &>/dev/null; then
    step_ok "openclaw --version OK"
else
    step_fail "openclaw --version failed"
fi
openclaw doctor 2>/dev/null && step_ok "openclaw doctor OK" || step_warn "openclaw doctor reported issues"
openclaw gateway status 2>/dev/null && step_ok "openclaw gateway OK" || step_warn "openclaw gateway not running"

# Step 8: Success
echo ""
echo "========================================"
printf "  ${GREEN}%s${NC}\n" "$(msg success)"
echo ""
echo "  $(msg run_cmd)"
echo "    openclaw"
echo ""
step_warn "$(msg new_terminal)"
