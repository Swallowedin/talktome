import streamlit as st
import openai
import logging
from logging.handlers import RotatingFileHandler

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

# CSS personnalisé
st.markdown("""
<style>
    /* Masquer les éléments Streamlit par défaut */
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

    /* Style du chat */
    .chat-widget {
        max-width: 800px;
        margin: 0 auto;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.1);
    }

    .chat-header {
        padding: 15px 20px;
        background: #1a365d;
        color: white;
        border-radius: 10px 10px 0 0;
        font-size: 18px;
        font-weight: bold;
    }

    /* Style des messages */
    .user-message {
        background: #1a365d;
        color: white;
        padding: 10px 15px;
        border-radius: 15px;
        border-bottom-right-radius: 5px;
        margin: 5px 0;
        margin-left: 20%;
        margin-right: 10px;
    }

    .assistant-message {
        background: #f1f5f9;
        color: #1a365d;
        padding: 10px 15px;
        border-radius: 15px;
        border-bottom-left-radius: 5px;
        margin: 5px 0;
        margin-right: 20%;
        margin-left: 10px;
    }

    /* Style de la zone de saisie */
    .stTextInput > div > div > input {
        border: 1px solid #e2e8f0;
        border-radius: 5px;
        padding: 10px 15px;
    }

    .stTextInput > div > div > input:focus {
        border-color: #1a365d;
        box-shadow: 0 0 0 1px #1a365d;
    }

    /* Style des boutons */
    .stButton > button {
        background-color: #1a365d;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .stButton > button:hover {
        background-color: #2c5282;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de la session state
if "messages" not in st.session_state:
    if 'OPENAI_API_KEY' not in st.secrets:
        logger.error('⚠️ OPENAI_API_KEY non configurée')
        st.error('⚠️ OPENAI_API_KEY non configurée')
        st.stop()
    openai.api_key = st.secrets['OPENAI_API_KEY']
    st.session_state.messages = []

def get_openai_response(message: str) -> dict:
    """Fonction pour obtenir une réponse d'OpenAI avec gestion des erreurs"""
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

def main():
    # En-tête personnalisé
    st.markdown('<div class="chat-widget">', unsafe_allow_html=True)
    st.markdown('<div class="chat-header">Assistant VIEW Avocats</div>', unsafe_allow_html=True)

    # Zone de messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)

    # Zone de saisie avec colonnes pour l'alignement
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("", placeholder="Posez votre question ici...", key="user_input")
    with col2:
        send_button = st.button("Envoyer")

    st.markdown('</div>', unsafe_allow_html=True)

    # Traitement du message
    if user_input and send_button:
        # Ajouter le message de l'utilisateur
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Obtenir la réponse
        response = get_openai_response(user_input)
        
        if response["status"] == "success":
            st.session_state.messages.append({"role": "assistant", "content": response["response"]})
        else:
            st.error(f"Erreur: {response.get('message', 'Une erreur est survenue')}")
        
        # Recharger la page pour afficher les nouveaux messages
        st.rerun()

if __name__ == "__main__":
    main()
