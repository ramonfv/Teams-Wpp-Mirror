WhatsApp Teams Bridge
Middleware experimental para validar o espelhamento de mensagens entre um grupo WhatsApp e um canal do Microsoft Teams.
Nesta etapa inicial, não há integração real com WhatsApp ainda. O objetivo é simular uma mensagem recebida do WhatsApp e publicá-la em um canal do Teams usando um webhook/workflow.


---
1. Tecnologias usadas nesta etapa
Python 3.11+
FastAPI
Uvicorn
HTTPX
Pydantic
Pydantic Settings
Python Dotenv
Microsoft Teams Workflows/Webhook
---
2. Pré-requisitos
Antes de começar, instale:
Obrigatórios
Python 3.11 ou superior
Git
Visual Studio Code
Acesso a um Microsoft Teams da organização
Permissão para criar Workflow/Webhook no canal do Teams
Recomendados
Postman ou Insomnia
Windows Terminal ou PowerShell
Extensão Python no VS Code
---
3. Criando o projeto
No terminal, escolha uma pasta onde deseja criar o projeto:
```bash
mkdir whatsapp-teams-bridge
cd whatsapp-teams-bridge
```
Inicialize o repositório Git:
```bash
git init
```
Crie a estrutura de pastas:
```bash
mkdir app
mkdir app/domain
mkdir app/services
mkdir app/adapters
mkdir tests
```
No Windows PowerShell, se preferir criar os arquivos pelo terminal:
```powershell
New-Item app/__init__.py
New-Item app/domain/__init__.py
New-Item app/services/__init__.py
New-Item app/adapters/__init__.py
New-Item app/main.py
New-Item app/config.py
New-Item app/domain/message.py
New-Item app/adapters/teams_webhook_sender.py
New-Item app/adapters/whatsapp_mock_receiver.py
New-Item app/services/message_router.py
New-Item requirements.txt
New-Item .env.example
New-Item .gitignore
New-Item README.md
```
Estrutura esperada:
```text
whatsapp-teams-bridge/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── domain/
│   │   ├── __init__.py
│   │   └── message.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── message_router.py
│   └── adapters/
│       ├── __init__.py
│       ├── teams_webhook_sender.py
│       └── whatsapp_mock_receiver.py
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```
---
4. Criando o ambiente virtual
Na raiz do projeto:
```bash
python -m venv .venv
```
Ative o ambiente virtual.
Windows PowerShell
```powershell
.venv\Scripts\Activate.ps1
```
Se o PowerShell bloquear a ativação, execute uma vez:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Depois tente ativar novamente:
```powershell
.venv\Scripts\Activate.ps1
```
Windows CMD
```cmd
.venv\Scripts\activate.bat
```
Linux/Mac
```bash
source .venv/bin/activate
```
Quando ativado, o terminal deve mostrar algo como:
```text
(.venv) PS C:\...
```
---
5. Instalando dependências
Preencha o arquivo `requirements.txt`:
```txt
fastapi
uvicorn[standard]
httpx
pydantic
pydantic-settings
python-dotenv
```
Instale:
```bash
pip install -r requirements.txt
```
---
6. Criando o webhook/workflow no Microsoft Teams
No Microsoft Teams:
Entre na equipe desejada.
Crie ou escolha um canal, por exemplo: `Espelho WhatsApp`.
Clique nos três pontos `...` do canal.
Procure por `Workflows`.
Escolha um modelo relacionado a receber uma solicitação de webhook e postar no canal.
Configure o workflow para postar a mensagem no canal.
Copie a URL do webhook gerada.
Essa URL será usada pela aplicação FastAPI.
---
7. Configuração de ambiente
Crie um arquivo `.env` na raiz do projeto.
Nunca suba o `.env` para o GitHub.
Conteúdo:
```env
TEAMS_WEBHOOK_URL=https://sua-url-do-webhook-aqui
APP_ENV=local
```
Crie também o `.env.example`:
```env
TEAMS_WEBHOOK_URL=https://example.webhook.office.com/...
APP_ENV=local
```
---


```
# Teams Wpp Mirror

Middleware experimental para espelhar mensagens entre grupos WhatsApp e canais do Microsoft Teams.

O projeto atualmente implementa um MVP local com FastAPI, SQLite, Microsoft Teams Workflow/Webhook e fluxos mock para WhatsApp e Teams.

---

## Current status

This project currently supports:

```text
Mock WhatsApp → FastAPI → Teams Workflow/Webhook
Mock Teams → FastAPI → Authorized Outbox → Mock WhatsApp Sender