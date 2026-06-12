"""pytest integration tests for FinanceEngine (Streamlit <-> Prolog layer).

Each test gets a fresh engine via the `engine` fixture, since the
underlying KB is stateful (dynamic facts persist until clear_user_data).
"""

import pytest

from app.prolog_engine import FinanceEngine, PrologQueryError


@pytest.fixture
def engine():
    eng = FinanceEngine()
    eng.reset()
    return eng


def load_scenario_a(eng: FinanceEngine):
    """Young adult, high-interest student loan (CLAUDE.md Scenario A)."""
    eng.load_profile(
        age=22, occupation="employed", income=80000,
        needs=38000, wants=22000,
        emergency_fund=5000, investment=0, goal="pay_debt",
    )
    eng.add_debt("student_loan", 300000, 18)


def load_scenario_b(eng: FinanceEngine):
    """Middle-aged, healthy finances (CLAUDE.md Scenario B)."""
    eng.load_profile(
        age=48, occupation="employed", income=250000,
        needs=100000, wants=50000,
        emergency_fund=950000, investment=200000, goal="retire_early",
    )
    eng.add_debt("mortgage", 5000000, 9)


# ------------------------------------------------------------
# Profile load
# ------------------------------------------------------------

def test_load_profile_sets_facts(engine):
    load_scenario_a(engine)
    assert engine.has_profile()


def test_reset_clears_profile(engine):
    load_scenario_a(engine)
    engine.reset()
    assert not engine.has_profile()


# ------------------------------------------------------------
# Gate computations
# ------------------------------------------------------------

def test_gate_statuses_scenario_a(engine):
    load_scenario_a(engine)
    gates = engine.gate_statuses()

    assert gates["budget"]["status"] == "healthy"
    assert gates["budget"]["passed"] is True
    assert gates["debt"]["status"] == "critical"
    assert gates["debt"]["passed"] is False


def test_gate_statuses_scenario_b(engine):
    load_scenario_b(engine)
    gates = engine.gate_statuses()

    assert gates["emergency"]["status"] == "adequate"
    assert gates["emergency"]["passed"] is True
    assert gates["investment"]["passed"] is True
    assert gates["investment"]["status"] == "ready"


def test_financial_health_scenario_a(engine):
    load_scenario_a(engine)
    assert engine.financial_health() == "poor"


def test_financial_health_scenario_b(engine):
    load_scenario_b(engine)
    assert engine.financial_health() == "good"


# ------------------------------------------------------------
# Metrics
# ------------------------------------------------------------

def test_metrics_scenario_a(engine):
    load_scenario_a(engine)
    metrics = engine.metrics()

    assert metrics["savings_rate"] == pytest.approx(25.0)
    assert metrics["debt_to_income"] is not None
    assert metrics["net_worth"] is not None
    assert metrics["emergency_fund_amount"] == 5000


def test_metrics_scenario_b_emergency_fund_months(engine):
    load_scenario_b(engine)
    metrics = engine.metrics()

    # 950000 / (100000 + 50000) = ~6.33 months covered
    assert metrics["emergency_fund_months"] == pytest.approx(950000 / 150000)
    # target = 6 months * 150000 total expenses
    assert metrics["emergency_fund_target"] == 900000


# ------------------------------------------------------------
# Recommendations
# ------------------------------------------------------------

def test_top_recommendation_scenario_a_high_interest_debt(engine):
    load_scenario_a(engine)
    top = engine.top_recommendation()
    assert "HIGH-INTEREST DEBT" in top


def test_recommendations_sorted_by_step(engine):
    load_scenario_a(engine)
    recs = engine.recommendations()

    assert recs, "expected at least one recommendation"
    steps = [step for step, _ in recs]
    assert steps == sorted(steps)


def test_top_recommendation_scenario_b_goal_advice(engine):
    load_scenario_b(engine)
    top = engine.top_recommendation()
    assert top == (
        "Maximise retirement contributions; diversified index funds; "
        "target 25x annual expenses."
    )


def test_goal_advice_scenario_b(engine):
    load_scenario_b(engine)
    assert engine.goal_advice() == (
        "Maximise retirement contributions; diversified index funds; "
        "target 25x annual expenses."
    )


def test_age_advice_present_for_each_age_group(engine):
    for age, occupation in [(10, "student"), (22, "employed"), (48, "employed"), (65, "retired")]:
        engine.load_profile(
            age=age, occupation=occupation, income=1000,
            needs=400, wants=300,
            emergency_fund=0, investment=0, goal="invest",
        )
        advice = engine.age_advice()
        assert isinstance(advice, str) and advice


# ------------------------------------------------------------
# Dynamic add/remove (debts, income, savings)
# ------------------------------------------------------------

def test_add_and_clear_debt(engine):
    load_scenario_b(engine)

    assert engine.add_debt("car_loan", 20000, 6) is True
    debts = dict(engine.all_debts())
    assert debts["car_loan"] == 6

    assert engine.clear_debt("car_loan") is True
    debts = dict(engine.all_debts())
    assert "car_loan" not in debts


def test_all_debts_returns_pairs(engine):
    load_scenario_a(engine)
    debts = engine.all_debts()
    assert ("student_loan", 18) in debts


def test_update_income_changes_metrics(engine):
    load_scenario_a(engine)
    before = engine.metrics()["savings_rate"]

    engine.update_income(40000)
    after = engine.metrics()["savings_rate"]

    assert after != before


def test_update_savings_changes_emergency_fund(engine):
    load_scenario_a(engine)

    engine.update_savings("emergency_fund", 999999)
    metrics = engine.metrics()
    assert metrics["emergency_fund_amount"] == 999999


# ------------------------------------------------------------
# Raw query console
# ------------------------------------------------------------

def test_raw_query_returns_bindings(engine):
    load_scenario_a(engine)
    rows = engine.raw_query("financial_health(user, X)")
    assert rows == [{"X": "poor"}]


def test_raw_query_findall(engine):
    load_scenario_a(engine)
    rows = engine.raw_query("findall(S-A, recommend_step(user, S, A), L)")
    assert len(rows) == 1
    assert isinstance(rows[0]["L"], list)
    assert rows[0]["L"]


def test_raw_query_rejects_directive(engine):
    with pytest.raises(PrologQueryError):
        engine.raw_query(":- shell(dir).")


def test_raw_query_rejects_forbidden_predicate(engine):
    with pytest.raises(PrologQueryError):
        engine.raw_query("halt")


def test_raw_query_rejects_assert(engine):
    with pytest.raises(PrologQueryError):
        engine.raw_query("assertz(evil(x))")


# ------------------------------------------------------------
# assert_fact / retract_fact
# ------------------------------------------------------------

def test_assert_and_retract_fact(engine):
    load_scenario_b(engine)

    assert engine.assert_fact("debt(user, personal_loan, 1000, 5)") is True
    debts = dict(engine.all_debts())
    assert debts["personal_loan"] == 5

    assert engine.retract_fact("debt(user, personal_loan, 1000, 5)") is True
    debts = dict(engine.all_debts())
    assert "personal_loan" not in debts


def test_assert_fact_rejects_directive(engine):
    with pytest.raises(PrologQueryError):
        engine.assert_fact(":- shell(dir)")
