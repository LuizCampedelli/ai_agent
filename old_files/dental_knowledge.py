class DentalKnowledgeBase:
    def __init__(self):
        self.symptoms_categories = {
            "dor": [
                "localização", "intensidade", "duração", "frequência",
                "fatores_desencadeantes", "fatores_amelioradores"
            ],
            "sangramento": [
                "local", "frequencia", "quantidade", "associacao_escovacao"
            ],
            "inchaço": [
                "local", "tamanho", "duração", "dor_associada"
            ],
            "sensibilidade": [
                "a_frio", "a_quente", "a_doces", "a_pressao"
            ]
        }

        self.medical_conditions = {
            "sistêmicas": [
                "diabetes", "hipertensão", "cardiopatias", "problemas_renais",
                "hepatite", "hiv", "cancer", "osteoporose"
            ],
            "alergias": [
                "penicilina", "anestésicos", "anti-inflamatórios", "latex"
            ],
            "medicamentos": [
                "anticoagulantes", "corticoides", "bifosfonatos", "imunossupressores"
            ],
            "hábitos": [
                "tabagismo", "etilismo", "bruxismo", "onicofagia"
            ]
        }

    def get_question_flow(self, symptom):
        """Retorna o fluxo de perguntas baseado no sintoma"""
        return self.symptoms_categories.get(symptom, [])

    def assess_urgency(self, symptoms):
        """Avalia urgência baseada nos sintomas"""
        urgent_symptoms = [
            "inchaço_facial_severo", "dificuldade_respirar",
            "sangramento_incontrolavel", "trauma_facial"
        ]

        for symptom in urgent_symptoms:
            if symptom in symptoms:
                return "URGENTE: Procure atendimento imediato"

        return "Pode agendar consulta regular"