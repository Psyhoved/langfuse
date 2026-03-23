# Langfuse Notebook Hardening Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the teaching notebook reproducible and safer for students by hardening setup, stabilizing model selection, fixing experiment logic, and reducing rerun-related confusion.

**Architecture:** Keep the existing tutorial structure and cell order, but patch the riskiest cells in place. Add lightweight content guards in the notebook itself, extend the repository validation script with notebook-content assertions, and align README/requirements with the actual runtime expectations.

**Tech Stack:** Jupyter notebook JSON, Python validation scripts, Langfuse Python SDK, LangChain/OpenRouter stack.

---

### Task 1: Add regression checks for notebook hardening

**Files:**
- Modify: `test_notebook.py`

**Step 1: Write failing content checks**

Add assertions for:
- fail-fast env validation in setup cells
- stable install command (`pip install -r requirements.txt`)
- no brittle `free_models[0]` selection
- safe trace DataFrame initialization
- compiled v2 prompt usage in experiments
- English refusal markers in `check_refusal`
- deterministic dataset item ids

**Step 2: Run validation to verify it fails**

Run: `python -X utf8 test_notebook.py`

Expected: FAIL on current notebook content.

**Step 3: Keep the new checks minimal and notebook-oriented**

Avoid execution-heavy checks; validate content and structure only.

**Step 4: Re-run after notebook fixes**

Run the same command and verify all checks pass.

### Task 2: Harden notebook setup and model selection

**Files:**
- Modify: `langfuse_notebook.ipynb`

**Step 1: Fix bootstrap cells**

Patch the setup cells to:
- use `pip install -r requirements.txt`
- validate all required env vars
- stop execution with a clear `RuntimeError` when prerequisites are missing
- stop when Langfuse auth fails

**Step 2: Stabilize model selection**

Replace alphabetical “first free model” selection with:
- optional env override(s)
- curated preferred free-model order
- capability-aware selection for the agent/tool-calling section

**Step 3: Run notebook validation**

Run: `python -m json.tool langfuse_notebook.ipynb > $null`

Expected: exit 0.

### Task 3: Fix experiment logic and rerun behavior

**Files:**
- Modify: `langfuse_notebook.ipynb`

**Step 1: Make trace analysis cells safe on empty data**

Initialize empty DataFrames before conditional fetch handling.

**Step 2: Make prompt management deterministic**

Replace fixed-version assumptions with label-based or ensured prompt retrieval so reruns stay understandable.

**Step 3: Make datasets idempotent**

Reuse or create the dataset safely and assign deterministic dataset item ids to avoid duplicate accumulation on reruns.

**Step 4: Fix experiment scoring**

Align safety evaluation with expected outcomes:
- refusal-based for `ОТКАЗ`
- no-PII-based for `БЕЗ_PII`
- add English refusal handling
- compile prompt templates before use

### Task 4: Align repository docs and dependencies

**Files:**
- Modify: `README.md`
- Modify: `requirements.txt`

**Step 1: Tighten environment guidance**

Document supported Python versions, external services, and first-run network/download expectations.

**Step 2: Align dependency declarations**

Add directly imported packages that are currently only available transitively.

**Step 3: Re-run validation and summarize residual limits**

Run:
- `python -m json.tool langfuse_notebook.ipynb > $null`
- `python -X utf8 test_notebook.py`

Expected: both pass.
