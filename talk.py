# api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = FastAPI()

# Configuration CORS plus restrictive et sécurisée
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://view-avocats.fr"],  # Votre domaine
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],  # Ajout de OPTIONS pour le preflight
    allow_headers=["*"],
)

# Modèle Pydantic pour la validation des données
class ChatMessage(BaseModel):
    message: str

# Configuration OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/chat")
async def chat(chat_message: ChatMessage):
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Maintien du modèle spécifié
            messages=[
                {"role": "system", "content": "Vous êtes l'assistant virtuel du cabinet VIEW Avocats."},
                {"role": "user", "content": chat_message.message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return {"status": "success", "response": response.choices[0].message.content}
    except Exception as e:
        logger.error(f"Erreur OpenAI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# talk.py
import streamlit as st
import openai
import logging
from logging.handlers import RotatingFileHandler
import requests
from typing import Dict, Any

# Configuration du logging
def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    file_handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=5)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()

def get_chat_response(message: str) -> Dict[str, Any]:
    try:
        # Utiliser l'URL de votre application Streamlit
        api_url = "https://talktomeview.streamlit.app/chat"
        
        # Ajout des headers CORS nécessaires
        headers = {
            "Content-Type": "application/json",
            "Origin": "https://view-avocats.fr"
        }
        
        response = requests.post(
            api_url,
            json={"message": message},
            headers=headers
        )
        
        if response.status_code == 303:
            logger.warning("Redirection 303 détectée")
            # Suivre la redirection manuellement si nécessaire
            response = requests.post(
                response.headers['Location'],
                json={"message": message},
                headers=headers
            )
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de l'appel API: {str(e)}")
        return {"status": "error", "message": f"Erreur de communication: {str(e)}"}

def main():
    # Configuration de la page
    st.set_page_config(
        page_title="Assistant VIEW Avocats",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Masquer les éléments Streamlit par défaut
    hide_streamlit_style = """
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
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # Gérer les messages de chat via les paramètres d'URL
    params = st.experimental_get_query_params()
    if "message" in params:
        message = params["message"][0]  # Prendre le premier message s'il y en a plusieurs
        logger.info(f"Message reçu du paramètre : {message}")
        response = get_chat_response(message)
        st.json(response)
        return

    # Page par défaut si pas de message dans les paramètres
    st.write("Assistant VIEW Avocats")
    logger.info("Affichage de la page d'accueil.")

if __name__ == "__main__":
    main()
