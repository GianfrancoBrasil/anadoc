import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def configurar_credenciais_google(json_key_path: str = 'app/config/soy-involution-472704-t3-4a5f3e402510.json'):
    """
    Configura as credenciais do Google Cloud definindo a variável de ambiente GOOGLE_APPLICATION_CREDENTIALS.

    Args:
        json_key_path (str): Caminho para o arquivo de chave JSON do serviço Google Cloud.

    Returns:
        bool: True se configurado com sucesso, False caso contrário.
    """
    # Verifica se o arquivo existe
    if not os.path.exists(json_key_path):
        logger.error(f"Erro: O arquivo '{json_key_path}' não foi encontrado. Certifique-se de que você fez o upload e o nome do arquivo está correto.")
        return False

    # Configura a variável de ambiente para autenticação
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(json_key_path)

    logger.info("Variável de ambiente GOOGLE_APPLICATION_CREDENTIALS configurada com sucesso.")
    logger.info("Agora você pode executar as operações que utilizam as credenciais do Google Cloud.")
    return True

# Para compatibilidade com execução direta do script
if __name__ == "__main__":
    configurar_credenciais_google()