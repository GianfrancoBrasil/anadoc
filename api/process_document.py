<<<<<<< Updated upstream
from fastapi import FastAPI
from fastapi.routing import APIRoute
from typing import List
=======
from fastapi import FastAPI, HTTPException
import os, json, logging
from google.oauth2 import service_account
>>>>>>> Stashed changes

app = FastAPI()

@app.get("/")
<<<<<<< Updated upstream
def root():
    # prova de vida: responde em /api/fast_health
    return {"ok": True, "where": "/api/fast_health"}

@app.get("/routes")
def list_routes() -> List[str]:
    # lista todas as rotas que ESTE app enxerga
    return [getattr(r, "path", str(r)) for r in app.router.routes]
=======
def health():
    return {"ok": True, "where": "/api/process_document"}

def get_gcp_credentials():
    """Lê a credencial da ENV GCP_KEY_JSON e cria Credentials.
       NÃO chama nada de Google fora desta função.
    """
    data = os.environ.get("GCP_KEY_JSON")
    if not data:
        raise RuntimeError("GCP_KEY_JSON ausente nas variáveis de ambiente do Vercel.")
    info = json.loads(data)
    return service_account.Credentials.from_service_account_info(info)


from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
import json
import os
import sys
from google.cloud import documentai_v1 as documentai
from google.cloud.documentai_v1 import types
from manage_processor import enable_document_ai_processor, disable_document_ai_processor, get_processor_name, get_processor_status

# Adicionar o diretório pai ao sys.path para importar conecta_google
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Pydantic Model for Request Validation ---
class DocumentRequest(BaseModel):
    document_url: str
    additional_text: str = None # additional_text is optional

# --- FastAPI Application Instance ---
# --- app = FastAPI() inserido no início

# --- Document AI Processing Function (from previous cell) ---
# Ensure this function is defined in a previous cell or included here
# I will include it here for clarity, but in the notebook, it should be defined before this cell.
# If it's already defined and working in a previous cell, you can remove this definition.

# --- Configuração via variáveis de ambiente ---
project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'soy-involution-472704-t3')
location = os.getenv('DOCUMENT_AI_LOCATION', 'us')
processor_id = os.getenv('DOCUMENT_AI_PROCESSOR_ID', 'd67df7340ec526b5')


def process_document_sample(project_id: str, location: str, processor_id: str, file_path: str, mime_type: str):
    # Crie um cliente Document AI
    client = documentai.DocumentProcessorServiceClient()

    # O nome completo do recurso do processador
    processor_name = client.processor_path(project_id, location, processor_id)

    # Baixe o conteúdo do arquivo a partir do URL
    response = requests.get(file_path)
    response.raise_for_status() # Levanta um erro para códigos de status ruins (4xx ou 5xx)
    image_content = response.content

    # Crie um RawDocument object
    raw_document = types.RawDocument(content=image_content, mime_type=mime_type)

    # Configure a requisição de processamento
    request = types.ProcessRequest(name=processor_name, raw_document=raw_document)

    # Envie a requisição para o processador
    result = client.process_document(request=request)

    # Obtenha o objeto Document do resultado
    document = result.document

    # --- Coletar e formatar a resposta como JSON ---
    extracted_data = {} # Usar um dicionário para a estrutura geral

    if document.entities:
        entities_list = []
        for entity in document.entities:
            entity_info = {
                "Campo": entity.type_,
                "Valor": entity.mention_text,
                "Confiança": round(entity.confidence, 2) # Formatar confiança para 2 casas decimais
            }

            # Adicionar entidades filhas (properties) se existirem
            if entity.properties:
                child_entities = []
                for prop in entity.properties:
                    child_entities.append({
                        "Campo Filho": prop.type_,
                        "Valor Filho": prop.mention_text,
                        "Confiança Filho": round(prop.confidence, 2)
                    })
                entity_info["Entidades Filhas"] = child_entities

            entities_list.append(entity_info)

        extracted_data['Entidades Extraídas'] = entities_list

    else:
        extracted_data['Status'] = "Nenhuma entidade extraída."

    return extracted_data # Return the dictionary instead of printing


# --- FastAPI Endpoint ---
@app.post("/process_document")
def process_document_api(payload: dict):
    try:
        # 1) Inicializa credenciais SÓ AGORA
        creds = get_gcp_credentials()

        # 2) Cria o(s) cliente(s) Google que você usa
        # Exemplo Document AI:
        # client = documentai.DocumentProcessorServiceClient(credentials=creds)
        # parent = client.processor_path(project_id, location, processor_id)
        #
        # 3) Coloque aqui sua LÓGICA atual (o que hoje estava rodando na importação
        #    ou em funções utilitárias que também chamavam credencial na import)

        # TODO: substitua pelo que seu código realmente faz
        # result = client.process_document(request={...})

        return {"ok": True, "received": payload}
    except Exception as e:
        logging.exception("Erro em /process_document")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/processor_status")
def get_processor_status_endpoint():
    try:
        # Se o status consulta algo no Google, inicialize aqui:
        # creds = get_gcp_credentials()
        # client = documentai.DocumentProcessorServiceClient(credentials=creds)
        # ... sua lógica de status ...
        return {"ok": True, "status": "running"}
    except Exception as e:
        logging.exception("Erro em /processor_status")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/enable_processor")
def enable_processor():
    try:
        # Se precisar falar com GCP para "habilitar", faça aqui:
        # creds = get_gcp_credentials()
        # client = documentai.DocumentProcessorServiceClient(credentials=creds)
        # ... sua lógica ...
        return {"ok": True, "processor": "enabled"}
    except Exception as e:
        logging.exception("Erro em /enable_processor")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/disable_processor")
def disable_processor():
    try:
        # Se precisar falar com GCP para "desabilitar", faça aqui:
        # creds = get_gcp_credentials()
        # client = documentai.DocumentProcessorServiceClient(credentials=creds)
        # ... sua lógica ...
        return {"ok": True, "processor": "disabled"}
    except Exception as e:
        logging.exception("Erro em /disable_processor")
        raise HTTPException(status_code=500, detail=str(e))
# Vercel serverless function handler
>>>>>>> Stashed changes

# catch-all para debug: se o roteamento do Vercel “mexer” no caminho,
# você verá aqui qual path realmente chegou ao app.
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def echo_path(path: str):
    return {"received_path": f"/{path}"}
