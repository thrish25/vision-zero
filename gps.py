import streamlit as st
import pandas as pd
import numpy as np
from streamlit_js_eval import get_geolocation
from datetime import datetime

# --- 1. GEOGRAPHY ENGINE ---
# We use the Haversine formula to find distance between two GPS points
def haversine_distance(lat1, lon1, lat2, lon2):
    r = 6371 # Earth radius in kilometers
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    
    a = np.sin(delta_phi / 2)**2 + \
        np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2)**2
    res = r * (2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a)))
    return res

# --- 2. DATA ENGINE ---
@st.cache_data
def load_data():
    df = pd.read_csv("final_dataset.csv")
    # Using the fixed coordinates we established earlier
    return df

st.set_page_config(page_title="Vision Zero: Live Guardian", layout="centered")

# --- 3. LIVE GPS TRACKER ---
st.title("🛡️ Vision Zero: Live Guardian")
st.markdown("### Real-Time Hazard Detection System")

# This component asks the user for browser location permission
location = get_geolocation()

if location:
    curr_lat = location['coords']['latitude']
    curr_lon = location['coords']['longitude']
    
    st.success(f"📍 Signal Locked: {curr_lat:.4f}, {curr_lon:.4f}")
    
    # Load hazard data
    df = load_data()
    
    # Calculate distance from user to EVERY accident point in the dataset
    # We create a 'Distance' column in kilometers
    df['dist_to_user'] = df.apply(lambda row: haversine_distance(curr_lat, curr_lon, row['Latitude'], row['Longitude']), axis=1)
    
    # Filter for "Hazard Tangents" (hotspots within 5km)
    nearby_hazards = df[df['dist_to_user'] < 5.0].sort_values(by='dist_to_user')

    # --- 4. POP-UP NOTIFICATION LOGIC ---
    if not nearby_hazards.empty:
        # Get the closest one
        closest = nearby_hazards.iloc[0]
        hazard_dist = round(closest['dist_to_user'], 2)
        
        # TRIGGER THE ALERT
        st.error(f"🚨 HAZARD DETECTED: {hazard_dist} km away!")
        st.toast(f"⚠️ Warning: High Accident Zone Ahead ({closest['Causes']})", icon="🚨")
        
        # Display specific warning details
        st.warning(f"""
        **LIVE ALERT DETAILS:**
        * **Tangent Point:** {closest['Location']} - {closest['Highway Type']}
        * **Primary Risk:** {closest['Causes']}
        * **Historical Density:** {closest['Count']} reported incidents here.
        * **Weather Context:** Hazards increase here during {closest['Weather']} conditions.
        """)
    else:
        st.balloons()
        st.success("✅ Path Clear: No major accident hotspots within 5km.")

else:
    st.info("🛰️ Waiting for GPS Signal... Please allow location access in your browser.")
    # Simulated Location for Testing (Uncomment to test without live GPS)
    # curr_lat, curr_lon = 28.6139, 77.2090 

# --- 5. VISUAL RADAR ---
st.divider()
st.subheader("📡 Proximity Radar")
if location and not nearby_hazards.empty:
    st.write("The following zones are currently on your trajectory:")
    st.dataframe(nearby_hazards[['Highway Type', 'Causes', 'dist_to_user', 'Severity']].rename(columns={'dist_to_user': 'Distance (km)'}))
else:
    st.caption("Radar range: 5km radius.")