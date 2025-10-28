import os
from crewai import Agent, Task, Crew, Process
from langchain.tools import Tool
from langchain.utilities import GoogleSerperAPIWrapper
import json

class DentalCrewAI:
    def __init__(self):
        self.setup_agents()
        self.setup_tools()

    def setup_agents(self):
        """Setup specialized dental agents"""

        # Dental Anamnesis Specialist Agent
        self.anamnesis_agent = Agent(
            role='Dental Anamnesis Specialist',
            goal='Conduct comprehensive dental health interviews to identify symptoms, '
                 'assess urgency, and gather relevant medical history',
            backstory='You are an experienced dental assistant with 10+ years in '
                     'patient intake and anamnesis. You excel at asking the right '
                     'questions to uncover dental issues while making patients feel '
                     'comfortable. You speak Brazilian Portuguese fluently and understand '
                     'common dental terminology used by patients.',
            allow_delegation=False,
            verbose=True
        )

        # Symptom Analysis Agent
        self.symptom_analyst = Agent(
            role='Dental Symptom Analyst',
            goal='Analyze reported symptoms to identify patterns, assess urgency, '
                 'and suggest possible conditions',
            backstory='You are a dental diagnostician specializing in symptom analysis. '
                     'You can correlate different symptoms to identify potential dental '
                     'conditions and assess the urgency of each case.',
            allow_delegation=False,
            verbose=True
        )

        # Treatment Advisor Agent
        self.treatment_advisor = Agent(
            role='Dental Treatment Advisor',
            goal='Provide preliminary treatment recommendations and professional guidance '
                 'based on symptoms and analysis',
            backstory='You are an experienced dentist who provides initial treatment '
                     'recommendations and professional advice. You know when to recommend '
                     'immediate care versus routine dental visits.',
            allow_delegation=False,
            verbose=True
        )

    def setup_tools(self):
        """Setup tools for the agents (optional - for enhanced capabilities)"""
        # You can add tools like web search, medical databases, etc.
        # For now, we'll use the agents without external tools
        self.tools = []

    def conduct_anamnesis(self, user_input, conversation_history):
        """Conduct dental anamnesis using CrewAI"""

        # Create anamnesis task
        anamnesis_task = Task(
            description=f"""
            CONDUCT DENTAL ANAMNESIS INTERVIEW

            Patient Input: "{user_input}"

            Conversation History:
            {self._format_conversation_history(conversation_history)}

            Your Role: Continue the dental anamnesis interview in Brazilian Portuguese.
            - Ask relevant follow-up questions based on the symptoms mentioned
            - Be empathetic and professional
            - Focus on gathering key dental health information
            - Assess the urgency of the situation
            - Ask about pain location, duration, intensity, triggers
            - Inquire about bleeding, swelling, sensitivity, or other symptoms
            - Consider medical history and medications if relevant

            Respond in Brazilian Portuguese, maintaining a natural conversation flow.
            """,
            agent=self.anamnesis_agent,
            expected_output="A natural, empathetic response in Brazilian Portuguese that continues the dental anamnesis interview with relevant follow-up questions."
        )

        # Create symptom analysis task
        analysis_task = Task(
            description=f"""
            ANALYZE REPORTED SYMPTOMS

            Current Input: "{user_input}"
            Conversation History: {len(conversation_history)} messages

            Analyze the symptoms mentioned and:
            1. Identify all dental symptoms present
            2. Assess urgency level (emergency, urgent, routine)
            3. Suggest key follow-up questions
            4. Identify potential dental conditions

            Provide your analysis in English for internal use.
            """,
            agent=self.symptom_analyst,
            expected_output="Structured analysis of symptoms, urgency assessment, and follow-up question suggestions."
        )

        # Create crew and execute
        dental_crew = Crew(
            agents=[self.anamnesis_agent, self.symptom_analyst],
            tasks=[anamnesis_task, analysis_task],
            process=Process.sequential,
            verbose=True
        )

        try:
            result = dental_crew.kickoff()
            return str(result)
        except Exception as e:
            return self._fallback_response(user_input, conversation_history)

    def analyze_complex_case(self, full_conversation):
        """Analyze complex dental cases with multiple agents"""

        analysis_task = Task(
            description=f"""
            COMPREHENSIVE DENTAL CASE ANALYSIS

            Full Conversation:
            {self._format_conversation_history(full_conversation)}

            Analyze this dental case comprehensively:
            1. Identify all symptoms and their patterns
            2. Assess overall urgency and risk factors
            3. Suggest possible differential diagnoses
            4. Recommend appropriate next steps
            5. Provide patient education points

            Focus on clinical accuracy while maintaining patient safety.
            """,
            agent=self.symptom_analyst,
            expected_output="Comprehensive dental case analysis with symptoms, urgency assessment, and recommendations."
        )

        advice_task = Task(
            description="""
            Based on the symptom analysis, provide professional dental advice including:
            - When to seek immediate care vs routine appointment
            - Home care recommendations if appropriate
            - Red flags to watch for
            - Professional follow-up recommendations
            """,
            agent=self.treatment_advisor,
            expected_output="Professional dental advice and recommendations for the patient."
        )

        analysis_crew = Crew(
            agents=[self.symptom_analyst, self.treatment_advisor],
            tasks=[analysis_task, advice_task],
            process=Process.sequential,
            verbose=True
        )

        try:
            result = analysis_crew.kickoff()
            return str(result)
        except Exception as e:
            return "Analysis complete. Please consult with a dental professional for comprehensive care."

    def _format_conversation_history(self, conversation_history):
        """Format conversation history for the AI"""
        if not conversation_history:
            return "No previous conversation."

        formatted = []
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            role = "Patient" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")

        return "\n".join(formatted)

    def _fallback_response(self, user_input, conversation_history):
        """Fallback response if CrewAI fails"""
        user_input_lower = user_input.lower()

        if any(word in user_input_lower for word in ["dor", "dói", "dolorido"]):
            return "Entendo que você está sentindo dor. Pode me dizer onde exatamente está localizada a dor e se é constante ou intermitente?"
        elif any(word in user_input_lower for word in ["sangramento", "sangra"]):
            return "Obrigado por mencionar o sangramento. Isso acontece durante a escovação ou espontaneamente? Há quanto tempo nota isso?"
        elif any(word in user_input_lower for word in ["inchaço", "inchado"]):
            return "Vejo que você tem inchaço. Onde está localizado? Há quanto tempo notou e está aumentando?"
        else:
            return "Obrigado pela informação. Pode me contar mais detalhes sobre seus sintomas ou preocupações odontológicas?"