from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import openai

# Cargar variables de entorno desde la carpeta config
load_dotenv(dotenv_path=os.path.join("config", ".env"))

# Configuración de FastAPI
app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Cambiar a dominios específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de PostgreSQL
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

def get_db_connection():
    """Establece una conexión con la base de datos."""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# Configuración de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE")

# Modelos para solicitudes
class VillancicoRequest(BaseModel):
    prompt: str

class ImageRequest(BaseModel):
    prompt: str

@app.post("/generate_villancico")
async def generate_villancico(request: VillancicoRequest):
    """
    Genera un villancico usando OpenAI GPT.
    """
    try:
        # Llamada a GPT para generar el villancico
        gpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": f"Genera un villancico que se parezca a: {request.prompt}"}
            ],
            max_tokens=500,
        )

        villancico_letra = gpt_response["choices"][0]["message"]["content"]

        return {"letra": villancico_letra}

    except openai.error.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"Error en la solicitud a OpenAI: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")

@app.post("/generate_image")
async def generate_image(request: ImageRequest):
    """
    Genera una imagen usando OpenAI DALL-E.
    """
    try:
        # Llamada a DALL-E para generar la imagen
        dalle_response = openai.Image.create(
            model="dall-e-3",  # Asegurando el modelo correcto
            prompt=request.prompt,
            n=1,
            size="1024x1024",
        )

        image_url = dalle_response["data"][0]["url"]

        return {"image_url": image_url}

    except openai.error.OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"Error en la solicitud a OpenAI: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")
