/* ============================================================
   PLUnit tests for end-to-end profile scenarios
   Covers the four sample profiles from CLAUDE.md (child, young
   adult, middle-aged, elder) plus dynamic KB assertz/retract
   round-trips via db_ops.pl.
   Run: swipl -g "consult('prolog/tests/test_scenarios.pl'), run_tests, halt"

   Note: dynamic facts must be asserted/retracted via user:<goal>
   so the KB predicates (defined in module `user`) see them -
   PLUnit test bodies execute in their own unit module.
   ============================================================ */

:- consult('../finance_advisor.pl').

:- begin_tests(scenarios).

/* ----- Scenario A: Young adult, high-interest student loan ----- */

test(scenario_young_adult_high_interest_debt) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 22, employed)),
    user:assertz(income(user, 80000)),
    user:assertz(expenses(user, needs, 38000)),
    user:assertz(expenses(user, wants, 22000)),
    user:assertz(debt(user, student_loan, 300000, 18)),
    user:assertz(savings(user, emergency_fund, 5000)),
    user:assertz(savings(user, investment, 0)),
    user:assertz(goal(user, pay_debt)),
    age_group(22, young_adult),
    once(budget_status(user, healthy)),
    once(financial_health(user, poor)),
    once(debt_status(user, critical)),
    top_recommendation(user, Action),
    once(sub_atom(Action, _, _, _, 'HIGH-INTEREST DEBT')).

/* ----- Scenario B: Middle-aged, healthy finances ----- */

test(scenario_middle_aged_healthy) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 48, employed)),
    user:assertz(income(user, 250000)),
    user:assertz(expenses(user, needs, 100000)),
    user:assertz(expenses(user, wants, 50000)),
    user:assertz(debt(user, mortgage, 5000000, 9)),
    user:assertz(savings(user, emergency_fund, 950000)),
    user:assertz(savings(user, investment, 200000)),
    user:assertz(goal(user, retire_early)),
    age_group(48, middle_age),
    emergency_fund_status(user, adequate),
    once(investment_ready(user)),
    once(financial_health(user, good)),
    top_recommendation(user, Action),
    Action == 'Maximise retirement contributions; diversified index funds; target 25x annual expenses.',
    once(goal_advice(user, GA)),
    GA == 'Maximise retirement contributions; diversified index funds; target 25x annual expenses.'.

/* ----- Scenario C: Elder, fixed income ----- */

test(scenario_elder_fixed_income) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 65, retired)),
    user:assertz(income(user, 60000)),
    user:assertz(expenses(user, needs, 45000)),
    user:assertz(expenses(user, wants, 10000)),
    user:assertz(savings(user, emergency_fund, 360000)),
    user:assertz(savings(user, investment, 0)),
    user:assertz(goal(user, invest)),
    age_group(65, elder),
    once(debt_status(user, debt_free)),
    emergency_fund_status(user, adequate),
    once(budget_status(user, poor)),
    top_recommendation(user, Action),
    once(sub_atom(Action, _, _, _, 'Budget alert')).

/* ----- Scenario D: Child, pocket money ----- */

test(scenario_child_pocket_money) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 10, student)),
    user:assertz(income(user, 2000)),
    user:assertz(expenses(user, needs, 500)),
    user:assertz(expenses(user, wants, 1000)),
    user:assertz(savings(user, emergency_fund, 200)),
    user:assertz(savings(user, investment, 0)),
    user:assertz(goal(user, education)),
    age_group(10, child),
    once(debt_status(user, debt_free)),
    once(budget_status(user, overspending_wants)),
    top_recommendation(user, Action),
    once(sub_atom(Action, _, _, _, 'Reduce wants spending')).

/* ----- Dynamic KB: assertz/retract round-trips via db_ops.pl ----- */

test(add_and_clear_debt_round_trip) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    \+ user:debt(user, credit_card, _, _),
    add_debt(credit_card, 5000, 22),
    user:debt(user, credit_card, 5000, 22),
    clear_debt(credit_card),
    \+ user:debt(user, credit_card, _, _).

test(clear_debt_on_missing_debt_does_not_fail) :-
    user:clear_user_data,
    clear_debt(nonexistent_type).

test(update_income_replaces_value) :-
    user:clear_user_data,
    user:assertz(income(user, 1000)),
    update_income(2000),
    user:income(user, 2000),
    \+ user:income(user, 1000).

test(update_savings_replaces_value) :-
    user:clear_user_data,
    user:assertz(savings(user, emergency_fund, 100)),
    update_savings(emergency_fund, 500),
    user:savings(user, emergency_fund, 500),
    \+ user:savings(user, emergency_fund, 100).

test(all_debts_bagof) :-
    user:clear_user_data,
    add_debt(credit_card, 5000, 24),
    add_debt(car_loan, 15000, 7),
    all_debts(user, Debts),
    sort(Debts, Sorted),
    sort([credit_card-24, car_loan-7], ExpectedSorted),
    Sorted == ExpectedSorted.

test(all_debts_empty_list_when_no_debts) :-
    user:clear_user_data,
    all_debts(user, []).

test(clear_user_data_resets_all_dynamic_facts) :-
    user:assertz(user_profile(user, 99, employed)),
    user:assertz(income(user, 1)),
    user:assertz(expenses(user, needs, 1)),
    user:assertz(debt(user, credit_card, 1, 1)),
    user:assertz(savings(user, emergency_fund, 1)),
    user:assertz(goal(user, invest)),
    clear_user_data,
    \+ user:user_profile(_, _, _),
    \+ user:income(_, _),
    \+ user:expenses(_, _, _),
    \+ user:debt(_, _, _, _),
    \+ user:savings(_, _, _),
    \+ user:goal(_, _).

:- end_tests(scenarios).
