/* ============================================================
   PERSONAL FINANCE ADVISOR - Expert System
   CM 2520 Deductive Reasoning and Logic Programming
   SWI-Prolog | Modular entry point

   This file is the single entry point for the knowledge base.
   It consults every other module and provides the CLI demo
   entry point (start/0). The Streamlit layer only loads this
   file.

   Run with:  ?- consult('finance_advisor.pl').  then  ?- start.
   ============================================================ */

:- consult('facts.pl').
:- consult('calculations.pl').
:- consult('foo_rules.pl').
:- consult('health.pl').
:- consult('recommendations.pl').
:- consult('goal_advice.pl').
:- consult('db_ops.pl').

/* ============================================================
   CLI INTERFACE
   ============================================================ */

start :-
    clear_user_data,
    nl,
    write('============================================'), nl,
    write('  PERSONAL FINANCE ADVISOR - Expert System  '), nl,
    write('============================================'), nl,
    write('(End every answer with a full stop, e.g. 25.)'), nl, nl,
    collect_profile,
    collect_income,
    collect_expenses,
    collect_debts,
    collect_savings,
    collect_goal,
    nl, write('--- Analysing your financial profile ---'), nl,
    run_analysis,
    main_menu.

collect_profile :-
    write('Your age: '), read(Age),
    write('Occupation (student/employed/self_employed/retired): '), read(Occ),
    assertz(user_profile(user, Age, Occ)).

collect_income :-
    write('Monthly income (0 if none): '), read(I),
    assertz(income(user, I)).

collect_expenses :-
    write('Monthly NEEDS spend (rent, food, bills, transport): '), read(N),
    assertz(expenses(user, needs, N)),
    write('Monthly WANTS spend (entertainment, dining, shopping): '), read(W),
    assertz(expenses(user, wants, W)).

collect_debts :-
    write('Do you have debts? (yes/no): '), read(Ans),
    ( Ans = yes -> debt_loop ; true ).

debt_loop :-
    write('Debt type (credit_card/student_loan/mortgage/car_loan/personal_loan): '),
    read(Type),
    write('Total amount: '), read(Amount),
    write('Annual interest rate %: '), read(Rate),
    assertz(debt(user, Type, Amount, Rate)),
    write('Add another debt? (yes/no): '), read(More),
    ( More = yes -> debt_loop ; true ).

collect_savings :-
    write('Emergency fund balance (0 if none): '), read(EF),
    assertz(savings(user, emergency_fund, EF)),
    write('Investment/retirement balance (0 if none): '), read(Inv),
    assertz(savings(user, investment, Inv)).

collect_goal :-
    write('Goal (buy_house/retire_early/pay_debt/education/invest/travel): '),
    read(G),
    ( valid_goal(G)
    -> assertz(goal(user, G))
    ;  write('Invalid goal - defaulting to invest.'), nl,
       assertz(goal(user, invest)) ).

/* ============================================================
   REPORT OUTPUT
   ============================================================ */

run_analysis :-
    nl, write('========= FINANCIAL HEALTH REPORT ========='), nl,
    age_advice(user, AA),
    format('  Age advice     : ~w~n', [AA]),
    financial_health(user, H),
    format('  Overall health : ~w~n', [H]),
    net_worth(user, NW),
    format('  Net worth      : ~w~n', [NW]),
    ( savings_rate(user, SR)
    -> format('  Savings rate   : ~2f%~n', [SR])
    ;  write('  Savings rate   : n/a (no income)'), nl ),
    debt_status(user, DS),
    format('  Debt status    : ~w~n', [DS]),
    emergency_fund_status(user, EFS),
    format('  Emergency fund : ~w~n', [EFS]),
    nl, write('========= TOP PRIORITY ACTION ============='), nl,
    top_recommendation(user, Top),
    format('  >> ~w~n', [Top]),
    nl, write('========= FULL ACTION PLAN ================'), nl,
    print_all_recommendations(user),
    nl, write('========= GOAL ADVICE ====================='), nl,
    goal_advice(user, GA),
    format('  ~w~n', [GA]).

/* ============================================================
   MENU LOOP
   ============================================================ */

main_menu :-
    nl,
    write('================ MENU ====================='), nl,
    write('  1. View report again'), nl,
    write('  2. Add a debt'), nl,
    write('  3. Update income'), nl,
    write('  4. Update savings'), nl,
    write('  5. List all debts'), nl,
    write('  6. Clear a paid-off debt'), nl,
    write('  7. New profile (start over)'), nl,
    write('  8. Exit'), nl,
    write('==========================================='), nl,
    write('Choose (1-8): '), read(C),
    handle(C).

handle(1) :- run_analysis, main_menu.
handle(2) :-
    write('Debt type: '), read(T),
    write('Amount: '), read(A),
    write('Interest rate %: '), read(R),
    add_debt(T, A, R),
    write('Debt added.'), nl, main_menu.
handle(3) :-
    write('New monthly income: '), read(I),
    update_income(I),
    write('Income updated.'), nl, main_menu.
handle(4) :-
    write('Savings type (emergency_fund/investment): '), read(T),
    write('New amount: '), read(A),
    update_savings(T, A),
    write('Savings updated.'), nl, main_menu.
handle(5) :-
    all_debts(user, L),
    format('Debts (type-rate%): ~w~n', [L]), main_menu.
handle(6) :-
    write('Debt type to remove: '), read(T),
    clear_debt(T), main_menu.
handle(7) :- start.
handle(8) :- write('Goodbye.'), nl.
handle(_) :- write('Invalid choice.'), nl, main_menu.

/* ============================================================
   TEST SCENARIOS (load manually)
   ============================================================
   Scenario A - Young adult, high-interest student loan:
   ?- clear_user_data,
      assertz(user_profile(user, 22, employed)),
      assertz(income(user, 80000)),
      assertz(expenses(user, needs, 38000)),
      assertz(expenses(user, wants, 22000)),
      assertz(debt(user, student_loan, 300000, 18)),
      assertz(savings(user, emergency_fund, 5000)),
      assertz(savings(user, investment, 0)),
      assertz(goal(user, pay_debt)),
      run_analysis.
   Expected: Step 2 high-interest debt fires as top action.

   Scenario B - Middle-aged, healthy finances:
   ?- clear_user_data,
      assertz(user_profile(user, 48, employed)),
      assertz(income(user, 250000)),
      assertz(expenses(user, needs, 100000)),
      assertz(expenses(user, wants, 50000)),
      assertz(debt(user, mortgage, 5000000, 9)),
      assertz(savings(user, emergency_fund, 950000)),
      assertz(savings(user, investment, 200000)),
      assertz(goal(user, retire_early)),
      run_analysis.
   Expected: investment ready, goal advice for retire_early fires.

   Scenario C - Elder, fixed income:
   ?- clear_user_data,
      assertz(user_profile(user, 65, retired)),
      assertz(income(user, 60000)),
      assertz(expenses(user, needs, 45000)),
      assertz(expenses(user, wants, 10000)),
      assertz(savings(user, emergency_fund, 360000)),
      assertz(savings(user, investment, 0)),
      assertz(goal(user, invest)),
      run_analysis.

   Scenario D - Child, pocket money:
   ?- clear_user_data,
      assertz(user_profile(user, 10, student)),
      assertz(income(user, 2000)),
      assertz(expenses(user, needs, 500)),
      assertz(expenses(user, wants, 1000)),
      assertz(savings(user, emergency_fund, 200)),
      assertz(savings(user, investment, 0)),
      assertz(goal(user, education)),
      run_analysis.
   ============================================================ */
