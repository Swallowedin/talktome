import streamlit as st
from streamlit.components.v1 import html
import openai
import json
from streamlit.web import WebClient
from streamlit.runtime.scriptrunner import get_script_run_ctx

# Configuration de la page
st.set_page_config(
    page_title="Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"  # Cache la barre latérale par défaut
)

# Masquer les éléments de l'interface Streamlit par défaut
hide_streamlit_style = """
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
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Configuration des secrets
if 'OPENAI_API_KEY' not in st.secrets:
    st.error('⚠️ OPENAI_API_KEY non configurée')
    st.stop()

openai.api_key = st.secrets['OPENAI_API_KEY']

# Cache des réponses pour éviter de multiplier les appels API
if "chat_responses" not in st.session_state:
    st.session_state.chat_responses = {}

# Fonction pour gérer les messages
def handle_message(message: str) -> str:
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant serviable et professionnel."},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur: {str(e)}"

# Endpoint pour recevoir les messages
def handle_chat_request():
    ctx = get_script_run_ctx()
    if ctx is None:
        return

    # Récupérer le message du query parameter
    query_params = st.experimental_get_query_params()
    if "message" in query_params:
        message = query_params["message"][0]
        response = handle_message(message)
        st.session_state.chat_responses[message] = response
        return json.dumps({"response": response})

# HTML du widget avec le style visuel du logo
CHAT_WIDGET_HTML = """
<style>
    /* Variables de couleurs basées sur le logo */
    :root {
        --main-color: #1B4D4D;      /* Vert foncé du logo */
        --light-color: #235f5f;     /* Version plus claire pour les hovers */
        --bg-light: #f0f4f4;        /* Fond très légèrement verdâtre */
        --text-color: #2c3e3e;      /* Texte verdâtre foncé */
    }

    #chat-widget-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        font-family: Arial, sans-serif;
    }

    .chat-widget-button {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background-color: var(--main-color);
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: transform 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
    }

    .chat-widget-button:hover {
        transform: scale(1.1);
    }

    .chat-window {
        display: none;
        position: fixed;
        bottom: 90px;
        right: 20px;
        width: 360px;
        height: 500px;
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 5px 25px rgba(0, 0, 0, 0.2);
        flex-direction: column;
        overflow: hidden;
    }

    .chat-window.active {
        display: flex;
    }

    .chat-header {
        background-color: var(--main-color);
        color: white;
        padding: 16px 20px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .close-button {
        background: transparent;
        border: none;
        color: white;
        font-size: 24px;
        cursor: pointer;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0.8;
    }

    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        background: white;
    }

    .message {
        margin-bottom: 12px;
        max-width: 80%;
        padding: 12px 16px;
        border-radius: 15px;
        font-size: 14px;
        line-height: 1.4;
    }

    .bot-message {
        background-color: var(--bg-light);
        color: var(--text-color);
        margin-right: auto;
        border-bottom-left-radius: 5px;
    }

    .user-message {
        background-color: var(--main-color);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 5px;
    }

    .chat-input {
        padding: 16px;
        border-top: 1px solid #eee;
    }

    .chat-form {
        display: flex;
        gap: 8px;
    }

    .chat-input input {
        flex: 1;
        padding: 12px 16px;
        border: 1px solid #ddd;
        border-radius: 25px;
        outline: none;
        font-size: 14px;
    }

    .chat-input input:focus {
        border-color: var(--main-color);
        box-shadow: 0 0 0 2px rgba(27, 77, 77, 0.1);
    }

    .typing-indicator {
        display: flex;
        gap: 4px;
        padding: 12px;
        background: var(--bg-light);
        border-radius: 10px;
        width: fit-content;
        margin-bottom: 12px;
    }

    .typing-dot {
        width: 6px;
        height: 6px;
        background: var(--text-color);
        border-radius: 50%;
        animation: typing 1s infinite;
    }

    @keyframes typing {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-4px); }
    }

    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
</style>

<div id="chat-widget-container">
    <button class="chat-widget-button" id="chatButton">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
    </button>

    <div class="chat-window" id="chatWindow">
        <div class="chat-header">
            <span>Assistant</span>
            <button class="close-button" id="closeButton">&times;</button>
        </div>

        <div class="chat-messages" id="chatMessages"></div>

        <div class="chat-input">
            <form class="chat-form" id="chatForm">
                <input type="text" id="userInput" placeholder="Posez votre question..." autocomplete="off">
                <button type="submit" class="chat-widget-button" style="width: 40px; height: 40px;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                    </svg>
                </button>
            </form>
        </div>
    </div>
</div>

<script>
class ChatWidget {
    constructor() {
        [Configuration précédente...]
    }

    async handleSubmit(e) {
        e.preventDefault();
        if (this.isWaitingResponse || !this.input.value.trim()) return;

        const userMessage = this.input.value.trim();
        this.addMessage(userMessage, 'user');
        this.input.value = '';
        this.isWaitingResponse = true;

        const indicator = this.showTypingIndicator();

        try {
            // Utiliser les query parameters pour envoyer le message
            const response = await fetch(`?message=${encodeURIComponent(userMessage)}`);
            if (!response.ok) throw new Error('Erreur réseau');

            const data = await response.json();
            this.addMessage(data.response, 'bot');
        } catch (error) {
            this.addMessage("Désolé, je rencontre des difficultés techniques. Veuillez réessayer.", 'bot');
        } finally {
            indicator.remove();
            this.isWaitingResponse = false;
        }
    }
    
    [Autres méthodes restent identiques...]
}

document.addEventListener('DOMContentLoaded', () => {
    new ChatWidget();
});
</script>
"""

def get_chat_response(message: str) -> str:
    """Obtient une réponse de l'API OpenAI"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant serviable et professionnel."},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content

    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return "Je rencontre des difficultés techniques. Veuillez réessayer."

def main():
    # Masquer les éléments Streamlit par défaut
    st.markdown("""
        <style>
            #root > div:first-child {background-color: transparent;}
            .main > div:first-child {padding: 0;}
            header {display: none !important;}
            .block-container {padding: 0 !important;}
            [data-testid="stToolbar"] {display: none !important;}
            footer {display: none !important;}
        </style>
    """, unsafe_allow_html=True)

    # Gérer les requêtes de chat
    handle_chat_request()

    # Afficher le widget
    html(CHAT_WIDGET_HTML, height=500)

if __name__ == "__main__":
    main()
