# FULL FINAL VERSION
# (code intentionally very long — do not trim)

import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.graph_objects as go
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

st.set_page_config(page_title="Portfolio War-Room Simulation", layout="wide")

# =====================================================
# SESSION DEFAULTS
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
    "alloc_history": [],
    "submitted": False,
    "scenario_sequence": [],
    "leaderboard": []
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k]=v

# =====================================================
# RESET
# =====================================================
def reset_all():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# =====================================================
# REGIME AI
# =====================================================
def regime_ai_allocation(regime):
    if regime in ["Crisis","Recession","Credit"]:
        return {"Indian Equity":0.1,"US Equity":0.1,"Bonds":0.35,"Gold":0.3,"Crypto":0.05,"Cash":0.1}
    elif regime in ["Rate Hike","Inflation"]:
        return {"Indian Equity":0.15,"US Equity":0.15,"Bonds":0.25,"Gold":0.3,"Crypto":0.05,"Cash":0.1}
    elif regime in ["Growth Rally","Liquidity","Soft Landing"]:
        return {"Indian Equity":0.3,"US Equity":0.3,"Bonds":0.1,"Gold":0.05,"Crypto":0.2,"Cash":0.05}
    else:
        return {"Indian Equity":0.2,"US Equity":0.2,"Bonds":0.2,"Gold":0.2,"Crypto":0.1,"Cash":0.1}

# =====================================================
# LEARNING INSIGHTS
# =====================================================
learning_insights={
"Rate Hike":"Higher policy rates compress equity valuations.",
"Growth Rally":"Risk appetite rises; equities & crypto rally.",
"Crisis":"Risk-off regime. Bonds and gold protect capital.",
"Disinflation":"Falling inflation supports balanced allocation.",
"Recession":"Growth slowdown favours defensive assets.",
"Liquidity":"Liquidity injection boosts risk assets.",
"Inflation":"Inflation hurts bonds; gold hedges.",
"Credit":"Financial stress leads to defensive rotation.",
"Mixed":"Diversification reduces regret.",
"Tech Correction":"Growth stocks correct sharply.",
"Commodity Boom":"Real assets outperform.",
"Soft Landing":"Balanced portfolios benefit.",
"Dollar Surge":"Strong USD pressures EM assets."
}

# =====================================================
# METRIC FUNCTIONS
# =====================================================
def max_drawdown(series):
    cm = series.cummax()
    dd = (series - cm)/cm
    return dd.min()*100

def behavioural_scores(alloc_history):
    df=pd.DataFrame(alloc_history)
    diversification=(df.gt(0).sum(axis=1).mean()/len(df.columns))*100
    risk_control=max(0,100-df.std().mean()*100)
    overtrade=min(100,df.diff().abs().sum(axis=1).mean())
    return round(diversification,2),round(risk_control,2),round(overtrade,2)

def regret_timing(history,smart_history):
    student=pd.Series([x["Value"] for x in history])
    ai=pd.Series([x["Value"] for x in smart_history])
    regret=max(0,(ai-student).max()/student.iloc[0]*100)
    timing=(student.pct_change().corr(ai.pct_change())+1)*50
    return round(regret,2),round(timing,2)

def commentary(div,risk,overtrade,regret,timing):
    text="This performance reflects decision discipline across regimes. "
    if div>70: text+="Diversification strong. "
    if risk<50: text+="Risk control reactive. "
    if overtrade>70: text+="Frequent reallocations observed. "
    if regret>15: text+="AI outperformed in some regimes. "
    if timing>70: text+="Timing aligned with macro shifts. "
    return text

# =====================================================
# PDF REPORT
# =====================================================
from io import BytesIO

def generate_pdf_bytes(data, comment):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>Portfolio Simulation Report</b>", styles['Title']))
    elements.append(Spacer(1, 0.3 * inch))

    table = Table(data)
    table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.5,colors.grey)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("<b>AI Commentary</b>", styles['Heading2']))
    elements.append(Paragraph(comment, styles['Normal']))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(
        "© 2026 Prof. Shalini Velappan | Academic teaching use only",
        styles['Normal']
    ))

    doc.build(elements)
    buffer.seek(0)

    return buffer

# =====================================================
# TITLE
# =====================================================
st.title("Portfolio War-Room Simulation")

# =====================================================
# START SCREEN
# =====================================================
if not st.session_state.initialized:
    capital=st.number_input("Initial Capital (₹)",value=1000000)
    if st.button("Start Simulation"):
        st.session_state.portfolio_value=capital
        st.session_state.bench_value=capital
        st.session_state.smart_value=capital
        st.session_state.initialized=True

        fixed=[
("Rate Hike","RBI hikes rates",{"Indian Equity":-0.07,"US Equity":-0.03,"Bonds":0.02,"Gold":0.04,"Crypto":-0.12,"Cash":0.01}),
("Growth Rally","AI boom",{"Indian Equity":0.06,"US Equity":0.09,"Bonds":-0.02,"Gold":-0.03,"Crypto":0.15,"Cash":0.01}),
("Crisis","Geopolitical crisis",{"Indian Equity":-0.10,"US Equity":-0.08,"Bonds":0.05,"Gold":0.08,"Crypto":-0.05,"Cash":0.01}),
("Disinflation","Inflation cools",{"Indian Equity":0.08,"US Equity":0.06,"Bonds":0.07,"Gold":-0.04,"Crypto":0.05,"Cash":0.01}),
("Recession","Recession fear",{"Indian Equity":-0.12,"US Equity":-0.15,"Bonds":0.06,"Gold":0.07,"Crypto":-0.20,"Cash":0.01})
]
        pool=[
("Liquidity","Liquidity injection",{"Indian Equity":0.11,"US Equity":0.13,"Bonds":0.03,"Gold":-0.02,"Crypto":0.20,"Cash":0.01}),
("Inflation","Oil shock",{"Indian Equity":-0.06,"US Equity":-0.05,"Bonds":-0.03,"Gold":0.07,"Crypto":-0.04,"Cash":0.01}),
("Credit","Bank stress",{"Indian Equity":-0.09,"US Equity":-0.08,"Bonds":0.05,"Gold":0.07,"Crypto":-0.10,"Cash":0.01}),
("Tech Correction","Tech selloff",{"Indian Equity":-0.05,"US Equity":-0.12,"Bonds":0.04,"Gold":0.05,"Crypto":-0.18,"Cash":0.01}),
("Commodity Boom","Commodity surge",{"Indian Equity":0.09,"US Equity":0.04,"Bonds":-0.02,"Gold":0.08,"Crypto":0.02,"Cash":0.01})
]
        st.session_state.scenario_sequence=fixed+random.sample(pool,5)
        st.rerun()
    st.stop()

# =====================================================
# ROUND DASHBOARD
# =====================================================
rd=st.session_state.round

student_val=st.session_state.portfolio_value
bench_val=st.session_state.bench_value
ai_val=st.session_state.smart_value

initial=student_val if not st.session_state.history else st.session_state.history[0]["Value"]

leader=max(student_val,bench_val,ai_val)

st.markdown("## 📊 Portfolio Dashboard")
c1,c2,c3,c4=st.columns(4)
c1.metric("Round",rd)

def leader_mark(v): return "🟢" if v==leader else "⚪"

c2.metric(f"{leader_mark(student_val)} Student",f"₹{int(student_val):,}")
c3.metric(f"{leader_mark(bench_val)} Benchmark",f"₹{int(bench_val):,}")
c4.metric(f"{leader_mark(ai_val)} AI",f"₹{int(ai_val):,}")

# =====================================================
# FINAL DASHBOARD
# =====================================================
    if rd>10:
        hist=pd.DataFrame(st.session_state.history)
        bench=pd.DataFrame(st.session_state.bench_history)
        smart=pd.DataFrame(st.session_state.smart_history)
    
        r=hist["Value"].pct_change().dropna()
        br=bench["Value"].pct_change().dropna()
        sr=smart["Value"].pct_change().dropna()
    
        sharpe_s=r.mean()/(r.std()+1e-9)*np.sqrt(10)
        sharpe_b=br.mean()/(br.std()+1e-9)*np.sqrt(10)
        sharpe_ai=sr.mean()/(sr.std()+1e-9)*np.sqrt(10)
    
        dd_s=max_drawdown(hist["Value"])
        dd_b=max_drawdown(bench["Value"])
        dd_ai=max_drawdown(smart["Value"])
    
        st.header("Final Performance")
    
        c1,c2,c3 = st.columns(3)
        c1.metric("Student Sharpe",round(sharpe_s,3))
        c2.metric("Benchmark Sharpe",round(sharpe_b,3))
        c3.metric("AI Sharpe",round(sharpe_ai,3))
    
        d1,d2,d3 = st.columns(3)
        d1.metric("Student DD",round(dd_s,1))
        d2.metric("Benchmark DD",round(dd_b,1))
        d3.metric("AI DD",round(dd_ai,1))
    
        st.line_chart(pd.DataFrame({
            "Student":hist["Value"],
            "Benchmark":bench["Value"],
            "AI":smart["Value"]
        }))
    
        div,risk,overtrade=behavioural_scores(st.session_state.alloc_history)
        regret,timing=regret_timing(st.session_state.history,st.session_state.smart_history)
    
        com=commentary(div,risk,overtrade,regret,timing)
        st.info(com)
    
        radar=go.Figure()
        radar.add_trace(go.Scatterpolar(
            r=[div,risk,100-overtrade,timing],
            theta=["Diversification","Risk","Discipline","Timing"],
            fill='toself'))
        st.plotly_chart(radar,use_container_width=True)
    
        data=[
            ["Student Sharpe",round(sharpe_s,3)],
            ["Benchmark Sharpe",round(sharpe_b,3)],
            ["AI Sharpe",round(sharpe_ai,3)],
            ["Student DD",round(dd_s,1)],
            ["Benchmark DD",round(dd_b,1)],
            ["AI DD",round(dd_ai,1)]
        ]
    
        pdf_buffer = generate_pdf_bytes(data, com)
    
        st.download_button(
            label="📄 Download Performance Report",
            data=pdf_buffer,
            file_name="Portfolio_Report.pdf",
            mime="application/pdf"
        )
    
        st.success("Simulation complete. You can download the report above.")

# =====================================================
# NORMAL ROUND
# =====================================================
regime,news,returns=st.session_state.scenario_sequence[rd-1]

st.header(f"Round {rd}")
st.info(news)

alloc={}
cols=st.columns(3)
for i,a in enumerate(returns.keys()):
    alloc[a]=cols[i%3].slider(a,0,100,0,key=f"{a}{rd}")

total=sum(alloc.values())
st.write("Total Allocation:",total)

if total==100 and not st.session_state.submitted:
    if st.button("Submit Allocation"):
        pv=student_val
        new_val=sum(pv*(alloc[a]/100)*(1+returns[a]) for a in returns)

        bpv=bench_val
        w=1/len(returns)
        bench_new=sum(bpv*w*(1+returns[a]) for a in returns)

        spv=ai_val
        smart_alloc=regime_ai_allocation(regime)
        smart_new=sum(spv*smart_alloc[a]*(1+returns[a]) for a in returns)

        st.session_state.portfolio_value=new_val
        st.session_state.bench_value=bench_new
        st.session_state.smart_value=smart_new

        st.session_state.history.append({"Round":rd,"Value":new_val})
        st.session_state.bench_history.append({"Round":rd,"Value":bench_new})
        st.session_state.smart_history.append({"Round":rd,"Value":smart_new})
        st.session_state.alloc_history.append(alloc)

        st.session_state.submitted=True
        st.rerun()

if st.session_state.submitted:
    st.success("Returns Revealed")
    st.write(pd.DataFrame({"Asset":returns.keys(),
                           "Return %":[returns[a]*100 for a in returns]}))
    st.info(learning_insights.get(regime,""))

    if st.button("Next Round"):
        st.session_state.round+=1
        st.session_state.submitted=False
        st.rerun()

st.markdown("""
---
<div style='text-align:center; font-size:13px; color:gray'>
Portfolio War-Room Simulation  
© 2026 Prof. Shalini Velappan  
</div>
""",unsafe_allow_html=True)
