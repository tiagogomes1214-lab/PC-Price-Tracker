import html
import re

import requests


def buscar_preco_kabum(link):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    resposta = requests.get(
        link,
        headers=headers,
        timeout=15
    )

    resposta.raise_for_status()

    # Converte:
    # &quot; -> "
    texto = html.unescape(
        resposta.text
    )

    # Procura estruturas como:
    #
    # "valueAsString":"R$ 2.799,99","value":2799.99
    padrao_preco = re.compile(
        r'"valueAsString":"R\$\s*[\d.]+,\d{2}",'
        r'"value":(?P<valor>\d+(?:\.\d+)?)'
    )

    precos = list(
        padrao_preco.finditer(texto)
    )

    if not precos:

        raise ValueError(
            "Nenhum preço foi encontrado na página da Kabum."
        )

    # Procura onde aparece a palavra PIX
    posicoes_pix = [
        resultado.start()
        for resultado in re.finditer(
            r"PIX",
            texto,
            re.IGNORECASE
        )
    ]

    if not posicoes_pix:

        raise ValueError(
            "Não encontrei a informação de preço no PIX."
        )

    melhor_preco = None
    menor_distancia = None

    # Procura o preço que estiver mais próximo
    # da informação de PIX
    for preco in precos:

        posicao_preco = preco.start()

        distancia = min(
            abs(
                posicao_preco - posicao_pix
            )
            for posicao_pix in posicoes_pix
        )

        if (
            menor_distancia is None
            or distancia < menor_distancia
        ):

            menor_distancia = distancia
            melhor_preco = preco

    if melhor_preco is None:

        raise ValueError(
            "Não consegui identificar o preço correto."
        )

    valor = melhor_preco.group(
        "valor"
    )

    return float(valor)


def buscar_preco(link):

    if "kabum.com.br" in link.lower():

        return buscar_preco_kabum(
            link
        )

    raise ValueError(
        "Essa loja ainda não possui atualização automática."
    )