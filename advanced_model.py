import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    pipeline
)
from llama_cpp import Llama
import os
from typing import Dict, List

class AdvancedDentalModel:
    def __init__(self, model_type="llama-cpp"):
        self.model_type = model_type
        self.model = None
        self.tokenizer = None
        self.setup_model()

    def setup_model(self):
        """Configura o modelo escolhido"""
        try:
            if self.model_type == "llama-cpp":
                self.setup_llama_cpp()
            elif self.model_type == "transformers":
                self.setup_transformers_model()
            elif self.model_type == "mistral":
                self.setup_mistral()
            else:
                self.setup_fallback()
        except Exception as e:
            print(f"Erro ao carregar modelo: {e}")
            self.setup_fallback()

    def setup_llama_cpp(self):
        """Configura LLaMA CPP para melhor performance local"""
        model_path = "models/llama-7b-q4.bin"

        # Download do modelo se não existir
        if not os.path.exists(model_path):
            os.makedirs("models", exist_ok=True)
            print("Baixando modelo LLaMA 7B quantizado...")
            # Aqui você pode adicionar o download do modelo
            # Por exemplo: wget, gdown, ou outro método
            return self.setup_fallback()

        self.model = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_batch=512,
            n_gpu_layers=35,  # Ajuste baseado na sua GPU
            verbose=False
        )
        print("✅ Modelo LLaMA carregado com sucesso")

    def setup_transformers_model(self):
        """Configura modelo transformers com quantização"""
        model_name = "microsoft/DialoGPT-medium"

        # Configuração de quantização para eficiência
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quantization_config,
            device_map="auto",
            torch_dtype=torch.float16
        )
        print("✅ Modelo Transformers carregado com sucesso")

    def setup_mistral(self):
        """Configura modelo Mistral"""
        try:
            from transformers import MistralForCausalLM, MistralTokenizer

            self.tokenizer = MistralTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
            self.model = MistralForCausalLM.from_pretrained(
                "mistralai/Mistral-7B-v0.1",
                device_map="auto",
                load_in_4bit=True,
                torch_dtype=torch.float16
            )
            print("✅ Modelo Mistral carregado com sucesso")
        except Exception as e:
            print(f"Erro ao carregar Mistral: {e}")
            self.setup_fallback()

    def setup_fallback(self):
        """Fallback para modelo simples"""
        print("Usando modelo de fallback")
        self.model_type = "fallback"

    def generate_response(self, prompt: str, context: str = "") -> str:
        """Gera resposta usando o modelo avançado"""

        if self.model_type == "llama-cpp" and self.model:
            return self._generate_llama_response(prompt, context)
        elif self.model_type == "transformers" and self.model:
            return self._generate_transformers_response(prompt, context)
        else:
            return self._generate_fallback_response(prompt)

    def _generate_llama_response(self, prompt: str, context: str) -> str:
        """Gera resposta usando LLaMA CPP"""

        system_prompt = """Você é um assistente virtual especializado em anamnese odontológica.
        Sua função é coletar informações sobre sintomas dentários de maneira profissional e empática.
        Mantenha as respostas claras e focadas na área odontológica."""

        full_prompt = f"""<s>[INST] <<SYS>>
        {system_prompt}
        <</SYS>>

        Contexto anterior: {context}

        Paciente: {prompt} [/INST] Assistente:"""

        try:
            output = self.model(
                full_prompt,
                max_tokens=256,
                temperature=0.7,
                top_p=0.9,
                echo=False,
                stop=["</s>", "[INST]"]
            )

            response = output['choices'][0]['text'].strip()
            return response.split("Assistente:")[-1].strip()

        except Exception as e:
            print(f"Erro na geração LLaMA: {e}")
            return self._generate_fallback_response(prompt)

    def _generate_transformers_response(self, prompt: str, context: str) -> str:
        """Gera resposta usando Transformers"""

        input_text = f"Contexto: {context}\nPaciente: {prompt}\nAssistente:"

        inputs = self.tokenizer.encode(input_text, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=len(inputs[0]) + 128,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                top_p=0.9
            )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.split("Assistente:")[-1].strip()

    def _generate_fallback_response(self, prompt: str) -> str:
        """Resposta de fallback baseada em regras"""
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ["dor", "dói", "dolorido"]):
            return "Entendo que você está sentindo dor. Pode me dizer onde exatamente está localizada a dor e se é constante ou intermitente?"
        elif any(word in prompt_lower for word in ["sangramento", "sangra"]):
            return "Compreendo sobre o sangramento. Isso acontece durante a escovação ou espontaneamente? Há quanto tempo nota isso?"
        else:
            return "Obrigado pela informação. Pode me contar mais detalhes sobre seus sintomas ou preocupações odontológicas?"