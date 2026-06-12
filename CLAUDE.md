# CLAUDE.md

This file gives Claude Code the context it needs to develop this repository. Read it before making any change to the codebase.

---

## 1. Project Overview

**Name:** Personal Finance Advisor — Expert System
**Course:** CM 2520 Deductive Reasoning and Logic Programming (2026)
**Goal:** A rule-based expert system that classifies a user's financial health and produces a prioritized action plan using the **Financial Order of Operations (FOO)**, exposed through a Streamlit web dashboard backed by a SWI-Prolog inference engine.

The expert system covers users of any age (child, teenager, young adult, adult, middle age, elder) and adjusts its rule thresholds per age group.

---

## 2. Tech Stack

### Core Expert System
- **SWI-Prolog 9.x** — knowledge base, inference engine, FOO rules

### Web Interface
- **Python 3.10+**
- **Streamlit** — single-page dashboard

### Integration Layer
- **PySwip** — Python ↔ SWI-Prolog bridge (`pip install pyswip`)
  - Requires SWI-Prolog installed and on PATH
  - On Windows, set `SWI_HOME_DIR` if PySwip cannot find the install

### Testing
- **PLUnit** — Prolog unit tests, embedded as `:- begin_tests(...)` blocks
- **pytest** — Python integration tests for the Streamlit ↔ Prolog layer

### Development
- VS Code (recommended extensions: VSC-Prolog, Python, Pylance)
- Git + GitHub for version control
- Conventional commits (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`)

---

## 3. Repository Structure

```
personal-finance-advisor/
│
├── CLAUDE.md                       ← this file
├── README.md                       ← user-facing setup + screenshots
├── requirements.txt                ← Python deps
├── .gitignore
│
├── prolog/
│   ├── finance_advisor.pl          ← main consult file; loads modules below
│   ├── facts.pl                    ← :- dynamic declarations, static thresholds
│   ├── calculations.pl             ← totals, ratios, savings_rate, DTI
│   ├── foo_rules.pl                ← Steps 1–5 of FOO (budget → investment)
│   ├── health.pl                   ← composite financial_health/2
│   ├── recommendations.pl          ← priority-ordered recommend_step/3
│   ├── goal_advice.pl              ← goal + age-specific advice layers
│   ├── db_ops.pl                   ← assertz/retract helpers, session reset
│   └── tests/
│       ├── test_calculations.pl    ← PLUnit
│       ├── test_foo_rules.pl
│       ├── test_recommendations.pl
│       └── test_scenarios.pl       ← end-to-end profile scenarios
│
├── app/
│   ├── streamlit_app.py            ← entry point (`streamlit run app/streamlit_app.py`)
│   ├── prolog_engine.py            ← PySwip wrapper around finance_advisor.pl
│   ├── components/
│   │   ├── sidebar.py              ← control panel (input, KB mgmt, queries)
│   │   ├── kb_overview.py          ← Section 1 summary cards
│   │   ├── kb_viewer.py            ← Section 2 facts/rules table
│   │   ├── inference_panel.py      ← Section 3 recommendations + scores
│   │   ├── explanation_panel.py    ← Section 4 reasoning trace
│   │   └── query_console.py        ← Section 5 raw Prolog console
│   └── utils/
│       ├── formatting.py           ← format Prolog terms for display
│       └── state.py                ← Streamlit session_state helpers
│
└── tests/
    └── test_prolog_engine.py       ← pytest integration tests
```

**Module loading rule:** `prolog/finance_advisor.pl` is the single entry point. It must `:- consult/1` every other `.pl` file. Streamlit only ever loads `finance_advisor.pl`.

---

## 4. Domain Model

### 4.1 Dynamic Facts (asserted at runtime from the UI)

```prolog
:- dynamic user_profile/3.   % user_profile(user, Age, Occupation)
:- dynamic income/2.         % income(user, MonthlyAmount)
:- dynamic expenses/3.       % expenses(user, needs|wants, Amount)
:- dynamic debt/4.           % debt(user, Type, Amount, InterestRate)
:- dynamic savings/3.        % savings(user, Type, Amount)
:- dynamic goal/2.           % goal(user, Goal)
```

### 4.2 Static Thresholds

```prolog
high_interest_threshold(15).     % >15% APR = high-interest
savings_rate_healthy(20).        % ≥20% savings rate = healthy
savings_rate_warning(10).        % 10–19% = warning
debt_to_income_safe(40).         % DTI ≤40% = manageable
budget_needs_max(50).            % 50/30/20 rule
budget_wants_max(30).
```

### 4.3 Age Groups & Adjusted Targets

| Group        | Age   | Emergency Fund (months) | Savings Rate Target |
|--------------|-------|-------------------------|---------------------|
| child        | 0–12  | 1                       | 5%                  |
| teenager     | 13–17 | 1                       | 10%                 |
| young_adult  | 18–25 | 3                       | 15%                 |
| adult        | 26–45 | 3                       | 20%                 |
| middle_age   | 46–60 | 6                       | 25%                 |
| elder        | 61+   | 6                       | 10%                 |

---

## 5. Financial Order of Operations (FOO)

The advisor evaluates the user against these gates **in order**. Each gate must pass before the next is considered relevant. This priority is enforced with cut (`!`) in `recommendations.pl`.

1. **Budget Check** — 50/30/20 rule → `budget_status/2`, `budget_gate_passed/1`
2. **High-Interest Debt** — avalanche method targeting worst debt → `debt_status/2`, `debt_gate_passed/1`
3. **Emergency Fund** — 3–6 months of expenses (age-adjusted) → `emergency_fund_status/2`, `emergency_gate_passed/1`
4. **Savings Rate** — ≥20% of income (age-adjusted) → `savings_status/2`, `savings_gate_passed/1`
5. **Investment Readiness** — only when gates 1–4 pass → `investment_ready/1`

**Composite score:** `financial_health/2` returns one of `excellent | good | moderate | poor | critical`.

---

## 6. Key Predicates (Public API for the Streamlit Layer)

These are the predicates `prolog_engine.py` is allowed to call. Treat the rest as internal.

| Predicate                          | Purpose                                          |
|-----------------------------------|--------------------------------------------------|
| `start/0`                         | CLI demo entry (not used by Streamlit)           |
| `clear_user_data/0`               | Reset entire dynamic KB                          |
| `add_debt/3`                      | `add_debt(Type, Amount, Rate)`                   |
| `clear_debt/1`                    | Retract a paid-off debt                          |
| `update_income/1`                 | Replace income value                             |
| `update_savings/2`                | Replace a savings category                       |
| `financial_health/2`              | Composite health score                           |
| `savings_rate/2`                  | %                                                |
| `debt_to_income/2`                | %                                                |
| `net_worth/2`                     | total_savings − total_debt                       |
| `budget_status/2`                 | critical / poor / overspending_wants / warning / healthy |
| `debt_status/2`                   | debt_free / manageable / high_interest / overloaded / critical |
| `emergency_fund_status/2`         | none / partial / adequate                        |
| `savings_status/2`                | critical / low / adequate / excellent            |
| `investment_ready/1`              | Boolean gate                                     |
| `top_recommendation/2`            | Single best next action                          |
| `recommend_step/3`                | All applicable recommendations (use `findall`)   |
| `goal_advice/2`                   | Goal-conditioned advice                          |
| `age_advice/2`                    | Age-group-specific guidance                      |
| `all_debts/2`                     | List of `Type-Rate` pairs                        |

---

## 7. Streamlit Dashboard Specification

Single-page two-column layout. Use `st.set_page_config(layout="wide")`.

### 7.1 Left Sidebar — Control Panel (`components/sidebar.py`)

Implemented with `st.sidebar`. Sections in order:

1. **User Input Form** (`st.form("user_profile")`)
   - Age (number_input, 0–120)
   - Occupation (selectbox: student / employed / self_employed / retired / unemployed)
   - Monthly income (number_input)
   - Monthly needs expenses (number_input)
   - Monthly wants expenses (number_input)
   - Emergency fund balance (number_input)
   - Investment balance (number_input)
   - Goal (selectbox: buy_house / retire_early / pay_debt / education / invest / travel)
   - Submit button → calls `prolog_engine.load_profile(...)` which asserts all facts

2. **Knowledge Base Management**
   - **Add Fact** — text input for fact (e.g., `debt(user, credit_card, 50000, 24)`) + button → `engine.assertz(fact)`
   - **Remove Fact** — text input + button → `engine.retract(fact)`

3. **Quick Actions** (each a `st.button`)
   - Run Recommendation → triggers full analysis, populates Sections 3–4
   - Show Knowledge Base → populates Section 2
   - Show Dynamic Facts → filters Section 2 to dynamic only
   - Explain Result → expands Section 4 reasoning trace

4. **Custom Prolog Query Input**
   - `st.text_area` for the query
   - Run button → `engine.query(text)` → results streamed to Section 5
   - Show last 10 queries in a small history list

### 7.2 Main Dashboard Area

#### Section 1 — Knowledge Base Overview (`kb_overview.py`)
Four `st.metric` cards in a single `st.columns(4)` row:
- **Total Facts** — count of all asserted clauses
- **Total Rules** — count of static rules (parse `.pl` files at load)
- **Dynamic Facts** — count of clauses for dynamic predicates only
- **System Status** — green "Ready" / yellow "No Profile" / red "Engine Error"

#### Section 2 — Knowledge Base Viewer (`kb_viewer.py`)
- `st.tabs(["Static Rules", "Dynamic Facts", "All"])`
- Inside each tab: `st.dataframe` with columns `Predicate | Arity | Clause | Module`
- Search box (`st.text_input`) filters the table client-side

#### Section 3 — Inference Results (`inference_panel.py`)
Populated after "Run Recommendation":
- **Composite Health Badge** — colored card showing `financial_health/2`
- **FOO Gate Status** — five status pills (Budget, Debt, Emergency, Savings, Investment) each ✅ / ⚠️ / ❌
- **Key Metrics** — savings rate %, DTI %, net worth, emergency fund coverage (months)
- **Ranked Recommendations** — ordered list from `findall(S-A, recommend_step(user, S, A), L)`, sorted by step number, with the **top recommendation** highlighted

#### Section 4 — Explanation Panel (`explanation_panel.py`)
For the top recommendation, show:
- **Why this was selected** — narrative built from which gate failed first
- **Rules that succeeded** — bullet list of `gate_passed` predicates that returned true
- **Rules that failed** — bullet list of `gate_passed` predicates that returned false
- **Final classification** — composite health label + brief justification
- Use `st.expander` for the full derivation trace (call `trace`/`notrace` is optional; instead, log which `recommend_step` clause matched)

#### Section 5 — Prolog Query Console (`query_console.py`)
- Read-only output area (`st.code(..., language="prolog")`)
- Each entry shows: timestamp, query, result(s), execution time
- Built-in example buttons that auto-fill the sidebar query box:
  ```prolog
  financial_health(user, X).
  findall(S-A, recommend_step(user, S, A), L).
  top_recommendation(user, A).
  all_debts(user, L).
  ```

### 7.3 Styling
- Wide layout
- Use `st.columns` for card grids
- Color tokens: success `#22c55e`, warning `#f59e0b`, danger `#ef4444`, neutral `#64748b`
- Do not introduce a CSS framework; stick to Streamlit primitives and small inline `st.markdown` with HTML for badges only

---

## 8. PySwip Integration Layer

`app/prolog_engine.py` wraps `pyswip.Prolog` with a thin class:

```python
class FinanceEngine:
    def __init__(self, kb_path: str = "prolog/finance_advisor.pl"):
        self.prolog = Prolog()
        self.prolog.consult(kb_path)

    def load_profile(self, age, occupation, income, needs, wants,
                     emergency_fund, investment, goal): ...

    def add_debt(self, type_, amount, rate): ...
    def clear_debt(self, type_): ...
    def update_income(self, amount): ...
    def update_savings(self, type_, amount): ...
    def reset(self): ...                          # clear_user_data

    def financial_health(self) -> str: ...
    def gate_statuses(self) -> dict: ...          # all five gates
    def metrics(self) -> dict: ...                # savings_rate, dti, net_worth
    def recommendations(self) -> list[tuple[int, str]]: ...
    def top_recommendation(self) -> str: ...
    def goal_advice(self) -> str: ...
    def age_advice(self) -> str: ...

    def assert_fact(self, fact: str): ...
    def retract_fact(self, fact: str): ...
    def raw_query(self, query: str) -> list[dict]: ...
```

**Important caveats:**
- PySwip cannot run two `Prolog()` instances safely. Use a single module-level engine cached via `@st.cache_resource`.
- All asserted facts persist across Streamlit reruns until `reset()` is called.
- Wrap every `list(self.prolog.query(...))` in try/except; PySwip raises `PrologError` on bad syntax.
- Escape user-entered query strings; never `eval` or concatenate without sanitising.

---

## 9. Testing Strategy

### 9.1 PLUnit (Prolog)
Each `prolog/tests/*.pl` file follows:

```prolog
:- begin_tests(foo_rules).

test(budget_critical) :-
    clear_user_data,
    assertz(user_profile(user, 30, employed)),
    assertz(income(user, 100000)),
    assertz(expenses(user, needs, 85000)),
    assertz(expenses(user, wants, 10000)),
    budget_status(user, critical).

:- end_tests(foo_rules).
```

Run with: `swipl -g "run_tests, halt" prolog/tests/test_foo_rules.pl`

### 9.2 Required test coverage
- Each FOO gate: at least one passing and one failing case
- All four sample scenarios from the draft (child, young adult, middle-aged, elder)
- Recommendation priority — verify the top recommendation matches the expected FOO step
- Dynamic KB — assertz then retract, verify state changes

### 9.3 pytest
Test `FinanceEngine` end-to-end: load a profile, assert facts via UI methods, check returned values. Use a fresh engine per test (`@pytest.fixture`).

---

## 10. Development Workflow for Claude Code

When implementing or editing this project, follow this order:

1. **Always read this file first.** Do not guess predicate names — they are listed in §6.
2. **Prolog logic before UI.** Any new domain rule goes into the appropriate `prolog/*.pl` module and gets a PLUnit test before the Streamlit layer is touched.
3. **Keep the public API in §6 stable.** If you must change a predicate signature, update this file, `prolog_engine.py`, and the affected Streamlit component in the same commit.
4. **Never bypass the Prolog engine in the UI.** The dashboard must not encode domain logic in Python — everything goes through `FinanceEngine`.
5. **Cut discipline.** Priority ordering depends on `!` in `recommend_step/3` and the cascading `top_recommendation/2` clauses. Do not remove cuts without re-testing the scenarios.
6. **Dynamic predicates only get modified through `db_ops.pl` helpers** (`add_debt/3`, `clear_debt/1`, `update_income/1`, `update_savings/2`, `clear_user_data/0`). No raw `assertz` calls scattered through other modules.
7. **Streamlit reruns are stateless.** Persist anything that must survive a rerun in `st.session_state` or in the Prolog KB — not in module-level Python variables.

---

## 11. Common Commands

```bash
# Install
pip install -r requirements.txt

# Run the Prolog CLI (sanity check)
swipl -s prolog/finance_advisor.pl

# Run PLUnit tests
swipl -g "consult('prolog/tests/test_foo_rules.pl'), run_tests, halt"

# Run pytest
pytest tests/

# Launch the Streamlit dashboard
streamlit run app/streamlit_app.py
```

---

## 12. Out of Scope

These are intentionally **not** part of this project unless explicitly requested:
- Real banking API integration
- Persistent database (the Prolog KB is the database)
- Authentication / multi-user sessions
- Mobile-native UI
- Forecasting or ML-based predictions (the system is purely rule-based by design — that is what the course requires)

---

## 13. Prolog Feature Checklist (Marking Criteria)

The implementation must demonstrate each of the following. The locations are the modules where they are currently used; if you refactor, preserve at least one usage of each.

| Feature                  | Location                                      |
|--------------------------|-----------------------------------------------|
| Facts                    | `facts.pl` (dynamic + static)                 |
| Rules with conditions    | `foo_rules.pl`, `recommendations.pl`          |
| Backtracking (`fail`)    | `recommendations.pl` → `print_all_recommendations/1` |
| Cut (`!`)                | `recommendations.pl` → `top_recommendation/2` |
| Negation (`\+`)          | `foo_rules.pl` → `worst_debt/4`, `debt_gate_passed/1` |
| If-then-else (`-> ;`)    | `db_ops.pl` → `clear_debt/1`, `all_debts/2`   |
| `findall/3`              | `calculations.pl`                             |
| `bagof/3`                | `db_ops.pl` → `all_debts/2`                   |
| `member/2`               | `goal_advice.pl` → `valid_goal/1`             |
| `assertz/1`              | `db_ops.pl`, input handlers                   |
| `retract/1` / `retractall/2` | `db_ops.pl`                              |
| Recursion                | `calculations.pl` → `sum_list_rec/2`          |
| Aggregation              | `calculations.pl` (`findall` + recursive sum) |
