import streamlit as st
import openai
import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

# Configuration CORS pour Streamlit
st.markdown("""
<head>
    <meta http-equiv="Access-Control-Allow-Origin" content="*">
    <meta http-equiv="Access-Control-Allow-Methods" content="GET, POST, OPTIONS">
    <meta http-equiv="Access-Control-Allow-Headers" content="Content-Type">
</head>
""", unsafe_allow_html=True)

# Masquer les éléments Streamlit
st.markdown("""
<style>
    header {display: none !important;}
    footer {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

# Configuration OpenAI
if 'OPENAI_API_KEY' not in st.secrets:
    logger.error('⚠️ OPENAI_API_KEY non configurée')
    st.error('⚠️ OPENAI_API_KEY non configurée')
    st.stop()

openai.api_key = st.secrets['OPENAI_API_KEY']

# Création de l'application FastAPI pour gérer les CORS
app = FastAPI()

# Configuration CORS pour FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://view-avocats.fr"],  # Remplace par ton domaine
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.options("/{path:path}")
async def options_handler():
    return JSONResponse(
        content="OK",
        headers={
            "Access-Control-Allow-Origin": "https://view-avocats.fr",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )

def main():
    # Vérifier si c'est une requête API
    params = st.query_params
    if "message" in params:
        message = params.get("message")
        response = get_openai_response(message)
        
        # Ajouter les headers CORS à la réponse
        st.write("")  # Nécessaire pour ajouter les headers
        st.markdown("""
            <script>
                const headers = document.getElementsByTagName('head')[0];
                headers.innerHTML += `
                    <meta http-equiv="Access-Control-Allow-Origin" content="https://view-avocats.fr">
                    <meta http-equiv="Access-Control-Allow-Methods" content="GET, POST, OPTIONS">
                    <meta http-equiv="Access-Control-Allow-Headers" content="Content-Type">
                `;
            </script>
        """, unsafe_allow_html=True)
        
        st.json(response)
        return
    
    # Page par défaut simple
    st.write("Assistant VIEW Avocats API")

if __name__ == "__main__":
    main()
