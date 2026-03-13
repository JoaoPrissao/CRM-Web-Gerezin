from fpdf import FPDF

def gerar_pdf_recibo(cliente: dict) -> bytes:
    azul_escuro = (15, 23, 42)
    azul_claro = (14, 165, 233)
    cinza_texto = (100, 116, 139)

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("helvetica", "B", 22)
    pdf.set_text_color(*azul_escuro)
    pdf.cell(0, 10, "GEREZIN REFRIGERAÇÃO", new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(*cinza_texto)
    pdf.cell(0, 6, "T.J.L Refrigeração LTDA | CNPJ: 11.074.782/0001-20", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 6, "Apucarana - PR | Cel: (43) 99973-9397 | Fixo: (43) 3422-7598", new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.ln(5)
    pdf.set_draw_color(*azul_claro)
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    pdf.set_font("helvetica", "B", 14)
    pdf.set_fill_color(*azul_claro)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "  RECIBO DE PRESTAÇÃO DE SERVIÇO", new_x="LMARGIN", new_y="NEXT", fill=True)
    pdf.ln(8)

    pdf.set_text_color(*azul_escuro)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 6, "INFORMAÇÕES DO CLIENTE:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Nome/Loja: {cliente['nome']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Telefone: {cliente['telefone']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Endereço: {cliente['endereco']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    pdf.set_text_color(*azul_escuro)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 6, "DETALHES DO SERVIÇO:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, f"Serviço Realizado: {cliente['tipo_servico']}", new_x="LMARGIN", new_y="NEXT")

    data_formatada = "/".join(reversed(cliente['data_servico'].split('-')))
    pdf.cell(0, 6, f"Data da Conclusão: {data_formatada}", new_x="LMARGIN", new_y="NEXT")
    if cliente['detalhes']:
        pdf.cell(0, 6, f"Observações: {cliente['detalhes']}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.2)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(16, 185, 129)
    pdf.cell(0, 10, f"VALOR TOTAL COBRADO: R$ {cliente['valor']}", new_x="LMARGIN", new_y="NEXT", align="R")

    pdf.set_font("helvetica", "I", 10)
    pdf.set_text_color(*cinza_texto)
    situacao = "Recebimento confirmado." if cliente['status_pagamento'] == "Pago" else "Pagamento pendente."
    pdf.cell(0, 6, situacao, new_x="LMARGIN", new_y="NEXT", align="R")

    pdf.ln(40)
    pdf.set_draw_color(*azul_escuro)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(*azul_escuro)
    pdf.cell(0, 6, "T.J.L Refrigeração LTDA", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("helvetica", "", 9)
    pdf.cell(0, 5, "Assinatura do Responsável Técnico", new_x="LMARGIN", new_y="NEXT", align="C")

    return pdf.output()