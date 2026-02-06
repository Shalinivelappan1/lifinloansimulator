import streamlit as st
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Debt Decision Lab", page_icon="🧪", layout="centered")

# =========================
# FINANCE FUNCTIONS
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
st.caption("Explore loans, escape faster, and decide smarter")

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
tab1, tab2, tab3 = st.tabs([
    "🧾 EMI",
    "🧨 Prepayment",
    "⚖️ Decision + NPV Lab"
])

# ======================================================
# TAB 3 — DECISION LAB WITH NPV
# ======================================================
with tab3:

    st.header("🏠 Buy vs Rent NPV Decision Lab")

    rent = st.number_input("Monthly Rent (₹)", value=8000)
    discount_rate = st.number_input("Discount Rate (%)", value=8.0)
    price_growth = st.number_input("House Price Growth (%)", value=3.0)

    # =========================
    # SCENARIO BUTTONS
    # =========================
    st.subheader("🎬 Case Scenario Buttons")

    col1, col2, col3, col4 = st.columns(4)

    if col1.button("Scenario 1: No price growth"):
        price_growth = 0

    if col2.button("Scenario 2: Price +10%"):
        price_growth = 10

    if col3.button("Scenario 3: Rate shock"):
        interest_rate += 1

    if col4.button("Scenario 4: Rent rises"):
        rent *= 1.25

    emi, n, r = calculate_emi(loan_amount, interest_rate, years)

    # =========================
    # NPV CALCULATION
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
    c2.metric("PV Rent", f"₹ {npv_rent:,.0_
