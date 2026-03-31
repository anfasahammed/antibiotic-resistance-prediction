import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="Antibiotic Recommendation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------
# DARK THEME + UI FIXES
# -----------------------
st.markdown("""
<style>

/* GLOBAL BACKGROUND */
.stApp {
    background-color: #0e1117;
}

/* REMOVE HEADER */
header {visibility: hidden;}
.block-container {padding-top: 1rem;}

/* TEXT */
body, p, div, span, label {
    color: #e5e7eb !important;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #020617;
}
section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* SELECTBOX FIX (FINAL) */
div[data-baseweb="select"] > div {
    background-color: #111827 !important;
    color: #ffffff !important;
}
div[data-baseweb="select"] span {
    color: #ffffff !important;
}
div[role="listbox"] {
    background-color: #111827 !important;
}
div[role="option"] {
    background-color: #111827 !important;
    color: #ffffff !important;
}
div[role="option"]:hover {
    background-color: #1f2937 !important;
}
div[aria-selected="true"] {
    background-color: #374151 !important;
}

/* TABLE */
[data-testid="stDataFrame"] {
    background-color: #020617 !important;
}

/* REMOVE WHITE CONTAINER */
[data-testid="stAppViewContainer"] {
    background-color: #0e1117;
}

</style>
""", unsafe_allow_html=True)

# -----------------------
# LOAD DATA
# -----------------------
df = pd.read_csv("cleaned_antibiotic_resistance_dataset.csv")

antibiotics =  [
    'Amoxicillin_Ampicillin',
    'Amoxicillin_Clavulanate',
    'Cefazolin',
    'Cefoxitin',
    'Cefotaxime_Ceftriaxone',
    'Imipenem',
    'Gentamicin',
    'Amikacin',
    'Nalidixic_Acid',
    'Ofloxacin',
    'Ciprofloxacin',
    'Chloramphenicol',
    'Cotrimoxazole',
    'Nitrofurantoin',
    'Colistin'
]

# -----------------------
# ANTIBIOTIC CLASSES (FOR MDR)
# -----------------------
antibiotic_class = {
        'Amoxicillin_Ampicillin':'Beta_lactams',
        'Amoxicillin_Clavulanate':'Beta_lactams',
        'Cefazolin':'Beta_lactams',
        'Cefoxitin':'Beta_lactams',
        'Cefotaxime_Ceftriaxone':'Beta_lactams',
        'Imipenem':'Carbapenems',
        'Gentamicin':'Aminoglycosides',
        'Amikacin':'Aminoglycosides',
        'Nalidixic_Acid':'Fluoroquinolones',
        'Ofloxacin':"Fluoroquinolones",
        'Ciprofloxacin':"Fluoroquinolones",
        'Chloramphenicol':"Phenicols",
        'Cotrimoxazole':"Folate_pathway_inhibitors",
        'Nitrofurantoin':"Nitrofurans",
        'Colistin':"Polymyxins"
    }

# -----------------------
# HEADER
# -----------------------
st.markdown("<h1 style='text-align:center;'>🧬 Antibiotic Recommendation System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Clinical decision support using resistance patterns</p>", unsafe_allow_html=True)

# -----------------------
# SIDEBAR
# -----------------------
st.sidebar.header("Patient Filters")

bacteria = st.sidebar.selectbox("Bacteria (Souches)", sorted(df["Souches"].unique()))
age_category = st.sidebar.selectbox("Age Category (Optional)", ["All"] + sorted(df["AgeCategory"].dropna().unique().tolist()))
infection_freq = st.sidebar.selectbox("Infection Frequency (Optional)", ["All"] + sorted(df["Infection_Freq"].dropna().unique().tolist()))

# -----------------------
# FILTER DATA
# -----------------------
filtered_df = df[df["Souches"] == bacteria]

if age_category != "All":
    filtered_df = filtered_df[filtered_df["AgeCategory"] == age_category]

if infection_freq != "All":
    filtered_df = filtered_df[filtered_df["Infection_Freq"] == infection_freq]

if filtered_df.empty:
    st.error("No data available for selected filters")
    st.stop()

# -----------------------
# CALCULATIONS
# -----------------------
resistance_rate = (filtered_df[antibiotics] == 'R').mean()
susceptibility = 1 - resistance_rate
top3 = susceptibility.sort_values(ascending=False).head(3)

# -----------------------
# MDR / XDR / PDR LOGIC
# -----------------------
class_groups = {}
for ab, cls in antibiotic_class.items():
    class_groups.setdefault(cls, []).append(ab)

class_res = {}
for cls, cols in class_groups.items():
    class_res[cls] = (filtered_df[cols] == 'R').any(axis=1).mean()

num_resistant_classes = sum(v > 0.5 for v in class_res.values())
total_classes = len(class_groups)

if num_resistant_classes == total_classes:
    status = "PDR"
elif num_resistant_classes >= total_classes - 2:
    status = "XDR"
elif num_resistant_classes >= 3:
    status = "MDR"
else:
    status = "Non-MDR"

# -----------------------
# DISPLAY WARNING
# -----------------------

# -----------------------
# TOP RECOMMENDATIONS
# -----------------------
st.markdown("## 💊 Top Recommended Antibiotics")

cols = st.columns(3)

for i, (drug, value) in enumerate(top3.items()):
    with cols[i]:
        st.markdown(f"""
        <div style="
            height:160px;
            display:flex;
            flex-direction:column;
            justify-content:center;
            align-items:center;
            background-color:#1f2937;
            border-radius:12px;
        ">
            <div style="font-size:16px; color:#9ca3af;">{drug}</div>
            <div style="font-size:30px; font-weight:bold;">
                {value*100:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------
# SUMMARY
# -----------------------
st.markdown("## 🧠 Summary")

sample_count = len(filtered_df)

if sample_count < 5:
    st.error(f"⚠️ Very low sample size ({sample_count}) — results may be unreliable")

st.write(f"**Bacteria:** {bacteria}")
st.write(f"**Samples considered:** {sample_count}")

# -----------------------
# TABLE
# -----------------------
st.markdown("## 📊 Full Antibiotic Ranking")

result_df = pd.DataFrame({
    "Antibiotic": susceptibility.index,
    "Susceptibility (%)": susceptibility.values * 100
}).sort_values(by="Susceptibility (%)", ascending=False)

st.dataframe(
    result_df.style.background_gradient(cmap="viridis"),
    use_container_width=True
)

# -----------------------
# BAR CHART
# -----------------------
st.markdown("## 📈 Antibiotic Effectiveness")

fig, ax = plt.subplots(figsize=(10,5))
fig.patch.set_facecolor("#0e1117")
ax.set_facecolor("#0e1117")

colors = sns.color_palette("viridis", len(result_df))

sns.barplot(
    data=result_df,
    x="Antibiotic",
    y="Susceptibility (%)",
    palette=colors,
    ax=ax
)

ax.set_title("Susceptibility Distribution", color="white")
ax.set_ylabel("Susceptibility (%)", color="white")

ax.tick_params(axis='x', rotation=45, colors='white')
ax.tick_params(axis='y', colors='white')

plt.grid(alpha=0.2)
plt.tight_layout()

st.pyplot(fig)

# -----------------------
# HEATMAP
# -----------------------
st.markdown("## 🔥 Resistance Heatmap")

heatmap_data = (filtered_df[antibiotics] == 'R').mean().to_frame()

fig, ax = plt.subplots(figsize=(6,8))
fig.patch.set_facecolor("#0e1117")
ax.set_facecolor("#0e1117")

sns.heatmap(
    heatmap_data,
    annot=True,
    cmap="mako",
    linewidths=0.5,
    cbar=True,
    ax=ax
)

ax.tick_params(colors='white')
plt.title("Resistance Profile", color="white")

st.pyplot(fig)

# -----------------------
# FOOTER
# -----------------------
st.markdown("---")
st.caption("⚠️ Decision support only. Not a substitute for clinical guidelines.")