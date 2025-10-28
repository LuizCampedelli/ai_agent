import streamlit as st
import json
import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io

# Load environment variables
load_dotenv()

class DentalGeminiAssistant:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.available = True
            except Exception as e:
                st.error(f"❌ Gemini setup failed: {e}")
                self.available = False
        else:
            self.available = False

    def chat(self, user_input, conversation_history, selected_teeth=None, is_final_message=False):
        if not self.available:
            return self._fallback_response(user_input, selected_teeth, is_final_message)

        try:
            # Build context from conversation
            context = self._build_context(conversation_history, selected_teeth, is_final_message)

            prompt = f"""
            VOCÊ É UM ASSISTENTE DENTAL PROFISSIONAL conduzindo uma anamnese odontológica rápida.

            CONTEXTO DA CONVERSA:
            {context}

            SUA IDENTIDADE:
            - Especialista em saúde bucal brasileiro
            - Focado em anamnese dental (entrevista de sintomas)
            - Empático mas objetivo
            - Responde SEMPRE em português brasileiro

            DIREITIVAS PRINCIPAIS:
            1. SE o paciente falar sobre sintomas dentários → Continue a anamnese
            2. SE o paciente fizer perguntas sobre saúde bucal → Responda educadamente
            3. SE o paciente fugir completamente do assunto → Redirecione gentilmente para a anamnese
            4. SE o paciente pedir diagnósticos → Explique que apenas dentistas podem diagnosticar
            5. SEMPRE mantenha o foco na coleta de informações para a anamnese

            CONVERSA ATUAL:
            Histórico recente: {self._format_recent_history(conversation_history)}
            Paciente: "{user_input}"

            SUA RESPOSTA (em português brasileiro):
            """

            response = self.model.generate_content(prompt)
            return self._post_process_response(response.text, user_input)

        except Exception as e:
            return self._fallback_response(user_input, selected_teeth, is_final_message)

    def _build_context(self, conversation_history, selected_teeth, is_final_message):
        context_lines = []

        # Add critical flags
        if is_final_message:
            context_lines.append("🚨 ATENÇÃO: PACIENTE SOLICITOU FINALIZAR - ENCERRAR COM ORIENTAÇÕES FINAIS")

        # Add tooth information if available
        if selected_teeth:
            teeth_names = [TOOTH_NUMBERS.get(int(tooth), f"Dente {tooth}") for tooth in selected_teeth if tooth.isdigit()]
            context_lines.append(f"DENTES COM PROBLEMAS: {', '.join(teeth_names)}")

        # Add interaction progress
        interaction_count = len([msg for msg in conversation_history if msg["role"] == "user"])
        context_lines.append(f"PROGRESSO: {interaction_count} de 5 interações realizadas")

        if interaction_count >= 4:
            context_lines.append("⚠️ ULTIMAS INTERAÇÕES - PREPARAR PARA ENCERRAMENTO")

        return "\n".join(context_lines)

    def _format_recent_history(self, conversation_history):
        """Format recent conversation history for context"""
        if not conversation_history:
            return "Primeira interação do paciente."

        recent_messages = []
        for msg in conversation_history[-4:]:  # Last 4 exchanges
            role = "Paciente" if msg["role"] == "user" else "Você"
            recent_messages.append(f"{role}: {msg['content']}")

        return " | ".join(recent_messages)

    def _post_process_response(self, response, user_input):
        """Post-process the AI response to ensure quality and focus"""

        # Ensure response is in Portuguese
        if not any(word in response.lower() for word in ['obrigado', 'por favor', 'pode', 'onde', 'quando', 'como', 'dor', 'dente']):
            # If response doesn't seem to be in Portuguese, add a Portuguese prefix
            response = "Entendo. " + response

        # Check for off-topic responses and redirect
        user_input_lower = user_input.lower()
        off_topic_keywords = [
            'politica', 'futebol', 'time', 'filme', 'musica', 'celebridade',
            'clima', 'tempo', 'viagem', 'comida', 'restaurante', 'filme',
            'series', 'netflix', 'youtube', 'instagram', 'facebook',
            'trabalho', 'emprego', 'escola', 'faculdade', 'professor'
        ]

        if any(topic in user_input_lower for topic in off_topic_keywords):
            if "anamnese" not in response.lower() and "dental" not in response.lower():
                response = self._redirect_to_dental_topic(response, user_input)

        # Ensure response length is appropriate
        if len(response.split()) > 100:
            # Truncate very long responses and add focus redirect
            sentences = response.split('.')
            if len(sentences) > 3:
                response = '. '.join(sentences[:3]) + '.'
                if "obrigado" not in response.lower():
                    response += " Para focarmos na sua saúde bucal, pode me contar mais sobre seus sintomas dentários?"

        return response

    def _redirect_to_dental_topic(self, current_response, user_input):
        """Redirect off-topic conversations back to dental anamnesis"""
        redirect_templates = [
            "Entendo seu interesse em {assunto}. Como estou aqui para ajudar com sua saúde bucal, gostaria de retomar nossa anamnese. ",
            "Interessante sua pergunta sobre {assunto}! No momento, meu foco é entender seus sintomas dentários para podermos encaminhá-lo adequadamente. ",
            "Agradeço por compartilhar sobre {assunto}. Para garantir que receba o cuidado dental adequado, vamos continuar com a avaliação dos seus sintomas. "
        ]

        import random
        template = random.choice(redirect_templates)

        # Extract main topic from user input
        user_words = user_input.lower().split()
        topic = next((word for word in user_words if any(t in word for t in [
            'politica', 'futebol', 'filme', 'musica', 'clima', 'trabalho', 'escola'
        ])), 'isso')

        redirect_message = template.format(assunto=topic)
        redirect_message += "Pode me descrever algum desconforto ou sintoma que está sentindo nos dentes ou gengivas?"

        return redirect_message

    def _fallback_response(self, user_input, selected_teeth, is_final_message):
        """Enhanced fallback response system"""
        interaction_count = len(st.session_state.conversation) // 2

        # Final message if requested or last interaction
        if is_final_message or interaction_count >= 4:
            return self._get_final_message()

        user_input_lower = user_input.lower()

        # Detect off-topic questions
        off_topic_indicators = [
            'politica', 'futebol', 'time', 'filme', 'musica', 'celebridade',
            'clima', 'tempo', 'viagem', 'comida', 'receita', 'filme',
            'series', 'netflix', 'youtube', 'instagram', 'facebook'
        ]

        if any(topic in user_input_lower for topic in off_topic_indicators):
            return "Entendo sua curiosidade! Como sou especializado em saúde bucal, vou focar em ajudar com seus sintomas dentários. Pode me contar se está sentindo algum desconforto nos dentes ou gengivas?"

        # Detect requests for diagnosis
        diagnosis_indicators = [
            'diagnóstico', 'diagnostico', 'o que eu tenho', 'qual minha doença',
            'estou com que', 'tenho qual problema', 'me diga o que é'
        ]

        if any(indicator in user_input_lower for indicator in diagnosis_indicators):
            return "Como assistente virtual, não posso fornecer diagnósticos. Isso requer avaliação presencial de um dentista. Posso ajudar coletando informações sobre seus sintomas para que você possa levar essas informações para sua consulta. Pode me descrever o que está sentindo?"

        # Context-aware responses for dental symptoms
        if selected_teeth:
            teeth_text = ", ".join(selected_teeth)
            if any(word in user_input_lower for word in ['dor', 'dói', 'dolorido']):
                return f"Entendo que você sente dor nos dentes {teeth_text}. Para entender melhor: a dor é constante ou vem e vai? Qual a intensidade numa escala de 1 a 10?"
            elif any(word in user_input_lower for word in ['sensibilidade', 'sensível']):
                return f"Nos dentes {teeth_text}, a sensibilidade é ao frio, ao quente, a doces ou à pressão da mastigação?"
            elif any(word in user_input_lower for word in ['inchaço', 'inchado']):
                return f"Em relação ao inchaço nos dentes {teeth_text}, há quanto tempo notou? Está aumentando? Há febre associada?"

        # General dental health questions
        dental_health_questions = {
            'clareamento': "O clareamento dental deve ser supervisionado por um dentista para evitar danos. Está sentindo algum sintoma específico nos dentes que gostaria de relatar?",
            'escova': "A escovação adequada é importante! Usa escova macia e faz movimentos suaves? Enquanto isso, está com algum desconforto dental no momento?",
            'fio dental': "O fio dental é essencial para saúde gengival! Nota sangramento ou sensibilidade ao usar fio dental?",
            'mau hálito': "O mau hálito pode ter várias causas. Há quanto tempo nota isso? Persiste mesmo após escovar os dentes?",
            'gengiva': "Problemas gengivais são comuns. Sua gengiva sangra, está inchada ou dolorida?",
        }

        for keyword, response in dental_health_questions.items():
            if keyword in user_input_lower:
                return response

        # General responses
        if any(word in user_input_lower for word in ['oi', 'olá', 'hello', 'hi', 'bom dia', 'boa tarde']):
            return "Olá! Sou seu assistente dental. Por favor, selecione quais dentes estão com problemas usando o sistema de numeração abaixo e descreva seus sintomas."

        if any(word in user_input_lower for word in ['obrigado', 'agradeço', 'valeu']):
            return "De nada! Estou aqui para ajudar. Pode me contar mais sobre seus sintomas para que possamos ter uma anamnese completa?"

        # Default response for unrecognized input
        return "Obrigado pela informação. Para focarmos na sua saúde bucal, pode me dar mais detalhes sobre seus sintomas dentários ou preocupações odontológicas?"

    def _get_final_message(self):
        return """✅ **Anamnese Concluída com Sucesso!**

Agradeço por compartilhar essas informações importantes sobre sua saúde bucal.

**📋 Resumo do Encaminhamento:**

🦷 **Próximos Passos Recomendados:**
1. **Agende uma consulta** com dentista na sua região
2. **Leve este relatório** para sua consulta
3. **Mantenha higiene oral** adequada enquanto aguarda

💡 **Cuidados Imediatos:**
- Evite alimentos muito quentes/frios se houver sensibilidade
- Use escova dental macia
- Evite mastigar no lado dolorido (se aplicável)

🔍 **Onde Encontrar um Dentista:**
- **Conselho Regional de Odontologia (CRO)** do seu estado
- **Doctoralia** ou **iDentista** (apps e sites)
- **Google Maps**: "clínica odontológica perto de mim"
- **Rede credenciada** do seu plano de saúde

🚨 **Procure Atendimento Imediato se observar:**
- Inchaço facial aumentando rapidamente
- Febre + dor dental intensa
- Sangramento que não cessa
- Dificuldade para respirar ou engolir

⚠️ **Lembre-se:** Esta é uma triagem virtual. A avaliação presencial com um dentista é essencial para diagnóstico e tratamento adequados.

📄 **Seu relatório completo está disponível para download abaixo.**"""

# Tooth numbering system (Universal Numbering System)
TOOTH_NUMBERS = {
    # Upper Right (1-8)
    1: "1 - Terceiro Molar Superior Direito",
    2: "2 - Segundo Molar Superior Direito",
    3: "3 - Primeiro Molar Superior Direito",
    4: "4 - Segundo Pré-Molar Superior Direito",
    5: "5 - Primeiro Pré-Molar Superior Direito",
    6: "6 - Canino Superior Direito",
    7: "7 - Incisivo Lateral Superior Direito",
    8: "8 - Incisivo Central Superior Direito",

    # Upper Left (9-16)
    9: "9 - Incisivo Central Superior Esquerdo",
    10: "10 - Incisivo Lateral Superior Esquerdo",
    11: "11 - Canino Superior Esquerdo",
    12: "12 - Primeiro Pré-Molar Superior Esquerdo",
    13: "13 - Segundo Pré-Molar Superior Esquerdo",
    14: "14 - Primeiro Molar Superior Esquerdo",
    15: "15 - Segundo Molar Superior Esquerdo",
    16: "16 - Terceiro Molar Superior Esquerdo",

    # Lower Left (17-24)
    17: "17 - Terceiro Molar Inferior Esquerdo",
    18: "18 - Segundo Molar Inferior Esquerdo",
    19: "19 - Primeiro Molar Inferior Esquerdo",
    20: "20 - Segundo Pré-Molar Inferior Esquerdo",
    21: "21 - Primeiro Pré-Molar Inferior Esquerdo",
    22: "22 - Canino Inferior Esquerdo",
    23: "23 - Incisivo Lateral Inferior Esquerdo",
    24: "24 - Incisivo Central Inferior Esquerdo",

    # Lower Right (25-32)
    25: "25 - Incisivo Central Inferior Direito",
    26: "26 - Incisivo Lateral Inferior Direito",
    27: "27 - Canino Inferior Direito",
    28: "28 - Primeiro Pré-Molar Inferior Direito",
    29: "29 - Segundo Pré-Molar Inferior Direito",
    30: "30 - Primeiro Molar Inferior Direito",
    31: "31 - Segundo Molar Inferior Direito",
    32: "32 - Terceiro Molar Inferior Direito"
}

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
if 'selected_teeth' not in st.session_state:
    st.session_state.selected_teeth = []
if 'interaction_count' not in st.session_state:
    st.session_state.interaction_count = 0
if 'conversation_finished' not in st.session_state:
    st.session_state.conversation_finished = False

def generate_pdf_report():
    """Generate a professional PDF report"""
    try:
        # Create a byte stream for the PDF
        buffer = io.BytesIO()

        # Create the PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            textColor=colors.HexColor('#2E86AB')
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.HexColor('#2E86AB')
        )

        normal_style = styles['Normal']

        # Content container
        story = []

        # Title
        story.append(Paragraph("RELATÓRIO DE ANAMNESE ODONTOLÓGICA", title_style))
        story.append(Spacer(1, 20))

        # Patient Information
        story.append(Paragraph("INFORMAÇÕES DO PACIENTE", heading_style))
        patient_data = [
            ["Nome:", st.session_state.patient_data["name"] or "Não informado"],
            ["Idade:", st.session_state.patient_data["age"] or "Não informado"],
            ["Telefone:", st.session_state.patient_data["phone"] or "Não informado"],
            ["Data da Anamnese:", st.session_state.patient_data["date"]]
        ]

        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8F9FA')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 20))

        # Selected Teeth
        if st.session_state.selected_teeth:
            story.append(Paragraph("DENTES SELECIONADOS COM PROBLEMAS", heading_style))
            teeth_list = []
            for tooth in st.session_state.selected_teeth:
                tooth_name = TOOTH_NUMBERS.get(int(tooth), f"Dente {tooth}")
                teeth_list.append([tooth, tooth_name])

            teeth_table = Table(teeth_list, colWidths=[1*inch, 5*inch])
            teeth_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8F9FA')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ]))
            story.append(teeth_table)
            story.append(Spacer(1, 20))

        # Conversation Summary
        story.append(Paragraph("RESUMO DA CONVERSA", heading_style))

        interactions = len([msg for msg in st.session_state.conversation if msg["role"] == "user"])
        completion_type = "Solicitação do paciente" if st.session_state.conversation_finished else "Automática (5 interações)"

        summary_data = [
            ["Total de Interações:", f"{interactions}/5"],
            ["Tipo de Conclusão:", completion_type],
            ["Data de Exportação:", datetime.datetime.now().strftime("%d/%m/%Y %H:%M")]
        ]

        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))

        # Conversation History
        story.append(Paragraph("HISTÓRICO DA CONVERSA", heading_style))

        for i, message in enumerate(st.session_state.conversation):
            role = "PACIENTE" if message["role"] == "user" else "ASSISTENTE"
            timestamp = message.get('timestamp', '')

            content = f"<b>{role}</b> ({timestamp}): {message['content']}"
            story.append(Paragraph(content, normal_style))
            story.append(Spacer(1, 8))

        story.append(Spacer(1, 20))

        # Recommendations
        story.append(Paragraph("RECOMENDAÇÕES E ENCAMINHAMENTO", heading_style))
        recommendations = [
            "• Agendar consulta com dentista para avaliação presencial",
            "• Manter boa higiene oral enquanto aguarda atendimento",
            "• Evitar alimentos muito quentes/frios se houver sensibilidade",
            "• Usar escova dental macia e fazer movimentos suaves",
            "• Em caso de emergência, procurar atendimento imediato"
        ]

        for rec in recommendations:
            story.append(Paragraph(rec, normal_style))
            story.append(Spacer(1, 4))

        story.append(Spacer(1, 20))

        # Footer
        footer_text = """
        <i>Relatório gerado automaticamente pelo Sistema de Anamnese Odontológica Inteligente.<br/>
        Este é um relatório de triagem virtual e não substitui a avaliação presencial de um profissional de saúde bucal.</i>
        """
        story.append(Paragraph(footer_text, styles['Italic']))

        # Build PDF
        doc.build(story)

        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()

        return pdf_data

    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")
        return None

def export_to_json():
    """Export conversation and patient data to JSON"""
    try:
        export_data = {
            "patient_info": st.session_state.patient_data,
            "selected_teeth": st.session_state.selected_teeth,
            "conversation": st.session_state.conversation,
            "interaction_count": len([msg for msg in st.session_state.conversation if msg["role"] == "user"]),
            "completion_type": "patient_request" if st.session_state.conversation_finished else "automatic",
            "export_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return json.dumps(export_data, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Erro ao exportar JSON: {e}")
        return None

def process_user_input(user_input):
    """Process user input and generate AI response"""
    # Add timestamp to user message
    user_message = {
        "role": "user",
        "content": user_input,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.conversation.append(user_message)

    # Check if this should be the final message
    is_final_message = (
        "finalizar" in user_input.lower() or
        "encerrar" in user_input.lower() or
        "fim" in user_input.lower() or
        "acabou" in user_input.lower()
    )

    # Generate AI response
    with st.spinner("🤖 Assistente dental pensando..."):
        ai_response = st.session_state.assistant.chat(
            user_input,
            st.session_state.conversation,
            st.session_state.selected_teeth,
            is_final_message
        )

    # Add AI response to conversation
    ai_message = {
        "role": "assistant",
        "content": ai_response,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.conversation.append(ai_message)

    # Update interaction count
    st.session_state.interaction_count = len([msg for msg in st.session_state.conversation if msg["role"] == "user"])

    # Check if conversation should be finished
    if is_final_message or st.session_state.interaction_count >= 5:
        st.session_state.conversation_finished = True

    st.rerun()

def finalize_conversation():
    """Finalize the conversation with final recommendations"""
    final_message = st.session_state.assistant._get_final_message()

    ai_message = {
        "role": "assistant",
        "content": final_message,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.conversation.append(ai_message)
    st.session_state.conversation_finished = True
    st.rerun()

def reset_conversation():
    """Reset the entire conversation and selections"""
    st.session_state.conversation = []
    st.session_state.selected_teeth = []
    st.session_state.interaction_count = 0
    st.session_state.conversation_finished = False
    st.rerun()

def main():
    st.set_page_config(
        page_title="Assistente Dental - Anamnese Inteligente",
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
            "Nome Completo*",
            value=st.session_state.patient_data["name"],
            placeholder="Seu nome completo"
        )

        st.session_state.patient_data["age"] = st.text_input(
            "Idade*",
            value=st.session_state.patient_data["age"],
            placeholder="Sua idade"
        )

        st.session_state.patient_data["phone"] = st.text_input(
            "Telefone*",
            value=st.session_state.patient_data["phone"],
            placeholder="(00) 00000-0000"
        )

        # Interaction counter
        st.divider()
        st.header("📊 Progresso")
        interactions = len([msg for msg in st.session_state.conversation if msg["role"] == "user"])
        st.progress(interactions / 5)
        st.write(f"**Interações:** {interactions}/5")

        if interactions >= 5 or st.session_state.conversation_finished:
            st.error("✅ Anamnese concluída!")
            st.info("Consulte a conversa para encaminhamento")

        st.divider()

        # Finalizar conversa button
        if not st.session_state.conversation_finished and interactions > 0:
            if st.button("🏁 Finalizar Anamnese Agora", type="primary", use_container_width=True):
                finalize_conversation()

        st.divider()

        # Quick actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Nova Anamnese", use_container_width=True):
                reset_conversation()

        with col2:
            if st.button("💾 Exportar", use_container_width=True):
                export_to_json()

def render_main_content():
    st.title("🦷 Assistente Dental - Anamnese Inteligente")
    st.markdown("""
    **Sistema de triagem dental com IA avançada** - Máximo 5 interações para agilidade
    """)

    # Check if maximum interactions reached or conversation finished
    interactions = len([msg for msg in st.session_state.conversation if msg["role"] == "user"])
    if interactions >= 5 or st.session_state.conversation_finished:
        st.error("🚫 **Anamnese concluída** - Encaminhamento gerado")
        st.info("Consulte a aba 💬 Anamnese para ver o encaminhamento final")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📍 Selecionar Dentes", "💬 Anamnese Inteligente", "📊 Resultado"])

    with tab1:
        render_tooth_selection()

    with tab2:
        render_chat_interface()

    with tab3:
        render_results()

def render_tooth_selection():
    st.header("📍 Selecione os Dentes com Problemas")

    # Check if conversation is finished
    if st.session_state.conversation_finished:
        st.info("📝 Anamnese já finalizada. Se precisar reiniciar, clique em 'Nova Anamnese' na sidebar.")
        return

    # Display tooth numbering system
    st.subheader("🦷 Sistema de Numeração Dental")

    # Create a clean visual representation of the tooth numbering system
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Dentes Superiores (Maxila)**
        ```
        Direita → Esquerda
        🦷🦷🦷🦷🦷🦷🦷🦷
         1  2  3  4  5  6  7  8
        ```
        """)

        st.markdown("""
        **Dentes Inferiores (Mandíbula)**
        ```
        Esquerda → Direita
        🦷🦷🦷🦷🦷🦷🦷🦷
        17 18 19 20 21 22 23 24
        ```
        """)

    with col2:
        st.markdown("""
        **Dentes Superiores (Maxila)**
        ```
        Esquerda → Direita
        🦷🦷🦷🦷🦷🦷🦷🦷
         9 10 11 12 13 14 15 16
        ```
        """)

        st.markdown("""
        **Dentes Inferiores (Mandíbula)**
        ```
        Direita → Esquerda
        🦷🦷🦷🦷🦷🦷🦷🦷
        25 26 27 28 29 30 31 32
        ```
        """)

    st.info("""
    **📋 Legenda:**
    - **1-8:** Dentes superiores direito
    - **9-16:** Dentes superiores esquerdo
    - **17-24:** Dentes inferiores esquerdo
    - **25-32:** Dentes inferiores direito
    """)

    st.markdown("""
    **Como usar:**
    1. Consulte o sistema de numeração acima para identificar os dentes
    2. Clique nos números correspondentes abaixo
    3. Descreva seus sintomas no chat
    4. **Finalize quando achar necessário** - botão na sidebar
    """)

    # Tooth number buttons in a grid
    st.subheader("🔢 Seleção por Números")

    # Create columns for tooth numbers
    cols = st.columns(8)
    for i, tooth_num in enumerate(range(1, 33)):
        col_idx = i % 8
        with cols[col_idx]:
            is_selected = str(tooth_num) in st.session_state.selected_teeth
            button_type = "primary" if is_selected else "secondary"

            if st.button(f"{tooth_num}", key=f"tooth_{tooth_num}",
                        use_container_width=True, type=button_type):
                # Toggle selection
                tooth_str = str(tooth_num)
                if tooth_str in st.session_state.selected_teeth:
                    st.session_state.selected_teeth.remove(tooth_str)
                else:
                    st.session_state.selected_teeth.append(tooth_str)
                st.rerun()

    # Show selected teeth
    if st.session_state.selected_teeth:
        st.success(f"✅ Dentes selecionados: {', '.join(sorted(st.session_state.selected_teeth))}")

        # Show tooth names
        selected_names = []
        for tooth in st.session_state.selected_teeth:
            if int(tooth) in TOOTH_NUMBERS:
                selected_names.append(TOOTH_NUMBERS[int(tooth)])

        with st.expander("Ver detalhes dos dentes selecionados"):
            for name in selected_names:
                st.write(f"• {name}")
    else:
        st.info("👆 Selecione os dentes com problemas clicando nos números acima")

def render_chat_interface():
    st.header("💬 Anamnese com IA Inteligente")

    # Interaction counter
    interactions = len([msg for msg in st.session_state.conversation if msg["role"] == "user"])
    st.caption(f"Interação {interactions}/5 - IA especializada em saúde bucal")

    # Display conversation
    for message in st.session_state.conversation:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(f"**Paciente**: {message['content']}")
        else:
            with st.chat_message("assistant"):
                st.write(f"**Assistente IA**: {message['content']}")
                if "redirecion" in message['content'].lower() or "focar" in message['content'].lower():
                    st.caption("🔍 IA mantendo o foco na saúde bucal")

    # Final message if conversation is finished
    if st.session_state.conversation_finished:
        st.success("""
        ## 🏁 Anamnese Finalizada pelo Paciente

        **Obrigado por utilizar nosso serviço de triagem inteligente!**

        Sua anamnese foi concluída e as informações estão salvas.
        Consulte a aba **📊 Resultado** para ver o relatório completo e encaminhamento.
        """)
        return

    # Chat input (disabled if max interactions reached or no teeth selected or conversation finished)
    interactions = len([msg for msg in st.session_state.conversation if msg["role"] == "user"])

    if interactions >= 5:
        st.warning("✅ Anamnese concluída automaticamente (5 interações)! Verifique o resultado final.")
        return

    if not st.session_state.selected_teeth:
        st.info("📍 Primeiro selecione os dentes com problemas na aba anterior")
        return

    # Quick finalize button in chat area too
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🏁 Finalizar Agora", type="primary", use_container_width=True):
            finalize_conversation()
            return

    with col1:
        user_input = st.chat_input("Descreva seus sintomas ou faça perguntas...")

    if user_input:
        process_user_input(user_input)

def render_results():
    st.header("📊 Resultado da Anamnese")

    interactions = len([msg for msg in st.session_state.conversation if msg["role"] == "user"])

    if interactions == 0 and not st.session_state.conversation_finished:
        st.info("💬 A anamnese ainda não começou. Selecione os dentes e inicie a conversa.")
        return

    # Summary card
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Interações", f"{interactions}/5")

    with col2:
        st.metric("Dentes Selecionados", len(st.session_state.selected_teeth))

    with col3:
        if st.session_state.conversation_finished:
            status = "Finalizada pelo paciente"
        elif interactions >= 5:
            status = "Concluída automaticamente"
        else:
            status = "Em andamento"
        st.metric("Status", status)

    # Final recommendation if completed
    if st.session_state.conversation_finished or interactions >= 5:
        st.success("""
        ## ✅ Anamnese Concluída!

        **Recomendação:** Consulta com dentista recomendada.

        🔍 **Para encontrar um dentista próximo:**
        - **Conselho Regional de Odontologia (CRO):** Consulte o site do CRO do seu estado
        - **Doctoralia:** www.doctoralia.com.br
        - **iDentista:** App disponível nas lojas de aplicativos
        - **Google Maps:** Pesquise "dentista perto de mim"
        - **Planos de saúde:** Consulte a rede credenciada do seu convênio

        📞 **Emergências:** Procure atendimento imediato em casos de:
        - Dor intensa e inchaço
        - Sangramento que não para
        - Trauma dental recente
        - Febre associada a dor dental
        """)

    # Export options
    if st.session_state.conversation:
        st.subheader("📤 Exportar Relatório")

        col1, col2 = st.columns(2)

        with col1:
            # JSON Export
            json_data = export_to_json()
            if json_data:
                st.download_button(
                    label="📄 Exportar JSON",
                    data=json_data,
                    file_name=f"anamnese_dental_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json",
                    use_container_width=True
                )

        with col2:
            # PDF Export
            pdf_data = generate_pdf_report()
            if pdf_data:
                st.download_button(
                    label="📋 Exportar PDF",
                    data=pdf_data,
                    file_name=f"relatorio_anamnese_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        # Conversation preview
        st.subheader("📝 Histórico da Conversa")
        with st.expander("Ver conversa completa"):
            for i, message in enumerate(st.session_state.conversation):
                if message["role"] == "user":
                    st.markdown(f"**👤 Paciente** ({message.get('timestamp', '')}):")
                    st.info(message["content"])
                else:
                    st.markdown(f"**🤖 Assistente IA** ({message.get('timestamp', '')}):")
                    st.success(message["content"])
                st.divider()

if __name__ == "__main__":
    main()