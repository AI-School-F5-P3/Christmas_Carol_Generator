import os
import streamlit as st
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv
import requests
import magenta.music as mm
from magenta.protobuf import music_pb2

# Cargar variables de entorno
load_dotenv()

# Configurar página de Streamlit
st.set_page_config(
    page_title="Generador de Villancicos Navideños",
    page_icon="🎄",
    layout="wide"
)

# Inicializar cliente de Azure OpenAI
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

# Inicializar cliente de OpenAI para generación de imágenes
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY_DALLE")
)

def generar_letra_villancico(prompt, nombre_nino=None, edad_nino=None):
    """Generar letras de villancicos usando ChatGPT"""
    try:
        if nombre_nino and edad_nino:
            prompt_completo = f"""Crea un villancico navideño sobre {prompt} para un niño llamado {nombre_nino}, de {edad_nino} años. 
            Haz la letra divertida, entretenida y apropiada para un niño. Incluye el nombre del niño en el villancico si es posible."""
        else:
            prompt_completo = f"Crea un villancico navideño sobre {prompt}"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un experto en crear villancicos navideños infantiles divertidos y creativos."},
                {"role": "user", "content": prompt_completo}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error al generar la letra del villancico: {e}")
        return None

def generar_imagen_villancico(prompt):
    """Generar una imagen navideña usando DALL-E"""
    try:
        st.write("Generando imagen con prompt:", prompt)
        st.write("Endpoint de Azure:", os.getenv("OPENAI_API_BASE"))
        st.write("Versión de API:", os.getenv("API_VERSION"))
        
        response = client2.images.generate(
            model="dall-e-3",
            prompt=f"Ilustración mágica navideña de {prompt}, alegre, colorida, estilo amigable para niños",
            n=1,
            size="1024x1024"
        )
        
        st.write("Respuesta de imagen:", response)
        imagen_url = response.data[0].url
        return imagen_url
    except Exception as e:
        st.error(f"Error al generar la imagen del villancico: {e}")
        st.error(f"Detalles del error: {str(e)}")
        return None

def generar_musica_navideña(letra):
    try:
        # Crear una melodía simple sin modelo pre-entrenado
        notes = [60, 62, 64, 65, 67, 69, 71, 72]  # Escala de Do mayor
        times = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
        durations = [0.5] * len(notes)
        
        # Crear secuencia MIDI
        sequence = music_pb2.NoteSequence()
        for note, time, duration in zip(notes, times, durations):
            sequence.notes.add(
                pitch=note,
                start_time=time,
                end_time=time + duration,
                velocity=80
            )
        sequence.total_time = max(times) + 0.5

        # Guardar como MIDI
        midi_filename = 'musica_navideña.mid'
        mm.sequence_proto_to_midi_file(sequence, midi_filename)
        
        return midi_filename
    except Exception as e:
        st.error(f"Error al generar la música: {e}")
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
    modo = st.sidebar.radio("Elige un modo de generación", 
        ["Modo Simple", "Modo Personalizado de Santa"]
    )

    st.markdown("<h1 class='title'>🎄 Creador de Villancicos Navideños 🎅</h1>", unsafe_allow_html=True)

    if modo == "Modo Simple":
        st.write("## ¿Sobre qué será tu villancico? 🎵")
        tema_villancico = st.text_input("Ingresa un tema o asunto para tu villancico")
        nombre_nino = None
        edad_nino = None
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
                        st.image(imagen_villancico, caption="Tu Ilustración Navideña Mágica", width=500)

                    # Generar Música
                    midi_filename = generar_musica_navideña(letra)
                    if midi_filename:
                        st.write("### 🎵 Melodía del Villancico:")
                        audio_file = open(midi_filename, 'rb')
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format='audio/midi')

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.download_button(
                            label="📝 Descargar Letra",
                            data=letra,
                            file_name="villancico_navidad.txt",
                            mime="text/plain"
                        )
                    
                    with col2:
                        if imagen_villancico:
                            st.download_button(
                                label="🖼️ Descargar Ilustración",
                                data=requests.get(imagen_villancico).content,
                                file_name="ilustracion_villancico.png",
                                mime="image/png"
                            )
                    
                    with col3:
                        if midi_filename:
                            with open(midi_filename, 'rb') as f:
                                st.download_button(
                                    label="🎵 Descargar Música",
                                    data=f.read(),
                                    file_name="villancico_navidad.mid",
                                    mime="audio/midi"
                                )
        else:
            st.warning("Por favor, ingresa un tema para tu villancico.")

if __name__ == "__main__":
    main()