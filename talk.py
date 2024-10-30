import streamlit as st
import openai
import json

# Configuration de la page
st.set_page_config(
    page_title="Assistant VIEW Avocats",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

# Headers CORS
st.markdown("""
<script>
    if (window.top !== window.self) {
        document.addEventListener('DOMContentLoaded', function() {
            const headers = new Headers();
            headers.append('Access-Control-Allow-Origin', '*');
            headers.append('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
            headers.append('Access-Control-Allow-Headers', 'Content-Type');
        });
    }
</script>
""", unsafe_allow_html=True)

# Vérification de la clé API OpenAI
if 'OPENAI_API_KEY' not in st.secrets:
    st.error('⚠️ OPENAI_API_KEY non configurée')
    st.stop()

openai.api_key = st.secrets['OPENAI_API_KEY']

def get_openai_response(message: str) -> dict:
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Gardé le modèle original
            messages=[
                {
                    "role": "system",
                    "content": """Vous êtes l'assistant virtuel du cabinet VIEW Avocats. 
                    Répondez de manière professionnelle et précise aux questions des utilisateurs,
                    en vous basant uniquement sur des informations factuelles et juridiques vérifiées."""
                },
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return {
            "status": "success",
            "response": response.choices[0].message.content
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def add_cors_headers():
    st.markdown("""
        <script>
            const meta = document.createElement('meta');
            meta.setAttribute('http-equiv', 'Access-Control-Allow-Origin');
            meta.setAttribute('content', '*');
            document.head.appendChild(meta);
        </script>
    """, unsafe_allow_html=True)

def main():
    # Ajouter les headers CORS
    add_cors_headers()
    
    # Gérer les messages de chat
    params = st.query_params
    if "message" in params:
        message = params["message"]
        response = get_openai_response(message)
        
        # Renvoyer la réponse en JSON
        st.write(response)
        return

    # Page par défaut quand aucun message n'est envoyé
    st.write("Assistant VIEW Avocats - Service en ligne")

if __name__ == "__main__":
    main()
