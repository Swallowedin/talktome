import streamlit as st
import openai
import os
import logging
from logging.handlers import RotatingFileHandler
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Configuration page
st.set_page_config(
   page_title="Assistant VIEW Avocats",
   layout="wide",
   initial_sidebar_state="collapsed"
)

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=5)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Styles
st.markdown("""
<style>
   #root > div:first-child { background-color: transparent; }
   .main > div:first-child { padding: 0rem 0rem; }
   header {display: none !important;}
   .block-container {padding: 0 !important;}
   [data-testid="stToolbar"] {display: none !important;}
   .stDeployButton {display: none !important;}
   footer {display: none !important;}
   
   .stChatFloatingInputContainer {
       position: fixed !important;
       bottom: 20px !important;
       background: white !important;
       padding: 10px !important;
       border-radius: 10px !important;
       box-shadow: 0 0 10px rgba(0,0,0,0.1) !important;
       width: 90% !important;
   }
   
   .stChatMessage {
       background: white !important;
       border-radius: 10px !important;
       margin: 5px 0 !important;
       padding: 10px !important;
   }
   
   .st-emotion-cache-1v0mbdj {
       width: 100% !important;
       max-width: none !important;
   }
</style>
""", unsafe_allow_html=True)

class KnowledgeBase:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        
    def load_documents(self, file_path):
        loader = TextLoader(file_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        
    def query(self, question, k=3):
        if not self.vector_store:
            return None
        return self.vector_store.similarity_search(question, k=k)

# Configuration OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialisation de la base de connaissances
if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = KnowledgeBase()
    st.session_state.knowledge_base.load_documents("knowledge_base.txt")

# Interface chat
if "messages" not in st.session_state:
   st.session_state.messages = []

# Afficher historique
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
           # Recherche dans la base de connaissances
           relevant_docs = st.session_state.knowledge_base.query(prompt)
           context = ""
           if relevant_docs:
               context = "INSTRUCTIONS IMPORTANTES: Basez-vous prioritairement sur ces informations pour répondre:\n\n" + \
                        "\n".join([doc.page_content for doc in relevant_docs]) + \
                        "\n\nSi ces informations ne sont pas suffisantes, vous pouvez utiliser vos connaissances générales en complément."
           
           response = openai.chat.completions.create(
               model="gpt-4o-mini",
               messages=[
                   {"role": "system", "content": "Vous êtes l'assistant virtuel du cabinet VIEW Avocats. Vous devez IMPÉRATIVEMENT utiliser les informations fournies dans le contexte pour répondre. Ne répondez qu'en vous basant sur les informations disponibles dans la base de connaissances. Si la réponse n'est pas dans la base, orientez vers une consultation avec un avocat."},
                   {"role": "user", "content": f"{context}\n\nQuestion de l'utilisateur: {prompt}"}
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
