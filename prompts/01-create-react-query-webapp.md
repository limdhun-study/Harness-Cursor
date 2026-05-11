# 에이전트 작업: TypeScript + React Query 웹 앱

이 저장소는 **Cursor CLI 헤드리스 하네스**(`scripts/harness_cli_loop.py`)와 **`python scripts/validate.py`** 를 사용한다. **현재 저장소 안에서만** 작업한다.

## 먼저 읽을 파일

- `AGENTS.md`
- `docs/forAgents/harness-policy.md`
- `.cursor/rules`
- `.cursor/skills/harness-engineering/SKILL.md`(있으면)

## 목표

**TypeScript** 기반 React 앱을 구현한다. 페이지 단 비동기 데이터는 **TanStack Query(React Query)** 로 처리한다.

## 기능

- 좌측 **탭** 레이아웃. 최소 다음 탭:
  - 대시보드
  - 글 목록
  - 설정
- **글 목록**에서 게시글 **CRUD** 가능.
- 게시글 필드 최소: **제목**, **본문**, **댓글**.
- **댓글**: 좋아요, 답글, 필요 시 중첩 답글.
- 백엔드가 없으면 저장소 **내부 mock 비동기 API** 를 만든다.

## 구현 기준

- TypeScript, React, `@tanstack/react-query`.
- **`QueryClient`** 와 **`QueryClientProvider`** 구성.
- 게시글·댓글 흐름에 **`useQuery`** / **`useMutation`** 사용.
- 런타임에 **외부 CDN** 사용 금지.
- 루트 **`package.json`** 에 의존성 선언, **`dev`**·**`build`** 스크립트 제공(Vite 가능).

## 검증

구현 후:

```bash
python scripts/validate.py --web-app
```

## 보고 형식

[변경 파일]

- …

[검증 명령]

```bash
python scripts/validate.py --web-app
```

[결과] PASS 또는 FAIL

[FAIL인 경우] 하네스 다음 라운드에 넣을 원인과 구체적 수정안.
