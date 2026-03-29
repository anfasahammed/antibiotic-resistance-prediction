import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Antibiotic Resistance Dashboard",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"  # This should open it by default
)

# COOL DARK THEME with Colorful Gradient Metrics
st.markdown("""
    <style>
    /* COMPLETELY HIDE the top header bar with all its contents */
    header[data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Remove top white bar */
    .block-container {
        padding-top: 1rem !important;
    }
    
    /* Force sidebar to ALWAYS be visible */
    [data-testid="stSidebar"] {
        min-width: 320px !important;
        max-width: 350px !important;
        transform: none !important;
        transition: none !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="false"] {
        transform: translateX(0) !important;
        margin-left: 0 !important;
    }
    
    /* Hide the collapse button on the left edge since sidebar is always visible */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* DARK BACKGROUND */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
    }
    
    .main {
        background-color: transparent !important;
    }
    
    .block-container {
        background-color: transparent !important;
    }
    
    /* TEXT COLORS FOR DARK THEME */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    p, span, div {
        color: #cbd5e1 !important;
    }
    
    /* COLORFUL GRADIENT METRIC CARDS */
    div[data-testid="stMetric"]:nth-of-type(1) {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        padding: 25px !important;
        border-radius: 16px !important;
        border: none !important;
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4) !important;
    }
    
    div[data-testid="stMetric"]:nth-of-type(2) {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        padding: 25px !important;
        border-radius: 16px !important;
        border: none !important;
        box-shadow: 0 8px 16px rgba(240, 147, 251, 0.4) !important;
    }
    
    div[data-testid="stMetric"]:nth-of-type(3) {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        padding: 25px !important;
        border-radius: 16px !important;
        border: none !important;
        box-shadow: 0 8px 16px rgba(79, 172, 254, 0.4) !important;
    }
    
    div[data-testid="stMetric"]:nth-of-type(4) {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
        padding: 25px !important;
        border-radius: 16px !important;
        border: none !important;
        box-shadow: 0 8px 16px rgba(67, 233, 123, 0.4) !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.95) !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stMetricDelta"] {
        color: rgba(255, 255, 255, 0.95) !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        background: rgba(255, 255, 255, 0.2);
        padding: 4px 10px;
        border-radius: 20px;
    }
    
    .main-header {
        font-size: 2.2rem;
        font-weight: 600;
        color: #ffffff !important;
        text-align: center;
        padding: 30px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        margin-bottom: 40px;
        letter-spacing: -0.5px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header span {
        color: #ffffff !important;
    }
    
    /* GLASS-MORPHISM RECOMMENDATION BOXES */
    .recommendation-box {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(16, 185, 129, 0.15) 100%) !important;
        padding: 25px;
        border-radius: 16px;
        border: 1px solid rgba(34, 197, 94, 0.3) !important;
        border-left: 4px solid #22c55e !important;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .recommendation-box * {
        color: #86efac !important;
    }
    
    .recommendation-box h3 {
        color: #4ade80 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .warning-box {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(251, 191, 36, 0.15) 100%) !important;
        padding: 25px;
        border-radius: 16px;
        border: 1px solid rgba(245, 158, 11, 0.3) !important;
        border-left: 4px solid #f59e0b !important;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .warning-box * {
        color: #fde047 !important;
    }
    
    .warning-box h3 {
        color: #fbbf24 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .danger-box {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.15) 100%) !important;
        padding: 25px;
        border-radius: 16px;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        border-left: 4px solid #ef4444 !important;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .danger-box * {
        color: #fca5a5 !important;
    }
    
    .danger-box h3 {
        color: #f87171 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    /* DARK SIDEBAR */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #334155 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    .sidebar-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff !important;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 2px solid rgba(167, 139, 250, 0.5);
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .info-section {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%) !important;
        padding: 18px;
        border-radius: 12px;
        margin: 15px 0;
        border-left: 3px solid #a78bfa !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .info-section h3 {
        color: #c4b5fd !important;
    }
    
    .info-section * {
        color: #cbd5e1 !important;
    }
    
    /* SELECTBOX - DARK STYLE WITH BETTER CONTRAST */
    .stSelectbox > div > div {
        background: rgba(30, 41, 59, 0.9) !important;
        border: 2px solid rgba(167, 139, 250, 0.5) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
    }
    
    .stSelectbox label {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* Dropdown options should be readable */
    div[role="listbox"] {
        background-color: #ffffff !important;
    }
    
    div[role="option"] {
        color: #111827 !important;
        background-color: #ffffff !important;
    }
    
    div[role="option"]:hover {
        background-color: #f3f4f6 !important;
    }
    
    /* CHECKBOX - DARK STYLE */
    .stCheckbox label {
        color: #f1f5f9 !important;
        font-weight: 500 !important;
    }
    
    /* PROGRESS BARS - COLORFUL */
    .stProgress > div > div {
        background: linear-gradient(90deg, #1e293b 0%, #334155 100%) !important;
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #22c55e 0%, #10b981 50%, #059669 100%) !important;
        box-shadow: 0 0 10px rgba(34, 197, 94, 0.5);
    }
    
    /* TABS - COOL DARK STYLE */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(30, 41, 59, 0.5) !important;
        gap: 10px;
        border-radius: 12px;
        padding: 8px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8 !important;
        background: transparent !important;
        border-radius: 8px;
        font-weight: 600 !important;
        padding: 12px 20px;
        font-size: 1rem !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        background: linear-gradient(135deg, rgba(167, 139, 250, 0.3) 0%, rgba(139, 92, 246, 0.3) 100%) !important;
        border-bottom: 3px solid #a78bfa !important;
        box-shadow: 0 4px 12px rgba(167, 139, 250, 0.3);
    }
    </style>
""", unsafe_allow_html=True)
#
st.markdown("""
<style>

/* FIX DOUBLE KEYBOARD */
div[data-baseweb="popover"] {
    z-index: 9999 !important;
}

div[data-baseweb="select"] {
    position: relative !important;
    z-index: 1 !important;
}

input, textarea {
    z-index: auto !important;
}

[data-testid="stAppViewContainer"] {
    overflow: visible !important;
}

</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Nigeria_encoded.csv")
    return df

# Dark theme configuration for Plotly charts
def apply_dark_theme(fig):
    """Apply consistent dark theme to Plotly figures"""
    fig.update_layout(
        paper_bgcolor='rgba(30, 41, 59, 0.5)',  # Dark semi-transparent background
        plot_bgcolor='rgba(15, 23, 42, 0.3)',    # Darker plot area
        font=dict(
            color='#f1f5f9',  # Light text
            size=13
        ),
        title_font=dict(
            color='#ffffff',
            size=16,
            family='Inter'
        ),
        legend=dict(
            bgcolor='rgba(30, 41, 59, 0.8)',
            bordercolor='rgba(167, 139, 250, 0.3)',
            borderwidth=1,
            font=dict(color='#f1f5f9')
        ),
        xaxis=dict(
            gridcolor='rgba(148, 163, 184, 0.1)',
            color='#cbd5e1'
        ),
        yaxis=dict(
            gridcolor='rgba(148, 163, 184, 0.1)',
            color='#cbd5e1'
        )
    )
    return fig

df = load_data()

# Title
st.markdown('''
<div class="main-header">
    <div style="font-size: 2.5rem; font-weight: 700; text-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);">
        Antibiotic Resistance Dashboard
    </div>
    <div style="font-size: 1.3rem; font-weight: 400; margin-top: 10px; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);">
        Osun State, Nigeria
    </div>
</div>
''', unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown('<div class="sidebar-header">Patient Information</div>', unsafe_allow_html=True)

# Area mapping dictionary
area_mapping = {
    "T": "Table",
    "S": "Soil Nearby",
    "C": "Concrete Slab"
}

# Reverse mapping for filtering
area_reverse_mapping = {v: k for k, v in area_mapping.items()}

# Location selection
with st.sidebar:
    location = st.selectbox(
        "Select Patient Location",
        options=["Select Location", "IFE", "OSU", "IWO", "EDE"],
        index=0
    )

# Area selection (optional)
show_area = st.sidebar.checkbox("Filter by Sample Collection Area", value=False)
area_display = None
if show_area:
    with st.sidebar:
        area_display = st.selectbox(
        "Select Collection Area Type",
        options=["All"] + list(area_mapping.values()),
        index=0,
        help="Filter by the type of area where samples were collected"
    )

st.sidebar.markdown("---")
st.sidebar.markdown('<div class="info-section">', unsafe_allow_html=True)
st.sidebar.markdown("### Dashboard Sections")
st.sidebar.markdown("""
- Treatment Recommendation
- Resistance Analysis  
- Visual Analytics (EDA)
- Location Comparison
""")
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Main content
if location != "Select Location":
    
    # Filter data for selected location
    location_data = df[df['Location'] == location]
    
    # Apply area filter if selected
    if show_area and area_display and area_display != "All":
        area = area_reverse_mapping[area_display]
        location_data = location_data[location_data['Area'] == area]
    
    total_patients = len(location_data)
    
    # Handle case when no patients match the filter
    if total_patients == 0:
        st.error(f"⚠️ No patients found for Location: {location}" + 
                (f" and Area: {area_display}" if show_area and area_display != "All" else ""))
        st.info("Please select a different location or area filter.")
        st.stop()
    
    # Calculate resistance metrics
    avg_resistance_count = location_data['Resistance_Count'].mean()
    
    # Classify resistance level
    if avg_resistance_count < 1.5:
        resistance_level = "LOW"
        resistance_color = "#22c55e"
        resistance_symbol = "●"
    elif avg_resistance_count < 2.5:
        resistance_level = "MODERATE"
        resistance_color = "#f59e0b"
        resistance_symbol = "●"
    elif avg_resistance_count < 3.5:
        resistance_level = "HIGH"
        resistance_color = "#ef4444"
        resistance_symbol = "●"
    else:
        resistance_level = "VERY HIGH"
        resistance_color = "#dc2626"
        resistance_symbol = "●"
    
    # Calculate resistance percentages
    resistance_distribution = location_data['Resistance_Level'].value_counts()
    
    # ============== SECTION 1: RESISTANCE OVERVIEW ==============
    st.markdown('<h3 style="font-size: 1.4rem; margin-bottom: 1rem;">Resistance Overview</h3>', unsafe_allow_html=True)
    
    # Show current filters
    filter_info = f"**Showing:** {location}"
    if show_area and area_display and area_display != "All":
        filter_info += f" | Area: {area_display}"
    st.markdown(filter_info)
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Location",
            value=location,
            delta=f"{total_patients} patients"
        )
    
    with col2:
        st.metric(
            label="Avg Resistance Count",
            value=f"{avg_resistance_count:.2f}",
            delta=f"out of 5 antibiotics"
        )
    
    with col3:
        st.metric(
            label="Resistance Level",
            value=resistance_level,
            delta=resistance_symbol,
            delta_color="off"
        )
    
    with col4:
        mdr_count = len(location_data[location_data['Resistance_Count'] >= 3])
        mdr_percentage = (mdr_count / total_patients) * 100
        st.metric(
            label="MDR Cases",
            value=f"{mdr_percentage:.1f}%",
            delta=f"{mdr_count}/{total_patients}"
        )
    
    # ============== SECTION 2: TREATMENT RECOMMENDATION ==============
    st.markdown('<h3 style="font-size: 1.4rem; margin-bottom: 1rem;">Treatment Recommendations</h3>', unsafe_allow_html=True)
    
    # Calculate antibiotic success rates
    antibiotics = ['IMIPENEM', 'CEFTAZIDIME', 'GENTAMICIN', 'AUGMENTIN', 'CIPROFLOXACIN']
    antibiotic_data = []
    
    for antibiotic in antibiotics:
        susceptible = (location_data[antibiotic] == 'S').sum()
        resistant = (location_data[antibiotic] == 'R').sum()
        intermediate = (location_data[antibiotic] == 'I').sum()
        success_rate = (susceptible / total_patients) * 100
        
        antibiotic_data.append({
            'Antibiotic': antibiotic,
            'Success_Rate': success_rate,
            'Susceptible': susceptible,
            'Resistant': resistant,
            'Intermediate': intermediate
        })
    
    # Sort by success rate
    antibiotic_data.sort(key=lambda x: x['Success_Rate'], reverse=True)
    
    # Categorize antibiotics
    recommended = [a for a in antibiotic_data if a['Success_Rate'] >= 70]
    moderate = [a for a in antibiotic_data if 50 <= a['Success_Rate'] < 70]
    avoid = [a for a in antibiotic_data if a['Success_Rate'] < 50]
    
    # Display recommendations
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Recommended
        if recommended:
            st.markdown('<div class="recommendation-box">', unsafe_allow_html=True)
            st.markdown('<h4 style="font-size: 1.1rem; margin-bottom: 0.5rem;">RECOMMENDED (Success Rate ≥ 70%)</h4>', unsafe_allow_html=True)
            for i, ab in enumerate(recommended, 1):
                st.markdown(f'<p style="font-size: 0.95rem; margin: 0.3rem 0;"><strong>{i}. {ab["Antibiotic"]}</strong> → <strong>{ab["Success_Rate"]:.1f}%</strong> success rate</p>', unsafe_allow_html=True)
                st.progress(ab['Success_Rate'] / 100)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            st.markdown('<h4 style="font-size: 1.1rem; margin-bottom: 0.5rem;">NO HIGHLY EFFECTIVE ANTIBIOTICS</h4>', unsafe_allow_html=True)
            st.markdown('<p style="font-size: 0.9rem;">Consider combination therapy and obtain culture immediately</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Moderate
        if moderate:
            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            st.markdown('<h4 style="font-size: 1.1rem; margin-bottom: 0.5rem;">USE WITH CAUTION (Success Rate 50-69%)</h4>', unsafe_allow_html=True)
            for ab in moderate:
                st.markdown(f'<p style="font-size: 0.95rem; margin: 0.3rem 0;"><strong>{ab["Antibiotic"]}</strong> → <strong>{ab["Success_Rate"]:.1f}%</strong> success rate</p>', unsafe_allow_html=True)
                st.progress(ab['Success_Rate'] / 100)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Avoid
        if avoid:
            st.markdown('<div class="danger-box">', unsafe_allow_html=True)
            st.markdown('<h4 style="font-size: 1.1rem; margin-bottom: 0.5rem;">AVOID (Success Rate < 50%)</h4>', unsafe_allow_html=True)
            for ab in avoid:
                st.markdown(f'<p style="font-size: 0.95rem; margin: 0.3rem 0;"><strong>{ab["Antibiotic"]}</strong> → <strong>{ab["Success_Rate"]:.1f}%</strong> success rate</p>', unsafe_allow_html=True)
                st.progress(ab['Success_Rate'] / 100)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Treatment plan
        st.markdown('<h4 style="font-size: 1.1rem; margin-top: 1rem; margin-bottom: 0.5rem;">Treatment Plan</h4>', unsafe_allow_html=True)
        if recommended:
            st.markdown(f'<p style="font-size: 0.9rem; margin: 0.2rem 0;"><strong>1. First-line:</strong> {recommended[0]["Antibiotic"]} ({recommended[0]["Success_Rate"]:.1f}%)</p>', unsafe_allow_html=True)
            if len(recommended) > 1:
                st.markdown(f'<p style="font-size: 0.9rem; margin: 0.2rem 0;"><strong>2. Alternative:</strong> {recommended[1]["Antibiotic"]} ({recommended[1]["Success_Rate"]:.1f}%)</p>', unsafe_allow_html=True)
            elif moderate:
                st.markdown(f'<p style="font-size: 0.9rem; margin: 0.2rem 0;"><strong>2. Alternative:</strong> {moderate[0]["Antibiotic"]} ({moderate[0]["Success_Rate"]:.1f}%)</p>', unsafe_allow_html=True)
        elif moderate:
            st.markdown(f'<p style="font-size: 0.9rem; margin: 0.2rem 0;"><strong>1. Best available:</strong> {moderate[0]["Antibiotic"]} ({moderate[0]["Success_Rate"]:.1f}%)</p>', unsafe_allow_html=True)
        
        st.markdown('<p style="font-size: 0.9rem; margin: 0.2rem 0;"><strong>3.</strong> Obtain culture & susceptibility testing</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 0.9rem; margin: 0.2rem 0;"><strong>4.</strong> Adjust based on culture results</p>', unsafe_allow_html=True)
        
        if mdr_percentage > 30:
            st.warning("High MDR prevalence - Consider infectious disease consultation")
    
    # ============== SECTION 3: VISUAL ANALYTICS ==============
    st.markdown('<h3 style="font-size: 1.4rem; margin-bottom: 1rem;">Visual Analytics (EDA)</h3>', unsafe_allow_html=True)
    
    # Tab layout for different visualizations
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Antibiotic Success Rates", 
        "Location Analysis", 
        "Area Analysis",
        "Resistance Distribution",
        "Heatmaps"
    ])
    
    with tab1:
        st.markdown("### Antibiotic Effectiveness Comparison")
        
        # Create bar chart for current location
        ab_df = pd.DataFrame(antibiotic_data)
        
        fig = go.Figure()
        
        colors = ['#4caf50' if x >= 70 else '#ff9800' if x >= 50 else '#f44336' 
                  for x in ab_df['Success_Rate']]
        
        fig.add_trace(go.Bar(
            x=ab_df['Antibiotic'],
            y=ab_df['Success_Rate'],
            marker_color=colors,
            text=ab_df['Success_Rate'].round(1),
            texttemplate='%{text}%',
            textposition='outside',
            name='Success Rate'
        ))
        
        fig.update_layout(
            title=f"Antibiotic Success Rates in {location}",
            xaxis_title="Antibiotic",
            yaxis_title="Success Rate (%)",
            yaxis_range=[0, 100],
            height=500,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        fig.add_hline(y=70, line_dash="dash", line_color="#22c55e", 
                     annotation_text="Recommended threshold (70%)", annotation_font_color="#86efac")
        fig.add_hline(y=50, line_dash="dash", line_color="#f59e0b", 
                     annotation_text="Caution threshold (50%)", annotation_font_color="#fde047")
        
        # Apply dark theme
        fig = apply_dark_theme(fig)
        fig = apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.markdown("### Detailed Statistics")
        detail_df = pd.DataFrame(antibiotic_data)
        detail_df = detail_df[['Antibiotic', 'Success_Rate', 'Susceptible', 'Intermediate', 'Resistant']]
        detail_df['Success_Rate'] = detail_df['Success_Rate'].round(1).astype(str) + '%'
        st.dataframe(detail_df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.markdown("### Location vs Antibiotic Resistance")
        
        # Calculate resistance rates for all locations
        location_antibiotic_data = []
        for loc in ['IFE', 'OSU', 'IWO', 'EDE']:
            loc_data = df[df['Location'] == loc]
            for ab in antibiotics:
                resistant = (loc_data[ab] == 'R').sum()
                total = len(loc_data)
                resistance_rate = (resistant / total) * 100
                location_antibiotic_data.append({
                    'Location': loc,
                    'Antibiotic': ab,
                    'Resistance_Rate': resistance_rate
                })
        
        loc_ab_df = pd.DataFrame(location_antibiotic_data)
        
        # Grouped bar chart
        fig = px.bar(
            loc_ab_df,
            x='Location',
            y='Resistance_Rate',
            color='Antibiotic',
            barmode='group',
            title='Resistance Rates by Location and Antibiotic',
            labels={'Resistance_Rate': 'Resistance Rate (%)'},
            height=500,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Location",
            yaxis_title="Resistance Rate (%)"
        )
        
        # Apply dark theme
        fig = apply_dark_theme(fig)
        fig = apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics by location
        st.markdown("### Average Resistance Count by Location")
        
        location_summary = df.groupby('Location').agg({
            'Resistance_Count': ['mean', 'std', 'min', 'max']
        }).round(2)
        location_summary.columns = ['Mean', 'Std Dev', 'Min', 'Max']
        location_summary = location_summary.reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=location_summary['Location'],
            y=location_summary['Mean'],
            error_y=dict(type='data', array=location_summary['Std Dev']),
            marker_color=['#4caf50' if x < 2 else '#ff9800' if x < 3 else '#f44336' 
                          for x in location_summary['Mean']],
            text=location_summary['Mean'].round(2),
            textposition='outside'
        ))
        
        fig.update_layout(
            title='Average Number of Resistant Antibiotics by Location',
            xaxis_title='Location',
            yaxis_title='Average Resistance Count',
            height=400,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        fig = apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### Area vs Antibiotic Resistance")
        
        # Calculate resistance rates for all areas
        area_antibiotic_data = []
        for ar in ['T', 'S', 'C']:
            area_data = df[df['Area'] == ar]
            area_name = area_mapping[ar]
            for ab in antibiotics:
                resistant = (area_data[ab] == 'R').sum()
                total = len(area_data)
                resistance_rate = (resistant / total) * 100
                area_antibiotic_data.append({
                    'Area': area_name,
                    'Antibiotic': ab,
                    'Resistance_Rate': resistance_rate
                })
        
        area_ab_df = pd.DataFrame(area_antibiotic_data)
        
        fig = px.bar(
            area_ab_df,
            x='Area',
            y='Resistance_Rate',
            color='Antibiotic',
            barmode='group',
            title='Resistance Rates by Area Type and Antibiotic',
            labels={'Resistance_Rate': 'Resistance Rate (%)'},
            height=500,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        fig = apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        
        # Location + Area combination
        st.markdown("### Location × Area Resistance Analysis")
        
        location_area_data = []
        for loc in ['IFE', 'OSU', 'IWO', 'EDE']:
            for ar in ['T', 'S', 'C']:
                filtered = df[(df['Location'] == loc) & (df['Area'] == ar)]
                if len(filtered) > 0:
                    avg_resistance = filtered['Resistance_Count'].mean()
                    location_area_data.append({
                        'Location': loc,
                        'Area': area_mapping[ar],
                        'Avg_Resistance': avg_resistance,
                        'Patients': len(filtered)
                    })
        
        loc_area_df = pd.DataFrame(location_area_data)
        
        fig = px.scatter(
            loc_area_df,
            x='Location',
            y='Area',
            size='Patients',
            color='Avg_Resistance',
            color_continuous_scale='RdYlGn_r',
            title='Average Resistance by Location and Area (bubble size = number of patients)',
            height=400,
            labels={'Avg_Resistance': 'Avg Resistance Count'}
        )
        
        fig = apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("### Resistance Level Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart for resistance levels
            resistance_counts = location_data['Resistance_Level'].value_counts()
            
            colors_map = {
                'N': '#4caf50',
                'HR': '#ff9800',
                'VHR': '#ff5722',
                'XHR': '#d32f2f'
            }
            
            fig = go.Figure(data=[go.Pie(
                labels=resistance_counts.index,
                values=resistance_counts.values,
                marker=dict(colors=[colors_map.get(x, '#999') for x in resistance_counts.index]),
                hole=0.4,
                textinfo='label+percent',
                textfont_size=14
            )])
            
            fig.update_layout(
                title=f'Resistance Level Distribution in {location}',
                height=400,
                showlegend=True
            )
            
            fig = apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Histogram of resistance counts
            fig = px.histogram(
                location_data,
                x='Resistance_Count',
                nbins=6,
                title=f'Distribution of Resistance Count in {location}',
                labels={'Resistance_Count': 'Number of Resistant Antibiotics'},
                color_discrete_sequence=['#1f77b4'],
                height=400
            )
            
            fig.update_layout(
                xaxis_title='Number of Resistant Antibiotics (0-5)',
                yaxis_title='Number of Patients',
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            fig = apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        
        # Resistance level comparison across locations
        st.markdown("### Resistance Level Comparison Across All Locations")
        
        resistance_comparison = []
        for loc in ['IFE', 'OSU', 'IWO', 'EDE']:
            loc_data = df[df['Location'] == loc]
            for level in ['N', 'HR', 'VHR', 'XHR']:
                count = (loc_data['Resistance_Level'] == level).sum()
                percentage = (count / len(loc_data)) * 100
                resistance_comparison.append({
                    'Location': loc,
                    'Level': level,
                    'Percentage': percentage
                })
        
        resist_comp_df = pd.DataFrame(resistance_comparison)
        
        fig = px.bar(
            resist_comp_df,
            x='Location',
            y='Percentage',
            color='Level',
            barmode='stack',
            title='Resistance Level Distribution by Location (Stacked)',
            labels={'Percentage': 'Percentage of Patients (%)'},
            color_discrete_map={
                'N': '#4caf50',
                'HR': '#ff9800',
                'VHR': '#ff5722',
                'XHR': '#d32f2f'
            },
            height=400
        )
        
        fig = apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.markdown("### Heatmap Visualizations")
        
        # Heatmap: Location vs Antibiotic (Resistance Rate)
        heatmap_data = []
        for loc in ['IFE', 'OSU', 'IWO', 'EDE']:
            loc_data = df[df['Location'] == loc]
            row = {'Location': loc}
            for ab in antibiotics:
                resistant = (loc_data[ab] == 'R').sum()
                total = len(loc_data)
                resistance_rate = (resistant / total) * 100
                row[ab] = resistance_rate
            heatmap_data.append(row)
        
        heatmap_df = pd.DataFrame(heatmap_data)
        heatmap_df = heatmap_df.set_index('Location')
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_df.values,
            x=heatmap_df.columns,
            y=heatmap_df.index,
            colorscale='RdYlGn_r',
            text=heatmap_df.values.round(1),
            texttemplate='%{text}%',
            textfont={"size": 12},
            colorbar=dict(title="Resistance<br>Rate (%)")
        ))
        
        fig.update_layout(
            title='Resistance Rate Heatmap: Location × Antibiotic',
            xaxis_title='Antibiotic',
            yaxis_title='Location',
            height=400
        )
        
        fig = apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        
        # Correlation heatmap between antibiotics
        st.markdown("### Antibiotic Co-Resistance Correlation")
        
        # Convert R/I/S to binary (R=1, S/I=0) for correlation
        corr_data = df.copy()
        for ab in antibiotics:
            corr_data[f'{ab}_R'] = (corr_data[ab] == 'R').astype(int)
        
        corr_cols = [f'{ab}_R' for ab in antibiotics]
        correlation_matrix = corr_data[corr_cols].corr()
        correlation_matrix.columns = antibiotics
        correlation_matrix.index = antibiotics
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale='Blues',
            text=correlation_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 12},
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title='Antibiotic Co-Resistance Correlation Matrix<br>(Higher values = antibiotics that resist together)',
            xaxis_title='Antibiotic',
            yaxis_title='Antibiotic',
            height=500
        )
        
        fig = apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("High correlation (darker blue) means if a patient is resistant to one antibiotic, they're likely resistant to the other.")

else:
    # Landing page when no location is selected
    st.markdown("## Welcome to the Antibiotic Resistance Dashboard")
    
    st.markdown("""
    ### How to Use This Dashboard:
    
    1. **Select a location** from the sidebar (IFE, OSU, IWO, or EDE)
    2. **Optionally filter by sample collection area** (Table, Soil Nearby, or Concrete Slab)
    3. **View personalized treatment recommendations** based on resistance patterns
    4. **Explore visualizations** to understand resistance trends
    
    ### Dataset Overview:
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Patients", len(df))
    
    with col2:
        st.metric("Locations", df['Location'].nunique())
    
    with col3:
        st.metric("Antibiotics Tested", 5)
    
    with col4:
        mdr_total = len(df[df['Resistance_Count'] >= 3])
        st.metric("MDR Cases", f"{(mdr_total/len(df)*100):.1f}%")
    
    # Overall statistics
    st.markdown("### Overall Antibiotic Effectiveness")
    
    nationwide_data = []
    for ab in ['IMIPENEM', 'CEFTAZIDIME', 'GENTAMICIN', 'AUGMENTIN', 'CIPROFLOXACIN']:
        susceptible = (df[ab] == 'S').sum()
        success_rate = (susceptible / len(df)) * 100
        nationwide_data.append({
            'Antibiotic': ab,
            'Success_Rate': success_rate
        })
    
    nationwide_df = pd.DataFrame(nationwide_data)
    nationwide_df = nationwide_df.sort_values('Success_Rate', ascending=False)
    
    fig = go.Figure()
    
    colors = ['#4caf50' if x >= 70 else '#ff9800' if x >= 50 else '#f44336' 
              for x in nationwide_df['Success_Rate']]
    
    fig.add_trace(go.Bar(
        x=nationwide_df['Antibiotic'],
        y=nationwide_df['Success_Rate'],
        marker_color=colors,
        text=nationwide_df['Success_Rate'].round(1),
        texttemplate='%{text}%',
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Nationwide Antibiotic Success Rates",
        xaxis_title="Antibiotic",
        yaxis_title="Success Rate (%)",
        yaxis_range=[0, 100],
        height=500,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig = apply_dark_theme(fig)
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("Select a location from the sidebar to get started!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Antibiotic Resistance Analysis Dashboard</strong></p>
    <p>Osun State, Nigeria</p>
    <p style='font-size: 0.9rem; margin-top: 10px;'>Data-Driven Treatment Decisions for Better Patient Outcomes</p>
    <p style='font-size: 0.8rem; color: #999; margin-top: 15px;'>This is a decision support tool. Always consult with healthcare professionals for final treatment decisions.</p>
</div>
""", unsafe_allow_html=True)
