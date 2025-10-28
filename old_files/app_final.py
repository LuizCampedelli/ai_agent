import streamlit as st
import json
import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DentalGeminiAssistant:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Use a model that's available
                self.model = genai.GenerativeModel('gemini-pro')
                self.available = True
                st.success("✅ Gemini AI Connected!")
            except Exception as e:
                st.error(f"❌ Gemini setup failed: {e}")
                self.available = False
        else:
            self.available = False
            st.warning("⚠️ Add GOOGLE_API_KEY to .env for AI features")

    def chat(self, user_input, conversation_history):
        if not self.available:
            return self._fallback_response(user_input)

        try:
            # Build context from conversation
            context = self._build_context(conversation_history)

            prompt = f"""
            Você é um assistente dental profissional brasileiro. Sua função é conduzir anamnese odontológica (entrevista para entender sintomas dentários).

            INSTRUÇÕES:
            - Responda SEMPRE em português brasileiro
            - Seja empático e profissional
            - Faça perguntas relevantes sobre os sintomas
            - Ajude a identificar a urgência do caso
            - Não dê diagnósticos definitivos
            - Mantenha a conversa natural

            HISTÓRICO DA CONVERSA:
            {context}

            PACIENTE: {user_input}

            ASSISTENTE DENTAL (responda em português):
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            st.error(f"🤖 AI Error: {e}")
            return self._fallback_response(user_input)

    def _build_context(self, conversation_history):
        if not conversation_history:
            return "Primeira mensagem do paciente."

        context_lines = []
        for msg in conversation_history[-8:]:  # Last 8 messages
            if msg["role"] == "user":
                context_lines.append(f"Paciente: {msg['content']}")
            else:
                context_lines.append(f"Assistente: {msg['content']}")

        return "\n".join(context_lines)

    def _fallback_response(self, user_input):
        user_input_lower = user_input.lower()

        # Smart fallback responses in Portuguese
        if any(word in user_input_lower for word in ['oi', 'olá', 'hello', 'hi']):
            return "Olá! Sou seu assistente virtual para anamnese odontológica. Por favor, descreva o que está sentindo."

        elif any(word in user_input_lower for word in ['dor', 'dói', 'dolorido']):
            return "Entendo que você está sentindo dor. Pode me dizer onde exatamente está localizada a dor? É constante ou vem e vai?"

        elif any(word in user_input_lower for word in ['sangramento', 'sangra']):
            return "Obrigado por mencionar o sangramento. Isso acontece durante a escovação ou espontaneamente? Há quanto tempo nota isso?"

        elif any(word in user_input_lower for word in ['inchaço', 'inchado']):
            return "Vejo que você tem inchaço. Onde está localizado? Há quanto tempo notou e está aumentando?"

        elif any(word in user_input_lower for word in ['sensibilidade', 'sensível']):
            return "Entendo sobre a sensibilidade. É ao frio, ao quente, a doces ou à pressão?"

        elif any(word in user_input_lower for word in ['obrigado', 'agradeço']):
            return "De nada! Estou aqui para ajudar. Posso auxiliar com mais alguma preocupação odontológica?"

        else:
            return "Obrigado pela informação. Pode me contar mais detalhes sobre seus sintomas ou preocupações odontológicas?"

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {
        "name": "", "age": "", "phone": "", "email": "",
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }
if 'assistant' not in st.session_state:
    st.session_state.assistant = DentalGeminiAssistant()

def main():
    st.set_page_config(
        page_title="Assistente Dental AI",
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
            value=st.session_state.patient_data["name"],
            placeholder="Seu nome completo"
        )

        st.session_state.patient_data["age"] = st.text_input(
            "Idade",
            value=st.session_state.patient_data["age"],
            placeholder="Sua idade"
        )

        st.session_state.patient_data["phone"] = st.text_input(
            "Telefone",
            value=st.session_state.patient_data["phone"],
            placeholder="(00) 00000-0000"
        )

        st.divider()
        st.header("⚙️ Configurações")

        # AI Status
        if st.session_state.assistant.available:
            st.success("✅ Gemini AI Ativo")
            st.caption("Conversas naturais em português")
        else:
            st.warning("⚡ Modo Básico")
            st.caption("Adicione GOOGLE_API_KEY para IA avançada")

        st.divider()

        # Quick actions
        if st.button("🔄 Nova Conversa", use_container_width=True):
            st.session_state.conversation = []
            st.rerun()

        if st.button("💾 Exportar Dados", use_container_width=True):
            export_to_json()

def render_main_content():
    st.title("🦷 Assistente de Saúde Dental")
    st.markdown("""
    **Sistema inteligente de anamnese odontológica**
    Descreva seus sintomas para uma avaliação inicial com IA.
    """)

    # Tabs
    tab1, tab2 = st.tabs(["💬 Chat com IA", "📊 Prontuário"])

    with tab1:
        render_chat_interface()

    with tab2:
        render_medical_records()

def render_chat_interface():
    st.header("💬 Anamnese Dental")

    # Display conversation
    for message in st.session_state.conversation:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(f"**Você**: {message['content']}")
                if message.get('timestamp'):
                    st.caption(f"({message['timestamp']})")
        else:
            with st.chat_message("assistant"):
                st.write(f"**Assistente**: {message['content']}")
                if message.get('timestamp'):
                    st.caption(f"({message['timestamp']})")
                if st.session_state.assistant.available:
                    st.caption("🤖 Powered by Google Gemini")

    # Quick symptom buttons
    st.subheader("🚨 Sintomas Comuns")
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

def render_medical_records():
    st.header("📊 Prontuário Médico")

    if st.session_state.conversation:
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mensagens", len(st.session_state.conversation))
        with col2:
            st.metric("Paciente", st.session_state.patient_data["name"] or "Não informado")
        with col3:
            ai_status = "Gemini" if st.session_state.assistant.available else "Básico"
            st.metric("Sistema", ai_status)

        # Export
        st.download_button(
            "📥 Baixar Anamnese (JSON)",
            data=json.dumps({
                "patient_info": st.session_state.patient_data,
                "conversation": st.session_state.conversation,
                "export_date": datetime.datetime.now().isoformat(),
                "ai_system": "Google Gemini" if st.session_state.assistant.available else "Basic"
            }, indent=2, ensure_ascii=False),
            file_name=f"anamnese_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )

        # Conversation preview
        st.subheader("Histórico da Conversa")
        for i, msg in enumerate(st.session_state.conversation):
            if msg["role"] == "user":
                st.info(f"**Paciente**: {msg['content']}")
            else:
                st.success(f"**Assistente**: {msg['content']}")
    else:
        st.info("💬 Nenhuma conversa registrada. Use a aba de chat para começar.")

def process_user_input(user_input):
    """Process user input with AI"""
    # Add user message
    st.session_state.conversation.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.datetime.now().strftime("%H:%M")
    })

    # Get AI response
    with st.spinner("🤔 Analisando..."):
        response = st.session_state.assistant.chat(
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
    """Export data to JSON"""
    if not st.session_state.conversation:
        st.sidebar.error("Nenhuma conversa para exportar")
        return

    st.sidebar.success("Use o botão de download na aba 📊 Prontuário")

if __name__ == "__main__":
    main()