from banco import listar_pecas, atualizar_preco
from precos import buscar_preco


pecas = listar_pecas()


for peca in pecas:

    try:

        preco_antigo = float(peca["preco"])

        preco_novo = buscar_preco(
            peca["link"]
        )

        print()
        print("Peça:", peca["nome"])
        print("Preço antigo:", preco_antigo)
        print("Preço encontrado:", preco_novo)


        if preco_novo != preco_antigo:

            atualizar_preco(
                peca["id"],
                preco_novo
            )

            print("Preço atualizado!")

        else:

            print("O preço continua igual.")


    except Exception as erro:

        print()
        print(
            "Erro ao atualizar:",
            peca["nome"]
        )

        print(erro)