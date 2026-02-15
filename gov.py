import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. AUTHORIZED PERSONNEL DATA ---
AUTH_DB = {
    "admin@transport.gov": {"name": "Director General", "id": "GOV-001", "pin": "1234"},
    "officer@safety.gov": {"name": "Safety Inspector", "id": "GOV-088", "pin": "5678"}
}

# Accurate State Centers for Mapping
STATE_COORDS = {
    'Andhra Pradesh': [15.9129, 79.7400], 'Bihar': [25.0961, 85.3131],
    'Gujarat': [22.2587, 71.1924], 'Maharashtra': [19.7515, 75.7139],
    'Tamil Nadu': [11.1271, 78.6569], 'Uttar Pradesh': [26.8467, 80.9462],
    'West Bengal': [22.9868, 87.8550], 'Delhi': [28.6139, 77.2090]
}

def login_gate():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🏛️ Government Policy Authorization")
        st.info("Access Restricted to Transport & Infrastructure Officials.")
        with st.form("Login"):
            email = st.text_input("Official Email ID")
            pin = st.text_input("Security PIN", type="password")
            submit = st.form_submit_button("Verify Credentials")
            if submit:
                user_data = AUTH_DB.get(email)
                if user_data and user_data["pin"] == pin:
                    st.session_state.authenticated = True
                    st.session_state.user = user_data["name"]
                    st.rerun()
                else:
                    st.error("Access Denied: Invalid Credentials")
        return False
    return True

# --- 2. GOV INTERFACE ---
if login_gate():
    st.set_page_config(page_title="Gov Safety Portal", layout="wide")
    
    # Sidebar
    st.sidebar.success(f"Verified: {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

    st.title("🛰️ Policy Strategy & Risk DNA Engine")
    
    # 3. LOAD DATA
    @st.cache_data
    def load_gov_data():
        df = pd.read_csv("final_dataset.csv")
        # Ensure correct mapping for officials
        df['Lat_Fixed'] = df['Location'].map(lambda x: STATE_COORDS.get(x, [20.59, 78.96])[0])
        df['Lon_Fixed'] = df['Location'].map(lambda x: STATE_COORDS.get(x, [20.59, 78.96])[1])
        return df

    df = load_gov_data()
    state = st.selectbox("Select State for Policy Review", sorted(df['Location'].unique()))
    state_df = df[df['Location'] == state]

    # --- 4. DATA-DRIVEN INSIGHTS ---
    st.divider()
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    # Identify dynamic risks
    top_cause = state_df['Causes'].mode()[0] if not state_df.empty else "N/A"
    top_highway = state_df['Highway Type'].mode()[0] if not state_df.empty else "N/A"
    total_incidents = state_df['Count'].sum()

    col_stat1.metric("Critical Root Cause", top_cause)
    col_stat2.metric("Highest Risk Zone", "National Highways" if "National" in top_highway else "State Roads")
    col_stat3.metric("Total State Incidents", total_incidents)

    # --- 5. RISK DNA ANALYSIS ---
    st.subheader("🧬 Regional Risk DNA")
    fig_dna = px.sunburst(
        state_df, 
        path=['Highway Type', 'Causes', 'Weather'], 
        values='Count',
        title=f"Incident Breakdown: {state}",
        color_continuous_scale='RdBu'
    )
    st.plotly_chart(fig_dna, use_container_width=True)

    # --- 6. STRATEGIC ACTION PLAN (AUTO-GENERATED) ---
    st.subheader("📝 Strategic Action Plan (Official Directive)")
    
    plan_col1, plan_col2 = st.columns(2)
    with plan_col1:
        st.markdown(f"**🛡️ Enforcement Priorities for {state}:**")
        st.write(f"1. **Primary Focus:** Immediate crackdown on **{top_cause}**.")
        st.write(f"2. **Checkpoints:** Deploy units on **{top_highway}** during Night hours.")
        st.write(f"3. **Technology:** Install AI-CCTV for automated violation detection.")
        
    with plan_col2:
        st.markdown(f"**🏗️ Infrastructure Directives:**")
        st.write(f"1. **Redesign:** Modify merging lanes on **{top_highway}**.")
        st.write(f"2. **Safety Tech:** Install smart lighting for Foggy/Night conditions.")
        st.write(f"3. **Budget:** Prioritize 40% of state road fund to {top_cause} prevention.")

    # --- 7. DEPLOYMENT MAP ---
    st.divider()
    st.subheader("📍 Enforcement Deployment Zones")
    center = STATE_COORDS.get(state, [20.59, 78.96])
    fig_map = px.density_mapbox(
        state_df, lat='Lat_Fixed', lon='Lon_Fixed', z='Count', radius=20,
        center={"lat": center[0], "lon": center[1]}, zoom=6,
        mapbox_style="carto-darkmatter", title="Concentration of Fatalities"
    )
    st.plotly_chart(fig_map, use_container_width=True)