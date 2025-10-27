import streamlit as st
import json
import datetime
from enhanced_agent import EnhancedDentalAgent
from dental_knowledge import DentalKnowledgeBase

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {
        "name": "",
        "age": "",
        "phone": "",
        "email": "",
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }
if 'dental_agent' not in st.session_state:
    st.session_state.dental_agent = EnhancedDentalAgent()
if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = DentalKnowledgeBase()

# Streamlit app layout
def main():
    st.set_page_config(
        page_title="Assistente Odontológico Avançado",
        page_icon="🦷",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar
    render_sidebar()

    # Main area
    st.title("🦷 Assistente Odontológico Inteligente")
    st.markdown("""
    **Sistema avançado de anamnese odontológica com IA**
    Descreva seus sintomas para uma avaliação inicial personalizada.
    """)

    # Main tabs
    tab1, tab2, tab3 = st.tabs([
        "💬 Chat com IA",
        "🖼️ Análise de Imagens",
        "📊 Prontuário & Exportar"
    ])

    with tab1:
        render_chat_interface()

    with tab2:
        render_image_interface()

    with tab3:
        render_ehr_interface()

def render_sidebar():
    """Renderiza a sidebar"""
    with st.sidebar:
        st.header("👤 Dados do Paciente")

        st.session_state.patient_data["name"] = st.text_input(
            "Nome Completo",
            value=st.session_state.patient_data["name"],
            placeholder="Nome do paciente"
        )

        st.session_state.patient_data["age"] = st.text_input(
            "Idade",
            value=st.session_state.patient_data["age"],
            placeholder="Idade"
        )

        st.session_state.patient_data["phone"] = st.text_input(
            "Telefone",
            value=st.session_state.patient_data["phone"],
            placeholder="(00) 00000-0000"
        )

        st.session_state.patient_data["email"] = st.text_input(
            "Email",
            value=st.session_state.patient_data["email"],
            placeholder="seu@email.com"
        )

        st.divider()
        st.header("⚙️ Configurações da IA")

        # Model selection
        ai_mode = st.selectbox(
            "Modo de Operação:",
            ["IA Avançada", "Modo Base em Conhecimento"]
        )

        # Show detected symptoms
        if st.session_state.dental_agent.conversation_context["symptoms_detected"]:
            st.subheader("📋 Sintomas Detectados")
            for symptom in st.session_state.dental_agent.conversation_context["symptoms_detected"]:
                st.write(f"• {symptom.capitalize()}")

        st.divider()

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Nova Conversa", use_container_width=True):
                st.session_state.conversation = []
                st.session_state.dental_agent.reset_conversation()
                st.rerun()

        with col2:
            if st.button("💾 Exportar Dados", use_container_width=True):
                export_to_json()

def render_chat_interface():
    """Interface principal de chat com IA"""
    st.header("💬 Anamnese com Assistente IA")

    # Display conversation
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.conversation:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(f"**Paciente**: {message['content']}")
                    if message.get('timestamp'):
                        st.caption(f"({message['timestamp']})")
            else:
                with st.chat_message("assistant"):
                    st.write(f"**Assistente IA**: {message['content']}")
                    if message.get('timestamp'):
                        st.caption(f"({message['timestamp']})")

    # Quick symptom buttons
    st.subheader("🚨 Sintomas Comuns")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("😣 Dor", use_container_width=True):
            process_user_input("Estou sentindo dor nos dentes")

    with col2:
        if st.button("🩸 Sangramento", use_container_width=True):
            process_user_input("Minha gengiva está sangrando")

    with col3:
        if st.button("📈 Inchaço", use_container_width=True):
            process_user_input("Estou com inchaço na boca")

    with col4:
        if st.button("❄️ Sensibilidade", use_container_width=True):
            process_user_input("Estou com sensibilidade nos dentes")

    # Chat input
    user_input = st.chat_input("Descreva seus sintomas dentários...")

    if user_input:
        process_user_input(user_input)

def render_image_interface():
    """Interface de análise de imagens"""
    st.header("🖼️ Análise de Imagens Odontológicas")
    st.info("""
    **Em desenvolvimento**: Em breve você poderá fazer upload de radiografias
    e fotos intraorais para análise assistida por IA.
    """)

    uploaded_file = st.file_uploader(
        "Faça upload de imagens dentárias",
        type=['png', 'jpg', 'jpeg'],
        help="Radiografias ou fotos intraorais"
    )

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Imagem enviada", use_column_width=True)
        st.warning("🔬 Análise de imagens estará disponível em breve!")

def render_ehr_interface():
    """Interface do prontuário eletrônico"""
    st.header("📊 Prontuário Eletrônico")

    if st.session_state.conversation:
        # Summary section
        st.subheader("📋 Resumo da Anamnese")

        symptoms = st.session_state.dental_agent.conversation_context["symptoms_detected"]
        if symptoms:
            st.write("**Sintomas identificados:**")
            for symptom in symptoms:
                st.write(f"• {symptom.capitalize()}")

        # Export options
        st.subheader("📤 Exportar Dados")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Gerar Relatório PDF", use_container_width=True):
                st.info("📊 Exportação para PDF em desenvolvimento")

        with col2:
            if st.button("📊 Exportar JSON", use_container_width=True):
                export_to_json()

        # Conversation history
        st.subheader("🗣️ Histórico da Conversa")
        for i, message in enumerate(st.session_state.conversation):
            if message["role"] == "user":
                st.info(f"**Paciente**: {message['content']}")
            else:
                st.success(f"**Assistente**: {message['content']}")
    else:
        st.info("💬 Nenhuma conversa registrada. Use a aba de chat para iniciar a anamnese.")

def process_user_input(user_input):
    """Processa input do usuário e gera resposta com IA"""
    # Add user message
    st.session_state.conversation.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.datetime.now().strftime("%H:%M")
    })

    # Generate AI response
    with st.spinner("🤔 Analisando sintomas..."):
        response = st.session_state.dental_agent.generate_response(
            user_input,
            st.session_state.conversation
        )

    # Add AI response
    st.session_state.conversation.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.datetime.now().strftime("%H:%M")
    })

    st.rerun()

def export_to_json():
    """Exporta dados para JSON"""
    if not st.session_state.conversation:
        st.sidebar.error("Nenhuma conversa para exportar")
        return

    # Create comprehensive export data
    data_to_export = {
        "patient_info": st.session_state.patient_data,
        "medical_anamnesis": {
            "symptoms_detected": st.session_state.dental_agent.conversation_context["symptoms_detected"],
            "conversation_summary": f"Anamnese com {len(st.session_state.conversation)} mensagens",
            "urgency_assessment": st.session_state.knowledge_base.assess_urgency(
                st.session_state.dental_agent.conversation_context["symptoms_detected"],
                [msg['content'] for msg in st.session_state.conversation if msg['role'] == 'user']
            )
        },
        "conversation_history": st.session_state.conversation,
        "export_metadata": {
            "export_date": datetime.datetime.now().isoformat(),
            "total_messages": len(st.session_state.conversation),
            "patient_name": st.session_state.patient_data["name"]
        }
    }

    json_str = json.dumps(data_to_export, indent=2, ensure_ascii=False)

    # Download button
    st.sidebar.download_button(
        label="📥 Baixar Anamnese Completa (JSON)",
        data=json_str,
        file_name=f"anamnese_odontologica_{st.session_state.patient_data['name']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json"
    )

if __name__ == "__main__":
    main()