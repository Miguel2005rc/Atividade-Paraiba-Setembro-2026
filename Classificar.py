import os
import time
import random

from dotenv import load_dotenv
from google import genai
from google.genai import types
load_dotenv()
class ClassificarAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY não encontrada. "
                "Configure a variável no arquivo .env."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.modelo_principal = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        )

        self.modelos = [
            self.modelo_principal,
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-3.5-flash"
        ]
    def classificar(self, nota):

        print("")
        print("=" * 60)
        print("AGENTE CLASSIFICADOR")
        print("=" * 60)
        produtos = nota.descricao_produtos

        if not produtos:
            produtos = []

        produtos_texto = "\n".join(
            f"- {produto}"
            for produto in produtos
        )

        prompt = f"""
PRODUTOS DA NOTA:

{produtos_texto}

Utilize uma ou mais das categorias abaixo:

INSUMOS AGRÍCOLAS
- Sementes
- Fertilizantes
- Defensivos Agrícolas
- Corretivos

MANUTENÇÃO E OPERAÇÃO
- Combustíveis/Lubrificantes
- Peças/Parafusos/Componentes Mecânicos
- Manutenção de Máquinas/Equipamentos
- Pneus/Filtros/Correias
- Ferramentas/Utensílios

RECURSOS HUMANOS
- Mão de Obra Temporária
- Salários e Encargos

SERVIÇOS OPERACIONAIS
- Frete/Transporte
- Colheita Terceirizada
- Secagem/Armazenagem
- Pulverização/Aplicação

INFRAESTRUTURA E UTILIDADES
- Energia Elétrica
- Arrendamento de Terras
- Construções/Reformas
- Materiais de Construção

ADMINISTRATIVAS
- Honorários Contábeis/Advocatícios/Agronômicos
- Despesas Bancárias/Financeiras

SEGUROS E PROTEÇÃO
- Seguro Agrícola
- Seguro de Ativos
- Seguro Prestamista

IMPOSTOS E TAXAS
- ITR
- IPTU
- IPVA
- INCRA-CCIR

 INVESTIMENTOS
- Aquisição de Máquinas/Implementos
- Veículos
- Imóveis
- Infraestrutura Rural
Retorne JSON.
Formato:

{{
    "tipo_despesa": [
        "NOME DA CATEGORIA"
    ]
}}
"""
        ultimo_erro = None
        for modelo in self.modelos:

            print("")
            print("-" * 60)
            print(f"Tentando classificar com: {modelo}")
            print("-" * 60)

            for tentativa in range(3):

                try:

                    print(
                        f"Tentativa {tentativa + 1}/3..."
                    )

                    resposta = self.client.models.generate_content(
                        model=modelo,

                        contents=[
                            prompt
                        ],

                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        )
                    )

                    if not resposta.text:
                        raise RuntimeError(
                            "O Gemini retornou uma resposta vazia."
                        )

                    print(
                        "Classificação recebida com sucesso."
                    )

                    import json

                    dados = json.loads(
                        resposta.text
                    )

                    tipo_despesa = dados.get(
                        "tipo_despesa",
                        []
                    )

                    if not isinstance(
                        tipo_despesa,
                        list
                    ):
                        tipo_despesa = [
                            tipo_despesa
                        ]

                    return {
                        "tipo_despesa": tipo_despesa
                    }

                except Exception as exc:
                    ultimo_erro = exc
                    erro_texto = str(exc)
                    print(
                        f"Erro na tentativa "
                        f"{tentativa + 1}/3:"
                    )
                    print(erro_texto)
                    erro_temporario = (
                        "503" in erro_texto
                        or "UNAVAILABLE" in erro_texto
                        or "429" in erro_texto
                        or "RESOURCE_EXHAUSTED" in erro_texto
                        or "408" in erro_texto
                        or "TIMEOUT" in erro_texto.upper()
                    )
                    if not erro_temporario:
                        raise RuntimeError(
                            "Erro ao classificar a despesa: "
                            f"{exc}"
                        )
                    if tentativa < 2:
                        espera = 5 * (
                            2 ** tentativa
                        )
                        espera += random.uniform(
                            0,
                            2
                        )
                        print(
                            f"Aguardando "
                            f"{espera:.1f} segundos..."
                        )

                        time.sleep(
                            espera
                        )
            print(
                f"O modelo {modelo} "
                "não conseguiu classificar."
            )
        raise RuntimeError(
            "Gemini não conseguiu classificar. "
            "Todos os modelos e tentativas foram testados. "
            f"Último erro: {ultimo_erro}"
        )