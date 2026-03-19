import streamlit as st
from utilis.calculations import prepare_monthly_summary, calculate_kpis, apply_scenario
from utilis.risk_model import calculate_risk_score, classify_risk

st.title("Scenario Engine")
uploaded_file = st.file_uploader("Upload your CSV", type=["csv"], key="scen")
if not uploaded_file:
    st.info("Upload your CSV to run scenarios.")
    st.stop()

summary_df = prepare_monthly_summary(uploaded_file)
base_kpis = calculate_kpis(summary_df)
base_risk = calculate_risk_score(base_kpis)

st.subheader("Scenario Inputs")
rev_change = st.slider("Revenue shock %", min_value=-50, max_value=20, value=-20, step=5)
exp_change = st.slider("Expense shock %", min_value=-20, max_value=50, value=10, step=5)

scenario_df = apply_scenario(summary_df, revenue_pct_change=rev_change / 100, expense_pct_change=exp_change / 100)
scenario_kpis = calculate_kpis(scenario_df)
scenario_risk = calculate_risk_score(scenario_kpis)

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Base")
    st.metric("Profit", f"R{base_kpis['total_profit']:,.0f}")
    st.metric("Runway", f"{base_kpis['cash_runway_months']:.1f} months")
    st.metric("Risk", f"{base_risk}/100 ({classify_risk(base_risk)})")
with col2:
    st.markdown("### Scenario")
    st.metric("Profit", f"R{scenario_kpis['total_profit']:,.0f}")
    st.metric("Runway", f"{scenario_kpis['cash_runway_months']:.1f} months")
    st.metric("Risk", f"{scenario_risk}/100 ({classify_risk(scenario_risk)})")

st.line_chart(scenario_df.set_index("month")[["revenue", "expenses", "profit"]])