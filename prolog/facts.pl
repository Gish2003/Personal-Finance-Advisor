/* ============================================================
   FACTS MODULE
   Dynamic declarations (runtime KB) and static domain knowledge
   (thresholds, age groups, age-adjusted targets).
   ============================================================ */

/* ----- Dynamic facts: asserted at runtime from the UI ----- */

:- dynamic user_profile/3.       % user_profile(user, Age, Occupation)
:- dynamic income/2.             % income(user, MonthlyAmount)
:- dynamic expenses/3.           % expenses(user, needs|wants, Amount)
:- dynamic debt/4.               % debt(user, Type, Amount, InterestRate)
:- dynamic savings/3.            % savings(user, Type, Amount)
:- dynamic goal/2.               % goal(user, Goal)

/* ----- Static thresholds ----- */

high_interest_threshold(15).     % >15% annual interest = high-interest
savings_rate_healthy(20).        % >=20% savings rate = healthy
savings_rate_warning(10).        % 10-19% = warning zone
debt_to_income_safe(40).         % DTI <=40% = manageable
budget_needs_max(50).            % 50/30/20 rule
budget_wants_max(30).

/* ----- Age group classification ----- */

age_group(Age, child)       :- Age >= 0,  Age =< 12.
age_group(Age, teenager)    :- Age >= 13, Age =< 17.
age_group(Age, young_adult) :- Age >= 18, Age =< 25.
age_group(Age, adult)       :- Age >= 26, Age =< 45.
age_group(Age, middle_age)  :- Age >= 46, Age =< 60.
age_group(Age, elder)       :- Age >= 61.

/* ----- Age-adjusted emergency fund target (months of expenses) ----- */

emergency_months_for(child,       1).
emergency_months_for(teenager,    1).
emergency_months_for(young_adult, 3).
emergency_months_for(adult,       3).
emergency_months_for(middle_age,  6).
emergency_months_for(elder,       6).

/* ----- Age-adjusted savings rate target (%) ----- */

savings_target_for(child,       5).
savings_target_for(teenager,    10).
savings_target_for(young_adult, 15).
savings_target_for(adult,       20).
savings_target_for(middle_age,  25).
savings_target_for(elder,       10).
