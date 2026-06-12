/* ============================================================
   DB OPS MODULE
   The only place dynamic facts are asserted/retracted from
   user-driven actions (per CLAUDE.md workflow rule 6).
   Demonstrates: assertz/1, retract/1, retractall/2,
   if-then-else (-> ;), bagof/3.
   ============================================================ */

clear_user_data :-
    retractall(user_profile(_, _, _)),
    retractall(income(_, _)),
    retractall(expenses(_, _, _)),
    retractall(debt(_, _, _, _)),
    retractall(savings(_, _, _)),
    retractall(goal(_, _)).

add_debt(Type, Amount, Rate) :-
    assertz(debt(user, Type, Amount, Rate)).

clear_debt(Type) :-
    ( retract(debt(user, Type, _, _))
    -> write('Debt cleared.'), nl
    ;  write('No such debt found.'), nl ).

update_income(New) :-
    retractall(income(user, _)),
    assertz(income(user, New)).

update_savings(Type, Amount) :-
    retractall(savings(user, Type, _)),
    assertz(savings(user, Type, Amount)).

/* bagof showcase: list all debt types with rates */
all_debts(User, List) :-
    ( bagof(Type-Rate, A^debt(User, Type, A, Rate), List)
    -> true
    ;  List = [] ).
