import os
import logging
import tempfile
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def configurar_credenciais_google(json_key_path: str = 'app/config/soy-involution-472704-t3-4a5f3e402510.json'):
    """
    Configura as credenciais do Google Cloud definindo a variável de ambiente GOOGLE_APPLICATION_CREDENTIALS.
    Prioriza a variável de ambiente GCP_KEY_JSON se disponível, caso contrário usa o arquivo JSON.

    Args:
        json_key_path (str): Caminho para o arquivo de chave JSON do serviço Google Cloud (fallback).

    Returns:
        bool: True se configurado com sucesso, False caso contrário.
    """
    # Verificar se a variável de ambiente GCP_KEY_JSON está definida
    gcp_key_json = os.getenv('GCP_KEY_JSON')
    if gcp_key_json:
        try:
            # Tentar parsear o JSON para validar
            key_data = json.loads(gcp_key_json)
            # Criar arquivo temporário com o conteúdo JSON
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(key_data, temp_file)
                temp_file_path = temp_file.name
            # Configurar a variável de ambiente para o arquivo temporário
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path
            logger.info("Credenciais configuradas via variável de ambiente GCP_KEY_JSON (arquivo temporário).")
            return True
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear GCP_KEY_JSON: {e}")
            return False
    else:
        # Fallback para arquivo JSON
        if not os.path.exists(json_key_path):
            logger.error(f"Erro: O arquivo '{json_key_path}' não foi encontrado e GCP_KEY_JSON não está definida.")
            return False
        # Configura a variável de ambiente para autenticação
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(json_key_path)
        logger.info("Credenciais configuradas via arquivo JSON.")
        return True

# Para compatibilidade com execução direta do script
if __name__ == "__main__":
    configurar_credenciais_google()