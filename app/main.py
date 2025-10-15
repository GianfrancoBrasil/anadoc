import os
import requests
import json # Importar a biblioteca json
from google.cloud import documentai_v1 as documentai
from google.cloud.documentai_v1 import types


# --- Configuração (substitua pelos seus valores) ---
project_id = 'soy-involution-472704-t3'  # Seu ID de projeto
location = 'us'  # A região do seu processador
processor_id = 'd67df7340ec526b5' # O ID do seu processador implantado
file_path = 'https://s3.sa-east-1.amazonaws.com/cdn-sctreinamentos.selecao.site/candidato/banca/arquivos/3723d90e5619347293f5b9410e32160a/d8458df6a4da4766547b6b233c5e2b9b.PDF' # Caminho para o documento que você quer processar
mime_type = 'application/pdf' # Tipo MIME do documento (ex: 'application/pdf', 'image/jpeg')

# Configure a variável de ambiente para autenticação
# Exemplo: os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/caminho/para/seu-arquivo-chave.json"
# Certifique-se de que suas credenciais de autenticação estejam configuradas corretamente
# para acessar os serviços do Google Cloud, por exemplo, usando `google.colab.auth`
# ou configurando a variável de ambiente GOOGLE_APPLICATION_CREDENTIALS.

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

    # Adicionar texto completo ao JSON (opcional, descomente se precisar)
    # extracted_data['full_text'] = document.text


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

    # Converter o dicionário para string JSON e imprimir
    print(json.dumps(extracted_data, indent=2, ensure_ascii=False)) # Usar indent para formatação legível, ensure_ascii=False para caracteres especiais

# --- Chame a função de exemplo ---
if __name__ == "__main__":
    process_document_sample(project_id, location, processor_id, file_path, mime_type)