import os
import time
import random
from dotenv import load_dotenv
from google import genai
from google.genai import types
from Modelos import NotaFiscal
load_dotenv()
class ExtratorAgent:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY não encontrada. "
                "Configure a variável de ambiente."
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

    def extrator(
        self,
        caminho_pdf: str
    ) -> NotaFiscal:
        print("Enviando PDF para o Gemini...")
        arquivo = self.client.files.upload(
            file=caminho_pdf
        )

        print("PDF enviado com sucesso.")

        prompt = """

FORNECEDOR:
- razão social
- fantasia
- CNPJ

FATURADO:
- nome completo
- CPF

NOTA FISCAL:
- número da nota fiscal
- data de emissão

PRODUTOS:
- descrição dos produtos

PARCELAS:
- quantidade de parcelas
- lista de parcelas

Cada parcela deve possuir:
- número
- data de vencimento
- valor

VALOR:
- valor total
"""
        ultimo_erro = None
        for modelo in self.modelos:

            print("")
            print("=" * 60)
            print(f"Tentando modelo: {modelo}")
            print("=" * 60)
            for tentativa in range(3):

                try:

                    print(
                        f"Tentativa {tentativa + 1}/3 "
                        f"com {modelo}..."
                    )

                    resposta = self.client.models.generate_content(
                        model=modelo,

                        contents=[
                            arquivo,
                            prompt
                        ],

                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=NotaFiscal
                        )
                    )
                    print(
                        f"Resposta recebida do modelo: {modelo}"
                    )
                    if not resposta.text:
                        raise RuntimeError(
                            "O Gemini retornou uma resposta vazia."
                        )

                    resultado = NotaFiscal.model_validate_json(
                        resposta.text
                    )

                    print(
                        "Extração concluída com sucesso "
                        f"usando {modelo}."
                    )

                    return resultado

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
                        print(
                            "Erro não temporário. "
                            "Interrompendo tentativas."
                        )
                        raise RuntimeError(
                            "Erro ao processar o PDF no Gemini: "
                            f"{exc}"
                        )
                    if tentativa < 2:
                        espera = 5 * (2 ** tentativa)
                        espera += random.uniform(
                            0,
                            2
                        )
                        print(
                            f"Aguardando {espera:.1f} segundos "
                            "antes da próxima tentativa..."
                        )
                        time.sleep(espera)

            print(
                f"O modelo {modelo} não conseguiu "
                "processar o PDF."
            )
        raise RuntimeError(
            "Gemini não conseguiu processar o PDF. "
            "Todos os modelos e tentativas foram testados. "
            f"Último erro: {ultimo_erro}"
        )