/* ============================================================
   PLUnit tests for foo_rules.pl
   Each FOO gate gets at least one passing and one failing case.
   Run: swipl -g "consult('prolog/tests/test_foo_rules.pl'), run_tests, halt"

   Note: dynamic facts must be asserted/retracted via user:<goal>
   so the KB predicates (defined in module `user`) see them -
   PLUnit test bodies execute in their own unit module.
   ============================================================ */

:- consult('../finance_advisor.pl').

:- begin_tests(foo_rules).

/* ----- Gate 1: Budget Check (50/30/20) ----- */

test(budget_critical) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(income(user, 100000)),
    user:assertz(expenses(user, needs, 85000)),
    user:assertz(expenses(user, wants, 10000)),
    budget_status(user, critical),
    \+ budget_gate_passed(user).

test(budget_healthy) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(income(user, 1000)),
    user:assertz(expenses(user, needs, 400)),
    user:assertz(expenses(user, wants, 300)),
    budget_status(user, healthy),
    once(budget_gate_passed(user)).

/* ----- Gate 2: High-Interest Debt ----- */

test(debt_gate_fails_with_high_interest) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(income(user, 100000)),
    user:assertz(debt(user, credit_card, 50000, 24)),
    has_high_interest_debt(user),
    \+ debt_gate_passed(user).

test(debt_gate_passes_without_high_interest) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(income(user, 100000)),
    user:assertz(debt(user, mortgage, 200000, 9)),
    \+ has_high_interest_debt(user),
    debt_gate_passed(user).

test(debt_status_debt_free) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(income(user, 100000)),
    debt_status(user, debt_free).

test(worst_debt_picks_highest_rate) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(income(user, 100000)),
    user:assertz(debt(user, credit_card, 5000, 24)),
    user:assertz(debt(user, car_loan, 15000, 7)),
    worst_debt(user, credit_card, 5000, 24).

/* ----- Gate 3: Emergency Fund ----- */

test(emergency_gate_passes_when_adequate) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(expenses(user, needs, 1000)),
    user:assertz(expenses(user, wants, 500)),
    % adult target = 3 months * 1500 = 4500
    user:assertz(savings(user, emergency_fund, 5000)),
    emergency_fund_status(user, adequate),
    emergency_gate_passed(user).

test(emergency_gate_fails_when_none) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(expenses(user, needs, 1000)),
    user:assertz(expenses(user, wants, 500)),
    emergency_fund_status(user, none),
    \+ emergency_gate_passed(user).

test(emergency_gate_fails_when_partial) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(expenses(user, needs, 1000)),
    user:assertz(expenses(user, wants, 500)),
    user:assertz(savings(user, emergency_fund, 1000)),
    emergency_fund_status(user, partial),
    \+ emergency_gate_passed(user).

/* ----- Gate 4: Savings Rate Adequacy ----- */

test(savings_gate_passes_when_adequate) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    % adult target = 20%
    user:assertz(income(user, 1000)),
    user:assertz(expenses(user, needs, 400)),
    user:assertz(expenses(user, wants, 300)),
    % savings rate = 30% >= 20%
    savings_status(user, S),
    member(S, [adequate, excellent]),
    savings_gate_passed(user).

test(savings_gate_fails_when_low) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(income(user, 1000)),
    user:assertz(expenses(user, needs, 600)),
    user:assertz(expenses(user, wants, 350)),
    % savings rate = 5% < 20% target
    once(savings_status(user, S)),
    once(member(S, [low, critical])),
    \+ once(savings_gate_passed(user)).

/* ----- Gate 5: Investment Readiness ----- */

test(investment_ready_when_all_gates_pass) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(income(user, 1000)),
    user:assertz(expenses(user, needs, 400)),
    user:assertz(expenses(user, wants, 200)),
    % savings rate = 40%, needs/wants ok
    user:assertz(savings(user, emergency_fund, 1800)),
    % adult target = 3 * 600 = 1800 -> adequate
    user:assertz(debt(user, mortgage, 100000, 5)),
    once(investment_ready(user)).

test(investment_not_ready_with_high_interest_debt) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(income(user, 1000)),
    user:assertz(expenses(user, needs, 400)),
    user:assertz(expenses(user, wants, 200)),
    user:assertz(savings(user, emergency_fund, 1800)),
    user:assertz(debt(user, credit_card, 5000, 24)),
    \+ investment_ready(user).

:- end_tests(foo_rules).
