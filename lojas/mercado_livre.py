import os
import re
from urllib.parse import quote_plus

import requests

from .comum import HEADERS, numero_preco


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
    item_id = _extrair_item_id(link)

    if not item_id:
        raise ValueError("Não consegui identificar o ID do anúncio do Mercado Livre.")

    url = f"{API}/items/{item_id}/prices"
    resposta = requests.get(url, headers=_headers(), timeout=20)

    if resposta.status_code in (401, 403):
        raise RuntimeError("Defina ML_ACCESS_TOKEN nos secrets.")

    resposta.raise_for_status()
    dados = resposta.json()

    valores = [
        numero_preco(preco.get("amount"))
        for preco in dados.get("prices", [])
        if preco.get("amount") is not None
    ]
    valores = [v for v in valores if v is not None]

    if not valores:
        raise ValueError("Preço não retornado pela API do Mercado Livre.")

    return min(valores)
