import streamlit as st
import pandas as pd

st.set_page_config(page_title="EcoPulse AI", layout="wide")

def load_data(uploaded):
    xls = pd.ExcelFile(uploaded)
    return {sheet: pd.read_excel(uploaded, sheet_name=sheet) for sheet in xls.sheet_names}

def normalize(data):
    fixed={}
    for name, df in data.items():
        n=name.lower().strip().replace("_"," ")
        if "month" in n or "operation" in n:
            fixed["Monthly Operations"]=df
        elif "supplier" in n:
            fixed["Suppliers"]=df
        elif "action" in n or "esg" in n:
            fixed["ESG Actions"]=df
        elif "company" in n or "profile" in n:
            fixed["Company Profile"]=df
        else:
            fixed[name]=df
    return fixed

def metrics(data):
    m={}
    ops=data.get("Monthly Operations")
    sup=data.get("Suppliers")
    actions=data.get("ESG Actions")

    if ops is not None:
        if "Profit AED" in ops.columns:
            m["profit"]=pd.to_numeric(ops["Profit AED"], errors="coerce").mean()
        if "Waste kg" in ops.columns:
            m["waste"]=pd.to_numeric(ops["Waste kg"], errors="coerce").mean()
        if "Electricity Cost AED" in ops.columns:
            m["electricity"]=pd.to_numeric(ops["Electricity Cost AED"], errors="coerce").mean()
        if "Water Cost AED" in ops.columns:
            m["water"]=pd.to_numeric(ops["Water Cost AED"], errors="coerce").mean()

    if sup is not None:
        risk=[c for c in sup.columns if "risk" in c.lower()]
        score=[c for c in sup.columns if "sustainability" in c.lower() or "score" in c.lower()]
        supplier=[c for c in sup.columns if "supplier" in c.lower()]
        if risk:
            high=sup[sup[risk[0]].astype(str).str.lower().str.contains("high", na=False)]
            m["risk_count"]=len(high)
            if len(high)>0 and supplier:
                m["high_supplier"]=str(high.iloc[0][supplier[0]])
        if score:
            m["avg_supplier_score"]=pd.to_numeric(sup[score[0]], errors="coerce").mean()

    if actions is not None:
        savings=[c for c in actions.columns if "saving" in c.lower()]
        action=[c for c in actions.columns if "action" in c.lower()]
        if savings and action:
            temp=actions.copy()
            temp[savings[0]]=pd.to_numeric(temp[savings[0]], errors="coerce")
            best=temp.sort_values(savings[0], ascending=False).iloc[0]
            m["best_action"]=str(best[action[0]])
            m["best_savings"]=float(best[savings[0]])

    return m

def answer(q,m):
    q=q.lower()
    if "supplier" in q or "risk" in q:
        supplier=m.get("high_supplier","the supplier with the lowest sustainability score / high risk label")
        return f"EcoPulse identifies **{supplier}** as the main supplier risk. Management should review this supplier because it may affect ESG readiness, supply-chain credibility, and future reporting quality. Recommended action: compare it with a more sustainable alternative and negotiate recyclable materials or improved sustainability terms."
    if "led" in q or "lighting" in q:
        return "The **LED Lighting Upgrade** is a strong quick-win action. It can reduce electricity cost, lower energy-related emissions, and improve the company’s ESG score. Because it is usually easy to implement and has a short payback period, EcoPulse recommends prioritizing it as an early sustainability action."
    if "cost" in q or "save" in q or "reduce" in q:
        return f"The strongest cost-saving opportunity is **{m.get('best_action','energy and logistics optimization')}**. The company should focus first on electricity, logistics, packaging, and waste disposal because these areas affect both profit and sustainability performance. Estimated priority saving opportunity: around AED {m.get('best_savings',0):,.0f} per month if the action data is applied."
    if "esg" in q or "ready" in q:
        return "This SME is **moderately ESG-ready**. It already has useful operational data such as electricity, water, waste, profit, and supplier information. However, it still needs stronger ESG reporting, supplier governance, sustainability policies, and regular tracking before it can be considered highly ESG-ready."
    if "summary" in q or "executive" in q:
        return f"Executive summary: This SME is profitable, with an average monthly profit of approximately **AED {m.get('profit',0):,.0f}**. However, the dashboard highlights sustainability and cost-efficiency opportunities, especially around energy use, waste, and supplier risk. EcoPulse recommends prioritizing quick-win actions that reduce cost while improving ESG readiness."
    if "priority" in q or "next" in q:
        return f"Next month, management should prioritize **{m.get('best_action','energy efficiency improvements')}**, review the high-risk supplier, and start monthly tracking of electricity, water, waste, and supplier sustainability. This creates both financial and ESG value."
    return "EcoPulse recommends focusing on three areas: reducing energy costs, lowering waste, and improving supplier sustainability. These actions improve ESG readiness while also supporting profitability and operational efficiency."

st.title("EcoPulse AI Sustainability Intelligence Dashboard")
st.caption("AI-assisted ESG + business intelligence prototype for UAE SMEs")

uploaded = st.file_uploader("Upload your SME Excel dataset", type=["xlsx"])

if uploaded:
    data = normalize(load_data(uploaded))
    m = metrics(data)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Avg Monthly Profit", f"AED {m.get('profit',0):,.0f}")
    c2.metric("Avg Waste", f"{m.get('waste',0):,.0f} kg")
    c3.metric("High-Risk Suppliers", m.get("risk_count",0))
    c4.metric("Top Action", m.get("best_action","Review Operations"))

    if "Monthly Operations" in data and "Month" in data["Monthly Operations"].columns:
        cols=[c for c in ["Electricity Cost AED","Water Cost AED","Profit AED"] if c in data["Monthly Operations"].columns]
        if cols:
            st.subheader("Operational Trends")
            st.line_chart(data["Monthly Operations"].set_index("Month")[cols])

    st.subheader("Ask EcoPulse AI")
    q=st.text_area("Ask a question", "Give me an executive summary of this SME.")
    if st.button("Ask AI"):
        st.markdown("### AI Response")
        st.success(answer(q,m))

else:
    st.info("Upload your Excel file to begin.")
