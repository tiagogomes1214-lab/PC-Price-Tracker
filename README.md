# PC Price Tracker

Aplicação em Python + Streamlit para montar PCs, comparar lojas, acompanhar preços e manter um histórico.

## O que a versão nova faz

- Cadastro de componentes.
- MPN, modelo e GTIN para reduzir comparação errada.
- Busca de ofertas em várias lojas.
- Comparação por preço e frete cadastrado.
- Melhor oferta pode alimentar automaticamente o preço usado nas montagens.
- Várias montagens de PC.
- Montagens ordenadas do menor para o maior total.
- Orçamento máximo por montagem.
- Verificação básica de compatibilidade.
- Histórico de preços.
- Alertas de preço dentro do app.
- Atualização horária das ofertas salvas.
- Nova busca de ofertas a cada 6 horas.
- Supabase como banco online.
- Streamlit para acesso no PC e celular.

## Lojas

### KaBuM
Busca por site e atualização de links implementadas.

### Pichau
Busca por página pública e leitura de preço implementadas. Como o HTML da loja pode mudar, o app trata falhas sem sobrescrever preço com valor inventado.

### Terabyte
Busca pela página de busca pública e leitura de preço implementadas.

### Mercado Livre
Integração preparada com API oficial.

Secret opcional:

```text
ML_ACCESS_TOKEN
```

### Amazon Brasil
Integração preparada para a Creators API.

Secrets necessários:

```text
AMAZON_CREATORS_TOKEN
AMAZON_PARTNER_TAG
```

### AliExpress
Integração preparada para a API de afiliados/Open Platform.

Secrets necessários:

```text
ALIEXPRESS_APP_KEY
ALIEXPRESS_APP_SECRET
ALIEXPRESS_TRACKING_ID
```

O tracking ID é opcional.

### Shopee
Links podem ser cadastrados e o leitor genérico tenta atualizar páginas que exponham preço. A busca global automática permanece desativada porque o projeto não assume um endpoint público de catálogo que não foi documentado para esse uso.

## Banco de dados

No Supabase, abra o SQL Editor e execute:

```text
migrations/000_setup_completo.sql
```

O arquivo é idempotente e pode ser executado mesmo se as tabelas antigas já existirem.

Ele cria ou atualiza:

- `pecas`
- `historico`
- `montagens`
- `montagem_pecas`
- `ofertas`
- `historico_ofertas`
- `alertas`

## Secrets do Streamlit

Obrigatórios:

```toml
SUPABASE_URL = "https://SEU-PROJETO.supabase.co"
SUPABASE_SECRET_KEY = "sb_secret_..."
```

Os secrets das APIs de lojas são opcionais. Sem eles, somente os provedores que não precisam dessas credenciais serão consultados.

## Secrets do GitHub Actions

Em:

`Settings > Secrets and variables > Actions`

adicione obrigatoriamente:

- `SUPABASE_URL`
- `SUPABASE_SECRET_KEY`

E, se quiser habilitar os provedores oficiais correspondentes:

- `ML_ACCESS_TOKEN`
- `AMAZON_CREATORS_TOKEN`
- `AMAZON_PARTNER_TAG`
- `ALIEXPRESS_APP_KEY`
- `ALIEXPRESS_APP_SECRET`
- `ALIEXPRESS_TRACKING_ID`

## Automação

`.github/workflows/atualizar_precos.yml`

Atualiza ofertas já salvas aproximadamente uma vez por hora.

`.github/workflows/buscar_ofertas.yml`

Tenta descobrir novas ofertas aproximadamente a cada 6 horas.

GitHub Actions pode atrasar tarefas agendadas em períodos de carga; o cron não deve ser tratado como relógio exato.

## Rodar localmente

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Compatibilidade

O app verifica conflitos simples quando os dados estiverem cadastrados:

- socket do processador x placa-mãe;
- DDR da memória x placa-mãe;
- comprimento da GPU x limite do gabinete;
- potência da fonte x recomendação da GPU;
- formato da placa-mãe x formatos informados no gabinete.

A verificação é auxiliar e não substitui a ficha técnica oficial dos fabricantes.
