import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Suivi de Commande Belaire", page_icon="🍾")

# --- STYLE PERSONNALISÉ (Optionnel pour faire "Pro") ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; background-color: #305496; color: white; }
    .status-card { 
        padding: 20px; 
        border-radius: 10px; 
        background-color: white; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🍾 Suivi de votre Commande")
st.write("Entrez votre numéro de commande pour connaître la date de disponibilité estimée.")

# --- CONNEXION GOOGLE SHEETS ---
def load_data():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        sheet = client.open("Belaire_DB_Commandes").sheet1
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error("Impossible de se connecter à la base de données.")
        return None

# --- INTERFACE DE RECHERCHE ---
num_cde_input = st.text_input("Numéro de Commande", placeholder="Ex: 2026-1234").strip()

if st.button("Vérifier le statut"):
    if num_cde_input:
        df = load_data()
        if df is not None:
            # Recherche du numéro (on nettoie pour éviter les erreurs d'espaces)
            result = df[df['NUM_CDE'].astype(str).str.contains(num_cde_input, na=False)]
            
            if not result.empty:
                info = result.iloc[0]
                st.markdown(f"""
                <div class="status-card">
                    <h3>Commande trouvée !</h3>
                    <p><b>Client :</b> {info['CLIENT']}</p>
                    <h2 style="color: #305496;">📅 Date estimée : {info['DATE_DISPO']}</h2>
                    <p style="font-size: 0.8em; color: gray;">Mise à jour le : {info['DERNIERE_MAJ']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Aucun numéro de commande correspondant trouvé. Veuillez vérifier votre saisie.")
    else:
        st.info("Veuillez entrer un numéro de commande.")

st.markdown("---")
st.caption("Données fournies à titre indicatif selon le planning de production actuel.")
