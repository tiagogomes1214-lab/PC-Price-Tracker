from urllib.parse import quote_plus

from .comum import buscar_html, ofertas_de_cards, preco_generico_url


def preco_pichau_url(link):
    return preco_generico_url(link)


def buscar_pichau(termo, alvo=None, limite=10):
    urls = [
        f"https://www.pichau.com.br/catalogsearch/result/?q={quote_plus(termo)}",
        f"https://www.pichau.com.br/search?q={quote_plus(termo)}",
    ]

    ultimo_erro = None

    for url in urls:
        try:
            html = buscar_html(url)
            resultados = ofertas_de_cards(
                html,
                "https://www.pichau.com.br",
                "Pichau",
                limite=limite,
            )
            if resultados:
                return resultados
        except Exception as erro:
            ultimo_erro = erro

    if ultimo_erro:
        raise ultimo_erro

    return []
