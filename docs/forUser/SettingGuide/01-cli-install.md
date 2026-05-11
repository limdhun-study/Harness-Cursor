# Cursor Agent CLI 설치

Windows는 **PowerShell에서 네이티브 설치**를 기본으로 한다. macOS·Linux는 터미널에서 **`curl | bash`** 이다.

인증·API 키는 [02-cursor-credentials.md](02-cursor-credentials.md) 를 따른다.

**하네스 루프**(`python scripts/harness_cli_loop.py`)는 **실행 중인 셸의 PATH**에서 `agent`(또는 설정 JSON의 `agent_command`)를 찾는다. Windows에서는 네이티브 설치 후 **같은 PowerShell**에서 `agent`와 `python`이 함께 보여야 한다.

---

## Windows(PowerShell, 네이티브)

공식 설치 스크립트:

```powershell
irm 'https://cursor.com/install?win32=true' | iex
```

스크립트가 바이너리를 **`%LOCALAPPDATA%\cursor-agent`** 아래에 두고, 사용자 PATH에 설치 경로를 넣는다. 끝나면 안내 문구가 나올 수 있다.

**바로 확인:** 먼저 **새 PowerShell**을 연 뒤 `agent --version` 을 실행한다. 같은 창에서 바로 확인하려면 사용자 PATH가 아직 세션에 없을 수 있어, 아래로 갱신한 뒤 버전을 본다.

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
agent --version
```

Worker 등 인증이 필요하면 [02-cursor-credentials.md](02-cursor-credentials.md) 의 **`agent login`** 을 따른다.

### 설치 중 오류(`Rename-Item` 액세스 거부 등)

설치 스크립트가 **`…\cursor-agent\versions\dist-package`** 이름을 버전 폴더로 바꿀 때 **파일이 다른 프로그램에 잠겨 있으면** 실패한다.

1. 다른 PowerShell/터미널에서 돌아가는 **`agent`** 가 있으면 종료한다.
2. 그래도 안 되면 **`%LOCALAPPDATA%\cursor-agent\versions\dist-package`** 폴더를 삭제한 뒤, 위 **`irm … | iex`** 를 다시 실행한다. (탐색기로 해당 폴더를 연 상태면 닫는다.)
3. 계속 잠기면 PC 재부팅 후 2번부터 반복한다.

관리자 PowerShell은 보통 필요 없다. 필요 시 Cursor 공식 문서를 본다.

### Worker 예시(선택)

저장소를 Windows 경로 그대로 쓴다.

```powershell
cd C:\path\to\Harness-Cursor
agent worker start --worker-dir .
```

---

## macOS / Linux

```bash
curl https://cursor.com/install -fsS | bash
```

설치 안내에 따라 PATH에 **`~/.local/bin`** 등이 잡혀 있는지 확인한 뒤:

```bash
agent --version
```

---

## 설치부터 Worker까지(Windows·압축 예)

저장소 경로는 본인 환경에 맞게 바꾼다.

```powershell
irm 'https://cursor.com/install?win32=true' | iex
# 새 PowerShell을 열거나, 위 Windows 절의 PATH 갱신 한 줄 후:
agent --version
agent login
cd C:\path\to\Harness-Cursor
agent worker start --worker-dir .
```

---

## 공식 문서

- [Cursor CLI 개요](https://www.cursor.com/docs/cli/overview)
- [헤드리스 / print 모드](https://www.cursor.com/docs/cli/headless)

설치 후 인증·API 키는 [02-cursor-credentials.md](02-cursor-credentials.md) 를 따른다. 하네스 실행·저장소 설명은 [harness-user-guide.md](../harness-user-guide.md) 를 본다.
