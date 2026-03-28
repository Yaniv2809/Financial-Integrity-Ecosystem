# Financial Integrity Ecosystem

[![gitcgr](https://gitcgr.com/badge/Yaniv2809/Financial-Integrity-Ecosystem.svg)](https://gitcgr.com/Yaniv2809/Financial-Integrity-Ecosystem)

**A multi-layered End-to-End test automation framework for a Financial Expense Tracker application, built to validate Data Integrity across Web, API, Mobile, and Database layers.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-9.0.2-0A9EDC?logo=pytest&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-1.58-2EAD33?logo=playwright&logoColor=white)
![Appium](https://img.shields.io/badge/Appium-3.x-662D91?logo=appium&logoColor=white)
![Allure](https://img.shields.io/badge/Allure-2.15-FC0?logo=allure&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-MySQL%208.0-2496ED?logo=docker&logoColor=white)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)

---

## Overview

In financial systems, a `200 OK` or a green checkbox on the UI is not enough. This framework validates that every transaction — creating, updating, or deleting an expense — reflects accurately and consistently in the underlying database.

The project covers **4 testing layers** (Web, API, Mobile, Database) with **53 automated tests**, strict design patterns, data-driven testing, and AI-powered failure analysis.

---

## Key Highlights

- **Multi-Platform Coverage** — Web (Playwright), API (requests + Flask), Mobile (Appium/UiAutomator2), Database (MySQL/SQLite)
- **Data Integrity Validation** — Set Theory (`new_set - old_set`) and SQL Aggregations to verify DB consistency
- **Data-Driven Testing (DDT)** — External CSV and JSON files with `test_id`-based filtering
- **Strict Design Patterns** — Page Object Model, Action/Verification Extensions, Workflow Orchestration
- **AI-Powered Failure Analysis** — Groq LLM analyzes test failures and suggests root causes
- **CI/CD Pipeline** — GitHub Actions with MySQL service, Allure Reports deployed to GitHub Pages

---

## Tech Stack

| Category | Tool | Version |
|----------|------|---------|
| Language | Python | 3.10+ |
| Test Runner | Pytest | 9.0.2 |
| Web Automation | Playwright | 1.58.0 |
| Mobile Automation | Appium + UiAutomator2 | 3.x |
| API Testing | requests | 2.32.5 |
| Backend Server | Flask | 3.x |
| API Mocking | JSON Server | latest |
| Database | MySQL 8.0 / SQLite | - |
| Containerization | Docker Compose | - |
| Reporting | Allure | 2.15.3 |
| AI Analysis | Groq API | 0.4.0+ |
| Assertions | smart-assertions | 1.0.2 |
| CI/CD | GitHub Actions | - |

---

## Architecture

```
                        +-----------------+
                        |   Test Layer    |
                        |  (Pytest + DDT) |
                        +--------+--------+
                                 |
                        +--------v--------+
                        |    Workflows    |
                        | (Orchestration) |
                        +--------+--------+
                                 |
                 +---------------+---------------+
                 |                               |
        +--------v--------+            +--------v--------+
        |     Actions      |            |  Verifications  |
        | (UI/API/Mobile)  |            |  (Assertions)   |
        +--------+---------+            +--------+--------+
                 |                               |
        +--------v--------+            +--------v--------+
        |  Page Objects    |            |   Data Layer    |
        | (Locators Only)  |            |  (CSV / JSON)   |
        +-----------------+            +-----------------+
```

Each layer has a single responsibility:
- **Page Objects** — Locator constants only (zero business logic)
- **Actions** — Reusable interactions (`click`, `fill`, `send_request`)
- **Verifications** — Assertion wrappers with Allure step reporting
- **Workflows** — Business logic combining actions into flows
- **Tests** — Scenario definitions loading external data

---

## Design Patterns

### Page Object Model (POM)
Strict separation — page objects contain only locator constants as class-level strings. No `find_element`, no `self.driver`, no business logic.

### Action / Verification Extensions
All methods are `@staticmethod` decorated with `@allure.step`. Driver or session is passed as the first parameter. Web uses Playwright auto-waiting; Mobile uses explicit `WebDriverWait`.

### Workflow Orchestration
Static workflow classes compose actions into business flows (e.g., `create_expense`, `delete_expense`). Tests call workflows, never raw actions.

### Data-Driven Testing (DDT)
Test data lives in external files — CSV for Web tests, JSON for API and Mobile tests. Each record has a `test_id` field. Tests load data via `read_data_from_csv_by_test()` or `read_json_data_by_test()`. Pytest `@parametrize` multiplies DDT tests automatically.

### Database Set Theory Validation
```python
# Pre-condition: capture current state
old_sum = SELECT SUM(amount) FROM expenses
old_set = {(id, name, amount) for each row}

# Action: create expense via UI or API

# Post-condition: capture new state
new_sum = SELECT SUM(amount) FROM expenses
new_set = {(id, name, amount) for each row}

# Validation
assert new_sum - old_sum == expected_amount
isolated_record = new_set - old_set  # Set difference
assert len(isolated_record) == 1     # Exactly one new record
```

---

## Test Coverage

| Layer | File | Tests | Key Scenarios |
|-------|------|:-----:|---------------|
| API | `test_api_expense.py` | 14 | CRUD, DDT (5 datasets), negative (missing fields, bad route, deleted ID) |
| API + DB | `test_db_api_expense.py` | 1 | API response validated against DB record |
| API E2E | `test_e2e_api_db_expense.py` | 5 | Create/update/delete reflect in DB, set theory integrity |
| Web | `test_web_expense.py` | 10 | CRUD, DDT (3 datasets), boundary, reload persistence, AI analysis |
| Web + DB | `test_db_web_expense.py` | 1 | DB-inserted record visible in Web UI |
| Web E2E | `test_e2e_web_expense.py` | 1 | Full lifecycle: create, verify, update, delete |
| Mobile | `test_mobile_expense.py` | 16 | Smoke, CRUD, DDT (4 datasets), negative, boundary, background persistence, keyboard |
| Cross-Layer E2E | `test_e2e_web_api_db.py` | 1 | Web UI extraction → API POST → DB INSERT → consistency check |
| Negative E2E | `test_e2e_negative_amount.py` | 2 | MySQL strict mode rejects negative amounts, VARCHAR(255) overflow |
| **Total** | **9 test files** | **53** | |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ (for JSON Server)
- Docker Desktop (for MySQL)
- Appium 2.x + UiAutomator2 driver (for mobile tests)
- Allure CLI (for report viewing)

### Installation

```bash
# Clone the repository
git clone https://github.com/YanivMetuku/Financial-Integrity-Ecosystem.git
cd Financial-Integrity-Ecosystem

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Database Setup

```bash
# Start MySQL via Docker
docker-compose up -d mysql

# Verify MySQL is healthy
docker ps
```

### Start Backend Servers

```bash
# Terminal 1 — JSON Server (port 3000)
npx json-server --watch json-server/db.json --port 3000

# Terminal 2 — Flask API (port 5000)
python server/app.py
```

---

## Running Tests

```bash
# Run by layer
pytest tests/web/                        # Web UI tests
pytest tests/api/                        # API tests
pytest tests/mobile/                     # Mobile tests (requires Appium + device)

# Run by marker
pytest -m web                            # All web-marked tests
pytest -m api                            # All API-marked tests
pytest -m e2e                            # All end-to-end tests
pytest -m "not mobile"                   # Everything except mobile

# Full suite with Allure reporting
pytest --alluredir=allure-results

# With AI-powered failure analysis
pytest --ai-analysis --alluredir=allure-results
```

### Viewing Allure Reports

```bash
allure serve allure-results
```

---

## CI/CD Pipeline

The project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that runs on every push and PR to `main`:

1. **Setup** — Python 3.13, Node.js 18
2. **Infrastructure** — MySQL 8.0 service container, JSON Server, Flask API
3. **Schema Init** — `data/init_mysql.sql` loaded into MySQL
4. **Test Execution** — `pytest -m "not mobile" --alluredir=allure-results --ai-analysis`
5. **Reporting** — Allure report generated and deployed to GitHub Pages (20-version history)

Mobile tests are excluded from CI (require physical device) and run locally.

---

## Project Structure

```
Financial-Integrity-Ecosystem/
├── .github/workflows/ci.yml        # GitHub Actions CI/CD pipeline
├── config/
│   └── config.json                  # Environment configs (QA, dev, production)
├── data/
│   ├── ddt/                         # DDT data files (JSON)
│   ├── e2e/                         # E2E test data
│   ├── web/expense_data.csv         # Web test data (CSV)
│   ├── mobile/                      # Mobile config & data paths
│   └── init_mysql.sql               # MySQL schema initialization
├── extensions/
│   ├── ui_actions.py                # Playwright UI interactions
│   ├── api_actions.py               # HTTP methods (GET/POST/PUT/DELETE)
│   ├── mobile_actions.py            # Appium mobile interactions
│   ├── db_actions.py                # SQL DQL/DML operations
│   ├── web_verification.py          # Web assertion wrappers
│   ├── api_verification.py          # API response assertions
│   ├── mobile_verifications.py      # Mobile element assertions
│   └── db_verifications.py          # Database assertion helpers
├── page_objects/
│   ├── web/expense_tracker_page.py  # Web UI selectors
│   └── mobile/expense_mobile_page.py # Mobile UiAutomator selectors
├── workflows/
│   ├── web/web_workflows_expense.py # Web business flows
│   ├── api/api_workflows_expense.py # API business flows
│   └── mobile/mobile_workflows.py   # Mobile business flows
├── tests/
│   ├── web/                         # Web UI test suite (3 files)
│   ├── api/                         # API test suite (3 files)
│   ├── mobile/                      # Mobile test suite (1 file)
│   ├── test_e2e_web_api_db.py       # Cross-layer E2E
│   └── test_e2e_negative_amount.py  # Negative E2E + boundary
├── server/app.py                    # Flask API backend
├── json-server/db.json              # JSON Server mock data
├── utils/
│   ├── common_ops.py                # DDT helpers (CSV/JSON readers)
│   ├── ai.py                        # AI-powered error analysis
│   └── ai_test_generator.py         # AI test case generator
├── conftest.py                      # Pytest fixtures (all layers)
├── pytest.ini                       # Pytest configuration & markers
├── docker-compose.yml               # MySQL + app services
├── Dockerfile                       # Multi-stage Docker build
├── requirements.txt                 # Python dependencies
└── .env.example                     # Environment variable template
```

---

## Allure Reports

Every test is decorated with `@allure.title`, `@allure.description`, and `@allure.severity`. Reports include:

- Step-by-step execution trace via `@allure.step`
- Screenshots captured automatically on failure
- Playwright traces for Web test debugging
- Severity classification (Blocker, Critical, Normal, Minor)
- Historical trend analysis across CI runs

---

## Contributor

**Yaniv Metuku** — Solo developer. Full design, architecture, implementation, and execution across all layers.

---

*Built for true End-to-End Quality Assurance — where data integrity matters.*
