import streamlit as st
from streamlit.components.v1 import html
import openai
import json
import logging

# Configuration des logs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuration de la page
st.set_page_config(
    page_title="Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Log de démarrage
logger.info("Application démarrée")

# Masquer les éléments de l'interface Streamlit
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

# Vérification de la clé API
if 'OPENAI_API_KEY' not in st.secrets:
    logger.error("Clé API OpenAI non trouvée dans les secrets")
    st.error('⚠️ OPENAI_API_KEY non configurée')
    st.stop()
else:
    logger.info("Clé API OpenAI trouvée dans les secrets")

openai.api_key = st.secrets['OPENAI_API_KEY']

# États de session pour le chat
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_chat_response(message: str) -> str:
    logger.info(f"Nouvelle demande de chat reçue: {message[:50]}...")
    try:
        logger.debug("Tentative d'appel à OpenAI")
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant serviable et professionnel."},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        result = response.choices[0].message.content
        logger.info("Réponse reçue d'OpenAI avec succès")
        return result
    except Exception as e:
        logger.error(f"Erreur lors de l'appel OpenAI: {str(e)}")
        return f"Erreur: {str(e)}"

# HTML complet du widget avec style intégré
CHAT_WIDGET_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* Variables de couleurs basées sur le logo */
        :root {
            --main-color: #1B4D4D;
            --light-color: #235f5f;
            --bg-light: #f0f4f4;
            --text-color: #2c3e3e;
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

        .send-button {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: var(--main-color);
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
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
</head>
<body>
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
                    <button type="submit" class="send-button">
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
                this.isOpen = false;
                this.isWaitingResponse = false;
                
                this.button = document.getElementById('chatButton');
                this.window = document.getElementById('chatWindow');
                this.closeButton = document.getElementById('closeButton');
                this.messages = document.getElementById('chatMessages');
                this.form = document.getElementById('chatForm');
                this.input = document.getElementById('userInput');
                
                this.button.addEventListener('click', () => this.toggleChat());
                this.closeButton.addEventListener('click', () => this.closeChat());
                this.form.addEventListener('submit', (e) => this.handleSubmit(e));
            }

            toggleChat() {
                this.isOpen = !this.isOpen;
                this.window.classList.toggle('active');
                
                if (this.isOpen && this.messages.children.length === 0) {
                    this.addMessage("Bonjour, comment puis-je vous aider ?", 'bot');
                }
            }

            closeChat() {
                this.isOpen = false;
                this.window.classList.remove('active');
            }

            addMessage(text, type) {
                const message = document.createElement('div');
                message.className = `message ${type}-message`;
                message.textContent = text;
                this.messages.appendChild(message);
                this.messages.scrollTop = this.messages.scrollHeight;
            }

            showTypingIndicator() {
                const indicator = document.createElement('div');
                indicator.className = 'typing-indicator';
                indicator.innerHTML = `
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                `;
                this.messages.appendChild(indicator);
                this.messages.scrollTop = this.messages.scrollHeight;
                return indicator;
            }

            async handleSubmit(e) {
                e.preventDefault();
                if (this.isWaitingResponse || !this.input.value.trim()) return;

                const userMessage = this.input.value.trim();
                console.log("Message envoyé:", userMessage);

                this.addMessage(userMessage, 'user');
                this.input.value = '';
                this.isWaitingResponse = true;

                const indicator = this.showTypingIndicator();

                try {
                    console.log("Envoi de la requête à Streamlit");
        
                    // Utiliser l'URL réelle de la page
                    const baseUrl = window.top.location.href;
                    const url = new URL(baseUrl);
                    url.searchParams.set('message', userMessage);
        
                    const response = await fetch(url.toString(), {
                        method: 'GET',
                        headers: {
                            'Accept': 'application/json'
                        }
                    });

                    console.log("Status de la réponse:", response.status);
        
                    if (!response.ok) throw new Error('Erreur réseau');

                    const text = await response.text();
                    console.log("Réponse brute:", text);

                    const data = JSON.parse(text);
                    console.log("Réponse parsée:", data);
        
                    if (data.response) {
                        this.addMessage(data.response, 'bot');
                    }
                } catch (error) {
                    console.error("Erreur:", error);
                    this.addMessage("Désolé, je rencontre des difficultés techniques. Veuillez réessayer.", 'bot');
                } finally {
                    indicator.remove();
                    this.isWaitingResponse = false;
                }
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            new ChatWidget();
        });
    </script>
</body>
</html>
"""

def main():
    logger.info("Démarrage de la fonction main()")
    
    # Gérer les messages entrants
    params = st.experimental_get_query_params()
    if "message" in params:
        message = params["message"][0]
        logger.info(f"Message reçu dans les query params: {message[:50]}...")
        response = get_chat_response(message)
        logger.info(f"Réponse générée: {response[:50]}...")
        # Retourner explicitement du JSON
        st.json({"response": response})
        logger.info("Réponse JSON envoyée")
        return

    logger.info("Affichage du widget HTML")
    # Afficher le widget
    html(CHAT_WIDGET_HTML, height=700)

if __name__ == "__main__":
    try:
        logger.info("Démarrage de l'application")
        main()
        logger.info("Application démarrée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors du démarrage de l'application: {str(e)}")
        st.error("Une erreur est survenue lors du démarrage de l'application")
