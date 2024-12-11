import streamlit as st
import openai
import requests
import json
import os
import time
from dotenv import load_dotenv
from PIL import Image
import io
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
import smtplib
from openai import AzureOpenAI

# Cargar variables de entorno
load_dotenv()

# Configuración de APIs
openai.api_key = os.getenv("OPENAI_API_KEY")
SUNO_BASE_URL = os.getenv("SUNO_API_URL", "http://localhost:3000")
SUNO_COOKIE = os.getenv("SUNO_COOKIE")

# Clase para manejar la API de Suno
class SunoAPI:
    def __init__(self, base_url, cookie):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Cookie": cookie
        }
    
    def check_credits(self):
        response = requests.get(
            f"{self.base_url}/api/get_limit",
            headers=self.headers
        )
        return response.json()
    
    def generate_music(self, lyrics, style="villancico navideño español"):
        endpoint = f"{self.base_url}/api/custom_generate"
        data = {
            "lyrics": lyrics,
            "style": style,
            "title": "Villancico Navideño",
            "description": "Villancico tradicional español con instrumentos navideños",
            "duration": 60
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            if task_id := result.get("task_id"):
                return self.wait_for_completion(task_id)
            return result
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error al generar la música: {str(e)}")
            return None
    
    def wait_for_completion(self, task_id, max_attempts=30):
        endpoint = f"{self.base_url}/api/get"
        
        for _ in range(max_attempts):
            response = requests.get(
                f"{endpoint}?ids={task_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "completed":
                    return result.get("url")
            
            st.warning("🎵 Generando música... por favor espera.")
            time.sleep(10)
        
        raise Exception("Tiempo de espera agotado para la generación de música")

# Funciones auxiliares
def setup_suno():
    if not SUNO_COOKIE:
        st.error("""
        🚨 No se ha configurado la cookie de Suno. Por favor:
        1. Crea una cuenta en app.suno.ai
        2. Obtén la cookie siguiendo las instrucciones en github.com/gcui-art/suno-api
        3. Configura la variable de entorno SUNO_COOKIE
        """)
        return None
    
    suno = SunoAPI(SUNO_BASE_URL, SUNO_COOKIE)
    try:
        credits = suno.check_credits()
        st.sidebar.info(f"🎵 Créditos Suno disponibles: {credits.get('credits_left', 'No disponible')}")
        return suno
    except Exception as e:
        st.error(f"Error al conectar con Suno: {str(e)}")
        return None

def generar_letra(tema):
    """Genera la letra del villancico usando ChatGPT"""
    try:
        response = openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un experto compositor de villancicos navideños en español. "
                               "Genera letras festivas, alegres y apropiadas para toda la familia."
                },
                {
                    "role": "user",
                    "content": f"Crea un villancico navideño sobre: {tema}. "
                               "Debe tener estrofas y un estribillo pegadizo. "
                               "La letra debe ser original y creativa."
                }
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:  # Captura general de excepciones
        st.error(f"Error al generar la letra: {e}")
        return ""

def generar_imagen(descripcion):
    """Genera una imagen navideña usando DALL-E"""
    response = openai.Image.create(
        model="dall-e-3",
        prompt=f"Ilustración navideña para un villancico sobre: {descripcion}. "
               "Estilo alegre y festivo, apropiado para toda la familia.",
        size="1024x1024",
        quality="standard",
        n=1
    )
    return response.data[0].url

def enviar_por_email(email, letra, audio_url, imagen_url):
    """Función para enviar el villancico por email"""
    # Implementar la lógica de envío de email
    pass

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="🎄 Generador de Villancicos Navideños",
    page_icon="🎅",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #c41e3a;
        color: white;
        border-radius: 20px;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        border-radius: 20px;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .success-message {
        padding: 1rem;
        border-radius: 10px;
        background-color: #d4edda;
        color: #155724;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("🎄 Generador de Villancicos Navideños 🎅")
    
    # Inicializar Suno
    suno = setup_suno()
    
    # Sidebar para navegación
    pagina = st.sidebar.radio(
        "Navegación",
        ["Crear Villancico", "Editar Letra", "Ver Resultado"]
    )
    
    # Inicializar variables de estado
    if 'letra' not in st.session_state:
        st.session_state.letra = ""
    if 'imagen_url' not in st.session_state:
        st.session_state.imagen_url = None
    if 'audio_url' not in st.session_state:
        st.session_state.audio_url = None
    
    if pagina == "Crear Villancico":
        st.header("✨ ¿Sobre qué quieres que vaya el villancico?")
        st.markdown("""
        Puedes escribir sobre cualquier tema navideño:
        - La estrella de Belén
        - Los Reyes Magos
        - El árbol de Navidad
        - La familia en Navidad
        Y mucho más...
        """)
        
        tema = st.text_input(
            "Escribe tu tema aquí",
            placeholder="Por ejemplo: la estrella de Belén, los regalos..."
        )
        
        if st.button("🎵 ¡Generar Villancico!"):
            with st.spinner("🎄 Componiendo tu villancico..."):
                st.session_state.letra = generar_letra(tema)
                st.success("¡Letra generada! Ve a 'Editar Letra' para revisarla.")
    
    elif pagina == "Editar Letra":
        if st.session_state.letra:
            st.header("✏️ Edita tu Villancico")
            st.session_state.letra = st.text_area(
                "Letra del Villancico",
                value=st.session_state.letra,
                height=300
            )
            
            if st.button("🎨 Confirmar y Generar Música e Imagen"):
                with st.spinner("🎵 Generando música e imagen..."):
                    # Generar imagen primero (más rápido)
                    st.session_state.imagen_url = generar_imagen(st.session_state.letra)
                    
                    # Generar música si Suno está configurado
                    if suno:
                        st.session_state.audio_url = suno.generate_music(st.session_state.letra)
                    
                st.success("¡Todo listo! Ve a 'Ver Resultado' para disfrutar tu villancico.")
        else:
            st.warning("⚠️ Primero genera un villancico en la página 'Crear Villancico'")
    
    elif pagina == "Ver Resultado":
        if st.session_state.letra and st.session_state.imagen_url:
            st.header("🎉 ¡Tu Villancico está Listo!")
            
            # Mostrar imagen
            st.image(st.session_state.imagen_url, caption="Ilustración del Villancico")
            
            # Mostrar letra
            st.markdown("### 📝 Letra del Villancico")
            st.markdown(st.session_state.letra)
            
            # Mostrar reproductor de audio si está disponible
            if st.session_state.audio_url:
                st.markdown("### 🎵 Música del Villancico")
                st.audio(st.session_state.audio_url, format='audio/mp3')
            
            # Opciones de guardado y compartir
            st.markdown("### 💾 Guardar y Compartir")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💾 Guardar en Dispositivo"):
                    # Implementar lógica de descarga
                    pass
            
            with col2:
                if st.button("📧 Enviar por Email"):
                    email = st.text_input("Ingresa tu email")
                    if email and st.button("Enviar"):
                        enviar_por_email(email, st.session_state.letra, 
                                       st.session_state.audio_url, 
                                       st.session_state.imagen_url)
            
            with col3:
                if st.button("🔄 Crear Nuevo Villancico"):
                    st.session_state.letra = ""
                    st.session_state.imagen_url = None
                    st.session_state.audio_url = None
                    st.experimental_rerun()
        else:
            st.warning("⚠️ Primero genera un villancico completo")

if __name__ == "__main__":
    main()