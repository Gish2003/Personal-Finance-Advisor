/* ============================================================
   FOO RULES MODULE
   Steps 1-5 of the Financial Order of Operations:
     1. Budget Check (50/30/20)
     2. High-Interest Debt Classification (avalanche)
     3. Emergency Fund
     4. Savings Rate Adequacy
     5. Investment Readiness
   Demonstrates: rules with conditions, cut (!), negation (\+).
   ============================================================ */

/* ----- FOO STEP 1: Budget Check (50/30/20) ----- */

budget_status(User, critical) :-
    needs_ratio(User, R), R > 80, !.
budget_status(User, poor) :-
    needs_ratio(User, R), budget_needs_max(M), R > M, !.
budget_status(User, overspending_wants) :-
    wants_ratio(User, R), budget_wants_max(M), R > M, !.
budget_status(User, warning) :-
    savings_rate(User, SR),
    savings_rate_warning(Lo), savings_rate_healthy(Hi),
    SR >= Lo, SR < Hi, !.
budget_status(User, healthy) :-
    savings_rate(User, SR), savings_rate_healthy(Hi), SR >= Hi.

budget_gate_passed(User) :-
    budget_status(User, S),
    member(S, [healthy, warning]).

/* ----- FOO STEP 2: Debt Classification ----- */

has_high_interest_debt(User) :-
    debt(User, _, _, Rate),
    high_interest_threshold(T),
    Rate > T.

/* Highest-interest debt = avalanche target. Negation \+ used. */
worst_debt(User, Type, Amount, Rate) :-
    debt(User, Type, Amount, Rate),
    \+ (debt(User, _, _, R2), R2 > Rate).

debt_status(User, debt_free) :-
    \+ debt(User, _, _, _), !.
debt_status(User, critical) :-
    has_high_interest_debt(User),
    debt_to_income(User, R), debt_to_income_safe(S), R > S, !.
debt_status(User, high_interest) :-
    has_high_interest_debt(User), !.
debt_status(User, overloaded) :-
    debt_to_income(User, R), debt_to_income_safe(S), R > S, !.
debt_status(_User, manageable).

debt_gate_passed(User) :-
    \+ has_high_interest_debt(User).

/* ----- FOO STEP 3: Emergency Fund ----- */

emergency_fund_amount(User, A) :-
    savings(User, emergency_fund, A), !.
emergency_fund_amount(_, 0).

emergency_fund_target(User, Target) :-
    user_profile(User, Age, _),
    age_group(Age, Group),
    emergency_months_for(Group, Months),
    total_expenses(User, E),
    Target is E * Months.

emergency_fund_status(User, adequate) :-
    emergency_fund_amount(User, A),
    emergency_fund_target(User, T),
    A >= T, !.
emergency_fund_status(User, partial) :-
    emergency_fund_amount(User, A),
    A > 0, !.
emergency_fund_status(_, none).

emergency_gate_passed(User) :-
    emergency_fund_status(User, adequate).

/* ----- FOO STEP 4: Savings Rate Adequacy ----- */

savings_status(User, excellent) :-
    user_profile(User, Age, _), age_group(Age, G),
    savings_target_for(G, T),
    savings_rate(User, R),
    R >= T + 10, !.
savings_status(User, adequate) :-
    user_profile(User, Age, _), age_group(Age, G),
    savings_target_for(G, T),
    savings_rate(User, R),
    R >= T, !.
savings_status(User, low) :-
    savings_rate(User, R), R >= 5, !.
savings_status(_, critical).

savings_gate_passed(User) :-
    savings_status(User, S),
    member(S, [adequate, excellent]).

/* ----- FOO STEP 5: Investment Readiness ----- */

investment_ready(User) :-
    budget_gate_passed(User),
    debt_gate_passed(User),
    emergency_gate_passed(User),
    savings_gate_passed(User).
