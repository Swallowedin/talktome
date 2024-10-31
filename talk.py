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

# Configuration OpenAI
if 'OPENAI_API_KEY' not in st.secrets:
    logger.error('⚠️ OPENAI_API_KEY non configurée')
    st.error('⚠️ OPENAI_API_KEY non configurée')
    st.stop()

openai.api_key = st.secrets['OPENAI_API_KEY']

# HTML original du widget
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

        /* Masquer les éléments Streamlit */
        header {display: none !important;}
        .stDeployButton {display: none !important;}
        footer {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
    </style>

    <div class="chat-header">
        <span>Assistant VIEW Avocats</span>
        <button class="toggle-btn">▼</button>
    </div>
    <div class="chat-messages"></div>
    <div class="typing-indicator">L'assistant répond...</div>
    <div class="chat-input">
        <input type="text" placeholder="Posez votre question ici...">
        <button type="submit">Envoi</button>
    </div>
</div>

<script>
class ViewChatWidget {
    constructor() {
        this.widget = document.getElementById('view-chat-widget');
        this.messagesContainer = this.widget.querySelector('.chat-messages');
        this.input = this.widget.querySelector('input');
        this.sendButton = this.widget.querySelector('button[type="submit"]');
        this.toggleBtn = this.widget.querySelector('.toggle-btn');
        this.typingIndicator = this.widget.querySelector('.typing-indicator');
        this.isOpen = false;

        this.setupEventListeners();
        this.loadMessages();
    }

    setupEventListeners() {
        this.toggleBtn.addEventListener('click', () => this.toggleChat());
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        this.widget.classList.toggle('open', this.isOpen);
        this.toggleBtn.textContent = this.isOpen ? '▼' : '▲';
        if (this.isOpen) this.input.focus();
    }

    async sendMessage() {
        const message = this.input.value.trim();
        if (!message) return;

        // Désactiver l'interface pendant l'envoi
        this.input.value = '';
        this.input.disabled = true;
        this.sendButton.disabled = true;

        // Afficher le message utilisateur
        this.addMessage('user', message);

        // Afficher l'indicateur de frappe
        this.typingIndicator.classList.add('visible');

        try {
            const response = await this.callChatAPI(message);
            if (response && response.status === 'success') {
                this.addMessage('assistant', response.response);
            } else {
                this.addMessage('assistant', "Je suis désolé, je n'ai pas pu traiter votre demande. Veuillez réessayer.");
            }
        } catch (error) {
            console.error('Error:', error);
            this.addMessage('assistant', "Une erreur est survenue. Veuillez réessayer plus tard.");
        } finally {
            // Réactiver l'interface
            this.input.disabled = false;
            this.sendButton.disabled = false;
            this.typingIndicator.classList.remove('visible');
            this.input.focus();
        }
    }

    async callChatAPI(message) {
        const encodedMessage = encodeURIComponent(message);
        const response = await fetch(`/?message=${encodedMessage}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    }

    addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = content;
        this.messagesContainer.appendChild(messageDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    loadMessages() {
        const savedMessages = localStorage.getItem('viewChatHistory');
        if (savedMessages) {
            JSON.parse(savedMessages).forEach(msg => {
                this.addMessage(msg.type, msg.content);
            });
        }
    }
}

// Initialiser le widget
document.addEventListener('DOMContentLoaded', () => {
    const chat = new ViewChatWidget();
    setTimeout(() => {
        if (!chat.isOpen) {
            chat.toggleChat();
        }
    }, 2000);
});
</script>
</div>
"""

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
    # Gérer les messages de chat
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
