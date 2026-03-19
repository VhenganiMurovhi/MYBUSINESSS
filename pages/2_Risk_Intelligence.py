import streamlit as st
from utilis.calculations import prepare_monthly_summary,calculate_kpis
from utilis.risk_model import calculate_risk_score, classify_risk, explain_risk_components
st.title("Risk Intelligence")
uploaded_file = st.file_uploader("Upload the same CSV", type=["csv"], key='risk')

if not uploaded_file:
    st.info("Please upload the same CSV file to Calculate your business risk.")
    st.stop()

summary_df = prepare_monthly_summary(uploaded_file)
kpis = calculate_kpis(summary_df)
risk_score = calculate_risk_score(kpis)
risk_level = classify_risk(risk_score)
components= explain_risk_components(kpis)

col1, col2 = st.columns(2)
col1.metric("Risk Score", f"{risk_score}/100")
col2.metric("Risk Level", risk_level)

st.progress(min(risk_score, 100)/100)

st.subheader("Risk Components Breakdown")
for name, value in components.items():
    st.write(f"**{name}:**{value}")


st.subheader("Decision View")
if risk_level == "High":
    st.error("The business is at high risk. Immediate action is recommended to reduce expenses, improve profitability, or secure additional funding.")
elif risk_level == "Moderate":
    st.warning("The business is at moderate risk. Consider strategies to improve financial health and monitor key metrics closely.")
else:
    st.success("The business is at low risk. Continue to manage finances prudently and monitor for any changes in key metrics.Though ongoing monitoring is important")


