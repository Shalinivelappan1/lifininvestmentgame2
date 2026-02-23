import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Portfolio War-Room", layout="wide")

# =====================================================
# SESSION STATE
# =====================================================
defaults = {
    "initialized": False,
    "round": 1,
    "portfolio_value": 0,
    "bench_value": 0,
    "ai_value": 0,
    "history": [],
    "bench_history": [],
    "ai_history": [],
    "alloc_history": [],
    "submitted": False,
    "scenarios": [],
    "leaderboard": []
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k]=v

# =====================================================
# SCENARIOS SAFE
# =====================================================
if not st.session_state.scenarios:
    fixed = [
("Rate Hike","RBI hikes rates",{"Equity":-0.07,"Bonds":0.02,"Gold":0.04,"Crypto":-0.12,"Cash":0.01}),
("Growth","AI boom",{"Equity":0.08,"Bonds":-0.02,"Gold":-0.01,"Crypto":0.15,"Cash":0.01}),
("Crisis","War",{"Equity":-0.10,"Bonds":0.05,"Gold":0.08,"Crypto":-0.06,"Cash":0.01}),
("Disinflation","Inflation cools",{"Equity":0.07,"Bonds":0.06,"Gold":-0.03,"Crypto":0.05,"Cash":0.01}),
("Recession","Slowdown",{"Equity":-0.12,"Bonds":0.06,"Gold":0.07,"Crypto":-0.20,"Cash":0.01})
]

    pool = [
("Liquidity","Stimulus",{"Equity":0.10,"Bonds":0.02,"Gold":-0.02,"Crypto":0.18,"Cash":0.01}),
("Inflation","Oil spike",{"Equity":-0.05,"Bonds":-0.03,"Gold":0.07,"Crypto":-0.04,"Cash":0.01}),
("Credit","Bank stress",{"Equity":-0.08,"Bonds":0.05,"Gold":0.06,"Crypto":-0.08,"Cash":0.01}),
("Recovery","Soft landing",{"Equity":0.09,"Bonds":0.03,"Gold":-0.01,"Crypto":0.07,"Cash":0.01}),
("Mixed","Uncertain",{"Equity":0.02,"Bonds":0.01,"Gold":0.01,"Crypto":0.03,"Cash":0.01})
]

    st.session_state.scenarios = fixed + random.sample(pool,5)

# =====================================================
# FUNCTIONS
# =====================================================
def ai_alloc(regime):
    if regime in ["Crisis","Recession","Credit"]:
        return {"Equity":0.1,"Bonds":0.4,"Gold":0.3,"Crypto":0.05,"Cash":0.15}
    if regime in ["Growth","Liquidity","Recovery"]:
        return {"Equity":0.4,"Bonds":0.1,"Gold":0.05,"Crypto":0.35,"Cash":0.1}
    return {"Equity":0.25,"Bonds":0.25,"Gold":0.2,"Crypto":0.15,"Cash":0.15}

def max_dd(series):
    cm=series.cummax()
    return ((series-cm)/cm).min()*100

def generate_pdf(data,comment):
    buf=BytesIO()
    doc=SimpleDocTemplate(buf)
    styles=getSampleStyleSheet()
    elements=[
        Paragraph("Portfolio Report",styles['Title']),
        Spacer(1,20),
        Table(data,style=[('GRID',(0,0),(-1,-1),0.5,colors.grey)]),
        Spacer(1,20),
        Paragraph(comment,styles['Normal'])
    ]
    doc.build(elements)
    buf.seek(0)
    return buf

# =====================================================
# START
# =====================================================
st.title("Portfolio War-Room")

if not st.session_state.initialized:
    cap=st.number_input("Initial Capital",value=1000000)
    if st.button("Start"):
        st.session_state.portfolio_value=cap
        st.session_state.bench_value=cap
        st.session_state.ai_value=cap
        st.session_state.initialized=True
        st.rerun()
    st.stop()

rd=st.session_state.round

# =====================================================
# LIVE DASHBOARD
# =====================================================
leader=max(st.session_state.portfolio_value,
           st.session_state.bench_value,
           st.session_state.ai_value)

def mark(v): return "🟢" if v==leader else "⚪"

st.subheader("Live Dashboard")
c1,c2,c3,c4=st.columns(4)
c1.metric("Round",rd)
c2.metric(f"{mark(st.session_state.portfolio_value)} Student",f"₹{int(st.session_state.portfolio_value):,}")
c3.metric(f"{mark(st.session_state.bench_value)} Benchmark",f"₹{int(st.session_state.bench_value):,}")
c4.metric(f"{mark(st.session_state.ai_value)} AI",f"₹{int(st.session_state.ai_value):,}")

# =====================================================
# FINAL
# =====================================================
if rd>10:

    hist=pd.DataFrame(st.session_state.history)
    bench=pd.DataFrame(st.session_state.bench_history)
    ai=pd.DataFrame(st.session_state.ai_history)

    r=hist["Value"].pct_change().dropna()
    br=bench["Value"].pct_change().dropna()
    ar=ai["Value"].pct_change().dropna()

    sharpe_s=r.mean()/(r.std()+1e-9)
    sharpe_b=br.mean()/(br.std()+1e-9)
    sharpe_a=ar.mean()/(ar.std()+1e-9)

    dd_s=max_dd(hist["Value"])
    dd_a=max_dd(ai["Value"])

    st.header("Final Performance")
    c1,c2,c3=st.columns(3)
    c1.metric("Student Sharpe",round(sharpe_s,3))
    c2.metric("Benchmark Sharpe",round(sharpe_b,3))
    c3.metric("AI Sharpe",round(sharpe_a,3))

    d1,d2=st.columns(2)
    d1.metric("Student DD",round(dd_s,1))
    d2.metric("AI DD",round(dd_a,1))

    st.line_chart(pd.DataFrame({
        "Student":hist["Value"],
        "Benchmark":bench["Value"],
        "AI":ai["Value"]
    }))

    # behaviour
    df=pd.DataFrame(st.session_state.alloc_history)
    div=(df.gt(0).sum(axis=1).mean()/len(df.columns))*100
    risk=max(0,100-df.std().mean()*100)

    radar=go.Figure()
    radar.add_trace(go.Scatterpolar(r=[div,risk],
                                    theta=["Diversification","Risk Control"],
                                    fill='toself'))
    st.plotly_chart(radar,use_container_width=True)

    comment="Performance across regimes."
    data=[["Sharpe",round(sharpe_s,3)],["Drawdown",round(dd_s,1)]]

    pdf=generate_pdf(data,comment)
    st.download_button("Download PDF",pdf,"report.pdf","application/pdf")
    st.stop()

# =====================================================
# ROUND
# =====================================================
regime,news,returns=st.session_state.scenarios[rd-1]

st.header(f"Round {rd}")
st.info(news)

alloc={}
for a in returns:
    alloc[a]=st.slider(a,0,100,0,key=f"{a}{rd}")

if sum(alloc.values())==100 and not st.session_state.submitted:
    if st.button("Submit"):

        pv=st.session_state.portfolio_value
        new_val=sum(pv*(alloc[a]/100)*(1+returns[a]) for a in returns)

        bench_ret=np.mean(list(returns.values()))
        st.session_state.bench_value*=1+bench_ret

        ai_w=ai_alloc(regime)
        ai_val=sum(st.session_state.ai_value*ai_w[a]*(1+returns[a]) for a in returns)

        st.session_state.portfolio_value=new_val
        st.session_state.ai_value=ai_val

        st.session_state.history.append({"Round":rd,"Value":new_val})
        st.session_state.bench_history.append({"Round":rd,"Value":st.session_state.bench_value})
        st.session_state.ai_history.append({"Round":rd,"Value":ai_val})
        st.session_state.alloc_history.append(alloc)

        st.session_state.submitted=True
        st.rerun()

if st.session_state.submitted:
    if st.button("Next Round"):
        st.session_state.round+=1
        st.session_state.submitted=False
        st.rerun()
