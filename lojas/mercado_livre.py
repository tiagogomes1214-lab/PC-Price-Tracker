import os
import re
from urllib.parse import quote_plus

import requests

from .comum import HEADERS, numero_preco, preco_generico_url


API = "https://api.mercadolibre.com"


def _headers():
    headers = dict(HEADERS)
    token = os.getenv("ML_ACCESS_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def buscar_mercado_livre(termo, alvo=None, limite=10):
    url = f"{API}/sites/MLB/search"
    resposta = requests.get(
        url,
        params={
            "q": termo,
            "sort": "price_asc",
            "limit": min(int(limite), 50),
        },
        headers=_headers(),
        timeout=20,
    )

    if resposta.status_code in (401, 403):
        raise RuntimeError(
            "Mercado Livre exige ML_ACCESS_TOKEN para esta consulta."
        )

    resposta.raise_for_status()
    dados = resposta.json()

    resultados = []

    for item in dados.get("results", []):
        preco = numero_preco(item.get("price"))
        if preco is None:
            continue

        shipping = item.get("shipping") or {}
        frete = 0.0 if shipping.get("free_shipping") else 0.0

        resultados.append(
            {
                "loja": "Mercado Livre",
                "produto_nome": item.get("title") or "",
                "preco": preco,
                "frete": frete,
                "link": item.get("permalink") or "",
                "disponivel": item.get("status", "active") == "active",
                "origem": "api",
                "vendedor": str(item.get("seller", {}).get("nickname") or ""),
                "identificador_externo": item.get("id"),
            }
        )

    return resultados[:limite]


def _extrair_item_id(link):
    match = re.search(r"(MLB[-_]?\d+)", link.upper())
    if not match:
        return None
    return match.group(1).replace("-", "").replace("_", "")


def preco_mercado_livre_url(link):
    """
    Atualiza um anúncio pelo link público.

    Primeiro tenta extrair o preço diretamente da página, sem exigir token.
    Se isso falhar e houver um ML_ACCESS_TOKEN configurado, tenta a API oficial.
    """

    try:
        return preco_generico_url(link)
    except Exception as erro_pagina:
        item_id = _extrair_item_id(link)
        token = os.getenv("ML_ACCESS_TOKEN")

        if not item_id or not token:
            raise ValueError(
                "Não consegui identificar um preço confiável nesse link do Mercado Livre. "
                "Tente usar o link completo do anúncio. Se a página continuar bloqueando "
                "a leitura, configure ML_ACCESS_TOKEN para usar a API oficial."
            ) from erro_pagina

        url = f"{API}/items/{item_id}/prices"
        resposta = requests.get(url, headers=_headers(), timeout=20)
        resposta.raise_for_status()
        dados = resposta.json()

        valores = [
            numero_preco(preco.get("amount"))
            for preco in dados.get("prices", [])
            if preco.get("amount") is not None
        ]
        valores = [v for v in valores if v is not None]

        if not valores:
            raise ValueError(
                "O Mercado Livre não retornou um preço para esse anúncio."
            )

        return min(valores)
