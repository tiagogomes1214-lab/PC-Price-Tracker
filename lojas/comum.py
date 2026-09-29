import json
import re
import unicodedata
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36"
    )
}


def normalizar_texto(texto):
    texto = unicodedata.normalize("NFKD", str(texto or ""))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-zA-Z0-9]+", " ", texto.lower())
    return " ".join(texto.split())


def numero_preco(valor):
    if valor is None:
        return None

    texto = str(valor).strip()
    texto = texto.replace("R$", "").replace("\xa0", " ").replace(" ", "")
    texto = re.sub(r"[^0-9,.]", "", texto)

    if not texto:
        return None

    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        partes = texto.split(",")
        if len(partes[-1]) == 2:
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif texto.count(".") > 1:
        partes = texto.split(".")
        texto = "".join(partes[:-1]) + "." + partes[-1]

    try:
        return float(texto)
    except ValueError:
        return None


def extrair_precos_texto(texto):
    candidatos = re.findall(
        r"R\$\s*([0-9][0-9.,]*[.,][0-9]{2})",
        str(texto or ""),
        flags=re.IGNORECASE,
    )

    valores = []

    for candidato in candidatos:
        preco = numero_preco(candidato)
        if preco is not None and preco > 0:
            valores.append(preco)

    return valores


def preco_perto_de_palavra(texto, palavra="pix"):
    texto = str(texto or "")
    posicoes = [m.start() for m in re.finditer(palavra, texto, re.IGNORECASE)]

    if not posicoes:
        return None

    matches = list(
        re.finditer(
            r"R\$\s*([0-9][0-9.,]*[.,][0-9]{2})",
            texto,
            re.IGNORECASE,
        )
    )

    if not matches:
        return None

    melhor = min(
        matches,
        key=lambda m: min(abs(m.start() - p) for p in posicoes),
    )

    return numero_preco(melhor.group(1))


def buscar_html(url, timeout=20):
    resposta = requests.get(url, headers=HEADERS, timeout=timeout)
    resposta.raise_for_status()
    return resposta.text


def _preco_json(objeto):
    if isinstance(objeto, dict):
        ofertas = objeto.get("offers")
        if ofertas is not None:
            valor = _preco_json(ofertas)
            if valor is not None:
                return valor

        for chave in (
            "price",
            "lowPrice",
            "sale_price",
            "salePrice",
            "priceAmount",
            "amount",
        ):
            if chave in objeto:
                valor = numero_preco(objeto[chave])
                if valor is not None and valor > 0:
                    return valor

        for valor_obj in objeto.values():
            valor = _preco_json(valor_obj)
            if valor is not None:
                return valor

    elif isinstance(objeto, list):
        for item in objeto:
            valor = _preco_json(item)
            if valor is not None:
                return valor

    return None


def preco_generico_url(url):
    html = buscar_html(url)
    soup = BeautifulSoup(html, "html.parser")

    seletores = [
        'meta[property="product:price:amount"]',
        'meta[property="og:price:amount"]',
        'meta[itemprop="price"]',
        '[itemprop="price"]',
    ]

    for seletor in seletores:
        elemento = soup.select_one(seletor)
        if not elemento:
            continue

        valor = elemento.get("content") or elemento.get_text(" ", strip=True)
        preco = numero_preco(valor)

        if preco is not None and preco > 0:
            return preco

    for script in soup.find_all("script", type="application/ld+json"):
        conteudo = script.string or script.get_text(strip=True)
        if not conteudo:
            continue

        try:
            dados = json.loads(conteudo)
        except Exception:
            continue

        preco = _preco_json(dados)
        if preco is not None:
            return preco

    texto = soup.get_text(" ", strip=True)
    preco_pix = preco_perto_de_palavra(texto, "pix")

    if preco_pix is not None:
        return preco_pix

    precos = extrair_precos_texto(texto)
    if precos:
        return min(precos)

    raise ValueError("A página não expôs um preço confiável.")


def pontuar_correspondencia(alvo, titulo):
    alvo = alvo or {}
    titulo_n = normalizar_texto(titulo)

    mpn = normalizar_texto(alvo.get("mpn"))
    modelo = normalizar_texto(alvo.get("modelo"))
    nome = normalizar_texto(alvo.get("nome"))

    if mpn and mpn in titulo_n:
        return 1.0

    if modelo and modelo in titulo_n:
        return 0.95

    tokens = [
        t
        for t in (mpn + " " + modelo + " " + nome).split()
        if len(t) >= 3
    ]

    if not tokens:
        return 0.0

    unicos = list(dict.fromkeys(tokens))
    acertos = sum(1 for token in unicos if token in titulo_n)
    return round(acertos / len(unicos), 3)


def ofertas_de_cards(html, base_url, loja, limite=15):
    soup = BeautifulSoup(html, "html.parser")
    resultados = []
    vistos = set()

    for link in soup.find_all("a", href=True):
        href = link.get("href")
        url = urljoin(base_url, href)

        if url in vistos:
            continue

        titulo = link.get_text(" ", strip=True)
        if len(titulo) < 12:
            continue

        pai = link
        for _ in range(4):
            if pai.parent is None:
                break
            pai = pai.parent

        texto = pai.get_text(" ", strip=True)
        preco = preco_perto_de_palavra(texto, "pix")

        if preco is None:
            precos = extrair_precos_texto(texto)
            if precos:
                preco = min(precos)

        if preco is None:
            continue

        vistos.add(url)
        resultados.append(
            {
                "loja": loja,
                "produto_nome": titulo[:300],
                "preco": float(preco),
                "frete": 0.0,
                "link": url,
                "disponivel": True,
                "origem": "busca_site",
                "vendedor": None,
            }
        )

        if len(resultados) >= limite:
            break

    return resultados
