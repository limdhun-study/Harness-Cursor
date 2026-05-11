"""공식 하네스 검증 진입점.

기본 모드는 이 저장소의 Python 하네스 스크립트·설정 파일을 검사한다(웹 앱 스캐폴드 없이 CI 통과용).

TypeScript + React + TanStack Query + npm 빌드 전체 게이트:
  python scripts/validate.py --web-app
  (동일: python scripts/validate_web_app.py)
"""

from __future__ import annotations

import argparse
import compileall
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

REQUIRED_FILES = (
    SCRIPTS / "validate.py",
    SCRIPTS / "harness_cli_loop.py",
    SCRIPTS / "validate_web_app.py",
    SCRIPTS / "harness.py",
    ROOT / "harness.config.json",
    ROOT / ".env.example",
    ROOT / "AGENTS.md",
    ROOT / "docs" / "forAgents" / "README.md",
    ROOT / "docs" / "forAgents" / "harness-policy.md",
    ROOT / "docs" / "forUser" / "harness-user-guide.md",
    ROOT / "docs" / "forUser" / "SettingGuide" / "01-cli-install.md",
    ROOT / "docs" / "forUser" / "SettingGuide" / "02-cursor-credentials.md",
)


def _fail(message: str) -> None:
    print("검증 실패")
    print(f"- {message}")
    sys.exit(1)


def _run_harness_gate() -> None:
    for path in REQUIRED_FILES:
        if not path.is_file():
            _fail(f"필수 파일 없음: {path.relative_to(ROOT)}")

    cfg_path = ROOT / "harness.config.json"
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        _fail(f"harness.config.json JSON 오류: {exc}")

    ac = cfg.get("agent_command", "agent")
    if not isinstance(ac, str) or not ac.strip():
        _fail('harness.config.json: "agent_command"는 비어 있지 않은 문자열이어야 한다.')
    if ac != "agent":
        _fail('harness.config.json: 커밋 기본값으로 "agent_command"가 "agent"이어야 한다.')
    if cfg.get("workspace_relative", ".") != ".":
        _fail('harness.config.json: 저장소 기본 클론용으로 "workspace_relative"는 "."이어야 한다.')
    if cfg.get("web_app_validate") is not False:
        _fail('harness.config.json: 안전 기본값으로 "web_app_validate"는 false여야 한다.')
    max_r = cfg.get("max_rounds", 3)
    if not isinstance(max_r, int) or max_r < 1 or max_r > 50:
        _fail('harness.config.json: "max_rounds"는 1~50 정수여야 한다.')

    ok = True
    for py in sorted(SCRIPTS.glob("*.py")):
        if not compileall.compile_file(str(py), ddir=str(py.relative_to(ROOT)), quiet=1):
            ok = False
    if not ok:
        _fail("scripts/ 아래 하나 이상의 Python 파일 컴파일에 실패했다.")

    print("검증 통과(하네스 프로젝트 게이트)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Harness-Cursor 검증.")
    parser.add_argument(
        "--web-app",
        action="store_true",
        help="웹 앱 전체 게이트(Node, npm, package.json, React Query, npm run build).",
    )
    args = parser.parse_args()

    if args.web_app:
        web = SCRIPTS / "validate_web_app.py"
        proc = subprocess.run([sys.executable, str(web)], cwd=ROOT)
        raise SystemExit(proc.returncode)

    _run_harness_gate()


if __name__ == "__main__":
    main()
