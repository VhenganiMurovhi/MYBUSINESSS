from __future__ import annotations

import pandas as pd


DATE_CANDIDATES = [
    "date", "transaction_date", "day", "created_at", "timestamp"
]

AMOUNT_CANDIDATES = [
    "amount", "transaction_amount", "value", "total", "amt"
]

REVENUE_CANDIDATES = [
    "revenue", "income", "sales", "credit_amount", "money_in"
]

EXPENSE_CANDIDATES = [
    "expenses", "expense", "cost", "debit_amount", "money_out"
]

TYPE_CANDIDATES = [
    "type", "transaction_type", "entry_type", "flow", "dr_cr", "credit_debit"
]

CATEGORY_CANDIDATES = [
    "category", "transaction_category", "account", "group", "class"
]

CASH_BALANCE_CANDIDATES = [
    "cash_balance", "balance", "closing_balance", "bank_balance"
]


def find_first_matching_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    cols = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in cols:
            return cols[candidate.lower()]
    return None


def normalize_type(value: str) -> str:
    if pd.isna(value):
        return "unknown"

    value = str(value).strip().lower()

    credit_values = {
        "credit", "cr", "income", "revenue", "sale", "sales", "money in", "inflow", "deposit"
    }
    debit_values = {
        "debit", "dr", "expense", "cost", "payment", "money out", "outflow", "withdrawal"
    }

    if value in credit_values:
        return "credit"
    if value in debit_values:
        return "debit"

    return "unknown"


def standardize_transactions(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    if df.empty:
        raise ValueError("The uploaded CSV is empty.")

    original_columns = df.columns.tolist()
    df.columns = [c.strip().lower() for c in df.columns]

    date_col = find_first_matching_column(df, DATE_CANDIDATES)
    amount_col = find_first_matching_column(df, AMOUNT_CANDIDATES)
    revenue_col = find_first_matching_column(df, REVENUE_CANDIDATES)
    expense_col = find_first_matching_column(df, EXPENSE_CANDIDATES)
    type_col = find_first_matching_column(df, TYPE_CANDIDATES)
    category_col = find_first_matching_column(df, CATEGORY_CANDIDATES)
    cash_balance_col = find_first_matching_column(df, CASH_BALANCE_CANDIDATES)

    if not date_col:
        raise ValueError(
            "No date column found. Include one like: date, transaction_date, day, created_at."
        )

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col]).copy()

    if df.empty:
        raise ValueError("No valid dates were found in the CSV.")

    standardized = pd.DataFrame()
    standardized["date"] = df[date_col]

    if category_col:
        standardized["category"] = df[category_col].astype(str)
    else:
        standardized["category"] = "Uncategorized"

    if cash_balance_col:
        standardized["cash_balance"] = pd.to_numeric(df[cash_balance_col], errors="coerce").fillna(0.0)
    else:
        standardized["cash_balance"] = 0.0

    # Case 1: CSV already has separate revenue and expense columns
    if revenue_col or expense_col:
        standardized["revenue"] = (
            pd.to_numeric(df[revenue_col], errors="coerce").fillna(0.0) if revenue_col else 0.0
        )
        standardized["expenses"] = (
            pd.to_numeric(df[expense_col], errors="coerce").fillna(0.0) if expense_col else 0.0
        )

    # Case 2: CSV has amount + transaction type
    elif amount_col and type_col:
        amount_series = pd.to_numeric(df[amount_col], errors="coerce").fillna(0.0)
        type_series = df[type_col].apply(normalize_type)

        standardized["revenue"] = amount_series.where(type_series == "credit", 0.0)
        standardized["expenses"] = amount_series.where(type_series == "debit", 0.0)

    # Case 3: CSV has just amount, where positive = revenue and negative = expense
    elif amount_col:
        amount_series = pd.to_numeric(df[amount_col], errors="coerce").fillna(0.0)
        standardized["revenue"] = amount_series.where(amount_series > 0, 0.0)
        standardized["expenses"] = (-amount_series).where(amount_series < 0, 0.0)

    else:
        raise ValueError(
            "Could not detect money columns. Include either:\n"
            "- revenue and/or expenses columns\n"
            "- amount + type/transaction_type column\n"
            "- or a single amount column with positive/negative values"
        )

    standardized["profit"] = standardized["revenue"] - standardized["expenses"]
    standardized["month"] = standardized["date"].dt.to_period("M").astype(str)

    return standardized


def prepare_monthly_summary(file) -> pd.DataFrame:
    transactions = standardize_transactions(file)

    monthly = (
        transactions.groupby("month", as_index=False)[["revenue", "expenses", "cash_balance"]]
        .sum()
        .sort_values("month")
    )

    monthly["profit"] = monthly["revenue"] - monthly["expenses"]
    return monthly


def prepare_category_summary(file) -> pd.DataFrame:
    transactions = standardize_transactions(file)

    category_summary = (
        transactions.groupby("category", as_index=False)[["revenue", "expenses"]]
        .sum()
        .sort_values(["expenses", "revenue"], ascending=False)
    )

    category_summary["net"] = category_summary["revenue"] - category_summary["expenses"]
    return category_summary


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