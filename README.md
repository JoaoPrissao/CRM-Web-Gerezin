# ❄️ Gerezin CRM & Gestão Financeira

Um sistema completo de Gestão de Relacionamento com o Cliente (CRM) e Controle Financeiro, desenvolvido sob medida para a empresa **T.J.L Refrigeração LTDA (Gerezin)**. 

Este projeto foi construído para modernizar o controle de agendamentos, automatizar a geração de recibos e proteger os dados sensíveis da empresa através de um sistema robusto de controle de acesso.

## 🚀 Principais Funcionalidades

* **Gestão Operacional:** Cadastro, edição e exclusão rápida de clientes e Ordens de Serviço.
* **Controle de Acesso por Perfis:** * **Perfil Chefe/Gerência:** Acesso total, incluindo o financeiro, faturamento e recebimentos diretos.
  * **Perfil Operador/Loja:** Acesso focado na fila de trabalho e histórico, com bloqueio automático à visão do dinheiro e faturamento.
* **Gerador de Recibos (PDF):** Criação automática de recibos profissionais personalizados, prontos para impressão ou envio no WhatsApp.
* **Dashboard Financeiro:** Gráficos visuais de fluxo de caixa e exportação de relatórios completos para o Excel (`.xlsx`).
* **Agenda Interativa:** Calendário para visualização clara de todos os serviços programados do mês.
* **Robô de Retenção:** Avisos automáticos mostrando quais clientes precisam de manutenção preventiva (1 ano após o último serviço de Ar Condicionado).

## 🛠️ Ferramentas Utilizadas

* **Python & FastAPI:** O "motor" principal do sistema, rápido e moderno.
* **PostgreSQL (Supabase):** Banco de dados seguro e hospedado na nuvem.
* **HTML, Javascript & Tailwind CSS:** A "lataria e pintura" do sistema, com visual moderno e Modo Escuro (Dark Mode).
* **Render & Docker:** Onde o sistema fica hospedado funcionando 24 horas por dia na internet.

## 📂 Organização das Pastas

```text
Gerezin_CRM/
├── frontend/             # A tela que o usuário vê (HTML e imagens)
│   ├── index.html
│   ├── logo_gerezin.png
│   └── favicon.png
├── main.py               # O motor principal em Python
├── requirements.txt      # A lista de ferramentas instaladas
├── Dockerfile            # A receita para ligar o servidor na nuvem
└── README.md             # Este manual que você está lendo
```

## 💻 Como rodar no seu próprio computador

Para rodar este projeto no seu PC para fazer testes, siga os passos abaixo:

1. **Baixe o código para o seu computador:**
   ```bash
   git clone https://github.com/JoaoPrissao/CRM-Web-Gerezin-SaaS-.git(https://github.com/SEU_NOME_DE_USUARIO_AQUI/NOME_DO_REPOSITORIO.git)
   cd NOME_DO_REPOSITORIO
   ```

2. **Ligue a sua caixa de ferramentas virtual e instale as dependências:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure as suas senhas secretas:**
   Crie um arquivo chamado `.env` na pasta principal do projeto e coloque as suas senhas de login e o link do seu banco de dados lá dentro.

4. **Ligue o motor do sistema:**
   ```bash
   uvicorn main:app --reload
   ```
   Agora é só abrir o seu navegador de internet e acessar: `http://localhost:8000`

---
*Projeto desenvolvido por João Vitor Prissão Oliveira, buscando aplicar os conceitos práticos da Engenharia de Computação para modernizar a prestação de serviços reais.*