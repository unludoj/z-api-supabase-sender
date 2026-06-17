import os
import re
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
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")

if not all([SUPABASE_URL, SUPABASE_KEY, ZAPI_URL, ZAPI_CLIENT_TOKEN]):
    logging.error("Variáveis de ambiente não configuradas corretamente no .env")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def validar_telefone(telefone):
    """
    Remove caracteres não numéricos e valida se o telefone 
    possui entre 11 e 13 dígitos (padrão Brasil com ou sem DDI).
    """
    telefone_limpo = re.sub(r'\D', '', str(telefone))
    return bool(re.match(r'^\d{11,13}$', telefone_limpo))

def obter_contatos():
    try:
        response = supabase.table("contatos").select("*").limit(10).execute()
        return response.data
    except Exception as e:
        logging.error(f"Erro ao buscar contatos no Supabase: {e}")
        return []

def enviar_mensagem(nome, telefone):
    mensagem = f"Olá, {nome}, tudo bem com você?"
    payload = {"phone": telefone, "message": mensagem}
    
    headers = {
        "Client-Token": ZAPI_CLIENT_TOKEN,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(ZAPI_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status() 
        
        logging.info(f"Mensagem enviada com sucesso para {nome} ({telefone})")
        return True
        
    except requests.exceptions.Timeout:
        logging.error(f"Timeout ao tentar enviar mensagem para {nome}")
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na requisição da Z-API para {nome}: {e}")
        logging.error(f"Detalhes do bloqueio na Z-API: {e.response.text}")
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
            if not validar_telefone(telefone):
                logging.warning(f"Contato ignorado por telefone inválido: {telefone}")
                falha += 1
                continue

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