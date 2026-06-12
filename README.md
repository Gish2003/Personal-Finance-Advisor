# Personal Finance Advisor — Expert System

A rule-based expert system that classifies a user's financial health and produces a
prioritized action plan using the **Financial Order of Operations (FOO)**. The
reasoning engine is written in **SWI-Prolog**; the dashboard is a **Streamlit**
single-page app connected via **PySwip**.

> CM 2520 Deductive Reasoning and Logic Programming — coursework project.

---

## Prerequisites

- **Python 3.10+**
- **SWI-Prolog 9.x** — must be installed and on your `PATH`
  - Download: https://www.swi-prolog.org/download/stable
  - On Windows, if PySwip cannot find your install, set the `SWI_HOME_DIR`
    environment variable to your SWI-Prolog installation directory
    (e.g. `C:\Program Files\swipl`).

---

## Setup

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

# 2. Install Python dependencies
pip install -r requirements.txt
```

---

## Running the Prolog engine standalone

```bash
swipl -s prolog/finance_advisor.pl
?- start.
```

This launches the original CLI walkthrough (collects a profile interactively
and prints the full FOO report).

---

## Running the tests

### PLUnit (Prolog unit tests)

```bash
# Windows
run_tests.bat

# macOS / Linux
./run_tests.sh
```

Or run an individual suite:

```bash
swipl -g "consult('prolog/tests/test_foo_rules.pl'), run_tests, halt"
```

### pytest (Python integration tests)

```bash
pytest tests/
```

---

## Launching the dashboard

```bash
streamlit run app/streamlit_app.py
```

The app opens in your browser (default `http://localhost:8501`).

### Using the dashboard

1. Fill in the **User Profile** form in the left sidebar (age, occupation,
   income, expenses, emergency fund, investments, goal) and click
   **Submit Profile**. This resets the session KB and asserts the new facts.
2. Optionally use **Add Fact** / **Remove Fact** to assert or retract debts
   and other facts directly (e.g. `debt(user, credit_card, 50000, 24)`).
3. Click **Run Recommendation** to populate Sections 3 and 4: the composite
   health badge, FOO gate pills, key metrics, and ranked recommendations.
4. Click **Explain Result** to expand the full derivation trace in
   Section 4.
5. Use **Show Knowledge Base** / **Show Dynamic Facts** as a pointer to the
   relevant tab in Section 2 (Knowledge Base Viewer), which always shows the
   current static rules and session facts.
6. Use the **Custom Prolog Query** box (or the example-query buttons) to run
   read-only queries against the engine — results and timing appear in the
   Query Console (Section 5).

---

## Project Structure

See [`CLAUDE.md`](CLAUDE.md) for the full architecture, domain model, and
predicate reference.

```
prolog/      Prolog knowledge base, rules, and PLUnit tests
app/         Streamlit dashboard + PySwip integration layer
tests/       pytest integration tests
```

---

## Screenshots

_Placeholders — to be added after running the dashboard:_

- `docs/screenshots/overview.png` — Knowledge Base Overview (Section 1)
- `docs/screenshots/viewer.png` — Knowledge Base Viewer (Section 2)
- `docs/screenshots/inference.png` — Inference Results (Section 3)
- `docs/screenshots/explanation.png` — Explanation Panel (Section 4)
- `docs/screenshots/console.png` — Prolog Query Console (Section 5)

