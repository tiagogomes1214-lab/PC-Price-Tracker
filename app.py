import pandas as pd
import streamlit as st

from banco import (
    adicionar_peca,
    adicionar_peca_montagem,
    aplicar_melhor_oferta,
    criar_alerta,
    criar_montagem,
    editar_peca,
    excluir_alerta,
    excluir_montagem,
    excluir_oferta,
    excluir_peca,
    listar_alertas,
    listar_montagens,
    listar_ofertas,
    listar_pecas,
    listar_pecas_montagem,
    pegar_historico,
    remover_peca_montagem,
    salvar_oferta,
)
from buscador import PROVEDORES, buscar_ofertas
from compatibilidade import verificar_compatibilidade
from precos import buscar_preco
from ui import aplicar_estilo, barra_orcamento, hero, kpi, titulo_secao


TIPOS = [
    "Processador",
    "Placa de vídeo",
    "Placa-mãe",
    "Memória RAM",
    "SSD",
    "HD",
    "Fonte",
    "Gabinete",
    "Cooler",
    "Water cooler",
    "Ventoinha",
    "Outro",
]

FAIXAS = [
    "Entrada",
    "Intermediário",
    "Alto desempenho",
    "Entusiasta",
    "Personalizado",
]


def formatar_real(valor):
    numero = float(valor or 0)
    texto = f"{numero:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def numero_opcional(valor):
    return float(valor) if valor and float(valor) > 0 else None


st.set_page_config(
    page_title="PC Price Tracker",
    page_icon="🖥️",
    layout="wide",
)

aplicar_estilo()
hero()

(
    aba_dashboard,
    aba_pecas,
    aba_busca,
    aba_montagens,
    aba_compatibilidade,
    aba_historico,
    aba_alertas,
) = st.tabs(
    [
        "🏠 Dashboard",
        "🧩 Peças",
        "🔎 Buscar preços",
        "🖥️ Montagens",
        "✅ Compatibilidade",
        "📈 Histórico",
        "🔔 Alertas",
    ]
)

pecas = listar_pecas()


with aba_dashboard:
    montagens_dashboard = listar_montagens()
    alertas_dashboard = listar_alertas()

    ofertas_dashboard = []
    for peca_dashboard in pecas:
        try:
            for oferta_dashboard in listar_ofertas(peca_dashboard["id"]):
                ofertas_dashboard.append((peca_dashboard, oferta_dashboard))
        except Exception:
            pass

    ofertas_dashboard.sort(
        key=lambda item: float(item[1].get("preco_final") or 999999999)
    )

    melhor_global = ofertas_dashboard[0] if ofertas_dashboard else None

    titulo_secao(
        "Visão geral",
        "Um resumo rápido do seu catálogo, montagens e oportunidades de preço.",
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi(
            "🧩",
            "Peças monitoradas",
            len(pecas),
            "Componentes cadastrados",
        )

    with c2:
        kpi(
            "🖥️",
            "Montagens",
            len(montagens_dashboard),
            "PCs salvos no projeto",
        )

    with c3:
        kpi(
            "🔔",
            "Alertas ativos",
            len(alertas_dashboard),
            "Metas de preço acompanhadas",
        )

    with c4:
        if melhor_global:
            _, oferta_melhor = melhor_global
            kpi(
                "🏆",
                "Menor oferta",
                formatar_real(oferta_melhor["preco_final"]),
                oferta_melhor["loja"],
            )
        else:
            kpi(
                "🏆",
                "Menor oferta",
                "—",
                "Busque ofertas para preencher",
            )

    if ofertas_dashboard:
        titulo_secao(
            "Melhores ofertas",
            "As menores ofertas encontradas entre as peças monitoradas.",
        )

        for posicao, (peca_oferta, oferta) in enumerate(
            ofertas_dashboard[:5],
            start=1,
        ):
            with st.container(border=True):
                a, b, c = st.columns([5, 2, 2])

                with a:
                    selo = "🏆" if posicao == 1 else f"#{posicao}"
                    st.markdown(
                        f"### {selo} {peca_oferta['nome']}"
                    )
                    st.caption(
                        f"{oferta['loja']} • "
                        f"{oferta.get('produto_nome') or 'Oferta monitorada'}"
                    )

                with b:
                    st.metric(
                        "Preço final",
                        formatar_real(oferta["preco_final"]),
                    )
                    if float(oferta.get("frete") or 0) > 0:
                        st.caption(
                            f"Inclui {formatar_real(oferta['frete'])} de frete"
                        )
                    else:
                        st.caption("Sem frete cadastrado")

                with c:
                    if oferta.get("link"):
                        st.link_button(
                            "Ver oferta",
                            oferta["link"],
                            use_container_width=True,
                        )

    titulo_secao(
        "Suas montagens",
        "Acompanhe o valor total e quanto do orçamento cada PC já utiliza.",
    )

    if not montagens_dashboard:
        st.info("Você ainda não criou nenhuma montagem.")
    else:
        for montagem_dashboard in montagens_dashboard[:6]:
            itens_dashboard = listar_pecas_montagem(
                montagem_dashboard["id"]
            )

            total_dashboard = sum(
                float(item["pecas"]["preco"]) * int(item["quantidade"])
                for item in itens_dashboard
                if item.get("pecas")
            )

            with st.container(border=True):
                a, b = st.columns([5, 2])

                with a:
                    st.markdown(
                        f"### {montagem_dashboard['nome']}"
                    )
                    st.caption(
                        f"{montagem_dashboard['faixa']} • "
                        f"{sum(int(i['quantidade']) for i in itens_dashboard)} item(ns)"
                    )

                    if montagem_dashboard.get("orcamento"):
                        barra_orcamento(
                            total_dashboard,
                            montagem_dashboard["orcamento"],
                        )

                with b:
                    st.metric(
                        "Total atual",
                        formatar_real(total_dashboard),
                    )


with aba_pecas:
    titulo_secao("Cadastrar componente", "Adicione uma peça e mantenha modelo, loja e dados técnicos organizados.")

    with st.form("nova_peca", clear_on_submit=True):
        c1, c2 = st.columns(2)

        with c1:
            tipo = st.selectbox("Tipo", TIPOS)
            nome = st.text_input("Nome", placeholder="Ex.: RTX 5060 AERO OC 8GB")
            fabricante = st.text_input("Fabricante", placeholder="Ex.: Gigabyte")
            modelo = st.text_input("Modelo", placeholder="Ex.: RTX 5060 AERO OC")
            mpn = st.text_input(
                "MPN / código do fabricante",
                placeholder="Ex.: GV-N5060AERO-OC-8GD",
            )
            gtin = st.text_input("GTIN / EAN (opcional)")

        with c2:
            loja = st.text_input("Loja atual")
            link = st.text_input("Link atual")
            preco = st.number_input(
                "Preço atual",
                min_value=0.0,
                step=10.0,
                format="%.2f",
            )

            with st.expander("Dados de compatibilidade"):
                socket = st.text_input("Socket", placeholder="AM4, AM5, LGA1700...")
                memoria_tipo = st.text_input(
                    "Tipo de memória",
                    placeholder="DDR4 ou DDR5",
                )
                formato = st.text_input(
                    "Formato",
                    placeholder="ATX, mATX, Mini-ITX...",
                )
                potencia_w = st.number_input(
                    "Potência da fonte (W)",
                    min_value=0.0,
                    step=50.0,
                )
                comprimento_mm = st.number_input(
                    "Comprimento da GPU (mm)",
                    min_value=0.0,
                    step=10.0,
                )
                gpu_max_mm = st.number_input(
                    "Máximo de GPU do gabinete (mm)",
                    min_value=0.0,
                    step=10.0,
                )
                psu_recomendada_w = st.number_input(
                    "Fonte recomendada pela GPU (W)",
                    min_value=0.0,
                    step=50.0,
                )
                formatos_suportados = st.text_input(
                    "Formatos suportados pelo gabinete",
                    placeholder="ATX, mATX, Mini-ITX",
                )
                observacoes = st.text_area("Observações")

        cadastrar = st.form_submit_button(
            "Adicionar peça",
            use_container_width=True,
            type="primary",
        )

    if cadastrar:
        if not nome.strip() or not loja.strip() or not link.strip():
            st.warning("Preencha nome, loja e link.")
        elif preco <= 0:
            st.warning("Digite um preço maior que zero.")
        else:
            adicionar_peca(
                tipo,
                nome.strip(),
                loja.strip(),
                link.strip(),
                preco,
                fabricante=fabricante.strip(),
                modelo=modelo.strip(),
                mpn=mpn.strip(),
                gtin=gtin.strip(),
                socket=socket.strip(),
                memoria_tipo=memoria_tipo.strip(),
                formato=formato.strip(),
                potencia_w=numero_opcional(potencia_w),
                comprimento_mm=numero_opcional(comprimento_mm),
                gpu_max_mm=numero_opcional(gpu_max_mm),
                psu_recomendada_w=numero_opcional(psu_recomendada_w),
                formatos_suportados=formatos_suportados.strip(),
                observacoes=observacoes.strip(),
            )
            st.success("Peça cadastrada.")
            st.rerun()

    pecas = listar_pecas()

    c1, c2 = st.columns(2)
    c1.metric("Peças cadastradas", len(pecas))
    c2.metric(
        "Soma dos preços atuais",
        formatar_real(sum(float(p["preco"]) for p in pecas)),
    )

    st.divider()

    for peca in pecas:
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 2, 2])

            with c1:
                st.markdown(f"### {peca['nome']}")
                st.write(f"**Tipo:** {peca['tipo']}")
                st.write(f"**Loja atual:** {peca['loja']}")
                detalhes = [
                    peca.get("fabricante"),
                    peca.get("modelo"),
                    peca.get("mpn"),
                ]
                detalhes = [str(v) for v in detalhes if v]
                if detalhes:
                    st.caption(" • ".join(detalhes))

                st.link_button(
                    "Abrir produto",
                    peca["link"],
                    use_container_width=True,
                )

            with c2:
                st.metric("Preço atual", formatar_real(peca["preco"]))
                if peca.get("atualizado_em"):
                    st.caption(f"Atualizado: {peca['atualizado_em']}")

            with c3:
                if st.button(
                    "Atualizar link",
                    key=f"update_preco_{peca['id']}",
                    use_container_width=True,
                ):
                    try:
                        novo = buscar_preco(peca["link"])
                        salvar_oferta(
                            peca["id"],
                            peca["loja"],
                            peca["link"],
                            novo,
                            0,
                            "automatico",
                            produto_nome=peca["nome"],
                            correspondencia=1.0,
                        )
                        aplicar_melhor_oferta(peca["id"])
                        st.rerun()
                    except Exception as erro:
                        st.error(str(erro))

                if st.button(
                    "Excluir",
                    key=f"excluir_{peca['id']}",
                    use_container_width=True,
                ):
                    excluir_peca(peca["id"])
                    st.rerun()


with aba_busca:
    titulo_secao("Buscar preços", "Compare ofertas da mesma peça e use automaticamente a opção mais barata.")

    if not pecas:
        st.info("Cadastre uma peça primeiro.")
    else:
        opcoes = {
            f"{p['tipo']} — {p['nome']}": p
            for p in pecas
        }

        chave = st.selectbox(
            "Peça",
            list(opcoes.keys()),
            key="busca_peca",
        )
        peca = opcoes[chave]

        lojas = st.multiselect(
            "Lojas",
            list(PROVEDORES.keys()),
            default=list(PROVEDORES.keys()),
        )

        st.caption(
            "MPN/modelo preenchidos melhoram bastante a identificação da peça correta."
        )

        if st.button(
            "🔎 Procurar ofertas",
            use_container_width=True,
            type="primary",
        ):
            with st.spinner("Consultando lojas..."):
                resultados, erros = buscar_ofertas(
                    peca,
                    lojas=lojas,
                    limite_por_loja=8,
                )

            for oferta in resultados:
                salvar_oferta(
                    peca["id"],
                    oferta["loja"],
                    oferta["link"],
                    oferta["preco"],
                    oferta.get("frete") or 0,
                    oferta.get("origem") or "busca",
                    oferta.get("vendedor"),
                    oferta.get("produto_nome"),
                    oferta.get("identificador_externo"),
                    oferta.get("correspondencia"),
                )

            if resultados:
                aplicar_melhor_oferta(peca["id"])
                st.success(f"{len(resultados)} oferta(s) compatível(is) salva(s).")

            if erros:
                st.warning("Algumas lojas não puderam ser consultadas:")
                for loja_nome, erro in erros.items():
                    st.write(f"**{loja_nome}:** {erro}")

            st.rerun()

        ofertas = listar_ofertas(peca["id"])

        if ofertas:
            melhor = ofertas[0]
            c1, c2, c3 = st.columns(3)
            c1.metric("Melhor loja", melhor["loja"])
            c2.metric("Preço + frete", formatar_real(melhor["preco_final"]))
            c3.metric(
                "Confiança",
                f"{float(melhor.get('correspondencia') or 0) * 100:.0f}%",
            )

            if st.button(
                "Aplicar melhor oferta à peça",
                use_container_width=True,
            ):
                aplicar_melhor_oferta(peca["id"])
                st.rerun()

        for posicao, oferta in enumerate(ofertas, start=1):
            with st.container(border=True):
                c1, c2, c3 = st.columns([5, 2, 2])

                with c1:
                    selo = "🏆 " if posicao == 1 else ""
                    st.markdown(f"### {selo}{oferta['loja']}")
                    if oferta.get("produto_nome"):
                        st.write(oferta["produto_nome"])
                    if oferta.get("vendedor"):
                        st.caption(f"Vendedor: {oferta['vendedor']}")
                    st.link_button(
                        "Abrir oferta",
                        oferta["link"],
                        use_container_width=True,
                    )

                with c2:
                    st.write("Produto:", formatar_real(oferta["preco"]))
                    st.write("Frete:", formatar_real(oferta["frete"]))
                    st.metric("Total", formatar_real(oferta["preco_final"]))

                with c3:
                    confianca = float(oferta.get("correspondencia") or 0)
                    st.write(f"Correspondência: {confianca * 100:.0f}%")
                    if st.button(
                        "Excluir oferta",
                        key=f"del_offer_{oferta['id']}",
                    ):
                        excluir_oferta(oferta["id"])
                        st.rerun()

        with st.expander("Adicionar oferta manualmente"):
            with st.form("oferta_manual", clear_on_submit=True):
                loja_manual = st.text_input("Loja")
                link_manual = st.text_input("Link")
                preco_manual = st.number_input(
                    "Preço",
                    min_value=0.0,
                    step=10.0,
                    format="%.2f",
                )
                frete_manual = st.number_input(
                    "Frete",
                    min_value=0.0,
                    step=5.0,
                    format="%.2f",
                )
                enviar = st.form_submit_button("Salvar")

            if enviar:
                salvar_oferta(
                    peca["id"],
                    loja_manual.strip(),
                    link_manual.strip(),
                    preco_manual,
                    frete_manual,
                    "manual",
                    produto_nome=peca["nome"],
                    correspondencia=1.0,
                )
                aplicar_melhor_oferta(peca["id"])
                st.rerun()


with aba_montagens:
    titulo_secao("Montagens de PC", "Crie configurações por orçamento e acompanhe o total em tempo real.")

    with st.form("nova_montagem", clear_on_submit=True):
        c1, c2 = st.columns(2)

        with c1:
            nome_montagem = st.text_input(
                "Nome",
                placeholder="Ex.: PC Gamer até R$ 5.000",
            )
            faixa = st.selectbox("Categoria", FAIXAS)
            orcamento = st.number_input(
                "Orçamento máximo (0 = sem limite)",
                min_value=0.0,
                step=500.0,
                format="%.2f",
            )

        with c2:
            descricao = st.text_area("Descrição")

        criar = st.form_submit_button(
            "Criar montagem",
            use_container_width=True,
            type="primary",
        )

    if criar:
        if not nome_montagem.strip():
            st.warning("Digite um nome.")
        else:
            criar_montagem(
                nome_montagem.strip(),
                faixa,
                descricao.strip(),
                orcamento if orcamento > 0 else None,
            )
            st.rerun()

    montagens = listar_montagens()
    cards = []

    for montagem in montagens:
        itens = listar_pecas_montagem(montagem["id"])
        total = sum(
            float(i["pecas"]["preco"]) * int(i["quantidade"])
            for i in itens
            if i.get("pecas")
        )
        cards.append((total, montagem, itens))

    cards.sort(key=lambda item: item[0])

    for posicao, (total, montagem, itens) in enumerate(cards, start=1):
        titulo = f"{posicao}. {montagem['nome']} — {formatar_real(total)}"

        with st.expander(titulo, expanded=posicao == 1):
            st.write(f"**Categoria:** {montagem['faixa']}")
            if montagem.get("descricao"):
                st.write(montagem["descricao"])

            c1, c2, c3 = st.columns(3)
            c1.metric("Total", formatar_real(total))
            c2.metric("Itens", sum(int(i["quantidade"]) for i in itens))

            orc = montagem.get("orcamento")
            if orc:
                saldo = float(orc) - total
                c3.metric(
                    "Saldo do orçamento",
                    formatar_real(saldo),
                    delta=f"{saldo:+.2f}",
                )
                barra_orcamento(total, orc)
            else:
                c3.metric("Orçamento", "Sem limite")

            avisos = verificar_compatibilidade(itens)
            erros_comp = [a for a in avisos if a[0] == "erro"]
            if erros_comp:
                st.error(
                    "Há incompatibilidades nesta montagem. "
                    "Veja a aba Compatibilidade."
                )

            for item in itens:
                peca_item = item.get("pecas")
                if not peca_item:
                    continue

                a, b, c = st.columns([5, 2, 1])
                a.write(
                    f"**{peca_item['tipo']}** — {peca_item['nome']} "
                    f"({peca_item['loja']})"
                )
                b.write(
                    f"{item['quantidade']} × "
                    f"{formatar_real(peca_item['preco'])}"
                )

                if c.button(
                    "Remover",
                    key=f"rm_{montagem['id']}_{item['id']}",
                ):
                    remover_peca_montagem(item["id"])
                    st.rerun()

            if pecas:
                nomes = {
                    f"{p['tipo']} — {p['nome']} — {formatar_real(p['preco'])}": p["id"]
                    for p in pecas
                }
                escolha = st.selectbox(
                    "Adicionar peça",
                    list(nomes.keys()),
                    key=f"add_select_{montagem['id']}",
                )
                qtd = st.number_input(
                    "Quantidade",
                    min_value=1,
                    max_value=20,
                    value=1,
                    key=f"qtd_{montagem['id']}",
                )

                if st.button(
                    "Adicionar à montagem",
                    key=f"add_btn_{montagem['id']}",
                    use_container_width=True,
                ):
                    adicionar_peca_montagem(
                        montagem["id"],
                        nomes[escolha],
                        int(qtd),
                    )
                    st.rerun()

            if st.button(
                "Excluir montagem",
                key=f"del_build_{montagem['id']}",
            ):
                excluir_montagem(montagem["id"])
                st.rerun()


with aba_compatibilidade:
    titulo_secao("Compatibilidade", "Verifique conflitos básicos entre processador, placa-mãe, memória, fonte e gabinete.")

    montagens = listar_montagens()

    if not montagens:
        st.info("Crie uma montagem primeiro.")
    else:
        opcoes_m = {m["nome"]: m for m in montagens}
        escolha_m = st.selectbox(
            "Montagem",
            list(opcoes_m.keys()),
            key="compat_montagem",
        )
        montagem = opcoes_m[escolha_m]
        itens = listar_pecas_montagem(montagem["id"])
        avisos = verificar_compatibilidade(itens)

        for nivel, mensagem in avisos:
            if nivel == "ok":
                st.success(mensagem)
            elif nivel == "erro":
                st.error(mensagem)
            else:
                st.warning(mensagem)

        st.caption(
            "A checagem depende dos dados técnicos cadastrados. "
            "Ela ajuda a encontrar conflitos óbvios, mas não substitui a ficha técnica do fabricante."
        )


with aba_historico:
    titulo_secao("Histórico de preços", "Veja como o preço das suas peças mudou ao longo do tempo.")

    if not pecas:
        st.info("Cadastre uma peça primeiro.")
    else:
        opcoes_h = {
            f"{p['nome']} — {p['loja']}": p["id"]
            for p in pecas
        }
        escolha_h = st.selectbox(
            "Peça",
            list(opcoes_h.keys()),
            key="historico",
        )

        historico = pegar_historico(opcoes_h[escolha_h])

        if not historico:
            st.info("Ainda não há histórico.")
        else:
            dados = pd.DataFrame(historico)
            dados["preco"] = dados["preco"].astype(float)
            dados["data"] = pd.to_datetime(dados["data"], utc=True)
            dados = dados.sort_values("data")

            c1, c2, c3 = st.columns(3)
            c1.metric("Atual", formatar_real(dados.iloc[-1]["preco"]))
            c2.metric("Menor", formatar_real(dados["preco"].min()))
            c3.metric("Maior", formatar_real(dados["preco"].max()))

            st.line_chart(
                dados.set_index("data")[["preco"]],
                y_label="Preço (R$)",
            )

            tabela = dados[["data", "preco"]].copy()
            tabela["data"] = tabela["data"].dt.strftime("%d/%m/%Y %H:%M")
            tabela["preco"] = tabela["preco"].apply(formatar_real)
            tabela.columns = ["Data", "Preço"]

            st.dataframe(
                tabela.iloc[::-1],
                hide_index=True,
                use_container_width=True,
            )


with aba_alertas:
    titulo_secao("Alertas de preço", "Defina uma meta e acompanhe quando uma peça atingir o valor desejado.")

    if pecas:
        opcoes_a = {
            f"{p['nome']} — atual {formatar_real(p['preco'])}": p["id"]
            for p in pecas
        }

        with st.form("novo_alerta", clear_on_submit=True):
            escolha_a = st.selectbox("Peça", list(opcoes_a.keys()))
            alvo = st.number_input(
                "Avisar quando chegar a",
                min_value=0.0,
                step=50.0,
                format="%.2f",
            )
            salvar_alerta = st.form_submit_button(
                "Criar alerta",
                use_container_width=True,
            )

        if salvar_alerta and alvo > 0:
            criar_alerta(opcoes_a[escolha_a], alvo)
            st.rerun()

    alertas = listar_alertas()

    if not alertas:
        st.info("Nenhum alerta ativo.")

    for alerta in alertas:
        peca_alerta = alerta.get("pecas") or {}
        atual = float(peca_alerta.get("preco") or 0)
        alvo = float(alerta["preco_alvo"])
        atingido = atual <= alvo

        with st.container(border=True):
            c1, c2, c3 = st.columns([4, 2, 1])

            c1.write(f"**{peca_alerta.get('nome', 'Peça')}**")
            c1.write(
                "Meta:",
                formatar_real(alvo),
                "• Atual:",
                formatar_real(atual),
            )

            if atingido:
                c2.success("🔥 Meta atingida")
            else:
                c2.info(
                    f"Faltam {formatar_real(max(atual - alvo, 0))}"
                )

            if c3.button(
                "Excluir",
                key=f"alerta_{alerta['id']}",
            ):
                excluir_alerta(alerta["id"])
                st.rerun()
