import streamlit as st

from banco import (
    listar_pecas,
    adicionar_peca,
    excluir_peca,
    atualizar_preco
)

from precos import buscar_preco


st.set_page_config(
    page_title="PC Price Tracker",
    page_icon="🖥️"
)


st.title("🖥️ PC Price Tracker")

st.subheader("Adicionar nova peça")

tipo = st.selectbox(
    "Tipo da peça",
    [
        "Processador",
        "Placa de vídeo",
        "Placa-mãe",
        "Memória RAM",
        "SSD",
        "Fonte",
        "Gabinete",
        "Cooler",
        "Outro"
    ]
)

nome = st.text_input("Nome da peça")
loja = st.text_input("Loja")
link = st.text_input("Link do produto")

preco = st.number_input(
    "Preço",
    min_value=0.0,
    step=10.0,
    format="%.2f"
)

if st.button("Adicionar peça"):

    if nome == "" or loja == "" or link == "":

        st.warning("Preencha todos os campos.")

    elif preco <= 0:

        st.warning("Digite um preço válido.")

    else:

        adicionar_peca(
            tipo,
            nome,
            loja,
            link,
            preco
        )

        st.success("Peça cadastrada com sucesso!")

        st.rerun()


st.divider()

st.subheader("Peças cadastradas")

pecas = listar_pecas()

total = sum(float(peca["preco"]) for peca in pecas)

st.metric(
    "Valor total da montagem",
    f"R$ {total:.2f}"
)


if not pecas:

    st.info("Nenhuma peça cadastrada.")

else:

    for peca in pecas:

        st.subheader(peca["nome"])

        st.write("Tipo:", peca["tipo"])
        st.write("Loja:", peca["loja"])
        st.write("Preço: R$", peca["preco"])

        st.link_button(
            "Abrir produto na loja",
            peca["link"]
        )

        if st.button(
            "Atualizar preço",
            key=f"atualizar_{peca['id']}"
        ):

            try:

                novo_preco = buscar_preco(
                    peca["link"]
                )

                atualizar_preco(
                    peca["id"],
                    novo_preco
                )

                st.success(
                    f"Novo preço: R$ {novo_preco:.2f}"
                )

                st.rerun()

            except Exception as erro:

                st.error(
                    f"Não foi possível atualizar: {erro}"
                )

        if st.button(
            "Excluir peça",
            key=f"excluir_{peca['id']}"
        ):

            excluir_peca(peca["id"])

            st.success("Peça excluída!")

            st.rerun()

        st.divider()