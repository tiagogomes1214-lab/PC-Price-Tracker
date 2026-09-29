import os
import re
from urllib.parse import quote_plus, unquote, urlparse

import requests

from .comum import (
    HEADERS,
    buscar_html,
    numero_preco,
    ofertas_de_cards,
    pontuar_correspondencia,
    preco_generico_url,
)


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


def _extrair_catalog_product_id(link):
    match = re.search(r"/p/(MLB\d+)", link, re.IGNORECASE)
    if not match:
        return None
    return match.group(1).upper()


def _extrair_item_id(link):
    if _extrair_catalog_product_id(link):
        return None

    match = re.search(r"(MLB[-_]?\d{8,})", link.upper())
    if not match:
        return None

    return match.group(1).replace("-", "").replace("_", "")


def _termo_do_catalogo(link):
    caminho = unquote(urlparse(link).path)
    parte = caminho.split("/p/", 1)[0].strip("/")
    termo = re.sub(r"[-_]+", " ", parte)
    return " ".join(termo.split())


def _preco_catalogo_api(catalog_id):
    if not os.getenv("ML_ACCESS_TOKEN"):
        return None

    resposta = requests.get(
        f"{API}/products/{catalog_id}",
        headers=_headers(),
        timeout=20,
    )
    resposta.raise_for_status()
    dados = resposta.json()

    vencedor = dados.get("buy_box_winner") or {}
    preco = numero_preco(vencedor.get("price"))

    if preco is None:
        return None

    return preco


def _preco_catalogo_busca_publica(link):
    termo = _termo_do_catalogo(link)

    if not termo:
        return None

    slug = re.sub(r"\s+", "-", termo.lower())
    url_busca = f"https://lista.mercadolivre.com.br/{slug}"

    html = buscar_html(url_busca)

    ofertas = ofertas_de_cards(
        html,
        "https://www.mercadolivre.com.br",
        "Mercado Livre",
        limite=20,
    )

    if not ofertas:
        return None

    alvo = {"nome": termo}

    candidatas = []

    for oferta in ofertas:
        confianca = pontuar_correspondencia(
            alvo,
            oferta.get("produto_nome") or "",
        )

        if confianca >= 0.55:
            candidatas.append(
                (
                    confianca,
                    float(oferta["preco"]),
                )
            )

    if not candidatas:
        return None

    melhor_confianca = max(item[0] for item in candidatas)

    precos = [
        preco
        for confianca, preco in candidatas
        if confianca >= melhor_confianca - 0.08
    ]

    return min(precos) if precos else None


def preco_mercado_livre_url(link):
    """
    Aceita tanto anúncio individual quanto página de produto de catálogo.
    """

    catalog_id = _extrair_catalog_product_id(link)

    if catalog_id:
        # A página /p/ reúne várias ofertas do mesmo produto.
        # Com token, usamos a oferta vencedora oficial do catálogo.
        preco_api = _preco_catalogo_api(catalog_id)

        if preco_api is not None:
            return preco_api

        # Sem token, tenta primeiro a própria página pública.
        try:
            return preco_generico_url(link)
        except Exception:
            pass

        # Se a PDP bloquear requests, tenta a página pública de busca
        # usando o nome presente no próprio link.
        try:
            preco_busca = _preco_catalogo_busca_publica(link)
            if preco_busca is not None:
                return preco_busca
        except Exception:
            pass

        raise ValueError(
            "Esse é um produto de catálogo do Mercado Livre e não consegui "
            "ler uma oferta atual com segurança. Tente usar o link de um "
            "anúncio/vendedor específico ou configure ML_ACCESS_TOKEN."
        )

    # Anúncio individual: tenta a página pública primeiro.
    try:
        return preco_generico_url(link)
    except Exception as erro_pagina:
        item_id = _extrair_item_id(link)
        token = os.getenv("ML_ACCESS_TOKEN")

        if not item_id or not token:
            raise ValueError(
                "Não consegui identificar um preço confiável nesse anúncio do "
                "Mercado Livre. Tente usar o link completo do anúncio."
            ) from erro_pagina

        resposta = requests.get(
            f"{API}/items/{item_id}/prices",
            headers=_headers(),
            timeout=20,
        )
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
