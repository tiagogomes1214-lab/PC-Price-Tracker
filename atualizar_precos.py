from banco import listar_pecas, atualizar_preco
from precos import buscar_preco


def main():
    pecas = listar_pecas()

    sucessos = 0
    alteracoes = 0
    erros = 0

    for peca in pecas:
        try:
            preco_antigo = float(peca["preco"])
            preco_novo = buscar_preco(peca["link"])

            alterou = atualizar_preco(
                peca["id"],
                preco_novo,
            )

            sucessos += 1

            if alterou:
                alteracoes += 1
                print(
                    f"{peca['nome']}: "
                    f"{preco_antigo:.2f} -> {preco_novo:.2f}"
                )
            else:
                print(
                    f"{peca['nome']}: preço continua em {preco_novo:.2f}"
                )

        except Exception as erro:
            erros += 1
            print(f"Erro em {peca['nome']}: {erro}")

    print()
    print("Atualização terminada.")
    print("Consultadas:", sucessos)
    print("Alteradas:", alteracoes)
    print("Erros:", erros)


if __name__ == "__main__":
    main()
