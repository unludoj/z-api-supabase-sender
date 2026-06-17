import os
import logging
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ZAPI_URL = os.getenv("ZAPI_URL")

if not all([SUPABASE_URL, SUPABASE_KEY, ZAPI_URL]):
    logging.error("Variáveis de ambiente não configuradas corretamente no .env")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def obter_contatos():
    try:
        response = supabase.table("contatos").select("*").limit(3).execute()
        return response.data
    except Exception as e:
        logging.error(f"Erro ao buscar contatos no Supabase: {e}")
        return []

def enviar_mensagem(nome, telefone):
    mensagem = f"Olá, {nome} tudo bem com você?"
    payload = {"phone": telefone, "message": mensagem}
    
    try:
        response = requests.post(ZAPI_URL, json=payload, timeout=10)
        response.raise_for_status() 
        
        logging.info(f"Mensagem enviada com sucesso para {nome} ({telefone})")
        return True
        
    except requests.exceptions.Timeout:
        logging.error(f"Timeout ao tentar enviar mensagem para {nome}")
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na requisição da Z-API para {nome}: {e}")
        return False

def main():
    logging.info("Iniciando rotina de envio de mensagens...")
    
    contatos = obter_contatos()
    
    if not contatos:
        logging.warning("Nenhum contato encontrado ou erro de permissão (RLS) no Supabase.")
        return
    
    logging.info(f"{len(contatos)} contato(s) retornado(s) para processamento.")
    
    sucesso = 0
    falha = 0
    
    for contato in contatos:
        nome = contato.get("nome")
        telefone = contato.get("telefone")
        
        if nome and telefone:
            if enviar_mensagem(nome, telefone):
                sucesso += 1
            else:
                falha += 1
        else:
            logging.warning(f"Contato ignorado por falta de dados: {contato}")
            falha += 1
            
    logging.info(f"Resumo da Execução -> Sucesso: {sucesso} | Falha: {falha} | Total: {sucesso + falha}")

if __name__ == "__main__":
    main()