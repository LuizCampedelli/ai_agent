import streamlit as st
import json
import datetime
import requests

# Dental Knowledge Base Class
class DentalKnowledgeBase:
    def __init__(self):
        self.symptoms_categories = {
            "dor": {
                "questions": [
                    "Onde exatamente você sente a dor?",
                    "A dor é constante ou vem e vai?",
                    "Qual a intensidade da dor (escala de 1 a 10)?",
                    "A dor piora com algo específico?",
                    "Há quanto tempo sente esta dor?"
                ],
                "keywords": ["dor", "dói", "dolorido", "latejando", "ardendo"]
            },
            "sangramento": {
                "questions": [
                    "O sangramento ocorre durante a escovação ou espontaneamente?",
                    "Há quanto tempo nota o sangramento?",
                    "O sangramento é abundante ou apenas manchas na escova?",
                    "A gengiva está inchada ou dolorida?"
                ],
                "keywords": ["sangramento", "sangra", "sangue", "hemorragia"]
            },
            "inchaço": {
                "questions": [
                    "Onde está localizado o inchaço?",
                    "Há quanto tempo notou o inchaço?",
                    "O inchaço está aumentando?",
                    "Há dor associada ao inchaço?",
                    "Há febre ou mal-estar?"
                ],
                "keywords": ["inchaço", "inchado", "inchar", "caroço"]
            },
            "sensibilidade": {
                "questions": [
                    "A sensibilidade é ao frio, ao quente ou a doces?",
                    "Quais dentes são sensíveis?",
                    "Há quanto tempo tem sensibilidade?",
                    "A sensibilidade piora com a escovação?"
                ],
                "keywords": ["sensibilidade", "sensível", "dói frio", "dói quente"]
            },
            "mau_hálito": {
                "questions": [
                    "Há quanto tempo nota o mau hálito?",
                    "Alguém próximo comentou sobre isso?",
                    "O mau hálito persiste mesmo após escovar os dentes?",
                    "Tem saburra lingual (placa na língua)?"
                ],
                "keywords": ["mau hálito", "bafo", "halitose"]
            }
        }

        self.medical_conditions = {
            "sistêmicas": [
                "diabetes", "hipertensão", "cardiopatias", "problemas_renais",
                "hepatite", "hiv", "cancer", "osteoporose", "asma", "artrite"
            ],
            "alergias": [
                "penicilina", "anestésicos", "anti-inflamatórios", "latex",
                "antibióticos", "analgésicos"
            ],
            "medicamentos": [
                "anticoagulantes", "corticoides", "bifosfonatos", "imunossupressores",
                "antidepressivos", "anti-hipertensivos"
            ],
            "hábitos": [
                "tabagismo", "etilismo", "bruxismo", "onicofagia", "respiração bucal"
            ]
        }

    def detect_symptoms(self, text):
        """Detecta sintomas mencionados no texto"""
        symptoms_found = []
        text_lower = text.lower()

        for symptom, data in self.symptoms_categories.items():
            if any(keyword in text_lower for keyword in data["keywords"]):
                symptoms_found.append(symptom)

        return symptoms_found

    def get_next_question(self, symptom, conversation_history):
        """Retorna a próxima pergunta baseada no sintoma e histórico"""
        if symptom not in self.symptoms_categories:
            return None

        questions = self.symptoms_categories[symptom]["questions"]

        # Verifica quais perguntas já foram respondidas
        answered_questions = []
        for msg in conversation_history:
            if msg["role"] == "assistant" and any(q in msg["content"] for q in questions):
                # Encontra qual pergunta foi feita
                for q in questions:
                    if q in msg["content"]:
                        answered_questions.append(q)
                        break

        # Retorna a primeira pergunta não respondida
        for question in questions:
            if question not in answered_questions:
                return question

        return None

    def assess_urgency(self, symptoms, responses):
        """Avalia urgência baseada nos sintomas e respostas"""
        urgent_conditions = {
            "inchaço_facial_severo": "URGENTE: Inchaço facial severo pode indicar infecção grave",
            "dificuldade_respirar": "EMERGÊNCIA: Dificuldade respiratória associada a inchaço facial",
            "sangramento_incontrolavel": "URGENTE: Sangramento incontrolável",
            "trauma_facial": "URGENTE: Trauma facial com dor intensa",
            "febre_alta_dor": "URGENTE: Febre alta associada a dor dental"
        }

        # Análise básica de urgência
        if "inchaço" in symptoms and any("aumentando" in str(r).lower() for r in responses):
            return urgent_conditions["inchaço_facial_severo"]

        return "Pode agendar consulta regular. Consulte um dentista para avaliação completa."

# Enhanced Dental Agent Class
class EnhancedDentalAgent:
    def __init__(self):
        self.knowledge_base = DentalKnowledgeBase()
        self.conversation_context = {
            "symptoms_detected": [],
            "current_focus": None,
            "questions_asked": []
        }

    def call_llm_api(self, prompt, max_tokens=150):
        """
        Integra com APIs de LLM gratuitas
        Por enquanto usa fallback, mas pode ser conectado a APIs reais
        """
        try:
            # Tentativa de usar API (substitua com sua API real)
            # return self._call_huggingface_api(prompt, max_tokens)
            return self._rule_based_fallback(prompt)
        except:
            return self._rule_based_fallback(prompt)

    def _rule_based_fallback(self, prompt):
        """Fallback inteligente baseado no conhecimento odontológico"""
        prompt_lower = prompt.lower()

        # Análise baseada no conhecimento
        symptoms = self.knowledge_base.detect_symptoms(prompt)

        if symptoms:
            symptom = symptoms[0]
            next_question = self.knowledge_base.get_next_question(symptom, [])

            if next_question:
                return next_question
            else:
                urgency = self.knowledge_base.assess_urgency(symptoms, [prompt])
                return f"Obrigado pelas informações. {urgency}"

        # Respostas gerais baseadas no contexto
        if any(word in prompt_lower for word in ["obrigado", "agradeço"]):
            urgency = self.knowledge_base.assess_urgency(
                self.conversation_context["symptoms_detected"],
                [prompt]
            )
            return f"De nada! {urgency}"

        elif any(word in prompt_lower for word in ["histórico", "doença", "medicamento"]):
            return "É importante saber seu histórico médico. Você tem alguma condição de saúde, toma medicamentos regularmente ou tem alergias?"

        elif any(word in prompt_lower for word in ["oi", "olá", "hello", "hi"]):
            return "Olá! Sou seu assistente virtual para anamnese odontológica. Por favor, descreva o que está sentindo."

        return "Obrigado por compartilhar. Pode me contar mais detalhes sobre seus sintomas odontológicos?"

    def generate_response(self, user_input, conversation_history):
        """Gera resposta usando conhecimento odontológico"""
        # Atualiza contexto com sintomas detectados
        symptoms = self.knowledge_base.detect_symptoms(user_input)
        if symptoms:
            for symptom in symptoms:
                if symptom not in self.conversation_context["symptoms_detected"]:
                    self.conversation_context["symptoms_detected"].append(symptom)

        # Para cada sintoma detectado, tenta fazer perguntas específicas
        for symptom in self.conversation_context["symptoms_detected"]:
            next_question = self.knowledge_base.get_next_question(symptom, conversation_history)
            if next_question:
                return next_question

        # Se não há perguntas específicas, usa fallback
        return self._rule_based_fallback(user_input)

    def reset_conversation(self):
        """Reseta o contexto da conversação"""
        self.conversation_context = {
            "symptoms_detected": [],
            "current_focus": None,
            "questions_asked": []
        }

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
            "urgency_assessment": st.session_state.dental_agent.knowledge_base.assess_urgency(
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