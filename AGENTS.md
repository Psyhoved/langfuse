# Repository Guidelines

## Current Project Context (March 2026)
Образовательный репозиторий: интерактивный учебник по Langfuse (observability для LLM).

Ключевые артефакты:
- `langfuse_notebook.ipynb` — основной учебный ноутбук
- `docker-compose.yml` — локальный Langfuse (Langfuse + Postgres + Redis)
- `requirements.txt` — зависимости Python
- `data/` — учебные документы для RAG-инструмента агента

## Project Structure & Module Organization

```
├── langfuse_notebook.ipynb   # Главный артефакт
├── docker-compose.yml        # Инфраструктура
├── data/                     # RAG-документы
├── docs/plans/               # Планы реализации
├── test_notebook.py          # Валидация ноутбука
└── run_cells.py              # Запуск ячеек
```

## Build, Run, and Development Commands

Окружение:
- `python -m venv .venv`
- `.\.venv\Scripts\Activate.ps1`
- `pip install -r requirements.txt`

Langfuse:
- `docker compose up -d` — запуск
- `docker compose down` — остановка
- `docker compose down -v` — остановка с удалением данных

Ноутбук:
- `jupyter notebook langfuse_notebook.ipynb`

Валидация:
- `python -m json.tool langfuse_notebook.ipynb > /dev/null`
- `python test_notebook.py`
- `python -m pip check`

## Coding Style & Naming Conventions

Python:
- 4-space indentation
- `snake_case` для файлов, функций, переменных
- `PascalCase` для классов
- Явные, описательные имена
- UTF-8 кодировка

## Testing Guidelines

- `test_notebook.py` — валидация структуры (10 разделов, порядок секций)
- `run_cells.py` — запуск отдельных ячеек для проверки
- `python -m json.tool langfuse_notebook.ipynb` — JSON-валидность

## Commit & PR Guidelines

Conventional Commits:
- `feat: add scoring section to notebook`
- `fix: correct OpenRouter model selection`
- `docs: update README with new API keys`
