"""Просмотр и информация о ячейках ноутбука.

Использование:
    python run_cells.py --list      # показать список ячеек
    python run_cells.py --info 5    # подробная информация о ячейке 5
    python run_cells.py --stats     # статистика ноутбука
"""

import json
import sys
from pathlib import Path


NOTEBOOK_PATH = Path("langfuse_notebook.ipynb")


def load_notebook():
    with NOTEBOOK_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def list_cells():
    nb = load_notebook()
    for i, cell in enumerate(nb["cells"]):
        cell_type = cell["cell_type"]
        source = "".join(cell.get("source", []))
        preview = source.strip().split("\n")[0][:80] if source.strip() else "(empty)"
        marker = "MD" if cell_type == "markdown" else "PY"
        print(f"  [{i:>3}] [{marker}] {preview}")


def show_info(index):
    nb = load_notebook()
    total = len(nb["cells"])

    if index >= total:
        print(f"Cell {index} does not exist (total: {total})")
        return

    cell = nb["cells"][index]
    source = "".join(cell.get("source", []))

    print(f"Cell {index} ({cell['cell_type']})")
    print(f"Lines: {len(source.splitlines())}")
    print(f"Characters: {len(source)}")
    print("-" * 60)
    print(source)


def show_stats():
    nb = load_notebook()
    total = len(nb["cells"])
    markdown = sum(1 for c in nb["cells"] if c["cell_type"] == "markdown")
    code = sum(1 for c in nb["cells"] if c["cell_type"] == "code")

    print(f"Total cells: {total}")
    print(f"  Markdown: {markdown}")
    print(f"  Code: {code}")

    # Count sections
    import re
    sections = 0
    for cell in nb["cells"]:
        if cell["cell_type"] == "markdown":
            source = "".join(cell.get("source", []))
            for line in source.splitlines():
                if re.match(r"^#\s+Раздел\s+\d+", line.strip()):
                    sections += 1
                    break
    print(f"  Sections: {sections}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--list":
        list_cells()
    elif sys.argv[1] == "--info" and len(sys.argv) > 2:
        show_info(int(sys.argv[2]))
    elif sys.argv[1] == "--stats":
        show_stats()
    else:
        print(__doc__)
