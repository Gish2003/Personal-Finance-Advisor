"""Formatting helpers for displaying Prolog terms and results in Streamlit."""

# Color tokens (CLAUDE.md section 7.3 - light theme palette)
COLOR_SUCCESS = "#16A34A"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER = "#DC2626"
COLOR_NEUTRAL = "#475569"
COLOR_ACCENT = "#2563EB"

HEALTH_COLORS = {
    "excellent": COLOR_SUCCESS,
    "good": COLOR_SUCCESS,
    "moderate": COLOR_WARNING,
    "poor": COLOR_DANGER,
    "critical": COLOR_DANGER,
}

# Per-gate status -> (icon, color)
GATE_STATUS_STYLE = {
    # budget_status/2
    "healthy": ("✅", COLOR_SUCCESS),
    "warning": ("⚠️", COLOR_WARNING),
    "overspending_wants": ("⚠️", COLOR_WARNING),
    "poor": ("⚠️", COLOR_WARNING),
    "critical": ("❌", COLOR_DANGER),
    # debt_status/2
    "debt_free": ("✅", COLOR_SUCCESS),
    "manageable": ("✅", COLOR_SUCCESS),
    "high_interest": ("⚠️", COLOR_WARNING),
    "overloaded": ("❌", COLOR_DANGER),
    # emergency_fund_status/2
    "adequate": ("✅", COLOR_SUCCESS),
    "partial": ("⚠️", COLOR_WARNING),
    "none": ("❌", COLOR_DANGER),
    # savings_status/2
    "excellent": ("✅", COLOR_SUCCESS),
    "low": ("⚠️", COLOR_WARNING),
    # investment readiness
    "ready": ("✅", COLOR_SUCCESS),
    "not_ready": ("⚠️", COLOR_WARNING),
}


def health_color(health: str | None) -> str:
    return HEALTH_COLORS.get(health or "", COLOR_NEUTRAL)


def gate_icon_color(status: str | None) -> tuple[str, str]:
    return GATE_STATUS_STYLE.get(status or "", ("❓", COLOR_NEUTRAL))


def format_status_label(status: str | None) -> str:
    if not status:
        return "unknown"
    return status.replace("_", " ").title()


def format_currency(value) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def format_percent(value, decimals: int = 1) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value):.{decimals}f}%"
    except (TypeError, ValueError):
        return str(value)


def format_months(value) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value):.1f} months"
    except (TypeError, ValueError):
        return str(value)


def badge_html(text: str, color: str) -> str:
    return (
        f'<span style="background-color:{color};color:white;'
        f'padding:0.25em 0.75em;border-radius:0.5em;font-weight:600;">'
        f"{text}</span>"
    )


def step_name(step: int) -> str:
    names = {
        1: "Budget (50/30/20)",
        2: "High-Interest Debt",
        3: "Emergency Fund",
        4: "Savings Rate",
        5: "Investment Readiness",
    }
    return names.get(step, f"Step {step}")


def format_prolog_value(value) -> str:
    if isinstance(value, list):
        return "[" + ", ".join(format_prolog_value(v) for v in value) + "]"
    return str(value)


def format_query_result(rows: list[dict]) -> str:
    """Render raw_query() rows as Prolog-style binding lines for st.code()."""
    if not rows:
        return "false."
    lines = []
    for row in rows:
        if not row:
            lines.append("true.")
            continue
        bindings = ", ".join(f"{k} = {format_prolog_value(v)}" for k, v in row.items())
        lines.append(bindings + ".")
    return "\n".join(lines)
