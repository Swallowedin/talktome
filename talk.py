import streamlit as st
import openai
import json
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional, List

# Configuration minimale
st.set_page_config(page_title="Assistant VIEW Avocats", layout="wide", initial_sidebar_state="collapsed")

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=5)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Style minimal
st.markdown("""
<style>
    /* Cacher tous les éléments non essentiels */
    header, footer, [data-testid="stToolbar"], .stDeployButton, #MainMenu {
        display: none !important;
    }
    
    /* Reset des marges et paddings */
    .main, .block-container, .element-container {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Ajustement du select et input uniquement */
    .stSelectbox > div > div, .stTextInput > div > div > input {
        padding: 8px !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    /* Style minimal du bouton */
    .stButton > button {
        margin-top: 5px !important;
    }
</style>
""", unsafe_allow_html=True)

def load_knowledge_base(file_path: str) -> Optional[str]:
    try:
        if not os.path.exists(file_path):
            logger.error(f"Le fichier {file_path} n'existe pas")
            return None
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la base de connaissances: {str(e)}")
        return None

def get_openai_response(message: str, context: str = "") -> dict:
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
        return {"status": "success", "response": response.choices[0].message.content}
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à OpenAI : {str(e)}")
        return {"status": "error", "message": str(e)}

def main():
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("Clé API OpenAI manquante")
        return
    
    knowledge_base_content = load_knowledge_base("knowledge_base.txt")
    if knowledge_base_content is None:
        logger.error("Erreur base de connaissances")
        return
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Interface minimale
    questions_predefinies = [
        "Quels sont vos domaines d'expertise ?",
        "Comment prendre rendez-vous ?",
        "Quels sont vos tarifs ?",
        "Où se trouve votre cabinet ?"
    ]
    
    selected_question = st.selectbox(
        "",  # Label vide
        [""] + questions_predefinies,
        label_visibility="collapsed"
    )
    
    custom_question = st.text_input(
        "",  # Label vide
        placeholder="Ou posez votre propre question",
        label_visibility="collapsed"
    )
    
    if st.button("Envoyer"):
        question = custom_question if custom_question else selected_question
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
    
    # Messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

if __name__ == "__main__":
    main()
