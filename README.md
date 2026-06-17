# Z-API Supabase Sender

Script em Python para leitura de contatos cadastrados no Supabase e disparo de mensagens automatizadas via WhatsApp utilizando a Z-API.

## 1. Setup da Tabela (Supabase)

Execute o script SQL abaixo no painel do Supabase (SQL Editor) para criar a tabela, configurar as políticas de segurança (RLS) e inserir os dados de teste:

```sql
CREATE TABLE IF NOT EXISTS contatos (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  telefone VARCHAR(20) NOT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Configuração de Segurança (RLS)
ALTER TABLE contatos ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir leitura pública dos contatos" ON contatos;

CREATE POLICY "Permitir leitura pública dos contatos" 
ON contatos 
FOR SELECT TO anon USING (true);

-- Inserção de Dados Fictícios para Teste
INSERT INTO contatos (nome, telefone) VALUES
('Contato Teste 1', '5511999999999'),
('Contato Teste 2', '5511888888888');
```
## 2. Variáveis de Ambiente (.env)

Crie um arquivo `.env` na raiz do projeto contendo as suas credenciais de acesso:

```env
SUPABASE_URL=[https://seu-projeto.supabase.co](https://seu-projeto.supabase.co)
SUPABASE_KEY=sua_chave_anon_publica
ZAPI_URL=[https://api.z-api.io/instances/sua_instancia/token/seu_token/send-text](https://api.z-api.io/instances/sua_instancia/token/seu_token/send-text)
ZAPI_CLIENT_TOKEN=seu_client_token_aqui
```

## 3. Como rodar

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o script:
```bash
python main.py
```

## 4. Comprovante de Execução

Abaixo, o registro demonstrando as mensagens disparadas com sucesso via script chegando ao WhatsApp de destino:

<img width="600" alt="WhatsApp Image 2026-06-17 at 20 03 04" src="https://github.com/user-attachments/assets/fc84c189-d357-4b8f-b78c-3b1547913d78" />


