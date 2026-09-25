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
    url = pegar_config("SUPABASE_URL")
    chave = pegar_config("SUPABASE_SECRET_KEY")
    return create_client(url, chave)


def listar_pecas():
    supabase = conectar()

    resposta = (
        supabase
        .table("pecas")
        .select("*")
        .order("id")
        .execute()
    )

    return resposta.data


def adicionar_peca(tipo, nome, loja, link, preco):
    supabase = conectar()
    agora = datetime.now(timezone.utc).isoformat()

    resposta = (
        supabase
        .table("pecas")
        .insert(
            {
                "tipo": tipo,
                "nome": nome,
                "loja": loja,
                "link": link,
                "preco": float(preco),
                "atualizado_em": agora,
            }
        )
        .execute()
    )

    if resposta.data:
        peca_id = resposta.data[0]["id"]

        (
            supabase
            .table("historico")
            .insert(
                {
                    "peca_id": peca_id,
                    "preco": float(preco),
                    "data": agora,
                }
            )
            .execute()
        )


def excluir_peca(peca_id):
    supabase = conectar()

    (
        supabase
        .table("pecas")
        .delete()
        .eq("id", peca_id)
        .execute()
    )


def atualizar_preco(peca_id, novo_preco):
    supabase = conectar()
    agora = datetime.now(timezone.utc).isoformat()

    resposta_atual = (
        supabase
        .table("pecas")
        .select("preco")
        .eq("id", peca_id)
        .limit(1)
        .execute()
    )

    preco_antigo = None

    if resposta_atual.data:
        preco_antigo = float(resposta_atual.data[0]["preco"])

    novo_preco = float(novo_preco)

    (
        supabase
        .table("pecas")
        .update(
            {
                "preco": novo_preco,
                "atualizado_em": agora,
            }
        )
        .eq("id", peca_id)
        .execute()
    )

    if preco_antigo is None or abs(preco_antigo - novo_preco) >= 0.01:
        (
            supabase
            .table("historico")
            .insert(
                {
                    "peca_id": peca_id,
                    "preco": novo_preco,
                    "data": agora,
                }
            )
            .execute()
        )
        return True

    return False


def pegar_historico(peca_id):
    supabase = conectar()

    resposta = (
        supabase
        .table("historico")
        .select("*")
        .eq("peca_id", peca_id)
        .order("data")
        .execute()
    )

    return resposta.data


def criar_montagem(nome, faixa, descricao=""):
    supabase = conectar()

    (
        supabase
        .table("montagens")
        .insert(
            {
                "nome": nome,
                "faixa": faixa,
                "descricao": descricao,
            }
        )
        .execute()
    )


def listar_montagens():
    supabase = conectar()

    resposta = (
        supabase
        .table("montagens")
        .select("*")
        .order("id")
        .execute()
    )

    return resposta.data


def excluir_montagem(montagem_id):
    supabase = conectar()

    (
        supabase
        .table("montagens")
        .delete()
        .eq("id", montagem_id)
        .execute()
    )


def listar_pecas_montagem(montagem_id):
    supabase = conectar()

    resposta = (
        supabase
        .table("montagem_pecas")
        .select(
            "id,quantidade,pecas(id,tipo,nome,loja,link,preco,atualizado_em)"
        )
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
        nova_quantidade = int(item["quantidade"]) + int(quantidade)

        (
            supabase
            .table("montagem_pecas")
            .update({"quantidade": nova_quantidade})
            .eq("id", item["id"])
            .execute()
        )
        return

    (
        supabase
        .table("montagem_pecas")
        .insert(
            {
                "montagem_id": montagem_id,
                "peca_id": peca_id,
                "quantidade": int(quantidade),
            }
        )
        .execute()
    )


def remover_peca_montagem(item_id):
    supabase = conectar()

    (
        supabase
        .table("montagem_pecas")
        .delete()
        .eq("id", item_id)
        .execute()
    )
