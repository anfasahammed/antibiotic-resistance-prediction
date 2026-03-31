#  CodeCure Biohackathon — Track B: Antibiotic Resistance Prediction

> **AI-powered antimicrobial resistance analysis, clinical decision support, and location-based treatment guidance**

---

##  Table of Contents

- [Project Overview](#project-overview)
- [Datasets Used](#datasets-used)
- [Project Structure](#project-structure)
- [Dashboards](#dashboards)
- [ML Models](#ml-models)
- [Data Preprocessing](#data-preprocessing)
- [Why CARD Dataset Was Not Used](#why-card-dataset-was-not-used)
- [How to Run](#how-to-run)
- [Dependencies](#dependencies)
- [Disclaimer](#disclaimer)

---

## 🔬 Project Overview

This project addresses **Track B: Antibiotic Resistance Prediction** of the CodeCure AI Biohackathon. Antimicrobial resistance (AMR) is one of the most critical global health challenges. This system uses machine learning and data visualization to:

- Predict antibiotic resistance patterns from bacterial phenotypic data
- Recommend the most effective antibiotics for a given bacterial species and patient profile
- Analyze location-based resistance trends in Osun State, Nigeria to **reduce unnecessary antibiotic testing costs**
- Classify multi-drug resistance (MDR), extensive drug resistance (XDR), and pan-drug resistance (PDR) status

Three interactive Streamlit dashboards were built to serve different users: **researchers, clinicians, and public health teams**.

---

##  Datasets Used

### 1. Primary Dataset — Antimicrobial Resistance Dataset (Mendeley)
**Source:** [https://data.mendeley.com/datasets/ccmrx8n7mk/1](https://data.mendeley.com/datasets/ccmrx8n7mk/1)
- Bacterial isolates from Osun State, Nigeria (locations: IFE, OSU, IWO, EDE)
- 5 antibiotics: Imipenem, Ceftazidime, Gentamicin, Augmentin, Ciprofloxacin
- Sample collection areas: Table (T), Soil Nearby (S), Concrete Slab (C)

**Cleaning steps applied:**
- Dropped name, sample number, and redundant numeric identifier columns
- Converted susceptibility results to standard R/I/S categories following CLSI/EUCAST breakpoint standards
- Computed `Resistance_Count` (0–5) and `Resistance_Level` (N / HR / VHR / XHR) per isolate
- No bacteria species information was present — only location and area data

**Output file:** `nigeria_encoded.csv`
-

---

### 2. Secondary Dataset — Multi-Resistance Antibiotic Susceptibility (Kaggle)
**Source:** [https://www.kaggle.com/datasets/adilimadeddinehosni/multi-resistance-antibiotic-susceptibility](https://www.kaggle.com/datasets/adilimadeddinehosni/multi-resistance-antibiotic-susceptibility)


 Clinical bacterial isolates with susceptibility test results (R / I / S)
- 9 bacterial species, 15 antibiotics tested
- Patient demographic data: Age, Gender, Comorbidities (Diabetes, Hypertension), Prior Hospitalization, Infection Frequency
- Used for: EDA dashboard, ML model training, and the antibiotic recommendation tool

**Cleaning steps applied:**
- Dropped irrelevant identifier and free-text columns
- Mapped age to categorical bins: Newborn, Child, Teenager, Young Adult, Senior Adult, Senior
- Assigned full species names (e.g., *Escherichia coli*, *Klebsiella pneumoniae*)
- Computed `MultiResistance` score (number of resistant antibiotics per isolate)
- Standardized R/I/S labels and removed nulls

**Output file:** `cleaned_antibiotic_resistance_dataset.csv`

---

### 3. CARD Dataset — Not Used *(see explanation below)*

---

##  Project Structure

```
CodeCure-TrackB/
│
├── datasets/
│   ├── Bacteria_dataset_Multiresistance.csv        # Raw secondary dataset (Kaggle)
│   ├── Dataset.xlsx                                # Raw primary dataset (Mendeley)
│   ├── cleaned_antibiotic_resistance_dataset.csv   # Cleaned primary dataset
│   └── nigeria_encoded.csv                         # Cleaned secondary dataset
│
├── notebooks/
│   ├── antibiotic-resistance-raw-dataset-cleaning.ipynb   # Data cleaning (primary dataset)
│   └── nigeria.ipynb                                       # Data cleaning + encoding (Nigeria dataset)
│
├── dashboards/
│   ├── dashboard.py                    # Dashboard 1: EDA + Model Performance
│   ├── treatment.py                    # Dashboard 2: Antibiotic Recommendation Tool
│   └── nigeria_dataset1_dashboard.py  # Dashboard 3: Nigeria Location-Based Analysis
│
└── README.md
```

---

##  Dashboards

### Dashboard 1 — `dashboard.py` — EDA & Model Performance
[Dashboard](https://model-dataset2.streamlit.app/)
**Purpose:** Data exploration and ML model results viewer for researchers and analysts.

**Features:**
- Summary metrics: total samples, average resistance count, MDR/XDR counts
- **Tab 1 – Overview:** Resistance rate per antibiotic (bar chart), RSI stacked profile, resistance count distribution, MultiResistance category breakdown
- **Tab 2 – Species Analysis:** Per-species sample counts, resistance/susceptibility/intermediate heatmaps across all 15 antibiotics × 9 species
- **Tab 3 – Antibiotic Families:** Resistance rates grouped by drug class (Beta-lactams, Carbapenems, Aminoglycosides, Fluoroquinolones, Phenicols, Nitrofurans, Polymyxins, Folate Pathway Inhibitors)
- **Tab 4 – Demographics:** Resistance by age category, gender breakdown, infection frequency, species distributions
- **Tab 5 – Model Performance:** Recall vs F1 trade-off for CatBoost and XGBoost models trained on 4 antibiotics (Imipenem, Gentamicin, Amikacin, Ciprofloxacin)
- Sidebar filters: bacteria species, age category, gender

---

### Dashboard 2 — `treatment.py` — Antibiotic Recommendation Tool
[link for the app](https://patient-hospital2.streamlit.app/)
**Purpose:** Clinical decision support tool for doctors — recommends the best 3 antibiotics based on patient filters.

**Features:**
- Select bacteria species, patient age category, and infection frequency
- Displays **Top 3 Recommended Antibiotics** ranked by susceptibility rate (%)
- MDR / XDR / PDR classification based on resistance across antibiotic classes
- Full susceptibility ranking table with colour gradient
- Bar chart of antibiotic effectiveness
- Heatmap of resistance profile for the selected filter
- Low sample size warning when < 5 records match the filter

**How it works:**
1. Filters the cleaned dataset by the selected bacteria and patient profile
2. Calculates `susceptibility rate = 1 - resistance rate` per antibiotic
3. Ranks antibiotics from highest to lowest susceptibility
4. Classifies MDR status by checking resistant classes: if ≥ 3 classes → MDR, if total−2 classes → XDR, if all → PDR

---

### Dashboard 3 — `nigeria_dataset1_dashboard.py` — Nigeria Location-Based Analysis
[Link for the app](https://nigeria-data.streamlit.app/)
**Purpose:** Helps public health officials and clinicians in Osun State, Nigeria determine which antibiotics to prioritize — **reducing the cost of full susceptibility testing** by predicting resistance patterns per location.

**Features:**
- Location selector (IFE, OSU, IWO, EDE) with optional area filter (Table, Soil Nearby, Concrete Slab)
- Resistance overview: average resistance count, MDR percentage, resistance classification level
- **Treatment Recommendations** panel:
  -  Recommended (success rate ≥ 70%)
  -  Use with Caution (50–69%)
  -  Avoid (< 50%)
  - Suggested first-line and alternative treatment plan
- **Tab 1 – Antibiotic Success Rates:** Per-location bar chart with threshold reference lines
- **Tab 2 – Location Analysis:** Resistance comparison across all 4 locations, average resistance count with error bars
- **Tab 3 – Area Analysis:** Resistance by sample collection area, Location × Area bubble chart
- **Tab 4 – Resistance Distribution:** Pie chart of resistance levels, histogram, stacked bar across all locations
- **Tab 5 – Heatmaps:** Location × Antibiotic resistance heatmap, antibiotic co-resistance correlation matrix

---

##  ML Models

Models were trained to predict resistance (R vs. non-R) for 4 key antibiotics using the cleaned primary dataset.

| Antibiotic | Best Recall Model | Recall Score | F1 @ Best Recall | Best F1 Model | F1 Score | Recall @ Best F1 |
|---|---|---|---|---|---|---|
| Imipenem | CatBoost 1 | 0.988 | 0.987 | CatBoost 1 | 0.987 | 0.988 |
| Gentamicin | CatBoost 3 | 0.889 | 0.741 | CatBoost 2 | 0.785 | 0.824 |
| Amikacin | CatBoost 3 | 0.937 | 0.727 | CatBoost 2 | 0.829 | 0.806 |
| Ciprofloxacin | CatBoost 3 | 0.920 | 0.531 | XGBoost | 0.612 | 0.820 |

**Features used:** Bacteria species, age category, gender, diabetes, hypertension, hospital history, infection frequency, other antibiotic results (cross-resistance features)

**Why Recall was prioritised:** In a clinical AMR context, a false negative (predicting Susceptible when actually Resistant) is more dangerous than a false positive. Missing a resistant case could lead to treatment failure. Recall was therefore the primary optimization metric.

---

##  Data Preprocessing

### Primary Dataset (`antibiotic-resistance-raw-dataset-cleaning.ipynb`)
- Dropped patient name, ID, and free-text columns
- Standardized bacterial species names to full scientific names
- Filled or dropped missing susceptibility values
- Created `AgeCategory` bins from raw age values
- Computed `MultiResistance` score (count of R labels per row)
- Final columns: Souches, patient features, 15 antibiotic columns (R/I/S), Age, Gender, AgeCategory, MultiResistance

### Secondary Dataset (`)
- Converted raw zone diameter or categorical values to R/I/S using standard CLSI/EUCAST breakpoints
- Computed `Resistance_Count` and `Resistance_Level` (N = None/Low, HR = High Resistance, VHR, XHR)
- Retained: Location, Area, 5 antibiotic columns, Resistance_Count, Resistance_Level

---

##  Why the CARD Dataset Was Not Used

The **Comprehensive Antibiotic Resistance Database (CARD)** was considered but ultimately excluded for the following reason:

The two bacterial species present in the secondary  dataset — ***Enterobacteria spp.*** and ***Citrobacter spp.*** — are listed at a genus/group level that does not have specific, mappable resistance gene records in CARD at that taxonomic resolution.

Attempting to query CARD for these species returns no matching gene-level data. Feeding zero-value gene feature vectors into a machine learning model is **not meaningfully zero — it is a data artifact**, and the model would learn from the absence of data rather than from true biological signals. This would produce misleading results and scientifically invalid predictions.

Therefore, CARD integration was excluded to preserve data integrity. The models were trained solely on phenotypic susceptibility data (R/I/S outcomes), which is both sufficient and scientifically sound for the scope of this project.

---

## ▶️ How to Run

### Prerequisites
```bash
pip install streamlit pandas numpy matplotlib seaborn plotly scikit-learn catboost xgboost
```

### Run Dashboard 1 — EDA & Model Performance
```bash
streamlit run dashboard.py
```
> Requires: `cleaned_antibiotic_resistance_dataset.csv` in the same directory

### Run Dashboard 2 — Antibiotic Recommendation Tool
```bash
streamlit run treatment.py
```
> Requires: `cleaned_antibiotic_resistance_dataset.csv` in the same directory

### Run Dashboard 3 — Nigeria Location Analysis
```bash
streamlit run nigeria_dataset1_dashboard.py
```
> Requires: `nigeria_encoded.csv` in the same directory

---

## 📦 Dependencies

| Library | Purpose |
|---|---|
| `streamlit` | Web dashboard framework |
| `pandas` | Data manipulation |
| `numpy` | Numerical operations |
| `plotly` | Interactive visualizations |
| `matplotlib` / `seaborn` | Static charts |
| `scikit-learn` | Model evaluation utilities |
| `catboost` | Primary ML model |
| `xgboost` | Secondary ML model |

---

##  Disclaimer

This project is a **decision support tool** built for a hackathon. It is not a substitute for clinical microbiological testing, culture results, or professional medical judgment. All treatment decisions must be made by qualified healthcare professionals in accordance with current clinical guidelines.

---

*Built for CodeCure Biohackathon — Track B: Antibiotic Resistance Prediction*
