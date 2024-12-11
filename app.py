import os
import streamlit as st
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv
import requests
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Configurar página de Streamlit
st.set_page_config(
    page_title="Generador de Villancicos Navideños",
    page_icon="🎄",
    layout="wide"
)

# Inicializar cliente de Azure OpenAI
try:
    client = AzureOpenAI(
        azure_endpoint=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY"),
        api_version="2024-02-01"
    )

    client2 = AzureOpenAI(
        azure_endpoint=os.getenv("OPENAI_API_BASE_2"),
        api_key=os.getenv("OPENAI_API_KEY_2"),
        api_version="2024-02-01"
    )

    openai_client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY_DALLE")
    )
except Exception as e:
    st.error("Error al inicializar los clientes de Azure OpenAI. Verifica las variables de entorno.")
    logger.error(f"Error al inicializar los clientes: {e}")


def generar_letra_villancico(prompt, nombre_nino=None, edad_nino=None):
    """Generar letras de villancicos usando ChatGPT"""
    try:
        if nombre_nino and edad_nino:
            prompt_completo = f"""Crea un villancico navide\u00f1o sobre {prompt} para un ni\u00f1o llamado {nombre_nino}, de {edad_nino} a\u00f1os. 
            Haz la letra divertida, entretenida y apropiada para un ni\u00f1o. Incluye el nombre del ni\u00f1o en el villancico si es posible."""
        else:
            prompt_completo = f"Crea un villancico navide\u00f1o sobre {prompt}"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un experto en crear villancicos navide\u00f1os infantiles divertidos y creativos."},
                {"role": "user", "content": prompt_completo}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error al generar la letra del villancico: {e}")
        logger.error(f"Error en generar_letra_villancico: {e}")
        return None


def generar_imagen_villancico(prompt):
    """Generar una imagen navide\u00f1a usando DALL-E"""
    try:
        logger.info(f"Generando imagen con prompt: {prompt}")

        response = client2.images.generate(
            model="dall-e-3",
            prompt=f"Ilustraci\u00f3n m\u00e1gica navide\u00f1a de {prompt}, alegre, colorida, estilo amigable para ni\u00f1os",
            n=1,
            size="1024x1024"
        )

        imagen_url = response.data[0].url
        logger.info(f"URL de imagen generada: {imagen_url}")
        return imagen_url
    except Exception as e:
        st.error(f"Error al generar la imagen del villancico: {e}")
        logger.error(f"Error en generar_imagen_villancico: {e}")
        return None


def main():
    st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .title {
        color: #c41e3a;
        text-align: center;
        font-size: 3em;
    }
    .stButton>button {
        background-color: #c41e3a;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("🎄 Modos de Generación de Villancicos")
    modo = st.sidebar.radio("Elige un modo de generación", ["Modo Simple", "Modo Personalizado de Santa"])

    st.markdown("<h1 class='title'>🎄 Creador de Villancicos Navideños 🎅</h1>", unsafe_allow_html=True)

    if modo == "Modo Simple":
        st.write("## ¿Sobre qué será tu villancico? 🎵")
        tema_villancico = st.text_input("Ingresa un tema o asunto para tu villancico")
        nombre_nino, edad_nino = None, None
    else:
        st.write("## Taller Personalizado de Villancicos de Santa 🎅")
        nombre_nino = st.text_input("¿Cuál es tu nombre?")
        edad_nino = st.number_input("¿Cuántos años tienes?", min_value=1, max_value=12, step=1)
        tema_villancico = st.text_input("¿Sobre qué te gustaría que sea tu villancico?")

    if st.button("✨ ¡Crea Mi Villancico Navideño!"):
        if tema_villancico:
            with st.spinner("Magia en progreso... 🎄✨"):
                letra = generar_letra_villancico(tema_villancico, nombre_nino, edad_nino)

                if letra:
                    st.write("### 🎵 Tu Villancico Mágico:")
                    st.write(letra)

                    imagen_villancico = generar_imagen_villancico(tema_villancico)

                    if imagen_villancico:
                        st.write("### 🖼️ Ilustración del Villancico:")
                        st.image(imagen_villancico, caption="Tu Ilustración Navideña Mágica", width=700)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="📝 Descargar Letra",
                                data=letra,
                                file_name="villancico_navidad.txt",
                                mime="text/plain"
                            )

                        with col2:
                            st.download_button(
                                label="🖼️ Descargar Ilustración",
                                data=requests.get(imagen_villancico).content,
                                file_name="ilustracion_villancico.png",
                                mime="image/png"
                            )
        else:
            st.warning("Por favor, ingresa un tema para tu villancico.")

    st.sidebar.write("## 🎵 Reproducir Villancico")
    try:
        with open("Los Cinco Estudiantes_ Un Villancico Navideño.mp3", "rb") as audio_file:
            st.sidebar.audio(audio_file.read(), format="audio/mp3")
    except FileNotFoundError:
        st.sidebar.error("Archivo de audio no encontrado.")


if __name__ == "__main__":
    main()
