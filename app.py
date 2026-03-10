import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="Suivi de Commande Belaire", page_icon="🍾")

# --- STYLE ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .status-card { 
        padding: 20px; 
        border-radius: 10px; 
        background-color: white; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 5px solid #305496;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🍾 Suivi de votre Commande")
st.write("Entrez votre numéro de commande pour connaître la date de disponibilité.")

# --- CONNEXION GOOGLE SHEETS (Version Robuste) ---
def load_data():
    try:
        if "json_key" not in st.secrets:
            st.error("Configuration manquante : json_key introuvable dans les Secrets.")
            return None
            
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        # On utilise la même méthode de lecture que pour l'Usine
        creds_info = json.loads(st.secrets["json_key"])
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # Ouverture du fichier
        sheet = client.open("Belaire_DB_Commandes").sheet1
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Détail technique de l'erreur : {e}")
        return None

# --- INTERFACE ---
num_cde_input = st.text_input("Référence de Commande", placeholder="Ex: 2024-5432").strip()

if st.button("Vérifier la disponibilité"):
    if num_cde_input:
        with st.spinner("Recherche dans la base de données..."):
            df = load_data()
            if df is not None and not df.empty:
                # On cherche la commande (on convertit en texte pour comparer)
                # On utilise 'NUM_CDE' car c'est le titre dans ton Google Sheets
                result = df[df['NUM_CDE'].astype(str).str.contains(num_cde_input, na=False)]
                
                if not result.empty:
                    info = result.iloc[0]
                    st.markdown(f"""
                    <div class="status-card">
                        <h3>Commande Identifiée</h3>
                        <p><b>Client :</b> {info.get('EXPE_NOM_CLIENT', 'Non renseigné')}</p>
                        <h2 style="color: #305496;">📅 Disponibilité : {info.get('DATE_DISPO_ESTIMEE', 'En cours d\'analyse')}</h2>
                        <p style="font-size: 0.8em; color: gray;">Dernière mise à jour : {info.get('DERNIERE_MAJ', 'Récemment')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Numéro de commande introuvable. Veuillez vérifier votre saisie ou contacter votre commercial.")
            elif df is not None and df.empty:
                st.info("La base de données est actuellement vide. L'Usine doit effectuer une première synchronisation.")
    else:
        st.info("Veuillez saisir un numéro.")

st.markdown("---")
st.caption("Belaire Production Portal - Accès sécurisé")
