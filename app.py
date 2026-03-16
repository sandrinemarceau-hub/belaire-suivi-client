import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

st.set_page_config(page_title="Mon Espace Belaire", layout="wide")
st.title("🥂 Suivi de vos Commandes Belaire")

def charger_suivi_pro():
    # Connexion au Google Sheet de suivi via le compte de service
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    info_cle = json.loads(st.secrets["gcp_service_account"])
    creds = service_account.Credentials.from_service_account_info(info_cle, scopes=scope)
    client = gspread.authorize(creds)
    
    # Ouvrir ton fichier de suivi
    sheet = client.open("NOM_DE_TON_GOOGLE_SHEET").sheet1
    return pd.DataFrame(sheet.get_all_records())

try:
    df = charger_suivi_pro()
    
    # Affichage propre avec boutons de téléchargement
    st.dataframe(
        df,
        column_config={
            "Lien_PL": st.column_config.LinkColumn("📥 Packing List", display_text="Télécharger"),
            "Lien_RDV": st.column_config.LinkColumn("🚚 RDV Transport", display_text="Voir RDV")
        },
        hide_index=True
    )
except:
    st.info("Aucune commande en cours pour le moment.")
