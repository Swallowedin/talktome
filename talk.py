import streamlit as st
import openai
import json
from streamlit.components.v1 import html

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

# Configuration CORS
st.markdown("""
    <script>
        const meta = document.createElement('meta');
        meta.setAttribute('http-equiv', 'Access-Control-Allow-Origin');
        meta.setAttribute('content', '*');
        document.head.appendChild(meta);
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
                    Répondez de manière professionnelle et précise aux questions des utilisateurs.
                    Vos réponses doivent être concises et factuelles."""
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

def set_cors_headers():
    st.write("""
        <script>
            const headers = new Headers();
            headers.append('Access-Control-Allow-Origin', 'https://view-avocats.fr');
            headers.append('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
            headers.append('Access-Control-Allow-Headers', 'Content-Type');
            headers.append('Access-Control-Allow-Credentials', 'true');
        </script>
    """, unsafe_allow_html=True)

def main():
    set_cors_headers()
    
    # Gérer les messages de chat
    params = st.query_params
    if "message" in params:
        message = params["message"]
        response = get_openai_response(message)
        
        # Ajouter les headers CORS à la réponse
        for header in [
            ('Access-Control-Allow-Origin', 'https://view-avocats.fr'),
            ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type'),
            ('Access-Control-Allow-Credentials', 'true'),
        ]:
            st.response.headers[header[0]] = header[1]
            
        st.json(response)
        return

    # Page par défaut
    st.write("Service de chat VIEW Avocats en ligne")

if __name__ == "__main__":
    main()
