import streamlit as st

st.title("Pricing")
st.caption("Simple offers for small businesses.")

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Starter")
    st.write("**R599 once-off**")
    st.write("- Basic financial summary")
    st.write("- Profit, expense, cash view")
    st.write("- 1 dashboard screenshot")
with col2:
    st.subheader("Growth")
    st.write("**R1099 once-off**")
    st.write("- Everything in Starter")
    st.write("- Risk score")
    st.write("- 3-month view")
    st.write("- Short written recommendations")
with col3:
    st.subheader("Decision Pack")
    st.write("**R1499 once-off**")
    st.write("- Everything in Growth")
    st.write("- Scenario testing")
    st.write("- PDF-style summary")
    st.write("- Priority turnaround")

st.divider()
st.subheader("Suggested sales line")
st.code(
    "I help small businesses understand profitability, financial health, and hidden risk using a simple analytics dashboard.",
    language="text",
)