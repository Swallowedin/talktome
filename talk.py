import streamlit as st
import openai
import json
import logging
from logging.handlers import RotatingFileHandler

# Configuration de la page
st.set_page_config(
    page_title="Assistant VIEW Avocats",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajout d'un handler pour écrire dans un fichier
file_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=5)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Masquer les éléments Streamlit par défaut
st.markdown("""
<style>
    #root > div:first-child {
        background-color: transparent;
    }
    .main > div:first-child {
        padding: 0rem 0rem;
    }
    header {display: none !important;}
    .block-container {padding: 0 !important;}
    [data-testid="stToolbar"] {display: none !important;}
    .stDeployButton {display: none !important;}
    footer {display: none !important;}
</style>
""", unsafe_allow_html=True)

# Vérification de la clé API OpenAI
if 'OPENAI_API_KEY' not in st.secrets:
    logger.error('⚠️ OPENAI_API_KEY non configurée')
    st.error('⚠️ OPENAI_API_KEY non configurée')
    st.stop()

openai.api_key = st.secrets['OPENAI_API_KEY']

def get_openai_response(message: str) -> dict:
    try:
        logger.info(f"Message envoyé à OpenAI: {message}")
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Vous êtes l'assistant virtuel du cabinet VIEW Avocats."},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        logger.info("Réponse reçue de OpenAI.")
        logger.debug(f"Réponse brute : {response}")
        return {
            "status": "success",
            "response": response['choices'][0]['message']['content']
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à OpenAI : {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def main():
    # Gérer les messages de chat
    params = st.query_params
    if "message" in params:
        message = params["message"]
        logger.info(f"Message reçu du paramètre : {message}")
        response = get_openai_response(message)
        st.json(response)  # Afficher la réponse sous format JSON
        return

    # Page par défaut
    st.write("Assistant VIEW Avocats")
    logger.info("Affichage de la page d'accueil.")

if __name__ == "__main__":
    main()
