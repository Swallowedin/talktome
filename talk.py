import streamlit as st
import openai
import os
import logging
from logging.handlers import RotatingFileHandler

# Configuration de la page
st.set_page_config(
   page_title="Assistant VIEW Avocats",
   layout="wide",
   initial_sidebar_state="collapsed"
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=5)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Masquer les éléments Streamlit
st.markdown("""
<style>
   #root > div:first-child { background-color: transparent; }
   .main > div:first-child { padding: 0rem 0rem; }
   header {display: none !important;}
   .block-container {padding: 0 !important;}
   [data-testid="stToolbar"] {display: none !important;}
   .stDeployButton {display: none !important;}
   footer {display: none !important;}
</style>
""", unsafe_allow_html=True)

# Configuration OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Interface de chat
st.title("Assistant VIEW Avocats")
if "messages" not in st.session_state:
   st.session_state.messages = []

# Afficher l'historique
for message in st.session_state.messages:
   with st.chat_message(message["role"]):
       st.markdown(message["content"])

# Zone de saisie
if prompt := st.chat_input("Votre message"):
   st.session_state.messages.append({"role": "user", "content": prompt})
   with st.chat_message("user"):
       st.markdown(prompt)

   # Réponse assistant
   with st.chat_message("assistant"):
       try:
           response = openai.chat.completions.create(
               model="gpt-4o-mini",
               messages=[
                   {"role": "system", "content": "Vous êtes l'assistant virtuel du cabinet VIEW Avocats."},
                   *st.session_state.messages
               ],
               temperature=0.7,
               max_tokens=500
           )
           reply = response.choices[0].message.content
           st.markdown(reply)
           st.session_state.messages.append({"role": "assistant", "content": reply})
           
       except Exception as e:
           logger.error(f"Erreur OpenAI : {str(e)}")
           st.error("Désolé, une erreur est survenue.")
