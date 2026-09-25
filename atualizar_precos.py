from banco import (
    aplicar_melhor_oferta,
    listar_ofertas,
    listar_pecas,
    marcar_oferta_indisponivel,
    salvar_oferta,
)
from precos import buscar_preco


def main():
    pecas = listar_pecas()

    consultadas = 0
    alteradas = 0
    erros = 0

    for peca in pecas:
        ofertas = listar_ofertas(peca["id"])

        if ofertas:
            for oferta in ofertas:
                try:
                    novo_preco = buscar_preco(oferta["link"])

                    salvar_oferta(
                        peca["id"],
                        oferta["loja"],
                        oferta["link"],
                        novo_preco,
                        oferta.get("frete") or 0,
                        "automatico",
                        oferta.get("vendedor"),
                        oferta.get("produto_nome"),
                        oferta.get("identificador_externo"),
                        oferta.get("correspondencia"),
                    )
                    consultadas += 1
                except Exception as erro:
                    erros += 1
                    print(
                        f"Oferta não atualizada: {peca['nome']} / "
                        f"{oferta['loja']}: {erro}"
                    )

            try:
                melhor = aplicar_melhor_oferta(peca["id"])
                alteradas += 1
                print(
                    f"{peca['nome']}: melhor oferta "
                    f"{melhor['loja']} = {float(melhor['preco_final']):.2f}"
                )
            except Exception as erro:
                erros += 1
                print(f"Erro aplicando melhor oferta em {peca['nome']}: {erro}")

        else:
            try:
                novo_preco = buscar_preco(peca["link"])
                salvar_oferta(
                    peca["id"],
                    peca["loja"],
                    peca["link"],
                    novo_preco,
                    0,
                    "automatico",
                    produto_nome=peca["nome"],
                    correspondencia=1.0,
                )
                aplicar_melhor_oferta(peca["id"])
                consultadas += 1
            except Exception as erro:
                erros += 1
                print(f"Erro atualizando {peca['nome']}: {erro}")

    print()
    print("Atualização terminada.")
    print("Ofertas consultadas:", consultadas)
    print("Peças recalculadas:", alteradas)
    print("Erros:", erros)


if __name__ == "__main__":
    main()
