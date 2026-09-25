from lojas import (
    buscar_aliexpress,
    buscar_amazon,
    buscar_kabum,
    buscar_mercado_livre,
    buscar_pichau,
    buscar_shopee,
    buscar_terabyte,
)
from lojas.comum import pontuar_correspondencia


PROVEDORES = {
    "KaBuM": buscar_kabum,
    "Pichau": buscar_pichau,
    "Terabyte": buscar_terabyte,
    "Mercado Livre": buscar_mercado_livre,
    "Amazon": buscar_amazon,
    "AliExpress": buscar_aliexpress,
    "Shopee": buscar_shopee,
}


def termo_da_peca(peca):
    for campo in ("mpn", "modelo", "nome"):
        valor = str(peca.get(campo) or "").strip()
        if valor:
            return valor
    return ""


def buscar_ofertas(peca, lojas=None, limite_por_loja=8, confianca_minima=0.35):
    termo = termo_da_peca(peca)

    if not termo:
        raise ValueError("A peça precisa ter nome, modelo ou MPN.")

    lojas = lojas or list(PROVEDORES)
    ofertas = []
    erros = {}

    for loja in lojas:
        provedor = PROVEDORES.get(loja)
        if provedor is None:
            continue

        try:
            resultados = provedor(
                termo,
                alvo=peca,
                limite=limite_por_loja,
            )
        except Exception as erro:
            erros[loja] = str(erro)
            continue

        for oferta in resultados or []:
            titulo = oferta.get("produto_nome") or ""
            confianca = pontuar_correspondencia(peca, titulo)

            if confianca < confianca_minima:
                continue

            preco = float(oferta.get("preco") or 0)
            frete = float(oferta.get("frete") or 0)

            if preco <= 0:
                continue

            oferta["correspondencia"] = confianca
            oferta["preco_final"] = preco + frete
            ofertas.append(oferta)

    unicas = {}
    for oferta in ofertas:
        chave = oferta.get("link") or (
            oferta.get("loja"),
            oferta.get("produto_nome"),
            oferta.get("preco"),
        )
        atual = unicas.get(chave)

        if atual is None or oferta["preco_final"] < atual["preco_final"]:
            unicas[chave] = oferta

    ofertas = list(unicas.values())
    ofertas.sort(
        key=lambda o: (
            -float(o.get("correspondencia") or 0),
            float(o.get("preco_final") or 999999999),
        )
    )

    return ofertas, erros
