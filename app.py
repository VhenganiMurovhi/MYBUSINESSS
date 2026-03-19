import streamlit as st
from utilis.calculations import prepare_monthly_summary, calculate_kpis
from utilis.risk_model import calculate_risk_score, classify_risk

st.set_page_config(page_title="SME Financial Intelligence", page_icon="📊", layout="wide")

st.title("SME Financial Intelligence")
st.caption("Upload business data and get financial clarity, risk insight, and simple decision support.")

with st.sidebar:
    st.header("Get Started")
    st.markdown(
        """
        **CSV columns expected:**
        - date
        - revenue
        - expenses
        - cash_balance *(optional)*

        Example date format: `2026-03-01`
        """
    )

uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

if not uploaded_file:
    st.info("Upload a CSV file to begin. Use the sample file in `data/sample_business_data.csv` as a template.")
    st.stop()

summary_df = prepare_monthly_summary(uploaded_file)
kpis = calculate_kpis(summary_df)
risk_score = calculate_risk_score(kpis)
risk_level = classify_risk(risk_score)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Revenue", f"R{kpis['total_revenue']:,.0f}")
col2.metric("Expenses", f"R{kpis['total_expenses']:,.0f}")
col3.metric("Profit", f"R{kpis['total_profit']:,.0f}")
col4.metric("Risk Score", f"{risk_score}/100")

st.subheader("Snapshot")
left, right = st.columns([2, 1])
with left:
    st.line_chart(summary_df.set_index("month")[["revenue", "expenses", "profit"]])
with right:
    st.metric("Profit Margin", f"{kpis['profit_margin']:.1%}")
    st.metric("Expense Ratio", f"{kpis['expense_ratio']:.1%}")
    st.metric("Cash Runway", f"{kpis['cash_runway_months']:.1f} months")
    st.metric("Risk Level", risk_level)

st.subheader("Core Interpretation")
messages = []
if kpis['profit_margin'] < 0.10:
    messages.append("Profit margin is thin. Price discipline or expense cuts may be needed.")
if kpis['expense_ratio'] > 0.75:
    messages.append("Expenses are consuming a large share of revenue.")
if kpis['cash_runway_months'] < 3:
    messages.append("Cash runway is short. Near-term liquidity is a priority.")
if not messages:
    messages.append("The business appears relatively stable on the current inputs.")

for m in messages:
    st.write(f"- {m}")

st.success("Open the pages in the sidebar for Financial Health, Risk Intelligence, Scenarios, and Pricing.")