import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.express as px

st.set_page_config(page_title="Portfolio War-Room Simulation", layout="wide")

# =====================================================
# SESSION STATE INITIALIZATION
# =====================================================
defaults = {
    "initialized": False,
    "round": 1,
    "portfolio_value": 0,
    "bench_value": 0,
    "smart_value": 0,
    "history": [],
    "bench_history": [],
    "smart_history": [],
    "submitted": False,
    "scenario_sequence": [],
    "confidence": 50,
    "emotion_log": [],
    "alloc_history": [],
    "confidence_log": []
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =====================================================
# RESET FUNCTION
# =====================================================
def reset_all():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# =====================================================
# REGIME AI MODEL
# =====================================================
def regime_ai_allocation(regime):

    if regime in ["Crisis", "Recession", "Credit"]:
        return {"Indian Equity":0.10,"US Equity":0.10,"Bonds":0.35,
                "Gold":0.30,"Crypto":0.05,"Cash":0.10}

    elif regime in ["Rate Hike", "Inflation"]:
        return {"Indian Equity":0.15,"US Equity":0.15,"Bonds":0.25,
                "Gold":0.30,"Crypto":0.05,"Cash":0.10}

    elif regime in ["Growth Rally", "Liquidity", "Soft Landing"]:
        return {"Indian Equity":0.30,"US Equity":0.30,"Bonds":0.10,
                "Gold":0.05,"Crypto":0.20,"Cash":0.05}

    else:
        return {"Indian Equity":0.20,"US Equity":0.20,"Bonds":0.20,
                "Gold":0.20,"Crypto":0.10,"Cash":0.10}

# =====================================================
# LEARNING INSIGHTS
# =====================================================
learning_insights = {
"Rate Hike":"Central banks raised rates. Growth stocks fall.",
"Growth Rally":"Tech optimism drove markets higher.",
"Crisis":"Risk-off. Bonds & gold outperform.",
"Disinflation":"Cooling inflation boosted bonds.",
"Recession":"Defensive rotation.",
"Liquidity":"Liquidity surge lifts risk assets.",
"Inflation":"Inflation shock hit bonds.",
"Credit":"Credit tightening stress.",
"Mixed":"Conflicting signals.",
"Tech Correction":"Tech selloff.",
"Commodity Boom":"Commodities surge.",
"Soft Landing":"Balanced portfolios win.",
"Dollar Surge":"Strong USD pressures EM."
}

# =====================================================
# TITLE
# =====================================================
st.title("Portfolio War-Room Simulation")
st.caption("Designed by Prof. Shalini Velappan | IIM Tiruchirappalli")

# =====================================================
# START SCREEN
# =====================================================
if not st.session_state.initialized:

    capital = st.number_input("Initial Capital (₹)", value=1000000, step=100000)

    if st.button("Start Simulation"):

        st.session_state.portfolio_value = capital
        st.session_state.bench_value = capital
        st.session_state.smart_value = capital
        st.session_state.initialized = True

        fixed_rounds = [
            ("Rate Hike","RBI hikes rates",
             {"Indian Equity":-0.07,"US Equity":-0.03,"Bonds":0.02,"Gold":0.04,"Crypto":-0.12,"Cash":0.01}),
            ("Growth Rally","AI boom",
             {"Indian Equity":0.06,"US Equity":0.09,"Bonds":-0.02,"Gold":-0.03,"Crypto":0.15,"Cash":0.01}),
            ("Crisis","Geopolitical crisis",
             {"Indian Equity":-0.10,"US Equity":-0.08,"Bonds":0.05,"Gold":0.08,"Crypto":-0.05,"Cash":0.01}),
            ("Disinflation","Inflation cools",
             {"Indian Equity":0.08,"US Equity":0.06,"Bonds":0.07,"Gold":-0.04,"Crypto":0.05,"Cash":0.01}),
            ("Recession","Recession fear",
             {"Indian Equity":-0.12,"US Equity":-0.15,"Bonds":0.06,"Gold":0.07,"Crypto":-0.20,"Cash":0.01})
        ]

        scenario_pool = [
            ("Liquidity","Global liquidity injection",
             {"Indian Equity":0.11,"US Equity":0.13,"Bonds":0.03,"Gold":-0.02,"Crypto":0.20,"Cash":0.01}),
            ("Inflation","Oil price shock",
             {"Indian Equity":-0.06,"US Equity":-0.05,"Bonds":-0.03,"Gold":0.07,"Crypto":-0.04,"Cash":0.01}),
            ("Credit","Banking stress",
             {"Indian Equity":-0.09,"US Equity":-0.08,"Bonds":0.05,"Gold":0.07,"Crypto":-0.10,"Cash":0.01}),
            ("Mixed","Mixed signals",
             {"Indian Equity":0.02,"US Equity":0.05,"Bonds":-0.02,"Gold":0.01,"Crypto":0.06,"Cash":0.01}),
            ("Tech Correction","Tech selloff",
             {"Indian Equity":-0.05,"US Equity":-0.12,"Bonds":0.04,"Gold":0.05,"Crypto":-0.18,"Cash":0.01}),
            ("Commodity Boom","Commodity boom",
             {"Indian Equity":0.09,"US Equity":0.04,"Bonds":-0.02,"Gold":0.08,"Crypto":0.02,"Cash":0.01}),
            ("Soft Landing","Soft landing",
             {"Indian Equity":0.05,"US Equity":0.04,"Bonds":0.03,"Gold":-0.01,"Crypto":0.04,"Cash":0.01}),
            ("Dollar Surge","Strong USD",
             {"Indian Equity":-0.04,"US Equity":0.02,"Bonds":0.01,"Gold":-0.03,"Crypto":-0.06,"Cash":0.01})
        ]

        random_rounds = random.sample(scenario_pool, k=5)
        st.session_state.scenario_sequence = fixed_rounds + random_rounds
        st.rerun()

    st.stop()

# =====================================================
# HEADER
# =====================================================
c1, c2, c3 = st.columns(3)
c1.metric("Portfolio", f"₹{int(st.session_state.portfolio_value):,}")
c2.metric("Benchmark", f"₹{int(st.session_state.bench_value):,}")
c3.metric("AI Fund", f"₹{int(st.session_state.smart_value):,}")

st.progress(st.session_state.round/10)

if st.button("Reset Simulation"):
    reset_all()

rd = st.session_state.round

# =====================================================
# FINAL DASHBOARD
# =====================================================
if rd > 10:

    st.header("Final Performance Dashboard")

    hist = pd.DataFrame(st.session_state.history)
    bench_hist = pd.DataFrame(st.session_state.bench_history)
    smart_hist = pd.DataFrame(st.session_state.smart_history)

    compare = pd.DataFrame({
        "Student": hist["Value"],
        "Benchmark": bench_hist["Value"],
        "Regime AI": smart_hist["Value"]
    })

    st.line_chart(compare)

    def sharpe(x):
        r = x.pct_change().dropna()
        return (r.mean()/(r.std()+1e-9))*np.sqrt(10)

    st.metric("Student Sharpe", round(sharpe(hist["Value"]),2))
    st.metric("Benchmark Sharpe", round(sharpe(bench_hist["Value"]),2))
    st.metric("AI Sharpe", round(sharpe(smart_hist["Value"]),2))

    # =====================================================
    # BEHAVIOUR RADAR
    # =====================================================
    st.subheader("Behaviour Radar")

    alloc_df = pd.DataFrame(st.session_state.alloc_history)

    if not alloc_df.empty:

        risk = alloc_df[["Indian Equity","US Equity","Crypto"]].sum(axis=1).mean()
        div = alloc_df.apply(lambda x: (x>0).sum(), axis=1).mean()*15
        timing = (hist["Value"].pct_change()>0).mean()*100
        ai_align = 50 + random.randint(-10,10)
        conf = np.mean(st.session_state.confidence_log) if st.session_state.confidence_log else 50

        behaviour = pd.DataFrame({
            "Metric":["Risk Taking","Diversification","Timing","AI Alignment","Confidence"],
            "Score":[risk,div,timing,ai_align,conf]
        })

        fig = px.line_polar(behaviour,r="Score",theta="Metric",line_close=True,range_r=[0,100])
        st.plotly_chart(fig,use_container_width=True)

    # =====================================================
    # EXCEL EXPORT
    # =====================================================
    st.subheader("Download Excel Report")

    alloc = pd.DataFrame(st.session_state.alloc_history)

    writer = pd.ExcelWriter("warroom_report.xlsx", engine="xlsxwriter")

    hist.to_excel(writer, sheet_name="Student")
    bench_hist.to_excel(writer, sheet_name="Benchmark")
    smart_hist.to_excel(writer, sheet_name="AI")
    alloc.to_excel(writer, sheet_name="Allocations")

    pd.DataFrame({
        "Confidence": st.session_state.confidence_log
    }).to_excel(writer, sheet_name="Confidence")

    writer.close()

    with open("warroom_report.xlsx","rb") as f:
        st.download_button("Download Excel", f, file_name="WarRoom_Report.xlsx")

    st.stop()

# =====================================================
# ROUND
# =====================================================
regime, news, returns = st.session_state.scenario_sequence[rd-1]

st.header(f"Round {rd}")
st.warning(news)

st.session_state.confidence = st.slider("Confidence",0,100,50)

alloc = {}
cols = st.columns(3)

for i, asset in enumerate(returns.keys()):
    alloc[asset] = cols[i%3].slider(asset,0,100,0,key=f"{asset}{rd}")

total = sum(alloc.values())
st.write("Total Allocation:", total)

if total == 100 and not st.session_state.submitted:

    if st.button("Submit Allocation"):

        st.session_state.alloc_history.append({"Round":rd,**alloc})
        st.session_state.confidence_log.append(st.session_state.confidence)

        pv = st.session_state.portfolio_value
        new_val = sum(pv*(alloc[a]/100)*(1+returns[a]) for a in returns)

        bpv = st.session_state.bench_value
        w = 1/len(returns)
        bench_new = sum(bpv*w*(1+returns[a]) for a in returns)

        spv = st.session_state.smart_value
        smart_alloc = regime_ai_allocation(regime)
        smart_new = sum(spv*smart_alloc[a]*(1+returns[a]) for a in returns)

        st.session_state.portfolio_value = new_val
        st.session_state.bench_value = bench_new
        st.session_state.smart_value = smart_new

        st.session_state.history.append({"Round":rd,"Value":new_val})
        st.session_state.bench_history.append({"Round":rd,"Value":bench_new})
        st.session_state.smart_history.append({"Round":rd,"Value":smart_new})

        st.session_state.submitted = True
        st.rerun()

# =====================================================
# REVEAL
# =====================================================
if st.session_state.submitted:

    st.success("Returns Revealed")

    st.dataframe(pd.DataFrame({
        "Asset": list(returns.keys()),
        "Return %":[returns[a]*100 for a in returns]
    }))

    st.markdown("### Market Insight")
    st.info(learning_insights.get(regime,""))

    st.markdown("### 🤖 Regime AI Allocation")
    ai_df = pd.DataFrame({
        "Asset": regime_ai_allocation(regime).keys(),
        "AI Weight %":[v*100 for v in regime_ai_allocation(regime).values()]
    })
    st.dataframe(ai_df)

    if st.button("Next Round"):
        st.session_state.round += 1
        st.session_state.submitted = False
        st.rerun()
