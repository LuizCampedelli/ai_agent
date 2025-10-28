import streamlit as st
import json
import datetime
from dental_crew_gemini import DentalCrewAIGemini
from config import config

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {
        "name": "", "age": "", "phone": "", "email": "",
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }
if 'dental_crew' not in st.session_state:
    st.session_state.dental_crew = DentalCrewAIGemini()
if 'symptom_analysis' not in st.session_state:
    st.session_state.symptom_analysis = {}

def main():
    st.set_page_config(
        page_title="Assistente Dental com Gemini AI",
        page_icon="🦷",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    render_sidebar()
    render_main_content()

def render_sidebar():
    with st.sidebar:
        st.header("👤 Dados do Paciente")

        st.session_state.patient_data["name"] = st.text_input(
            "Nome Completo",
            value=st.session_state.patient_data["name"]
        )

        st.session_state.patient_data["age"] = st.text_input(
            "Idade",
            value=st.session_state.patient_data["age"]
        )

        st.divider()
        st.header("🤖 Configuração AI")

        # Show Gemini status
        if st.session_state.dental_crew.gemini_available:
            st.success("✅ Google Gemini Conectado")
            st.info(f"Modelo: {config.google_model}")
        else:
            st.warning("⚡ Modo Básico (Sem Gemini)")
            st.info("Adicione GOOGLE_API_KEY no .env para ativar Gemini")

        # Available features
        features = []
        if st.session_state.dental_crew.gemini_available:
            features.append("Conversas em Português")
            features.append("Análise Avançada")
        features.append("Anamnese Inteligente")

        st.write("**Recursos:**", ", ".join(features))

        st.divider()

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Nova Conversa", use_container_width=True):
                st.session_state.conversation = []
                st.rerun()

        with col2:
            if st.button("💾 Exportar", use_container_width=True):
                export_to_json()

def render_main_content():
    st.title("🦷 Assistente Dental com Google Gemini")

    if st.session_state.dental_crew.gemini_available:
        st.success("**Gemini AI Ativo** - Conversas naturais em português")
    else:
        st.info("**Modo Básico** - Adicone uma chave do Google Gemini para conversas mais naturais")

    st.markdown("Descreva seus sintomas dentários para uma avaliação inicial com IA.")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat com Gemini", "📋 Análise", "📊 Exportar"])

    with tab1:
        render_chat_interface()

    with tab2:
        render_analysis_interface()

    with tab3:
        render_export_interface()

def render_chat_interface():
    st.header("💬 Anamnese com Gemini AI")

    # Display conversation
    for message in st.session_state.conversation:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(f"**Paciente**: {message['content']}")
        else:
            with st.chat_message("assistant"):
                st.write(f"**Assistente**: {message['content']}")
                if st.session_state.dental_crew.gemini_available:
                    st.caption("🤖 Powered by Google Gemini")

    # Quick actions
    st.subheader("🚨 Sintomas Rápidos")
    cols = st.columns(4)

    symptoms = [
        ("😣 Dor Dental", "Estou com dor no dente"),
        ("🩸 Sangramento", "Minha gengiva está sangrando"),
        ("📈 Inchaço", "Estou com inchaço na boca"),
        ("❄️ Sensibilidade", "Meus dentes estão sensíveis")
    ]

    for col, (label, text) in zip(cols, symptoms):
        with col:
            if st.button(label, use_container_width=True):
                process_user_input(text)

    # Chat input
    user_input = st.chat_input("Descreva seus sintomas em português...")

    if user_input:
        process_user_input(user_input)

def render_analysis_interface():
    st.header("📋 Análise de Sintomas")

    if st.session_state.conversation:
        st.success(f"✅ {len(st.session_state.conversation)} mensagens analisadas")

        # Simple symptom detection
        symptoms = detect_symptoms_from_conversation()
        if symptoms:
            st.subheader("Sintomas Detectados")
            for symptom in symptoms:
                st.write(f"• {symptom}")

        # Analysis button
        if st.button("🧠 Análise Profunda com Gemini"):
            with st.spinner("Gemini analisando o caso..."):
                analysis = st.session_state.dental_crew.analyze_with_gemini_direct(
                    f"Analise esta conversa dental e forneça insights: {st.session_state.conversation}"
                )
            st.write(analysis)
    else:
        st.info("💬 Inicie uma conversa para ver a análise")

def render_export_interface():
    st.header("📊 Exportar Dados")

    if st.session_state.conversation:
        st.download_button(
            label="📥 Baixar Conversa (JSON)",
            data=json.dumps({
                "patient": st.session_state.patient_data,
                "conversation": st.session_state.conversation,
                "ai_system": "Google Gemini" if st.session_state.dental_crew.gemini_available else "CrewAI Basic"
            }, indent=2, ensure_ascii=False),
            file_name=f"anamnese_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )

        # Conversation preview
        st.subheader("Visualização da Conversa")
        for msg in st.session_state.conversation:
            st.text(f"{msg['role']}: {msg['content']}")
    else:
        st.info("Nenhuma conversa para exportar")

def process_user_input(user_input):
    """Process user input with Gemini-powered crew"""
    st.session_state.conversation.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })

    with st.spinner("🤔 Gemini analisando sua mensagem..."):
        response = st.session_state.dental_crew.conduct_anamnesis(
            user_input,
            st.session_state.conversation
        )

    st.session_state.conversation.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })

    st.rerun()

def detect_symptoms_from_conversation():
    """Detect symptoms from conversation"""
    symptoms = set()
    for message in st.session_state.conversation:
        content = message['content'].lower()
        if any(word in content for word in ['dor', 'dói']):
            symptoms.add('Dor')
        if any(word in content for word in ['sangramento', 'sangra']):
            symptoms.add('Sangramento')
        if any(word in content for word in ['inchaço', 'inchado']):
            symptoms.add('Inchaço')
        if any(word in content for word in ['sensibilidade', 'sensível']):
            symptoms.add('Sensibilidade')
    return symptoms

def export_to_json():
    """Export conversation to JSON"""
    # Implementation similar to previous versions

if __name__ == "__main__":
    main()