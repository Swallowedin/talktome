import streamlit as st
import openai
import json

# Configuration de la page
st.set_page_config(page_title="Assistant VIEW Avocats", layout="wide", initial_sidebar_state="collapsed")

# Masquer les éléments Streamlit par défaut
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
</style>
""", unsafe_allow_html=True)

# Vérification de la clé API OpenAI
if 'OPENAI_API_KEY' not in st.secrets:
    st.error('⚠️ OPENAI_API_KEY non configurée')
    st.stop()

openai.api_key = st.secrets['OPENAI_API_KEY']

def get_openai_response(message: str) -> dict:
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Vous êtes l'assistant virtuel du cabinet VIEW Avocats. Répondez de manière professionnelle et précise aux questions des utilisateurs."},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return {"status": "success", "response": response.choices[0].message.content}
    except Exception as e:
        return {"status": "error", "message": str(e)}

CHAT_WIDGET_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* ... [styles précédents inchangés] ... */
        
        .send-button {
            min-width: 40px;
            min-height: 40px;
            width: 40px;
            height: 40px;
            padding: 0;
            border-radius: 50%;
            background-color: #1B4D4D;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            flex-shrink: 0;
        }

        .send-button:hover {
            background-color: #235f5f;
        }

        .send-button svg {
            width: 16px;
            height: 16px;
            margin: auto;
        }
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
                <span>Assistant VIEW Avocats</span>
                <button class="close-button" id="closeButton">&times;</button>
            </div>

            <div class="chat-messages" id="chatMessages"></div>

            <div class="chat-input">
                <form class="chat-form" id="chatForm">
                    <input type="text" id="userInput" placeholder="Posez votre question..." autocomplete="off">
                    <button type="submit" class="send-button">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
                this.streamlitUrl = window.location.origin;
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

            // ... [autres méthodes inchangées] ...

            async handleSubmit(e) {
                e.preventDefault();
                if (this.isWaitingResponse || !this.input.value.trim()) return;

                const userMessage = this.input.value.trim();
                this.addMessage(userMessage, 'user');
                this.input.value = '';
                this.isWaitingResponse = true;

                const indicator = this.showTypingIndicator();

                try {
                    const response = await fetch(`${this.streamlitUrl}?message=${encodeURIComponent(userMessage)}`, {
                        method: 'GET',
                        headers: {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                        },
                        mode: 'cors',
                        credentials: 'include'
                    });

                    const data = await response.json();
                    if (data.status === "success" && data.response) {
                        this.addMessage(data.response, 'bot');
                    } else {
                        throw new Error(data.message || 'Erreur de réponse');
                    }
                } catch (error) {
                    console.error('Error:', error);
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
    # Gérer les messages de chat
    params = st.query_params
    if "message" in params:
        message = params["message"]
        response = get_openai_response(message)
        st.json(response)
        return

    # Afficher le widget
    st.components.v1.html(CHAT_WIDGET_HTML, height=700)

if __name__ == "__main__":
    main()
