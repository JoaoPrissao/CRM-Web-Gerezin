# ❄️ Gerezin CRM - Sistema de Gestão Operacional e Financeira

Um sistema web completo (SaaS) desenvolvido sob medida para centralizar a operação de uma empresa de manutenção e climatização de ar condicionado. O software resolve problemas reais do dia a dia, como controle de agenda, inadimplência de clientes e fidelização, tudo em uma interface moderna, rápida e responsiva.

## 🚀 Funcionalidades Principais

* **📊 Dashboard Interativo:** Painel com métricas em tempo real mostrando o volume de trabalho do dia, serviços concluídos e gráficos de faturamento (usando *Chart.js*).
* **🗓️ Agenda Inteligente:** Visão de calendário (*FullCalendar*) separando clientes agendados e concluídos por cores, prevenindo conflitos de horários.
* **💰 Módulo Financeiro:** Controle exato de faturamento bruto, dinheiro já recebido e valores pendentes na praça.
* **📋 Histórico e Busca:** Banco de dados de clientes com barra de pesquisa rápida em tempo real.
* **🤖 Robô de Retenção:** Uma aba inteligente que varre o sistema e encontra clientes que fizeram serviços há mais de 1 ano, gerando um botão de WhatsApp para o dono oferecer uma manutenção preventiva.
* **📈 Relatórios Gerenciais:** Exportação do banco de dados completo para planilhas do Excel em um clique (usando *SheetJS*).

## 🛡️ Segurança de Nível Comercial

O sistema foi construído pensando na privacidade dos dados financeiros do negócio:
* **Cofre Invisível (.env):** Senhas e chaves secretas isoladas do código fonte.
* **Criptografia Bcrypt:** Senha do administrador triturada no banco de dados.
* **Autenticação JWT (JSON Web Tokens):** Geração de "crachá digital" com tempo de expiração, blindando todas as rotas da API contra acessos de terceiros.

## 🛠️ Tecnologias Utilizadas

**Backend:**
* Python 3
* FastAPI (Framework super rápido para criar o motor do sistema)
* SQLite (Banco de dados embutido e leve)

**Frontend:**
* HTML5 / CSS3
* Tailwind CSS (Design moderno e responsivo)
* JavaScript Puro (Vanilla JS)

## 💻 Como rodar este projeto localmente

1. Faça o clone (cópia) deste repositório:
```bash
git clone [https://github.com/SEU-USUARIO/Gerezin-CRM.git](https://github.com/SEU-USUARIO/Gerezin-CRM.git)
Entre na pasta do projeto e crie o arquivo de segurança .env com as suas credenciais:

Snippet de código
SECRET_KEY=sua_chave_aleatoria_aqui
ADMIN_USERNAME=seu_usuario
ADMIN_PASSWORD=sua_senha_forte
Instale as ferramentas necessárias:

Bash
pip install -r requirements.txt
Ligue o servidor:

Bash
uvicorn main:app --reload
Abra o navegador no endereço http://127.0.0.1:8000/index.html.

Desenvolvido por João Vitor Prissão Oliveira - Estudante de Engenharia da Computação na UTFPR.