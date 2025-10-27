import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
import numpy as np
from dental_knowledge import DentalKnowledgeBase
import re

class DentalAgent:
    def __init__(self):
        self.knowledge_base = DentalKnowledgeBase()
        self.conversation_history = []
        self.current_context = {}

        # Carregar modelo local (usando um modelo menor para rodar localmente)
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
            self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        except:
            print("Usando fallback para modelo simples")
            self.model = None

    def preprocess_input(self, text):
        """Pré-processa o input do usuário"""
        text = text.lower().strip()
        # Remove caracteres especiais mas mantém acentos
        text = re.sub(r'[^\w\sáàâãéèêíïóôõöúçñ]', '', text)
        return text

    def detect_symptoms(self, text):
        """Detecta sintomas mencionados no texto"""
        symptoms_found = []
        text_lower = text.lower()

        symptom_keywords = {
            "dor": ["dor", "dói", "dolorido", "latejando"],
            "sangramento": ["sangra", "sangramento", "sangue"],
            "inchaço": ["inchaço", "inchado", "inchar"],
            "sensibilidade": ["sensível", "sensibilidade", "dói frio", "dói quente"],
            "cárie": ["cárie", "buraco", "escuro"],
            "mau_hálito": ["mau hálito", "bafo", "halitose"]
        }

        for symptom, keywords in symptom_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                symptoms_found.append(symptom)

        return symptoms_found

    def generate_response(self, user_input):
        """Gera resposta baseada no input do usuário"""
        processed_input = self.preprocess_input(user_input)
        symptoms = self.detect_symptoms(processed_input)

        # Adiciona sintomas detectados ao contexto
        if symptoms:
            self.current_context['symptoms_detected'] = symptoms

        # Lógica de conversação baseada em regras
        response = self.rule_based_response(processed_input, symptoms)

        # Se não houver resposta por regras, usa o modelo
        if not response and self.model:
            response = self.model_based_response(processed_input)

        self.conversation_history.append({
            "user": user_input,
            "agent": response,
            "symptoms": symptoms
        })

        return response

    def rule_based_response(self, user_input, symptoms):
        """Resposta baseada em regras do domínio odontológico"""

        # Saudação inicial
        if any(word in user_input for word in ["oi", "olá", "bom dia", "boa tarde"]):
            return ("Olá! Sou seu assistente virtual para anamnese odontológica. "
                   "Vou fazer algumas perguntas para entender melhor seu caso. "
                   "Por favor, descreva o que está sentindo.")

        # Detecção de sintomas
        if symptoms:
            symptom_list = ", ".join(symptoms)
            follow_up = "Para me ajudar a entender melhor, "

            if "dor" in symptoms:
                follow_up += "onde exatamente está sentindo dor? É constante ou vem e vai?"
            elif "sangramento" in symptoms:
                follow_up += "o sangramento acontece durante a escovação ou espontaneamente?"
            elif "inchaço" in symptoms:
                follow_up += "há quanto tempo notou o inchaço? Está aumentando?"
            else:
                follow_up += "pode me contar mais sobre quando começou e como tem evoluído?"

            return f"Entendo que você está com {symptom_list}. {follow_up}"

        # Perguntas sobre histórico médico
        if any(word in user_input for word in ["histórico", "doença", "medicamento", "alergia"]):
            return ("É importante saber seu histórico médico. "
                   "Você tem alguma condição médica como diabetes, hipertensão ou problemas cardíacos? "
                   "Toma algum medicamento regularmente? Tem alergias?")

        # Finalização
        if any(word in user_input for word in ["obrigado", "agradeço", "tchau"]):
            assessment = self.knowledge_base.assess_urgency(
                self.current_context.get('symptoms_detected', [])
            )
            return (f"Obrigado pelas informações! {assessment} "
                   "Lembre-se: sou apenas um assistente virtual. "
                   "Consulte sempre um dentista para diagnóstico preciso.")

        return None

    def model_based_response(self, user_input):
        """Usa modelo de linguagem para gerar resposta (fallback)"""
        if not self.model:
            return "Pode me contar mais detalhes sobre seu problema dental?"

        # Prepara input para o modelo
        input_ids = self.tokenizer.encode(user_input + self.tokenizer.eos_token, return_tensors='pt')

        # Gera resposta
        with torch.no_grad():
            output = self.model.generate(
                input_ids,
                max_length=1000,
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7
            )

        response = self.tokenizer.decode(output[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
        return response

    def get_conversation_summary(self):
        """Retorna resumo da conversa para o dentista"""
        symptoms = set()
        for entry in self.conversation_history:
            symptoms.update(entry['symptoms'])

        return {
            "sintomas_identificados": list(symptoms),
            "historico_conversa": self.conversation_history,
            "contexto_atual": self.current_context
        }