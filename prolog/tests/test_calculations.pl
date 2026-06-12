/* ============================================================
   PLUnit tests for calculations.pl
   Run: swipl -g "consult('prolog/tests/test_calculations.pl'), run_tests, halt"

   Note: finance_advisor.pl is consulted into the `user` module,
   while PLUnit test bodies execute in their own unit module.
   Dynamic facts must therefore be asserted/retracted via
   user:<goal> so the KB predicates (defined in `user`) see them.
   ============================================================ */

:- consult('../finance_advisor.pl').

:- begin_tests(calculations).

test(sum_list_rec_empty) :-
    sum_list_rec([], 0).

test(sum_list_rec_values) :-
    sum_list_rec([10, 20, 30], 60).

test(total_needs) :-
    user:clear_user_data,
    user:assertz(expenses(user, needs, 1000)),
    user:assertz(expenses(user, needs, 500)),
    total_needs(user, 1500).

test(total_wants) :-
    user:clear_user_data,
    user:assertz(expenses(user, wants, 200)),
    user:assertz(expenses(user, wants, 300)),
    total_wants(user, 500).

test(total_expenses) :-
    user:clear_user_data,
    user:assertz(expenses(user, needs, 1000)),
    user:assertz(expenses(user, wants, 500)),
    total_expenses(user, 1500).

test(total_debt) :-
    user:clear_user_data,
    user:assertz(debt(user, credit_card, 5000, 22)),
    user:assertz(debt(user, car_loan, 15000, 7)),
    total_debt(user, 20000).

test(total_savings) :-
    user:clear_user_data,
    user:assertz(savings(user, emergency_fund, 1000)),
    user:assertz(savings(user, investment, 4000)),
    total_savings(user, 5000).

test(savings_rate) :-
    user:clear_user_data,
    user:assertz(income(user, 1000)),
    user:assertz(expenses(user, needs, 500)),
    user:assertz(expenses(user, wants, 200)),
    savings_rate(user, Rate),
    Rate =:= 30.0.

test(needs_ratio) :-
    user:clear_user_data,
    user:assertz(income(user, 1000)),
    user:assertz(expenses(user, needs, 500)),
    needs_ratio(user, Ratio),
    Ratio =:= 50.0.

test(wants_ratio) :-
    user:clear_user_data,
    user:assertz(income(user, 1000)),
    user:assertz(expenses(user, wants, 300)),
    wants_ratio(user, Ratio),
    Ratio =:= 30.0.

test(debt_to_income) :-
    user:clear_user_data,
    user:assertz(income(user, 1000)),
    user:assertz(debt(user, credit_card, 400, 20)),
    debt_to_income(user, DTI),
    DTI =:= 40.0.

test(net_worth) :-
    user:clear_user_data,
    user:assertz(savings(user, emergency_fund, 5000)),
    user:assertz(savings(user, investment, 2000)),
    user:assertz(debt(user, car_loan, 3000, 6)),
    net_worth(user, NW),
    NW =:= 4000.

:- end_tests(calculations).
