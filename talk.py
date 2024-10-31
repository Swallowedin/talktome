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

# Style CSS mis à jour avec la couleur verte et la flèche
st.markdown("""
<style>
    /* Reset Streamlit */
    .main > div:first-child {padding: 0 !important;}
    header {display: none !important;}
    .block-container {padding: 0 !important; max-width: 100% !important;}
    [data-testid="stToolbar"] {display: none !important;}
    .stDeployButton {display: none !important;}
    footer {display: none !important;}
    .st-emotion-cache-1v0mbdj {width: auto !important;}
    
    /* Widget Container */
    .chat-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 380px;
        height: 600px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.1);
        border-radius: 10px;
        overflow: hidden;
        background: white;
        display: flex;
        flex-direction: column;
    }

    /* Chat Header */
    .chat-header {
        background: #22c55e;
        color: white;
        padding: 15px 20px;
        font-size: 16px;
        font-weight: 500;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Messages Area */
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        display: flex;
        flex-direction: column;
        gap: 10px;
        background: #f8fafc;
    }

    .message {
        max-width: 85%;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 4px 0;
    }

    .user-message {
        background: #22c55e;
        color: white;
        align-self: flex-end;
        border-bottom-right-radius: 5px;
    }

    .assistant-message {
        background: white;
        color: #1a1a1a;
        align-self: flex-start;
        border-bottom-left-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* Input Area */
    .chat-input {
        padding: 15px;
        background: white;
        border-top: 1px solid #e2e8f0;
        display: flex;
        gap: 10px;
    }

    /* Streamlit Elements Styling */
    .stTextInput > div > div > input {
        border: 1px solid #e2e8f0 !important;
        border-radius: 5px !important;
        padding: 10px !important;
        font-size: 14px !important;
        background: white !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #22c55e !important;
        box-shadow: 0 0 0 1px #22c55e !important;
    }

    .stButton > button {
        background-color: #22c55e !important;
        padding: 10px 20px !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        cursor: pointer !important;
        transition: background-color 0.2s !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 42px !important;
    }

    .stButton > button:hover {
        background-color: #16a34a !important;
    }

    .stButton > button:after {
        content: '➤';
        margin-left: 5px;
        font-size: 14px;
    }

    @media (max-width: 480px) {
        .chat-container {
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

# Initialisation des messages
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
    # Container du chat
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # Header
    st.markdown('''
        <div class="chat-header">
            <span>Assistant VIEW Avocats</span>
            <span class="toggle-btn">▼</span>
        </div>
    ''', unsafe_allow_html=True)

    # Messages
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        message_class = "user-message" if message["role"] == "user" else "assistant-message"
        st.markdown(f'<div class="message {message_class}">{message["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Zone de saisie
    st.markdown('<div class="chat-input">', unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input("", placeholder="Posez votre question ici...", key="user_input", label_visibility="collapsed")
    
    with col2:
        send_button = st.button("Envoi")

    st.markdown('</div></div>', unsafe_allow_html=True)

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
