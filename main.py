import asyncio
import os
import tempfile
import uuid
from pathlib import Path

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Request
)

from fastapi.responses import (
    FileResponse,
    RedirectResponse,
    JSONResponse
)

from starlette.middleware.sessions import SessionMiddleware

from extrator import ExtratorAgent
from Classificar import ClassificarAgent

load_dotenv()


app = FastAPI(
    title="Agente Financeiro",
    description="Sistema de processamento de notas fiscais com Agentes de IA",
    version="1.0.0"
)


SESSION_SECRET = os.getenv(
    "SESSION_SECRET",
    "chave-local-desenvolvimento"
)


HTTPS_ONLY = (
    os.getenv(
        "HTTPS_ONLY",
        "false"
    ).lower()
    == "true"
)
MAX_PDF_SIZE = 50 * 1024 * 1024
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="finance_session",
    max_age=8 * 60 * 60,
    same_site="lax",
    https_only=HTTPS_ONLY
)
try:
    extrator = ExtratorAgent()
    classificar = ClassificarAgent()
except Exception as erro:
    print(
        "ERRO AO INICIALIZAR OS AGENTES:"
    )
    print(
        repr(erro)
    )
    extrator = None
    classificar = None
trabalhos = {}
def criar_trabalho(
    trabalho_id: str,
    status: str,
    mensagem: str,
    resultado=None
):
    trabalhos[
        trabalho_id
    ] = {

        "status":
        status,
        "message":
        mensagem,
        "mensagem":
        mensagem,
        "result":
        resultado,
        "resultado":
        resultado
    }
@app.get("/")
async def inicio(
    request: Request
):
    if not request.session.get(
        "logado"
    ):
        return RedirectResponse(
            "/login"
        )
    return FileResponse(
        "index.html"
    )
@app.get("/login")
async def pagina_login():
    caminho_login = Path(
        "login.html"
    )
    if not caminho_login.exists():
        return JSONResponse(
            status_code=500,
            content={
                "detail":
                "O arquivo login.html não foi encontrado na pasta do projeto."
            }
        )
    return FileResponse(
        caminho_login
    )

@app.post("/login")
async def fazer_login(
    request: Request
):
    try:
        formulario = await request.form()
        usuario = formulario.get(
            "usuario"
        )
        senha = formulario.get(
            "senha"
        )
        usuario_correto = os.getenv(
            "ADMIN_USER",
            ""
        )
        senha_correta = os.getenv(
            "ADMIN_PASSWORD",
            ""
        )
        if not usuario_correto:

            usuario_correto = (
                "AnaJamyle_Miguel_Vinicius"
            )


        if not senha_correta:

            senha_correta = (
                "poiu7654321"
            )


        if (
            usuario == usuario_correto
            and
            senha == senha_correta
        ):

            request.session[
                "logado"
            ] = True


            return RedirectResponse(

                "/",

                status_code=303
            )


        return RedirectResponse(

            "/login?erro=1",

            status_code=303
        )


    except Exception as erro:

        print(
            "ERRO NO LOGIN:"
        )

        print(
            repr(erro)
        )


        return JSONResponse(

            status_code=500,

            content={
                "detail":
                "Erro ao realizar login."
            }
        )

@app.get("/logout")
async def logout(
    request: Request
):
    request.session.clear()
    return RedirectResponse(
        "/login"
    )
@app.get("/api/health")
async def health():

    return {
        "status":
        "online",
        "sistema":
        "Agente Financeiro",
        "extrator":
        extrator is not None,
        "classificador":
        classificar is not None
    }
@app.post("/api/extrair")
async def iniciar_trabalho(
    request: Request,
    arquivo: UploadFile = File(...)
):
    if not request.session.get(
        "logado"
    ):
        return JSONResponse(
            status_code=401,
            content={
                "detail":
                "Usuário não autenticado."
            }
        )
    if extrator is None:
        return JSONResponse(
            status_code=500,
            content={
                "detail":
                "O ExtratorAgent não foi inicializado."
            }
        )
    if classificar is None:
        return JSONResponse(
            status_code=500,
            content={
                "detail":
                "O ClassificarAgent não foi inicializado."
            }
        )
    if not arquivo.filename:
        return JSONResponse(
            status_code=400,
            content={
                "detail":
                "Nenhum arquivo foi enviado."
            }
        )
    if not arquivo.filename.lower().endswith(
        ".pdf"
    ):
        return JSONResponse(
            status_code=400,
            content={
                "detail":
                "O arquivo precisa estar no formato PDF."
            }
        )
    try:
        conteudo = await arquivo.read()
    except Exception as erro:
        return JSONResponse(
            status_code=400,
            content={
                "detail":
                f"Não foi possível ler o PDF: {erro}"
            }
        )
    if len(conteudo) == 0:
        return JSONResponse(
            status_code=400,
            content={
                "detail":
                "O PDF está vazio."
            }
        )
    if len(conteudo) > MAX_PDF_SIZE:
        return JSONResponse(
            status_code=400,
            content={
                "detail":
                "O PDF deve ter no máximo 50 MB."
            }
        )
    trabalho_id = str(
        uuid.uuid4()
    )
    criar_trabalho(
        trabalho_id,
        "aguardando",
        "PDF recebido. Aguardando processamento.",
        None
    )
    try:
        pasta_temporaria = (
            tempfile.gettempdir()
        )

        caminho_pdf = (
            Path(pasta_temporaria)
            /
            f"{trabalho_id}.pdf"
        )
        caminho_pdf.write_bytes(
            conteudo
        )
    except Exception as erro:
        criar_trabalho(
            trabalho_id,
            "erro",
            f"Erro ao salvar o PDF: {erro}",
            None
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail":
                f"Erro ao salvar o PDF: {erro}",
                "trabalho_id":
                trabalho_id
            }
        )
    asyncio.create_task(
        processar_trabalho(
            trabalho_id,
            str(caminho_pdf)
        )
    )
    return JSONResponse(
        status_code=200,
        content={
            "sucesso":
            True,
            "trabalho_id":
            trabalho_id,
            "status":
            "aguardando",
            "message":
            "PDF enviado com sucesso.",
            "mensagem":
            "PDF enviado com sucesso."
        }
    )
async def processar_trabalho(
    trabalho_id: str,
    caminho_pdf: str
):
    try:
        print(
            f"\n[{trabalho_id}] Iniciando ExtratorAgent..."
        )
        criar_trabalho(
            trabalho_id,
            "processando",
            " Agente Extrator analisando o PDF...",
            None
        )
        print(
            "Enviando PDF para o Gemini..."
        )
        resultado = await asyncio.to_thread(
            extrator.extrator,
            caminho_pdf
        )
        print(
            "PDF processado pelo ExtratorAgent."
        )
        criar_trabalho(
            trabalho_id,
            "processando",
            "Agente Classificador analisando as despesas...",
            None
        )
        print(
            "Iniciando ClassificarAgent..."
        )

        classificacao = await asyncio.to_thread(
            classificar.classificar,
            resultado
        )
        print(
            "Classificação concluída."
        )
        if hasattr(
            resultado,
            "model_dump"
        ):
            resultado_final = (
                resultado.model_dump()
            )
        elif isinstance(
            resultado,
            dict
        ):
            resultado_final = (
                resultado.copy()
            )
        else:
            resultado_final = {
                "dados":
                resultado
            }
        if hasattr(
            classificacao,
            "model_dump"
        ):
            classificacao = (
                classificacao.model_dump()
            )
        if isinstance(
            classificacao,
            dict
        ):
            resultado_final[
                "tipo_despesa"
            ] = classificacao.get(
                "tipo_despesa",
                []
            )
        criar_trabalho(
            trabalho_id,
            "concluido",
            " Dados extraídos e classificados com sucesso.",
            resultado_final
        )
        print(
            f"[{trabalho_id}] Trabalho concluído com sucesso."
        )
    except Exception as erro:
        print(
            "\n============================================================"
        )
        print(
            "ERRO NO TRABALHO"
        )
        print(
            f"[{trabalho_id}]"
        )
        print(
            repr(erro)
        )
        print(
            "============================================================\n"
        )

        criar_trabalho(
            trabalho_id,
            "erro",
            str(erro),
            None
        )
    finally:
        try:
            Path(
                caminho_pdf
            ).unlink(
                missing_ok=True
            )
            print(
                f"[{trabalho_id}] PDF temporário removido."
            )
        except Exception as erro:
            print(
                f"Erro ao remover PDF temporário: {erro}"
            )
@app.get(
    "/api/status/{trabalho_id}"
)
async def consultar_trabalho(
    request: Request,
    trabalho_id: str
):
    if not request.session.get(
        "logado"
    ):
        return JSONResponse(
            status_code=401,
            content={
                "detail":
                "Usuário não autenticado."
            }
        )
    trabalho = trabalhos.get(
        trabalho_id
    )
    if trabalho is None:
        return JSONResponse(
            status_code=404,
            content={
                "detail":
                "Trabalho não encontrado.",
                "trabalho_id":
                trabalho_id
            }
        )
    status = trabalho.get(
        "status",
        "desconhecido"
    )
    mensagem = trabalho.get(
        "message",
        trabalho.get(
            "mensagem",
            ""
        )
    )
    resultado = trabalho.get(
        "result",
        trabalho.get(
            "resultado",
            None
        )
    )
    return JSONResponse(
        status_code=200,
        content={
            "trabalho_id":
            trabalho_id,
            "status":
            status,
            "message":
            mensagem,
            "mensagem":
            mensagem,
            "result":
            resultado,
            "resultado":
            resultado
        }
    )
@app.delete(
    "/api/trabalhos/{trabalho_id}"
)
async def excluir_trabalho(
    request: Request,
    trabalho_id: str
):
    if not request.session.get(
        "logado"
    ):
        return JSONResponse(
            status_code=401,
            content={
                "detail":
                "Usuário não autenticado."
            }
        )
    if trabalho_id not in trabalhos:
        return JSONResponse(
            status_code=404,
            content={
                "detail":
                "Trabalho não encontrado."
            }
        )
    del trabalhos[
        trabalho_id
    ]
    return {
        "sucesso":
        True,
        "mensagem":
        "Trabalho removido."
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )