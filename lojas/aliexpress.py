import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import requests

from .comum import numero_preco


API = "https://eco.taobao.com/router/rest"


def _config():
    app_key = os.getenv("ALIEXPRESS_APP_KEY")
    app_secret = os.getenv("ALIEXPRESS_APP_SECRET")
    tracking_id = os.getenv("ALIEXPRESS_TRACKING_ID", "")

    if not app_key or not app_secret:
        raise RuntimeError(
            "AliExpress exige ALIEXPRESS_APP_KEY e ALIEXPRESS_APP_SECRET."
        )

    return app_key, app_secret, tracking_id


def _assinar(params, secret):
    base = "".join(
        f"{chave}{params[chave]}"
        for chave in sorted(params)
        if params[chave] is not None
    )

    return hmac.new(
        secret.encode("utf-8"),
        base.encode("utf-8"),
        hashlib.md5,
    ).hexdigest().upper()


def _coletar_produtos(objeto, saida=None):
    if saida is None:
        saida = []

    if isinstance(objeto, dict):
        titulo = (
            objeto.get("product_title")
            or objeto.get("productTitle")
            or objeto.get("title")
        )
        link = (
            objeto.get("promotion_link")
            or objeto.get("product_detail_url")
            or objeto.get("productDetailUrl")
        )
        preco = (
            objeto.get("target_sale_price")
            or objeto.get("sale_price")
            or objeto.get("app_sale_price")
        )

        if titulo and preco:
            valor = numero_preco(preco)
            if valor is not None:
                saida.append(
                    {
                        "loja": "AliExpress",
                        "produto_nome": titulo,
                        "preco": valor,
                        "frete": 0.0,
                        "link": link or "",
                        "disponivel": True,
                        "origem": "api",
                        "vendedor": objeto.get("shop_name"),
                        "identificador_externo": objeto.get("product_id"),
                    }
                )

        for valor in objeto.values():
            _coletar_produtos(valor, saida)

    elif isinstance(objeto, list):
        for item in objeto:
            _coletar_produtos(item, saida)

    return saida


def buscar_aliexpress(termo, alvo=None, limite=10):
    app_key, secret, tracking_id = _config()

    params = {
        "method": "aliexpress.affiliate.product.query",
        "app_key": app_key,
        "format": "json",
        "sign_method": "hmac",
        "timestamp": datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"),
        "v": "2.0",
        "keywords": termo,
        "page_no": "1",
        "page_size": str(min(int(limite), 50)),
        "sort": "SALE_PRICE_ASC",
        "target_currency": "BRL",
        "target_language": "PT",
        "ship_to_country": "BR",
    }

    if tracking_id:
        params["tracking_id"] = tracking_id

    params["sign"] = _assinar(params, secret)

    resposta = requests.post(
        API,
        data=params,
        timeout=30,
    )
    resposta.raise_for_status()

    resultados = _coletar_produtos(resposta.json())
    resultados.sort(key=lambda oferta: oferta["preco"])

    return resultados[:limite]


def preco_aliexpress_url(link):
    raise RuntimeError(
        "Atualização por URL do AliExpress ainda depende da API de detalhe; "
        "use a busca automática para renovar as ofertas."
    )
