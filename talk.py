import streamlit as st
import openai
import json
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional, List

# Configuration de la page
st.set_page_config(
    page_title="Assistant VIEW Avocats",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=5)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Styles personnalisés
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
    
    .question-box {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    
    .stTextInput {
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

def load_knowledge_base(file_path: str) -> Optional[str]:
    """Charge le contenu de la base de connaissances depuis un fichier texte"""
    try:
        if not os.path.exists(file_path):
            logger.error(f"Le fichier {file_path} n'existe pas")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la base de connaissances: {str(e)}")
        return None

def get_openai_response(message: str, context: str = "") -> dict:
    """Obtient une réponse d'OpenAI"""
    try:
        logger.info(f"Message envoyé à OpenAI: {message}")
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": "Vous êtes l'assistant virtuel du cabinet VIEW Avocats. " + 
                              "Répondez en vous basant sur les informations fournies dans le contexte."
                },
                {"role": "user", "content": f"{context}\n\nQuestion: {message}"}
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

def display_question_box():
    """Affiche la boîte de questions"""
    with st.container():
        st.markdown('<div class="question-box">', unsafe_allow_html=True)
        
        questions_predefinies = [
            "Quels sont vos domaines d'expertise ?",
            "Comment prendre rendez-vous ?",
            "Quels sont vos tarifs ?",
            "Où se trouve votre cabinet ?"
        ]
        
        selected_question = st.selectbox(
            "Questions fréquentes",
            [""] + questions_predefinies,
            index=0,
            key="preset_questions"
        )
        
        custom_question = st.text_input(
            "Ou posez votre propre question",
            key="custom_question"
        )
        
        if st.button("Envoyer", key="send_button"):
            question = custom_question if custom_question else selected_question
            if question:
                return question
        
        st.markdown('</div>', unsafe_allow_html=True)
        return None

def main():
    st.title("Assistant VIEW Avocats")
    
    # Vérification de la clé API
    if not os.getenv('OPENAI_API_KEY'):
        st.error("La clé API OpenAI n'est pas configurée. Veuillez configurer la variable d'environnement OPENAI_API_KEY.")
        return
    
    # Chargement de la base de connaissances
    knowledge_base_content = load_knowledge_base("knowledge_base.txt")
    if knowledge_base_content is None:
        st.error("Erreur lors du chargement de la base de connaissances")
        return
    
    # Initialisation de l'historique des messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Affichage de la box de questions
    question = display_question_box()
    
    # Traitement de la question
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        
        try:
            # Obtention de la réponse avec le contexte de la base de connaissances
            response = get_openai_response(question, knowledge_base_content)
            
            if response["status"] == "success":
                st.session_state.messages.append({"role": "assistant", "content": response["response"]})
            else:
                st.error("Désolé, une erreur est survenue lors du traitement de votre demande.")
                logger.error(f"Erreur de réponse: {response.get('message', 'Unknown error')}")
        
        except Exception as e:
            st.error("Une erreur est survenue lors du traitement de votre question.")
            logger.error(f"Erreur lors du traitement de la question: {str(e)}")
    
    # Affichage de l'historique des messages
    with st.container():
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

if __name__ == "__main__":
    main()
