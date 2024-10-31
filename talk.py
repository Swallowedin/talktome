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

# Style personnalisé pour ressembler au widget original
st.markdown("""
<style>
    /* Cacher les éléments Streamlit par défaut */
    header {display: none !important;}
    footer {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    .stDeployButton {display: none !important;}
    
    /* Style pour le chat */
    .stTextInput input {
        border: 1px solid #e2e8f0 !important;
        padding: 10px !important;
        border-radius: 5px !important;
    }
    
    .stButton > button {
        background-color: #22c55e !important;
        color: white !important;
        padding: 10px 20px !important;
        border-radius: 5px !important;
    }
    
    .stButton > button:hover {
        background-color: #16a34a !important;
    }
    
    /* Style des messages */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 0 !important;
    }
    
    .user-message {
        background-color: #22c55e;
        color: white;
        padding: 10px 15px;
        border-radius: 15px;
        border-bottom-right-radius: 5px;
        margin: 5px 0;
        max-width: 85%;
        float: right;
    }
    
    .assistant-message {
        background-color: white;
        color: #1a1a1a;
        padding: 10px 15px;
        border-radius: 15px;
        border-bottom-left-radius: 5px;
        margin: 5px 0;
        max-width: 85%;
        float: left;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Configuration OpenAI
if 'OPENAI_API_KEY' not in st.secrets:
    logger.error('⚠️ OPENAI_API_KEY non configurée')
    st.error('⚠️ OPENAI_API_KEY non configurée')
    st.stop()

openai.api_key = st.secrets['OPENAI_API_KEY']

# Initialisation de la session state pour l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

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

def main():
    st.title("Assistant VIEW Avocats")
    
    # Afficher l'historique des messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)

    # Input utilisateur
    if prompt := st.chat_input("Posez votre question ici..."):
        # Ajouter le message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Obtenir et afficher la réponse
        response = get_openai_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Rafraîchir pour afficher les nouveaux messages
        st.rerun()

if __name__ == "__main__":
    main()
