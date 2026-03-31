import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import re

# ── Page config ─────────────────────────
st.set_page_config(page_title="Dashboard", layout="wide")

# ── Load dataset ────────────────────────
df = pd.read_csv("Bacteria_dataset_Multiresictance.csv")

# ── Normalize values ────────────────────
df = df.applymap(lambda x: str(x).strip().upper() if isinstance(x, str) else x)

# ── Antibiotic columns (fixed) ──────────
antibiotic_cols = [
    "Amoxicillin_Ampicillin",
    "Amoxicillin_Clavulanate",
    "Cefazolin",
    "Cefoxitin",
    "Cefotaxime_Ceftriaxone",
    "Imipenem",
    "Gentamicin",
    "Amikacin",
    "Nalidixic_Acid",
    "Ofloxacin",
    "Ciprofloxacin",
    "Chloramphenicol",
    "Cotrimoxazole",
    "Nitrofurantoin",
    "Colistin"
]

# ── Resistance count ────────────────────
df["Resistance_Count"] = (df[antibiotic_cols] == "R").sum(axis=1)

# ── KPI ────────────────────────────────
st.title("🦠 Antibiotic Resistance Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Total Samples", len(df))
col2.metric("Avg Resistance", round(df["Resistance_Count"].mean(), 2))
col3.metric("No. Antibiotics", len(antibiotic_cols))

# ── Resistance chart ────────────────────
resist_data = []

for col in antibiotic_cols:
    val = (df[col] == "R").mean() * 100
    resist_data.append({
        "Antibiotic": col,
        "Resistance %": round(val, 2)
    })

res_df = pd.DataFrame(resist_data)
res_df = res_df.sort_values(by="Resistance %", ascending=False)

fig = px.bar(
    res_df,
    x="Antibiotic",
    y="Resistance %",
    template="plotly_white",
    color="Resistance %",
    color_continuous_scale="Oranges"
)

st.plotly_chart(fig, use_container_width=True)

# ── Model Data ──────────────────────────
raw_data = [
    ["Imipenem","CatBoost 1 (0.988)",0.987,"CatBoost 1 (0.987)",0.988],
    ["Gentamicin","CatBoost 3 (0.8886)",0.741,"CatBoost 2 (0.7852)",0.8238],
    ["Amikacin","CatBoost 3 (0.9370)",0.727,"CatBoost 2 (0.8286)",0.8058],
    ["Ciprofloxacin","CatBoost 3 (0.9204)",0.531,"XGBoost (0.6116)",0.8201],
]

cols = [
    "Antibiotic",
    "Best_Recall_Model",
    "F1_of_Best_Recall",
    "Best_F1_Model",
    "Recall_of_Best_F1"
]

perf = pd.DataFrame(raw_data, columns=cols)

# ── Clean model names ───────────────────
def clean_model(text):
    text = re.sub(r'\d+(/\d+)?', '', text)
    model = re.match(r'([A-Za-z]+)', text).group(1)
    val = float(re.search(r'\((.*?)\)', text).group(1))
    return model, val

perf["Recall_Model"], perf["Recall_Value"] = zip(
    *perf["Best_Recall_Model"].apply(clean_model)
)

perf["F1_Model"], perf["F1_Value"] = zip(
    *perf["Best_F1_Model"].apply(clean_model)
)

# ── Model display ──────────────────────
st.subheader("🤖 Model Performance")

for _, row in perf.iterrows():
    st.markdown(f"""
**{row['Antibiotic']}**

- Recall Model: {row['Recall_Model']} ({row['Recall_Value']:.2f})
- F1: {row['F1_of_Best_Recall']:.2f}
- Best F1 Model: {row['F1_Model']} ({row['F1_Value']:.2f})
- Recall: {row['Recall_of_Best_F1']:.2f}
""")