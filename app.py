import streamlit as st
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Debt Decision Lab", page_icon="🧪", layout="centered")

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

# =========================
# HEADER
# =========================
st.title("🧪 Debt Decision Lab")
st.caption("Explore loans, escape faster, decide smarter")

# =========================
# GLOBAL INPUTS
# =========================
st.subheader("📥 Your Loan")

loan_amount = st.number_input("Loan Amount (₹)", value=500000)
interest_rate = st.number_input("Interest Rate (%)", value=10.0)
remaining_years = st.number_input("Remaining Years", value=5)

emi, n, r = calculate_emi(loan_amount, interest_rate, remaining_years)

st.write(f"💸 EMI ≈ **₹ {emi:,.0f}**")

st.markdown("---")

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs([
    "🧾 EMI Lab",
    "🧨 Prepayment Lab",
    "⚖️ Decision Lab"
])

# ======================================================
# TAB 1 — EMI LAB
# ======================================================
with tab1:
    st.header("🧾 EMI Lab")

    total_payment = emi * n
    total_interest = total_payment - loan_amount

    st.metric("Total Interest", f"₹ {total_interest:,.0f}")
    st.metric("Total Payment", f"₹ {total_payment:,.0f}")

# ======================================================
# TAB 2 — PREPAYMENT
# ======================================================
with tab2:
    st.header("🧨 Prepayment Lab")

    prepay_year = st.number_input("Prepay after years", 1, remaining_years, 2)
    prepay_amount = st.number_input("Prepayment amount", value=50000)

    k = prepay_year * 12
    balance_before = remaining_balance(loan_amount, r, emi, k)
    new_balance = balance_before - prepay_amount

    if new_balance > 0:
        new_n = math.log(emi / (emi - new_balance * r)) / math.log(1 + r)
        new_n = int(math.ceil(new_n))

        months_saved = (n - k) - new_n
        st.metric("Months Saved", months_saved)

# ======================================================
# TAB 3 — DECISION + NPV
# ======================================================
with tab3:
    st.header("⚖️ Prepay vs Invest + NPV Case")

    extra_monthly = st.number_input("Extra per month", value=5000)
    expected_return = st.number_input("Investment return %", value=12.0)

    # ----- Prepay sim
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

    # ----- Invest
    fv = future_value_monthly_sip(extra_monthly, expected_return, n)

    st.subheader("Decision")
    col1, col2 = st.columns(2)

    col1.metric("Interest Saved", f"₹ {interest_saved:,.0f}")
    col2.metric("Future Value", f"₹ {fv:,.0f}")

    # ======================================================
    # NPV BLOCK (FOR CASE TEACHING)
    # ======================================================
    st.markdown("---")
    st.header("🏠 Case NPV Block")

    rent = st.number_input("Monthly Rent", value=8000)
    discount_rate = st.number_input("Discount rate %", value=8.0)
    price_growth = st.number_input("House price growth %", value=3.0)

    # Scenario buttons
    c1,c2,c3,c4 = st.columns(4)
    if c1.button("Scenario 1"):
        price_growth = 0
    if c2.button("Scenario 2"):
        price_growth = 10
    if c3.button("Scenario 3"):
        interest_rate += 1
    if c4.button("Scenario 4"):
        rent *= 1.25

    emi_case, n_case, _ = calculate_emi(loan_amount, interest_rate, remaining_years)

    pv_buy = npv_stream(emi_case, discount_rate, n_case)
    pv_rent = npv_stream(rent, discount_rate, n_case)

    future_price = loan_amount*((1+price_growth/100)**remaining_years)
    pv_resale = future_price/((1+discount_rate/100)**remaining_years)

    npv_buy = pv_buy - pv_resale
    npv_rent = pv_rent
    diff = npv_buy - npv_rent

    st.subheader("NPV Result")
    d1,d2,d3 = st.columns(3)
    d1.metric("Buy PV", f"₹ {npv_buy:,.0f}")
    d2.metric("Rent PV", f"₹ {npv_rent:,.0f}")
    d3.metric("Difference", f"₹ {diff:,.0f}")

    # Graph NPV vs interest
    st.subheader("NPV vs Interest")
    rates = np.linspace(2,15,25)
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

    # Heatmap
    st.subheader("Sensitivity Heatmap")

    rate_range=np.linspace(5,15,10)
    growth_range=np.linspace(0,10,10)

    heat=[]
    for g in growth_range:
        row=[]
        for rate in rate_range:
            emi_t,_,_=calculate_emi(loan_amount,rate,remaining_years)
            pv_buy_t=npv_stream(emi_t,discount_rate,n_case)
            future_price_t=loan_amount*((1+g/100)**remaining_years)
            pv_resale_t=future_price_t/((1+discount_rate/100)**remaining_years)
            row.append((pv_buy_t-pv_resale_t)-pv_rent)
        heat.append(row)

    df=pd.DataFrame(heat,index=np.round(growth_range,1),columns=np.round(rate_range,1))

    fig2,ax2=plt.subplots()
    sns.heatmap(df,cmap="RdYlGn",center=0)
    st.pyplot(fig2)
