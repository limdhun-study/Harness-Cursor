"""TypeScript + React + TanStack Query 앱 전체 검증 게이트.

웹 앱 스캐폴드가 있을 때(하네스 또는 수동 작업 후) 실행한다:
  python scripts/validate_web_app.py

PATH에 Node.js와 npm이 있어야 한다.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON = ROOT / "package.json"

REQUIRED_PACKAGES = (
    "react",
    "react-dom",
    "@tanstack/react-query",
    "typescript",
)

IGNORED_DIRS = {
    ".git",
    ".cursor",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".next",
    ".vite",
    "venv",
    ".venv",
}

# 소스 문자열 스캔(가벼운 게이트용; AST 아님).
REACT_QUERY_TOKENS = (
    "@tanstack/react-query",
    "QueryClient",
    "QueryClientProvider",
    "useQuery",
    "useMutation",
)


def _fail(message: str) -> None:
    print("웹 앱 검증 실패")
    print(f"- {message}")
    sys.exit(1)


def _run(cmd: list[str]) -> None:
    print(f"+ {' '.join(cmd)}", flush=True)
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        _fail(f"명령이 코드 {result.returncode}로 종료됨: {' '.join(cmd)}")


def _require_executable(name: str) -> None:
    if shutil.which(name) is None:
        _fail(f"PATH에 필요한 실행 파일이 없음: {name}")


def _load_package_json() -> dict:
    if not PACKAGE_JSON.is_file():
        _fail("저장소 루트에 package.json이 없다.")

    try:
        return json.loads(PACKAGE_JSON.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        _fail(f"package.json JSON 오류: {exc}")


def _collect_source_files() -> list[Path]:
    source_files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative_parts = set(path.relative_to(ROOT).parts)
        if relative_parts & IGNORED_DIRS:
            continue
        if path.suffix in {".ts", ".tsx"}:
            source_files.append(path)
    return sorted(source_files)


def _check_react_query_usage(source_files: list[Path]) -> None:
    haystack_parts: list[str] = []
    for path in source_files:
        try:
            haystack_parts.append(path.read_text(encoding="utf-8-sig"))
        except UnicodeDecodeError:
            _fail(f"UTF-8로 읽을 수 없는 소스: {path.relative_to(ROOT)}")

    haystack = "\n".join(haystack_parts)
    tokens = REACT_QUERY_TOKENS
    if tokens[0] not in haystack:
        _fail("소스에서 @tanstack/react-query를 import해야 한다.")

    query_client, query_provider = tokens[1], tokens[2]
    hooks = tokens[3:]
    provider_used = query_client in haystack and query_provider in haystack
    hook_used = any(token in haystack for token in hooks)
    if not provider_used:
        _fail("소스에서 QueryClient와 QueryClientProvider로 React Query를 구성해야 한다.")
    if not hook_used:
        _fail("페이지 단 비동기 흐름에 useQuery 또는 useMutation을 사용해야 한다.")


def main() -> None:
    _require_executable("node")
    _require_executable("npm")

    pkg = _load_package_json()

    scripts = pkg.get("scripts") or {}
    if "build" not in scripts:
        _fail('package.json에 "build" 스크립트가 있어야 한다.')

    deps: dict[str, str] = {}
    deps.update(pkg.get("dependencies") or {})
    deps.update(pkg.get("devDependencies") or {})
    missing = [name for name in REQUIRED_PACKAGES if name not in deps]
    if missing:
        _fail(
            "package.json dependencies 또는 devDependencies에 다음 패키지가 필요하다: "
            + ", ".join(missing)
        )

    source_files = _collect_source_files()
    if not source_files:
        _fail("TypeScript 소스(.ts 또는 .tsx)가 하나도 없다.")

    if not any(path.suffix == ".tsx" for path in source_files):
        _fail(".tsx React 컴포넌트 파일이 하나도 없다.")

    _check_react_query_usage(source_files)

    if (ROOT / "package-lock.json").is_file():
        _run(["npm", "ci"])
    else:
        _run(["npm", "install"])

    _run(["npm", "run", "build"])
    print("웹 앱 검증 통과")


if __name__ == "__main__":
    main()
