import streamlit as st
import openai
import logging
from logging.handlers import RotatingFileHandler
import time

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

# Code HTML du widget
CHAT_HTML = """
<script>
var lastMessageTime = 0;

function sendMessage(message) {
    const currentTime = Date.now();
    if (currentTime - lastMessageTime < 1000) {
        return new Promise(resolve => setTimeout(() => resolve(sendMessage(message)), 1000));
    }
    lastMessageTime = currentTime;

    const element = window.parent.document.querySelector('#streamlit-widget');
    const event = new CustomEvent('streamlit:message', {
        detail: { message: message }
    });
    element.dispatchEvent(event);
    return Promise.resolve();
}

window.sendMessage = sendMessage;
</script>
<div class="chat-widget">
    <style>
        .chat-widget {
            width: 100%;
            max-width: 800px;
            height: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
        }

        .chat-header {
            padding: 15px 20px;
            background: #22c55e;
            color: white;
            border-radius: 10px 10px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 500;
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
            padding: 12px 16px;
            border-radius: 15px;
            margin: 5px 0;
            word-wrap: break-word;
            line-height: 1.5;
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
            padding: 12px;
            border: 1px solid #e2e8f0;
            border-radius: 5px;
            outline: none;
            transition: border-color 0.2s;
        }

        .chat-input input:focus {
            border-color: #22c55e;
        }

        .chat-input button {
            padding: 12px 20px;
            background: #22c55e;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            display: flex;
            align-items: center;
            transition: background 0.2s;
            font-weight: 500;
        }

        .chat-input button:after {
            content: '➤';
            margin-left: 8px;
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
            padding: 12px 16px;
            border-radius: 15px;
            color: #1a1a1a;
            margin: 5px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .typing-indicator.visible {
            display: block;
        }

        .typing-dot {
            display: inline-block;
            width: 4px;
            height: 4px;
            border-radius: 50%;
            background-color: #1a1a1a;
            margin-right: 3px;
            animation: typing 1s infinite;
        }

        @keyframes typing {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-4px); }
        }
    </style>
    <div class="chat-header">
        <span>Assistant VIEW Avocats</span>
    </div>
    <div class="chat-messages" id="chat-messages"></div>
    <div class="typing-indicator">
        L'assistant répond
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
    </div>
    <div class="chat-input">
        <input type="text" placeholder="Posez votre question ici..." id="chat-input">
        <button onclick="sendMessage(document.getElementById('chat-input').value)">Envoi</button>
    </div>
</div>

<script>
document.getElementById('chat-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage(this.value);
        this.value = '';
    }
});

window.addEventListener('message', function(e) {
    if (e.data.type === 'chat_response') {
        const messagesDiv = document.getElementById('chat-messages');
        
        // Ajouter le message utilisateur
        const userDiv = document.createElement('div');
        userDiv.className = 'message user';
        userDiv.textContent = e.data.user_message;
        messagesDiv.appendChild(userDiv);
        
        // Ajouter la réponse de l'assistant
        const assistantDiv = document.createElement('div');
        assistantDiv.className = 'message assistant';
        assistantDiv.textContent = e.data.response;
        messagesDiv.appendChild(assistantDiv);
        
        // Scroll en bas
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        
        // Réactiver l'input
        document.getElementById('chat-input').value = '';
        document.getElementById('chat-input').disabled = false;
    }
});
</script>
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
    # Injecter le widget HTML avec un ID unique
    st.components.v1.html(CHAT_HTML, height=600)
    
    # Créer un placeholder pour la communication JS->Python
    placeholder = st.empty()
    
    # Si un message est reçu via le composant
    if message := st.experimental_get_query_params().get("message"):
        response = get_openai_response(message[0])
        st.write(response)

    # Masquer les éléments Streamlit par défaut
    st.markdown("""
        <style>
            header {display: none !important;}
            .stDeployButton {display: none !important;}
            footer {display: none !important;}
            [data-testid="stToolbar"] {display: none !important;}
        </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
