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
    layout="centered",  # Centré pour une meilleure présentation
    initial_sidebar_state="collapsed"
)

# Style élégant et professionnel
st.markdown("""
<style>
    /* Style général */
    .main {
        background-color: #ffffff;
    }
    
    /* Style des conteneurs */
    .element-container {
        padding: 0.5rem 0;
    }
    
    /* Style du selectbox */
    .stSelectbox > div > div {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        background: white;
        padding: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #1D4E44;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Style du champ texte */
    .stTextInput > div > div > input {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1D4E44;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Style du bouton */
    .stButton > button {
        background-color: #1D4E44;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #2a6d5f;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-1px);
    }
    
    /* Style des messages du chat */
    .stChatMessage {
        background-color: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
    
    /* Style des messages utilisateur */
    .stChatMessage[data-testid="user-message"] {
        background-color: #f8f9fa;
    }
    
    /* Style des messages assistant */
    .stChatMessage[data-testid="assistant-message"] {
        background-color: #f1f8f6;
        border-left: 3px solid #1D4E44;
    }
    
    /* Style des labels */
    .stSelectbox label, .stTextInput label {
        color: #666;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 0.3rem;
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
    
    # Interface élégante
    questions_predefinies = [
        "Quels sont vos domaines d'expertise ?",
        "Comment prendre rendez-vous ?",
        "Quels sont vos tarifs ?",
        "Où se trouve votre cabinet ?"
    ]
    
    st.markdown("##### Posez votre question")
    
    selected_question = st.selectbox(
        "Choisissez une question fréquente",
        [""] + questions_predefinies
    )
    
    custom_question = st.text_input(
        "Ou écrivez votre propre question",
        placeholder="Tapez votre question ici..."
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
    
    # Affichage des messages avec style
    if st.session_state.messages:
        st.markdown("---")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

if __name__ == "__main__":
    main()
