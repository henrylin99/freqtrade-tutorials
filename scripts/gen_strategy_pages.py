#!/usr/bin/env python3
"""Generate browsable strategy-code pages for the MkDocs site.

Converts every user_data/strategies/*.py into docs/zh/strategies/<Name>.md
(markdown page with a highlighted python code block), plus an index page
linking to each. Run before `mkdocs build` in CI; output is gitignored.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "user_data" / "strategies"
OUT = REPO / "docs" / "zh" / "strategies"
REPO_URL = "https://github.com/henrylin99/freqtrade-tutorials/blob/main"

# strategies whose class name we surface as the page title
SKIP_FILES = {"__init__.py"}


def first_strategy_class(code: str, fallback: str) -> str:
    for line in code.splitlines():
        if line.startswith("class ") and line.endswith("IStrategy):"):
            return line[len("class "):line.index("(")].strip()
    return fallback


def main() -> int:
    if not SRC.is_dir():
        print(f"strategy dir not found: {SRC}", file=sys.stderr)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)

    index_links = []
    for py in sorted(SRC.glob("*.py")):
        if py.name in SKIP_FILES or py.name.startswith("_"):
            continue
        code = py.read_text(encoding="utf-8", errors="replace")
        name = first_strategy_class(code, py.stem)
        page = OUT / f"{py.stem}.md"
        page.write_text(
            f"# 策略代码：{name}\n\n"
            f"> 源文件：[`user_data/strategies/{py.name}`]({REPO_URL}/user_data/strategies/{py.name})\n\n"
            f"```python\n{code}\n```\n",
            encoding="utf-8",
        )
        index_links.append(f"- [{name}]({py.stem}.md) — `{py.name}`")
        print(f"generated {page}")

    (OUT / "index.md").write_text(
        "# 策略代码\n\n"
        "以下策略随仓库维护，可直接用于回测学习（详见各课教程）。"
        "点击查看完整源码：\n\n" + "\n".join(index_links) + "\n",
        encoding="utf-8",
    )
    print(f"index written, {len(index_links)} strategies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
