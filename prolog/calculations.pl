/* ============================================================
   CALCULATIONS MODULE
   Totals, ratios, savings rate, debt-to-income, net worth.
   Demonstrates: recursion, findall/3, aggregation.
   ============================================================ */

/* Recursive list sum (own implementation for marks) */
sum_list_rec([], 0).
sum_list_rec([H|T], Sum) :-
    sum_list_rec(T, Rest),
    Sum is H + Rest.


total_needs(User, Total) :-
    findall(A, expenses(User, needs, A), L),
    sum_list_rec(L, Total).
total_wants(User, Total) :-
    findall(A, expenses(User, wants, A), L),
    sum_list_rec(L, Total).

total_expenses(User, Total) :-
    total_needs(User, N),
    total_wants(User, W),
    Total is N + W.

total_debt(User, Total) :-
    findall(A, debt(User, _, A, _), L),
    sum_list_rec(L, Total).

total_savings(User, Total) :-
    findall(A, savings(User, _, A), L),
    sum_list_rec(L, Total).

savings_rate(User, Rate) :-
    income(User, I), I > 0,
    total_expenses(User, E),
    Rate is ((I - E) / I) * 100.

needs_ratio(User, R) :-
    income(User, I), I > 0,
    total_needs(User, N),
    R is (N / I) * 100.

wants_ratio(User, R) :-
    income(User, I), I > 0,
    total_wants(User, W),
    R is (W / I) * 100.

debt_to_income(User, R) :-
    income(User, I), I > 0,
    total_debt(User, D),
    R is (D / I) * 100.

net_worth(User, NW) :-
    total_savings(User, S),
    total_debt(User, D),
    NW is S - D.
