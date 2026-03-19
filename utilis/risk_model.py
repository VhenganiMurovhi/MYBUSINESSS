from __future__ import annotations


def _clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


def calculate_risk_score(kpis: dict) -> int:
    expense_component = _clamp(kpis["expense_ratio"] * 40)
    profit_inverse = max(0.0, 1 - kpis["profit_margin"])
    profit_component = _clamp(profit_inverse * 30)
    runway_risk = 1.0 if kpis["cash_runway_months"] <= 1 else max(0.0, 1 - (kpis["cash_runway_months"] / 12))
    runway_component = _clamp(runway_risk * 30)
    return round(expense_component + profit_component + runway_component)


def classify_risk(score: int) -> str:
    if score >= 70:
        return "High"
    if score >= 40:
        return "Moderate"
    return "Low"


def explain_risk_components(kpis: dict) -> dict:
    return {
        "Expense pressure": f"Expense ratio is {kpis['expense_ratio']:.1%} of revenue.",
        "Profit resilience": f"Profit margin is {kpis['profit_margin']:.1%}.",
        "Liquidity buffer": f"Estimated cash runway is {kpis['cash_runway_months']:.1f} months.",
    }