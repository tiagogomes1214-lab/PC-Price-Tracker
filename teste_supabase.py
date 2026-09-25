import streamlit as st
from supabase import create_client


url = st.secrets["SUPABASE_URL"]
chave = st.secrets["SUPABASE_SECRET_KEY"]

supabase = create_client(url, chave)

print("Conexão funcionando!")

supabase.table("pecas").insert({
    "tipo": "Placa de video",
    "nome": "RX 7600",
    "loja": "Pichau",
    "link": "https://exemplo.com",
    "preco": 1699.90
}).execute()

print("Peça cadastrada!")