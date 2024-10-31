import streamlit as st
import openai
import logging
from logging.handlers import RotatingFileHandler
import time

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
    layout="centered",  # Changé pour un meilleur centrage
    initial_sidebar_state="collapsed"
)

# Configuration OpenAI
if 'OPENAI_API_KEY' not in st.secrets:
    logger.error('⚠️ OPENAI_API_KEY non configurée')
    st.error('⚠️ OPENAI_API_KEY non configurée')
    st.stop()

openai.api_key = st.secrets['OPENAI_API_KEY']

# CSS pour le style du widget
st.markdown("""
<style>
    /* Reset Streamlit */
    .stDeployButton, footer, header, [data-testid="stToolbar"] {display: none !important;}
    section[data-testid="stSidebar"] {display: none !important;}
    .main > div:first-child {padding-top: 0 !important;}
    
    /* Messages */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .stMarkdown {
        min-height: 0 !important;
    }
    
    /* Chat container */
    .st-emotion-cache-1v0mbdj > div:first-child {
        margin-top: -100px;  /* Ajuster pour enlever l'espace en haut */
    }
    
    /* Styliser les messages */
    .user-message {
        background-color: #22c55e;
        color: white;
        padding: 10px 15px;
        border-radius: 15px;
        border-bottom-right-radius: 5px;
        margin: 5px 0;
        margin-left: 20%;
        max-width: 80%;
        float: right;
        clear: both;
    }
    
    .assistant-message {
        background-color: white;
        color: #1a1a1a;
        padding: 10px 15px;
        border-radius: 15px;
        border-bottom-left-radius: 5px;
        margin: 5px 0;
        margin-right: 20%;
        max-width: 80%;
        float: left;
        clear: both;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Styliser l'input et le bouton */
    .stTextInput input {
        border: 1px solid #e2e8f0;
        padding: 10px;
        border-radius: 5px;
        width: calc(100% - 20px);
    }
    
    .stButton button {
        background-color: #22c55e !important;
        color: white !important;
        border: none !important;
        padding: 10px 15px !important;
        border-radius: 5px !important;
    }
    
    .stButton button::after {
        content: " ➤";
    }
    
    /* Container personnalisé */
    .chat-container {
        max-width: 380px !important;
        margin: 0 auto;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    
    .chat-header {
        background: #22c55e;
        color: white;
        padding: 15px 20px;
        font-weight: 500;
    }
    
    .messages-container {
        height: 450px;
        overflow-y: auto;
        padding: 20px;
        background: #f8fafc;
    }
    
    .input-container {
        padding: 15px;
        background: white;
        border-top: 1px solid #e2e8f0;
    }
    
    /* Masquer le texte d'entrée par défaut */
    .stTextInput div div::before {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

def get_openai_response(message: str):
    """Obtenir une réponse d'OpenAI"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Vous êtes l'assistant virtuel du cabinet VIEW Avocats."},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Erreur OpenAI: {str(e)}")
        return "Désolé, je n'ai pas pu traiter votre demande. Veuillez réessayer."

def main():
    # Initialiser l'historique des messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Structure du widget
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # En-tête
    st.markdown('<div class="chat-header">Assistant VIEW Avocats</div>', unsafe_allow_html=True)
    
    # Zone des messages
    st.markdown('<div class="messages-container">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        st.markdown(
            f'<div class="{message["role"]}-message">{message["content"]}</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Zone de saisie
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    cols = st.columns([4, 1])
    with cols[0]:
        user_input = st.text_input("", placeholder="Posez votre question ici...", label_visibility="collapsed")
    with cols[1]:
        send_button = st.button("Envoi")
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Traitement du message
    if user_input and send_button:
        # Ajouter le message de l'utilisateur
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Obtenir et ajouter la réponse
        response = get_openai_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Recharger la page pour afficher les nouveaux messages
        st.rerun()

if __name__ == "__main__":
    main()
