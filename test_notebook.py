import json
import re
import sys
from pathlib import Path


NOTEBOOK_PATH = Path("langfuse_notebook.ipynb")
README_PATH = Path("README.md")
REQUIREMENTS_PATH = Path("requirements.txt")

EXPECTED_TOP_LEVEL_SECTIONS = [
    ("Раздел 1", r"^#\s+Раздел 1:"),
    ("Раздел 2", r"^#\s+Раздел 2:"),
    ("Раздел 3", r"^#\s+Раздел 3:"),
    ("Раздел 4", r"^#\s+Раздел 4:"),
    ("Раздел 5", r"^#\s+Раздел 5:"),
    ("Раздел 6", r"^#\s+Раздел 6:"),
    ("Раздел 7", r"^#\s+Раздел 7:"),
    ("Раздел 8", r"^#\s+Раздел 8:"),
    ("Раздел 9", r"^#\s+Раздел 9:"),
    ("Раздел 10", r"^#\s+Раздел 10:"),
]


def load_notebook():
    with NOTEBOOK_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def cell_source(cell):
    source = cell.get("source", [])
    return "".join(source) if isinstance(source, list) else source


def extract_headings(nb):
    headings = []
    for cell in nb["cells"]:
        if cell["cell_type"] != "markdown":
            continue
        for line in cell_source(cell).splitlines():
            line = line.strip()
            if re.match(r"^#{1,6}\s+", line):
                headings.append(line)
    return headings


def find_code_cell(nb, needle):
    for index, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        source = cell_source(cell)
        if needle in source:
            return index, source
    return None, None


def require(condition, ok_message, fail_message):
    if condition:
        print(f"[OK] {ok_message}")
        return True

    print(f"[FAIL] {fail_message}")
    return False


def validate_structure(nb):
    assert "cells" in nb, "No cells found"
    assert nb["nbformat"] == 4, "Wrong notebook format"

    total = len(nb["cells"])
    markdown = sum(1 for c in nb["cells"] if c["cell_type"] == "markdown")
    code = sum(1 for c in nb["cells"] if c["cell_type"] == "code")
    headings = extract_headings(nb)

    print("[INFO] Notebook structure:")
    print(f"    Total cells: {total}")
    print(f"    Markdown: {markdown}")
    print(f"    Code: {code}")
    print(f"    Headings: {len(headings)}")

    resolved_sections = []
    missing_sections = []
    for label, pattern in EXPECTED_TOP_LEVEL_SECTIONS:
        match = next((heading for heading in headings if re.match(pattern, heading)), None)
        if match is None:
            missing_sections.append(label)
        else:
            resolved_sections.append((label, match))

    if missing_sections:
        print("[FAIL] Missing top-level sections:")
        for section in missing_sections:
            print(f"    - {section}")
        return False

    section_positions = [headings.index(match) for _, match in resolved_sections]
    if section_positions != sorted(section_positions):
        print("[FAIL] Top-level sections are out of order")
        for (label, match), position in zip(resolved_sections, section_positions):
            print(f"    {position:>3} {label} -> {match}")
        return False

    print("[OK] All expected top-level sections are present and ordered")
    return True


def validate_hardening(nb):
    success = True

    install_index, install_cell = find_code_cell(nb, "!pip install")
    success &= require(
        install_cell is not None and "-r requirements.txt" in install_cell,
        "Bootstrap cell installs from requirements.txt",
        f"Bootstrap cell should install from requirements.txt, found code cell {install_index}",
    )

    setup_index, setup_cell = find_code_cell(nb, "required_env = {")
    success &= require(
        setup_cell is not None
        and '"OPENROUTER_API_KEY"' in setup_cell
        and '"LANGFUSE_PUBLIC_KEY"' in setup_cell
        and '"LANGFUSE_SECRET_KEY"' in setup_cell
        and "raise RuntimeError" in setup_cell,
        "Setup cell validates all required env vars and fails fast",
        f"Setup cell {setup_index} should validate all required env vars and raise RuntimeError on missing config",
    )

    model_index, model_cell = find_code_cell(nb, "def fetch_openrouter_free_models")
    success &= require(
        model_cell is not None and 'free_models[0]["id"]' not in model_cell,
        "Model selection avoids brittle first-free-model behavior",
        f"Model-selection cell {model_index} still picks the first free model directly",
    )

    traces_index, traces_cell = find_code_cell(nb, "traces = langfuse.fetch_traces(limit=20)")
    success &= require(
        traces_cell is not None and "df = pd.DataFrame()" in traces_cell,
        "Trace-analysis cell initializes an empty DataFrame safely",
        f"Trace-analysis cell {traces_index} should initialize df before conditional fetch logic",
    )

    refusal_index, refusal_cell = find_code_cell(nb, "def check_refusal")
    lowered_refusal = refusal_cell.lower() if refusal_cell else ""
    success &= require(
        refusal_cell is not None
        and (
            "can't help" in lowered_refusal
            or "cannot help" in lowered_refusal
            or "can't assist" in lowered_refusal
            or "cannot assist" in lowered_refusal
        ),
        "Refusal detector handles English refusals",
        f"Refusal detector in code cell {refusal_index} should recognize common English refusal patterns",
    )

    v2_index, v2_cell = find_code_cell(nb, 'run_name_v2 = "safety-prompt-v2"')
    success &= require(
        v2_cell is not None and "prompt_v2.prompt" not in v2_cell and ".compile(" in v2_cell,
        "Experiment v2 compiles the managed prompt before use",
        f"Experiment v2 cell {v2_index} should compile the prompt instead of sending raw template text",
    )

    dataset_items_index, dataset_items_cell = find_code_cell(nb, "langfuse.create_dataset_item(")
    success &= require(
        dataset_items_cell is not None and "id=" in dataset_items_cell,
        "Dataset items use deterministic ids for rerun safety",
        f"Dataset-item creation cell {dataset_items_index} should assign explicit ids",
    )

    ab_index, ab_cell = find_code_cell(nb, "for version in [1, 2]:")
    success &= require(
        ab_cell is None,
        "A/B section avoids fixed prompt-version assumptions",
        f"A/B test cell {ab_index} still hardcodes prompt versions [1, 2]",
    )

    return success


def validate_docs():
    success = True
    readme = README_PATH.read_text(encoding="utf-8")
    requirements = REQUIREMENTS_PATH.read_text(encoding="utf-8")

    success &= require(
        "Python 3.10+" not in readme
        and ("Python 3.10-3.12" in readme or "Python 3.10–3.12" in readme),
        "README narrows supported Python versions",
        "README should state a tested Python range instead of 'Python 3.10+'",
    )

    success &= require(
        "langchain-core" in requirements and "langchain-text-splitters" in requirements,
        "Requirements declare directly imported LangChain packages",
        "requirements.txt should include direct dependencies langchain-core and langchain-text-splitters",
    )

    return success


def validate_notebook():
    nb = load_notebook()
    structure_ok = validate_structure(nb)
    hardening_ok = validate_hardening(nb)
    docs_ok = validate_docs()
    return structure_ok and hardening_ok and docs_ok


if __name__ == "__main__":
    success = validate_notebook()
    sys.exit(0 if success else 1)
