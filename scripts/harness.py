"""통합 진입: 검증과 Cursor CLI 하네스 루프."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

DISPATCH = {
    "validate": "validate.py",
    "loop": "harness_cli_loop.py",
}


def main() -> None:
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(
            "사용법: python scripts/harness.py <validate|loop> [인자...]\n"
            "  validate — python scripts/validate.py 와 동일\n"
            "  loop     — harness_cli_loop.py (헤드리스 Cursor CLI + 검증 라운드)\n"
            "예:\n"
            "  python scripts/harness.py validate\n"
            "  python scripts/harness.py validate --web-app\n"
            "  python scripts/harness.py loop\n"
            "  python scripts/harness.py loop --config 팀용설정.json\n",
            end="",
        )
        sys.exit(0 if argv else 2)

    cmd = argv[0]
    if cmd not in DISPATCH:
        print(f"알 수 없는 명령: {cmd}", file=sys.stderr)
        print("도움말: python scripts/harness.py --help", file=sys.stderr)
        sys.exit(2)

    script = SCRIPTS / DISPATCH[cmd]
    proc = subprocess.run([sys.executable, str(script)] + argv[1:], cwd=ROOT)
    raise SystemExit(proc.returncode)


if __name__ == "__main__":
    main()
