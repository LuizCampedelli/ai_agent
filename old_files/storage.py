import json
import os

class DataManager:
    def __init__(self, storage_dir="data"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_conversation(self, patient_data, conversation):
        filename = f"{patient_data['nome']}_{patient_data.get('data_consulta', 'unknown')}.json"
        filepath = os.path.join(self.storage_dir, filename)

        data = {
            "patient_data": patient_data,
            "conversation": conversation,
            "summary": self.generate_summary(conversation)
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def generate_summary(self, conversation):
        # Gera resumo automático da conversa
        symptoms = []
        for message in conversation:
            if message['role'] == 'user':
                # Análise simples de sintomas
                text = message['content'].lower()
                if 'dor' in text:
                    symptoms.append('dor')
                if 'sangramento' in text:
                    symptoms.append('sangramento')

        return {
            "sintomas_identificados": list(set(symptoms)),
            "quantidade_mensagens": len(conversation)
        }