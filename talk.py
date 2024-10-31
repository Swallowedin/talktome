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

# Masquer les éléments Streamlit
st.markdown("""
    <style>
        header {display: none !important;}
        footer {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        .stDeployButton {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# Configuration OpenAI
if 'OPENAI_API_KEY' not in st.secrets:
    logger.error('⚠️ OPENAI_API_KEY non configurée')
    st.error('⚠️ OPENAI_API_KEY non configurée')
    st.stop()

openai.api_key = st.secrets['OPENAI_API_KEY']

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

# HTML du widget avec JavaScript simplifié
CHAT_HTML = """
<div id="view-chat-widget" class="chat-widget">
    <style>
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
            transform: translateY(90%);
            transition: transform 0.3s ease;
        }

        .chat-widget.open {
            transform: translateY(0);
        }

        .chat-header {
            padding: 15px 20px;
            background: #22c55e;
            color: white;
            border-radius: 10px 10px 0 0;
            cursor: pointer;
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
            background: #f8fafc;
        }

        .message {
            max-width: 85%;
            padding: 10px 15px;
            border-radius: 15px;
            margin: 5px 0;
            word-wrap: break-word;
        }

        .message.user {
            background: #22c55e;
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 5px;
        }

        .message.assistant {
            background: white;
            color: #1a1a1a;
            align-self: flex-start;
            border-bottom-left-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .chat-input {
            padding: 15px;
            background: white;
            border-top: 1px solid #e2e8f0;
            display: flex;
            gap: 10px;
        }

        .chat-input input {
            flex: 1;
            padding: 10px;
            border: 1px solid #e2e8f0;
            border-radius: 5px;
            outline: none;
        }

        .chat-input button {
            padding: 10px 20px;
            background: #22c55e;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.2s;
            display: flex;
            align-items: center;
        }

        .chat-input button:after {
            content: '➤';
            margin-left: 5px;
        }

        .chat-input button:hover {
            background: #16a34a;
        }

        .chat-input button:disabled {
            background: #cbd5e1;
            cursor: not-allowed;
        }

        .typing-indicator {
            display: none;
            align-self: flex-start;
            background: white;
            padding: 10px 15px;
            border-radius: 15px;
            color: #1a1a1a;
            margin: 5px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .typing-indicator.visible {
            display: block;
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

    <div class="chat-header">
        <span>Assistant VIEW Avocats</span>
        <button class="toggle-btn">▼</button>
    </div>
    <div class="chat-messages"></div>
    <div class="typing-indicator">L'assistant répond...</div>
    <div class="chat-input">
        <input type="text" placeholder="Posez votre question ici..." id="chat-input">
        <button onclick="handleSendMessage()">Envoi</button>
    </div>
</div>

<script>
let isOpen = false;
const widget = document.getElementById('view-chat-widget');
const input = document.getElementById('chat-input');
const messagesContainer = widget.querySelector('.chat-messages');
const toggleBtn = widget.querySelector('.toggle-btn');
const typingIndicator = widget.querySelector('.typing-indicator');

// Fonction pour basculer le chat
function toggleChat() {
    isOpen = !isOpen;
    widget.classList.toggle('open', isOpen);
    toggleBtn.textContent = isOpen ? '▼' : '▲';
    if (isOpen) input.focus();
}

// Fonction pour ajouter un message
function addMessage(content, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
    messageDiv.textContent = content;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Fonction pour envoyer un message
async function handleSendMessage() {
    const message = input.value.trim();
    if (!message) return;

    // Désactiver l'input pendant l'envoi
    input.value = '';
    input.disabled = true;
    
    // Afficher le message utilisateur
    addMessage(message, true);
    
    // Afficher l'indicateur de frappe
    typingIndicator.style.display = 'block';

    try {
        const response = await fetch(`?message=${encodeURIComponent(message)}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });

        const data = await response.json();
        
        if (data.status === 'success') {
            addMessage(data.response, false);
        } else {
            addMessage("Désolé, une erreur est survenue. Veuillez réessayer.", false);
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage("Désolé, une erreur est survenue. Veuillez réessayer.", false);
    } finally {
        // Réactiver l'input
        input.disabled = false;
        typingIndicator.style.display = 'none';
        input.focus();
    }
}

// Event listeners
toggleBtn.addEventListener('click', toggleChat);
input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSendMessage();
});

// Ouvrir le chat après 2 secondes
setTimeout(() => {
    if (!isOpen) toggleChat();
}, 2000);
</script>
</div>
"""

def main():
    # Gérer les requêtes API
    params = st.query_params
    if "message" in params:
        message = params["message"]
        response = get_openai_response(message)
        st.json(response)
        return

    # Afficher le widget
    st.components.v1.html(CHAT_HTML, height=700)

if __name__ == "__main__":
    main()
