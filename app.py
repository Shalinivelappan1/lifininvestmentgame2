import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.express as px
import io

st.set_page_config(page_title="Portfolio War-Room Simulation", layout="wide")

# =====================================================
# SAFE SESSION INITIALIZATION
# =====================================================
def init_state():
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
        "alloc_history": [],
        "confidence_log": []
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# =====================================================
# RESET (SAFE)
# =====================================================
def reset_all():
    st.session_state.clear()
    init_state()
    st.rerun()

# =====================================================
# REGIME AI
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

learning_insights = {
"Rate Hike":"Rates up → growth stocks fall.",
"Growth Rally":"Risk assets surge.",
"Crisis":"Defensive assets win.",
"Disinflation":"Bonds rally.",
"Recession":"Risk assets fall.",
"Liquidity":"Crypto + equities rally.",
"Inflation":"Bonds hurt.",
"Credit":"Stress in system.",
"Mixed":"Balanced wins.",
"Tech Correction":"Growth pain.",
"Commodity Boom":"Gold shines.",
"Soft Landing":"Stable growth.",
"Dollar Surge":"EM pressured."
}

# =====================================================
# TITLE
# =====================================================
st.title("Portfolio War-Room Simulation")
st.caption("Live Classroom Edition | IIM")

# =====================================================
# START SCREEN
# =====================================================
if not st.session_state.initialized:

    capital = st.number_input("Initial Capital (₹)", value=1000000, step=100000)

    if st.button("Start Simulation"):

        fixed_rounds = [
            ("Rate Hike","RBI hikes rates",
             {"Indian Equity":-0.07,"US Equity":-0.03,"Bonds":0.02,"Gold":0.04,"Crypto":-0.12,"Cash":0.01}),
            ("Growth Rally","AI boom",
             {"Indian Equity":0.06,"US Equity":0.09,"Bonds":-0.02,"Gold":-0.03,"Crypto":0.15,"Cash":0.01}),
            ("Crisis","Geopolitical shock",
             {"Indian Equity":-0.10,"US Equity":-0.08,"Bonds":0.05,"Gold":0.08,"Crypto":-0.05,"Cash":0.01}),
            ("Disinflation","Inflation cools",
             {"Indian Equity":0.08,"US Equity":0.06,"Bonds":0.07,"Gold":-0.04,"Crypto":0.05,"Cash":0.01}),
            ("Recession","Recession fear",
             {"Indian Equity":-0.12,"US Equity":-0.15,"Bonds":0.06,"Gold":0.07,"Crypto":-0.20,"Cash":0.01})
        ]

        scenario_pool = [
            ("Liquidity","Liquidity injection",
             {"Indian Equity":0.11,"US Equity":0.13,"Bonds":0.03,"Gold":-0.02,"Crypto":0.20,"Cash":0.01}),
            ("Inflation","Oil shock",
             {"Indian Equity":-0.06,"US Equity":-0.05,"Bonds":-0.03,"Gold":0.07,"Crypto":-0.04,"Cash":0.01}),
            ("Credit","Bank stress",
             {"Indian Equity":-0.09,"US Equity":-0.08,"Bonds":0.05,"Gold":0.07,"Crypto":-0.10,"Cash":0.01}),
            ("Tech Correction","Tech selloff",
             {"Indian Equity":-0.05,"US Equity":-0.12,"Bonds":0.04,"Gold":0.05,"Crypto":-0.18,"Cash":0.01}),
            ("Commodity Boom","Commodity surge",
             {"Indian Equity":0.09,"US Equity":0.04,"Bonds":-0.02,"Gold":0.08,"Crypto":0.02,"Cash":0.01})
        ]

        random_rounds = random.sample(scenario_pool, k=5)

        st.session_state.scenario_sequence = fixed_rounds + random_rounds
        st.session_state.portfolio_value = capital
        st.session_state.bench_value = capital
        st.session_state.smart_value = capital
        st.session_state.initialized = True
        st.session_state.round = 1
        st.session_state.submitted = False

        st.rerun()

    st.stop()

# =====================================================
# SAFE PROGRESS BAR
# =====================================================
progress_val = min(st.session_state.round-1, 10) / 10
st.progress(progress_val)

# =====================================================
# HEADER
# =====================================================
c1, c2, c3 = st.columns(3)
c1.metric("Portfolio", f"₹{int(st.session_state.portfolio_value):,}")
c2.metric("Benchmark", f"₹{int(st.session_state.bench_value):,}")
c3.metric("AI Fund", f"₹{int(st.session_state.smart_value):,}")

if st.button("Reset Simulation"):
    reset_all()

rd = st.session_state.round

# =====================================================
# FINAL DASHBOARD
# =====================================================
if rd > 10:

    st.header("Final Results")

    hist = pd.DataFrame(st.session_state.history)
    bench = pd.DataFrame(st.session_state.bench_history)
    smart = pd.DataFrame(st.session_state.smart_history)

    if not hist.empty:
        st.line_chart(pd.DataFrame({
            "Student": hist["Value"],
            "Benchmark": bench["Value"],
            "AI": smart["Value"]
        }))

    # Behaviour Radar
    if st.session_state.alloc_history:
        alloc_df = pd.DataFrame(st.session_state.alloc_history)
        risk = alloc_df[["Indian Equity","US Equity","Crypto"]].sum(axis=1).mean()
        div = alloc_df.apply(lambda x: (x>0).sum(), axis=1).mean()*15
        timing = (hist["Value"].pct_change()>0).mean()*100
        conf = np.mean(st.session_state.confidence_log)

        radar = pd.DataFrame({
            "Metric":["Risk","Diversification","Timing","Confidence"],
            "Score":[risk,div,timing,conf]
        })

        fig = px.line_polar(radar,r="Score",theta="Metric",
                            line_close=True,range_r=[0,100])
        st.plotly_chart(fig,use_container_width=True)

    # Excel (cloud-safe)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        hist.to_excel(writer, sheet_name="Student", index=False)
        bench.to_excel(writer, sheet_name="Benchmark", index=False)
        smart.to_excel(writer, sheet_name="AI", index=False)
        pd.DataFrame(st.session_state.alloc_history).to_excel(writer, sheet_name="Allocations", index=False)

    output.seek(0)

    st.download_button("Download Excel Report",
                       data=output,
                       file_name="WarRoom_Report.xlsx")

    st.stop()

# =====================================================
# SAFE ROUND EXECUTION
# =====================================================
if len(st.session_state.scenario_sequence) < rd:
    st.warning("Sequence issue. Restarting.")
    reset_all()

regime, news, returns = st.session_state.scenario_sequence[rd-1]

st.header(f"Round {rd}")
st.warning(news)

st.session_state.confidence = st.slider("Confidence",0,100,50)

alloc = {}
cols = st.columns(3)

for i, asset in enumerate(returns.keys()):
    alloc[asset] = cols[i%3].slider(asset,0,100,0,key=f"{asset}{rd}")

if sum(alloc.values()) == 100 and not st.session_state.submitted:

    if st.button("Submit Allocation"):

        st.session_state.alloc_history.append({"Round":rd,**alloc})
        st.session_state.confidence_log.append(st.session_state.confidence)

        pv = st.session_state.portfolio_value
        new_val = sum(pv*(alloc[a]/100)*(1+returns[a]) for a in returns)

        bpv = st.session_state.bench_value
        w = 1/len(returns)
        bench_new = sum(bpv*w*(1+returns[a]) for a in returns)

        spv = st.session_state.smart_value
        smart_new = sum(spv*regime_ai_allocation(regime)[a]*(1+returns[a]) for a in returns)

        st.session_state.portfolio_value = new_val
        st.session_state.bench_value = bench_new
        st.session_state.smart_value = smart_new

        st.session_state.history.append({"Round":rd,"Value":new_val})
        st.session_state.bench_history.append({"Round":rd,"Value":bench_new})
        st.session_state.smart_history.append({"Round":rd,"Value":smart_new})

        st.session_state.submitted = True
        st.rerun()

if st.session_state.submitted:

    st.success("Returns Revealed")

    st.dataframe(pd.DataFrame({
        "Asset": list(returns.keys()),
        "Return %":[returns[a]*100 for a in returns]
    }))

    st.info(learning_insights.get(regime,""))

    if st.button("Next Round"):
        st.session_state.round += 1
        st.session_state.submitted = False
        st.rerun()
