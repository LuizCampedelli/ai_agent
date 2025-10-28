import json
import sqlite3
import pandas as pd
from datetime import datetime
import os
from typing import Dict, List, Optional

class ElectronicHealthRecord:
    def __init__(self, db_path="dental_records.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Inicializa banco de dados SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabela de pacientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                birth_date TEXT,
                phone TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabela de consultas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consultations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                consultation_date TEXT,
                chief_complaint TEXT,
                symptoms TEXT,
                diagnosis TEXT,
                treatment_plan TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')

        # Tabela de anamneses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anamnesis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                consultation_id INTEGER,
                conversation_data TEXT,
                symptoms_detected TEXT,
                urgency_level TEXT,
                ai_analysis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (consultation_id) REFERENCES consultations (id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_patient(self, name: str, birth_date: str = None,
                   phone: str = None, email: str = None) -> int:
        """Adiciona novo paciente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO patients (name, birth_date, phone, email)
            VALUES (?, ?, ?, ?)
        ''', (name, birth_date, phone, email))

        patient_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return patient_id

    def add_consultation(self, patient_id: int, consultation_date: str,
                        chief_complaint: str, symptoms: str) -> int:
        """Adiciona nova consulta"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO consultations
            (patient_id, consultation_date, chief_complaint, symptoms)
            VALUES (?, ?, ?, ?)
        ''', (patient_id, consultation_date, chief_complaint, symptoms))

        consultation_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return consultation_id

    def save_anamnesis(self, consultation_id: int, conversation_data: Dict,
                      symptoms_detected: List, urgency_level: str,
                      ai_analysis: Dict) -> int:
        """Salva dados da anamnese do agente de IA"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO anamnesis
            (consultation_id, conversation_data, symptoms_detected,
             urgency_level, ai_analysis)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            consultation_id,
            json.dumps(conversation_data, ensure_ascii=False),
            json.dumps(symptoms_detected, ensure_ascii=False),
            urgency_level,
            json.dumps(ai_analysis, ensure_ascii=False)
        ))

        anamnesis_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return anamnesis_id

    def export_to_pdf(self, consultation_id: int, output_path: str):
        """Exporta consulta para PDF"""
        try:
            from fpdf import FPDF
            import tempfile

            # Busca dados da consulta
            conn = sqlite3.connect(self.db_path)
            query = '''
                SELECT p.name, p.birth_date, c.consultation_date,
                       c.chief_complaint, c.symptoms, a.conversation_data,
                       a.symptoms_detected, a.urgency_level, a.ai_analysis
                FROM consultations c
                JOIN patients p ON c.patient_id = p.id
                LEFT JOIN anamnesis a ON c.id = a.consultation_id
                WHERE c.id = ?
            '''

            df = pd.read_sql_query(query, conn, params=[consultation_id])
            conn.close()

            if df.empty:
                return False

            data = df.iloc[0]

            # Cria PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)

            # Cabeçalho
            pdf.cell(0, 10, "Prontuário Odontológico", ln=True, align='C')
            pdf.ln(10)

            # Dados do paciente
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Dados do Paciente:", ln=True)
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 10, f"Nome: {data['name']}", ln=True)
            pdf.cell(0, 10, f"Data de Nascimento: {data['birth_date']}", ln=True)
            pdf.cell(0, 10, f"Data da Consulta: {data['consultation_date']}", ln=True)
            pdf.ln(5)

            # Queixa principal
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Queixa Principal:", ln=True)
            pdf.set_font("Arial", '', 12)
            pdf.multi_cell(0, 10, data['chief_complaint'])
            pdf.ln(5)

            # Análise da IA
            if data['ai_analysis']:
                ai_data = json.loads(data['ai_analysis'])
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, "Análise do Assistente IA:", ln=True)
                pdf.set_font("Arial", '', 12)

                if 'sintomas_identificados' in ai_data:
                    symptoms = ", ".join(ai_data['sintomas_identificados'])
                    pdf.cell(0, 10, f"Sintomas detectados: {symptoms}", ln=True)

                if 'urgencia' in ai_data:
                    pdf.cell(0, 10, f"Nível de urgência: {ai_data['urgencia']}", ln=True)

            pdf.output(output_path)
            return True

        except ImportError:
            print("Biblioteca FPDF não instalada. Instale com: pip install fpdf")
            return False
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            return False

    def export_to_json(self, consultation_id: int, output_path: str):
        """Exporta para JSON"""
        conn = sqlite3.connect(self.db_path)
        query = '''
            SELECT p.*, c.*, a.*
            FROM consultations c
            JOIN patients p ON c.patient_id = p.id
            LEFT JOIN anamnesis a ON c.id = a.consultation_id
            WHERE c.id = ?
        '''

        df = pd.read_sql_query(query, conn, params=[consultation_id])
        conn.close()

        if df.empty:
            return False

        data = df.iloc[0].to_dict()

        # Processa campos JSON
        json_fields = ['conversation_data', 'symptoms_detected', 'ai_analysis']
        for field in json_fields:
            if data.get(field):
                try:
                    data[field] = json.loads(data[field])
                except:
                    pass

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return True

# Integração com o sistema principal
class EHRIntegration:
    def __init__(self):
        self.ehr = ElectronicHealthRecord()

    def save_complete_anamnesis(self, patient_data: Dict,
                               conversation_data: List,
                               agent_analysis: Dict):
        """Salva anamnese completa no prontuário eletrônico"""

        # Adiciona ou busca paciente
        patient_id = self.ehr.add_patient(
            name=patient_data.get('nome', ''),
            birth_date=patient_data.get('data_nascimento', ''),
            phone=patient_data.get('telefone', ''),
            email=patient_data.get('email', '')
        )

        # Adiciona consulta
        consultation_id = self.ehr.add_consultation(
            patient_id=patient_id,
            consultation_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            chief_complaint=agent_analysis.get('queixa_principal', ''),
            symptoms=", ".join(agent_analysis.get('sintomas_identificados', []))
        )

        # Salva anamnese da IA
        anamnesis_id = self.ehr.save_anamnesis(
            consultation_id=consultation_id,
            conversation_data=conversation_data,
            symptoms_detected=agent_analysis.get('sintomas_identificados', []),
            urgency_level=agent_analysis.get('nivel_urgencia', 'baixa'),
            ai_analysis=agent_analysis
        )

        return {
            "patient_id": patient_id,
            "consultation_id": consultation_id,
            "anamnesis_id": anamnesis_id
        }