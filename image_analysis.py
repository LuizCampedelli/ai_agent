import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
import os
from datetime import datetime

class DentalImageAnalyzer:
    def __init__(self):
        self.setup_model()
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def setup_model(self):
        """Configura modelo para análise de imagens dentárias"""
        try:
            # Usando um modelo pré-treinado e adaptando para odontologia
            self.model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', pretrained=True)
            self.model.eval()

            # Simulando uma adaptação para odontologia
            # Em produção, você teria um modelo treinado especificamente
            self.dental_conditions = {
                0: "Cárie detectada",
                1: "Doença periodontal",
                2: "Abscesso periapical",
                3: "Fratura dental",
                4: "Normal"
            }

        except Exception as e:
            print(f"Erro ao carregar modelo de imagem: {e}")
            self.model = None

    def analyze_xray(self, image_path):
        """Analisa radiografia odontológica"""
        if not self.model:
            return {"error": "Modelo não disponível"}

        try:
            # Carrega e processa imagem
            image = Image.open(image_path).convert('RGB')
            input_tensor = self.transform(image).unsqueeze(0)

            # Análise
            with torch.no_grad():
                outputs = self.model(input_tensor)
                _, predicted = torch.max(outputs, 1)

            condition_id = predicted.item() % len(self.dental_conditions)
            condition = self.dental_conditions[condition_id]

            # Análise adicional com OpenCV
            cv_analysis = self._opencv_analysis(image_path)

            return {
                "condicao_principal": condition,
                "analise_cv": cv_analysis,
                "confianca": 0.85,  # Simulado
                "recomendacoes": self._get_recommendations(condition)
            }

        except Exception as e:
            return {"error": f"Erro na análise: {str(e)}"}

    def _opencv_analysis(self, image_path):
        """Análise usando OpenCV para características visuais"""
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            return {}

        # Análise básica de características
        analysis = {}

        # Detecta bordas (possíveis fraturas)
        edges = cv2.Canny(image, 100, 200)
        analysis["intensidade_bordas"] = np.sum(edges) / (image.shape[0] * image.shape[1])

        # Análise de histograma
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        analysis["brilho_medio"] = np.mean(image)
        analysis["contraste"] = np.std(image)

        # Detecta áreas escuras (possíveis cáries)
        _, dark_areas = cv2.threshold(image, 50, 255, cv2.THRESH_BINARY_INV)
        analysis["areas_escuras"] = np.sum(dark_areas == 255) / (image.shape[0] * image.shape[1])

        return analysis

    def _get_recommendations(self, condition):
        """Retorna recomendações baseadas na condição"""
        recommendations = {
            "Cárie detectada": [
                "Restauração com resina composta",
                "Avaliação de extensão da lesão",
                "Controle dietético"
            ],
            "Doença periodontal": [
                "Raspagem e alisamento radicular",
                "Acompanhamento periodontal",
                "Melhoria da higiene oral"
            ],
            "Abscesso periapical": [
                "Tratamento endodôntico urgente",
                "Drenagem se necessário",
                "Antibioticoterapia"
            ],
            "Fraturas dental": [
                "Avaliação de extensão da fratura",
                "Restauração ou coroa",
                "Possível tratamento endodôntico"
            ],
            "Normal": [
                "Manutenção da saúde oral",
                "Controle regular a cada 6 meses"
            ]
        }

        return recommendations.get(condition, ["Avaliação clínica complementar"])

    def analyze_intraoral_photo(self, image_path):
        """Analisa fotos intraorais"""
        # Similar à análise de radiografia, mas focado em tecidos moles
        image = cv2.imread(image_path)

        analysis = {
            "tipo_analise": "Foto Intraoral",
            "observacoes": [
                "Análise de tecidos moles",
                "Verificação de inflamação gengival",
                "Avaliação de restaurações existentes"
            ]
        }

        # Análise de cor para detectar inflamação
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Faixa para tecido inflamado (vermelho)
        lower_red = np.array([0, 50, 50])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)

        inflammation_ratio = np.sum(mask > 0) / (image.shape[0] * image.shape[1])
        analysis["indicador_inflamacao"] = inflammation_ratio

        return analysis

# Integração com Streamlit
class StreamlitImageAnalyzer:
    def __init__(self):
        self.analyzer = DentalImageAnalyzer()

    def process_uploaded_image(self, uploaded_file):
        """Processa imagem uploadada no Streamlit"""
        # Salva arquivo temporariamente
        file_path = f"temp_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Determina tipo de análise baseado no nome do arquivo
        if any(term in uploaded_file.name.lower() for term in ['xray', 'radiografia', 'raio']):
            analysis = self.analyzer.analyze_xray(file_path)
        else:
            analysis = self.analyzer.analyze_intraoral_photo(file_path)

        # Limpa arquivo temporário
        os.remove(file_path)

        return analysis