-- PC Price Tracker v2
-- Execute este arquivo no SQL Editor do Supabase uma única vez.

CREATE TABLE IF NOT EXISTS montagens (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome TEXT NOT NULL,
    faixa TEXT NOT NULL DEFAULT 'Personalizado',
    descricao TEXT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS montagem_pecas (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    montagem_id BIGINT NOT NULL REFERENCES montagens(id) ON DELETE CASCADE,
    peca_id BIGINT NOT NULL REFERENCES pecas(id) ON DELETE CASCADE,
    quantidade INTEGER NOT NULL DEFAULT 1 CHECK (quantidade > 0),
    UNIQUE (montagem_id, peca_id)
);

CREATE INDEX IF NOT EXISTS idx_montagem_pecas_montagem
ON montagem_pecas(montagem_id);

CREATE INDEX IF NOT EXISTS idx_montagem_pecas_peca
ON montagem_pecas(peca_id);

ALTER TABLE montagens ENABLE ROW LEVEL SECURITY;
ALTER TABLE montagem_pecas ENABLE ROW LEVEL SECURITY;
