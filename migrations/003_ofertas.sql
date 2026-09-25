-- PC Price Tracker v2 - ofertas por loja
-- Execute no SQL Editor do Supabase uma única vez.

CREATE TABLE IF NOT EXISTS ofertas (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    peca_id BIGINT NOT NULL REFERENCES pecas(id) ON DELETE CASCADE,
    loja TEXT NOT NULL,
    link TEXT NOT NULL,
    preco NUMERIC(12,2) NOT NULL,
    frete NUMERIC(12,2) NOT NULL DEFAULT 0,
    preco_final NUMERIC(12,2) NOT NULL,
    disponivel BOOLEAN NOT NULL DEFAULT TRUE,
    origem TEXT NOT NULL DEFAULT 'manual',
    vendedor TEXT,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (peca_id, link)
);

CREATE INDEX IF NOT EXISTS idx_ofertas_peca
ON ofertas(peca_id);

CREATE INDEX IF NOT EXISTS idx_ofertas_preco_final
ON ofertas(peca_id, preco_final);

ALTER TABLE ofertas ENABLE ROW LEVEL SECURITY;
