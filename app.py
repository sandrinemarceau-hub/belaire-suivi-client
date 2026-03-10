import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="Suivi de Commande Belaire", page_icon="🍾")

st.markdown("""
    <style>
    .status-card { 
        padding: 20px; border-radius: 10px; background-color: white; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;
        border-top: 5px solid #305496; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🍾 Suivi de votre Commande")
st.write("Entrez votre numéro de commande pour connaître la date de disponibilité.")

# --- CONNEXION SANS CACHE (Pour avoir toujours la date réelle) ---
def load_data_fresh():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_info = json.loads(st.secrets["json_key"])
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        sheet = client.open("Belaire_DB_Commandes").sheet1
        # On force la lecture complète sans mise en mémoire
        return pd.DataFrame(sheet.get_all_records())
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None

# --- INTERFACE ---
num_cde_input = st.text_input("Référence de Commande (ex: CA291707)", "").strip()

if st.button("Vérifier la disponibilité"):
    if num_cde_input:
        with st.spinner("Vérification en temps réel..."):
            df = load_data_fresh()
            if df is not None:
                # RECHERCHE EXACTE (pour éviter de confondre deux numéros proches)
                # On nettoie les espaces pour être sûr
                df['NUM_CDE'] = df['NUM_CDE'].astype(str).str.strip()
                result = df[df['NUM_CDE'] == num_cde_input]
                
                if not result.empty:
                    info = result.iloc[0]
                    st.markdown(f"""
                    <div class="status-card">
                        <h3>Commande Identifiée</h3>
                        <p><b>Client :</b> {info.get('CLIENT', 'N/A')}</p>
                        <h2 style="color: #305496;">📅 Disponibilité : {info.get('DATE_DISPO')}</h2>
                        <p style="font-size: 0.8em; color: gray;">Actualisé le : {info.get('DERNIERE_MAJ')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning(f"⚠️ Le numéro '{num_cde_input}' n'est pas encore dans la base. Veuillez patienter ou vérifier la saisie.")
    else:
        st.info("Veuillez saisir un numéro de commande.")
