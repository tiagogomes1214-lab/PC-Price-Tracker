import html

import streamlit as st


def aplicar_estilo():
    st.markdown(
        """
        <style>
        :root {
            --bg: #080d16;
            --panel: rgba(16, 24, 39, .82);
            --panel-2: rgba(24, 34, 52, .72);
            --border: rgba(148, 163, 184, .16);
            --text: #f8fafc;
            --muted: #94a3b8;
            --accent: #38bdf8;
            --accent-2: #818cf8;
            --success: #34d399;
            --warning: #fbbf24;
            --danger: #fb7185;
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 0%, rgba(56, 189, 248, .10), transparent 28rem),
                radial-gradient(circle at 92% 10%, rgba(129, 140, 248, .10), transparent 30rem),
                linear-gradient(180deg, #080d16 0%, #0b111c 45%, #080d16 100%);
        }

        .block-container {
            max-width: 1440px;
            padding-top: 1.6rem;
            padding-bottom: 5rem;
        }

        #MainMenu, footer {
            visibility: hidden;
        }

        header[data-testid="stHeader"] {
            background: rgba(8, 13, 22, .72);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(148, 163, 184, .08);
        }

        .pc-hero {
            position: relative;
            overflow: hidden;
            padding: 2rem 2.2rem;
            margin: .4rem 0 1.4rem;
            border: 1px solid var(--border);
            border-radius: 24px;
            background:
                linear-gradient(135deg, rgba(56, 189, 248, .12), rgba(129, 140, 248, .07) 52%, rgba(16, 24, 39, .76)),
                rgba(15, 23, 42, .78);
            box-shadow: 0 24px 80px rgba(0, 0, 0, .22);
        }

        .pc-hero:after {
            content: "";
            position: absolute;
            width: 240px;
            height: 240px;
            right: -80px;
            top: -110px;
            border-radius: 999px;
            background: rgba(56, 189, 248, .13);
            filter: blur(4px);
        }

        .pc-kicker {
            display: inline-flex;
            align-items: center;
            gap: .45rem;
            padding: .35rem .7rem;
            margin-bottom: .8rem;
            border: 1px solid rgba(56, 189, 248, .2);
            border-radius: 999px;
            color: #7dd3fc;
            background: rgba(14, 165, 233, .08);
            font-size: .78rem;
            font-weight: 700;
            letter-spacing: .08em;
            text-transform: uppercase;
        }

        .pc-hero h1 {
            margin: 0;
            color: var(--text);
            font-size: clamp(2rem, 4vw, 3.4rem);
            letter-spacing: -.045em;
            line-height: 1.03;
        }

        .pc-hero p {
            max-width: 760px;
            margin: .8rem 0 0;
            color: #a8b4c6;
            font-size: 1.03rem;
            line-height: 1.65;
        }

        .pc-section {
            margin: 1.1rem 0 .8rem;
        }

        .pc-section h2 {
            margin: 0;
            font-size: 1.4rem;
            letter-spacing: -.02em;
        }

        .pc-section p {
            margin: .25rem 0 0;
            color: var(--muted);
        }

        .pc-kpi {
            min-height: 132px;
            padding: 1.15rem 1.25rem;
            border: 1px solid var(--border);
            border-radius: 18px;
            background: linear-gradient(145deg, rgba(22, 31, 48, .90), rgba(12, 19, 31, .88));
            box-shadow: 0 12px 34px rgba(0,0,0,.18);
        }

        .pc-kpi-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: .65rem;
        }

        .pc-kpi-icon {
            font-size: 1.25rem;
        }

        .pc-kpi-label {
            color: var(--muted);
            font-size: .83rem;
            font-weight: 650;
        }

        .pc-kpi-value {
            color: var(--text);
            font-size: 1.72rem;
            font-weight: 800;
            letter-spacing: -.035em;
            line-height: 1.2;
        }

        .pc-kpi-subtitle {
            margin-top: .45rem;
            color: #748399;
            font-size: .78rem;
        }

        div[data-testid="stForm"],
        div[data-testid="stExpander"],
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--border) !important;
            background: rgba(15, 23, 42, .52);
            border-radius: 18px !important;
        }

        div[data-testid="stMetric"] {
            padding: 1rem 1.05rem;
            border: 1px solid var(--border);
            border-radius: 16px;
            background: rgba(15, 23, 42, .62);
        }

        div[data-testid="stMetricLabel"] {
            color: #94a3b8;
        }

        div[data-testid="stMetricValue"] {
            letter-spacing: -.035em;
        }

        div[data-baseweb="tab-list"] {
            gap: .35rem;
            padding: .35rem;
            border: 1px solid rgba(148, 163, 184, .10);
            border-radius: 14px;
            background: rgba(15, 23, 42, .46);
        }

        button[data-baseweb="tab"] {
            height: 42px;
            border-radius: 10px;
            padding-left: .9rem !important;
            padding-right: .9rem !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, rgba(56, 189, 248, .16), rgba(129, 140, 248, .13));
        }

        div.stButton > button,
        div.stLinkButton > a {
            min-height: 42px;
            border-radius: 12px;
            border: 1px solid rgba(148, 163, 184, .16);
            font-weight: 700;
            transition: transform .15s ease, border-color .15s ease, box-shadow .15s ease;
        }

        div.stButton > button:hover,
        div.stLinkButton > a:hover {
            transform: translateY(-1px);
            border-color: rgba(56, 189, 248, .55);
            box-shadow: 0 8px 24px rgba(14, 165, 233, .10);
        }

        div.stButton > button[kind="primary"] {
            border: none;
            background: linear-gradient(135deg, #0ea5e9, #6366f1);
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        textarea {
            border-radius: 11px !important;
        }

        .pc-offer {
            padding: 1rem 1.1rem;
            margin: .45rem 0;
            border: 1px solid var(--border);
            border-radius: 16px;
            background: rgba(15, 23, 42, .60);
        }

        .pc-offer-best {
            border-color: rgba(52, 211, 153, .30);
            background: linear-gradient(135deg, rgba(16, 185, 129, .08), rgba(15, 23, 42, .66));
        }

        .pc-progress {
            width: 100%;
            height: 9px;
            margin-top: .6rem;
            border-radius: 999px;
            overflow: hidden;
            background: rgba(148, 163, 184, .12);
        }

        .pc-progress > div {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #38bdf8, #818cf8);
        }

        .pc-muted {
            color: var(--muted);
        }

        @media (max-width: 768px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .pc-hero {
                padding: 1.5rem 1.25rem;
                border-radius: 18px;
            }

            .pc-kpi {
                min-height: 112px;
            }

            button[data-baseweb="tab"] {
                padding-left: .6rem !important;
                padding-right: .6rem !important;
                font-size: .82rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero():
    st.markdown(
        """
        <div class="pc-hero">
            <div class="pc-kicker">● Monitoramento inteligente de hardware</div>
            <h1>PC Price Tracker</h1>
            <p>
                Compare preços, encontre a melhor oferta e monte seu PC com
                orçamento, histórico e compatibilidade no mesmo lugar.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def titulo_secao(titulo, subtitulo=None):
    subtitulo_html = (
        f"<p>{html.escape(str(subtitulo))}</p>"
        if subtitulo
        else ""
    )

    st.markdown(
        f"""
        <div class="pc-section">
            <h2>{html.escape(str(titulo))}</h2>
            {subtitulo_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi(icone, rotulo, valor, subtitulo=""):
    st.markdown(
        f"""
        <div class="pc-kpi">
            <div class="pc-kpi-top">
                <span class="pc-kpi-label">{html.escape(str(rotulo))}</span>
                <span class="pc-kpi-icon">{html.escape(str(icone))}</span>
            </div>
            <div class="pc-kpi-value">{html.escape(str(valor))}</div>
            <div class="pc-kpi-subtitle">{html.escape(str(subtitulo))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def barra_orcamento(total, orcamento):
    if not orcamento:
        return

    total = float(total or 0)
    orcamento = float(orcamento or 0)

    if orcamento <= 0:
        return

    percentual = max(0, min((total / orcamento) * 100, 100))

    st.markdown(
        f"""
        <div class="pc-progress" title="{percentual:.0f}% do orçamento utilizado">
            <div style="width:{percentual:.2f}%"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
