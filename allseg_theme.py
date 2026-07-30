"""Tema visual compartilhado do Painel Allseg.

Centraliza o CSS usado nas páginas (esconde a navegação automática do
Streamlit, o header/toolbar/footer nativos e estiliza sidebar e page_links).
Importado por app.py e pelas páginas em pages/.
"""
import streamlit as st

ALLSEG_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Variáveis — tema claro com cards elevados ─────────────────── */
:root {
    --bg-page:       #f0f2f6;
    --bg-card:       #ffffff;
    --bg-card-hover: #f8f9fc;
    --bg-sidebar:    #ffffff;
    --accent:        #1a56db;
    --accent-soft:   #e8effd;
    --accent-hover:  #1648c0;
    --text-primary:  #111827;
    --text-secondary:#6b7280;
    --text-muted:    #9ca3af;
    --border:        #e5e7eb;
    --success:       #059669;
    --warning:       #d97706;
    --danger:        #dc2626;
    --shadow-sm:     0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md:     0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
    --shadow-lg:     0 10px 28px rgba(0,0,0,0.10), 0 4px 8px rgba(0,0,0,0.06);
    --radius:        12px;
    --radius-sm:     8px;
    --font-main:     'Inter', sans-serif;
    --font-mono:     'DM Mono', monospace;
}

html, body, [class*="css"] {
    font-family: var(--font-main) !important;
    color: var(--text-primary) !important;
}

/* ── Fundo da página ──────────────────────────────────────────── */
.stApp {
    background-color: var(--bg-page) !important;
    background-image: none !important;
}

/* ── Layout principal ─────────────────────────────────────────── */
.main .block-container {
    overflow-y: visible !important;
    max-width: 96% !important;
    padding: 1.5rem 2rem 10rem !important;
    background: transparent !important;
}

/* ── Sidebar ──────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.06) !important;
}
[data-testid="stSidebarNav"] { display: none !important; }

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    color: var(--text-muted) !important;
    padding-top: 1.2rem !important;
    margin-bottom: 0.4rem !important;
}

/* ── Títulos globais ──────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-family: var(--font-main) !important;
}
h1 { font-size: 1.5rem !important; font-weight: 700 !important; letter-spacing: -0.025em !important; }

/* st.subheader — recebe estilo de "título de seção de card" */
[data-testid="stHeading"] h2 {
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    margin-top: 0.5rem !important;
    margin-bottom: 0.25rem !important;
    padding-bottom: 0.6rem !important;
    border-bottom: 2px solid var(--accent-soft) !important;
}

/* ── Card wrapper — aplicado em cada bloco principal ─────────── */
/* KPI row e cada linha de conteúdo ganham aparência de card via
   column containers e element containers  */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"],
[data-testid="column"] {
    background: transparent !important;
}

/* KPI Métricas ─ card individual */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1.1rem 1.4rem !important;
    box-shadow: var(--shadow-md) !important;
    transition: box-shadow 0.2s, transform 0.15s !important;
}
[data-testid="stMetric"]:hover {
    box-shadow: var(--shadow-lg) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: var(--text-secondary) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.3rem !important;
    font-weight: 400 !important;
    color: var(--text-primary) !important;
    font-family: var(--font-main) !important;
    letter-spacing: -0.01em !important;
    word-break: break-word !important;
    white-space: normal !important;
    line-height: 1.25 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

/* ── DataFrames — card com sombra ─────────────────────────────── */
[data-testid="stDataFrame"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow-md) !important;
    overflow: visible !important;
    padding: 0 !important;
}

/* ── Gráficos Plotly — card com sombra ───────────────────────── */
[data-testid="stPlotlyChart"] > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow-md) !important;
    padding: 0.75rem !important;
    overflow: visible !important;
}

/* ── st.text — label de seção estilizado ─────────────────────── */
[data-testid="stText"] {
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: var(--text-primary) !important;
    margin-bottom: 0.4rem !important;
}

/* ── Controles da sidebar ─────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background: #f9fafb !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
}
[data-testid="stSelectbox"] > div > div:focus-within,
[data-testid="stMultiSelect"] > div > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-soft) !important;
}

/* ── File Uploader ────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 1.5px dashed #cbd5e1 !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── Botões ───────────────────────────────────────────────────── */
.stButton > button {
    background: var(--bg-card) !important;
    color: var(--accent) !important;
    border: 1.5px solid var(--accent) !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    padding: 0.4rem 1.1rem !important;
    transition: all 0.15s !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button:hover {
    background: var(--accent) !important;
    color: #fff !important;
    box-shadow: 0 4px 14px rgba(26,86,219,0.35) !important;
}

/* ── Alerts ───────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: var(--radius) !important;
    border-left: 4px solid var(--accent) !important;
    background: #f0f5ff !important;
    box-shadow: var(--shadow-sm) !important;
    font-size: 0.84rem !important;
}

/* ── Tabs ─────────────────────────────────────────────────────── */
[data-testid="stTabs"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
    box-shadow: var(--shadow-md) !important;
    padding: 0 1rem !important;
}
[data-testid="stTabs"] [role="tablist"] {
    gap: 0.1rem;
    border-bottom: 1px solid var(--border) !important;
    padding-top: 0.5rem;
}
[data-testid="stTabs"] [role="tab"] {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    padding: 0.5rem 1.1rem !important;
    border: none !important;
    background: transparent !important;
    transition: color 0.15s !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: var(--accent-soft) !important;
}
[data-testid="stTabs"] [role="tabpanel"] {
    padding: 1rem 0.25rem 0.75rem !important;
}

/* ── Divider ──────────────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 2rem 0 !important;
}

/* ── Caption ──────────────────────────────────────────────────── */
[data-testid="stCaption"] {
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
}

/* ── Scrollbar ────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-page); }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* ── Botão "voltar ao topo" ───────────────────────────────────── */
a.btn-topo, a.btn-topo:link, a.btn-topo:visited {
    position: fixed; bottom: 4.5rem; right: 1.5rem; z-index: 9999;
    background: var(--bg-card);
    color: var(--accent) !important;
    border: 1.5px solid var(--accent);
    border-radius: 50%; width: 42px; height: 42px;
    font-size: 20px; cursor: pointer; text-align: center;
    line-height: 40px; text-decoration: none !important;
    box-shadow: var(--shadow-md);
    transition: all 0.2s;
}
a.btn-topo:hover {
    background: var(--accent) !important;
    color: white !important;
    box-shadow: 0 6px 20px rgba(26,86,219,0.35) !important;
}

/* ── Slider ───────────────────────────────────────────────────── */
[data-testid="stSlider"] [role="slider"] {
    background: var(--accent) !important;
    box-shadow: 0 2px 6px rgba(26,86,219,0.4) !important;
}

/* ── Info box de upload ───────────────────────────────────────── */
[data-testid="stInfo"] {
    background: #eff6ff !important;
    border-left: 4px solid var(--accent) !important;
    border-radius: var(--radius) !important;
}

/* ── Info Cards (Segurado, Corretor etc) — idêntico ao st.metric ─ */
.info-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.4rem;
    box-shadow: var(--shadow-md);
    transition: box-shadow 0.2s, transform 0.15s;
    height: 100%;
}
.info-card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}
.info-card-label {
    margin: 0 0 0.4rem 0;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-secondary);
    font-family: var(--font-main);
}
.info-card-value {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    font-family: var(--font-main);
    line-height: 1.35;
    word-break: break-word;
}

/* ── Labels de seção (st.text acima de df/gráfico) ─────────────── */
/* Unifica st.text, st.subheader quando usado como label de bloco   */
[data-testid="stText"] p,
[data-testid="stText"] {
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: var(--text-primary) !important;
    font-family: var(--font-main) !important;
    margin-bottom: 0.4rem !important;
}


/* Cards de texto (Segurado, Corretor…) — valor em fonte de texto, menor */
.text-metric-row [data-testid="stMetricValue"] {
    font-size: 1rem !important;
    font-weight: 400 !important;
    font-family: var(--font-main) !important;
    letter-spacing: 0 !important;
    white-space: normal !important;
    line-height: 1.3 !important;
}

/* ── Label de seção (df e gráficos) — igual ao stMetricLabel ──── */
.section-label {
    margin: 0 0 0.5rem 0 !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: var(--text-primary) !important;
    font-family: var(--font-main) !important;
    line-height: 1 !important;
}

/* ── Oculta header e footer fixos do Streamlit ───────────────── */
/* Esconde botão de colapsar sidebar — sidebar sempre visível */
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
footer { display: none !important; }
</style>
"""


def aplicar_tema():
    """Injeta o CSS padrão do painel na página atual."""
    st.markdown(ALLSEG_CSS, unsafe_allow_html=True)
