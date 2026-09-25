from urllib.parse import quote_plus

from .comum import buscar_html, ofertas_de_cards, preco_generico_url


def preco_terabyte_url(link):
    return preco_generico_url(link)


def buscar_terabyte(termo, alvo=None, limite=10):
    url = f"https://www.terabyteshop.com.br/busca?str={quote_plus(termo)}"
    html = buscar_html(url)

    return ofertas_de_cards(
        html,
        "https://www.terabyteshop.com.br",
        "Terabyte",
        limite=limite,
    )
