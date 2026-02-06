import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

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

loan_amount = st.number_input("Loan Amount (₹)", value=500000)
interest_rate = st.number_input("Loan Interest Rate (%)", value=10.0)
remaining_years = st.number_input("Remaining Tenure (Years)", value=5)

emi, n, r = calculate_emi(loan_amount, interest_rate, remaining_years)
st.write(f"💸 EMI ≈ ₹ {emi:,.0f}")

st.markdown("---")

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3 = st.tabs([
    "🧾 EMI Lab: Understand Your Loan",
    "🧨 Prepayment Lab: Escape Faster",
    "⚖️ Decision Lab: Prepay or Invest?"
])

# =========================================================
# TAB 1 — EMI
# =========================================================
with tab1:
    st.header("EMI Lab: Understand Your Loan")

    total_payment = emi * n
    total_interest = total_payment - loan_amount

    c1, c2, c3 = st.columns(3)
    c1.metric("Monthly EMI", f"₹ {emi:,.0f}")
    c2.metric("Total Interest", f"₹ {total_interest:,.0f}")
    c3.metric("Total Payment", f"₹ {total_payment:,.0f}")

    # ---------- TIME COMMITMENT ----------
    st.subheader("⏳ Time Commitment")
    st.write(f"You are committing **{n} months ({remaining_years} years of your life)** to this loan.")

    # ---------- BURDEN ----------
    st.subheader("⚠️ Burden Meter")
    ratio = total_interest / loan_amount

    if ratio < 0.3:
        st.success("🟢 Light Burden")
    elif ratio < 0.7:
        st.warning("🟠 Heavy Burden: A large part of what you repay is interest.")
    else:
        st.error("🔴 Very Heavy Burden")

    st.info("🧠 A loan is not a number. It is a multi-year contract with your future self.")

# =========================================================
# TAB 2 — PREPAYMENT
# =========================================================
with tab2:
    st.header("Prepayment Lab: Escape Faster")

    prepay_year = st.number_input("Prepay after how many years?", 1, remaining_years, 2)
    prepay_amount = st.number_input("Prepayment Amount (₹)", value=50000)

    k = prepay_year * 12
    balance_before = remaining_balance(loan_amount, r, emi, k)
    new_balance = balance_before - prepay_amount

    if new_balance > 0:
        new_n = math.log(emi / (emi - new_balance * r)) / math.log(1 + r)
        new_n = int(math.ceil(new_n))
        months_saved = (n - k) - new_n

        original_remaining = n - k
        interest_saved = emi * original_remaining - emi * new_n

        st.subheader("📉 Prepayment Impact")

        c1, c2, c3 = st.columns(3)
        c1.metric("⏳ Months Reduced", months_saved)
        c2.metric("💰 Interest Saved", f"₹ {interest_saved:,.0f}")
        c3.metric("🏁 New Remaining Tenure", f"{new_n} months")

        st.success("💡 Small actions can buy back years of your life.")

# =========================================================
# TAB 3 — DECISION
# =========================================================
with tab3:
    st.header("Decision Lab: Should I Prepay or Invest?")

    extra_monthly = st.number_input("Extra money available per month (₹)", value=5000)
    expected_return = st.number_input("Expected investment return (%)", value=12.0)

    # ---------- PREPAY SIM ----------
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
    years_saved = (n - months)/12
    fv = future_value_monthly_sip(extra_monthly, expected_return, n)

    st.subheader("📊 Comparison")

    col1, col2 = st.columns(2)

    with col1:
        st.write("🅰️ Prepay Loan")
        st.write(f"Loan closes in: {months} months")
        st.write(f"Years saved: {years_saved:.1f}")
        st.write(f"Interest saved: ₹ {interest_saved:,.0f}")

    with col2:
        st.write("🅱️ Invest Instead")
        st.write(f"Future investment value: ₹ {fv:,.0f}")

    st.markdown("---")

    st.subheader("🏁 Verdict")

    if fv > interest_saved:
        st.success("📈 Mathematically, INVESTING wins in this scenario.")
    else:
        st.warning("📉 Mathematically, PREPAYING wins in this scenario.")

    st.info("""
Prepaying gives a guaranteed return equal to the loan interest rate.  
Investing gives a risky but potentially higher return.  
Great decisions balance math, risk, and peace of mind.
""")

    # =========================================================
    # CASE SCENARIOS
    # =========================================================
    st.markdown("---")
    st.header("🏠 Case Scenario Simulator")

    rent = st.number_input("Monthly Rent", value=8000)
    discount_rate = st.number_input("Discount Rate (%)", value=8.0)
    price_growth = st.number_input("House Price Growth (%)", value=3.0)

    st.write("Click scenarios")

    col1,col2,col3,col4 = st.columns(4)

    if col1.button("Scenario 1: No growth"):
        price_growth = 0
        st.info("Prices flat → renting stronger")

    if col2.button("Scenario 2: High growth"):
        price_growth = 10
        st.info("High growth → buying stronger")

    if col3.button("Scenario 3: Rate ↑"):
        interest_rate += 1
        st.info("Higher interest → renting stronger")

    if col4.button("Scenario 4: Rent ↑"):
        rent *= 1.25
        st.info("Higher rent → buying stronger")

    emi_case, n_case, _ = calculate_emi(loan_amount, interest_rate, remaining_years)

    pv_buy = npv_stream(emi_case, discount_rate, n_case)
    pv_rent = npv_stream(rent, discount_rate, n_case)

    future_price = loan_amount*((1+price_growth/100)**remaining_years)
    pv_resale = future_price/((1+discount_rate/100)**remaining_years)

    diff = (pv_buy - pv_resale) - pv_rent

    st.metric("NPV Difference (Buy − Rent)", f"₹ {diff:,.0f}")

    if diff < 0:
        st.success("Buying wins")
    else:
        st.warning("Renting wins")

    # GRAPH
    st.subheader("📈 Decision Flip Graph")

    rates = np.linspace(2,15,30)
    vals=[]

    for rate in rates:
        emi_t,_,_=calculate_emi(loan_amount,rate,remaining_years)
        pv_buy_t=npv_stream(emi_t,discount_rate,n_case)
        future_price_t=loan_amount*((1+price_growth/100)**remaining_years)
        pv_resale_t=future_price_t/((1+discount_rate/100)**remaining_years)
        vals.append((pv_buy_t-pv_resale_t)-pv_rent)

    fig,ax=plt.subplots()
    ax.plot(rates,vals)
    ax.axhline(0,linestyle="--")
    st.pyplot(fig)
