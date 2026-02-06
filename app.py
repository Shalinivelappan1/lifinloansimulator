import streamlit as st
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Debt Decision Lab", page_icon="🧪", layout="centered")

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
st.caption("Learn how debt decisions affect your financial future")

st.info(
"""
**This simulator is for learning.**

You will explore:
• How EMIs really behave  
• Why prepayment matters  
• When investing beats prepaying  
• How NPV helps make decisions
"""
)

# =========================================================
# GLOBAL INPUTS
# =========================================================
st.subheader("📥 Your Loan Inputs")

loan_amount = st.number_input("Loan Amount (₹)", value=500000)
interest_rate = st.number_input("Interest Rate (% per year)", value=10.0)
remaining_years = st.number_input("Remaining Years", value=5)

emi, n, r = calculate_emi(loan_amount, interest_rate, remaining_years)

st.success(f"Monthly EMI ≈ ₹ {emi:,.0f}")

with st.expander("📘 What is EMI?"):
    st.write("""
EMI = Equated Monthly Installment  
It includes:
• Interest payment  
• Principal repayment  

Early years → mostly interest  
Later years → mostly principal  

Banks earn interest first.  
You reduce principal slowly.
""")

st.markdown("---")

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3 = st.tabs([
    "🧾 EMI Lab",
    "🧨 Prepayment Lab",
    "⚖️ Decision + NPV Lab"
])

# =========================================================
# TAB 1 — EMI LAB
# =========================================================
with tab1:
    st.header("🧾 Understanding Your Loan")

    total_payment = emi * n
    total_interest = total_payment - loan_amount

    c1, c2 = st.columns(2)
    c1.metric("Total Interest Paid", f"₹ {total_interest:,.0f}")
    c2.metric("Total Payment", f"₹ {total_payment:,.0f}")

    with st.expander("🎓 Teaching Insight"):
        st.write("""
Students often think interest is small.  
But over long tenures:

Interest paid can equal the loan itself.

This is why:
Long tenure = bank profits  
Short tenure = borrower freedom
""")

# =========================================================
# TAB 2 — PREPAYMENT LAB
# =========================================================
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

        st.info("""
💡 Prepayment reduces:
• Interest burden  
• Time in debt  
• Financial stress  

Early prepayment has **maximum impact**.
""")

# =========================================================
# TAB 3 — DECISION LAB
# =========================================================
with tab3:
    st.header("⚖️ Prepay vs Invest")

    extra_monthly = st.number_input("Extra per month", value=5000)
    expected_return = st.number_input("Investment return %", value=12.0)

    # Prepay sim
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
        st.success("Investing gives higher mathematical value.")
    else:
        st.warning("Prepaying is financially safer.")

    with st.expander("🎓 Teaching Insight"):
        st.write("""
Prepay return = guaranteed = loan interest rate  
Investment return = uncertain  

So decision depends on:
• Risk tolerance  
• Liquidity needs  
• Psychological comfort
""")

    st.markdown("---")

    # =========================================================
    # NPV SECTION
    # =========================================================
    st.header("🏠 Case Decision Using NPV")

    rent = st.number_input("Monthly Rent", value=8000)
    discount_rate = st.number_input("Discount Rate %", value=8.0)
    price_growth = st.number_input("House Price Growth %", value=3.0)

    emi_case, n_case, _ = calculate_emi(loan_amount, interest_rate, remaining_years)

    pv_buy = npv_stream(emi_case, discount_rate, n_case)
    pv_rent = npv_stream(rent, discount_rate, n_case)

    future_price = loan_amount*((1+price_growth/100)**remaining_years)
    pv_resale = future_price/((1+discount_rate/100)**remaining_years)

    npv_buy = pv_buy - pv_resale
    diff = npv_buy - pv_rent

    d1,d2,d3 = st.columns(3)
    d1.metric("NPV Buy", f"₹ {npv_buy:,.0f}")
    d2.metric("NPV Rent", f"₹ {pv_rent:,.0f}")
    d3.metric("Buy − Rent", f"₹ {diff:,.0f}")

    with st.expander("🎓 What does NPV mean?"):
        st.write("""
NPV converts future payments into today's value.

Lower NPV cost = better option.

So:
If Buy NPV < Rent NPV → Buy  
If Rent NPV < Buy NPV → Rent
""")

    # =========================================================
    # GRAPH
    # =========================================================
    st.subheader("📈 NPV vs Interest Rate")

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
    ax.set_xlabel("Interest Rate")
    ax.set_ylabel("Buy − Rent NPV")
    st.pyplot(fig)

    st.caption("Where line crosses zero → decision flips")
