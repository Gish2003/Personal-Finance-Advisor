/* ============================================================
   GOAL ADVICE MODULE
   Goal-conditioned advice (Step 5 / investment readiness) and
   age-group-specific guidance.
   Demonstrates: member/2.
   ============================================================ */

/* ----- Goal validation and advice ----- */

valid_goal(G) :-
    member(G, [buy_house, retire_early, pay_debt, education, invest, travel]).

investment_advice_for_goal(buy_house,
  'Save a 20% down payment in a fixed deposit or money market fund.').
investment_advice_for_goal(retire_early,
  'Maximise retirement contributions; diversified index funds; target 25x annual expenses.').
investment_advice_for_goal(education,
  'Open an education savings plan with low-risk instruments timed to need.').
investment_advice_for_goal(invest,
  'Start with low-cost index funds; automate monthly contributions.').
investment_advice_for_goal(travel,
  'Create a separate travel fund; never dip into the emergency fund.').
investment_advice_for_goal(pay_debt,
  'High-interest debt cleared - prepay low-interest debt while investing the difference.').

goal_advice(User, Advice) :-
    goal(User, Goal),
    financial_health(User, H),
    member(H, [good, excellent]),
    investment_advice_for_goal(Goal, Advice), !.
goal_advice(User, Advice) :-
    goal(User, Goal),
    format(atom(Advice),
      'Goal (~w) noted but deferred - complete the earlier FOO steps first.', [Goal]).

/* ----- Age-specific advice ----- */

user_age_group(User, Group) :-
    user_profile(User, Age, _),
    age_group(Age, Group).

age_advice(User, A) :- user_age_group(User, child),
  A = 'Learn the saving habit: separate spending money from savings, even small amounts.'.
age_advice(User, A) :- user_age_group(User, teenager),
  A = 'Avoid all debt. Save 10% of any income. Learn compound interest early.'.
age_advice(User, A) :- user_age_group(User, young_adult),
  A = 'Clear student loans aggressively. Build the emergency fund before investing. Start early - time is your biggest asset.'.
age_advice(User, A) :- user_age_group(User, adult),
  A = 'Balance mortgage, family costs and retirement. Aim for a 20-25% savings rate. Review insurance.'.
age_advice(User, A) :- user_age_group(User, middle_age),
  A = 'Accelerate retirement savings, clear remaining debt, grow emergency fund to 6+ months.'.
age_advice(User, A) :- user_age_group(User, elder),
  A = 'Shift to capital preservation. Secure healthcare coverage. Plan withdrawals and estate.'.
