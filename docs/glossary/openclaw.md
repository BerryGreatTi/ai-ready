# OpenClaw

An open-source personal AI assistant that runs locally. Created by Peter Steinberger. Enables Claude or other AI models to autonomously perform tasks across your computer and connected services (email, calendar, messaging, browser automation, etc.).

## Installation characteristics

- **Installer script** (recommended): Auto-detects OS, installs Node.js if needed, launches onboarding.
- **npm method**: Requires Node.js 22.16+ (24 recommended).
- **Onboarding**: `openclaw onboard --install-daemon` sets up API keys, AI model selection, and background daemon.
- **Verification**: `openclaw --version`, `openclaw doctor`, `openclaw gateway status`.

## AI provider support

Supports multiple AI providers. Primary: Anthropic (Claude), OpenAI, Google Gemini. Also supports local models via Ollama.

## Key commands

- `openclaw onboard --install-daemon` - Initial setup
- `openclaw doctor` - Health check
- `openclaw gateway status` - Verify gateway
