import pandas as pd
import streamlit as st

from banco import (
    adicionar_peca,
    adicionar_peca_montagem,
    atualizar_preco,
    criar_montagem,
    excluir_montagem,
    excluir_peca,
    listar_montagens,
    listar_pecas,
    listar_pecas_montagem,
    pegar_historico,
    remover_peca_montagem,
)
from precos import buscar_preco


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


def atualizar_uma_peca(peca):
    novo_preco = buscar_preco(peca["link"])
    alterou = atualizar_preco(peca["id"], novo_preco)
    return novo_preco, alterou


st.set_page_config(
    page_title="PC Price Tracker",
    page_icon="🖥️",
    layout="wide",
)

st.title("🖥️ PC Price Tracker")
st.caption("Peças, montagens e histórico de preços em um só lugar.")

aba_pecas, aba_montagens, aba_historico = st.tabs(
    ["Peças", "Montagens", "Histórico"]
)

pecas = listar_pecas()


with aba_pecas:
    st.subheader("Cadastrar peça")

    with st.form("form_nova_peca", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            tipo = st.selectbox("Tipo da peça", TIPOS)
            nome = st.text_input("Nome da peça")
            loja = st.text_input("Loja")

        with col2:
            link = st.text_input("Link do produto")
            preco = st.number_input(
                "Preço atual",
                min_value=0.0,
                step=10.0,
                format="%.2f",
            )

        cadastrar = st.form_submit_button(
            "Adicionar peça",
            use_container_width=True,
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
            )
            st.success("Peça cadastrada com sucesso.")
            st.rerun()

    pecas = listar_pecas()
    total_pecas = sum(float(peca["preco"]) for peca in pecas)

    col1, col2 = st.columns(2)
    col1.metric("Peças cadastradas", len(pecas))
    col2.metric("Soma de todas as peças", formatar_real(total_pecas))

    if pecas and st.button("🔄 Atualizar todas as peças", use_container_width=True):
        sucessos = 0
        falhas = []

        with st.spinner("Consultando as lojas..."):
            for peca in pecas:
                try:
                    atualizar_uma_peca(peca)
                    sucessos += 1
                except Exception as erro:
                    falhas.append(f"{peca['nome']}: {erro}")

        if sucessos:
            st.success(f"{sucessos} peça(s) consultada(s).")

        if falhas:
            st.warning("Algumas peças não puderam ser atualizadas:")
            for falha in falhas:
                st.write("•", falha)

        st.rerun()

    st.divider()
    st.subheader("Catálogo de peças")

    if not pecas:
        st.info("Nenhuma peça cadastrada ainda.")

    for peca in pecas:
        with st.container(border=True):
            col_info, col_preco, col_acoes = st.columns([4, 2, 2])

            with col_info:
                st.markdown(f"### {peca['nome']}")
                st.write(f"**Tipo:** {peca['tipo']}")
                st.write(f"**Loja:** {peca['loja']}")
                st.link_button(
                    "Abrir produto na loja",
                    peca["link"],
                    use_container_width=True,
                )

            with col_preco:
                st.metric("Preço atual", formatar_real(peca["preco"]))
                if peca.get("atualizado_em"):
                    st.caption(f"Última consulta: {peca['atualizado_em']}")

            with col_acoes:
                if st.button(
                    "Atualizar preço",
                    key=f"atualizar_{peca['id']}",
                    use_container_width=True,
                ):
                    try:
                        novo_preco, alterou = atualizar_uma_peca(peca)
                        if alterou:
                            st.success(f"Novo preço: {formatar_real(novo_preco)}")
                        else:
                            st.info("O preço continua igual.")
                        st.rerun()
                    except Exception as erro:
                        st.error(f"Não foi possível atualizar: {erro}")

                if st.button(
                    "Excluir peça",
                    key=f"excluir_{peca['id']}",
                    use_container_width=True,
                ):
                    excluir_peca(peca["id"])
                    st.rerun()


with aba_montagens:
    st.subheader("Montagens de PC")
    st.caption(
        "Crie vários PCs e compare do mais barato ao mais caro usando os preços atuais das peças."
    )

    try:
        montagens = listar_montagens()
        banco_montagens_ok = True
    except Exception:
        montagens = []
        banco_montagens_ok = False

    if not banco_montagens_ok:
        st.warning(
            "As tabelas de montagens ainda não existem no Supabase. "
            "Execute o arquivo migrations/002_montagens.sql no SQL Editor."
        )
    else:
        with st.form("form_montagem", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                nome_montagem = st.text_input(
                    "Nome da montagem",
                    placeholder="Ex.: PC Gamer de entrada",
                )
                faixa = st.selectbox("Categoria", FAIXAS)

            with col2:
                descricao = st.text_area(
                    "Descrição",
                    placeholder="Ex.: PC para Full HD, estudos e jogos competitivos.",
                )

            criar = st.form_submit_button(
                "Criar montagem",
                use_container_width=True,
            )

        if criar:
            if not nome_montagem.strip():
                st.warning("Digite um nome para a montagem.")
            else:
                criar_montagem(
                    nome_montagem.strip(),
                    faixa,
                    descricao.strip(),
                )
                st.success("Montagem criada.")
                st.rerun()

        montagens = listar_montagens()

        cards = []
        for montagem in montagens:
            itens = listar_pecas_montagem(montagem["id"])
            total = sum(
                float(item["pecas"]["preco"]) * int(item["quantidade"])
                for item in itens
                if item.get("pecas")
            )
            cards.append((total, montagem, itens))

        cards.sort(key=lambda item: item[0])

        if not cards:
            st.info("Crie sua primeira montagem de PC.")

        for posicao, (total, montagem, itens) in enumerate(cards, start=1):
            titulo = (
                f"{posicao}. {montagem['nome']} — {formatar_real(total)}"
            )

            with st.expander(titulo, expanded=posicao == 1):
                st.write(f"**Categoria:** {montagem['faixa']}")
                if montagem.get("descricao"):
                    st.write(montagem["descricao"])

                col_total, col_quantidade = st.columns(2)
                col_total.metric("Total atual", formatar_real(total))
                col_quantidade.metric("Itens", sum(int(i["quantidade"]) for i in itens))

                st.markdown("#### Peças desta montagem")

                if not itens:
                    st.info("Nenhuma peça adicionada nesta montagem.")

                for item in itens:
                    peca = item.get("pecas")
                    if not peca:
                        continue

                    c1, c2, c3 = st.columns([5, 2, 1])
                    c1.write(
                        f"**{peca['tipo']}** — {peca['nome']} ({peca['loja']})"
                    )
                    c2.write(
                        f"{item['quantidade']} × {formatar_real(peca['preco'])}"
                    )

                    if c3.button(
                        "Remover",
                        key=f"remover_{montagem['id']}_{item['id']}",
                    ):
                        remover_peca_montagem(item["id"])
                        st.rerun()

                st.markdown("#### Adicionar peça")

                if pecas:
                    opcoes = {
                        f"{p['tipo']} — {p['nome']} — {p['loja']} — {formatar_real(p['preco'])}": p["id"]
                        for p in pecas
                    }

                    escolha = st.selectbox(
                        "Escolha uma peça do catálogo",
                        list(opcoes.keys()),
                        key=f"select_peca_{montagem['id']}",
                    )

                    quantidade = st.number_input(
                        "Quantidade",
                        min_value=1,
                        max_value=20,
                        value=1,
                        step=1,
                        key=f"qtd_{montagem['id']}",
                    )

                    if st.button(
                        "Adicionar à montagem",
                        key=f"add_{montagem['id']}",
                        use_container_width=True,
                    ):
                        adicionar_peca_montagem(
                            montagem["id"],
                            opcoes[escolha],
                            int(quantidade),
                        )
                        st.rerun()
                else:
                    st.info("Cadastre peças primeiro na aba Peças.")

                if st.button(
                    "Excluir montagem",
                    key=f"excluir_montagem_{montagem['id']}",
                ):
                    excluir_montagem(montagem["id"])
                    st.rerun()


with aba_historico:
    st.subheader("Histórico de preços")

    if not pecas:
        st.info("Cadastre uma peça para começar a registrar preços.")
    else:
        opcoes_historico = {
            f"{p['nome']} — {p['loja']}": p["id"]
            for p in pecas
        }

        escolha = st.selectbox(
            "Escolha uma peça",
            list(opcoes_historico.keys()),
            key="historico_peca",
        )

        historico = pegar_historico(opcoes_historico[escolha])

        if not historico:
            st.info("Ainda não há histórico para essa peça.")
        else:
            dados = pd.DataFrame(historico)
            dados["preco"] = dados["preco"].astype(float)
            dados["data"] = pd.to_datetime(dados["data"], utc=True)
            dados = dados.sort_values("data")

            col1, col2, col3 = st.columns(3)
            col1.metric("Preço atual", formatar_real(dados.iloc[-1]["preco"]))
            col2.metric("Menor registrado", formatar_real(dados["preco"].min()))
            col3.metric("Maior registrado", formatar_real(dados["preco"].max()))

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
                use_container_width=True,
                hide_index=True,
            )
