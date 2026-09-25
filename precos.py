import json
import re

import requests
from bs4 import BeautifulSoup


def procurar_produtos(objeto, encontrados=None):

    if encontrados is None:
        encontrados = []

    if isinstance(objeto, dict):

        if (
            isinstance(objeto.get("price"), (int, float))
            and isinstance(objeto.get("description"), str)
        ):
            encontrados.append(objeto)

        for valor in objeto.values():
            procurar_produtos(
                valor,
                encontrados
            )

    elif isinstance(objeto, list):

        for item in objeto:
            procurar_produtos(
                item,
                encontrados
            )

    return encontrados


def buscar_preco_kabum(link):

    resultado = re.search(
        r"/produto/(\d+)",
        link
    )

    if not resultado:

        raise ValueError(
            "Não consegui identificar o código do produto da Kabum."
        )

    codigo = resultado.group(1)

    url_busca = (
        f"https://www.kabum.com.br/busca/{codigo}"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/153.0.0.0 Safari/537.36"
        )
    }

    resposta = requests.get(
        url_busca,
        headers=headers,
        timeout=15
    )

    resposta.raise_for_status()

    soup = BeautifulSoup(
        resposta.text,
        "html.parser"
    )

    script = soup.find(
        "script",
        id="__NEXT_DATA__"
    )

    if script is None or script.string is None:

        raise ValueError(
            "A Kabum não retornou os dados do produto."
        )

    dados = json.loads(
        script.string
    )

    produtos = procurar_produtos(
        dados
    )

    if not produtos:

        raise ValueError(
            "Produto não encontrado nos dados da Kabum."
        )

    produto = produtos[0]

    preco_normal = produto.get(
        "price"
    )

    preco_pix = produto.get(
        "priceWithDiscount"
    )

    if (
        isinstance(preco_pix, (int, float))
        and isinstance(preco_normal, (int, float))
        and preco_pix < preco_normal
    ):
        return float(preco_pix)

    if isinstance(
        preco_normal,
        (int, float)
    ):
        return float(preco_normal)

    raise ValueError(
        "Preço não encontrado."
    )


def buscar_preco(link):

    if "kabum.com.br" in link.lower():

        return buscar_preco_kabum(
            link
        )

    raise ValueError(
        "Essa loja ainda não possui atualização automática."
    )