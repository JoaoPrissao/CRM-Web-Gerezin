# ❄️ CRM Web Gerezin (SaaS)

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

Um sistema de gestão completo (Software as a Service) desenvolvido sob medida para otimizar a operação e o fluxo financeiro de uma empresa de climatização e manutenção de ar condicionado. 

O objetivo deste projeto é centralizar as informações da operação, oferecendo desde o controle de agenda até a emissão de recibos profissionais, tudo rodando em nuvem com alta segurança.

---

## ✨ Funcionalidades

* **📊 Dashboard de Operações:** Painel com gráficos (*Chart.js*) e indicadores em tempo real de serviços pendentes, concluídos e faturamento.
* **🗓️ Agenda Inteligente:** Calendário interativo (*FullCalendar*) que previne conflitos de horários e separa serviços por cores de status.
* **💰 Módulo Financeiro e Relatórios:** Controle de valores e inadimplência, com exportação instantânea do banco de dados para Excel (`.xlsx`) via *SheetJS*.
* **📄 Emissão de Recibos em PDF:** Geração automática de recibos profissionais no backend (usando `fpdf2`), já formatados com dados do cliente, valor, CNPJ e identidade visual da empresa.
* **🤖 Robô de Retenção (Pós-venda):** Algoritmo que rastreia clientes com mais de 1 ano sem manutenção e gera um link de WhatsApp com abordagem pré-pronta.

---

## 🛡️ Arquitetura, Segurança e Nuvem

O sistema foi arquitetado utilizando os principais padrões da indústria para escalabilidade e segurança:

* **Banco de Dados em Nuvem:** Migração completa para **PostgreSQL (via Supabase)**, garantindo integridade e disponibilidade dos dados 24/7.
* **Conteinerização:** Aplicação empacotada com **Docker** (`Dockerfile`), garantindo que o sistema rode de forma idêntica em qualquer ambiente ou servidor.
* **Autenticação JWT (JSON Web Tokens):** Geração de tokens com tempo de expiração para blindar as rotas da API RESTful.
* **Criptografia Bcrypt:** Senhas "trituradas" e protegidas nativamente.
* **Isolamento de Variáveis (.env):** Chaves secretas e credenciais de banco mantidas estritamente fora do controle de versão.

---

## 🚀 Como rodar o projeto localmente

Siga os passos abaixo no seu terminal para baixar e iniciar o sistema:

```bash
# 1. Clone o repositório
git clone https://github.com/SEU-USUARIO/CRM-Web-Gerezin-SaaS.git

# 2. Entre na pasta
cd CRM-Web-Gerezin-SaaS

# 3. Crie um arquivo .env na raiz do projeto e insira suas credenciais:
# SECRET_KEY=sua_chave_aleatoria
# ADMIN_USERNAME=admin
# ADMIN_PASSWORD=sua_senha_forte
# DATABASE_URL=postgresql://usuario:senha@host:5432/postgres

# 4. Instale as dependências do servidor
pip install -r requirements.txt

# 5. Inicie o motor FastAPI
uvicorn main:app --reload
```

**Passo Final:** Com o servidor rodando, abra o arquivo `index.html` diretamente no seu navegador. O sistema solicitará as credenciais definidas no arquivo `.env` para liberar o acesso corporativo.

---

💼 *Desenvolvido por **João Vitor Prissão Oliveira*** *Estudante de Engenharia da Computação na UTFPR - Apucarana.*