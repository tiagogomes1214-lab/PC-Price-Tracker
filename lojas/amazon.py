import os
import re

import requests

from .comum import numero_preco


API = "https://creatorsapi.amazon/catalog/v1"


def _config():
    token = os.getenv("AMAZON_CREATORS_TOKEN")
    tag = os.getenv("AMAZON_PARTNER_TAG")

    if not token or not tag:
        raise RuntimeError(
            "Amazon exige AMAZON_CREATORS_TOKEN e AMAZON_PARTNER_TAG."
        )

    return token, tag


def _headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "x-marketplace": "www.amazon.com.br",
    }


def _achar_precos(objeto, saida=None):
    if saida is None:
        saida = []

    if isinstance(objeto, dict):
        for chave, valor in objeto.items():
            if chave.lower() in {"amount", "price", "displayamount"}:
                preco = numero_preco(valor)
                if preco is not None and preco > 0:
                    saida.append(preco)
            _achar_precos(valor, saida)
    elif isinstance(objeto, list):
        for item in objeto:
            _achar_precos(item, saida)

    return saida


def buscar_amazon(termo, alvo=None, limite=10):
    token, tag = _config()

    corpo = {
        "partnerTag": tag,
        "keywords": termo,
        "searchIndex": "Electronics",
        "itemCount": min(int(limite), 10),
        "resources": [
            "itemInfo.title",
            "offersV2.listings.price",
        ],
    }

    resposta = requests.post(
        f"{API}/searchItems",
        json=corpo,
        headers=_headers(token),
        timeout=25,
    )
    resposta.raise_for_status()
    dados = resposta.json()

    itens = (
        dados.get("searchResult", {}).get("items", [])
        or dados.get("SearchResult", {}).get("Items", [])
    )

    resultados = []

    for item in itens:
        titulo = (
            item.get("itemInfo", {}).get("title", {}).get("displayValue")
            or item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue")
            or ""
        )

        precos = _achar_precos(item)
        if not precos:
            continue

        resultados.append(
            {
                "loja": "Amazon",
                "produto_nome": titulo,
                "preco": min(precos),
                "frete": 0.0,
                "link": item.get("detailPageURL") or item.get("DetailPageURL") or "",
                "disponivel": True,
                "origem": "api",
                "vendedor": "Amazon Marketplace",
                "identificador_externo": item.get("asin") or item.get("ASIN"),
            }
        )

    return resultados[:limite]


def preco_amazon_url(link):
    token, tag = _config()

    match = re.search(r"(?:/dp/|/gp/product/)([A-Z0-9]{10})", link.upper())
    if not match:
        raise ValueError("Não consegui identificar o ASIN da Amazon.")

    asin = match.group(1)

    corpo = {
        "partnerTag": tag,
        "itemIds": [asin],
        "itemIdType": "ASIN",
        "condition": "New",
        "resources": ["itemInfo.title", "offersV2.listings.price"],
    }

    resposta = requests.post(
        f"{API}/getItems",
        json=corpo,
        headers=_headers(token),
        timeout=25,
    )
    resposta.raise_for_status()

    precos = _achar_precos(resposta.json())

    if not precos:
        raise ValueError("A Amazon não retornou preço para este ASIN.")

    return min(precos)
