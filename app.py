import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="Debt Decision Lab", page_icon="🧪")

# =========================================================
# FUNCTIONS
# =========================================================
def calculate_emi(principal, annual_rate, years):
    r = annual_rate / (12 * 100)
    n = years * 12
    if r == 0:
        emi = principal / n
    else:
        emi = principal * r * (1 + r)**n / ((1 + r)**n - 1)
    return emi, n, r

def remaining_balance(P, r, emi, k):
    return P * (1 + r)**k - emi * ((1 + r)**k - 1) / r

def future_value_monthly_sip(pmt, annual_return, months):
    r = annual_return / (12 * 100)
    if r == 0:
        return pmt * months
    return pmt * ((1 + r)**months - 1) / r

def npv_stream(payment, discount_rate, months):
    r = discount_rate / (12 * 100)
    if r == 0:
        return payment * months
    return payment * (1 - (1 + r)**(-months)) / r

# =========================================================
# HEADER
# =========================================================
st.title("🧪 Debt Decision Lab")

st.info(
"""
This lab is for **learning and exploration**.

You will explore:
• How loans behave  
• Prepayment impact  
• Prepay vs invest  
• Case decision using NPV
-Developed by Dr.Shalini Velappan, IIM Trichy
"""
)

# =========================================================
# GLOBAL INPUTS
# =========================================================
st.subheader("📥 Your Loan")

loan_amount = st.number_input("Loan Amount (₹)", value=500000)
interest_rate = st.number_input("Loan Interest Rate (%)", value=10.0)
remaining_years = st.number_input("Remaining Years", value=5)

emi, n, r = calculate_emi(loan_amount, interest_rate, remaining_years)
st.write(f"💸 EMI ≈ ₹ {emi:,.0f}")

st.markdown("---")

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3 = st.tabs([
    "🧾 EMI Lab",
    "🧨 Prepayment Lab",
    "⚖️ Decision Lab"
])

# =========================================================
# TAB 1 — EMI LAB
# =========================================================
with tab1:
    st.header("EMI Lab: Understand Your Loan")

    total_payment = emi * n
    total_interest = total_payment - loan_amount

    c1, c2, c3 = st.columns(3)
    c1.metric("Monthly EMI", f"₹ {emi:,.0f}")
    c2.metric("Total Interest", f"₹ {total_interest:,.0f}")
    c3.metric("Total Payment", f"₹ {total_payment:,.0f}")

    st.info("A loan is a multi-year contract with your future self.")

# =========================================================
# TAB 2 — PREPAYMENT LAB
# =========================================================
with tab2:
    st.header("Prepayment Lab")

    prepay_year = st.number_input("Prepay after years", 1, remaining_years, 2)
    prepay_amount = st.number_input("Prepayment amount", value=50000)

    k = prepay_year * 12
    balance_before = remaining_balance(loan_amount, r, emi, k)
    new_balance = balance_before - prepay_amount

    if new_balance > 0:
        new_n = math.log(emi / (emi - new_balance * r)) / math.log(1 + r)
        new_n = int(math.ceil(new_n))
        months_saved = (n - k) - new_n

        st.metric("Months Reduced", months_saved)

# =========================================================
# TAB 3 — DECISION LAB
# =========================================================
with tab3:
    st.header("Decision Lab: Prepay or Invest")

    extra_monthly = st.number_input("Extra money per month", value=5000)
    expected_return = st.number_input("Expected investment return (%)", value=12.0)

    # ---------- Prepay ----------
    balance = loan_amount
    months = 0
    total_payment_with_prepay = 0

    while balance > 0 and months < 1000:
        interest = balance * r
        payment = emi + extra_monthly
        principal_paid = payment - interest
        balance -= principal_paid
        total_payment_with_prepay += payment
        months += 1

    interest_saved = (emi*n - loan_amount) - (total_payment_with_prepay - loan_amount)
    fv = future_value_monthly_sip(extra_monthly, expected_return, n)

    c1, c2 = st.columns(2)
    c1.metric("Interest Saved", f"₹ {interest_saved:,.0f}")
    c2.metric("Investment Value", f"₹ {fv:,.0f}")

    if fv > interest_saved:
        st.success("Investing wins mathematically")
    else:
        st.warning("Prepaying wins mathematically")

    st.markdown("---")

    # =========================================================
    # CASE SCENARIOS
    # =========================================================
    st.header("🏠 Case Scenarios")

    rent = st.number_input("Monthly Rent", value=8000)
    discount_rate = st.number_input("Discount rate for NPV (%)", value=8.0)
    price_growth = st.number_input("House price growth (%)", value=3.0)

    st.write("Click scenarios to see decision change")

    col1, col2, col3, col4 = st.columns(4)

    if col1.button("Scenario 1"):
        price_growth = 0
        st.info("No price growth → renting stronger")

    if col2.button("Scenario 2"):
        price_growth = 10
        st.info("High price growth → buying stronger")

    if col3.button("Scenario 3"):
        interest_rate += 1
        st.info("Interest rises → renting stronger")

    if col4.button("Scenario 4"):
        rent *= 1.25
        st.info("Rent rises → buying stronger")

    emi_case, n_case, _ = calculate_emi(loan_amount, interest_rate, remaining_years)

    pv_buy = npv_stream(emi_case, discount_rate, n_case)
    pv_rent = npv_stream(rent, discount_rate, n_case)

    future_price = loan_amount * ((1 + price_growth/100) ** remaining_years)
    pv_resale = future_price / ((1 + discount_rate/100) ** remaining_years)

    npv_buy_total = pv_buy - pv_resale
    npv_rent_total = pv_rent
    diff = npv_buy_total - npv_rent_total

    c1, c2, c3 = st.columns(3)
    c1.metric("NPV Buy", f"₹ {npv_buy_total:,.0f}")
    c2.metric("NPV Rent", f"₹ {npv_rent_total:,.0f}")
    c3.metric("Buy − Rent", f"₹ {diff:,.0f}")

    if diff < 0:
        st.success("Buying is better")
    else:
        st.warning("Renting is better")

    st.markdown("---")

    # =========================================================
    # GRAPH
    # =========================================================
    st.subheader("NPV vs Interest Rate")

    rates = np.linspace(2, 15, 30)
    npvs = []

    for rate in rates:
        emi_temp, _, _ = calculate_emi(loan_amount, rate, remaining_years)
        pv_buy_temp = npv_stream(emi_temp, discount_rate, n_case)
        future_price_temp = loan_amount*((1+price_growth/100)**remaining_years)
        pv_resale_temp = future_price_temp/((1+discount_rate/100)**remaining_years)
        npv_temp = (pv_buy_temp - pv_resale_temp) - pv_rent
        npvs.append(npv_temp)

    fig, ax = plt.subplots()
    ax.plot(rates, npvs)
    ax.axhline(0, linestyle="--")
    ax.set_xlabel("Interest Rate")
    ax.set_ylabel("Buy − Rent NPV")
    st.pyplot(fig)
