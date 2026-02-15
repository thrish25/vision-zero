import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. DATA & GEOGRAPHY ENGINE ---
# Reference dictionary for accurate Indian State centers
STATE_COORDS = {
    'Andaman and Nicobar Island': [11.7401, 92.6586], 'Andhra Pradesh': [15.9129, 79.7400],
    'Arunachal Pradesh': [28.2180, 94.7278], 'Assam': [26.2006, 92.9376],
    'Bihar': [25.0961, 85.3131], 'Chandigarh': [30.7333, 76.7794],
    'Chhattisgarh': [21.2787, 81.8661], 'Delhi': [28.6139, 77.2090],
    'Goa': [15.2993, 74.1240], 'Gujarat': [22.2587, 71.1924],
    'Haryana': [29.0588, 76.0856], 'Himachal Pradesh': [31.1048, 77.1734],
    'Jammu and Kashmir': [33.7782, 76.5762], 'Jharkhand': [23.6102, 85.2799],
    'Karnataka': [15.3173, 75.7139], 'Kerala': [10.8505, 76.2711],
    'Madhya Pradesh': [22.9734, 78.6569], 'Maharashtra': [19.7515, 75.7139],
    'Odisha': [20.9517, 85.0985], 'Punjab': [31.1471, 75.3412],
    'Rajasthan': [27.0238, 74.2179], 'Tamil Nadu': [11.1271, 78.6569],
    'Telangana': [18.1124, 79.0193], 'Uttar Pradesh': [26.8467, 80.9462],
    'West Bengal': [22.9868, 87.8550]
}

@st.cache_data
def load_and_fix():
    df = pd.read_csv("final_dataset.csv")
    # Recreate the 'Hour' column
    df['Hour'] = pd.to_datetime(df['Clock Time'], format='%H:%M').dt.hour
    # Fix Latitude/Longitude based on State Name for real accuracy
    df['Lat_Fixed'] = df['Location'].map(lambda x: STATE_COORDS.get(x, [20.59, 78.96])[0])
    df['Lon_Fixed'] = df['Location'].map(lambda x: STATE_COORDS.get(x, [20.59, 78.96])[1])
    return df

df = load_and_fix()
current_hour = datetime.now().hour

# --- 2. SIDEBAR ---
st.sidebar.title("🛡️ Vision Zero AI")
st.sidebar.write(f"**🕒 System Hour:** {current_hour}:00")

v_type = st.sidebar.selectbox("Your Vehicle Type", sorted(df['Vehicle Details'].unique()))
weather_input = st.sidebar.select_slider("Current Weather", ["Clear", "Rainy", "Foggy", "Stormy"])

# --- 3. MAIN INTERFACE ---
st.title("🛣️ Vision Zero: Highway Safety System")

col1, col2 = st.columns(2)
with col1:
    state = st.selectbox("🗺️ Select State", sorted(df['Location'].unique()))
with col2:
    # Requirement: "Highways" instead of subzones
    highway = st.selectbox("📍 Select Specific Highway", sorted(df['Highway Type'].unique()))

# Filter Data
active_df = df[(df['Location'] == state) & 
               (df['Highway Type'] == highway) & 
               (df['Vehicle Details'] == v_type)]

# --- 4. DANGER TIME ANALYSIS (CURRENT CONTEXT) ---
st.divider()
st.subheader(f"⚡ Current Context Analysis ({weather_input})")
current_weather_df = active_df[active_df['Weather'] == weather_input]

if not current_weather_df.empty:
    peak_hour = current_weather_df.groupby('Hour')['Count'].sum().idxmax()
    peak_val = current_weather_df.groupby('Hour')['Count'].sum().max()
    
    col_t1, col_t2 = st.columns(2)
    col_t1.metric("Peak Danger Hour", f"{peak_hour}:00", delta="High Risk", delta_color="inverse")
    col_t2.metric(f"Intensity ({weather_input})", f"{peak_val} Incidents")
else:
    st.info(f"No specific historical data for {weather_input} on this highway.")

# --- 5. ADVERSE WEATHER PROJECTIONS (RAINY & STORMY) ---
st.subheader("⛈️ Adverse Weather Projections")
aw_col1, aw_col2 = st.columns(2)
weathers_to_analyze = ["Rainy", "Stormy"]

for idx, bad_weather in enumerate(weathers_to_analyze):
    bw_df = active_df[active_df['Weather'] == bad_weather]
    target_col = aw_col1 if idx == 0 else aw_col2
    with target_col:
        if not bw_df.empty:
            bw_peak_hour = bw_df.groupby('Hour')['Count'].sum().idxmax()
            target_col.warning(f"**{bad_weather} Scenario**")
            target_col.metric(f"Avoid Travel At", f"{bw_peak_hour}:00")
        else:
            target_col.success(f"{bad_weather}: Low Risk")

# --- 6. LOCATION MAP (CORRECT DATA) ---
st.divider()
st.subheader(f"📍 Real-World Mapping: {state}")
if not active_df.empty:
    # Force the map to the real state center
    center_coords = STATE_COORDS.get(state, [20.59, 78.96])
    fig_map = px.scatter_mapbox(
        active_df, 
        lat="Lat_Fixed", lon="Lon_Fixed",
        color="Weather", size="Count",
        zoom=6, mapbox_style="carto-positron",
        title=f"Accident Points: {state} ({highway})"
    )
    fig_map.update_layout(mapbox_center={"lat": center_coords[0], "lon": center_coords[1]})
    st.plotly_chart(fig_map, use_container_width=True)

# --- 7. PATTERN ANALYSIS ---
st.divider()
st.subheader("📊 Comparative Pattern Analysis")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown(f"**Risk by Weather on {highway}**")
    highway_weather_data = df[df['Highway Type'] == highway].groupby('Weather')['Count'].sum().reset_index()
    fig_risk = px.bar(highway_weather_data, x="Weather", y="Count", color="Weather")
    st.plotly_chart(fig_risk, use_container_width=True)

with col_chart2:
    st.markdown("**Global Trend: When do accidents happen?**")
    pattern_data = df.groupby(['Time Category', 'Weather'])['Count'].sum().reset_index()
    fig_pattern = px.density_heatmap(pattern_data, x="Time Category", y="Weather", z="Count", color_continuous_scale="Viridis")
    st.plotly_chart(fig_pattern, use_container_width=True)