import streamlit as st
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
import openai

# Cargar variables de entorno
load_dotenv()

# Set OpenAI API settings for Azure
openai.api_type = "azure"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE")

# Configuración de APIs
client_text = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version="2023-05-15",
    azure_endpoint=os.getenv("OPENAI_API_BASE")
)

client_image = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY_2"),
    api_version="2023-05-15",
    azure_endpoint=os.getenv("OPENAI_API_BASE_2")
)

# Funciones auxiliares
def generar_letra(tema):
    try:
        response = client_text.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un experto compositor de villancicos navideños en español."},
                {"role": "user", "content": f"Crea un villancico navideño sobre: {tema}. Debe tener estrofas y un estribillo pegadizo."}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error al generar la letra: {e}")
        return ""

def generar_imagen(descripcion):
    try:
        response = client_image.images.generate(
            model="dall-e-3",
            prompt=f"Ilustración navideña para un villancico sobre: {descripcion}. Estilo alegre y festivo.",
            size="1024x1024",
            quality="standard",
            n=1
        )
        return response.data[0].url
    except Exception as e:
        st.error(f"Error al generar la imagen: {e}")
        return None

def enviar_por_email(email, letra, audio_url, imagen_url):
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
    body {
        color: #333;
        background-color: #f0f0f0;
    }
    .stButton>button {
        background-color: #c41e3a;
        color: white;
        border-radius: 20px;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #9e1a2d;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
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
    .sidebar .sidebar-content {
        background-color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🎄 Generador de Villancicos Navideños 🎅")

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
            if st.button("🎨 Confirmar y Generar Imagen"):
                with st.spinner("🎨 Generando imagen..."):
                    st.session_state.imagen_url = generar_imagen(st.session_state.letra[:100])
                st.success("¡Imagen generada! Ve a 'Ver Resultado' para disfrutar tu villancico.")
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
            
            # Opciones de guardado y compartir
            st.markdown("### 💾 Guardar y Compartir")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Descargar Letra"):
                    b64 = base64.b64encode(st.session_state.letra.encode()).decode()
                    href = f'<a href="data:file/txt;base64,{b64}" download="villancico.txt">Descargar Letra</a>'
                    st.markdown(href, unsafe_allow_html=True)
            with col2:
                if st.button("🔄 Crear Nuevo Villancico"):
                    st.session_state.letra = ""
                    st.session_state.imagen_url = None
                    st.experimental_rerun()
        else:
            st.warning("⚠️ Primero genera un villancico completo")

if __name__ == "__main__":
    main()
