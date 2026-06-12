"""PySwip wrapper around the finance_advisor.pl knowledge base.

This module is the only place the Streamlit layer talks to Prolog.
See CLAUDE.md sections 6 and 8 for the public API contract.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from pyswip import Prolog
from pyswip.easy import Atom, Variable

KB_PATH = Path(__file__).resolve().parent.parent / "prolog" / "finance_advisor.pl"

# Modules consulted by finance_advisor.pl, in load order. Used to parse
# static rule/fact clauses for the Knowledge Base Viewer (CLAUDE.md 7.2,
# section 2) - the KB itself has no "list my static clauses" predicate,
# so the source files are the source of truth.
KB_MODULES = (
    "facts.pl",
    "calculations.pl",
    "foo_rules.pl",
    "health.pl",
    "recommendations.pl",
    "goal_advice.pl",
    "db_ops.pl",
)

# Dynamic predicates declared in facts.pl (CLAUDE.md section 4.1).
DYNAMIC_PREDICATES = (
    ("user_profile", 3),
    ("income", 2),
    ("expenses", 3),
    ("debt", 4),
    ("savings", 3),
    ("goal", 2),
)

# Only allow simple Prolog terms in user-supplied fact/query strings:
# atoms, numbers, variables, whitespace, and the punctuation needed to
# write a compound term, list, or findall/3 goal. This blocks
# directive-style payloads (e.g. ":- shell(...)") and comment/clause
# injection.
_SAFE_TERM_RE = re.compile(r"^[A-Za-z0-9_,\.\(\)\[\]\-\+\s'=]+$")

# Predicates that could affect the OS, halt the engine, or load
# arbitrary code are never allowed in user-supplied queries/facts,
# regardless of the character whitelist above.
_FORBIDDEN_PREDICATES = (
    "shell", "halt", "consult", "ensure_loaded", "use_module",
    "process_create", "open", "read_term", "see", "tell",
    "load_files", "qsave_program",
)

# Additionally forbidden in raw_query/3 (the read-only console):
# any direct KB mutation must go through assert_fact/retract_fact or
# the db_ops.pl helpers, never the free-form query box.
_WRITE_PREDICATES = (
    "assertz", "asserta", "assert(", "retract", "nb_setval", "nb_getval",
)


class PrologQueryError(Exception):
    """Raised when a user-supplied query or fact is rejected or fails."""


def _sanitise(term: str, allow_write: bool = False) -> str:
    """Reject Prolog strings that look like directives, reference
    forbidden predicates, or contain characters not needed for
    facts/queries against this KB.

    `allow_write=True` is used for assert_fact/retract_fact, where the
    caller wraps `term` in assertz(...)/retract(...) itself - so `term`
    is the fact being asserted/retracted, not a write predicate call.
    """
    term = term.strip().rstrip(".").strip()
    if not term:
        raise PrologQueryError("Empty query.")
    if term.startswith(":-") or term.startswith("?-"):
        raise PrologQueryError("Directives are not allowed.")
    if not _SAFE_TERM_RE.match(term):
        raise PrologQueryError("Query contains disallowed characters.")
    lowered = term.lower()
    for forbidden in _FORBIDDEN_PREDICATES:
        if forbidden in lowered:
            raise PrologQueryError(f"Use of '{forbidden}' is not allowed.")
    if not allow_write:
        for forbidden in _WRITE_PREDICATES:
            if forbidden in lowered:
                raise PrologQueryError(
                    f"'{forbidden}' is not allowed in queries; "
                    "use Add Fact / Remove Fact instead."
                )
    return term


def _term_to_value(value):
    """Convert a pyswip result value into a plain Python value."""
    if isinstance(value, Atom):
        return value.value
    if isinstance(value, Variable):
        return str(value)
    if isinstance(value, list):
        return [_term_to_value(v) for v in value]
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def _row_to_dict(row: dict) -> dict:
    return {k: _term_to_value(v) for k, v in row.items()}


_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_LINE_COMMENT_RE = re.compile(r"%.*$", re.MULTILINE)
_HEAD_RE = re.compile(r"^([a-z][a-zA-Z0-9_]*)\s*(\((.*)\))?$", re.DOTALL)


def _strip_comments(text: str) -> str:
    text = _BLOCK_COMMENT_RE.sub("", text)
    return _LINE_COMMENT_RE.sub("", text)


def _split_clauses(text: str) -> list[str]:
    """Split source text into top-level clauses on '.' followed by whitespace."""
    clauses = []
    buf: list[str] = []
    in_quote = None
    i = 0
    while i < len(text):
        c = text[i]
        if in_quote:
            buf.append(c)
            if c == in_quote:
                in_quote = None
        elif c in ("'", '"'):
            in_quote = c
            buf.append(c)
        elif c == "." and (i + 1 >= len(text) or text[i + 1] in " \t\r\n"):
            clause = "".join(buf).strip()
            if clause:
                clauses.append(clause)
            buf = []
        else:
            buf.append(c)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        clauses.append(tail)
    return clauses


def _split_top_level_args(args: str) -> list[str]:
    """Split a clause's argument string on top-level commas."""
    parts = []
    buf: list[str] = []
    depth = 0
    in_quote = None
    for c in args:
        if in_quote:
            buf.append(c)
            if c == in_quote:
                in_quote = None
        elif c in ("'", '"'):
            in_quote = c
            buf.append(c)
        elif c in "([{":
            depth += 1
            buf.append(c)
        elif c in ")]}":
            depth -= 1
            buf.append(c)
        elif c == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(c)
    parts.append("".join(buf))
    return parts


def _clause_head(clause: str) -> tuple[str, int, bool] | None:
    """Return (predicate_name, arity, is_rule) for a clause's head, or None
    if the clause is a directive (e.g. ':- dynamic ...') and has no head."""
    depth = 0
    in_quote = None
    head_end = len(clause)
    i = 0
    while i < len(clause) - 1:
        c = clause[i]
        if in_quote:
            if c == in_quote:
                in_quote = None
        elif c in ("'", '"'):
            in_quote = c
        elif c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif depth == 0 and clause[i:i + 2] == ":-":
            head_end = i
            break
        i += 1

    head = clause[:head_end].strip()
    is_rule = head_end < len(clause)
    if not head or head.startswith(":-"):
        return None

    match = _HEAD_RE.match(head)
    if not match:
        return None

    name = match.group(1)
    args = match.group(3)
    if args is None:
        arity = 0
    else:
        arity = len(_split_top_level_args(args))
    return name, arity, is_rule


def _parse_module_clauses(path: Path) -> list[dict]:
    """Parse a .pl source file into a list of {Predicate, Arity, Clause,
    Module, IsRule} dicts, skipping directives and comments."""
    text = _strip_comments(path.read_text(encoding="utf-8"))
    rows = []
    for clause in _split_clauses(text):
        head = _clause_head(clause)
        if head is None:
            continue
        name, arity, is_rule = head
        rows.append({
            "Predicate": name,
            "Arity": arity,
            "Clause": clause,
            "Module": path.name,
            "IsRule": is_rule,
        })
    return rows


class FinanceEngine:
    """Thin wrapper around pyswip.Prolog for the finance advisor KB."""

    def __init__(self, kb_path: str | None = None):
        if "SWI_HOME_DIR" not in os.environ:
            swi_home = os.environ.get("SWI_HOME_DIR")
            if swi_home:
                os.environ["SWI_HOME_DIR"] = swi_home

        self.prolog = Prolog()
        path = kb_path or str(KB_PATH)
        self.prolog.consult(path)

    # ------------------------------------------------------------
    # Profile / KB population
    # ------------------------------------------------------------

    def load_profile(self, age, occupation, income, needs, wants,
                      emergency_fund, investment, goal):
        """Reset the KB and assert a fresh user profile."""
        self.reset()
        self._do(f"assertz(user_profile(user, {int(age)}, {occupation}))")
        self._do(f"assertz(income(user, {self._num(income)}))")
        self._do(f"assertz(expenses(user, needs, {self._num(needs)}))")
        self._do(f"assertz(expenses(user, wants, {self._num(wants)}))")
        self._do(f"assertz(savings(user, emergency_fund, {self._num(emergency_fund)}))")
        self._do(f"assertz(savings(user, investment, {self._num(investment)}))")
        self._do(f"assertz(goal(user, {goal}))")

    @staticmethod
    def _num(value) -> str:
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

    def _do(self, goal: str) -> bool:
        try:
            return bool(list(self.prolog.query(goal)))
        except Exception as exc:  # PrologError on bad syntax
            raise PrologQueryError(str(exc)) from exc

    def _query_all(self, goal: str) -> list[dict]:
        """Run a query to completion and return all result rows.

        pyswip's query() is a generator backed by an open Prolog query
        handle; leaving it unconsumed raises NestedQueryError on the
        next call. Always materialise to a list before returning.
        """
        try:
            return list(self.prolog.query(goal))
        except Exception as exc:  # PrologError on bad syntax
            raise PrologQueryError(str(exc)) from exc

    def _query_first(self, goal: str, var: str = "X"):
        """Return the value bound to `var` in the first solution, or None."""
        rows = self._query_all(goal)
        if not rows:
            return None
        return _term_to_value(rows[0][var])

    # ------------------------------------------------------------
    # Dynamic KB operations (delegate to db_ops.pl)
    # ------------------------------------------------------------

    def add_debt(self, type_: str, amount, rate):
        return self._do(f"add_debt({type_}, {self._num(amount)}, {self._num(rate)})")

    def clear_debt(self, type_: str):
        return self._do(f"clear_debt({type_})")

    def update_income(self, amount):
        return self._do(f"update_income({self._num(amount)})")

    def update_savings(self, type_: str, amount):
        return self._do(f"update_savings({type_}, {self._num(amount)})")

    def reset(self):
        return self._do("clear_user_data")

    # ------------------------------------------------------------
    # Inference results
    # ------------------------------------------------------------

    def financial_health(self) -> str | None:
        return self._query_first("financial_health(user, X)")

    def gate_statuses(self) -> dict:
        """Status + pass/fail for all five FOO gates."""
        investment_ready = self._do("investment_ready(user)")
        return {
            "budget": {
                "status": self._query_first("budget_status(user, X)"),
                "passed": self._do("budget_gate_passed(user)"),
            },
            "debt": {
                "status": self._query_first("debt_status(user, X)"),
                "passed": self._do("debt_gate_passed(user)"),
            },
            "emergency": {
                "status": self._query_first("emergency_fund_status(user, X)"),
                "passed": self._do("emergency_gate_passed(user)"),
            },
            "savings": {
                "status": self._query_first("savings_status(user, X)"),
                "passed": self._do("savings_gate_passed(user)"),
            },
            "investment": {
                "status": "ready" if investment_ready else "not_ready",
                "passed": investment_ready,
            },
        }

    def metrics(self) -> dict:
        """Savings rate, DTI, net worth, and emergency fund coverage."""
        amount = self._query_first("emergency_fund_amount(user, X)")
        target = self._query_first("emergency_fund_target(user, X)")
        expenses = self._query_first("total_expenses(user, X)")

        months = None
        if amount is not None and expenses:
            months = amount / expenses

        return {
            "savings_rate": self._query_first("savings_rate(user, X)"),
            "debt_to_income": self._query_first("debt_to_income(user, X)"),
            "net_worth": self._query_first("net_worth(user, X)"),
            "emergency_fund_amount": amount,
            "emergency_fund_target": target,
            "emergency_fund_months": months,
        }

    def recommendations(self) -> list[tuple[int, str]]:
        """All applicable recommendations, sorted by FOO step number."""
        rows = self._query_all("recommend_step(user, S, A)")
        results = [(_term_to_value(r["S"]), _term_to_value(r["A"])) for r in rows]
        results.sort(key=lambda pair: pair[0])
        return results

    def top_recommendation(self) -> str | None:
        return self._query_first("top_recommendation(user, X)")

    def goal_advice(self) -> str | None:
        return self._query_first("goal_advice(user, X)")

    def age_advice(self) -> str | None:
        return self._query_first("age_advice(user, X)")

    def all_debts(self) -> list[tuple[str, float]]:
        """List of (Type, Rate) pairs from db_ops.pl's all_debts/2 (bagof)."""
        pair_re = re.compile(r"^-\((\w+),\s*([\d.]+)\)$")
        rows = self._query_all("all_debts(user, L)")
        if not rows:
            return []
        pairs = []
        for item in _term_to_value(rows[0]["L"]) or []:
            match = pair_re.match(str(item))
            if match:
                type_, rate = match.groups()
                rate_val = float(rate) if "." in rate else int(rate)
                pairs.append((type_, rate_val))
        return pairs

    # ------------------------------------------------------------
    # KB introspection (Section 1 + 2 of the dashboard)
    # ------------------------------------------------------------

    def static_clauses(self) -> list[dict]:
        """Static facts/rules parsed from the prolog/*.pl source modules."""
        kb_dir = KB_PATH.parent
        rows = []
        for module in KB_MODULES:
            rows.extend(_parse_module_clauses(kb_dir / module))
        return rows

    def dynamic_clauses(self) -> list[dict]:
        """Currently asserted dynamic facts, one row per clause."""
        rows = []
        for name, arity in DYNAMIC_PREDICATES:
            args = ", ".join(f"A{i}" for i in range(arity))
            goal = f"functor(T, {name}, {arity}), clause(T, true), T =.. [_{', ' + args if args else ''}]"
            for row in self._query_all(goal):
                values = [_term_to_value(row[f"A{i}"]) for i in range(arity)]
                clause_text = f"{name}({', '.join(str(v) for v in values)})"
                rows.append({
                    "Predicate": name,
                    "Arity": arity,
                    "Clause": clause_text,
                    "Module": "dynamic (session)",
                    "IsRule": False,
                })
        return rows

    def kb_overview(self) -> dict:
        """Counts for the Section 1 summary cards."""
        static_rows = self.static_clauses()
        dynamic_rows = self.dynamic_clauses()
        total_rules = sum(1 for r in static_rows if r["IsRule"])
        total_static_facts = sum(1 for r in static_rows if not r["IsRule"])
        return {
            "total_facts": total_static_facts + len(dynamic_rows),
            "total_rules": total_rules,
            "dynamic_facts": len(dynamic_rows),
        }

    # ------------------------------------------------------------
    # KB mutation / raw query console
    # ------------------------------------------------------------

    def assert_fact(self, fact: str):
        term = _sanitise(fact, allow_write=True)
        return self._do(f"assertz({term})")

    def retract_fact(self, fact: str):
        term = _sanitise(fact, allow_write=True)
        return self._do(f"retract({term})")

    def raw_query(self, query: str) -> list[dict]:
        term = _sanitise(query)
        return [_row_to_dict(row) for row in self._query_all(term)]

    def has_profile(self) -> bool:
        return self._do("user_profile(user, _, _)")
