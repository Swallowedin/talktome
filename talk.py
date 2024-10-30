import streamlit as st
import openai
import json
from streamlit.web import WebRequestInfo

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

# Configuration CORS
st.markdown("""
<head>
    <meta http-equiv="Access-Control-Allow-Origin" content="https://view-avocats.fr">
    <meta http-equiv="Access-Control-Allow-Methods" content="GET, POST, OPTIONS">
    <meta http-equiv="Access-Control-Allow-Headers" content="Content-Type">
</head>
""", unsafe_allow_html=True)

# Vérification de la clé API OpenAI
if 'OPENAI_API_KEY' not in st.secrets:
    st.error('⚠️ OPENAI_API_KEY non configurée')
    st.stop()

openai.api_key = st.secrets['OPENAI_API_KEY']

def get_openai_response(message: str) -> dict:
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Ne pas changer le modèle
            messages=[
                {
                    "role": "system",
                    "content": """Vous êtes l'assistant virtuel du cabinet VIEW Avocats. 
                    Répondez de manière professionnelle et précise aux questions des utilisateurs."""
                },
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return {
            "status": "success",
            "response": response.choices[0].message.content
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def handle_cors():
    # Ajouter les headers CORS
    for header in [
        ('Access-Control-Allow-Origin', 'https://view-avocats.fr'),
        ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
        ('Access-Control-Allow-Headers', 'Content-Type'),
    ]:
        st.response.headers[header[0]] = header[1]

def main():
    # Gérer les headers CORS pour toutes les requêtes
    handle_cors()

    # Gérer les messages de chat
    params = st.query_params
    if "message" in params:
        message = params["message"]
        response = get_openai_response(message)
        st.json(response)
        return

    # Page par défaut
    st.write("Assistant VIEW Avocats")

if __name__ == "__main__":
    main()
