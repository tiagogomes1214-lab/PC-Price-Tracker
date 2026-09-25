from banco import (
    aplicar_melhor_oferta,
    listar_pecas,
    salvar_oferta,
)
from buscador import buscar_ofertas


LOJAS = [
    "KaBuM",
    "Pichau",
    "Terabyte",
    "Mercado Livre",
    "Amazon",
    "AliExpress",
    "Shopee",
]


def main():
    pecas = listar_pecas()

    for peca in pecas:
        print()
        print("Buscando:", peca["nome"])

        ofertas, erros = buscar_ofertas(
            peca,
            lojas=LOJAS,
            limite_por_loja=6,
        )

        for oferta in ofertas:
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

        if ofertas:
            melhor = aplicar_melhor_oferta(peca["id"])
            print(
                "Melhor:",
                melhor["loja"],
                melhor["preco_final"],
            )

        for loja, erro in erros.items():
            print(f"{loja}: {erro}")


if __name__ == "__main__":
    main()
