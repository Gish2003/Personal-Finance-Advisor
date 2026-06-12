/* ============================================================
   HEALTH MODULE
   Composite financial health classification, derived from the
   FOO gate statuses.
   ============================================================ */

financial_health(User, excellent) :-
    budget_status(User, healthy),
    debt_status(User, debt_free),
    emergency_gate_passed(User),
    savings_status(User, excellent), !.
financial_health(User, good) :-
    investment_ready(User), !.
financial_health(User, moderate) :-
    budget_gate_passed(User),
    debt_gate_passed(User), !.
financial_health(User, poor) :-
    budget_gate_passed(User), !.
financial_health(_, critical).
