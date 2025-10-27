import requests
import json
from dental_knowledge import DentalKnowledgeBase

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
        Opções: Hugging Face, OpenAI-compatible APIs, ou outros serviços gratuitos
        """
        try:
            # Opção 1: Usando Hugging Face Inference API (gratuita para modelos pequenos)
            return self._call_huggingface_api(prompt, max_tokens)
        except:
            try:
                # Opção 2: Usando API alternativa
                return self._call_local_llm(prompt)
            except:
                # Fallback para regras baseadas em conhecimento
                return self._rule_based_fallback(prompt)

    def _call_huggingface_api(self, prompt, max_tokens):
        """Usa Hugging Face Inference API"""
        # Modelo em português ou multilíngue
        API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        headers = {"Authorization": "Bearer hf_your_token_here"}  # Você precisa criar conta gratuita

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": 0.7,
                "do_sample": True
            }
        }

        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '').split(prompt)[-1].strip()

        raise Exception("API call failed")

    def _call_local_llm(self, prompt):
        """Alternativa para APIs locais ou outras APIs gratuitas"""
        # Você pode integrar com outros serviços como:
        # - OpenAI-compatible APIs locais
        # - Outros serviços de LLM gratuitos
        # - Modelos via transformers localmente (se tiver recursos)

        # Por enquanto, usaremos o fallback baseado em regras
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
                return "Obrigado pelas informações. Posso ajudar com mais algum sintoma ou preocupação odontológica?"

        # Respostas gerais baseadas no contexto
        if any(word in prompt_lower for word in ["obrigado", "agradeço"]):
            urgency = self.knowledge_base.assess_urgency(
                self.conversation_context["symptoms_detected"],
                [prompt]
            )
            return f"De nada! {urgency}"

        elif any(word in prompt_lower for word in ["histórico", "doença", "medicamento"]):
            return "É importante saber seu histórico médico. Você tem alguma condição de saúde, toma medicamentos regularmente ou tem alergias?"

        return "Obrigado por compartilhar. Pode me contar mais detalhes sobre seus sintomas odontológicos?"

    def generate_response(self, user_input, conversation_history):
        """Gera resposta usando LLM quando disponível"""
        # Atualiza contexto com sintomas detectados
        symptoms = self.knowledge_base.detect_symptoms(user_input)
        if symptoms:
            self.conversation_context["symptoms_detected"].extend(symptoms)
            self.conversation_context["symptoms_detected"] = list(set(self.conversation_context["symptoms_detected"]))

        # Gera prompt para LLM
        llm_prompt = self.knowledge_base.generate_llm_prompt(
            user_input,
            conversation_history,
            self.conversation_context["symptoms_detected"]
        )

        try:
            # Tenta usar LLM
            response = self.call_llm_api(llm_prompt)

            # Se a resposta for muito genérica, usa fallback
            if len(response.strip()) < 10:
                raise Exception("Response too short")

            return response

        except Exception as e:
            # Fallback para sistema baseado em regras
            return self._rule_based_fallback(user_input)

    def reset_conversation(self):
        """Reseta o contexto da conversação"""
        self.conversation_context = {
            "symptoms_detected": [],
            "current_focus": None,
            "questions_asked": []
        }