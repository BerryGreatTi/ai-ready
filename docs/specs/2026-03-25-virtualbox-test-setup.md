# AIReady - VirtualBox 테스트 환경 구축 가이드

Windows 10/11 클린 환경에서 AIReady를 수동 테스트하기 위한 상세 절차.

---

## Part 1: VirtualBox 설치

### 1.1 다운로드

1. https://www.virtualbox.org/wiki/Downloads 접속
2. **"VirtualBox platform packages"** 섹션에서 자신의 호스트 OS에 맞는 링크 클릭:
   - Windows 호스트: **"Windows hosts"** 클릭
   - macOS 호스트: **"macOS / Intel hosts"** 또는 **"macOS / Apple Silicon hosts"** 클릭
   - Linux 호스트: **"Linux distributions"** 클릭
3. (선택) **"VirtualBox Extension Pack"** - 같은 페이지 아래에서 **"All supported platforms"** 클릭하여 다운로드. USB 3.0 등 추가 기능이 필요할 때만.

### 1.2 설치 (Windows 호스트 기준)

1. 다운로드한 `VirtualBox-7.x.x-xxxxx-Win.exe` 더블클릭
2. **Next** → **Next** → **Next** → **Yes** (네트워크 경고, 일시적으로 끊길 수 있음) → **Install**
3. 설치 완료 후 **Finish** (VirtualBox 자동 실행)

### 1.3 설치 (macOS 호스트 기준)

1. 다운로드한 `VirtualBox-7.x.x-xxxxx-macOS.dmg` 더블클릭
2. `VirtualBox.pkg` 더블클릭하여 설치
3. **시스템 설정 → 개인 정보 및 보안** 에서 Oracle 소프트웨어 허용
4. 재시작

---

## Part 2: Windows ISO 다운로드

타겟 사용자가 Home 에디션을 사용할 확률이 높으므로, **Home 에디션을 기본으로 테스트**합니다. multi-edition ISO에서 설치 시 Home을 선택합니다.

### 2.1 Windows 10 ISO (Home)

**권장: multi-edition ISO (Home 포함)**

1. https://www.microsoft.com/ko-kr/software-download/windows10ISO 접속
   - Windows PC에서 접속하면 Media Creation Tool 페이지로 리다이렉트될 수 있음
   - 이 경우 브라우저 개발자 도구 (F12) → 모바일 모드로 전환 후 새로고침하면 직접 ISO 다운로드 가능
2. 에디션 선택: **"Windows 10"**
3. 언어: **"Korean"** (한글 Windows 인코딩 테스트 필수)
4. **"64-bit 다운로드"** 클릭 (약 5GB)
5. 설치 시 에디션 선택 화면에서 **"Windows 10 Home"** 선택

**대안: Enterprise 평가판 (제품키 불필요, 90일)**

1. https://www.microsoft.com/en-us/evalcenter/evaluate-windows-10-enterprise 접속
2. **"Download the ISO"** → 양식 작성 → Korean → 64-bit
3. 제품키 입력 불필요. 단, 실제 사용자 환경(Home)과 다를 수 있음.

### 2.2 Windows 11 ISO (Home)

**권장: multi-edition ISO (Home 포함)**

1. https://www.microsoft.com/ko-kr/software-download/windows11 접속
2. **"Windows 11 디스크 이미지(ISO) 다운로드"** 섹션에서 **"Windows 11 (multi-edition ISO)"** 선택
3. **"다운로드"** 클릭
4. 언어: **"Korean"** → **"확인"**
5. **"64-bit 다운로드"** 클릭 (약 6GB)
6. 설치 시 에디션 선택 화면에서 **"Windows 11 Home"** 선택

**대안: Enterprise 평가판 (제품키 불필요, 90일)**

1. https://www.microsoft.com/en-us/evalcenter/evaluate-windows-11-enterprise 접속
2. **"Download the ISO"** → 양식 작성 → Korean → 64-bit

### 제품키 참고

multi-edition ISO로 Home을 설치할 때 제품키를 요구하면:
- **"제품 키가 없습니다"** 클릭하면 에디션 선택 화면이 나옴
- 활성화 없이 사용 가능 (바탕화면에 워터마크만 표시, 기능 제한 없음)
- 테스트 목적으로는 충분

---

## Part 3: VM 생성

### 3.1 Windows 10 VM

1. VirtualBox 실행 → **"새로 만들기"** (또는 Machine → New)
2. 설정:
   - **이름**: `AIReady-Test-Win10`
   - **폴더**: 기본값
   - **ISO Image**: 다운로드한 Windows 10 ISO 파일 선택
   - **"Skip Unattended Installation"** 체크 (수동 설치를 위해)
3. **Next** → 하드웨어:
   - **메모리(RAM)**: `4096` MB (4GB)
   - **프로세서**: `2` CPU
4. **Next** → 가상 하드 디스크:
   - **"Create a Virtual Hard Disk Now"** 선택
   - **크기**: `50` GB (동적 할당이므로 실제로는 필요한 만큼만 사용)
5. **Next** → **Finish**

### 3.2 Windows 11 VM

Windows 11은 추가 요구사항이 있습니다 (TPM 2.0, Secure Boot).

1. VirtualBox 실행 → **"새로 만들기"**
2. 설정:
   - **이름**: `AIReady-Test-Win11`
   - **ISO Image**: 다운로드한 Windows 11 ISO 파일 선택
   - **"Skip Unattended Installation"** 체크
3. **Next** → 하드웨어:
   - **메모리(RAM)**: `4096` MB (4GB, 최소)
   - **프로세서**: `2` CPU
   - **"Enable EFI"** 체크
4. **Next** → 가상 하드 디스크:
   - **크기**: `64` GB
5. **Finish**

**TPM 우회 (Windows 11 설치 시 필수):**

6. 생성된 VM 선택 → **설정(Settings)**
7. **System → Motherboard**:
   - **"Enable EFI"** 체크 확인
8. **시작** 후 Windows 설치 화면에서 TPM 체크를 우회해야 할 수 있음:
   - 설치 화면에서 `Shift + F10` → 명령 프롬프트 열기
   - `regedit` 입력
   - `HKEY_LOCAL_MACHINE\SYSTEM\Setup` 이동
   - 우클릭 → 새로 만들기 → 키 → 이름: `LabConfig`
   - `LabConfig` 안에 DWORD (32비트) 값 3개 생성:
     - `BypassTPMCheck` = `1`
     - `BypassRAMCheck` = `1`
     - `BypassSecureBootCheck` = `1`
   - 레지스트리 편집기 닫고 설치 계속

---

## Part 4: Windows 설치

### 4.1 VM 시작 및 설치

1. VM 선택 → **시작(Start)** 클릭
2. "Press any key to boot from CD..." 메시지가 나오면 아무 키 입력
3. Windows 설치 화면:
   - 언어: **한국어**
   - 시간: **한국**
   - 키보드: **한국어**
   - **"지금 설치"** 클릭
4. 제품키:
   - 평가판 ISO: 자동으로 입력됨
   - multi-edition ISO: **"제품 키가 없습니다"** 클릭 → **"Windows 10 Home"** 또는 **"Windows 11 Home"** 선택 (사용자 환경 재현)
5. 사용 조건 동의 → **"사용자 지정: Windows만 설치"**
6. 파티션 선택: 할당되지 않은 공간 선택 → **"다음"**
7. 설치 완료까지 대기 (10-20분, 자동 재시작 포함)

### 4.2 초기 설정 (OOBE)

**Windows 10:**
1. 지역: 한국
2. 키보드: 한국어 → 건너뛰기
3. **"오프라인 계정"** → **"제한된 경험"** (Microsoft 계정 없이 진행)
4. 사용자 이름: `TestUser`
5. 비밀번호: (비워두면 암호 없이 로그인)
6. 개인 정보 설정: 모두 **아니요** → **수락**

**Windows 11:**
1. 국가/지역: 한국
2. 키보드: 한국어
3. 네트워크: **"인터넷에 연결되어 있지 않음"** → **"제한된 설정으로 계속"**
   - 이 옵션이 안 보이면: `Shift + F10` → `OOBE\BYPASSNRO` 입력 → 재시작
4. 사용자 이름: `TestUser`
5. 비밀번호: (비워두기)
6. 개인 정보 설정: 모두 **아니요** → **수락**

### 4.3 VM 설정 최적화

Windows 설치 완료 후:

1. **VirtualBox Guest Additions 설치:**
   - VM 메뉴 → **장치 → Guest Additions CD 이미지 삽입**
   - 파일 탐색기 → CD 드라이브 → `VBoxWindowsAdditions.exe` 실행
   - 설치 후 재시작
   - 효과: 해상도 자동 조정, 클립보드 공유, 드래그&드롭

2. **공유 클립보드 설정:**
   - VM 메뉴 → **장치 → 공유 클립보드 → 양방향**

3. **인터넷 연결 확인:**
   - 브라우저 열기 → google.com 접속 확인
   - 안 되면: VM 설정 → 네트워크 → 어댑터 1 → NAT 선택

---

## Part 5: 스냅샷 저장

**중요: 테스트 전에 클린 상태 스냅샷을 반드시 저장합니다.**

1. VM이 실행 중인 상태에서: VM 메뉴 → **머신 → 스냅샷 찍기**
2. 이름: `Clean-Install` (또는 `클린-상태`)
3. **확인**

이 스냅샷으로 언제든 초기 상태로 복원 가능:
- VM 종료 → 스냅샷 탭 → `Clean-Install` 우클릭 → **"복원"**

---

## Part 6: AIReady 테스트 수행

### 6.1 테스트 준비

VM 내 브라우저에서 릴리즈 페이지 접속:
```
https://github.com/BerryGreatTi/ai-ready/releases/latest
```

### 6.2 테스트 시나리오 A: GUI (Windows 10)

| 단계 | 수행 | 예상 결과 |
|------|------|----------|
| 1 | `AIReady-ClaudeCode-Win.exe` 다운로드 | 정상 다운로드 |
| 2 | 더블클릭 실행 | SmartScreen 경고 → "추가 정보" → "실행" |
| 3 | 언어 선택 | 한국어/English 버튼 표시 |
| 4 | 한국어 선택 | UI가 한국어로 전환 |
| 5 | Claude Code 선택 → 다음 | 진행 화면 표시 |
| 6 | Git 감지 | **"Git이 감지되지 않아 설치합니다"** (클린 환경이므로) |
| 7 | Git 설치 | 직접 .exe 다운로드 + /VERYSILENT (winget 아님) |
| 8 | Claude Code 설치 | install.cmd 실행 (npm 아님) |
| 9 | 인증 안내 | 브라우저 열림 |
| 10 | 완료 | `claude` 명령어 표시 + 복사 버튼 |

### 6.3 테스트 시나리오 B: BAT 스크립트 (Windows 10, 한글)

| 단계 | 수행 | 예상 결과 |
|------|------|----------|
| 1 | `AIReady-ClaudeCode.bat` 다운로드 | 정상 다운로드 |
| 2 | 더블클릭 실행 | CMD 창 열림 |
| 3 | 인코딩 확인 | 한글 메시지와 명령어가 **섞이지 않음** |
| 4 | 언어 선택 (1) | 한국어 메시지 표시 |
| 5 | Git 설치 | 직접 .exe 다운로드 (winget 아님) |
| 6 | Claude Code 설치 | install.cmd 실행 |
| 7 | 인증 안내 | 브라우저 자동 열림 |

### 6.4 테스트 시나리오 C: PS1 스크립트 (Windows 10)

| 단계 | 수행 | 예상 결과 |
|------|------|----------|
| 1 | PowerShell 열기 | 시작 → PowerShell 검색 → 실행 |
| 2 | 실행 정책 설정 | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| 3 | 스크립트 실행 | `.\AIReady-ClaudeCode.ps1` |
| 4 | 인코딩 확인 | 한글이 깨지지 않음 ($Strings 해시테이블 사용) |
| 5 | 설치 진행 | Git + Claude Code 설치 |

### 6.5 테스트 시나리오 D: OpenClaw (Windows 11)

| 단계 | 수행 | 예상 결과 |
|------|------|----------|
| 1 | `AIReady-OpenClaw-Win.exe` 다운로드 + 실행 | GUI 실행 |
| 2 | Node.js 감지 | 클린 환경: "Node.js가 없습니다. 설치합니다" |
| 3 | Node.js 설치 | .msi 다운로드 + msiexec (winget 아님) |
| 4 | OpenClaw 설치 | 공식 installer script → npm fallback |
| 5 | AI 제공자 선택 | Anthropic(추천), OpenAI, Gemini 상단 표시 |
| 6 | API 키 입력 | 마스킹, 붙여넣기 버튼, 유효성 검증 |
| 7 | 온보딩 | `openclaw onboard --install-daemon` 자동 실행 |

### 6.6 각 테스트 후

1. 결과 기록 (성공/실패, 스크린샷)
2. VM 종료
3. `Clean-Install` 스냅샷으로 복원
4. 다음 테스트 시나리오 수행

---

## Part 7: 테스트 결과 기록 템플릿

```markdown
## Test Report: AIReady v0.1.0-rc4

### Environment
- VirtualBox: 7.x.x
- Host OS: [macOS/Linux/Windows]
- Guest OS: Windows 10 Korean / Windows 11 Korean

### Results

| # | Scenario | OS | Result | Notes |
|---|----------|----|--------|-------|
| 1 | GUI - Claude Code | Win10 | PASS/FAIL | |
| 2 | GUI - OpenClaw | Win10 | PASS/FAIL | |
| 3 | BAT - Claude Code | Win10 | PASS/FAIL | |
| 4 | BAT - OpenClaw | Win10 | PASS/FAIL | |
| 5 | PS1 - Claude Code | Win10 | PASS/FAIL | |
| 6 | PS1 - OpenClaw | Win10 | PASS/FAIL | |
| 7 | GUI - Claude Code | Win11 | PASS/FAIL | |
| 8 | GUI - OpenClaw | Win11 | PASS/FAIL | |
| 9 | BAT - Claude Code | Win11 | PASS/FAIL | |
| 10 | BAT - OpenClaw | Win11 | PASS/FAIL | |
| 11 | BAT encoding test | Win10 Korean | PASS/FAIL | 한글/명령어 혼합 여부 |

### Issues Found
- [ ] Issue 1: ...
- [ ] Issue 2: ...
```

---

## 시간 예상

| 작업 | 소요 시간 |
|------|----------|
| VirtualBox 설치 | 5분 |
| Windows 10 ISO 다운로드 | 20-40분 (네트워크 속도 따라) |
| Windows 11 ISO 다운로드 | 20-40분 |
| Windows 10 VM 생성 + 설치 | 30분 |
| Windows 11 VM 생성 + 설치 | 30분 |
| 스냅샷 생성 | 2분 x 2 |
| 테스트 수행 (11개 시나리오) | 각 10-15분 |
| **총 합계** | **약 3-4시간** |

## 팁

- **ISO 다운로드와 VM 설치를 병렬로**: Windows 10 ISO를 먼저 받고 VM 설치하는 동안 Windows 11 ISO 다운로드
- **스냅샷은 돈이 안 듬**: 의심스러우면 스냅샷 복원하고 다시 테스트
- **클립보드 공유 필수**: API 키 붙여넣기 테스트에 필요
- **한글 Windows가 핵심**: 반드시 한국어로 설치하여 인코딩 이슈 재현
