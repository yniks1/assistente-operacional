import os
import google.generativeai as genai
from dotenv import load_dotenv
import warnings

warnings.filterwarnings("ignore") # Esconde aquele aviso de atualização

load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

print("🔍 Buscando modelos de Texto (Chat) suportados...\n")

for m in genai.list_models():
    # Agora estamos filtrando por 'generateContent' (geração de texto)
    if 'generateContent' in m.supported_generation_methods:
        print(f"Nome: {m.name}")
        print("-" * 40)