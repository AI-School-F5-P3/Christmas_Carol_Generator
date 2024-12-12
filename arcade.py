import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import traceback

# Cargar variables de entorno
load_dotenv()

# Inicializar cliente de OpenAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
)

def generar_letra(tema):
    """Genera la letra del villancico usando OpenAI con instrucciones detalladas"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Modelo más reciente de 3.5
            messages=[
                {
                    "role": "system", 
                    "content": """
                    Eres un maestro compositor de villancicos navideños con más de 30 años de experiencia. 
                    Debes crear villancicos que:
                    - Tengan una estructura tradicional de villancico (estrofas y estribillo)
                    - Sean alegres y emotivos
                    - Usen lenguaje poético y navideño
                    - Tengan un ritmo musical suave y melodioso
                    - Incluyan referencias culturales navideñas
                    - No excedan las 4 estrofas y un estribillo
                    """
                },
                {
                    "role": "user", 
                    "content": f"Crea un villancico navideño profesional y emotivo sobre: {tema}. Quiero que tenga profundidad emocional y sea muy tradicional."
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error al generar la letra: {str(e)}")
        traceback.print_exc()
        return ""

def generar_imagen(descripcion):
    """Genera una imagen navideña usando DALL-E 3 con mayor precisión"""
    try:
        response = client.images.generate(
            prompt=f"""
            Imagen navideña profesional de alta calidad sobre: {descripcion}. 
            Estilo: Ilustración fotorrealista ultra detallada, 
            Iluminación: Cálida y acogedora, 
            Colores: Tradicionales navideños (rojos, verdes, dorados), 
            Calidad: 4K, 
            Detalles: Perfectos y nítidos
            """,
            n=1,
            size="1024x1024",
            model="dall-e-3",
            quality="hd"
        )
        return response.data[0].url
    except Exception as e:
        st.error(f"Error al generar imagen: {str(e)}")
        traceback.print_exc()
        return None

def main():
    st.set_page_config(
        page_title="Generador Mágico de Villancicos", 
        page_icon="🎄", 
        layout="centered"
    )
    
    st.title("🎄 Generador Profesional de Villancicos Navideños 🎅")
    st.markdown("*Crea villancicos únicos y mágicos con inteligencia artificial*")
    
    # Estilos personalizados
    st.markdown("""
    <style>
    .stButton > button {
        background-color: #FF4500;
        color: white;
        font-weight: bold;
    }
    .stTextInput > div > div > input {
        border: 2px solid #228B22;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Input con ejemplos sugeridos
    temas_ejemplo = [
        "El árbol de Navidad", 
        "Familia reunida en Nochebuena", 
        "Paz y esperanza", 
        "Amor en Navidad"
    ]
    tema = st.selectbox(
        "Elige un tema para tu villancico", 
        temas_ejemplo, 
        index=0
    )
    tema_personalizado = st.text_input(
        "O escribe tu propio tema", 
        placeholder="Tema personalizado aquí"
    )
    
    # Usar tema personalizado si se proporciona
    tema_final = tema_personalizado if tema_personalizado else tema
    
    if st.button("🎵 Generar Villancico Mágico"):
        col1, col2 = st.columns(2)
        
        with col1:
            with st.spinner("✨ Creando letra mágica..."):
                letra = generar_letra(tema_final)
                if letra:
                    st.session_state["letra"] = letra
                    st.markdown("### 🎼 Letra del Villancico")
                    st.text_area("Letra generada", letra, height=300)
                else:
                    st.warning("No se pudo generar la letra.")
        
        with col2:
            with st.spinner("🖌 Pintando imagen navideña..."):
                imagen_url = generar_imagen(tema_final)
                if imagen_url:
                    st.session_state["imagen_url"] = imagen_url
                    st.image(imagen_url, caption="Ilustración navideña AI", use_column_width=True)
                else:
                    st.warning("No se pudo generar la imagen.")

    # Pie de página decorativo
    st.markdown("""
    ---
    *Creado con ✨ magia navideña y 🤖 inteligencia artificial*
    """)

if __name__ == "__main__":
    main()