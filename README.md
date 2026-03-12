# 🛡️ Financial Integrity Ecosystem - Test Automation Framework

A robust, multi-layered End-to-End (E2E) test automation framework designed for a Financial Expense Tracker application. 
This project goes beyond standard UI testing by validating **Data Integrity** and **ACID principles** across the Web, Mobile, API, and Database layers.

## 🌟 Project Overview

In financial systems, a `200 OK` status or a successful UI click is not enough. This framework ensures that every action (like adding an expense) reflects correctly and consistently inside the underlying Database. 

**Key Highlights:**
* **Multi-Platform:** Covers Web (Desktop browsers), Mobile (Android Native), and API interfaces.
* **Data Integrity Validations:** Uses advanced mathematical concepts (like **Set Theory** and Aggregations) in Python to validate DB consistency.
* **Data-Driven Testing (DDT):** Seamlessly injects test data from `CSV` and `JSON` files.
* **Design Patterns:** Implements Page Object Model (POM) and modular Action/Verification extensions for highly maintainable code.

## 🛠️ Tech Stack & Tools

* **Language:** Python 3
* **Test Runner:** Pytest
* **Web Automation:** Playwright (Fast, Auto-waiting)
* **Mobile Automation:** Appium (UiAutomator2)
* **API Testing:** Python `requests` (with Session pooling)
* **Database:** SQLite3 (Direct SQL DQL/DML executions)
* **Reporting:** Allure Reports (Rich visual reports with screenshots on failure)

## 🏗️ Architecture

The framework is built with a clear separation of concerns:
```text
├── config/             # Environment configurations and DB paths
├── data/               # Test data (CSV, JSON for DDT)
├── extensions/         # Custom wrappers (APIActions, DBActions, Verifications)
├── page_objects/       # Web & Mobile UI Elements (POM)
├── tests/              # Pytest test classes (api/, db/, mobile/, web/, e2e/)
├── utils/              # Helper functions (CSV/JSON readers)
└── workflows/          # Business logic combining UI/API steps

```

## 🧠 The "Data Integrity" Approach

One of the core features of this framework is the way it validates Database consistency. Instead of looping through UI elements, we use **Python's Set Theory (`new_set - old_set`)** combined with SQL Aggregations:

1. **Pre-condition:** Fetch total sum and current records set from the DB.
2. **Action:** Create a new transaction via API/UI.
3. **Post-condition:** Fetch the new total sum and new records set.
4. **Validation:** Verify the sum increased exactly by the expected amount, and extract the isolated new record using set difference to ensure no duplicates or ghosts records were created.

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* Node.js (for Appium)
* Appium Server / Appium Studio (for Mobile execution)
* Allure Commandline (for viewing reports)

### Installation

1. **Clone the repository:**
```bash
git clone [https://github.com/YourUsername/Financial-Integrity-Ecosystem.git](https://github.com/YourUsername/Financial-Integrity-Ecosystem.git)
cd Financial-Integrity-Ecosystem

```


2. **Create and activate a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```


3. **Install dependencies:**
```bash
pip install -r requirements.txt

```


4. **Install Playwright browsers:**
```bash
playwright install

```



## 🏃‍♂️ Running the Tests

Run tests by platform or layer using Pytest:

**Run Web Tests:**

```bash
pytest tests/web/

```

**Run API Tests:**

```bash
pytest tests/api/

```

**Run Mobile Tests (Ensure Appium Server & Device are ready):**

```bash
pytest tests/mobile/

```

**Run Everything & Generate Allure Results:**

```bash
pytest --alluredir=allure-results

```

## 📊 Viewing Test Reports

To view the generated Allure report with detailed steps, logs, and screenshots:

```bash
allure serve allure-results

```

## 👥 Contributors

* **[Yaniv Metuku and Eden Biru]** - Web, Mobile & Reporting Architecture, API, Database & Data Integrity Logic

---

*Built with ❤️ for true End-to-End Quality Assurance.*

```
