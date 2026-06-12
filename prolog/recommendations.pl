/* ============================================================
   RECOMMENDATIONS MODULE
   Priority-ordered recommendations following the FOO sequence.
   Demonstrates: cut (!) for priority ordering, backtracking
   with fail/0 to enumerate all applicable recommendations.
   ============================================================ */

/* recommend_step(User, StepNo, Action) - all matching steps */

recommend_step(User, 1, Action) :-
    budget_status(User, critical),
    Action = 'URGENT: Needs consume over 80% of income. Cut expenses or raise income before anything else.'.
recommend_step(User, 1, Action) :-
    budget_status(User, poor),
    needs_ratio(User, R),
    format(atom(Action),
      'Budget alert: needs are ~2f% of income (limit 50%). Restructure spending.', [R]).
recommend_step(User, 1, Action) :-
    budget_status(User, overspending_wants),
    wants_ratio(User, R),
    format(atom(Action),
      'Reduce wants spending: currently ~2f% of income (limit 30%).', [R]).

recommend_step(User, 2, Action) :-
    has_high_interest_debt(User),
    worst_debt(User, Type, Amount, Rate),
    format(atom(Action),
      'HIGH-INTEREST DEBT: pay off ~w (amount ~w at ~w%) first - avalanche method.',
      [Type, Amount, Rate]).

recommend_step(User, 3, Action) :-
    emergency_fund_status(User, none),
    emergency_fund_target(User, T),
    format(atom(Action),
      'No emergency fund. Build one now. Target: ~w (months of expenses for your age).', [T]).
recommend_step(User, 3, Action) :-
    emergency_fund_status(User, partial),
    emergency_fund_amount(User, A),
    emergency_fund_target(User, T),
    Rem is T - A,
    format(atom(Action),
      'Emergency fund partial (~w). You need ~w more to reach the target.', [A, Rem]).

recommend_step(User, 4, Action) :-
    \+ savings_gate_passed(User),
    user_profile(User, Age, _), age_group(Age, G),
    savings_target_for(G, T),
    savings_rate(User, R),
    format(atom(Action),
      'Savings rate is ~2f%. Target for your age group is ~w%. Automate savings first.', [R, T]).

recommend_step(User, 5, Action) :-
    investment_ready(User),
    goal(User, Goal),
    investment_advice_for_goal(Goal, Action).

/* Top recommendation: first FOO step that fires (cut enforces priority) */
top_recommendation(User, Action) :- recommend_step(User, 1, Action), !.
top_recommendation(User, Action) :- recommend_step(User, 2, Action), !.
top_recommendation(User, Action) :- recommend_step(User, 3, Action), !.
top_recommendation(User, Action) :- recommend_step(User, 4, Action), !.
top_recommendation(User, Action) :- recommend_step(User, 5, Action), !.
top_recommendation(_, 'All gates clear. Maintain habits and review quarterly.').

/* Backtracking with fail: print EVERY applicable recommendation */
print_all_recommendations(User) :-
    recommend_step(User, Step, Action),
    format('  [Step ~w] ~w~n', [Step, Action]),
    fail.
print_all_recommendations(_).
