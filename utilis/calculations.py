
from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = {"date", "revenue", "expenses"}


def prepare_monthly_summary(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    missing = REQUIRED_COLUMNS - set(df.columns.str.lower())
    df.columns = [c.lower() for c in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    df["date"] = pd.to_datetime(df["date"])
    if "cash_balance" not in df.columns:
        df["cash_balance"] = 0.0

    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly = (
        df.groupby("month", as_index=False)[["revenue", "expenses", "cash_balance"]]
        .sum()
        .sort_values("month")
    )
    monthly["profit"] = monthly["revenue"] - monthly["expenses"]
    return monthly


def calculate_kpis(summary_df: pd.DataFrame) -> dict:
    total_revenue = float(summary_df["revenue"].sum())
    total_expenses = float(summary_df["expenses"].sum())
    total_profit = float(summary_df["profit"].sum())
    avg_monthly_revenue = float(summary_df["revenue"].mean()) if not summary_df.empty else 0.0
    avg_monthly_expenses = float(summary_df["expenses"].mean()) if not summary_df.empty else 0.0
    avg_monthly_profit = float(summary_df["profit"].mean()) if not summary_df.empty else 0.0
    ending_cash = float(summary_df["cash_balance"].iloc[-1]) if not summary_df.empty else 0.0
    burn = max(avg_monthly_expenses - avg_monthly_revenue, 0)
    cash_runway_months = (ending_cash / burn) if burn > 0 else 12.0

    profit_margin = (total_profit / total_revenue) if total_revenue > 0 else 0.0
    expense_ratio = (total_expenses / total_revenue) if total_revenue > 0 else 1.0

    return {
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "total_profit": total_profit,
        "avg_monthly_revenue": avg_monthly_revenue,
        "avg_monthly_expenses": avg_monthly_expenses,
        "avg_monthly_profit": avg_monthly_profit,
        "profit_margin": profit_margin,
        "expense_ratio": expense_ratio,
        "cash_runway_months": cash_runway_months,
    }


def apply_scenario(summary_df: pd.DataFrame, revenue_pct_change: float, expense_pct_change: float) -> pd.DataFrame:
    scenario_df = summary_df.copy()
    scenario_df["revenue"] = scenario_df["revenue"] * (1 + revenue_pct_change)
    scenario_df["expenses"] = scenario_df["expenses"] * (1 + expense_pct_change)
    scenario_df["profit"] = scenario_df["revenue"] - scenario_df["expenses"]
    return scenario_df