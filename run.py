#!/usr/bin/env python3
import subprocess
import sys
import os

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    try:
        import streamlit
        import transformers
        import torch
        print("✅ Todas as dependências estão instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        return False

def main():
    print("🦷 Inicializando Assistente de Anamnese Odontológica...")

    if not check_dependencies():
        print("Instalando dependências...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    print("Abrindo interface web...")
    os.system("streamlit run app.py")

if __name__ == "__main__":
    main()
