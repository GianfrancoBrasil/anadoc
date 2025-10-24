@app.get("/")
def health():
    return {"ok": True, "where": "/api/process_document"}

from fastapi import FastAPI
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
from app.conecta_google import configurar_credenciais_google

# Configurar credenciais do Google Cloud
configurar_credenciais_google()

# --- Pydantic Model for Request Validation ---
class DocumentRequest(BaseModel):
    document_url: str
    additional_text: str = None # additional_text is optional

# --- FastAPI Application Instance ---
app = FastAPI()

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
async def process_document_api(request_data: DocumentRequest):
    document_url = request_data.document_url
    additional_text = request_data.additional_text

    if not document_url:
        return JSONResponse(content={"error": "URL do documento não fornecida"}, status_code=400)

    # Determine mime_type (assuming PDF for now, you might need more sophisticated logic)
    mime_type = 'application/pdf'

    try:
        # Call the document processing function
        extracted_data = process_document_sample(project_id, location, processor_id, document_url, mime_type)

        # Incorporate additional_text (placeholder)
        response_content = {
            "status": "Processado",
            "document_url_recebida": document_url,
            "texto_adicional_recebido": additional_text,
            "dados_extraidos": extracted_data
        }

        return JSONResponse(content=response_content, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": f"Erro ao processar o documento: {e}"}, status_code=500)

# --- Processor Management Endpoints ---
@app.post("/enable_processor")
async def enable_processor():
    try:
        enable_document_ai_processor(project_id, location, processor_id)
        return JSONResponse(content={"status": "Processador ativado com sucesso"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": f"Erro ao ativar processador: {e}"}, status_code=500)

@app.post("/disable_processor")
async def disable_processor():
    try:
        disable_document_ai_processor(project_id, location, processor_id)
        return JSONResponse(content={"status": "Processador desativado com sucesso"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": f"Erro ao desativar processador: {e}"}, status_code=500)

@app.get("/processor_status")
async def get_processor_status_endpoint():
    try:
        status = get_processor_status(project_id, location, processor_id)
        return JSONResponse(content=status, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": f"Erro ao obter status do processador: {e}"}, status_code=500)

# Vercel serverless function handler
from mangum import Mangum
handler = Mangum(app)
