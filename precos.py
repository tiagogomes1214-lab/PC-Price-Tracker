from urllib.parse import urlparse

from lojas.amazon import preco_amazon_url
from lojas.aliexpress import preco_aliexpress_url
from lojas.comum import preco_generico_url
from lojas.kabum import preco_kabum_url
from lojas.mercado_livre import preco_mercado_livre_url
from lojas.pichau import preco_pichau_url
from lojas.shopee import preco_shopee_url
from lojas.terabyte import preco_terabyte_url


def buscar_preco(link):
    host = urlparse(link).netloc.lower()

    if "kabum.com.br" in host:
        return preco_kabum_url(link)

    if "pichau.com.br" in host:
        return preco_pichau_url(link)

    if "terabyteshop.com.br" in host:
        return preco_terabyte_url(link)

    if "mercadolivre.com" in host or "mercadolibre.com" in host:
        return preco_mercado_livre_url(link)

    if "amazon.com.br" in host:
        return preco_amazon_url(link)

    if "aliexpress." in host:
        return preco_aliexpress_url(link)

    if "shopee.com.br" in host:
        return preco_shopee_url(link)

    return preco_generico_url(link)
