import streamlit as st
import openai
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime, timedelta

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

# Configuration des en-têtes de sécurité
def set_security_headers():
    headers = {
        'Access-Control-Allow-Origin': 'https://view-avocats.fr',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Credentials': 'true',
        'X-Frame-Options': 'ALLOW-FROM https://view-avocats.fr',
        'Content-Security-Policy': "frame-ancestors 'self' https://view-avocats.fr"
    }
    
    for key, value in headers.items():
        st.markdown(f"<meta http-equiv='{key}' content='{value}'>", unsafe_allow_html=True)

# Initialisation de l'état de session
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.messages = []
    st.session_state.authenticated = False

# Configuration OpenAI
if 'OPENAI_API_KEY' not in st.secrets:
    logger.error('⚠️ OPENAI_API_KEY non configurée')
    st.error('⚠️ OPENAI_API_KEY non configurée')
    st.stop()

openai.api_key = st.secrets['OPENAI_API_KEY']

def get_openai_response(message: str) -> str:
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
        logger.info("Réponse reçue de OpenAI")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à OpenAI : {str(e)}")
        return f"Désolé, une erreur est survenue : {str(e)}"

def authenticate():
    # Vérification de l'origine
    params = st.experimental_get_query_params()
    origin = params.get('origin', [''])[0]
    
    if origin == 'https://view-avocats.fr':
        st.session_state.authenticated = True
        return True
    
    logger.warning(f"Tentative d'accès non autorisée depuis : {origin}")
    return False

def handle_api_request(message: str):
    if not st.session_state.authenticated:
        if not authenticate():
            return {"status": "error", "message": "Non autorisé"}
    
    try:
        response = get_openai_response(message)
        return {"status": "success", "response": response}
    except Exception as e:
        logger.error(f"Erreur API: {str(e)}")
        return {"status": "error", "message": str(e)}

def main():
    # Appliquer les en-têtes de sécurité
    set_security_headers()
    
    # Vérifier s'il s'agit d'une requête API
    params = st.experimental_get_query_params()
    if 'message' in params:
        message = params['message'][0]
        response = handle_api_request(message)
        st.json(response)
        return
    
    # Interface utilisateur normale
    st.title("Assistant VIEW Avocats")
    
    # Afficher l'historique des messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(
                f'<div style="background-color: #22c55e; color: white; padding: 10px; border-radius: 15px; margin: 5px 0; text-align: right;">{message["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div style="background-color: white; color: black; padding: 10px; border-radius: 15px; margin: 5px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">{message["content"]}</div>',
                unsafe_allow_html=True
            )

    # Input utilisateur
    if prompt := st.chat_input("Posez votre question ici..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = get_openai_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

if __name__ == "__main__":
    main()
