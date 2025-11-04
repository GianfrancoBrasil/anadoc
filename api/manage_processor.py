# Funções utilitárias para gerenciamento de processadores Document AI
import os
import logging
import sys
from google.cloud import documentai_v1 as documentai

# Adicionar o diretório pai ao sys.path para importar conecta_google
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.conecta_google import configurar_credenciais_google

# Configurar credenciais do Google Cloud
configurar_credenciais_google()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuração via variáveis de ambiente ---
project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'soy-involution-472704-t3')
location = os.getenv('DOCUMENT_AI_LOCATION', 'us')
processor_id = os.getenv('DOCUMENT_AI_PROCESSOR_ID', 'd67df7340ec526b5')

def get_processor_name(project_id: str, location: str, processor_id: str) -> str:
    """Constrói o nome completo do recurso do processador."""
    client = documentai.DocumentProcessorServiceClient()
    return client.processor_path(project_id, location, processor_id)

def enable_document_ai_processor(project_id: str, location: str, processor_id: str):
    """Ativa um processador do Document AI."""
    client = documentai.DocumentProcessorServiceClient()
    processor_name = get_processor_name(project_id, location, processor_id)

    logger.info(f"Tentando ativar o processador: {processor_name}")
    try:
        request = documentai.EnableProcessorRequest(name=processor_name)
        operation = client.enable_processor(request=request)

        # A operação de ativar/desativar é assíncrona, então esperamos sua conclusão.
        logger.info("Operação de ativação iniciada. Aguardando conclusão...")
        response = operation.result() # Isso bloqueia até a conclusão da operação

        logger.info(f"Processador {processor_name} ATIVADO com sucesso.")
        return {"status": "success", "message": f"Processador {processor_name} ativado"}

    except Exception as e:
        logger.error(f"Erro ao ativar o processador {processor_name}: {e}")
        raise e

def disable_document_ai_processor(project_id: str, location: str, processor_id: str):
    """Desativa um processador do Document AI."""
    client = documentai.DocumentProcessorServiceClient()
    processor_name = get_processor_name(project_id, location, processor_id)

    logger.info(f"Tentando desativar o processador: {processor_name}")
    try:
        request = documentai.DisableProcessorRequest(name=processor_name)
        operation = client.disable_processor(request=request)

        # A operação de ativar/desativar é assíncrona, então esperamos sua conclusão.
        logger.info("Operação de desativação iniciada. Aguardando conclusão...")
        response = operation.result() # Isso bloqueia até a conclusão da operação

        logger.info(f"Processador {processor_name} DESATIVADO com sucesso.")
        return {"status": "success", "message": f"Processador {processor_name} desativado"}

    except Exception as e:
        logger.error(f"Erro ao desativar o processador {processor_name}: {e}")
        raise e

# Função para obter status do processador
def get_processor_status(project_id: str, location: str, processor_id: str):
    """Obtém o status atual de um processador do Document AI."""
    client = documentai.DocumentProcessorServiceClient()
    processor_name = get_processor_name(project_id, location, processor_id)

    try:
        processor = client.get_processor(name=processor_name)
        return {
            "processor_id": processor_id,
            "state": processor.state.name,
            "display_name": processor.display_name,
            "create_time": processor.create_time.isoformat() if processor.create_time else None
        }
    except Exception as e:
        logger.error(f"Erro ao obter status do processador {processor_name}: {e}")
        raise e