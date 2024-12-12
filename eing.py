import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

url = os.getenv("OPENAI_API_BASE") + "/models"
headers = {
    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("✅ Conexión exitosa. Modelos disponibles:")
    print(response.json())
else:
    print(f"❌ Error: {response.status_code}")
    print(response.json())
    