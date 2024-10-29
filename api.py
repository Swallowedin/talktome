from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import openai
from pydantic import BaseModel

app = FastAPI()

# Permettre les requêtes CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration OpenAI
openai.api_key = "votre-clé-api"  # À mettre dans un .env

@app.post("/chat")
async def chat(message: str):
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
        return {"response": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}
