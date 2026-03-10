import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="Belaire Order Tracking", page_icon="🍾")

st.markdown("""
    <style>
    .status-card { 
        padding: 25px; border-radius: 12px; background-color: white; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center;
        border-top: 6px solid #305496; margin-top: 20px;
    }
    h2 { color: #305496; }
    </style>
    """, unsafe_allow_html=True)

st.title("🍾 Order Tracking Portal")
st.write("Please enter your **Purchase Order (PO) number** to check the estimated availability date.")

# --- DATA LOADING ---
def load_data():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_info = json.loads(st.secrets["json_key"])
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        sheet = client.open("Belaire_DB_Commandes").sheet1
        return pd.DataFrame(sheet.get_all_records())
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

# --- SEARCH INTERFACE ---
customer_ref_input = st.text_input("Your PO / Reference Number", placeholder="e.g. PO-12345").strip().upper()

if st.button("Check Status"):
    if customer_ref_input:
        with st.spinner("Searching our database..."):
            df = load_data()
            if df is not None and not df.empty:
                # On cherche dans la colonne CUSTOMER_REF (notre nouvelle colonne C)
                df['CUSTOMER_REF'] = df['CUSTOMER_REF'].astype(str).str.strip().str.upper()
                result = df[df['CUSTOMER_REF'] == customer_ref_input]
                
                if not result.empty:
                    info = result.iloc[0]
                    st.markdown(f"""
                    <div class="status-card">
                        <h3>Order Found!</h3>
                        <p><b>Internal ID:</b> {info.get('INTERNAL_ID', 'N/A')}</p>
                        <h2>📅 Estimated Date: {info.get('DISPO_DATE')}</h2>
                        <p style="font-size: 0.85em; color: gray;">Last updated: {info.get('LAST_UPDATE')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning(f"⚠️ Reference '{customer_ref_input}' not found. Please double-check your entry or contact your sales representative.")
            else:
                st.info("The database is currently being updated. Please try again in a few minutes.")
    else:
        st.info("Please enter a reference number.")

st.markdown("---")
st.caption("Belaire Production & Logistics - Real-time tracking")
