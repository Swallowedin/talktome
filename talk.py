import streamlit as st
import openai
import logging
from logging.handlers import RotatingFileHandler
import time
from typing import Dict, Any

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=5)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Configuration de la page
st.set_page_config(
    page_title="Assistant VIEW Avocats",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

# Initialisation de la session state
if "openai_initialized" not in st.session_state:
    if 'OPENAI_API_KEY' not in st.secrets:
        logger.error('⚠️ OPENAI_API_KEY non configurée')
        st.error('⚠️ OPENAI_API_KEY non configurée')
        st.stop()
    openai.api_key = st.secrets['OPENAI_API_KEY']
    st.session_state.openai_initialized = True
    st.session_state.messages = []
    st.session_state.last_request_time = 0
    st.session_state.processing = False

def get_openai_response(message: str) -> Dict[str, Any]:
    """Fonction pour obtenir une réponse d'OpenAI avec gestion des erreurs et du rate limiting"""
    try:
        # Vérifier le rate limiting
        current_time = time.time()
        time_since_last_request = current_time - st.session_state.last_request_time
        if time_since_last_request < 1:  # Attendre au moins 1 seconde entre les requêtes
            time.sleep(1 - time_since_last_request)

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
        
        st.session_state.last_request_time = time.time()
        logger.info("Réponse reçue de OpenAI")
        
        return {
            "status": "success",
            "response": response.choices[0].message.content
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à OpenAI : {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def handle_api_request():
    """Gestion des requêtes API"""
    params = st.experimental_get_query_params()
    if "api" in params and params["api"][0] == "true" and "message" in params:
        message = params["message"][0]
        response = get_openai_response(message)
        st.json(response)
        return True
    return False

def main():
    # Vérifier si c'est une requête API
    if handle_api_request():
        return

    # Interface utilisateur normale
    st.header("Assistant VIEW Avocats")

    # Afficher l'historique des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Zone de saisie
    if prompt := st.chat_input("Comment puis-je vous aider ?"):
        if not st.session_state.processing:
            st.session_state.processing = True
            
            # Afficher le message de l'utilisateur immédiatement
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Obtenir et afficher la réponse
            with st.chat_message("assistant"):
                response = get_openai_response(prompt)
                if response["status"] == "success":
                    st.markdown(response["response"])
                    st.session_state.messages.append({"role": "assistant", "content": response["response"]})
                else:
                    st.error(f"Erreur: {response.get('message', 'Une erreur est survenue')}")
            
            st.session_state.processing = False
            st.experimental_rerun()

if __name__ == "__main__":
    main()
