# ❄️ Gerezin CRM & Gestão Financeira

CRM desenvolvido para a **T.J.L Refrigeração LTDA (Gerezin)**, cobrindo gestão de ordens de serviço, controle financeiro e automação de retenção de clientes. Backend em FastAPI, banco de dados PostgreSQL via Supabase, deploy em produção via Render + Docker.

O projeto nasceu da necessidade de substituir o controle manual em papel por um sistema centralizado, com geração automática de recibos e controle de acesso por perfis de usuário.

---

## Funcionalidades

- **Gestão Operacional:** Cadastro, edição, busca com filtros e exclusão de clientes e Ordens de Serviço.
- **Segurança e Controle de Acesso:** Autenticação JWT e senhas protegidas com hash (Bcrypt).
  - **Gerência:** Acesso completo, incluindo painel financeiro e faturamento.
  - **Operador:** Acesso restrito à fila de trabalho e histórico de clientes.
- **Gerador de Recibos (PDF):** Recibos profissionais com identidade visual da empresa, prontos para impressão ou envio via WhatsApp.
- **Dashboard Financeiro:** Visualização de fluxo de caixa com exportação de relatórios para Excel (`.xlsx`).
- **Agenda Interativa:** Calendário com todos os serviços agendados do mês.
- **Robô de Retenção:** Alertas automáticos para clientes que realizaram serviço de ar-condicionado há exatamente 1 ano. Inclui fluxo de CRM completo para registrar novas manutenções, reagendar contatos futuros ou inativar clientes.
- **UI/UX Responsiva:** Interface adaptável para dispositivos móveis com menu hambúrguer, suporte a *Dark Mode* e notificações não-bloqueantes (Toasts).

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.11, FastAPI, Passlib (Bcrypt), JWT |
| Banco de dados | PostgreSQL (Supabase) |
| Frontend | HTML, JavaScript, Tailwind CSS |
| Deploy | Render, Docker |

---

## Estrutura do Projeto

A arquitetura do projeto segue o padrão modular (Separation of Concerns) para facilitar a manutenção e escalabilidade:

```text
Gerezin_CRM/
├── database.py         # Conexão e inicialização do banco de dados
├── models.py           # Modelos de validação de dados (Pydantic)
├── security.py         # Lógica de autenticação JWT e hashing
├── pdf_service.py      # Lógica isolada de geração de relatórios PDF
├── routes.py           # Endpoints da API (CRUD e Financeiro)
├── main.py             # Arquivo principal que orquestra a aplicação
├── migrar_dados.py     # Script ETL para importação de clientes legados
├── frontend/
│   ├── index.html      # Estrutura visual principal
│   ├── logo_gerezin.png
│   ├── favicon.png
│   └── assets/
│       ├── style.css   # Estilos e animações personalizadas
│       └── app.js      # Lógica de interface e consumo da API
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Rodando localmente

**1. Clone o repositório:**
```bash
git clone [https://github.com/JoaoPrissao/CRM-Web-Gerezin.git](https://github.com/JoaoPrissao/CRM-Web-Gerezin.git)
cd CRM-Web-Gerezin
```

**2. Crie e ative o ambiente virtual:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**3. Configure as variáveis de ambiente:**

Crie um arquivo `.env` na raiz do projeto contendo as credenciais do banco e os usuários de acesso:

```env
DATABASE_URL=sua_url_do_supabase
SECRET_KEY=sua_chave_secreta_jwt
USUARIO_JOAO=joao_vitor
SENHA_JOAO=senha_aqui
USUARIO_TECO=teco_gerezin
SENHA_TECO=senha_aqui
USUARIO_LOJA=loja
SENHA_LOJA=senha_aqui
```

**4. Inicie o servidor:**
```bash
uvicorn main:app --reload
```

Acesse em: `http://localhost:8000`

---

## Limitações Conhecidas

O token JWT de autenticação é armazenado no `localStorage` do navegador. Esta abordagem é funcional para o escopo atual, mas expõe o token a possíveis ataques XSS em ambientes de produção mais críticos. A solução mais robusta seria migrar para cookies `httpOnly`, que são inacessíveis via JavaScript. Esta melhoria está planejada para uma versão futura.

---

## Próximos Passos

Após a conclusão da refatoração e modularização completa do código, as próximas etapas focam em aprimorar a segurança e escalabilidade:

- **Segurança:** Migrar o armazenamento do token JWT para cookies `httpOnly`.
- **Testes:** Implementar testes automatizados para as rotas da API utilizando `pytest`.