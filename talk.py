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

# Style CSS pour reproduire exactement le widget
st.markdown("""
<style>
    /* Masquer les éléments Streamlit */
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
    .st-emotion-cache-1v0mbdj {width: auto !important;}
    
    /* Style du widget */
    .chat-widget {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 380px;
        height: 600px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.1);
        display: flex;
        flex-direction: column;
        z-index: 9999;
    }

    .chat-header {
        padding: 15px 20px;
        background: #1a365d;
        color: white;
        border-radius: 10px 10px 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        display: flex;
        flex-direction: column;
        gap: 10px;
        height: calc(100% - 130px);
    }

    .user-message {
        background: #1a365d;
        color: white;
        padding: 10px 15px;
        border-radius: 15px;
        border-bottom-right-radius: 5px;
        margin: 5px 0;
        align-self: flex-end;
        max-width: 85%;
    }

    .assistant-message {
        background: #f1f5f9;
        color: #1a365d;
        padding: 10px 15px;
        border-radius: 15px;
        border-bottom-left-radius: 5px;
        margin: 5px 0;
        align-self: flex-start;
        max-width: 85%;
    }

    .chat-input-container {
        padding: 15px;
        border-top: 1px solid #e2e8f0;
        background: white;
        border-radius: 0 0 10px 10px;
    }

    .chat-input {
        display: flex;
        gap: 10px;
    }

    /* Style des éléments Streamlit pour matcher le widget */
    .stTextInput > div > div > input {
        border: 1px solid #e2e8f0 !important;
        border-radius: 5px !important;
        padding: 10px !important;
        font-size: 14px !important;
    }

    .stButton > button {
        background-color: #1a365d !important;
        color: white !important;
        border: none !important;
        padding: 8px 20px !important;
        border-radius: 5px !important;
        cursor: pointer !important;
        transition: background-color 0.2s !important;
    }

    .stButton > button:hover {
        background-color: #2c5282 !important;
    }

    @media (max-width: 480px) {
        .chat-widget {
            width: 100%;
            height: 100vh;
            bottom: 0;
            right: 0;
            border-radius: 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Configuration OpenAI
if 'OPENAI_API_KEY' not in st.secrets:
    logger.error('⚠️ OPENAI_API_KEY non configurée')
    st.error('⚠️ OPENAI_API_KEY non configurée')
    st.stop()

openai.api_key = st.secrets['OPENAI_API_KEY']

# Initialisation de la session state
if "messages" not in st.session_state:
    st.session_state.messages = []

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

def main():
    # Structure du widget
    st.markdown('<div class="chat-widget">', unsafe_allow_html=True)
    
    # En-tête
    st.markdown('''
        <div class="chat-header">
            <span>Assistant VIEW Avocats</span>
        </div>
    ''', unsafe_allow_html=True)
    
    # Zone des messages
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Zone de saisie
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    st.markdown('<div class="chat-input">', unsafe_allow_html=True)
    
    # Utiliser les colonnes pour la mise en page
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("", placeholder="Posez votre question ici...", key="user_input", label_visibility="collapsed")
    with col2:
        send_button = st.button("Envoyer")
    
    st.markdown('</div></div></div>', unsafe_allow_html=True)
    
    # Traitement du message
    if user_input and send_button:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        response = get_openai_response(user_input)
        if response["status"] == "success":
            st.session_state.messages.append({"role": "assistant", "content": response["response"]})
        else:
            st.error("Une erreur est survenue. Veuillez réessayer.")
        
        # Vider le champ de saisie
        st.session_state.user_input = ""
        
        st.rerun()

if __name__ == "__main__":
    main()
