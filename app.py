import streamlit as st
from utilis.calculations import (
    prepare_monthly_summary,
    calculate_kpis,
    prepare_category_summary,
)
from utilis.risk_model import calculate_risk_score, classify_risk

st.set_page_config(page_title="SME Financial Intelligence", page_icon="📊", layout="wide")

st.title("SME Financial Intelligence")
st.caption("Upload business transaction data and get financial clarity, risk insight, and decision support.")

with st.sidebar:
    st.header("Supported CSV Formats")
    st.markdown(
        """
        **Format A**
        - date
        - revenue
        - expenses
        - category *(optional)*
        - cash_balance *(optional)*

        **Format B**
        - date
        - amount
        - type *(credit/debit)*
        - category *(optional)*
        - cash_balance *(optional)*

        **Format C**
        - date
        - amount *(positive = revenue, negative = expense)*
        - category *(optional)*
        - cash_balance *(optional)*

        **Recognized examples**
        - date / transaction_date
        - amount / value / total
        - revenue / income / sales
        - expenses / expense / cost
        - type / transaction_type / dr_cr
        - category / account / group
        """
    )

uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

if not uploaded_file:
    st.info("Upload your CSV to begin.")
    st.stop()

try:
    summary_df = prepare_monthly_summary(uploaded_file)
    uploaded_file.seek(0)
    category_df = prepare_category_summary(uploaded_file)
    kpis = calculate_kpis(summary_df)
    risk_score = calculate_risk_score(kpis)
    risk_level = classify_risk(risk_score)
except Exception as e:
    st.error(f"Error processing file: {e}")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Revenue", f"R{kpis['total_revenue']:,.0f}")
col2.metric("Expenses", f"R{kpis['total_expenses']:,.0f}")
col3.metric("Profit", f"R{kpis['total_profit']:,.0f}")
col4.metric("Risk Score", f"{risk_score}/100")

st.subheader("Monthly Snapshot")
left, right = st.columns([2, 1])

with left:
    st.line_chart(summary_df.set_index("month")[["revenue", "expenses", "profit"]])

with right:
    st.metric("Profit Margin", f"{kpis['profit_margin']:.1%}")
    st.metric("Expense Ratio", f"{kpis['expense_ratio']:.1%}")
    st.metric("Cash Runway", f"{kpis['cash_runway_months']:.1f} months")
    st.metric("Risk Level", risk_level)

st.subheader("Category Breakdown")
st.dataframe(category_df, use_container_width=True)

if not category_df.empty:
    top_expense_categories = category_df.sort_values("expenses", ascending=False).head(5)
    st.bar_chart(top_expense_categories.set_index("category")["expenses"])

st.subheader("Core Interpretation")
messages = []

if kpis["profit_margin"] < 0.10:
    messages.append("Profit margin is thin. The business may need pricing improvement or cost control.")
if kpis["expense_ratio"] > 0.75:
    messages.append("Expenses consume a large portion of revenue.")
if kpis["cash_runway_months"] < 3:
    messages.append("Cash runway is short. Liquidity pressure may emerge quickly.")
if risk_level == "High":
    messages.append("Current business conditions indicate elevated financial vulnerability.")
if category_df["expenses"].sum() > 0 and len(category_df) > 0:
    biggest_expense = category_df.sort_values("expenses", ascending=False).iloc[0]["category"]
    messages.append(f"The biggest expense pressure appears to come from: {biggest_expense}.")

if not messages:
    messages.append("The business appears relatively stable based on the uploaded data.")

for m in messages:
    st.write(f"- {m}")

st.success("You can now use your transaction data, not only simple revenue/expense summaries.")