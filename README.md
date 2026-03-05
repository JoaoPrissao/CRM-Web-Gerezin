# ❄️ CRM Web Gerezin (SaaS)

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

Um sistema de gestão completo (Software as a Service) desenvolvido sob medida para otimizar a operação e o fluxo financeiro de uma empresa de climatização e manutenção de ar condicionado. 

O objetivo deste projeto é eliminar o uso de papel, unificar informações e evitar furos na agenda, tudo em uma interface de página única (SPA) rápida e responsiva.

---

## ✨ Funcionalidades

O sistema foi dividido em módulos inteligentes focados em resolver problemas reais do dia a dia do prestador de serviço:

* **📊 Dashboard de Operações:** Painel de controle com gráficos (*Chart.js*) e indicadores em tempo real de serviços pendentes, concluídos e faturamento.
* **🗓️ Visão de Calendário:** Agenda visual interativa (*FullCalendar*) que diferencia serviços na fila (azul) e já concluídos (verde).
* **📋 Gestão de Fila e Histórico:** Sistema de entrada e saída de clientes, com busca instantânea no banco de dados.
* **💰 Módulo Financeiro Avançado:** Controle de valores recebidos e pendentes, com geração automática de relatórios em Excel (`.xlsx`) via *SheetJS*.
* **🤖 Robô de Retenção (Pós-venda):** Aba inteligente que rastreia clientes que não fazem manutenção há mais de 1 ano e gera um link direto para o WhatsApp com uma mensagem de abordagem pré-pronta.

---

## 🛡️ Arquitetura e Segurança (Nível Comercial)

O backend do sistema foi construído pensando na integridade absoluta dos dados financeiros da empresa, implementando os principais padrões de segurança da indústria:

* **Autenticação JWT (JSON Web Tokens):** Geração de tokens com tempo de expiração, garantindo que todas as rotas da API (`/clientes`) estejam blindadas contra acessos anônimos.
* **Criptografia Bcrypt:** Senhas "trituradas" e protegidas no servidor, impedindo vazamentos em caso de invasões.
* **Isolamento de Variáveis (.env):** Chaves secretas e credenciais de administrador mantidas fora do controle de versão e do código-fonte.

---

## 🛠️ Tecnologias Utilizadas

**Motor (Backend):**
* **Python**
* **FastAPI** (Construção da API RESTful de alta performance)
* **SQLite** (Banco de dados embutido nativo)
* **Uvicorn** (Servidor assíncrono)
* **PyJWT & Passlib** (Camada de segurança e autenticação)

**Interface (Frontend):**
* **HTML5 / CSS3 / Vanilla JavaScript**
* **Tailwind CSS** (Estilização fluida e Dark Mode)
* Integrações visuais: *Chart.js*, *FullCalendar*, *SheetJS*.

---

## 🚀 Como rodar o projeto na sua máquina

Siga os passos abaixo no seu terminal para baixar e iniciar o sistema localmente:

```bash
# 1. Clone o repositório para o seu computador
git clone [https://github.com/SEU-USUARIO/CRM-Web-Gerezin-SaaS.git](https://github.com/SEU-USUARIO/CRM-Web-Gerezin-SaaS.git)

# 2. Entre na pasta do projeto
cd CRM-Web-Gerezin-SaaS

# 3. Crie um arquivo chamado .env na raiz do projeto e insira suas credenciais:
# SECRET_KEY=cole_aqui_uma_chave_aleatoria
# ADMIN_USERNAME=admin
# ADMIN_PASSWORD=sua_senha_forte

# 4. Instale todas as dependências necessárias
pip install -r requirements.txt

# 5. Inicie o servidor do backend
uvicorn main:app --reload