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

# Styles personnalisés avec header discret
st.markdown("""
<style>
    /* Reset et base */
    #root > div:first-child {
        background-color: transparent;
    }
    .main {
        padding: 0 !important;
    }
    .main > div:first-child {
        padding: 0 !important;
    }
    header {display: none !important;}
    .block-container {padding: 0 !important;}
    [data-testid="stToolbar"] {display: none !important;}
    .stDeployButton {display: none !important;}
    footer {display: none !important;}
    
    /* Style du header discret */
    h1 {
        font-size: 14px !important;
        color: #666666 !important;
        padding: 8px 12px !important;
        margin: 0 !important;
        background-color: #f8f9fa !important;
        border-bottom: 1px solid #e0e0e0 !important;
        font-weight: 500 !important;
        text-align: center !important;
    }
    
    /* Style des conteneurs */
    .element-container {
        margin: 0 !important;
        padding: 3px 0 !important;
    }
    
    /* Style des sélecteurs */
    .stSelectbox > div > div {
        border: 1px solid #e0e0e0 !important;
        border-radius: 5px !important;
        min-height: 36px !important;
        background: white !important;
    }
    
    .stSelectbox [data-testid="stMarkdown"] {
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* Style du champ texte */
    .stTextInput > div > div > input {
        border: 1px solid #e0e0e0 !important;
        border-radius: 5px !important;
        padding: 8px 12px !important;
        height: 36px !important;
        background: white !important;
    }
    
    /* Style du bouton */
    .stButton > button {
        background-color: #1D4E44 !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 6px 12px !important;
        height: 36px !important;
        width: auto !important;
        margin: 5px 0 !important;
        cursor: pointer !important;
    }
    
    .stButton > button:hover {
        background-color: #2a6d5f !important;
    }
    
    /* Style des messages */
    .stChatMessage {
        background-color: white !important;
        border-radius: 5px !important;
        margin: 5px 0 !important;
        padding: 8px 12px !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    /* Style des labels */
    .stSelectbox label, .stTextInput label {
        font-size: 13px !important;
        color: #666 !important;
        padding-bottom: 2px !important;
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
            model="gpt-4o-mini",
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
    """Affiche la zone de questions"""
    questions_predefinies = [
        "Quels sont vos domaines d'expertise ?",
        "Comment prendre rendez-vous ?",
        "Quels sont vos tarifs ?",
        "Où se trouve votre cabinet ?"
    ]
    
    with st.container():
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
        
        return None

def main():
    # Header discret
    st.markdown("<h1>Assistant VIEW Avocats</h1>", unsafe_allow_html=True)
    
    # Vérification de la clé API
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("Clé API OpenAI manquante")
        return
    
    # Chargement de la base de connaissances
    knowledge_base_content = load_knowledge_base("knowledge_base.txt")
    if knowledge_base_content is None:
        logger.error("Erreur base de connaissances")
        return
    
    # Initialisation de l'historique
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Zone de questions
    question = display_question_box()
    
    # Traitement de la question
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        try:
            response = get_openai_response(question, knowledge_base_content)
            if response["status"] == "success":
                st.session_state.messages.append({"role": "assistant", "content": response["response"]})
            else:
                logger.error(f"Erreur de réponse: {response.get('message', 'Unknown error')}")
        except Exception as e:
            logger.error(f"Erreur de traitement: {str(e)}")
    
    # Affichage des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

if __name__ == "__main__":
    main()
