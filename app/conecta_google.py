import os
#from google.colab import files

# Substitua 'seu-arquivo-chave.json' pelo nome do arquivo que você fez upload
json_key_path = 'app/config/soy-involution-472704-t3-4a5f3e402510.json'

# Verifica se o arquivo existe (opcional, mas recomendado)
if not os.path.exists(json_key_path):
  print(f"Erro: O arquivo '{json_key_path}' não foi encontrado. Certifique-se de que você fez o upload e o nome do arquivo está correto.")
else:
  # Configura a variável de ambiente para autenticação
  #os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_key_path
  os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(json_key_path)

  print("Variável de ambiente GOOGLE_APPLICATION_CREDENTIALS configurada com sucesso.")
  print("Agora você pode executar as células que utilizam as credenciais do Google Cloud.")

  #$env:GOOGLE_APPLICATION_CREDENTIALS="app/config/soy-involution-472704-t3-4a5f3e402510.json"