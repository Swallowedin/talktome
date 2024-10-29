# app.py
import streamlit as st
import openai
from datetime import datetime
import json
import os

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Assistant Juridique",
    page_icon="⚖️",
    layout="centered"
)

# Styles CSS personnalisés
st.markdown("""
<style>
    .stTextInput > div > div > input {
        background-color: white;
    }
    .user-message {
        background-color: #2563EB;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #F3F4F6;
        color: black;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    .message-container {
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de la session state
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Bonjour, je suis l'assistant juridique virtuel du cabinet. Comment puis-je vous aider aujourd'hui ?"
        }
    ]

def init_openai():
    """Initialise OpenAI avec la clé API depuis les secrets"""
    # En production, utilisez st.secrets
    if 'OPENAI_API_KEY' in st.secrets:
        openai.api_key = st.secrets['OPENAI_API_KEY']
    # Pour le développement local
    elif 'OPENAI_API_KEY' in os.environ:
        openai.api_key = os.environ['OPENAI_API_KEY']
    else:
        st.error("La clé API OpenAI n'est pas configurée.")
        st.stop()

def get_chatbot_response(messages):
    """Obtient une réponse de l'API OpenAI"""
    try:
        system_prompt = """Tu es un assistant virtuel pour un cabinet d'avocats français.
        Ton rôle est d'aider les visiteurs avec des informations générales sur le cabinet et le droit français.
        Instructions importantes:
        - Réponds de manière professionnelle et concise
        - Ne donne jamais de conseil juridique spécifique
        - Pour les questions complexes, suggère de prendre rendez-vous avec un avocat
        - Informe que les réponses sont données à titre informatif
        - Utilise le vouvoiement
        - Ne mentionne pas que tu es une IA
        - Nom du cabinet: {VOTRE_NOM_CABINET}
        - Adresse: {VOTRE_ADRESSE}
        - Téléphone: {VOTRE_TELEPHONE}
        - Horaires: {VOS_HORAIRES}
        - Domaines de pratique: {VOS_DOMAINES}"""

        full_messages = [
            {"role": "system", "content": system_prompt},
            *messages
        ]

        response = openai.chat.completions.create(
            model="gpt-4",  # ou gpt-3.5-turbo selon votre abonnement
            messages=full_messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content

    except Exception as e:
        st.error(f"Erreur lors de la communication avec OpenAI: {str(e)}")
        return "Je rencontre des difficultés techniques. Veuillez réessayer ou nous contacter directement par téléphone."

def save_conversation(messages):
    """Sauvegarde la conversation dans un fichier JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    conversation = {
        "timestamp": timestamp,
        "messages": messages
    }
    
    # Créer le dossier logs s'il n'existe pas
    os.makedirs("logs", exist_ok=True)
    
    # Sauvegarder la conversation
    with open(f"logs/conversation_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(conversation, f, ensure_ascii=False, indent=2)

def main():
    st.title("Assistant Juridique")
    
    # Initialisation d'OpenAI
    init_openai()

    # Affichage des messages
    for message in st.session_state.messages:
        role_style = "user-message" if message["role"] == "user" else "assistant-message"
        st.markdown(f'<div class="{role_style}">{message["content"]}</div>', unsafe_allow_html=True)

    # Zone de saisie utilisateur
    user_input = st.text_input("Votre question:", key="user_input", placeholder="Posez votre question...")

    # Traitement du message utilisateur
    if user_input:
        # Ajouter le message utilisateur à l'historique
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Obtenir la réponse du chatbot
        with st.spinner("En train de réfléchir..."):
            bot_response = get_chatbot_response(st.session_state.messages)
            
        # Ajouter la réponse du bot à l'historique
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        
        # Sauvegarder la conversation
        save_conversation(st.session_state.messages)
        
        # Recharger la page pour afficher les nouveaux messages
        st.rerun()

if __name__ == "__main__":
    main()
