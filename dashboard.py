import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re

st.set_page_config(
    page_title="Antibiotic Resistance Dashboard",
    page_icon="\U0001f9a0",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0e1621; }
.block-container { padding: 1.5rem 2rem 2rem; }
h1 { color: #e2e8f0 !important; font-weight: 700 !important; }
h2, h3 { color: #cbd5e1 !important; font-weight: 600 !important; }
div[data-testid="metric-container"] {
    background: #162032; border: 1px solid #1e3a52;
    border-radius: 12px; padding: 1rem 1.25rem;
    border-top: 3px solid #38bdf8;
}
div[data-testid="metric-container"] label { color: #94a3b8 !important; font-size: 0.78rem !important; text-transform: uppercase; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #e2e8f0 !important; font-size: 1.6rem !important; font-weight: 700 !important; }
section[data-testid="stSidebar"] { background: #0a1220 !important; border-right: 1px solid #1e3a52; }
.section-header {
    background: linear-gradient(90deg, #162032, transparent);
    border-left: 4px solid #38bdf8; padding: 0.5rem 1rem;
    margin: 1.5rem 0 0.8rem; border-radius: 0 6px 6px 0;
    color: #e2e8f0; font-weight: 600; font-size: 1.05rem;
}
.stTabs [data-baseweb="tab-list"] { background: transparent; gap: 4px; }
.stTabs [data-baseweb="tab"] { background: #162032 !important; border-radius: 8px 8px 0 0 !important; color: #94a3b8 !important; border: 1px solid #1e3a52 !important; padding: 0.5rem 1.2rem !important; }
.stTabs [aria-selected="true"] { background: #1e3a52 !important; color: #38bdf8 !important; border-bottom: 2px solid #38bdf8 !important; }
</style>
""", unsafe_allow_html=True)

ANTIBIOTIC_COLS = [
    "Amoxicillin_Ampicillin","Amoxicillin_Clavulanate","Cefazolin",
    "Cefoxitin","Cefotaxime_Ceftriaxone","Imipenem","Gentamicin",
    "Amikacin","Nalidixic_Acid","Ofloxacin","Ciprofloxacin",
    "Chloramphenicol","Cotrimoxazole","Nitrofurantoin","Colistin",
]
ANTIBIOTIC_FAMILIES = {
    "Beta-lactams":              ["Amoxicillin_Ampicillin","Amoxicillin_Clavulanate","Cefazolin","Cefoxitin","Cefotaxime_Ceftriaxone"],
    "Carbapenems":               ["Imipenem"],
    "Aminoglycosides":           ["Gentamicin","Amikacin"],
    "Fluoroquinolones":          ["Nalidixic_Acid","Ofloxacin","Ciprofloxacin"],
    "Phenicols":                 ["Chloramphenicol"],
    "Folate Pathway Inhibitors": ["Cotrimoxazole"],
    "Nitrofurans":               ["Nitrofurantoin"],
    "Polymyxins":                ["Colistin"],
}
FAMILY_COLORS = {
    "Beta-lactams":"#f97316","Carbapenems":"#ef4444","Aminoglycosides":"#a855f7",
    "Fluoroquinolones":"#3b82f6","Phenicols":"#10b981",
    "Folate Pathway Inhibitors":"#f59e0b","Nitrofurans":"#ec4899","Polymyxins":"#06b6d4",
}
RSI_COLORS = {"R":"#ef4444","I":"#f59e0b","S":"#22c55e"}
AGE_ORDER = ["Newborn","Child","Teenager","Young Adult","Senior Adult","Senior"]

# ALL 15 ANTIBIOTICS MODEL DATA
MODEL_DATA = [
    ["Amoxicillin / Ampicillin",  "CatBoost 1", 0.917, 0.763, "XGBoost",      0.766, 0.912],
    ["Amoxicillin / Clavulanate", "CatBoost 1", 0.929, 0.781, "CatBoost 1",   0.781, 0.929],
    ["Cefazolin",                 "CatBoost 1", 0.905, 0.754, "LightGBM",     0.761, 0.885],
    ["Cefoxitin",                 "CatBoost 1", 0.931, 0.766, "CatBoost 1",   0.766, 0.931],
    ["Cefotaxime / Ceftriaxone",  "XGBoost",    0.924, 0.774, "CatBoost 1",   0.780, 0.910],
    ["Imipenem",                  "CatBoost 1", 0.988, 0.987, "CatBoost 1",   0.987, 0.988],
    ["Gentamicin",                "CatBoost 3", 0.889, 0.741, "CatBoost 2",   0.785, 0.824],
    ["Amikacin",                  "CatBoost 3", 0.937, 0.727, "CatBoost 2",   0.829, 0.806],
    ["Nalidixic Acid",            "CatBoost 3", 0.928, 0.535, "CatBoost 2",   0.624, 0.852],
    ["Ofloxacin",                 "CatBoost 3", 0.938, 0.530, "CatBoost 1",   0.601, 0.855],
    ["Ciprofloxacin",             "CatBoost 3", 0.920, 0.531, "XGBoost",      0.612, 0.820],
    ["Chloramphenicol",           "CatBoost 1", 0.942, 0.952, "CatBoost 2/3", 0.961, 0.931],
    ["Cotrimoxazole",             "CatBoost 1", 0.940, 0.957, "CatBoost 2/3", 0.958, 0.936],
    ["Nitrofurantoin",            "XGBoost",    0.905, 0.896, "CatBoost 2/3", 0.926, 0.875],
    ["Colistin",                  "XGBoost",    0.948, 0.857, "CatBoost 3",   0.951, 0.910],
]
MODEL_COLS = ["Antibiotic","Best Recall Model","Recall Score","F1 @ Best Recall","Best F1 Model","F1 Score","Recall @ Best F1"]

@st.cache_data
def load_data():
    data = pd.read_csv("cleaned_antibiotic_resistance_dataset.csv")
    str_cols = data.select_dtypes(include=["object"]).columns
    for col in str_cols:
        data[col] = data[col].str.strip().str.upper()
    data["Resistance_Count"] = (data[ANTIBIOTIC_COLS] == "R").sum(axis=1)
    col_to_family = {}
    for fam, cols in ANTIBIOTIC_FAMILIES.items():
        for c in cols:
            col_to_family[c] = fam
    return data, col_to_family

df, col_to_family = load_data()

PLOT_LAYOUT = dict(plot_bgcolor="#0e1621", paper_bgcolor="#0e1621")

with st.sidebar:
    st.markdown("### \U0001f9a0 Filters")
    st.markdown("---")
    all_bacteria = sorted(df["Souches"].dropna().unique())
    sel_bacteria = st.multiselect("Bacteria species", all_bacteria, default=all_bacteria)
    all_age = sorted(df["AgeCategory"].dropna().unique(), key=lambda x: AGE_ORDER.index(x.title()) if x.title() in AGE_ORDER else 99)
    sel_age = st.multiselect("Age category", all_age, default=all_age)
    all_gender = sorted(df["Gender"].dropna().unique())
    sel_gender = st.multiselect("Gender", all_gender, default=all_gender)
    st.markdown("---")
    st.caption(f"{len(df):,} total samples · 9 species · 15 antibiotics")

filtered = df[df["Souches"].isin(sel_bacteria) & df["AgeCategory"].isin(sel_age) & df["Gender"].isin(sel_gender)].copy()

st.markdown("<h1>\U0001f9a0 Antibiotic Resistance Dashboard</h1>", unsafe_allow_html=True)
st.caption(f"Showing **{len(filtered):,}** of {len(df):,} samples")
st.markdown("---")

k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.metric("Total Samples",    f"{len(filtered):,}")
k2.metric("Avg Resistance",   f"{filtered['Resistance_Count'].mean():.2f}")
k3.metric("Multi-Resistant",  f"{(filtered['Resistance_Count']>=3).sum():,}")
k4.metric("Fully Sensitive",  f"{(filtered['Resistance_Count']==0).sum():,}")
k5.metric("Extremely MDR",    f"{(filtered['Resistance_Count']>=6).sum():,}")
k6.metric("Antibiotics",      str(len(ANTIBIOTIC_COLS)))
st.markdown("---")

tab1,tab2,tab3,tab4,tab5 = st.tabs(["\U0001f4ca Overview","\U0001f52c Species Analysis","\U0001f48a Antibiotic Families","\U0001f464 Demographics","\U0001f916 Model Performance"])

# TAB 1
with tab1:
    st.markdown('<div class="section-header">Resistance Rate per Antibiotic</div>', unsafe_allow_html=True)
    resist_data = [{"Antibiotic":c.replace("_"," "),"Resistant %":round((filtered[c]=="R").mean()*100,1),"Intermediate %":round((filtered[c]=="I").mean()*100,1),"Sensitive %":round((filtered[c]=="S").mean()*100,1),"Family":col_to_family.get(c,"Other")} for c in ANTIBIOTIC_COLS]
    res_df = pd.DataFrame(resist_data).sort_values("Resistant %", ascending=False)
    fig = px.bar(res_df,x="Antibiotic",y="Resistant %",color="Family",color_discrete_map=FAMILY_COLORS,template="plotly_dark",text="Resistant %",hover_data=["Intermediate %","Sensitive %"])
    fig.update_traces(texttemplate="%{text}%",textposition="outside")
    fig.update_layout(xaxis_tickangle=-38,height=400,margin=dict(t=30,b=10),legend=dict(orientation="h",y=1.1,x=0),**PLOT_LAYOUT)
    st.plotly_chart(fig,use_container_width=True)

    st.markdown('<div class="section-header">RSI Profile — All 15 Antibiotics (Stacked 100%)</div>', unsafe_allow_html=True)
    rsi_rows = []
    for c in ANTIBIOTIC_COLS:
        total = len(filtered[c].dropna())
        for s in ["R","I","S"]:
            rsi_rows.append({"Antibiotic":c.replace("_"," "),"Family":col_to_family.get(c,"Other"),"Status":s,"Pct":round((filtered[c]==s).sum()/total*100,1) if total>0 else 0})
    rsi_df = pd.DataFrame(rsi_rows)
    r_order = rsi_df[rsi_df["Status"]=="R"].sort_values("Pct",ascending=False)["Antibiotic"].tolist()
    fig2 = px.bar(rsi_df,x="Antibiotic",y="Pct",color="Status",color_discrete_map=RSI_COLORS,template="plotly_dark",text="Pct",barmode="stack",category_orders={"Antibiotic":r_order,"Status":["R","I","S"]})
    fig2.update_traces(texttemplate="%{text}%",textposition="inside",textfont_size=10)
    fig2.update_layout(xaxis_tickangle=-38,height=420,yaxis=dict(title="%",range=[0,101]),margin=dict(t=10,b=10),legend=dict(orientation="h",y=1.05,x=0),**PLOT_LAYOUT)
    st.plotly_chart(fig2,use_container_width=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">Resistance Count Distribution</div>', unsafe_allow_html=True)
        fig3 = px.histogram(filtered,x="Resistance_Count",nbins=16,template="plotly_dark",color_discrete_sequence=["#38bdf8"])
        fig3.update_layout(xaxis_title="Number of Resistant Antibiotics",yaxis_title="Samples",height=320,margin=dict(t=10,b=10),bargap=0.08,**PLOT_LAYOUT)
        st.plotly_chart(fig3,use_container_width=True)
    with c2:
        st.markdown('<div class="section-header">MultiResistance Category</div>', unsafe_allow_html=True)
        mr_labels={0:"None",1:"Low(1)",2:"Low(2)",3:"Moderate(3)",4:"Moderate(4)",5:"High(5)",6:"Very High(6)",7:"Extreme(7)",8:"Extreme(8)"}
        mr_df = filtered["MultiResistance"].value_counts().sort_index().reset_index()
        mr_df.columns=["MultiResistance","Count"]
        mr_df["Label"]=mr_df["MultiResistance"].map(mr_labels)
        fig4=px.bar(mr_df,x="Label",y="Count",color="Count",color_continuous_scale="Oranges",template="plotly_dark",text="Count")
        fig4.update_traces(textposition="outside")
        fig4.update_layout(xaxis_title="",yaxis_title="Samples",height=320,margin=dict(t=10,b=10),coloraxis_showscale=False,**PLOT_LAYOUT)
        st.plotly_chart(fig4,use_container_width=True)

# TAB 2
with tab2:
    st.markdown('<div class="section-header">Sample Count by Bacteria Species</div>', unsafe_allow_html=True)
    bac_df = filtered["Souches"].value_counts().reset_index()
    bac_df.columns=["Species","Count"]
    bac_df["Species"]=bac_df["Species"].str.title()
    fig5=px.bar(bac_df.sort_values("Count",ascending=True),x="Count",y="Species",orientation="h",color="Count",color_continuous_scale="Blues",template="plotly_dark",text="Count")
    fig5.update_traces(textposition="outside")
    fig5.update_layout(height=340,margin=dict(t=10,b=10,l=10),yaxis_title="",xaxis_title="Samples",coloraxis_showscale=False,**PLOT_LAYOUT)
    st.plotly_chart(fig5,use_container_width=True)

    for label, status, scale, col_title in [("Resistance","R","YlOrRd","% R"),("Susceptibility","S","Greens","% S"),("Intermediate","I","Blues","% I")]:
        st.markdown(f'<div class="section-header">{label} Heatmap — Species × Antibiotic</div>', unsafe_allow_html=True)
        rows=[]
        for bac in sorted(filtered["Souches"].unique()):
            sub=filtered[filtered["Souches"]==bac]
            rd={"Species":bac.title()}
            for c in ANTIBIOTIC_COLS:
                rd[c.replace("_"," ")]=round((sub[c]==status).mean()*100,1)
            rows.append(rd)
        hdf=pd.DataFrame(rows).set_index("Species")
        figh=px.imshow(hdf,color_continuous_scale=scale,template="plotly_dark",aspect="auto",text_auto=True,zmin=0,zmax=100)
        figh.update_layout(xaxis_title="Antibiotic",yaxis_title="",coloraxis_colorbar_title=col_title,margin=dict(t=10,b=10),height=480,font=dict(size=11),**PLOT_LAYOUT)
        figh.update_xaxes(tickangle=-35)
        st.plotly_chart(figh,use_container_width=True)

# TAB 3
with tab3:
    st.markdown('<div class="section-header">Resistance Rate by Antibiotic Family</div>', unsafe_allow_html=True)
    fam_rows=[]
    for fam,cols in ANTIBIOTIC_FAMILIES.items():
        ec=[c for c in cols if c in filtered.columns]
        if not ec: continue
        fam_rows.append({"Family":fam,"Resistant %":round((filtered[ec]=="R").mean().mean()*100,1),"Intermediate %":round((filtered[ec]=="I").mean().mean()*100,1),"Sensitive %":round((filtered[ec]=="S").mean().mean()*100,1),"Antibiotics":len(ec)})
    fam_df=pd.DataFrame(fam_rows).sort_values("Resistant %",ascending=False)
    c1,c2=st.columns(2)
    with c1:
        figf=px.bar(fam_df,x="Family",y="Resistant %",color="Family",color_discrete_map=FAMILY_COLORS,template="plotly_dark",text="Resistant %")
        figf.update_traces(texttemplate="%{text}%",textposition="outside")
        figf.update_layout(height=380,showlegend=False,xaxis_tickangle=-30,margin=dict(t=10,b=10),**PLOT_LAYOUT)
        st.plotly_chart(figf,use_container_width=True)
    with c2:
        fam_melt=fam_df.melt(id_vars="Family",value_vars=["Resistant %","Intermediate %","Sensitive %"],var_name="Status",value_name="Pct")
        fam_melt["Status"]=fam_melt["Status"].str.replace(" %","").str[0]
        figfs=px.bar(fam_melt,x="Family",y="Pct",color="Status",color_discrete_map=RSI_COLORS,template="plotly_dark",barmode="stack",text="Pct",category_orders={"Status":["R","I","S"]})
        figfs.update_traces(texttemplate="%{text}%",textposition="inside",textfont_size=10)
        figfs.update_layout(height=380,xaxis_tickangle=-30,margin=dict(t=10,b=10),yaxis=dict(range=[0,101],title="%"),legend=dict(orientation="h",y=1.08),**PLOT_LAYOUT)
        st.plotly_chart(figfs,use_container_width=True)

    st.markdown('<div class="section-header">Per-Family Detail</div>', unsafe_allow_html=True)
    fam_sel=st.selectbox("Select family",list(ANTIBIOTIC_FAMILIES.keys()),label_visibility="collapsed")
    fam_cols=ANTIBIOTIC_FAMILIES[fam_sel]
    fdet=[]
    for c in fam_cols:
        if c not in filtered.columns: continue
        for s in ["R","I","S"]:
            fdet.append({"Antibiotic":c.replace("_"," "),"Status":s,"Pct":round((filtered[c]==s).mean()*100,1)})
    fdet_df=pd.DataFrame(fdet)
    figfd=px.bar(fdet_df,x="Antibiotic",y="Pct",color="Status",color_discrete_map=RSI_COLORS,barmode="stack",template="plotly_dark",text="Pct",category_orders={"Status":["R","I","S"]})
    figfd.update_traces(texttemplate="%{text}%",textposition="inside")
    figfd.update_layout(height=360,margin=dict(t=10,b=10),yaxis=dict(range=[0,101],title="%"),legend=dict(orientation="h",y=1.08),**PLOT_LAYOUT)
    st.plotly_chart(figfd,use_container_width=True)

# TAB 4
with tab4:
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="section-header">Age Category vs Avg Resistance</div>', unsafe_allow_html=True)
        age_res=filtered.groupby("AgeCategory")["Resistance_Count"].agg(["mean","median","count"]).round(2).reset_index()
        age_res.columns=["Age Category","Avg Resistance","Median","N"]
        age_res["_s"]=age_res["Age Category"].str.title().map(lambda x: AGE_ORDER.index(x) if x in AGE_ORDER else 99)
        age_res=age_res.sort_values("_s").drop("_s",axis=1)
        figa=px.bar(age_res,x="Age Category",y="Avg Resistance",color="Avg Resistance",color_continuous_scale="RdYlGn_r",template="plotly_dark",text="Avg Resistance",hover_data=["Median","N"])
        figa.update_traces(texttemplate="%{text}",textposition="outside")
        figa.update_layout(coloraxis_showscale=False,height=360,margin=dict(t=10,b=10),xaxis_tickangle=-20,**PLOT_LAYOUT)
        st.plotly_chart(figa,use_container_width=True)
    with c2:
        st.markdown('<div class="section-header">Gender vs Avg Resistance</div>', unsafe_allow_html=True)
        gdf=filtered.copy()
        gdf["Gender_Label"]=gdf["Gender"].map({"F":"Female","M":"Male"}).fillna(gdf["Gender"])
        gagg=gdf.groupby("Gender_Label")["Resistance_Count"].agg(["mean","count"]).round(2).reset_index()
        gagg.columns=["Gender","Avg Resistance","N"]
        figg=px.bar(gagg,x="Gender",y="Avg Resistance",color="Gender",color_discrete_sequence=["#f472b6","#38bdf8"],template="plotly_dark",text="Avg Resistance",hover_data=["N"])
        figg.update_traces(texttemplate="%{text}",textposition="outside")
        figg.update_layout(showlegend=False,height=360,margin=dict(t=10,b=10),**PLOT_LAYOUT)
        st.plotly_chart(figg,use_container_width=True)

    st.markdown('<div class="section-header">Resistance Distribution by Age Category (Box Plot)</div>', unsafe_allow_html=True)
    box_df=filtered.copy()
    box_df["AgeCategory"]=pd.Categorical(box_df["AgeCategory"].str.title(),categories=AGE_ORDER,ordered=True)
    box_df=box_df.sort_values("AgeCategory")
    figbox=px.box(box_df,x="AgeCategory",y="Resistance_Count",color="AgeCategory",template="plotly_dark",points="outliers",color_discrete_sequence=px.colors.qualitative.Pastel)
    figbox.update_layout(showlegend=False,height=380,xaxis_title="Age Category",yaxis_title="Resistance Count",margin=dict(t=10,b=10),**PLOT_LAYOUT)
    st.plotly_chart(figbox,use_container_width=True)

    st.markdown('<div class="section-header">Key Features Overview</div>', unsafe_allow_html=True)
    f1,f2,f3=st.columns(3)
    with f1:
        st.markdown("**Species**")
        sp=filtered["Souches"].value_counts().reset_index()
        sp.columns=["Species","Count"]
        sp["Species"]=sp["Species"].str.title()
        figsp=px.bar(sp.sort_values("Count",ascending=True),x="Count",y="Species",orientation="h",color_discrete_sequence=["#38bdf8"],template="plotly_dark",text="Count")
        figsp.update_traces(textposition="outside")
        figsp.update_layout(height=300,margin=dict(t=5,b=5,l=5),**PLOT_LAYOUT)
        st.plotly_chart(figsp,use_container_width=True)
    with f2:
        st.markdown("**Age Distribution**")
        figah=px.histogram(filtered,x="Age",nbins=20,color_discrete_sequence=["#a78bfa"],template="plotly_dark")
        figah.update_layout(height=300,margin=dict(t=5,b=5),xaxis_title="Age (years)",yaxis_title="Count",**PLOT_LAYOUT)
        st.plotly_chart(figah,use_container_width=True)
    with f3:
        st.markdown("**Infection Frequency**")
        inf_df=filtered["Infection_Freq"].value_counts().sort_index().reset_index()
        inf_df.columns=["Infection_Freq","Count"]
        inf_df["Label"]=inf_df["Infection_Freq"].map({0:"0 (None)",1:"1 (Low)",2:"2 (Moderate)",3:"3 (High)"})
        figif=px.bar(inf_df,x="Label",y="Count",color="Count",color_continuous_scale="Purples",template="plotly_dark",text="Count")
        figif.update_traces(textposition="outside")
        figif.update_layout(height=300,margin=dict(t=5,b=5),coloraxis_showscale=False,xaxis_title="",**PLOT_LAYOUT)
        st.plotly_chart(figif,use_container_width=True)

    f4,f5=st.columns(2)
    with f4:
        st.markdown("**Age Category Counts**")
        ac=filtered["AgeCategory"].str.title().value_counts().reset_index()
        ac.columns=["AgeCategory","Count"]
        ac["_s"]=ac["AgeCategory"].map(lambda x: AGE_ORDER.index(x) if x in AGE_ORDER else 99)
        ac=ac.sort_values("_s").drop("_s",axis=1)
        figac=px.bar(ac,x="AgeCategory",y="Count",color="Count",color_continuous_scale="Teal",template="plotly_dark",text="Count")
        figac.update_traces(textposition="outside")
        figac.update_layout(height=300,margin=dict(t=5,b=5),coloraxis_showscale=False,xaxis_title="",**PLOT_LAYOUT)
        st.plotly_chart(figac,use_container_width=True)
    with f5:
        st.markdown("**MultiResistance Level**")
        mr2=filtered["MultiResistance"].value_counts().sort_index().reset_index()
        mr2.columns=["Level","Count"]
        figmr=px.bar(mr2,x="Level",y="Count",color="Level",color_continuous_scale="Reds",template="plotly_dark",text="Count")
        figmr.update_traces(textposition="outside")
        figmr.update_layout(height=300,margin=dict(t=5,b=5),coloraxis_showscale=False,xaxis_title="MultiResistance Score",**PLOT_LAYOUT)
        st.plotly_chart(figmr,use_container_width=True)

# TAB 5 — MODEL PERFORMANCE (ALL 15 ANTIBIOTICS)
with tab5:
    perf_df = pd.DataFrame(MODEL_DATA, columns=MODEL_COLS)

    st.markdown('<div class="section-header">Model Performance Summary — All 15 Antibiotics</div>', unsafe_allow_html=True)

    # Full styled table — tall enough to show all 15 rows without scrolling
    st.dataframe(
        perf_df.style
            .format({"Recall Score":"{:.3f}","F1 @ Best Recall":"{:.3f}","F1 Score":"{:.3f}","Recall @ Best F1":"{:.3f}"})
            .background_gradient(subset=["Recall Score","F1 @ Best Recall","F1 Score","Recall @ Best F1"], cmap="YlOrRd"),
        use_container_width=True,
        hide_index=True,
        height=600,
    )

    # Chart 1: Grouped bar — all 15 antibiotics, 4 metrics
    st.markdown('<div class="section-header">Recall & F1 Scores — All 15 Antibiotics</div>', unsafe_allow_html=True)

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name="Best Recall Score",
        x=perf_df["Antibiotic"], y=perf_df["Recall Score"],
        marker_color="#f97316",
        text=perf_df["Recall Score"].round(3), textposition="outside", textfont=dict(size=9),
    ))
    fig_bar.add_trace(go.Bar(
        name="F1 @ Best Recall",
        x=perf_df["Antibiotic"], y=perf_df["F1 @ Best Recall"],
        marker_color="#fb923c", opacity=0.80,
        text=perf_df["F1 @ Best Recall"].round(3), textposition="outside", textfont=dict(size=9),
    ))
    fig_bar.add_trace(go.Bar(
        name="Best F1 Score",
        x=perf_df["Antibiotic"], y=perf_df["F1 Score"],
        marker_color="#38bdf8",
        text=perf_df["F1 Score"].round(3), textposition="outside", textfont=dict(size=9),
    ))
    fig_bar.add_trace(go.Bar(
        name="Recall @ Best F1",
        x=perf_df["Antibiotic"], y=perf_df["Recall @ Best F1"],
        marker_color="#7dd3fc", opacity=0.80,
        text=perf_df["Recall @ Best F1"].round(3), textposition="outside", textfont=dict(size=9),
    ))
    fig_bar.update_layout(
        barmode="group",
        template="plotly_dark",
        height=560,
        yaxis=dict(range=[0, 1.15], title="Score", tickformat=".2f", gridcolor="#1e3a52"),
        xaxis=dict(title="", tickangle=-38, tickfont=dict(size=10)),
        legend=dict(orientation="h", y=1.06, x=0, font=dict(size=11)),
        margin=dict(t=40, b=10, l=10, r=10),
        font=dict(color="#cbd5e1"),
        **PLOT_LAYOUT,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Chart 2: Score Heatmap
    st.markdown('<div class="section-header">Score Heatmap — All Antibiotics × All Metrics</div>', unsafe_allow_html=True)

    heat_data = perf_df[["Antibiotic","Recall Score","F1 @ Best Recall","F1 Score","Recall @ Best F1"]].set_index("Antibiotic")
    fig_heat = px.imshow(
        heat_data,
        color_continuous_scale="RdYlGn",
        zmin=0.5, zmax=1.0,
        text_auto=".3f",
        aspect="auto",
        template="plotly_dark",
    )
    fig_heat.update_layout(
        height=560,
        margin=dict(t=20, b=10, l=10, r=10),
        xaxis=dict(title="", tickfont=dict(size=13), side="bottom"),
        yaxis=dict(title="", tickfont=dict(size=11)),
        coloraxis_colorbar=dict(title="Score", tickformat=".2f"),
        font=dict(color="#cbd5e1"),
        **PLOT_LAYOUT,
    )
    fig_heat.update_traces(textfont=dict(size=11))
    st.plotly_chart(fig_heat, use_container_width=True)

    # Chart 3: Scatter — F1 vs Recall trade-off
    st.markdown('<div class="section-header">F1 vs Recall Trade-off (All 15 Antibiotics)</div>', unsafe_allow_html=True)

    scatter_rows = []
    for _, row in perf_df.iterrows():
        scatter_rows.append({"Antibiotic": row["Antibiotic"], "Recall": row["Recall Score"],    "F1": row["F1 @ Best Recall"], "Mode": "Best Recall", "Model": row["Best Recall Model"]})
        scatter_rows.append({"Antibiotic": row["Antibiotic"], "Recall": row["Recall @ Best F1"],"F1": row["F1 Score"],          "Mode": "Best F1",     "Model": row["Best F1 Model"]})
    sdf = pd.DataFrame(scatter_rows)

    figs = px.scatter(
        sdf, x="Recall", y="F1",
        color="Mode", symbol="Mode",
        text="Antibiotic",
        hover_data=["Model"],
        color_discrete_map={"Best Recall":"#f97316","Best F1":"#38bdf8"},
        template="plotly_dark",
    )
    figs.update_traces(marker_size=13, textposition="top center", textfont=dict(size=9))
    figs.add_shape(type="line", x0=0.45, y0=0.45, x1=1.04, y1=1.04,
                   line=dict(color="#334155", dash="dot", width=1))
    figs.update_layout(
        height=560,
        margin=dict(t=20, b=10, l=10, r=10),
        xaxis=dict(range=[0.45, 1.04], title="Recall", gridcolor="#1e3a52", tickformat=".2f"),
        yaxis=dict(range=[0.45, 1.04], title="F1 Score", gridcolor="#1e3a52", tickformat=".2f"),
        legend=dict(orientation="h", y=1.06, x=0, font=dict(size=12)),
        font=dict(color="#cbd5e1"),
        **PLOT_LAYOUT,
    )
    st.plotly_chart(figs, use_container_width=True)

    # Per-antibiotic expandable cards in 3 columns
    st.markdown('<div class="section-header">Per-Antibiotic Model Detail</div>', unsafe_allow_html=True)
    cols_exp = st.columns(3)
    for i, (_, row) in enumerate(perf_df.iterrows()):
        with cols_exp[i % 3]:
            with st.expander(f"**{row['Antibiotic']}**"):
                d1, d2 = st.columns(2)
                d1.metric("Best Recall Model", row["Best Recall Model"])
                d2.metric("Recall Score", f"{row['Recall Score']:.3f}")
                d3, d4 = st.columns(2)
                d3.metric("Best F1 Model", row["Best F1 Model"])
                d4.metric("F1 Score", f"{row['F1 Score']:.3f}")
                d5, d6 = st.columns(2)
                d5.metric("F1 @ Best Recall", f"{row['F1 @ Best Recall']:.3f}")
                d6.metric("Recall @ Best F1", f"{row['Recall @ Best F1']:.3f}")

st.markdown("---")
with st.expander("\U0001f4cb Raw Data Explorer"):
    st.write(f"**{len(filtered):,} rows x {len(filtered.columns)} columns**")
    st.dataframe(filtered.head(300), use_container_width=True)
    st.download_button(
        label="Download filtered CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_resistance_data.csv",
        mime="text/csv",
    )