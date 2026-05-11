# Cursor 자격 증명(CLI 헤드리스)

**비밀값은 저장소에 커밋하지 않는다.** 로컬 **`.env`**(gitignore) 또는 셸 환경 변수를 사용한다. 이름·더미값만 공유할 때는 루트 **`.env.example`** 을 본다.

CLI 설치는 [01-cli-install.md](01-cli-install.md) 를 따른다. 아래는 **Windows PowerShell** 과 **Linux/macOS 셸** 기준이다.

---

## Windows PowerShell (네이티브 CLI)

### 방법 A: `agent login`(권장)

```powershell
agent login
```

브라우저 안내에 따라 Cursor 계정으로 로그인한다.

### 방법 B: 환경 변수

```powershell
$env:CURSOR_API_KEY = "여기에_키"
```

Worker 예시(저장소 루트에서):

```powershell
cd C:\path\to\Harness-Cursor
agent worker start --worker-dir .
```

명령줄에 키를 넣으면 **PowerShell 기록 등에 남을 수 있어** 가능하면 **방법 A** 또는 루트 **`.env`** 를 쓴다.

---

## Linux / macOS (Unix 셸)

```bash
export CURSOR_API_KEY="여기에_키"
```

대화형 로그인:

```bash
agent login
```

---

## API 키(스크립트·CI·하네스)

1. [cursor.com](https://cursor.com) 에 로그인한다.
2. **설정(Settings)** → **API keys**(예: [cursor.com/settings](https://cursor.com/settings))로 이동한다.
3. 조직 정책이 허용하면 자동화용 키를 발급한다.

비대화형 환경에서 `harness_cli_loop.py` 를 돌리기 전에 인증 정보를 둔다.

**저장소 루트 `.env`(권장, 커밋 금지):** 루프 시작 시 **`harness_cli_loop.py`** 가 루트 `.env`의 `KEY=VALUE`를 읽어, **아직 설정되지 않은** 키만 `os.environ`에 넣는다. 자식 `agent` 프로세스가 같은 환경을 상속한다.

---

## 로그인과 키가 함께 있을 때

**`CURSOR_API_KEY`** 와 로그인이 동시에 있으면 제품이 키를 우선할 수 있다. 최신 Cursor CLI 문서를 참고한다.

---

## 다음 단계

- [harness-user-guide.md](../harness-user-guide.md) — `validate`·`loop` 실행과 저장소 파일 설명.
