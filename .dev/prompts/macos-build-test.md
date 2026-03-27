# macOS Build & E2E Test Prompt

이 프롬프트는 macOS에서 AIReady GUI 앱을 빌드하고 테스트하기 위한 것입니다.

## 사전 준비

```bash
# 1. 최신 코드 pull
cd ~/Projects/install-ai  # 또는 프로젝트 경로
git pull origin main

# 2. Python 환경 설정
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pip install pyinstaller customtkinter
```

## 1단계: 빌드

```bash
# GUI .app 번들 빌드
.dev/scripts/build-all.sh v0.2.0-rc1
```

빌드 결과:
- `release/v0.2.0-rc1/gui/AIReady-ClaudeCode-Mac.zip`
- `release/v0.2.0-rc1/gui/AIReady-OpenClaw-Mac.zip`

## 2단계: Gatekeeper 우회 테스트

```bash
# .app 압축 해제
cd release/v0.2.0-rc1/gui
unzip AIReady-ClaudeCode-Mac.zip

# Tier 1: xattr 명령으로 quarantine 해제
xattr -cr AIReady-ClaudeCode-Mac.app

# 실행
open AIReady-ClaudeCode-Mac.app
```

**체크리스트:**
- [ ] xattr -cr 후 정상 실행되는가?
- [ ] 우클릭 -> Open으로도 실행 가능한가? (별도 복사본으로 테스트)

## 3단계: GUI 기능 테스트

### Claude Code 설치 플로우
- [ ] 언어 선택 화면 표시 (한국어/English)
- [ ] 한국어 선택 후 도구 선택 화면
- [ ] Claude Code 선택 후 Progress 화면
- [ ] 각 설치 단계 진행 표시:
  - check_system
  - install_prereqs (Git, Node.js, UV)
  - verify_prereqs
  - install_tool (claude)
  - verify_install
- [ ] 완료 화면에서 자동 터미널 실행 (Terminal.app)
- [ ] "Launch" 버튼 반복 클릭 가능
- [ ] Copy 버튼으로 명령어 클립보드 복사

### OpenClaw 설치 플로우
- [ ] 동일 플로우 반복 (openclaw 선택)
- [ ] 터미널에서 `openclaw onboard` 실행되는지 확인

## 4단계: 플랫폼 특화 테스트

### Homebrew 경로 테스트
- [ ] Homebrew 있는 환경: `brew install node/git` 사용하는지 확인
- [ ] PATH refresh 후 바이너리 탐지 성공

### xcode-select 폴링 (Homebrew 없는 환경에서만)
- [ ] Homebrew 미설치 시 `xcode-select --install` 다이얼로그 표시
- [ ] CLT 설치 완료 후 git 자동 탐지 (최대 10분 폴링)
- [ ] 설치 취소/타임아웃 시 적절한 에러 메시지

### PATH 영구 저장
- [ ] 설치 후 `~/.zshrc` 또는 `~/.bashrc`에 PATH export 추가됨
- [ ] 새 터미널에서 `claude --version` 또는 `openclaw --version` 동작

### sudo 동작
- [ ] Homebrew 없을 때 Node.js pkg 설치 시 sudo 비밀번호 요청
- [ ] sudo 인증 후 설치 성공

## 5단계: 엣지 케이스

- [ ] 이미 설치된 도구가 있을 때 skip 동작
- [ ] 네트워크 오프라인 시 적절한 에러 표시
- [ ] 다크모드 / 라이트모드 UI 확인
- [ ] 창 크기 적절한지 확인 (500x520)

## 문제 발생 시

로그 파일 위치: `~/.aiready/logs/`

문제가 발생하면 다음 정보와 함께 보고:
1. macOS 버전 (예: Sonoma 14.x)
2. 칩 (Intel vs Apple Silicon)
3. Homebrew 설치 여부
4. 에러 메시지 또는 스크린샷
