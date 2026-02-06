import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

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

st.info("""
This simulator helps you explore:

• How EMIs really work  
• Why prepayment matters  
• Prepay vs invest decision  
• Buy vs rent using NPV  
• How assumptions change decisions
-Developed by Prof.Shalini Velappan, IIM Trichy
""")

# =========================================================
# INPUTS
# =========================================================
loan_amount = st.number_input("Loan Amount (₹)", value=500000)
interest_rate = st.number_input("Loan Interest Rate (%)", value=10.0)
remaining_years = st.number_input("Remaining Tenure (Years)", value=5)

emi, n, r = calculate_emi(loan_amount, interest_rate, remaining_years)
st.write(f"💸 Monthly EMI ≈ ₹ {emi:,.0f}")

st.markdown("---")

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3 = st.tabs([
    "🧾 EMI Lab",
    "🧨 Prepayment Lab",
    "⚖️ Decision + Case Lab"
])

# =========================================================
# TAB 1 — EMI
# =========================================================
with tab1:
    total_payment = emi * n
    total_interest = total_payment - loan_amount

    c1, c2, c3 = st.columns(3)
    c1.metric("Monthly EMI", f"₹ {emi:,.0f}")
    c2.metric("Total Interest", f"₹ {total_interest:,.0f}")
    c3.metric("Total Payment", f"₹ {total_payment:,.0f}")

    st.subheader("⏳ Time Commitment")
    st.write(f"You are committing **{n} months ({remaining_years} years)** to this loan.")

    st.subheader("⚠️ Burden Meter")
    ratio = total_interest / loan_amount

    if ratio < 0.3:
        st.success("🟢 Light burden")
    elif ratio < 0.7:
        st.warning("🟠 Heavy burden: large share goes to interest")
    else:
        st.error("🔴 Very heavy burden")

    st.info("""
**Conceptual Insight**

In early years, most of your EMI goes to interest.  
This means long tenures make loans expensive.

Banks earn interest first.  
You reduce principal slowly.
""")

# =========================================================
# TAB 2 — PREPAYMENT
# =========================================================
with tab2:
    st.header("📉 Prepayment Impact")

    prepay_year = st.number_input("Prepay after how many years?", 1, remaining_years, 2)
    prepay_amount = st.number_input("Prepayment Amount (₹)", value=50000)

    k = prepay_year * 12
    balance_before = remaining_balance(loan_amount, r, emi, k)
    new_balance = balance_before - prepay_amount

    if new_balance > 0:
        new_n = math.log(emi / (emi - new_balance * r)) / math.log(1 + r)
        new_n = int(math.ceil(new_n))

        original_remaining = n - k
        new_remaining_payment = emi * new_n
        original_remaining_payment = emi * original_remaining

        interest_saved = original_remaining_payment - new_remaining_payment
        months_saved = original_remaining - new_n

        col1, col2, col3 = st.columns(3)
        col1.metric("⏳ Months Reduced", months_saved)
        col2.metric("💰 Interest Saved", f"₹ {interest_saved:,.0f}")
        col3.metric("🏁 New Remaining Tenure", f"{new_n} months")

        st.success("💡 Small actions can buy back years of your life.")

    st.info("""
**Conceptual Insight**

Prepayment works best early.  
Reducing principal early reduces future interest dramatically.
""")

# =========================================================
# TAB 3 — DECISION
# =========================================================
with tab3:
    st.header("📊 Prepay vs Invest")

    extra_monthly = st.number_input("Extra per month (₹)", value=5000)
    expected_return = st.number_input("Expected investment return (%)", value=12.0)

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

    col1, col2 = st.columns(2)

    with col1:
        st.write("🅰️ Prepay Loan")
        st.write(f"Loan closes in: **{months} months**")
        st.write(f"Years saved: **{years_saved:.1f}**")
        st.write(f"Interest saved: **₹ {interest_saved:,.0f}**")

    with col2:
        st.write("🅱️ Invest Instead")
        st.write(f"Future investment value: **₹ {fv:,.0f}**")

    st.markdown("---")

    st.subheader("🏁 Verdict")

    if fv > interest_saved:
        st.success("📈 Mathematically, INVESTING wins in this scenario.")
    else:
        st.warning("📉 Mathematically, PREPAYING wins in this scenario.")

    st.info("""
Prepay return = guaranteed = loan rate  
Investment return = uncertain  
Decision depends on risk tolerance.
""")

    st.markdown("---")
    st.header("🏠 Case Scenarios")

    rent = st.number_input("Monthly Rent", value=8000)
    discount_rate = st.number_input("Discount Rate (%)", value=8.0)
    price_growth = st.number_input("House Price Growth (%)", value=3.0)

    col1,col2,col3,col4 = st.columns(4)

    if col1.button("No price growth"):
        price_growth = 0
        st.info("If prices don't grow → renting stronger")

    if col2.button("High growth"):
        price_growth = 10
        st.info("High growth → buying stronger")

    if col3.button("Interest ↑"):
        interest_rate += 1
        st.info("Higher interest → renting stronger")

    if col4.button("Rent ↑"):
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

    st.info("""
**How to interpret NPV**

NPV converts all future cash flows into today's value.  
Lower total cost option is financially better.
""")

        # =========================
    # GRAPH
    # =========================
    st.subheader("📈 NPV vs Interest Rate")

    rates = np.linspace(2, 15, 25)
    vals = []

    for rate in rates:
        emi_t, _, _ = calculate_emi(loan_amount, rate, remaining_years)
        pv_buy_t = npv_stream(emi_t, discount_rate, n_case)
        future_price_t = loan_amount * ((1 + price_growth/100) ** remaining_years)
        pv_resale_t = future_price_t / ((1 + discount_rate/100) ** remaining_years)
        vals.append((pv_buy_t - pv_resale_t) - pv_rent)

    fig, ax = plt.subplots()
    ax.plot(rates, vals)
    ax.axhline(0, linestyle="--")
    st.pyplot(fig)

    st.markdown("""
    ### 📈 How to read this chart

    The horizontal line at **0** is the break-even point.

    • Below 0 → Buying is cheaper  
    • Above 0 → Renting is cheaper  

    Where the line crosses zero = decision flip.
    """)

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
            emi_t, _, _ = calculate_emi(loan_amount, rate, remaining_years)
            pv_buy_t = npv_stream(emi_t, discount_rate, n_case)
            future_price_t = loan_amount * ((1 + g/100) ** remaining_years)
            pv_resale_t = future_price_t / ((1 + discount_rate/100) ** remaining_years)
            row.append((pv_buy_t - pv_resale_t) - pv_rent)
        heat.append(row)

    df = pd.DataFrame(
        heat,
        index=np.round(growth_range, 1),
        columns=np.round(rate_range, 1)
    )

    fig2, ax2 = plt.subplots()
    sns.heatmap(df, cmap="RdYlGn", center=0)
    st.pyplot(fig2)

    st.markdown("""
    ### 🔥 How to read this heatmap

    Each cell shows whether **buying** or **renting** is better.

    X-axis → Interest rate  
    Y-axis → Price growth  

    🟢 Green → Buy better  
    🔴 Red → Rent better  

    Small changes in assumptions can flip the decision.
    """)
