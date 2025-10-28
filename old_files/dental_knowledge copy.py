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

        self.dental_procedures = {
            "restaurações": "Verificar necessidade de restaurações ou troca de antigas",
            "extração": "Avaliar indicação de exodontia",
            "canal": "Verificar necessidade de tratamento endodôntico",
            "limpeza": "Indicar profilaxia profissional",
            "periodontal": "Avaliar saúde gengival e periodontal"
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

    def generate_llm_prompt(self, user_input, conversation_history, symptoms_detected):
        """Gera prompt para o LLM baseado no conhecimento odontológico"""

        system_prompt = """Você é um assistente virtual especializado em anamnese odontológica.
        Sua função é coletar informações sobre sintomas dentários de maneira profissional e empática.
        Mantenha as respostas claras, focadas na área odontológica e em português.

        Diretrizes:
        - Seja empático e profissional
        - Faça perguntas específicas sobre os sintomas
        - Não dê diagnósticos definitivos
        - Encaminhe para consulta com dentista quando necessário
        - Use linguagem clara e acessível"""

        context = f"""
        Sintomas detectados: {', '.join(symptoms_detected)}
        Histórico recente: {conversation_history[-3:] if conversation_history else 'Nenhum'}
        """

        user_context = f"""
        Input atual do paciente: {user_input}
        """

        full_prompt = f"{system_prompt}\n\n{context}\n{user_context}"
        return full_prompt