from .comum import preco_generico_url


def buscar_shopee(termo, alvo=None, limite=10):
    raise RuntimeError(
        "A busca pública da Shopee não possui uma API de catálogo genérica "
        "habilitada neste projeto. Cadastre links de ofertas da Shopee no comparador."
    )


def preco_shopee_url(link):
    return preco_generico_url(link)
