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
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

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
learning_insights = {
"Rate Hike":"Rates rise → equities pressured, defensive assets help.",
"Growth Rally":"Risk assets surge in optimistic growth cycles.",
"Crisis":"Risk-off regime. Bonds & gold protect capital.",
"Disinflation":"Falling inflation supports bonds and balance.",
"Recession":"Defensive positioning usually performs better.",
"Liquidity":"Liquidity boosts risk assets broadly.",
"Inflation":"Real assets hedge inflation shocks.",
"Credit":"Financial stress → defensive rotation.",
"Mixed":"Diversification reduces regret.",
"Tech Correction":"High-growth stocks correct sharply.",
"Commodity Boom":"Real assets outperform.",
"Soft Landing":"Balanced portfolios perform well.",
"Dollar Surge":"Strong USD pressures EM assets."
}

# =====================================================
# BEHAVIOUR ANALYSIS
# =====================================================
def behavioural_analysis(alloc_history, values):
    df = pd.DataFrame(alloc_history)
    active_assets = (df > 0).sum(axis=1).mean()
    diversification = round((active_assets / len(df.columns)) * 100,2)

    volatility = df.std().mean()
    risk_control = round(max(0,100 - volatility*100),2)

    series = pd.Series(values)
    drawdown = ((series - series.cummax())/series.cummax()).min()*100

    if diversification > 70 and risk_control > 70:
        profile = "Disciplined Diversifier"
    elif diversification < 40:
        profile = "Aggressive Concentrator"
    else:
        profile = "Tactical Allocator"

    return diversification, risk_control, drawdown, profile

# =====================================================
# ADVANCED METRICS
# =====================================================
def advanced_metrics(alloc_history, history, smart_history):
    df = pd.DataFrame(alloc_history)
    turnover = df.diff().abs().sum(axis=1).mean()
    overtrade = round(min(100,turnover),2)

    student_vals = pd.Series([x["Value"] for x in history])
    ai_vals = pd.Series([x["Value"] for x in smart_history])
    regret = round(max(0,(ai_vals - student_vals).max()/student_vals.iloc[0]*100),2)

    timing = round((student_vals.pct_change().corr(ai_vals.pct_change())+1)*50,2)
    return overtrade, regret, timing

# =====================================================
# PROFESSOR COMMENTARY
# =====================================================
def generate_ai_commentary(div,risk,overtrade,regret,timing,profile):
    text = "This performance reflects decision discipline across regimes. "
    if div>75:
        text += "Diversification was structurally strong. "
    elif div<40:
        text += "Portfolio concentration amplified volatility. "
    if risk<50:
        text += "Risk control appeared reactive. "
    if overtrade>70:
        text += "Frequent reallocations suggest tactical over-adjustment. "
    if regret>15:
        text += "There were regimes where the systematic model outperformed materially. "
    if timing>70:
        text += "Market timing aligned well with macro shifts. "
    text += f"Overall behavioural classification: {profile}."
    return text

# =====================================================
# PDF REPORT
# =====================================================
def generate_pdf_report(filename,data,commentary):
    doc = SimpleDocTemplate(filename)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>Portfolio Simulation Report</b>", styles['Title']))
    elements.append(Spacer(1,0.3*inch))

    table = Table(data)
    table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.5,colors.grey)]))
    elements.append(table)
    elements.append(Spacer(1,0.3*inch))

    elements.append(Paragraph("<b>AI Commentary</b>", styles['Heading2']))
    elements.append(Paragraph(commentary, styles['Normal']))
    elements.append(Spacer(1,0.3*inch))

    elements.append(Paragraph(
        "© 2026 Prof. Shalini Velappan | IIM Tiruchirappalli. Academic teaching use only.",
        styles['Normal']
    ))

    doc.build(elements)

# =====================================================
# TITLE + INSTRUCTOR MODE
# =====================================================
st.title("Portfolio War-Room Simulation")
instructor_mode = st.toggle("Instructor Dashboard Mode", value=False)

if instructor_mode and st.session_state.leaderboard:
    st.header("Instructor Dashboard")
    lb = pd.DataFrame(st.session_state.leaderboard)
    st.dataframe(lb.sort_values("Final Value",ascending=False))
    st.bar_chart(lb["Sharpe"])
    st.stop()

# =====================================================
# START SCREEN
# =====================================================
if not st.session_state.initialized:
    capital = st.number_input("Initial Capital (₹)", value=1000000)
    if st.button("Start Simulation"):
        st.session_state.portfolio_value = capital
        st.session_state.bench_value = capital
        st.session_state.smart_value = capital
        st.session_state.initialized = True

        fixed = [
            ("Rate Hike","RBI hikes rates",{"Indian Equity":-0.07,"US Equity":-0.03,"Bonds":0.02,"Gold":0.04,"Crypto":-0.12,"Cash":0.01}),
            ("Growth Rally","AI boom",{"Indian Equity":0.06,"US Equity":0.09,"Bonds":-0.02,"Gold":-0.03,"Crypto":0.15,"Cash":0.01}),
            ("Crisis","Geopolitical crisis",{"Indian Equity":-0.10,"US Equity":-0.08,"Bonds":0.05,"Gold":0.08,"Crypto":-0.05,"Cash":0.01}),
            ("Disinflation","Inflation cools",{"Indian Equity":0.08,"US Equity":0.06,"Bonds":0.07,"Gold":-0.04,"Crypto":0.05,"Cash":0.01}),
            ("Recession","Recession fear",{"Indian Equity":-0.12,"US Equity":-0.15,"Bonds":0.06,"Gold":0.07,"Crypto":-0.20,"Cash":0.01})
        ]

        pool = [
            ("Liquidity","Liquidity injection",{"Indian Equity":0.11,"US Equity":0.13,"Bonds":0.03,"Gold":-0.02,"Crypto":0.20,"Cash":0.01}),
            ("Inflation","Oil shock",{"Indian Equity":-0.06,"US Equity":-0.05,"Bonds":-0.03,"Gold":0.07,"Crypto":-0.04,"Cash":0.01}),
            ("Credit","Bank stress",{"Indian Equity":-0.09,"US Equity":-0.08,"Bonds":0.05,"Gold":0.07,"Crypto":-0.10,"Cash":0.01}),
            ("Tech Correction","Tech selloff",{"Indian Equity":-0.05,"US Equity":-0.12,"Bonds":0.04,"Gold":0.05,"Crypto":-0.18,"Cash":0.01}),
            ("Commodity Boom","Commodity surge",{"Indian Equity":0.09,"US Equity":0.04,"Bonds":-0.02,"Gold":0.08,"Crypto":0.02,"Cash":0.01})
        ]

        st.session_state.scenario_sequence = fixed + random.sample(pool,5)
        st.rerun()
    st.stop()

# =====================================================
# ROUND LOGIC
# =====================================================
rd = st.session_state.round

if rd > 10:
    hist=pd.DataFrame(st.session_state.history)
    r=hist["Value"].pct_change().dropna()
    sharpe=r.mean()/(r.std()+1e-9)*np.sqrt(10)

    st.header("Final Dashboard")
    st.metric("Final Value", f"₹{int(st.session_state.portfolio_value):,}")
    st.metric("Sharpe", round(sharpe,3))

    st.line_chart(pd.DataFrame({
        "Student":hist["Value"],
        "Benchmark":pd.DataFrame(st.session_state.bench_history)["Value"],
        "AI":pd.DataFrame(st.session_state.smart_history)["Value"]
    }))

    div,risk,dd,profile=behavioural_analysis(
        st.session_state.alloc_history,
        [x["Value"] for x in st.session_state.history]
    )
    overtrade,regret,timing=advanced_metrics(
        st.session_state.alloc_history,
        st.session_state.history,
        st.session_state.smart_history
    )

    commentary=generate_ai_commentary(div,risk,overtrade,regret,timing,profile)
    st.info(commentary)

    radar=go.Figure()
    radar.add_trace(go.Scatterpolar(
        r=[div,risk,100-overtrade,timing],
        theta=["Diversification","Risk Control","Discipline","Timing"],
        fill='toself'))
    st.plotly_chart(radar,use_container_width=True)

    st.session_state.leaderboard.append({
        "Final Value":st.session_state.portfolio_value,
        "Sharpe":round(sharpe,3),
        "Regret":regret
    })
    st.dataframe(pd.DataFrame(st.session_state.leaderboard)
                 .sort_values("Final Value",ascending=False))

    data=[
        ["Final Value",f"₹{int(st.session_state.portfolio_value):,}"],
        ["Sharpe",round(sharpe,3)],
        ["Diversification",div],
        ["Risk Control",risk],
        ["Overtrading",overtrade],
        ["Regret",regret],
        ["Timing",timing],
        ["Profile",profile]
    ]

    file="report.pdf"
    generate_pdf_report(file,data,commentary)
    with open(file,"rb") as f:
        st.download_button("Download PDF Report",f,"Performance_Report.pdf")
    st.stop()

# NORMAL ROUND
regime,news,returns = st.session_state.scenario_sequence[rd-1]

st.header(f"Round {rd}")
st.info(news)

alloc={}
cols=st.columns(3)
for i,a in enumerate(returns.keys()):
    alloc[a]=cols[i%3].slider(a,0,100,0,key=f"{a}{rd}")

total=sum(alloc.values())
st.write("Total Allocation:", total)

if total==100 and not st.session_state.submitted:
    if st.button("Submit Allocation"):
        pv=st.session_state.portfolio_value
        new_val=sum(pv*(alloc[a]/100)*(1+returns[a]) for a in returns)

        bpv=st.session_state.bench_value
        w=1/len(returns)
        bench_new=sum(bpv*w*(1+returns[a]) for a in returns)

        spv=st.session_state.smart_value
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

# =====================================================
# FOOTER
# =====================================================
st.markdown("""
---
<div style='text-align:center; font-size:13px; color:gray'>
Portfolio War-Room Simulation  
© 2026 Prof. Shalini Velappan | IIM Tiruchirappalli  
For academic teaching use only
</div>
""", unsafe_allow_html=True)
