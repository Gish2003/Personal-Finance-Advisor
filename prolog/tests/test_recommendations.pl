/* ============================================================
   PLUnit tests for recommendations.pl
   Verifies FOO priority ordering and top_recommendation/2.
   Run: swipl -g "consult('prolog/tests/test_recommendations.pl'), run_tests, halt"

   Note: dynamic facts must be asserted/retracted via user:<goal>
   so the KB predicates (defined in module `user`) see them -
   PLUnit test bodies execute in their own unit module.
   ============================================================ */

:- consult('../finance_advisor.pl').

:- begin_tests(recommendations).

/* Step 1 (budget) outranks everything else when it fires */
test(top_recommendation_step1_budget_critical) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(income(user, 100000)),
    user:assertz(expenses(user, needs, 90000)),
    user:assertz(expenses(user, wants, 5000)),
    user:assertz(debt(user, credit_card, 50000, 24)),
    top_recommendation(user, Action),
    Action == 'URGENT: Needs consume over 80% of income. Cut expenses or raise income before anything else.'.

/* Step 2 (high-interest debt) outranks emergency fund / savings,
   but only when the budget gate (Step 1) passes. */
test(top_recommendation_step2_high_interest_debt) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(income(user, 1000)),
    user:assertz(expenses(user, needs, 400)),
    user:assertz(expenses(user, wants, 300)),
    user:assertz(debt(user, credit_card, 5000, 24)),
    top_recommendation(user, Action),
    once(sub_atom(Action, _, _, _, 'HIGH-INTEREST DEBT')).

/* Step 3 (emergency fund) fires when budget and debt gates pass */
test(top_recommendation_step3_emergency_fund) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(income(user, 1000)),
    user:assertz(expenses(user, needs, 400)),
    user:assertz(expenses(user, wants, 300)),
    % savings rate 30% healthy, no debt, no emergency fund
    top_recommendation(user, Action),
    once(sub_atom(Action, _, _, _, 'emergency fund')).

/* Step 4 (savings rate) fires once budget/debt/emergency gates pass.
   Budget healthy/warning requires savings_rate >= 20%, so only an age
   group with a target ABOVE 20% (middle_age = 25%) can have the
   savings gate fail while the budget gate passes. */
test(top_recommendation_step4_savings_rate) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 50, employed)),
    user:assertz(income(user, 1000)),
    user:assertz(expenses(user, needs, 500)),
    user:assertz(expenses(user, wants, 300)),
    % savings rate = 20%, middle_age target = 25% -> savings gate fails
    % middle_age emergency target = 6 * 800 = 4800, fully funded
    user:assertz(savings(user, emergency_fund, 4800)),
    top_recommendation(user, Action),
    once(sub_atom(Action, _, _, _, 'Savings rate')).

/* Step 5 (investment readiness) fires goal advice when all gates pass */
test(top_recommendation_step5_goal_advice) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(income(user, 1000)),
    user:assertz(expenses(user, needs, 400)),
    user:assertz(expenses(user, wants, 200)),
    user:assertz(savings(user, emergency_fund, 1800)),
    user:assertz(debt(user, mortgage, 100000, 5)),
    user:assertz(goal(user, invest)),
    once(investment_ready(user)),
    top_recommendation(user, Action),
    Action == 'Start with low-cost index funds; automate monthly contributions.'.

/* No goal asserted: investment-ready user gets the all-clear default */
test(top_recommendation_default_all_clear) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(income(user, 1000)),
    user:assertz(expenses(user, needs, 400)),
    user:assertz(expenses(user, wants, 200)),
    user:assertz(savings(user, emergency_fund, 1800)),
    \+ user:goal(user, _),
    top_recommendation(user, Action),
    Action == 'All gates clear. Maintain habits and review quarterly.'.

/* print_all_recommendations/1 enumerates every applicable step via fail-driven backtracking */
test(print_all_recommendations_enumerates_all_steps) :-
    user:clear_user_data,
    user:assertz(user_profile(user, 30, employed)),
    user:assertz(income(user, 100000)),
    user:assertz(expenses(user, needs, 90000)),
    user:assertz(expenses(user, wants, 5000)),
    user:assertz(debt(user, credit_card, 50000, 24)),
    findall(Step-Action, recommend_step(user, Step, Action), Recs),
    Recs \== [],
    once(member(1-_, Recs)),
    once(member(2-_, Recs)).

:- end_tests(recommendations).
