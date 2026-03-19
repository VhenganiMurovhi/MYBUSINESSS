import streamlit as st
from utilis.calculations import prepare_monthly_summary, calculate_kpis

st.title("Financial Health")
uploaded_file = st.file_uploader("Upload the same CSV", type=["csv"], key='fh')
if not uploaded_file:
    st.info("Please upload the same CSV file to see the financial health analysis.")
    st.stop()

summary_df = prepare_monthly_summary(uploaded_file)
kpis = calculate_kpis(summary_df)

col1, col2, col3 = st.columns(3)
col1.metric("Average Monthly Revenue", f"R{kpis['avg_monthly_revenue']:,.0f}")
col2.metric("Average Monthly Expenses", f"R{kpis['avg_monthly_expenses']:,.0f}")
col3.metric("Average Monthly Profit", f"R{kpis['avg_monthly_profit']:,.0f}")

st.subheader("Monthly Summary")
st.dataframe(summary_df, use_container_width=True)

st.subheader("Interpretation")
st.write(f"Profit margin: **{kpis['profit_margin']:.1%}**")
st.write(f"Expense ratio: **{kpis['expense_ratio']:.1%}**")
st.write(f"Cash runway: **{kpis['cash_runway_months']:.1f} months**")

if kpis['profit_margin'] < 0.05:
    st.warning("Profitability is fragile. Small revenue shocks could push the business into loss.")
elif kpis['profit_margin'] < 0.15:
    st.info("Profitability exists, but the business still has limited buffer.")
else:
    st.success("Profitability looks healthier on the current data.")