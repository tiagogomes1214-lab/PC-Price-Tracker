import html as html_lib
import re
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from .comum import buscar_html, ofertas_de_cards, numero_preco


def preco_kabum_url(link):
    texto = html_lib.unescape(buscar_html(link))

    padrao = re.compile(
        r'"valueAsString":"R\$\s*[\d.]+,\d{2}",'
        r'"value":(?P<valor>\d+(?:\.\d+)?)'
    )

    precos = list(padrao.finditer(texto))
    posicoes_pix = [m.start() for m in re.finditer("PIX", texto, re.IGNORECASE)]

    if precos and posicoes_pix:
        melhor = min(
            precos,
            key=lambda preco: min(
                abs(preco.start() - posicao)
                for posicao in posicoes_pix
            ),
        )
        return float(melhor.group("valor"))

    soup = BeautifulSoup(texto, "html.parser")
    visivel = soup.get_text(" ", strip=True)

    match = re.search(
        r"R\$\s*([\d.]+,\d{2}).{0,80}?PIX",
        visivel,
        re.IGNORECASE,
    )

    if match:
        return numero_preco(match.group(1))

    raise ValueError("Não consegui identificar o preço da KaBuM.")


def buscar_kabum(termo, alvo=None, limite=10):
    url = f"https://www.kabum.com.br/busca/{quote_plus(termo)}"
    html = buscar_html(url)

    resultados = ofertas_de_cards(
        html,
        "https://www.kabum.com.br",
        "KaBuM",
        limite=limite,
    )

    return resultados
