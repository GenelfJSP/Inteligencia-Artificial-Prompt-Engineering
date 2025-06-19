import streamlit as st
from dotenv import load_dotenv
import os
import requests
import re

# Configuración inicial
load_dotenv()
DEEPINFRA_TOKEN = os.getenv("DEEPINFRA_TOKEN")
st.set_page_config(page_title="🐭👨‍🍳🍲 Chefsit Guide", page_icon="🐭👨‍🍳🍲", layout="centered")

# --- Modelo a usar ---
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"  # Modelo potente y gratuito en DeepInfra

# --- Interfaz de Usuario ---
st.title("🐭👨‍🍳🍲 Chefsit Guide")

with st.sidebar:
    st.header("⚙️ Configuración")

    # Selector de idioma
    language = st.selectbox(
        "Idioma del menú",
        ["Español", "Inglés"],
        index=0
    )

    # Selector de dieta
    diet_type = st.selectbox(
        "Tipo de dieta",
        [
            "General",
            "Celíaca (sin gluten)",
            "Crudivegana",
            "Dieta detox",
            "Flexitariana",
            "Frutariana",
            "Halal",
            "Keto (cetogénica)",
            "Kosher",
            "Lacto-vegetariana",
            "Low FODMAP",
            "Macrobiótica",
            "Ovo-vegetariana",
            "Paleo",
            "Pescetariana",
            "Sin azúcar",
            "Sin lactosa",
            "Vegana",
            "Vegetariana"
        ],
        index=0
    )

    # Selector de comida
    meal_type = st.selectbox(
        "Tipo de comida",
        [
            "Desayuno",
            "Almuerzo", 
            "Merienda",
            "Cena",
            "Colación / Tentempié",
            "Picada",
            "Brunch",
            "Hora del té",
            "Aperitivo",
            "Postre",
            "Resopón"
        ],
        index=0
    )

    # Cantidad de días
    days = st.slider("Cantidad de días", 1, 7, 1)

    # Tiempo de preparación
    prep_time = st.slider("⏱️ Tiempo por comida (min)", 10, 120, 30)

# --- Función para llamar a la API de DeepInfra ---
def generar_menu_api(user_input, language):
    API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPINFRA_TOKEN}",
        "Content-Type": "application/json"
    }
    
    language_instruction = "Responde en español." if language == "Español" else "Respond in English."
    
    prompt = f"""Eres un chef experto en comida {diet_type.lower()}. {language_instruction}
    Genera un menú de {meal_type.lower()} para {days} día(s), con platos de hasta {prep_time} minutos.
    Usa estos ingredientes: {user_input.strip()}

    Formato de respuesta:
    ### Menú
    **Día 1**: [Nombre del plato] (~{prep_time}min)
    - Ingredientes: [lista]
    - Preparación: [pasos breves]"""

    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"🚨 Error: {str(e)}")
        if hasattr(response, 'status_code') and response.status_code == 429:
            st.warning("¡Límite temporal alcanzado! Espera 1 minuto.")
        return None

# --- Generación del Menú ---
user_input = st.text_area("🍽️ Ingredientes disponibles", placeholder="Ej: arroz, pollo, zanahoria...", height=100)

if st.button("✨ Generar Menú", type="primary"):
    if not user_input.strip():
        st.warning("⚠️ ¡Ingresá al menos un ingrediente!")
    else:
        with st.spinner(f"🧑‍🍳 Creando menú para {days} día(s)..."):
            menu = generar_menu_api(user_input, language)
            if menu:
                # Limpieza del output (elimina posibles artefactos)
                menu_limpio = re.sub(r'<\/?s>|\[INST\]|<<\/?SYS>>', '', menu)
                
                # Mostrar resultados
                with st.expander("🍽️ Menú Generado", expanded=True):
                    st.markdown(menu_limpio)

                # Botón de descarga
                file_lang = "es" if language == "Español" else "en"
                st.download_button(
                    "📥 Descargar Menú",
                    data=menu_limpio,
                    file_name=f"menu_{diet_type}_{days}dias_{file_lang}.txt",
                    mime="text/plain"
                )

# Footer
st.markdown("---")
st.caption(f"🐭👨‍🍳🍲 Chefsit Guide · Modelo: {MODEL_NAME} via DeepInfra 🤖")