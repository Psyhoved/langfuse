# План: Интерактивный учебник по Langfuse

## Контекст

Это третий учебник в серии для обучения LLM-инженеров (после `common_ai_agents` с RAG/агентами). Фокус — **наблюдаемость (observability) LLM-приложений** через Langfuse с уклоном в AI Safety и LLMSecOps. Главный объект — ИИ-агент (OpenRouter LLM) с двумя инструментами: RAG-search и Web-search, который постепенно обрастает трассировкой, оценкой и мониторингом безопасности.

## Архитектура проекта

Следуем паттерну `common_ai_agents` — **один Jupyter-ноутбук** как главный артефакт + вспомогательные скрипты:

```
D:/work/study/y_practicum/langfuse/
├── langfuse_notebook.ipynb      # Главный артефакт (~160-180 ячеек)
├── docker-compose.yml           # Локальный Langfuse (Langfuse + Postgres + Redis)
├── requirements.txt             # Зависимости Python
├── README.md                    # Быстрый старт (RU)
├── AGENTS.md                    # Правила для Claude Code
├── .env.example                 # Шаблон API-ключей
├── .gitignore                   # .env, __pycache__, .ipynb_checkpoints
├── data/                        # Учебные документы для RAG (3-5 .txt файлов)
│   ├── llm_observability.txt    # Основы наблюдаемости LLM
│   ├── ai_safety_basics.txt     # Основы AI Safety
│   ├── prompt_injection.txt     # Виды prompt injection атак
│   ├── llmsecops_practices.txt  # Практики LLMSecOps
│   └── langfuse_overview.txt    # Обзор возможностей Langfuse
├── test_notebook.py             # Валидация структуры
├── run_cells.py                 # Запуск отдельных ячеек
└── docs/
    └── plans/
        └── 2026-03-16-langfuse-tutorial.md  # Копия плана
```

**RAG-данные:** В проекте создаётся папка `data/` с небольшим набором учебных текстовых документов по теме LLM observability и AI safety (3-5 файлов .txt/.md). Это формальный RAG для обучения — содержание документов подобрано так, чтобы агент мог демонстрировать поиск по базе знаний.

## Зависимости (requirements.txt)

```
# Langfuse SDK
langfuse>=2.56.0

# LLM через OpenRouter (OpenAI-совместимый API)
langchain>=1.2.10,<1.3.0
langchain-community>=0.4.0,<0.5.0
langchain-openai>=1.0.0,<1.2.0
langgraph>=1.0.8,<1.1.0
openai>=1.60.0

# RAG-компоненты
langchain-huggingface>=1.2.0,<1.3.0
faiss-cpu>=1.8.0
sentence-transformers>=5.2.0,<5.3.0

# Web-search
duckduckgo-search>=6.0.0

# Notebook и визуализация
jupyter>=1.0.0
ipywidgets>=8.1.0
matplotlib>=3.9.0
pandas>=2.2.0
numpy>=2.0.0
seaborn>=0.13.0

# Утилиты
python-dotenv>=1.0.0
tqdm>=4.66.0
```

## Docker Compose (локальный Langfuse)

Основной сценарий — **локальный Langfuse** через Docker Compose. Файл `docker-compose.yml` включает:
- **langfuse** (web + API) на порту 3000
- **postgres** (хранилище) на порту 5432
- **redis** (кэш/очереди)

Запуск: `docker compose up -d`, затем открыть http://localhost:3000, создать проект, получить ключи.

Облачный вариант (cloud.langfuse.com) упомянут кратко как альтернатива, без детального разбора.

## API-ключи (.env.example)

```bash
OPENROUTER_API_KEY=sk-or-...

# Локальный Langfuse (основной сценарий)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=http://localhost:3000

# Альтернатива: облачный Langfuse
# LANGFUSE_HOST=https://cloud.langfuse.com
```

## Структура ноутбука (10 разделов)

### Раздел 1: Введение в Langfuse и наблюдаемость LLM (~15 ячеек)
- **Теория:** Зачем наблюдаемость, обзор Langfuse, иерархия Trace→Span→Generation→Event
- **Код:**
  - Запуск локального Langfuse через docker-compose (инструкция + проверка)
  - pip install, загрузка .env, `Langfuse()`, `auth_check()`
  - Динамический выбор бесплатной модели OpenRouter (паттерн из common_ai_agents)
  - Первый тестовый LLM-вызов
- **Упражнение:** Поднять локальный Langfuse, сделать тестовый вызов, найти трассировку в UI (http://localhost:3000)
- **LLMSecOps:** API-ключи только в .env, .gitignore
- **Примечание:** Кратко упомянуть cloud.langfuse.com как альтернативу для тех, у кого нет Docker

### Раздел 2: Декоратор @observe() — первые трассировки (~16 ячеек)
- **Теория:** Как `@observe()` автоматически строит дерево трассировок
- **Код:** Простые и вложенные функции с `@observe()`, `langfuse_context.update_current_observation()`, `flush()`
- **Упражнение:** 3-уровневая цепочка функций, анализ узких мест по метаданным
- **LLMSecOps:** user_id и session_id для аудита

### Раздел 3: Spans, Generations и Events — детальная трассировка (~16 ячеек)
- **Теория:** Разница между Span/Generation/Event, ручное vs автоматическое создание, подсчёт токенов
- **Код:** Low-level API (`trace.span()`, `span.generation()`), `@observe(as_type="generation")`, usage tracking
- **Визуализация:** DataFrame из `fetch_traces()` — стоимость, латентность
- **Упражнение:** Вручную инструментировать RAG-пайплайн (retrieve + generate)
- **LLMSecOps:** Мониторинг стоимости, детекция аномальных всплесков

### Раздел 4: OpenAI Wrapper и интеграция с OpenRouter (~14 ячеек)
- **Теория:** Drop-in обёртка `from langfuse.openai import OpenAI`, автотрассировка
- **Код:** OpenAI клиент с OpenRouter base_url, streaming с трассировкой, сравнение с LangChain
- **Визуализация:** Распределение латентности моделей (matplotlib)
- **Упражнение:** Сравнить стоимость 3 моделей OpenRouter на одном наборе промптов
- **LLMSecOps:** Логирование использования моделей

### Раздел 5: Prompt Management — версионирование и переменные (~16 ячеек)
- **Теория:** Централизованное управление промптами, версии, метки (production/staging), переменные `{{var}}`
- **Код:** `create_prompt()`, `get_prompt()`, `compile()`, привязка промпта к generation
- **Упражнение:** A/B-тест 3 версий системного промпта на 5 вопросах
- **LLMSecOps:** Аудит изменений промптов, защита от prompt injection через управляемые промпты

### Раздел 6: Оценка и скоринг — качество LLM (~18 ячеек)
- **Теория:** Типы скоров (numeric, categorical, boolean), ручная vs автоматическая оценка
- **Код:** `score_current_trace()`, простые эвалюаторы (релевантность, PII-детекция, токсичность)
- **Визуализация:** Heatmap скоров, временной ряд средней оценки
- **Упражнение:** 3-эвалюаторный пайплайн на 10 трассировках
- **LLMSecOps:** Автоматическая валидация выходов, "safety score"

### Раздел 7: Datasets и эксперименты — системное тестирование (~18 ячеек)
- **Теория:** Датасеты Langfuse, запуск экспериментов, сравнение ранов, регрессионное тестирование
- **Код:** `create_dataset()`, `create_dataset_item()`, запуск эксперимента с `item.observe()`
- **Упражнение:** 15 вопросов (нормальные + атаки), 2 варианта промптов, сравнение безопасности
- **LLMSecOps:** Систематическое тестирование на prompt injection, jailbreak, data exfiltration

### Раздел 8: Интеграция с LangChain — CallbackHandler (~18 ячеек)
- **Теория:** `CallbackHandler` — автотрассировка цепочек LangChain, сравнение подходов
- **Код:** Загрузка документов из `data/`, FAISS индекс, RAG-цепочка с retriever + CallbackHandler
- **Упражнение:** RAG-цепочка с трассировкой, анализ латентности retrieval vs generation

### Раздел 9: Трассировка ИИ-агента — инструменты, ReAct, циклы (~20 ячеек)
- **Теория:** Нелинейная трассировка агентов, циклы thought→action→observation, сессии
- **Код:**
  - Tool 1: `search_knowledge_base` (RAG по документам из `data/`)
  - Tool 2: `web_search` (DuckDuckGo)
  - `create_react_agent()` + Langfuse CallbackHandler
- **Визуализация:** Стоимость по инструментам, waterfall латентности
- **Упражнение:** 5 запросов к агенту, анализ выбора инструментов и стоимости
- **LLMSecOps:** Детекция инъекций через tool outputs, контроль runaway-циклов

### Раздел 10: Безопасность и LLMSecOps с Langfuse — финальный проект (~20 ячеек)
- **Теория:** Комплексный фреймворк LLMSecOps, фильтрация данных, алерты, аудит, compliance
- **Код:**
  - PII-фильтрация перед отправкой в Langfuse (regex: карты, email, телефоны)
  - Prompt injection detector как скорер (паттерны + пороги)
  - Дашборд мониторинга стоимости (pandas + matplotlib)
  - Safety evaluation: датасет из Р7 + агент из Р9
- **Визуализация:** Security dashboard — частота атак, тренды стоимости, PII rate, safety scores
- **Финальное упражнение:** Полный пайплайн мониторинга для агента
- **LLMSecOps:** Capstone всей серии — все нити безопасности сходятся

## Прогрессия сложности

| Раздел | Концепция Langfuse | Уровень | Зависит от |
|--------|-------------------|---------|------------|
| 1 | Setup, auth | Начальный | — |
| 2 | @observe() | Начальный | 1 |
| 3 | Spans, Generations, Events | Средний | 2 |
| 4 | OpenAI wrapper + OpenRouter | Средний | 1, 3 |
| 5 | Prompt Management | Средний | 4 |
| 6 | Scoring & Evaluation | Средний | 3, 4 |
| 7 | Datasets & Experiments | Продвинутый | 6 |
| 8 | LangChain CallbackHandler | Продвинутый | 3, 4 |
| 9 | Agent tracing (кульминация) | Продвинутый | 8 |
| 10 | LLMSecOps capstone | Продвинутый | Все |

## Стратегия переиспользования паттернов

Паттерны из `common_ai_agents` используются как **справочник стиля и подхода** (не прямые импорты):
- Стиль подачи: теория → код → визуализация → упражнение
- OpenRouter: динамический выбор бесплатной модели, ChatOpenAI с base_url
- FAISS: создание индекса из текстовых документов
- Tools: `@tool` декоратор LangChain для RAG и Web-search
- Agent: `create_react_agent()` из LangGraph
- Валидация ноутбука: test_notebook.py с проверкой секций

Весь код пишется заново внутри этого репозитория. RAG работает с собственными документами из `data/`.

## Порядок имплементации

1. **Инфра-файлы:** docker-compose.yml, requirements.txt, .env.example, .gitignore
2. **Документация:** README.md, AGENTS.md
3. **Ноутбук:** разделы 1-4 (Docker setup, основы Langfuse, трассировка, OpenRouter)
4. **Ноутбук:** разделы 5-7 (prompt management, scoring, datasets)
5. **Ноутбук:** разделы 8-10 (LangChain, агент, LLMSecOps capstone)
6. **Скрипты:** test_notebook.py, run_cells.py
7. **Финализация:** docs/plans/, проверка структуры

## Верификация

- `python -m json.tool langfuse_notebook.ipynb > /dev/null` — валидность JSON
- `python test_notebook.py` — все 10 разделов на месте и в порядке
- `python -m pip check` — совместимость зависимостей
- Ручная проверка: запуск ключевых ячеек (setup, LLM call, tracing)
