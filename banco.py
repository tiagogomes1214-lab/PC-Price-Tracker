import os
from datetime import datetime, timezone

from supabase import create_client


def pegar_config(nome):
    valor = os.getenv(nome)

    if valor:
        return valor

    try:
        import streamlit as st
        return st.secrets[nome]
    except Exception as erro:
        raise RuntimeError(
            f"A configuração {nome} não foi encontrada."
        ) from erro


def conectar():
    return create_client(
        pegar_config("SUPABASE_URL"),
        pegar_config("SUPABASE_SECRET_KEY"),
    )


def listar_pecas():
    resposta = (
        conectar()
        .table("pecas")
        .select("*")
        .order("tipo")
        .order("nome")
        .execute()
    )
    return resposta.data


def adicionar_peca(
    tipo,
    nome,
    loja,
    link,
    preco,
    fabricante=None,
    modelo=None,
    mpn=None,
    gtin=None,
    socket=None,
    memoria_tipo=None,
    formato=None,
    potencia_w=None,
    comprimento_mm=None,
    gpu_max_mm=None,
    psu_recomendada_w=None,
    formatos_suportados=None,
    observacoes=None,
):
    supabase = conectar()
    agora = datetime.now(timezone.utc).isoformat()

    dados = {
        "tipo": tipo,
        "nome": nome,
        "loja": loja,
        "link": link,
        "preco": float(preco),
        "atualizado_em": agora,
        "fabricante": fabricante or None,
        "modelo": modelo or None,
        "mpn": mpn or None,
        "gtin": gtin or None,
        "socket": socket or None,
        "memoria_tipo": memoria_tipo or None,
        "formato": formato or None,
        "potencia_w": potencia_w or None,
        "comprimento_mm": comprimento_mm or None,
        "gpu_max_mm": gpu_max_mm or None,
        "psu_recomendada_w": psu_recomendada_w or None,
        "formatos_suportados": formatos_suportados or None,
        "observacoes": observacoes or None,
    }

    resposta = (
        supabase
        .table("pecas")
        .insert(dados)
        .execute()
    )

    if resposta.data:
        peca_id = resposta.data[0]["id"]
        (
            supabase
            .table("historico")
            .insert({
                "peca_id": peca_id,
                "preco": float(preco),
                "data": agora,
            })
            .execute()
        )
        return peca_id

    return None


def editar_peca(peca_id, dados):
    permitidos = {
        "tipo",
        "nome",
        "loja",
        "link",
        "fabricante",
        "modelo",
        "mpn",
        "gtin",
        "socket",
        "memoria_tipo",
        "formato",
        "potencia_w",
        "comprimento_mm",
        "gpu_max_mm",
        "psu_recomendada_w",
        "formatos_suportados",
        "observacoes",
    }

    payload = {
        chave: valor if valor not in ("", None) else None
        for chave, valor in dados.items()
        if chave in permitidos
    }

    if payload:
        (
            conectar()
            .table("pecas")
            .update(payload)
            .eq("id", peca_id)
            .execute()
        )


def excluir_peca(peca_id):
    (
        conectar()
        .table("pecas")
        .delete()
        .eq("id", peca_id)
        .execute()
    )


def atualizar_preco(peca_id, novo_preco):
    supabase = conectar()
    agora = datetime.now(timezone.utc).isoformat()

    atual = (
        supabase
        .table("pecas")
        .select("preco")
        .eq("id", peca_id)
        .limit(1)
        .execute()
    )

    preco_antigo = None
    if atual.data:
        preco_antigo = float(atual.data[0]["preco"])

    novo_preco = float(novo_preco)

    (
        supabase
        .table("pecas")
        .update({
            "preco": novo_preco,
            "atualizado_em": agora,
        })
        .eq("id", peca_id)
        .execute()
    )

    mudou = (
        preco_antigo is None
        or abs(preco_antigo - novo_preco) >= 0.01
    )

    if mudou:
        (
            supabase
            .table("historico")
            .insert({
                "peca_id": peca_id,
                "preco": novo_preco,
                "data": agora,
            })
            .execute()
        )

    return mudou


def pegar_historico(peca_id):
    resposta = (
        conectar()
        .table("historico")
        .select("*")
        .eq("peca_id", peca_id)
        .order("data")
        .execute()
    )
    return resposta.data


def criar_montagem(nome, faixa, descricao="", orcamento=None):
    (
        conectar()
        .table("montagens")
        .insert({
            "nome": nome,
            "faixa": faixa,
            "descricao": descricao,
            "orcamento": float(orcamento) if orcamento else None,
        })
        .execute()
    )


def listar_montagens():
    resposta = (
        conectar()
        .table("montagens")
        .select("*")
        .order("id")
        .execute()
    )
    return resposta.data


def excluir_montagem(montagem_id):
    (
        conectar()
        .table("montagens")
        .delete()
        .eq("id", montagem_id)
        .execute()
    )


def listar_pecas_montagem(montagem_id):
    resposta = (
        conectar()
        .table("montagem_pecas")
        .select("id,quantidade,travada,pecas(*)")
        .eq("montagem_id", montagem_id)
        .order("id")
        .execute()
    )
    return resposta.data


def adicionar_peca_montagem(montagem_id, peca_id, quantidade=1):
    supabase = conectar()

    existente = (
        supabase
        .table("montagem_pecas")
        .select("id,quantidade")
        .eq("montagem_id", montagem_id)
        .eq("peca_id", peca_id)
        .limit(1)
        .execute()
    )

    if existente.data:
        item = existente.data[0]
        (
            supabase
            .table("montagem_pecas")
            .update({
                "quantidade": int(item["quantidade"]) + int(quantidade)
            })
            .eq("id", item["id"])
            .execute()
        )
        return

    (
        supabase
        .table("montagem_pecas")
        .insert({
            "montagem_id": montagem_id,
            "peca_id": peca_id,
            "quantidade": int(quantidade),
        })
        .execute()
    )


def remover_peca_montagem(item_id):
    (
        conectar()
        .table("montagem_pecas")
        .delete()
        .eq("id", item_id)
        .execute()
    )


def listar_ofertas(peca_id):
    resposta = (
        conectar()
        .table("ofertas")
        .select("*")
        .eq("peca_id", peca_id)
        .eq("disponivel", True)
        .order("preco_final")
        .execute()
    )
    return resposta.data


def listar_todas_ofertas():
    resposta = (
        conectar()
        .table("ofertas")
        .select("*")
        .eq("disponivel", True)
        .order("peca_id")
        .execute()
    )
    return resposta.data


def salvar_oferta(
    peca_id,
    loja,
    link,
    preco,
    frete=0,
    origem="manual",
    vendedor=None,
    produto_nome=None,
    identificador_externo=None,
    correspondencia=None,
):
    supabase = conectar()
    agora = datetime.now(timezone.utc).isoformat()

    preco = float(preco)
    frete = float(frete or 0)
    preco_final = preco + frete

    anterior = (
        supabase
        .table("ofertas")
        .select("id,preco,frete,preco_final")
        .eq("peca_id", peca_id)
        .eq("link", link)
        .limit(1)
        .execute()
    )

    dados = {
        "peca_id": peca_id,
        "loja": loja,
        "link": link,
        "preco": preco,
        "frete": frete,
        "preco_final": preco_final,
        "disponivel": True,
        "origem": origem,
        "vendedor": vendedor or None,
        "produto_nome": produto_nome or None,
        "identificador_externo": identificador_externo or None,
        "correspondencia": correspondencia,
        "moeda": "BRL",
        "atualizado_em": agora,
    }

    resposta = (
        supabase
        .table("ofertas")
        .upsert(dados, on_conflict="peca_id,link")
        .execute()
    )

    oferta_id = None
    if resposta.data:
        oferta_id = resposta.data[0]["id"]
    elif anterior.data:
        oferta_id = anterior.data[0]["id"]

    mudou = True
    if anterior.data:
        mudou = abs(
            float(anterior.data[0]["preco_final"]) - preco_final
        ) >= 0.01

    if oferta_id and mudou:
        (
            supabase
            .table("historico_ofertas")
            .insert({
                "oferta_id": oferta_id,
                "preco": preco,
                "frete": frete,
                "preco_final": preco_final,
                "data": agora,
            })
            .execute()
        )

    return oferta_id


def marcar_oferta_indisponivel(oferta_id):
    (
        conectar()
        .table("ofertas")
        .update({"disponivel": False})
        .eq("id", oferta_id)
        .execute()
    )


def excluir_oferta(oferta_id):
    (
        conectar()
        .table("ofertas")
        .delete()
        .eq("id", oferta_id)
        .execute()
    )


def aplicar_melhor_oferta(peca_id):
    ofertas = listar_ofertas(peca_id)

    if not ofertas:
        raise ValueError("Nenhuma oferta disponível para essa peça.")

    melhor = ofertas[0]
    supabase = conectar()
    agora = datetime.now(timezone.utc).isoformat()

    atual = (
        supabase
        .table("pecas")
        .select("preco")
        .eq("id", peca_id)
        .limit(1)
        .execute()
    )

    preco_antigo = None
    if atual.data:
        preco_antigo = float(atual.data[0]["preco"])

    preco_final = float(melhor["preco_final"])

    (
        supabase
        .table("pecas")
        .update({
            "loja": melhor["loja"],
            "link": melhor["link"],
            "preco": preco_final,
            "atualizado_em": agora,
        })
        .eq("id", peca_id)
        .execute()
    )

    if (
        preco_antigo is None
        or abs(preco_antigo - preco_final) >= 0.01
    ):
        (
            supabase
            .table("historico")
            .insert({
                "peca_id": peca_id,
                "preco": preco_final,
                "data": agora,
            })
            .execute()
        )

    return melhor


def criar_alerta(peca_id, preco_alvo):
    (
        conectar()
        .table("alertas")
        .insert({
            "peca_id": peca_id,
            "preco_alvo": float(preco_alvo),
            "ativo": True,
        })
        .execute()
    )


def listar_alertas():
    resposta = (
        conectar()
        .table("alertas")
        .select("id,preco_alvo,ativo,criado_em,pecas(id,nome,tipo,preco,loja,link)")
        .eq("ativo", True)
        .order("id")
        .execute()
    )
    return resposta.data


def excluir_alerta(alerta_id):
    (
        conectar()
        .table("alertas")
        .delete()
        .eq("id", alerta_id)
        .execute()
    )
