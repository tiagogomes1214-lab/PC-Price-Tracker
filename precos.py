import html
import json
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def _numero_br(valor):
    texto = str(valor).strip().replace("R$", "").replace(" ", "")

    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")

    texto = re.sub(r"[^0-9.]", "", texto)

    if not texto:
        return None

    try:
        return float(texto)
    except ValueError:
        return None


def buscar_preco_kabum(link):
    resposta = requests.get(
        link,
        headers=HEADERS,
        timeout=20,
    )

    resposta.raise_for_status()

    texto = html.unescape(resposta.text)

    padrao_preco = re.compile(
        r'"valueAsString":"R\$\s*[\d.]+,\d{2}",'
        r'"value":(?P<valor>\d+(?:\.\d+)?)'
    )

    precos = list(padrao_preco.finditer(texto))

    if not precos:
        raise ValueError("Nenhum preço foi encontrado na página da KaBuM.")

    posicoes_pix = [
        resultado.start()
        for resultado in re.finditer(
            r"PIX",
            texto,
            re.IGNORECASE,
        )
    ]

    if not posicoes_pix:
        raise ValueError("Não encontrei a informação de preço no PIX.")

    melhor_preco = min(
        precos,
        key=lambda preco: min(
            abs(preco.start() - posicao_pix)
            for posicao_pix in posicoes_pix
        ),
    )

    return float(melhor_preco.group("valor"))


def _procurar_preco_json(objeto):
    if isinstance(objeto, dict):
        ofertas = objeto.get("offers")

        if ofertas is not None:
            preco = _procurar_preco_json(ofertas)
            if preco is not None:
                return preco

        for chave in ("price", "lowPrice"):
            if chave in objeto:
                preco = _numero_br(objeto[chave])
                if preco is not None:
                    return preco

        for valor in objeto.values():
            preco = _procurar_preco_json(valor)
            if preco is not None:
                return preco

    elif isinstance(objeto, list):
        for item in objeto:
            preco = _procurar_preco_json(item)
            if preco is not None:
                return preco

    return None


def buscar_preco_generico(link):
    resposta = requests.get(
        link,
        headers=HEADERS,
        timeout=20,
    )

    resposta.raise_for_status()

    soup = BeautifulSoup(resposta.text, "html.parser")

    seletores = [
        'meta[property="product:price:amount"]',
        'meta[property="og:price:amount"]',
        'meta[itemprop="price"]',
        '[itemprop="price"]',
    ]

    for seletor in seletores:
        elemento = soup.select_one(seletor)

        if elemento:
            valor = elemento.get("content") or elemento.get_text(strip=True)
            preco = _numero_br(valor)

            if preco is not None:
                return preco

    for script in soup.find_all("script", type="application/ld+json"):
        if not script.string:
            continue

        try:
            dados = json.loads(script.string)
        except json.JSONDecodeError:
            continue

        preco = _procurar_preco_json(dados)

        if preco is not None:
            return preco

    raise ValueError("O site não expôs um preço que o leitor genérico consiga identificar.")


def buscar_preco(link):
    host = urlparse(link).netloc.lower()

    if "kabum.com.br" in host:
        return buscar_preco_kabum(link)

    if "shopee.com.br" in host:
        raise ValueError(
            "A Shopee exige integração específica. "
            "O link continua salvo, mas a atualização automática por link ainda não está habilitada."
        )

    if "aliexpress." in host:
        raise ValueError(
            "O AliExpress exige integração específica. "
            "O link continua salvo, mas a atualização automática por link ainda não está habilitada."
        )

    return buscar_preco_generico(link)
