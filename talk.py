import streamlit as st
import openai
import json

# Configuration de la page
st.set_page_config(page_title="Assistant", layout="wide", initial_sidebar_state="collapsed")

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

# Fonction pour obtenir une réponse d'OpenAI
def get_openai_response(message: str) -> dict:
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
        return {"status": "success", "response": response.choices[0].message.content}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Le HTML du widget avec le JavaScript modifié
CHAT_WIDGET_HTML = """
<!DOCTYPE html>
<html lang="fr">
<!-- ... (styles inchangés) ... -->
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

            // Stocker l'URL de base au démarrage
            this.baseUrl = this.getBaseUrl();
        }

        getBaseUrl() {
            // Récupérer l'URL parente si nous sommes dans un iframe
            const parentUrl = window.parent.location.href;
            // Nettoyer l'URL de tous les paramètres existants
            return parentUrl.split('?')[0];
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
            this.addMessage(userMessage, 'user');
            this.input.value = '';
            this.isWaitingResponse = true;

            const indicator = this.showTypingIndicator();

            try {
                // Construire l'URL avec le message
                const url = new URL(this.baseUrl);
                url.searchParams.set('message', userMessage);

                const response = await fetch(url.toString(), {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json',
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                if (data.status === "success" && data.response) {
                    this.addMessage(data.response, 'bot');
                } else if (data.status === "error") {
                    throw new Error(data.message);
                } else {
                    throw new Error('Format de réponse invalide');
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
