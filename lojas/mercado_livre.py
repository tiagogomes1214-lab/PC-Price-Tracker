import os
import re
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import requests

try:
    import streamlit as st
except Exception:
    st = None

from .comum import (
    HEADERS,
    buscar_html,
    numero_preco,
    ofertas_de_cards,
    pontuar_correspondencia,
    preco_generico_url,
)


API = "https://api.mercadolibre.com"


def _token():
    token = _token()

    if token:
        return token

    if st is not None:
        try:
            token = st.secrets.get("ML_ACCESS_TOKEN")
            if token:
                return token
        except Exception:
            pass

    return None


def _headers():
    headers = dict(HEADERS)
    token = _token()

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


def _normalizar_item_id(valor):
    match = re.search(r"(MLB[-_]?\d{8,})", str(valor or "").upper())

    if not match:
        return None

    return match.group(1).replace("-", "").replace("_", "")


def _extrair_item_id(link):
    """
    Tenta encontrar o ID do anúncio específico.

    Suporta links com:
    - ?wid=MLB123...
    - ?item_id=MLB123...
    - ?pdp_filters=item_id:MLB123...
    - fragmentos que carreguem os mesmos parâmetros
    - links tradicionais de anúncio contendo MLB123... no próprio caminho
    """

    parsed = urlparse(link)

    blocos_parametros = [
        parse_qs(parsed.query),
        parse_qs(parsed.fragment),
    ]

    for parametros in blocos_parametros:
        for chave in ("wid", "item_id"):
            for valor in parametros.get(chave, []):
                item_id = _normalizar_item_id(valor)
                if item_id:
                    return item_id

        for valor in parametros.get("pdp_filters", []):
            match = re.search(
                r"item_id\s*[:=]\s*(MLB[-_]?\d{8,})",
                unquote(valor),
                re.IGNORECASE,
            )
            if match:
                return _normalizar_item_id(match.group(1))

    texto_extra = unquote(
        " ".join(
            [
                parsed.query or "",
                parsed.fragment or "",
            ]
        )
    )

    match = re.search(
        r"(?:wid|item_id)\s*[:=]\s*(MLB[-_]?\d{8,})",
        texto_extra,
        re.IGNORECASE,
    )
    if match:
        return _normalizar_item_id(match.group(1))

    match = re.search(
        r"pdp_filters[^#&]*item_id(?:%3A|:|=)(MLB[-_]?\d{8,})",
        link,
        re.IGNORECASE,
    )
    if match:
        return _normalizar_item_id(match.group(1))

    # Em páginas /p/ o MLB do caminho é o ID do catálogo, não do anúncio.
    if _extrair_catalog_product_id(link):
        return None

    return _normalizar_item_id(link)


def _preco_item_api_publica(item_id):
    """
    Tenta consultar os dados públicos do anúncio pelo ID.
    Não exige token quando o endpoint estiver disponível publicamente.
    """

    resposta = requests.get(
        f"{API}/items/{item_id}",
        headers=HEADERS,
        timeout=20,
    )

    if resposta.status_code in (401, 403, 404):
        return None

    resposta.raise_for_status()
    dados = resposta.json()

    preco = numero_preco(dados.get("price"))

    if preco is None or preco <= 0:
        return None

    return preco


def _termo_do_catalogo(link):
    caminho = unquote(urlparse(link).path)
    parte = caminho.split("/p/", 1)[0].strip("/")
    termo = re.sub(r"[-_]+", " ", parte)
    return " ".join(termo.split())


def _preco_catalogo_api(catalog_id):
    if not _token():
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
    Aceita anúncio individual, página de catálogo e catálogo com oferta específica.
    """

    item_id = _extrair_item_id(link)

    if item_id:
        # Links de catálogo podem carregar um anúncio específico via wid/item_id.
        # Quando isso acontece, acompanhamos esse anúncio em vez do catálogo inteiro.
        preco_item = _preco_item_api_publica(item_id)

        if preco_item is not None:
            return preco_item

        try:
            return preco_generico_url(link)
        except Exception as erro_pagina:
            token = _token()

            if not token:
                raise ValueError(
                    "Encontrei o anúncio específico do Mercado Livre, mas não consegui "
                    "ler o preço automaticamente. O ID encontrado foi "
                    f"{item_id}. Tente copiar novamente pelo botão Compartilhar do "
                    "Mercado Livre ou configure ML_ACCESS_TOKEN."
                ) from erro_pagina

            resposta = requests.get(
                f"{API}/items/{item_id}/sale_price",
                params={"context": "channel_marketplace"},
                headers=_headers(),
                timeout=20,
            )
            resposta.raise_for_status()
            dados = resposta.json()

            preco = numero_preco(dados.get("amount"))

            if preco is not None and preco > 0:
                return preco

            raise ValueError(
                "O Mercado Livre identificou o anúncio, mas não retornou o preço de venda."
            )

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

    # Link sem ID identificável: último recurso pela página pública.
    try:
        return preco_generico_url(link)
    except Exception as erro_pagina:
        raise ValueError(
            "Não consegui identificar um anúncio específico nem um preço confiável "
            "nesse link do Mercado Livre. Use o botão Compartilhar da oferta para "
            "copiar um link que contenha wid, item_id ou o ID MLB do anúncio."
        ) from erro_pagina
