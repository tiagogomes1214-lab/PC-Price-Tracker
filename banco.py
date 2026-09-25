import streamlit as st
from supabase import create_client
from datetime import datetime, timezone


def conectar():
    url = st.secrets["SUPABASE_URL"]
    chave = st.secrets["SUPABASE_SECRET_KEY"]

    return create_client(url, chave)


def listar_pecas():
    supabase = conectar()

    resposta = (
        supabase
        .table("pecas")
        .select("*")
        .execute()
    )

    return resposta.data

def adicionar_peca(tipo, nome, loja, link, preco):
    supabase = conectar()

    supabase.table("pecas").insert({
        "tipo": tipo,
        "nome": nome,
        "loja": loja,
        "link": link,
        "preco": preco
    }).execute()

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

    agora = datetime.now(
        timezone.utc
    ).isoformat()

    (
        supabase
        .table("pecas")
        .update({
            "preco": novo_preco,
            "atualizado_em": agora
        })
        .eq("id", peca_id)
        .execute()
    )

    (
        supabase
        .table("historico")
        .insert({
            "peca_id": peca_id,
            "preco": novo_preco,
            "data": agora
        })
        .execute()
    )