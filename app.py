import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="Belaire Order Tracking", page_icon="🍾", layout="centered")

st.markdown("""
    <style>
    .status-card { 
        padding: 25px; border-radius: 12px; background-color: white; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center;
        border-top: 6px solid #305496; margin-top: 20px;
    }
    h2 { color: #305496; }
    .update-banner {
        background-color: #e8f0fe; color: #1a73e8; padding: 10px; 
        border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🍾 Order Tracking Portal")
st.write("Welcome to your dedicated logistics portal.")

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

with st.spinner("Connecting to Belaire Factory..."):
    df = load_data()

if df is not None and not df.empty:
    
    # --- 1. DATE DE DERNIÈRE MISE À JOUR ---
    derniere_maj = df['LAST_UPDATE'].iloc[0] if 'LAST_UPDATE' in df.columns else "Recently"
    st.markdown(f"<div class='update-banner'>🔄 Data last synchronized by the factory on: {derniere_maj}</div>", unsafe_allow_html=True)
    
    # Nettoyage de la colonne des PO
    df['CUSTOMER_REF'] = df['CUSTOMER_REF'].astype(str).str.strip().str.upper()
    
    # Création de la liste des PO (en enlevant les cases vides s'il y en a)
    liste_po = [po for po in df['CUSTOMER_REF'].unique() if po != "" and po != "NAN"]
    liste_po.sort() # On trie par ordre alphabétique

    st.markdown("### 🔍 Check a specific order")
    
    # --- 2. MENU DÉROULANT ---
    po_selectionne = st.selectbox(
        "Select your Purchase Order (PO):", 
        options=["-- Please select a PO --"] + liste_po
    )

    if po_selectionne != "-- Please select a PO --":
        result = df[df['CUSTOMER_REF'] == po_selectionne]
        info = result.iloc[0]
        
        st.markdown(f"""
        <div class="status-card">
            <h3>Order Found!</h3>
            <p><b>Internal ID:</b> {info.get('INTERNAL_ID', 'N/A')}</p>
            <h2>📅 Estimated Date: {info.get('DISPO_DATE')}</h2>
            <p style="font-size: 0.85em; color: gray;">Includes standard security margin</p>
        </div>
        """, unsafe_allow_html=True)
    
    # --- 3. BOUTON TÉLÉCHARGEMENT EXCEL COMPLET ---
    st.markdown("---")
    st.markdown("### 📥 Download your Full Order Book")
    st.write("Get a complete summary of all your ongoing orders in one click.")
    
    # On prépare un bel Excel en mémoire
    output = io.BytesIO()
    # On sélectionne les colonnes intéressantes pour le client
    colonnes_export = ['CUSTOMER_REF', 'INTERNAL_ID', 'DISPO_DATE']
    df_export = df[colonnes_export].copy()
    df_export.rename(columns={'CUSTOMER_REF': 'PO Number', 'INTERNAL_ID': 'Belaire Ref', 'DISPO_DATE': 'Estimated Availability'}, inplace=True)
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_export.to_excel(writer, index=False, sheet_name='Ongoing Orders')
        # Ajuster la largeur des colonnes
        worksheet = writer.sheets['Ongoing Orders']
        worksheet.set_column('A:C', 25)
    
    st.download_button(
        label="📄 Download Excel Report",
        data=output.getvalue(),
        file_name="Belaire_Order_Book.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("The database is currently empty or updating. Please try again later.")
