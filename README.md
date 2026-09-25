# PC Price Tracker

Aplicação em Python + Streamlit para cadastrar componentes, acompanhar preços e montar vários PCs com total atualizado.

## Recursos

- Cadastro de peças com loja, link e preço atual.
- Atualização manual de preços.
- Atualização automática preparada para GitHub Actions.
- Histórico de preços com gráfico.
- Comparador de várias lojas por peça, incluindo preço, frete e total.
- Seleção da menor oferta para alimentar as montagens.
- Montagens de PC com quantidades e total.
- Montagens ordenadas do menor para o maior valor.
- Banco de dados Supabase.
- Interface responsiva para PC e celular.

## Lojas

- **KaBuM:** atualização automática por link implementada.
- **Outras lojas com metadados/JSON-LD de preço:** o leitor genérico tenta atualizar.
- **Shopee:** o link pode ser salvo, mas a atualização automática confiável depende de integração específica/API.
- **AliExpress:** o link pode ser salvo, mas a atualização automática confiável depende de integração específica/API.

## Banco de dados

O projeto usa as tabelas já existentes:

- `pecas`
- `historico`

Para habilitar montagens, execute no SQL Editor do Supabase:

`migrations/002_montagens.sql`

Para habilitar o comparador de ofertas, execute também:

`migrations/003_ofertas.sql`

## Secrets do Streamlit

No Streamlit Community Cloud:

```toml
SUPABASE_URL = "https://SEU-PROJETO.supabase.co"
SUPABASE_SECRET_KEY = "sb_secret_..."
```

Nunca publique a secret key no repositório.

## Atualização automática

O arquivo:

`.github/workflows/atualizar_precos.yml`

está configurado para rodar uma vez por hora.

No GitHub, adicione estes Actions Secrets:

- `SUPABASE_URL`
- `SUPABASE_SECRET_KEY`

Depois disso o workflow consegue executar `atualizar_precos.py` mesmo com o computador desligado.

## Rodar localmente

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
