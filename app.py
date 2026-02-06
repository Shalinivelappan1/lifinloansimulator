import streamlit as st
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Debt Decision Lab", page_icon="🧪")

# =========================
# FUNCTIONS
# =========================
def calculate_emi(principal, annual_rate, years):
    r = annual_rate / (12 * 100)
    n = years * 12
    if r == 0:
        emi = principal / n
    else:
        emi = principal * r * (1 + r)**n / ((1 + r)**n - 1)
    return emi, n, r

def npv_stream(payment, discount_rate, months):
    r = discount_rate / (12 * 100)
    if r == 0:
        return payment * months
    return payment * (1 - (1 + r)**(-months)) / r

# =========================
# HEADER
# =========================
st.title("🧪 Debt Decision Lab")

# =========================
# GLOBAL INPUTS
# =========================
loan_amount = st.number_input("Loan Amount (₹)", value=500000)
interest_rate = st.number_input("Interest Rate (%)", value=10.0)
years = st.number_input("Tenure (Years)", value=5)

emi, n, r = calculate_emi(loan_amount, interest_rate, years)
st.write(f"💸 EMI: **₹ {emi:,.0f}**")

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs(["EMI", "Prepayment", "Decision Lab"])

# ======================================================
# TAB 3 — DECISION + NPV
# ======================================================
with tab3:

    st.header("🏠 Buy vs Rent NPV Lab")

    rent = st.number_input("Monthly Rent (₹)", value=8000)
    discount_rate = st.number_input("Discount Rate (%)", value=8.0)
    price_growth = st.number_input("Price Growth (%)", value=3.0)

    # =========================
    # SCENARIO BUTTONS
    # =========================
    st.subheader("🎬 Case Scenarios")

    col1, col2, col3, col4 = st.columns(4)

    if col1.button("Scenario 1"):
        price_growth = 0

    if col2.button("Scenario 2"):
        price_growth = 10

    if col3.button("Scenario 3"):
        interest_rate += 1

    if col4.button("Scenario 4"):
        rent *= 1.25

    emi, n, r = calculate_emi(loan_amount, interest_rate, years)

    # =========================
    # NPV
    # =========================
    pv_buy = npv_stream(emi, discount_rate, n)
    pv_rent = npv_stream(rent, discount_rate, n)

    future_price = loan_amount * ((1 + price_growth/100) ** years)
    pv_resale = future_price / ((1 + discount_rate/100) ** years)

    npv_buy = pv_buy - pv_resale
    npv_rent = pv_rent
    npv_diff = npv_buy - npv_rent

    st.subheader("📊 NPV Results")

    c1, c2, c3 = st.columns(3)
    c1.metric("PV Buy", f"₹ {npv_buy:,.0f}")
    c2.metric("PV Rent", f"₹ {npv_rent:,.0f}")
    c3.metric("NPV (Buy-Rent)", f"₹ {npv_diff:,.0f}")

    if npv_diff < 0:
        st.success("Buying wins")
    else:
        st.warning("Renting wins")

    # =========================
    # GRAPH: NPV vs RATE
    # =========================
    st.subheader("📈 NPV vs Interest Rate")

    rates = np.linspace(2, 15, 30)
    npvs = []

    for rate in rates:
        emi_temp, _, _ = calculate_emi(loan_amount, rate, years)
        pv_buy_temp = npv_stream(emi_temp, discount_rate, n)
        future_price_temp = loan_amount * ((1 + price_growth/100) ** years)
        pv_resale_temp = future_price_temp / ((1 + discount_rate/100) ** years)
        npv_temp = (pv_buy_temp - pv_resale_temp) - pv_rent
        npvs.append(npv_temp)

    fig, ax = plt.subplots()
    ax.plot(rates, npvs)
    ax.axhline(0, linestyle="--")
    ax.set_xlabel("Interest Rate")
    ax.set_ylabel("NPV")
    st.pyplot(fig)

    # =========================
    # HEATMAP
    # =========================
    st.subheader("🔥 Sensitivity Heatmap")

    rate_range = np.linspace(5, 15, 12)
    growth_range = np.linspace(0, 10, 12)

    heat = []

    for g in growth_range:
        row = []
        for rate in rate_range:
            emi_temp, _, _ = calculate_emi(loan_amount, rate, years)
            pv_buy_temp = npv_stream(emi_temp, discount_rate, n)
            future_price_temp = loan_amount * ((1 + g/100) ** years)
            pv_resale_temp = future_price_temp / ((1 + discount_rate/100) ** years)
            npv_temp = (pv_buy_temp - pv_resale_temp) - pv_rent
            row.append(npv_temp)
        heat.append(row)

    heat_df = pd.DataFrame(heat, index=np.round(growth_range,1), columns=np.round(rate_range,1))

    fig2, ax2 = plt.subplots()
    sns.heatmap(heat_df, cmap="RdYlGn", center=0)
    ax2.set_xlabel("Interest Rate")
    ax2.set_ylabel("Price Growth")
    st.pyplot(fig2)
