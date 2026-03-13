// === VARIÁVEIS GLOBAIS ===
let listaDeClientesAtuais = [], clienteSendoEditadoId = null, idParaConcluir = null, graficoFinancas = null, calendarioApp = null;
const fmt = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

// SVGs reutilizados nos cartões dinâmicos
const IC = {
    edit:    `<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>`,
    trash:   `<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>`,
    receipt: `<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>`,
    check:   `<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
    money:   `<svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
    tool:    `<svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>`,
    cal:     `<svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`,
    phone:   `<svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>`,
};

// === TOAST ===
function mostrarToast(msg, tipo = "info", dur = 3500) {
    const icons = { success:"✅", error:"❌", warning:"⚠️", info:"ℹ️" };
    const t = document.createElement("div");
    t.className = `toast toast-${tipo}`;
    t.innerHTML = `<span>${icons[tipo]}</span><span>${msg}</span>`;
    document.getElementById("toast-container").appendChild(t);
    setTimeout(() => { t.classList.add("hide"); t.addEventListener("animationend", () => t.remove()); }, dur);
}

// === AUTH ===
function checarAcesso() {
    const token = localStorage.getItem("token_gerezin"), perfil = localStorage.getItem("perfil_gerezin");
    if (token) {
        document.getElementById("tela-login").classList.add("hidden");
        document.getElementById("sistema-principal").classList.remove("hidden");
        document.getElementById("sistema-principal").classList.add("flex");
        document.getElementById("btn-aba-financeiro").classList.toggle("hidden", perfil !== "chefe");
        carregarClientes();
    } else {
        document.getElementById("tela-login").classList.remove("hidden");
        document.getElementById("sistema-principal").classList.add("hidden");
        document.getElementById("sistema-principal").classList.remove("flex");
    }
}

function fazerLogin(e) {
    e.preventDefault();
    const p = new URLSearchParams();
    p.append("username", document.getElementById("login-user").value);
    p.append("password", document.getElementById("login-pass").value);
    fetch("/login", { method: "POST", body: p })
        .then(r => { if (!r.ok) throw new Error(); return r.json(); })
        .then(d => {
            localStorage.setItem("token_gerezin", d.access_token);
            localStorage.setItem("perfil_gerezin", d.perfil);
            document.getElementById("msg-erro-login").classList.add("hidden");
            const hoje = new Date();
            document.getElementById("filtro-ano").value = hoje.getFullYear().toString();
            document.getElementById("filtro-mes").value = (hoje.getMonth()+1).toString().padStart(2,'0');
            checarAcesso();
        })
        .catch(() => document.getElementById("msg-erro-login").classList.remove("hidden"));
}

function fazerLogout() { localStorage.removeItem("token_gerezin"); localStorage.removeItem("perfil_gerezin"); checarAcesso(); }
function auth() { return { "Content-Type": "application/json", "Authorization": "Bearer " + localStorage.getItem("token_gerezin") }; }
function alternarTema() { document.documentElement.classList.toggle('dark'); }

function toggleMenuMobile() {
    const menu = document.getElementById('mobile-menu');
    const hamburger = document.getElementById('hamburger-icon');
    const close = document.getElementById('close-icon');
    const aberto = menu.classList.toggle('hidden') === false;
    hamburger.classList.toggle('hidden', aberto);
    close.classList.toggle('hidden', !aberto);
}

function fecharMenuMobile() {
    document.getElementById('mobile-menu').classList.add('hidden');
    document.getElementById('hamburger-icon').classList.remove('hidden');
    document.getElementById('close-icon').classList.add('hidden');
}

// === NAVEGAÇÃO ===
function mudarAba(id, btn) {
    document.querySelectorAll('.aba').forEach(a => { a.classList.remove('block','animar-entrada'); a.classList.add('hidden'); });
    document.querySelectorAll('.menu-btn').forEach(b => {
        b.classList.remove('bg-secundaria','text-white','shadow-lg','shadow-secundaria/30');
        if (!b.classList.contains('menu-btn-mobile')) b.classList.add('text-slate-600','dark:text-slate-300');
    });
    const aba = document.getElementById(id);
    aba.classList.remove('hidden'); aba.classList.add('block');
    aba.style.animation='none'; aba.offsetHeight; aba.style.animation=null; aba.classList.add('animar-entrada');
    if (btn) { btn.classList.remove('text-slate-600','dark:text-slate-300'); btn.classList.add('bg-secundaria','text-white','shadow-lg','shadow-secundaria/30'); }
    if (id==='calendario' && calendarioApp) setTimeout(() => calendarioApp.render(), 100);
}

// === MODAIS ===
// === MODAL ROBÔ ===
let idRoboAtual = null, prazoRoboMeses = 3;

function abrirModalRobo(id) {
    idRoboAtual = id;
    prazoRoboMeses = 3;
    const c = listaDeClientesAtuais.find(c => c.id === id);
    document.getElementById("robo-nome-cliente").innerText = c ? `${c.nome} · ${c.telefone}` : "";
    roboStep1();
    document.getElementById("modal-robo").classList.remove("hidden");
}

function fecharModalRobo() {
    idRoboAtual = null;
    document.getElementById("modal-robo").classList.add("hidden");
}

function roboStep1() {
    document.getElementById("robo-step1").classList.remove("hidden");
    document.getElementById("robo-step2-fez").classList.add("hidden");
    document.getElementById("robo-step2-naofez").classList.add("hidden");
    document.getElementById("robo-step2-inativo").classList.add("hidden");
}

function roboFez() {
    document.getElementById("robo-step1").classList.add("hidden");
    document.getElementById("robo-step2-fez").classList.remove("hidden");
}

function roboNaoFez() {
    document.getElementById("robo-step1").classList.add("hidden");
    document.getElementById("robo-step2-naofez").classList.remove("hidden");
}

function roboInativo() {
    document.getElementById("robo-step1").classList.add("hidden");
    document.getElementById("robo-step2-inativo").classList.remove("hidden");
    document.getElementById("robo-motivo-inativo").value = "";
}

function roboConfirmarInativo() {
    const c = listaDeClientesAtuais.find(c => c.id === idRoboAtual);
    if (!c) return;
    const motivo = document.getElementById("robo-motivo-inativo").value.trim();
    const obs = `__INATIVO__ ${motivo ? "— " + motivo : ""}`.trim();
    fetch(`/clientes/${idRoboAtual}`, {
        method: "PUT", headers: auth(),
        body: JSON.stringify({ ...c, detalhes: obs })
    }).then(r => {
        if (r.status === 401) return fazerLogout();
        fecharModalRobo();
        mostrarToast("Cliente marcado como inativo.", "info", 4000);
        carregarClientes();
    });
}

function selecionarPrazo(btn, meses) {
    prazoRoboMeses = meses;
    document.querySelectorAll(".prazo-btn").forEach(b => {
        b.classList.remove("bg-secundaria", "text-white");
        b.classList.add("bg-slate-100", "dark:bg-slate-700", "text-slate-700", "dark:text-white");
    });
    btn.classList.add("bg-secundaria", "text-white");
    btn.classList.remove("bg-slate-100", "dark:bg-slate-700", "text-slate-700", "dark:text-white");
}

function roboConfirmarFez() {
    const c = listaDeClientesAtuais.find(c => c.id === idRoboAtual);
    if (!c) return;
    const hoje = new Date().toISOString().split("T")[0];
    const pacote = {
        nome: c.nome, telefone: c.telefone, endereco: c.endereco,
        tipo_servico: c.tipo_servico, data_servico: hoje,
        status_servico: "Concluído",
        status_pagamento: document.getElementById("robo-pago").value,
        valor: document.getElementById("robo-valor").value || "0",
        ligar_mais_tarde: false,
        detalhes: "Manutenção registrada via Robô de Retenção."
    };
    fetch("/clientes", { method: "POST", headers: auth(), body: JSON.stringify(pacote) })
        .then(r => { if (r.status === 401) return fazerLogout(); fecharModalRobo(); mostrarToast("Manutenção registrada. Próximo alerta em 1 ano.", "success", 4500); carregarClientes(); });
}

function roboConfirmarNaoFez() {
    const c = listaDeClientesAtuais.find(c => c.id === idRoboAtual);
    if (!c) return;
    const dataFutura = new Date();
    dataFutura.setMonth(dataFutura.getMonth() + prazoRoboMeses);
    const dataStr = dataFutura.toISOString().split("T")[0];
    const pacote = {
        nome: c.nome, telefone: c.telefone, endereco: c.endereco,
        tipo_servico: c.tipo_servico, data_servico: dataStr,
        status_servico: "Concluído",
        status_pagamento: "Pendente",
        valor: "0",
        ligar_mais_tarde: false,
        detalhes: `Contato de retenção em ${new Date().toLocaleDateString("pt-BR")} — cliente não quis manutenção. Reagendado para ${prazoRoboMeses} mês(es).`
    };
    fetch("/clientes", { method: "POST", headers: auth(), body: JSON.stringify(pacote) })
        .then(r => { if (r.status === 401) return fazerLogout(); fecharModalRobo(); mostrarToast(`Cliente reagendado para daqui ${prazoRoboMeses} mês(es).`, "info", 4500); carregarClientes(); });
}

function abrirModalDetalhes(id) {
    const c = listaDeClientesAtuais.find(c => c.id === parseInt(id));
    if (!c) return;
    document.getElementById('detalhe-nome').innerText = c.nome;
    document.getElementById('detalhe-telefone').innerText = c.telefone;
    document.getElementById('detalhe-endereco').innerText = c.endereco;
    document.getElementById('detalhe-servico').innerText = c.tipo_servico;
    document.getElementById('detalhe-data').innerText = c.data_servico.split('-').reverse().join('/');
    document.getElementById('detalhe-situacao').innerText = c.status_servico;
    document.getElementById('detalhe-pagamento').innerText = c.status_pagamento;
    const val = parseFloat(c.valor) > 0;
    document.getElementById('linha-detalhe-valor').classList.toggle('hidden', !val);
    if (val) document.getElementById('detalhe-valor').innerText = fmt.format(parseFloat(c.valor));
    document.getElementById('detalhe-obs').innerText = c.detalhes || "Nenhuma anotação extra.";
    document.getElementById('btn-modal-recibo').onclick = () => baixarRecibo(c.id, document.getElementById('btn-modal-recibo'));
    document.getElementById('btn-modal-editar').onclick = () => { fecharModalDetalhes(); prepararEdicao(c.id); };
    document.getElementById('btn-modal-excluir').onclick = () => { fecharModalDetalhes(); apagarCliente(c.id); };
    document.getElementById('modal-detalhes').classList.remove('hidden');
}
function fecharModalDetalhes() { document.getElementById('modal-detalhes').classList.add('hidden'); }
function abrirModalConcluir(id) { idParaConcluir = id; document.getElementById("modal-concluir").classList.remove("hidden"); }
function fecharModalConcluir() { idParaConcluir = null; document.getElementById("modal-concluir").classList.add("hidden"); document.getElementById("input-modal-valor").value = ""; document.getElementById("input-modal-pago").value = "Pago"; }

// === CALENDÁRIO ===
function iniciarCalendario() {
    calendarioApp = new FullCalendar.Calendar(document.getElementById('div-calendario-visual'), {
        initialView: 'dayGridMonth', locale: 'pt-br',
        headerToolbar: { left: 'prev,next today', center: 'title', right: 'dayGridMonth,timeGridWeek' },
        buttonText: { today: 'Hoje', month: 'Mês', week: 'Semana' },
        events: [], eventClick: info => abrirModalDetalhes(info.event.id)
    });
    calendarioApp.render();
}
document.addEventListener('DOMContentLoaded', () => { iniciarCalendario(); checarAcesso(); });

// === FORM ===
function verificarStatus() {
    const concluido = document.getElementById("input-status-servico").value === "Concluído";
    document.getElementById("div-valor").classList.toggle("hidden", !concluido);
    document.getElementById("div-pagamento").classList.toggle("hidden", !concluido);
    if (!concluido && !clienteSendoEditadoId) {
        document.getElementById("input-valor").value = "";
        document.getElementById("input-status-pagamento").value = "Pendente";
    }
}

function prepararNovo() {
    clienteSendoEditadoId = null;
    document.querySelectorAll('input[type="text"], input[type="date"], input[type="number"], textarea').forEach(i => i.value='');
    document.getElementById("input-ligar").checked = false;
    document.getElementById("input-status-servico").value = "Agendado";
    document.getElementById("input-status-pagamento").value = "Pendente";
    verificarStatus();
    document.getElementById("alerta-duplicado").classList.add("hidden");
    document.getElementById("titulo-aba-form").innerText = "Novo Registro";
    document.getElementById("btn-salvar-form").innerHTML = `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/></svg> Lançar no Sistema`;
}

function prepararEdicao(id) {
    const c = listaDeClientesAtuais.find(c => c.id === id);
    if (!c) return;
    clienteSendoEditadoId = id;
    document.getElementById("input-telefone").value = c.telefone;
    document.getElementById("input-nome").value = c.nome;
    document.getElementById("input-endereco").value = c.endereco;
    document.getElementById("input-servico").value = c.tipo_servico;
    document.getElementById("input-data").value = c.data_servico;
    document.getElementById("input-status-servico").value = c.status_servico;
    document.getElementById("input-status-pagamento").value = c.status_pagamento;
    document.getElementById("input-ligar").checked = c.ligar_mais_tarde === 1 || c.ligar_mais_tarde === true;
    document.getElementById("input-valor").value = c.valor || "";
    document.getElementById("input-detalhes").value = c.detalhes || "";
    verificarStatus();
    document.getElementById("alerta-duplicado").classList.add("hidden");
    document.getElementById("titulo-aba-form").innerText = "Editar Registro";
    document.getElementById("btn-salvar-form").innerHTML = `${IC.edit} Salvar Alterações`;
    mudarAba('novo', document.getElementById('btn-menu-novo'));
}

document.getElementById("input-telefone").addEventListener("input", function(e) {
    if (clienteSendoEditadoId) return;
    const existe = listaDeClientesAtuais.some(c => c.telefone === e.target.value.trim());
    document.getElementById("alerta-duplicado").classList.toggle("hidden", !existe || !e.target.value.trim());
});

function renderFila() {
    const termo = (document.getElementById("input-pesquisa-fila")?.value || "").toLowerCase();
    const tipo  = document.getElementById("filtro-tipo-fila")?.value || "";
    const ordem = document.getElementById("filtro-ordem-fila")?.value || "asc";
    let lista = listaDeClientesAtuais.filter(c => c.status_servico === "Agendado");
    if (tipo) lista = lista.filter(c => c.tipo_servico.toLowerCase().includes(tipo.toLowerCase()));
    if (termo) lista = lista.filter(c => (c.nome+c.telefone+c.tipo_servico+c.endereco).toLowerCase().includes(termo));
    lista.sort((a,b) => ordem === "asc"
        ? new Date(a.data_servico)-new Date(b.data_servico)
        : new Date(b.data_servico)-new Date(a.data_servico));
    const div = document.getElementById("lista-pendentes");
    div.innerHTML = "";
    lista.forEach(c => div.appendChild(criarCartao(c,"Fila")));
}

function renderHistorico() {
    const termo    = (document.getElementById("input-pesquisa")?.value || "").toLowerCase();
    const tipo     = document.getElementById("filtro-tipo-hist")?.value || "";
    const pgto     = document.getElementById("filtro-pagamento-hist")?.value || "";
    const ordem    = document.getElementById("filtro-ordem-hist")?.value || "desc";
    let lista = [...listaDeClientesAtuais];
    if (tipo)  lista = lista.filter(c => c.tipo_servico.toLowerCase().includes(tipo.toLowerCase()));
    if (pgto)  lista = lista.filter(c => c.status_pagamento === pgto && c.status_servico === "Concluído");
    if (termo) lista = lista.filter(c => (c.nome+c.telefone+c.tipo_servico+c.endereco).toLowerCase().includes(termo));
    lista.sort((a,b) => ordem === "asc"
        ? new Date(a.data_servico)-new Date(b.data_servico)
        : new Date(b.data_servico)-new Date(a.data_servico));
    const div = document.getElementById("lista-concluidos");
    div.innerHTML = "";
    lista.forEach(c => div.appendChild(criarCartao(c,"Histórico")));
}

// === AÇÕES ===
function confirmarConclusao() {
    const valor = document.getElementById("input-modal-valor").value;
    if (!valor) { mostrarToast("Informe o valor cobrado.", "error"); return; }
    fetch("/clientes/"+idParaConcluir+"/concluir", { method:"PUT", headers:auth(), body:JSON.stringify({ valor, status_pagamento: document.getElementById("input-modal-pago").value }) })
        .then(r => { if (r.status===401) return fazerLogout(); fecharModalConcluir(); mostrarToast("Serviço finalizado.", "success"); carregarClientes(); });
}

function exportarExcel() {
    const ano = document.getElementById("filtro-ano").value, mes = document.getElementById("filtro-mes").value;
    const filtrados = listaDeClientesAtuais.filter(c => (ano==="todos"||c.data_servico.substring(0,4)===ano) && (mes==="todos"||c.data_servico.substring(5,7)===mes));
    if (!filtrados.length) { mostrarToast("Nenhum dado no período selecionado.", "warning"); return; }
    const dados = filtrados.map(c => ({"ID":c.id,"Cliente / Loja":c.nome,"Telefone":c.telefone,"Endereço":c.endereco,"Tipo de Serviço":c.tipo_servico,"Data":c.data_servico.split('-').reverse().join('/'),"Situação":c.status_servico,"Pagamento":c.status_pagamento,"Valor (R$)":parseFloat(c.valor)||0,"Ligar Depois?":c.ligar_mais_tarde?"Sim":"Não","Obs":c.detalhes||""}));
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(dados), "Relatório");
    XLSX.writeFile(wb, `Relatorio_Gerezin_${ano}_${mes}.xlsx`);
    mostrarToast("Relatório exportado.", "success");
}

// === CARTÃO ===
function criarCartao(cliente, contexto) {
    const perfil = localStorage.getItem("perfil_gerezin");
    const el = document.createElement("div");
    const dataFmt = cliente.data_servico.split('-').reverse().join('/');
    const valorFmt = fmt.format(parseFloat(cliente.valor) || 0);

    const badgePgto = cliente.status_pagamento === "Pago"
        ? `<span class="px-3 py-1 bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 rounded-full text-xs font-bold">💰 PAGO</span>`
        : `<span class="px-3 py-1 bg-amber-500/10 text-amber-600 border border-amber-500/20 rounded-full text-xs font-bold">⏳ PENDENTE</span>`;
    const badgeLigar = cliente.ligar_mais_tarde && contexto!=="Financeiro" ? `<span class="px-3 py-1 bg-orange-500/10 text-orange-600 border border-orange-500/20 rounded-full text-xs font-bold ml-2">📞 LIGAR DEPOIS</span>` : '';
    const ehInativo = (cliente.detalhes || "").startsWith("__INATIVO__");
    const badgeStatus = contexto==="Histórico"
        ? (ehInativo
            ? `<span class="px-3 py-1 bg-slate-400/10 text-slate-500 border border-slate-400/20 rounded-full text-xs font-bold ml-2">🚫 INATIVO</span>`
            : cliente.status_servico==="Concluído"
                ? `<span class="px-3 py-1 bg-sky-500/10 text-sky-600 border border-sky-500/20 rounded-full text-xs font-bold ml-2">✅ CONCLUÍDO</span>`
                : `<span class="px-3 py-1 bg-slate-500/10 text-slate-600 border border-slate-500/20 rounded-full text-xs font-bold ml-2">📝 FILA</span>`)
        : '';

    const base = "bg-white/70 dark:bg-slate-800/70 backdrop-blur-xl p-6 rounded-3xl shadow-xl border border-white/40 dark:border-slate-700 flex flex-col xl:flex-row justify-between items-center text-center xl:text-left gap-6 hover:-translate-y-1 hover:shadow-2xl transition-all duration-300 ";
    if (contexto==="Fila"||(contexto==="Histórico"&&cliente.status_servico==="Agendado")) el.className = base+"border-l-4 border-secundaria";
    else if (contexto==="Alerta") el.className = base+"border-l-4 border-orange-500 bg-orange-50/50";
    else if (contexto==="Financeiro") el.className = base+(cliente.status_pagamento==="Pago"?"border-l-4 border-emerald-500":"border-l-4 border-amber-500");
    else el.className = base;

    let acoes = `<div class="flex flex-wrap gap-3 w-full xl:w-auto mt-4 xl:mt-0 justify-center xl:justify-end">`;
    if (cliente.status_servico==="Concluído"&&(contexto==="Histórico"||contexto==="Financeiro"))
        acoes += `<button onclick="baixarRecibo(${cliente.id},this)" class="px-5 py-2.5 bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 border border-emerald-200 dark:border-emerald-900 rounded-xl font-bold text-sm transition-all hover:bg-emerald-500 hover:text-white flex items-center gap-2">${IC.receipt} Recibo</button>`;
    if (contexto==="Fila"||contexto==="Histórico")
        acoes += `<button onclick="prepararEdicao(${cliente.id})" class="px-5 py-2.5 bg-white dark:bg-slate-900 border border-blue-200 text-blue-500 rounded-xl font-bold text-sm flex items-center gap-2">${IC.edit} Editar</button>`;
    if (cliente.status_pagamento==="Pendente"&&cliente.status_servico==="Concluído"&&contexto!=="Alerta"&&perfil==="chefe")
        acoes += `<button onclick="pagarServico(${cliente.id})" class="px-5 py-2.5 bg-white border-2 border-emerald-500 text-emerald-600 rounded-xl font-bold text-sm flex items-center gap-2">${IC.money} Receber ${valorFmt}</button>`;
    if (contexto==="Fila") {
        acoes += `<button onclick="abrirModalConcluir(${cliente.id})" class="px-5 py-2.5 bg-secundaria text-white rounded-xl font-bold text-sm flex items-center gap-2">${IC.check} Concluir</button>`;
        acoes += `<button onclick="apagarCliente(${cliente.id})" class="px-4 py-2.5 bg-red-50 text-red-500 rounded-xl font-bold flex items-center">${IC.trash}</button>`;
    } else if (contexto==="Histórico"||contexto==="Financeiro")
        acoes += `<button onclick="apagarCliente(${cliente.id})" class="px-5 py-2.5 bg-white border border-red-200 text-red-500 rounded-xl font-bold text-sm flex items-center gap-2">${IC.trash} Excluir</button>`;
    else if (contexto==="Alerta") {
        acoes += `<a href="https://wa.me/55${cliente.telefone.replace(/\D/g,'')}?text=Olá" target="_blank" class="px-5 py-2.5 bg-[#25D366] text-white rounded-xl font-bold text-sm flex items-center gap-2">💬 Conversar</a>`;
        acoes += `<button onclick="abrirModalRobo(${cliente.id})" class="px-5 py-2.5 bg-orange-500 hover:bg-orange-600 text-white rounded-xl font-bold text-sm flex items-center gap-2">${IC.check} Registrar contato</button>`;
    }
    acoes += `</div>`;

    let info = "";
    if (contexto!=="Financeiro"&&(cliente.valor||cliente.detalhes)) {
        info = `<div class="mt-3 text-sm text-slate-500 bg-slate-100/50 dark:bg-slate-900/50 p-3 rounded-lg text-left">`;
        if (cliente.valor&&cliente.status_servico==="Concluído"&&perfil==="chefe") info += `<b>Faturamento:</b> ${valorFmt}<br>`;
        if (cliente.detalhes) info += `<b>Detalhes:</b> ${cliente.detalhes}`;
        info += `</div>`;
    } else if (contexto==="Financeiro") {
        info = `<div class="mt-3 bg-slate-100/50 dark:bg-slate-900/50 p-3 rounded-lg flex justify-between items-center w-full max-w-sm"><span class="text-sm font-bold text-slate-500 uppercase tracking-widest">Valor do Serviço:</span><span class="text-xl font-black ${cliente.status_pagamento==="Pago"?"text-emerald-500":"text-amber-500"}">${valorFmt}</span></div>`;
    }

    el.innerHTML = `
        <div class="flex-1 w-full">
            <div class="flex flex-col xl:flex-row items-center gap-4 mb-4">
                <h4 class="text-2xl font-black text-primaria dark:text-white">${cliente.nome}</h4>
                <div>${cliente.status_servico==="Concluído"?badgePgto:""}${badgeLigar}${badgeStatus}</div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm font-medium">
                <div class="bg-slate-100/50 dark:bg-slate-900/50 py-2 px-4 rounded-lg flex items-center gap-2 text-secundaria">
                    ${IC.tool}<span class="dark:text-slate-300 text-slate-700">${cliente.tipo_servico}</span>
                </div>
                <div class="bg-slate-100/50 dark:bg-slate-900/50 py-2 px-4 rounded-lg flex items-center gap-2 text-secundaria">
                    ${IC.cal}<span class="dark:text-slate-300 text-slate-700">${dataFmt}</span>
                </div>
                <div class="bg-slate-100/50 dark:bg-slate-900/50 py-2 px-4 rounded-lg flex items-center gap-2 col-span-1 md:col-span-2 text-secundaria">
                    ${IC.phone}<span class="dark:text-slate-300 text-slate-700">${cliente.telefone} &nbsp;|&nbsp; 📍 ${cliente.endereco}</span>
                </div>
            </div>
            ${info}
        </div>
        ${acoes}`;
    return el;
}

// === FINANCEIRO ===
function aplicarFiltroFinanceiro() {
    if (localStorage.getItem("perfil_gerezin") !== "chefe") return;
    const ano = document.getElementById("filtro-ano").value, mes = document.getElementById("filtro-mes").value;
    const div = document.getElementById("lista-financeiro");
    div.innerHTML = "";
    let rec = 0, pend = 0;
    listaDeClientesAtuais.forEach(c => {
        const val = parseFloat((c.valor||"").replace("R$","").replace(/\./g,"").replace(",","."));
        if (val > 0) {
            const ok = (ano==="todos"||c.data_servico.substring(0,4)===ano) && (mes==="todos"||c.data_servico.substring(5,7)===mes);
            if (ok) { c.status_pagamento==="Pago" ? rec+=val : pend+=val; div.appendChild(criarCartao(c,"Financeiro")); }
        }
    });
    document.getElementById("metrica-recebido").innerText = fmt.format(rec);
    document.getElementById("metrica-pendente").innerText = fmt.format(pend);
    if (graficoFinancas) graficoFinancas.destroy();
    graficoFinancas = new Chart(document.getElementById('grafico-financas').getContext('2d'), {
        type:'doughnut', data:{ labels:['Recebido','Pendente'], datasets:[{ data:[rec,pend], backgroundColor:['#10b981','#f59e0b'], borderWidth:0 }] },
        options:{ responsive:true, maintainAspectRatio:false, plugins:{ legend:{ position:'bottom', labels:{ color:'#64748b', font:{ weight:'bold' } } } } }
    });
}

// === CARREGAMENTO ===
function carregarClientes() {
    fetch("/clientes", { headers: auth() })
        .then(r => { if (r.status===401) { fazerLogout(); throw new Error(); } return r.json(); })
        .then(dados => {
            listaDeClientesAtuais = dados;
            const divP = document.getElementById("lista-pendentes"), divC = document.getElementById("lista-concluidos"), divA = document.getElementById("lista-alertas");
            divP.innerHTML = ""; divC.innerHTML = ""; divA.innerHTML = "";
            const pendentes = dados.filter(c => c.status_servico==="Agendado");
            const umAno = 1000*60*60*24*365;
            const alertas = dados.filter(c => c.status_servico==="Concluído").filter(c => {
                if ((c.detalhes || "").startsWith("__INATIVO__")) return false;
                const ehAr = ["limpeza","instala","ar"].some(k => c.tipo_servico.toLowerCase().includes(k));
                return ehAr && (new Date()-new Date(c.data_servico)) > umAno;
            });
            if (calendarioApp) {
                calendarioApp.removeAllEvents();
                dados.forEach(c => calendarioApp.addEvent({ id:c.id, title:`${c.nome} - ${c.tipo_servico}`, start:c.data_servico, allDay:true, backgroundColor:c.status_servico==='Concluído'?'#10b981':'#0ea5e9', borderColor:'transparent' }));
            }
            document.getElementById("metrica-fila").innerText = pendentes.length;
            document.getElementById("metrica-concluidos").innerText = dados.filter(c => c.status_servico==="Concluído").length;
            document.getElementById("metrica-alertas").innerText = alertas.length;
            // Robô: oldest first (fixed)
            alertas.sort((a,b) => new Date(a.data_servico)-new Date(b.data_servico));
            alertas.forEach(c => divA.appendChild(criarCartao(c,"Alerta")));
            renderFila();
            renderHistorico();
            aplicarFiltroFinanceiro();
        }).catch(()=>{});
}

function salvarCliente() {
    const p = { nome:document.getElementById("input-nome").value, telefone:document.getElementById("input-telefone").value, tipo_servico:document.getElementById("input-servico").value, endereco:document.getElementById("input-endereco").value, data_servico:document.getElementById("input-data").value, status_servico:document.getElementById("input-status-servico").value, status_pagamento:document.getElementById("input-status-pagamento").value, ligar_mais_tarde:document.getElementById("input-ligar").checked, detalhes:document.getElementById("input-detalhes").value, valor:document.getElementById("input-valor").value };
    fetch(clienteSendoEditadoId?`/clientes/${clienteSendoEditadoId}`:"/clientes", { method:clienteSendoEditadoId?"PUT":"POST", headers:auth(), body:JSON.stringify(p) })
        .then(r => { if(r.status===401) return fazerLogout(); mostrarToast(clienteSendoEditadoId?"Registro atualizado.":"Registro salvo.", "success"); prepararNovo(); carregarClientes(); });
}

function pagarServico(id) {
    fetch("/clientes/"+id+"/pagar", { method:"PUT", headers:auth() })
        .then(r => { if(r.status===401) return fazerLogout(); mostrarToast("Pagamento confirmado.", "success"); carregarClientes(); });
}

function apagarCliente(id) {
    if (!confirm("Excluir permanentemente?")) return;
    fetch("/clientes/"+id, { method:"DELETE", headers:auth() })
        .then(r => { if(r.status===401) return fazerLogout(); mostrarToast("Registro excluído.", "info"); carregarClientes(); });
}

function baixarRecibo(id, btn) {
    const orig = btn.innerHTML;
    btn.innerHTML = "Gerando...";
    fetch("/clientes/"+id+"/recibo", { headers:auth() })
        .then(r => { if(r.status===401) return fazerLogout(); if(!r.ok) throw new Error(); return r.blob(); })
        .then(blob => {
            const url = window.URL.createObjectURL(blob), a = document.createElement('a');
            a.href=url; a.download="Recibo_Servico.pdf";
            document.body.appendChild(a); a.click(); window.URL.revokeObjectURL(url);
            btn.innerHTML = orig; mostrarToast("Recibo gerado.", "success");
        })
        .catch(() => { btn.innerHTML=orig; mostrarToast("Erro ao gerar o recibo.", "error"); });
}