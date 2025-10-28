import streamlit as st
import json
import datetime

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

# Simple dental agent class
class SimpleDentalAgent:
    def __init__(self):
        self.knowledge_base = {
            "pain": ["location", "intensity", "duration"],
            "bleeding": ["when", "how_much", "triggers"],
            "swelling": ["location", "size", "duration"]
        }

    def generate_response(self, user_input):
        user_input_lower = user_input.lower()

        # Basic response logic
        if any(word in user_input_lower for word in ["hello", "hi", "olá", "oi"]):
            return "Olá! Sou seu assistente odontológico. Por favor, descreva suas preocupações dentárias."

        elif any(word in user_input_lower for word in ["pain", "hurt", "dor", "dói"]):
            return "Entendo que você está sentindo dor. Pode me dizer onde exatamente a dor está localizada e qual a intensidade?"

        elif any(word in user_input_lower for word in ["bleeding", "sangramento", "sangra"]):
            return "Obrigado por mencionar o sangramento. Isso acontece durante a escovação ou espontaneamente? Há quanto tempo ocorre?"

        elif any(word in user_input_lower for word in ["swelling", "inchaço", "inchado"]):
            return "Vejo que você tem inchaço. Onde está localizado e há quanto tempo notou isso?"

        elif any(word in user_input_lower for word in ["sensibilidade", "sensível"]):
            return "Entendo sobre a sensibilidade. É ao frio, ao quente ou a doces?"

        else:
            return "Obrigado pela informação. Pode me contar mais sobre suas preocupações ou sintomas odontológicos?"

# Create agent instance
agent = SimpleDentalAgent()

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

    # Área principal
    st.title("🦷 Assistente Odontológico Inteligente")
    st.markdown("""
    Sistema avançado de anamnese odontológica. Descreva seus sintomas e eu ajudarei a avaliar sua situação.
    """)

    # Abas principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Chat Principal",
        "🎤 Entrada por Voz",
        "🖼️ Análise de Imagens",
        "📊 Prontuário"
    ])

    with tab1:
        render_chat_interface()

    with tab2:
        render_voice_interface()

    with tab3:
        render_image_interface()

    with tab4:
        render_ehr_interface()

def render_sidebar():
    """Renderiza a sidebar"""
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
        st.session_state.patient_data["phone"] = st.text_input(
            "Telefone",
            value=st.session_state.patient_data["phone"]
        )
        st.session_state.patient_data["email"] = st.text_input(
            "Email",
            value=st.session_state.patient_data["email"]
        )

        st.divider()
        st.header("⚙️ Configurações")

        # Seleção de modelo
        model_option = st.selectbox(
            "Modelo de IA:",
            ["LLaMA (Local)", "Transformers", "Mistral", "Fallback"]
        )

        # Configurações de voz
        voice_enabled = st.checkbox("Ativar reconhecimento de voz")

        st.divider()

        # Botões de ação
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Nova Conversa"):
                st.session_state.conversation = []
                st.rerun()

        with col2:
            if st.button("💾 Salvar Prontuário"):
                save_current_session()

def render_chat_interface():
    """Interface principal de chat"""
    st.header("💬 Conversa com o Assistente")

    # Display conversation
    for message in st.session_state.conversation:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(f"**Você**: {message['content']}")
        else:
            with st.chat_message("assistant"):
                st.write(f"**Assistente**: {message['content']}")

    # Chat input at the bottom
    user_input = st.chat_input("Descreva seus sintomas dentários...")

    if user_input:
        process_user_input(user_input)

def render_voice_interface():
    """Interface de entrada por voz"""
    st.header("🎤 Entrada por Voz")
    st.markdown("Funcionalidade de voz em desenvolvimento. Use a aba de chat para digitar.")

    if st.button("🎤 Iniciar Gravação", type="primary"):
        st.info("Sistema de voz em desenvolvimento. Use a aba de chat para digitar.")

def render_image_interface():
    """Interface de análise de imagens"""
    st.header("🖼️ Análise de Imagens Odontológicas")
    st.markdown("""
    Faça upload de radiografias ou fotos intraorais para análise assistida por IA.
    """)

    uploaded_file = st.file_uploader(
        "Escolha uma imagem",
        type=['png', 'jpg', 'jpeg'],
        help="Radiografias ou fotos intraorais"
    )

    if uploaded_file is not None:
        col1, col2 = st.columns(2)

        with col1:
            st.image(uploaded_file, caption="Imagem Uploadada", use_column_width=True)

        with col2:
            if st.button("🔍 Analisar Imagem"):
                st.info("Sistema de análise de imagens em desenvolvimento.")

def render_ehr_interface():
    """Interface do prontuário eletrônico"""
    st.header("📊 Prontuário Eletrônico")

    tab1, tab2 = st.tabs(["Exportar Dados", "Histórico"])

    with tab1:
        st.subheader("Exportar Consulta Atual")

        if st.session_state.get('conversation'):
            col1, col2 = st.columns(2)

            with col1:
                if st.button("📄 Exportar para PDF"):
                    st.info("Exportação para PDF em desenvolvimento")

            with col2:
                if st.button("📊 Exportar para JSON"):
                    export_to_json()
        else:
            st.info("Nenhuma conversa para exportar.")

    with tab2:
        st.subheader("Histórico de Consultas")
        st.info("Funcionalidade em desenvolvimento...")

def process_user_input(user_input):
    """Processa input do usuário e gera resposta"""
    # Add user message to conversation
    st.session_state.conversation.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.datetime.now().strftime("%H:%M")
    })

    # Generate and add assistant response
    with st.spinner("Pensando..."):
        response = agent.generate_response(user_input)

    st.session_state.conversation.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.datetime.now().strftime("%H:%M")
    })

    st.rerun()

def save_current_session():
    """Salva a sessão atual"""
    st.sidebar.success("Dados salvos localmente!")

def export_to_json():
    """Exporta para JSON"""
    if not st.session_state.conversation:
        st.error("Nenhuma conversa para exportar.")
        return

    data_to_export = {
        "patient_data": st.session_state.patient_data,
        "conversation": st.session_state.conversation,
        "export_date": datetime.datetime.now().isoformat()
    }

    json_str = json.dumps(data_to_export, indent=2, ensure_ascii=False)

    st.download_button(
        label="📥 Baixar JSON",
        data=json_str,
        file_name=f"anamnese_{st.session_state.patient_data['name']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json"
    )

if __name__ == "__main__":
    main()