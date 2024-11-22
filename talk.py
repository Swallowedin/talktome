import streamlit as st
import openai
import json
import logging
import os
from logging.handlers import RotatingFileHandler

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=5)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Configuration de la page Streamlit
st.set_page_config(page_title="Assistant VIEW Avocats", layout="wide")

# Style personnalisé
st.markdown("""
<style>
    .stApp {
        background-color: transparent;
    }
    .main {
        background-color: white;
    }
    .stTextInput > div > div > input {
        background-color: white;
    }
    .stButton > button {
        background-color: #1D4E44;
        color: white;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #f0f2f6;
    }
    .assistant-message {
        background-color: #e5f5f1;
    }
</style>
""", unsafe_allow_html=True)

# Configuration OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_openai_response(message: str) -> dict:
    """Obtient une réponse d'OpenAI"""
    try:
        logger.info(f"Message envoyé à OpenAI: {message}")
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Vous êtes l'assistant virtuel du cabinet VIEW Avocats. Répondez de manière professionnelle et concise."
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
        logger.error(f"Erreur lors de l'appel à OpenAI : {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def init_session_state():
    """Initialise les variables de session"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

def display_chat_history():
    """Affiche l'historique des messages"""
    for message in st.session_state.messages:
        with st.container():
            st.markdown(
                f"""<div class="chat-message {'user-message' if message['role'] == 'user' else 'assistant-message'}">
                    {message['content']}
                </div>""",
                unsafe_allow_html=True
            )

def main():
    st.title("Assistant VIEW Avocats")
    
    # Initialisation
    init_session_state()
    
    # Zone de saisie du message
    user_input = st.text_input("Votre message:", key="user_input")
    
    # Traitement du message
    if st.button("Envoyer", key="send_button"):
        if user_input:
            # Ajout du message utilisateur
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Obtention de la réponse
            response = get_openai_response(user_input)
            
            if response["status"] == "success":
                st.session_state.messages.append({"role": "assistant", "content": response["response"]})
            else:
                st.error("Désolé, une erreur est survenue lors du traitement de votre demande.")
                logger.error(f"Erreur de réponse: {response.get('message', 'Unknown error')}")
    
    # Affichage de l'historique
    display_chat_history()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Erreur principale: {str(e)}")
        st.error("Une erreur est survenue. Veuillez réessayer plus tard.")
