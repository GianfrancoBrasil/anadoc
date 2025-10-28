import json
import os
from fastapi import FastAPI, HTTPException
from google.cloud import documentai_v1 as documentai
from google.oauth2 import service_account
# from dotenv import load_dotenv # Para carregar variáveis de ambiente localmente

# Carrega variáveis de ambiente do arquivo .env (apenas para desenvolvimento local)
#load_dotenv()

app = FastAPI()

# --- Configurações do Google Cloud Document AI ---
# Estas variáveis devem ser definidas como variáveis de ambiente
# no Vercel e/ou no seu ambiente local (via .env).
# Exemplo de uso:
# GOOGLE_CLOUD_PROJECT_ID="soy-involution-472704-t3"
# GOOGLE_CLOUD_LOCATION="us"
# GOOGLE_CLOUD_PROCESSOR_ID="SEU_PROCESSOR_ID_AQUI" (ex: d67df7340ec526b5)
# GCP_KEY_JSON="conteúdo do JSON de credenciais como string"

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
PROCESSOR_ID = os.getenv("GOOGLE_CLOUD_PROCESSOR_ID")
GCP_KEY_JSON = os.getenv("GCP_KEY_JSON")

# --- Validação de Configuração ---
if not all([PROJECT_ID, LOCATION, PROCESSOR_ID, GCP_KEY_JSON]):
    raise ValueError(
        "As variáveis de ambiente GOOGLE_CLOUD_PROJECT_ID, GOOGLE_CLOUD_LOCATION, "
        "GOOGLE_CLOUD_PROCESSOR_ID e GCP_KEY_JSON devem ser definidas."
    )

# --- Autenticação Google Cloud ---
credentials = service_account.Credentials.from_service_account_info(json.loads(GCP_KEY_JSON))

# --- Cliente Document AI (instanciado uma vez por cold start da função) ---
# O cliente será reutilizado para requisições subsequentes dentro da mesma execução da função serverless.
documentai_client = documentai.DocumentProcessorServiceClient(credentials=credentials)

@app.get("/")
async def read_root():
    """Endpoint de teste simples para verificar se a API está funcionando."""
    return {"message": "Document AI Processor Status API is running!"}

@app.get("/processor-status")
async def get_processor_status():
    """
    Retorna o status atual do processador do Google Cloud Document AI.
    """
    try:
        # Constrói o nome completo do recurso do processador
        processor_name = documentai_client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)

        # Busca as informações do processador
        processor = documentai_client.get_processor(name=processor_name)

        # Mapeia o estado numérico para uma string legível
        # Os valores possíveis para processor.state são definidos em google.cloud.documentai_v1.Processor.State
        status_map = {
            documentai.Processor.State.UNSPECIFIED: "Não Especificado",
            documentai.Processor.State.ENABLED: "Ativado",
            documentai.Processor.State.DISABLED: "Desativado",
            documentai.Processor.State.CREATING: "Criando",
            documentai.Processor.State.FAILED: "Falhou",
            documentai.Processor.State.DELETING: "Excluindo",
            documentai.Processor.State.UPDATING: "Atualizando",
            documentai.Processor.State.TRAINING: "Treinando",
            documentai.Processor.State.DEPLOYING: "Implantando",
            documentai.Processor.State.UNDEPLOYING: "Desimplantando"
        }
        
        status_string = status_map.get(processor.state, "Estado Desconhecido")

        return {
            "processor_id": processor.name.split('/')[-1], # Extrai o ID do nome completo
            "display_name": processor.display_name,
            "type": processor.type,
            "status": status_string,
            "last_updated_time": processor.update_time.isoformat() if processor.update_time else None
        }

    except Exception as e:
        # Captura qualquer exceção e retorna um erro HTTP 500
        raise HTTPException(status_code=500, detail=f"Erro ao obter o status do processador: {str(e)}")

# Para Vercel, o FastAPI automaticamente cria o 'app' como o ponto de entrada.
# Para execução local, você pode usar:
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

