import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import WebsiteSearchTool
import google.generativeai as genai
from config import config

class DentalCrewAIGemini:
    def __init__(self):
        self.config = config
        self.setup_gemini()
        self.setup_tools()
        self.setup_agents()

    def setup_gemini(self):
        """Configure Google Gemini"""
        if self.config.google_api_key:
            try:
                genai.configure(api_key=self.config.google_api_key)
                print("✅ Google Gemini configured successfully")

                # Test the connection
                self.gemini_available = True
                print(f"🤖 Using Gemini model: {self.config.google_model}")

            except Exception as e:
                print(f"❌ Gemini configuration failed: {e}")
                self.gemini_available = False
        else:
            self.gemini_available = False
            print("ℹ️  Gemini API key not found, using CrewAI default")

    def setup_tools(self):
        """Setup tools for agents"""
        self.tools = []

        # Add website search tool
        try:
            website_tool = WebsiteSearchTool()
            self.tools.append(website_tool)
            print("✅ Website search tool loaded")
        except Exception as e:
            print(f"❌ Failed to load website tool: {e}")

    def setup_agents(self):
        """Setup dental agents optimized for Gemini"""

        llm_config = self.config.get_llm_config()
        print(f"🚀 Using LLM: {llm_config['provider']} - {llm_config['model']}")

        # Dental Anamnesis Specialist - Optimized for Portuguese conversations
        self.anamnesis_agent = Agent(
            role='Especialista em Anamnese Odontológica',
            goal='''
            Realizar entrevistas completas de saúde bucal em português para identificar
            sintomas, avaliar urgência e coletar histórico médico dental. Manter conversa
            natural e empática com pacientes brasileiros.
            ''',
            backstory='''
            Você é um assistente dental brasileiro com mais de 10 anos de experiência
            em atendimento ao paciente. Especialista em fazer as perguntas certas para
            descobrir problemas dentários enquanto faz os pacientes se sentirem confortáveis.
            Fala português fluente e entende a terminologia dental comum usada pelos pacientes.
            ''',
            tools=self.tools,
            allow_delegation=False,
            verbose=self.config.debug_mode,
            max_iter=3,
            max_rpm=10,
            language='portuguese'  # Important for Gemini to understand context
        )

        # Symptom Analyst - For clinical analysis
        self.symptom_analyst = Agent(
            role='Analista de Sintomas Dentários',
            goal='Analisar sintomas relatados para identificar padrões, avaliar urgência e sugerir possíveis condições dentárias',
            backstory='''
            Você é um diagnosticador dental especializado em análise de sintomas.
            Consegue correlacionar diferentes sintomas para identificar condições dentárias
            potenciais e avaliar com precisão a urgência de cada caso.
            ''',
            tools=self.tools,
            allow_delegation=False,
            verbose=self.config.debug_mode,
            max_iter=2
        )

        # Treatment Advisor - For professional recommendations
        self.treatment_advisor = Agent(
            role='Consultor de Tratamento Dental',
            goal='Fornecer recomendações preliminares de tratamento e orientação profissional baseada em sintomas e análise',
            backstory='''
            Você é um dentista experiente que fornece recomendações de tratamento baseadas em evidências.
            Sabe quando recomendar cuidado imediato versus consultas dentárias de rotina
            e pode explicar conceitos dentários complexos em termos simples.
            ''',
            tools=self.tools,
            allow_delegation=False,
            verbose=self.config.debug_mode,
            max_iter=2
        )

    def conduct_anamnesis(self, user_input, conversation_history):
        """Conduct dental anamnesis using Gemini-powered agents"""

        # Enhanced prompt optimized for Portuguese responses
        anamnesis_task = Task(
            description=f"""
            REALIZAR ENTREVISTA DE ANAMNESE DENTAL - RESPONDER EM PORTUGUÊS

            ENTRADA ATUAL DO PACIENTE: "{user_input}"

            HISTÓRICO RECENTE DA CONVERSA:
            {self._format_conversation_history(conversation_history)}

            INSTRUÇÕES ESPECÍFICAS:
            1. Continue a anamnese dental naturalmente em PORTUGUÊS BRASILEIRO
            2. Faça perguntas de acompanhamento relevantes baseadas nos sintomas mencionados
            3. Seja empático e profissional
            4. Foque em coletar informações-chave de saúde bucal
            5. Avalie urgência se sintomas preocupantes forem mencionados
            6. Use linguagem simples e clara que pacientes possam entender
            7. Mantenha o tom conversacional e acolhedor

            SINTOMAS COMUNS A INVESTIGAR:
            - Dor: localização, intensidade, duração, fatores desencadeantes
            - Sangramento: quando ocorre, frequência, quantidade
            - Inchaço: localização, tempo de evolução, dor associada
            - Sensibilidade: a frio, quente, doces, pressão

            IMPORTANTE: Sempre responda em PORTUGUÊS BRASILEIRO.
            """,
            agent=self.anamnesis_agent,
            expected_output="Uma resposta natural e empática em português brasileiro que continua a anamnese dental com perguntas de acompanhamento relevantes."
        )

        try:
            dental_crew = Crew(
                agents=[self.anamnesis_agent],
                tasks=[anamnesis_task],
                process=Process.sequential,
                verbose=self.config.debug_mode,
                memory=True
            )

            result = dental_crew.kickoff()

            # Post-process to ensure Portuguese response
            processed_result = self._ensure_portuguese_response(str(result))
            return processed_result

        except Exception as e:
            print(f"🚨 CrewAI Error: {e}")
            return self._fallback_response(user_input, conversation_history)

    def analyze_with_gemini_direct(self, prompt):
        """Use Gemini directly for complex analysis (fallback)"""
        if not self.gemini_available:
            return "Análise não disponível no momento."

        try:
            model = genai.GenerativeModel(self.config.google_model)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"🚨 Gemini direct call failed: {e}")
            return "Desculpe, não consegui processar sua solicitação no momento."

    def _ensure_portuguese_response(self, text):
        """Ensure response is in Portuguese"""
        portuguese_indicators = [
            'obrigado', 'por favor', 'pode me', 'onde', 'quando',
            'como', 'dói', 'dor', 'sangramento', 'inchaço'
        ]

        # If response doesn't seem to be in Portuguese, translate key parts
        if not any(indicator in text.lower() for indicator in portuguese_indicators):
            if self.gemini_available:
                translation_prompt = f"""
                Traduza este texto para português brasileiro mantendo o significado médico:
                "{text}"

                Mantenha termos técnicos em português e o tom profissional mas amigável.
                """
                try:
                    model = genai.GenerativeModel(self.config.google_model)
                    response = model.generate_content(translation_prompt)
                    return response.text
                except:
                    return text  # Return original if translation fails

        return text

    def _format_conversation_history(self, conversation_history):
        """Format conversation history"""
        if not conversation_history:
            return "Nenhuma conversa anterior."

        formatted = []
        for msg in conversation_history[-6:]:
            role = "Paciente" if msg["role"] == "user" else "Assistente"
            formatted.append(f"{role}: {msg['content']}")

        return "\n".join(formatted)

    def _fallback_response(self, user_input, conversation_history):
        """Intelligent fallback in Portuguese"""
        user_input_lower = user_input.lower()

        symptom_responses = {
            'dor': "Entendo que você está sentindo dor. Pode me dizer onde exatamente está localizada a dor? É constante ou vai e vem?",
            'sangramento': "Obrigado por mencionar o sangramento. Isso acontece durante a escovação ou espontaneamente? Há quanto tempo nota isso?",
            'inchaço': "Vejo que você tem inchaço. Onde está localizado? Há quanto tempo notou? Está aumentando?",
            'sensibilidade': "Entendo sobre a sensibilidade. É ao frio, ao quente, a doces ou à pressão? Quais dentes são sensíveis?",
            'mau hálito': "Obrigado por mencionar o mau hálito. Há quanto tempo nota isso? Persiste mesmo após escovar os dentes?"
        }

        for symptom, response in symptom_responses.items():
            if symptom in user_input_lower:
                return response

        # Greeting responses
        if any(word in user_input_lower for word in ['oi', 'olá', 'hello', 'hi']):
            return "Olá! Sou seu assistente virtual para anamnese odontológica. Por favor, descreva o que está sentindo."

        # Thank you responses
        if any(word in user_input_lower for word in ['obrigado', 'agradeço']):
            return "De nada! Posso ajudar com mais alguma preocupação odontológica?"

        return "Obrigado pela informação. Pode me contar mais detalhes sobre seus sintomas ou preocupações odontológicas?"