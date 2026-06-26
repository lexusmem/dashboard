import streamlit as st
import pandas as pd
import io
import base64
import logging
import plotly.graph_objects as go
import plotly.express as px
import streamlit_antd_components as sac
from datetime import datetime

st.set_page_config(layout='wide', page_title='Dados Gerais — Allseg', page_icon='📊')

ALLSEG_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg-page:       #f0f2f6;
    --bg-card:       #ffffff;
    --bg-sidebar:    #ffffff;
    --accent:        #1a56db;
    --accent-soft:   #e8effd;
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

html, body, [class*="css"] { font-family: var(--font-main) !important; color: var(--text-primary) !important; }

.stApp { background-color: var(--bg-page) !important; background-image: none !important; }

.main .block-container {
    overflow-y: visible !important;
    max-width: 96% !important;
    padding: 1.5rem 2rem 10rem !important;
    background: transparent !important;
}

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

h1, h2, h3, h4, h5, h6 { color: var(--text-primary) !important; font-family: var(--font-main) !important; }
h1 { font-size: 1.5rem !important; font-weight: 700 !important; letter-spacing: -0.025em !important; }

[data-testid="stHeading"] h2 {
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    margin-top: 0.5rem !important;
    padding-bottom: 0.6rem !important;
    border-bottom: 2px solid var(--accent-soft) !important;
}

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

[data-testid="stDataFrame"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow-md) !important;
    overflow: visible !important;
    padding: 0 !important;
}

[data-testid="stPlotlyChart"] > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow-md) !important;
    padding: 0.75rem !important;
    overflow: visible !important;
}

[data-testid="stText"] {
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: var(--text-primary) !important;
    margin-bottom: 0.4rem !important;
}

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

[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 1.5px dashed #cbd5e1 !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow-sm) !important;
}

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

[data-testid="stAlert"] {
    border-radius: var(--radius) !important;
    border-left: 4px solid var(--accent) !important;
    background: #f0f5ff !important;
    box-shadow: var(--shadow-sm) !important;
    font-size: 0.84rem !important;
}

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
[data-testid="stTabs"] [role="tabpanel"] { padding: 1rem 0.25rem 0.75rem !important; }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 2rem 0 !important; }
[data-testid="stCaption"] { color: var(--text-muted) !important; font-size: 0.72rem !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-page); }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

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

[data-testid="stSlider"] [role="slider"] {
    background: var(--accent) !important;
    box-shadow: 0 2px 6px rgba(26,86,219,0.4) !important;
}

/* ── Info Cards — idêntico ao st.metric ──────────────────────── */
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
st.markdown(ALLSEG_CSS, unsafe_allow_html=True)


# Mapeamento fuzzy de coberturas — com cache para evitar recálculo
@st.cache_data
def _calcular_mapa_franquia(pares_sin, cob_tuples, threshold=0.75):
    from difflib import SequenceMatcher
    import pandas as pd
    cob_df = pd.DataFrame(list(cob_tuples), columns=['N° Apólice','Cobertura Apólice','Franquia Apólice'])
    mapa = {}
    for apolice, nome_sin in pares_sin:
        cobs_ap = cob_df[cob_df['N° Apólice'] == apolice]
        if cobs_ap.empty:
            mapa[(apolice, nome_sin)] = 0.0
            continue
        scores = [(SequenceMatcher(None, nome_sin.lower(), c.lower()).ratio(), c) for c in cobs_ap['Cobertura Apólice'].tolist()]
        best_score, best_cob = max(scores, key=lambda x: x[0])
        if best_score >= threshold:
            franquia = cobs_ap[cobs_ap['Cobertura Apólice'] == best_cob]['Franquia Apólice'].values
            mapa[(apolice, nome_sin)] = float(franquia[0]) if len(franquia) > 0 else 0.0
        else:
            mapa[(apolice, nome_sin)] = 0.0
    return mapa

def mapear_franquia_por_cobertura(df_sinistro, df_cobertura_filtrado, threshold=0.75):
    if df_cobertura_filtrado.empty or df_sinistro.empty:
        df_sinistro = df_sinistro.copy()
        df_sinistro['Franquia Apólice'] = 0.0
        return df_sinistro
    if 'nr_endosso' in df_cobertura_filtrado.columns:
        cob_vigente = df_cobertura_filtrado.sort_values('nr_endosso', ascending=False)\
            .drop_duplicates(subset=['N° Apólice','Cobertura Apólice'])\
            [['N° Apólice','Cobertura Apólice','Franquia Apólice']].copy()
    else:
        cob_vigente = df_cobertura_filtrado\
            .drop_duplicates(subset=['N° Apólice','Cobertura Apólice'])\
            [['N° Apólice','Cobertura Apólice','Franquia Apólice']].copy()
    pares_sin = tuple(df_sinistro[['N° Apólice','Cobertura']].drop_duplicates().itertuples(index=False, name=None))
    cob_tuples = tuple(cob_vigente.itertuples(index=False, name=None))
    mapa = _calcular_mapa_franquia(pares_sin, cob_tuples, threshold)
    df_sinistro = df_sinistro.copy()
    df_sinistro['Franquia Apólice'] = df_sinistro.apply(
        lambda r: mapa.get((r['N° Apólice'], str(r['Cobertura'])), 0.0), axis=1
    )
    return df_sinistro



@st.cache_data
def _filtrar_sinistros_por_apolices(df_sin_tuple, apolices_tuple):
    """Filtra sinistros pelas apólices — cacheado para não refiltrar a cada rerun."""
    import pandas as pd
    df = pd.DataFrame(list(df_sin_tuple[1]), columns=df_sin_tuple[0])
    apolices = set(apolices_tuple)
    return df[df['N° Apólice'].isin(apolices)].copy()

@st.cache_data
def _calcular_periodo_max_aviso(dt_aviso_series_tuple, dt_ocorrencia_series_tuple):
    """Calcula o período máximo da base — executa uma única vez."""
    import pandas as pd
    dt_av  = pd.to_datetime(pd.Series(list(dt_aviso_series_tuple)),     dayfirst=True, errors='coerce')
    dt_oc  = pd.to_datetime(pd.Series(list(dt_ocorrencia_series_tuple)),dayfirst=True, errors='coerce')
    return int((dt_av.dropna().max() - dt_oc.dropna().min()).days)

@st.cache_data
def _calcular_media_dias_aviso(apolices_tuple, dt_aviso_tuple, dt_ocorrencia_tuple, periodo_max):
    """Calcula média de dias para aviso — cacheado por conjunto de apólices."""
    import pandas as pd
    import numpy as np
    dt_av = pd.to_datetime(pd.Series(list(dt_aviso_tuple)),     dayfirst=True, errors='coerce')
    dt_oc = pd.to_datetime(pd.Series(list(dt_ocorrencia_tuple)),dayfirst=True, errors='coerce')
    dias  = (dt_av - dt_oc).dt.days
    dias_validos = dias[(dias >= 0) & (dias <= periodo_max)]
    media = dias_validos.mean()
    return f"{media:.0f} dias" if not pd.isna(media) else "—"

# Função de Formatação de Valores para o padrão Brasileiro
def formatar_valor_br(valor):
    if pd.isna(valor):
        return ""
    valor_us_format = f"{valor:,.2f}"
    return valor_us_format.replace(",", "X").replace(".", ",").replace("X", ".")

# Recupera os dados do session_state (carregados na página principal)
if 'dados_calculados' not in st.session_state or st.session_state['dados_calculados'].empty:
    st.warning("⚠️ Os dados ainda não foram carregados. Volte à página principal e faça o upload dos arquivos.")
    st.stop()

dados_calculados = st.session_state['dados_calculados']
df_sinistros     = st.session_state['df_sinistros']
df_cobertura     = st.session_state.get('df_cobertura', pd.DataFrame())

# ─────────────────────────────────────────────────────────────────────────────
# 📸 SNAPSHOT DIÁRIO DA BASE DE SINISTROS — fluxo manual download/upload
# Como o app roda no Streamlit Community Cloud (filesystem efêmero), snapshots
# não podem ser persistidos em disco. Em vez disso:
#   • Botão de DOWNLOAD gera o snapshot do dia em memória (Parquet) para o
#     usuário salvar manualmente no Google Drive/OneDrive.
#   • UPLOAD permite carregar snapshots antigos para comparação histórica.
# ─────────────────────────────────────────────────────────────────────────────
_HOJE_STR = pd.Timestamp.today().strftime("%Y-%m-%d")

def _coage_categoria_str(_df, _cols):
    """Garante que colunas categóricas (Ramo, Utilização) tenham tipo string consistente.
    Resolve mistura de tipos (int + str) que quebra a serialização Parquet com PyArrow.
    Valores nulos viram a string '(não informado)' para preservar a linha no groupby."""
    for _c in _cols:
        if _c in _df.columns:
            _df[_c] = _df[_c].fillna('(não informado)').astype(str)
    return _df

def _gerar_snapshot_bytes(_df_sin, _dados_calc=None):
    """Gera bytes Parquet do snapshot consolidado (hoje + histórico em sessão).

    Schema v2 — duas "tabelas lógicas" empilhadas em um único Parquet,
    distinguidas pela coluna tipo_registro:
      • tipo_registro = 'SINISTRO'    → uma linha por nr_sinistro, com valores
        financeiros e Ramo/Utilização (enriquecidos via merge com dados_calc).
      • tipo_registro = 'AGG_CARTEIRA' → uma linha por (Ramo × Utilização),
        com qtd_apolices_vigentes e soma_premio (carteira inteira, sem slider).

    Retrocompatibilidade: snapshots antigos sem tipo_registro são tratados como
    SINISTRO ao serem carregados (e enriquecidos com Ramo/Utilização on the fly
    via merge com dados_calc do dia atual).
    """
    import io as _io

    # ── Snapshot de hoje — SINISTROS ────────────────────────────────────────
    _cols_snap = [c for c in [
        'nr_sinistro', 'N° Apólice', 'cd_apolice', 'nr_ramo',
        'dt_aviso', 'dt_ocorrencia',
        'vl_sinistro_pago', 'vl_sinistro_pendente', 'vl_sinistro_total',
        'vl_despesa_pago', 'vl_despesa_pendente', 'vl_despesa_total',
        'vl_honorario_total', 'vl_salvado_total',
        'Total Sinistro',
        'status_processo', 'status_movimento'
    ] if c in _df_sin.columns]
    _df_hoje_sin = _df_sin[_cols_snap].copy()

    # Enriquece com Ramo/Utilização via merge em dados_calc (essas colunas não
    # existem em df_sinistros — vêm das tabelas de apólice/cobertura)
    if _dados_calc is not None and 'N° Apólice' in _dados_calc.columns:
        _mapa_apo = _dados_calc[['N° Apólice', 'Ramo', 'Utilização']].drop_duplicates('N° Apólice').copy()
        _mapa_apo['N° Apólice'] = _mapa_apo['N° Apólice'].astype(str)
        # Coage Ramo/Utilização para string consistente antes do merge
        _mapa_apo = _coage_categoria_str(_mapa_apo, ['Ramo', 'Utilização'])
        if 'N° Apólice' in _df_hoje_sin.columns:
            _df_hoje_sin['N° Apólice'] = _df_hoje_sin['N° Apólice'].astype(str)
            _df_hoje_sin = _df_hoje_sin.merge(_mapa_apo, on='N° Apólice', how='left')
        # Após merge: linhas sem match têm NaN em Ramo/Utilização → coage de novo
        _df_hoje_sin = _coage_categoria_str(_df_hoje_sin, ['Ramo', 'Utilização'])

    _df_hoje_sin['tipo_registro'] = 'SINISTRO'
    _df_hoje_sin['data_snapshot'] = pd.Timestamp(_HOJE_STR)

    # ── Snapshot de hoje — AGG_CARTEIRA ─────────────────────────────────────
    _df_hoje_agg = pd.DataFrame()
    if _dados_calc is not None and not _dados_calc.empty:
        # Garante numérico no prêmio e string em Ramo/Utilização
        _dc = _dados_calc.copy()
        _dc = _coage_categoria_str(_dc, ['Ramo', 'Utilização'])
        _dc['_premio_num'] = pd.to_numeric(
            _dc['Soma Prêmio Pago por Apolice'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False),
            errors='coerce'
        ).fillna(0)
        _df_hoje_agg = _dc.groupby(['Ramo', 'Utilização'], dropna=False).agg(
            qtd_apolices_vigentes=('N° Apólice', 'nunique'),
            soma_premio=('_premio_num', 'sum'),
        ).reset_index()
        # Coação final defensiva — garante string mesmo após groupby
        _df_hoje_agg = _coage_categoria_str(_df_hoje_agg, ['Ramo', 'Utilização'])
        _df_hoje_agg['tipo_registro'] = 'AGG_CARTEIRA'
        _df_hoje_agg['data_snapshot'] = pd.Timestamp(_HOJE_STR)

    # ── Combina histórico (snapshots_uploaded) ──────────────────────────────
    _todos_dfs = [_df_hoje_sin]
    if not _df_hoje_agg.empty:
        _todos_dfs.append(_df_hoje_agg)

    for _date_key, _df_hist in st.session_state.get('snapshots_uploaded', {}).items():
        if _date_key == _HOJE_STR:
            continue
        _df_h = _df_hist.copy()
        if 'data_snapshot' not in _df_h.columns:
            _df_h['data_snapshot'] = pd.Timestamp(_date_key)
        # Retrocompat: snapshots antigos não têm tipo_registro
        if 'tipo_registro' not in _df_h.columns:
            _df_h['tipo_registro'] = 'SINISTRO'
        _todos_dfs.append(_df_h)

    _consolidado = pd.concat(_todos_dfs, ignore_index=True, sort=False)

    # Dedup separado por tipo de registro
    _mask_sin = _consolidado['tipo_registro'] == 'SINISTRO'
    _sin = _consolidado[_mask_sin].drop_duplicates(subset=['nr_sinistro', 'data_snapshot'], keep='last')
    _agg = _consolidado[~_mask_sin]
    if not _agg.empty and 'Ramo' in _agg.columns and 'Utilização' in _agg.columns:
        _agg = _agg.drop_duplicates(subset=['Ramo', 'Utilização', 'data_snapshot'], keep='last')
    _consolidado = pd.concat([_sin, _agg], ignore_index=True, sort=False)

    _buf = _io.BytesIO()
    _consolidado.to_parquet(_buf, index=False)
    _buf.seek(0)
    return _buf.getvalue(), len(_consolidado), _consolidado['data_snapshot'].nunique()

# Inicializa o dicionário de snapshots carregados nesta sessão (chave = data ISO)
if 'snapshots_uploaded' not in st.session_state:
    st.session_state['snapshots_uploaded'] = {}

# Prepara dados_exibicao
dados_exibicao = dados_calculados.copy()
dados_exibicao['Soma Prêmio Pago por Apolice'] = dados_exibicao['Soma Prêmio Pago por Apolice'].astype(object)
dados_exibicao['Soma Sinistro Por Apolice']     = dados_exibicao['Soma Sinistro Por Apolice'].astype(object)
dados_exibicao['% Sin'] = (dados_exibicao['Soma Sinistro Por Apolice'] / dados_exibicao['Soma Prêmio Pago por Apolice'].replace(0, float('nan'))).fillna(0).map(lambda x: f"{x:.2%}")
dados_exibicao['Soma Prêmio Pago por Apolice'] = dados_exibicao['Soma Prêmio Pago por Apolice'].map(formatar_valor_br)
dados_exibicao['Soma Sinistro Por Apolice']     = dados_exibicao['Soma Sinistro Por Apolice'].map(formatar_valor_br)
colunas = list(dados_exibicao.columns)
for col in ['Soma Sinistro Por Apolice', '% Sin']:
    if col in colunas:
        colunas.remove(col)
colunas.insert(2, 'Soma Sinistro Por Apolice')
colunas.insert(3, '% Sin')
dados_exibicao = dados_exibicao[colunas].sort_values('N° Apólice')

# ── PÁGINA 2: DADOS GERAIS ────────────────────────────────────────────────────

# Link de volta para a página principal na sidebar
st.sidebar.header('Dados por Apólice')
st.sidebar.page_link("app_homologacao.py", label="📋  Apólice / Segurado")

# --- Lógica de Filtragem Hierárquica na Sidebar ---
st.sidebar.header('Filtros Dados Gerais')

# Botão para Resetar Filtros — limpa todas as keys do session_state
_filtro_keys = ['filtro_rep', 'filtro_cor', 'filtro_seg', 'filtro_ramo', 'filtro_util', 'filtro_tp_emissao', 'filtro_regiao', 'filtro_uf', 'filtro_apolice']

st.sidebar.markdown('<div style="margin-top:1rem"></div>', unsafe_allow_html=True)
if st.sidebar.button('Limpar Todos os Filtros'):
    for k in _filtro_keys:
        if k in st.session_state:
            st.session_state[k] = []
    st.session_state['resetar_slider'] = True
    st.rerun()

# 1. Filtro por Representante
representantes_unicos = sorted(dados_exibicao['Representante'].astype(str).unique())
representantes_selecionados = st.sidebar.multiselect('Representante(s)', options=representantes_unicos, default=[], key='filtro_rep')

dados_filtrados_rep = dados_exibicao.copy()
if representantes_selecionados:
    dados_filtrados_rep = dados_filtrados_rep[dados_filtrados_rep['Representante'].astype(str).isin(representantes_selecionados)]

# 2. Filtro por Corretor
corretores_unicos = sorted(dados_filtrados_rep['Corretor'].astype(str).unique())
corretores_selecionados = st.sidebar.multiselect('Corretor(es)', options=corretores_unicos, default=[], key='filtro_cor')

dados_filtrados_corr = dados_filtrados_rep.copy()
if corretores_selecionados:
    dados_filtrados_corr = dados_filtrados_corr[dados_filtrados_corr['Corretor'].astype(str).isin(corretores_selecionados)]

# 3. Filtro por Segurado
segurados_unicos = sorted(dados_filtrados_corr['Segurado'].astype(str).unique())
segurados_selecionados = st.sidebar.multiselect('Segurado(s)', options=segurados_unicos, default=[], key='filtro_seg')

dados_filtrados_segurado = dados_filtrados_corr.copy()
if segurados_selecionados:
    dados_filtrados_segurado = dados_filtrados_segurado[dados_filtrados_segurado['Segurado'].astype(str).isin(segurados_selecionados)]

# 4. Filtro por Ramo
ramos_unicos = sorted(dados_filtrados_segurado['Ramo'].unique())
ramos_selecionados = st.sidebar.multiselect('Ramo(s)', options=ramos_unicos, default=[], key='filtro_ramo')

dados_filtrados_ramo = dados_filtrados_segurado.copy()
if ramos_selecionados:
    dados_filtrados_ramo = dados_filtrados_ramo[dados_filtrados_ramo['Ramo'].isin(ramos_selecionados)]

# 5. Filtro por Utilização
utilizacoes_unicas = sorted(dados_filtrados_ramo['Utilização'].astype(str).unique())
utilizacoes_selecionadas = st.sidebar.multiselect('Utilização(ões)', options=utilizacoes_unicas, default=[], key='filtro_util')

dados_filtrados_util = dados_filtrados_ramo.copy()
if utilizacoes_selecionadas:
    dados_filtrados_util = dados_filtrados_util[dados_filtrados_util['Utilização'].astype(str).isin(utilizacoes_selecionadas)]

# 6. Filtro por Tipo de Emissão
tipos_emissao_unicos = sorted(dados_filtrados_util['Tipo de Apólice'].astype(str).unique())
tipos_emissao_selecionados = st.sidebar.multiselect('Tipo de Emissão', options=tipos_emissao_unicos, default=[], key='filtro_tp_emissao')

dados_filtrados_tp_emissao = dados_filtrados_util.copy()
if tipos_emissao_selecionados:
    dados_filtrados_tp_emissao = dados_filtrados_tp_emissao[dados_filtrados_tp_emissao['Tipo de Apólice'].astype(str).isin(tipos_emissao_selecionados)]

# 7. Filtro por Região de Circulação
regioes_unicas = sorted(dados_filtrados_tp_emissao['Região de Circulação'].astype(str).unique())
regioes_selecionadas = st.sidebar.multiselect('Região de Circulação', options=regioes_unicas, default=[], key='filtro_regiao')

dados_filtrados_regiao = dados_filtrados_tp_emissao.copy()
if regioes_selecionadas:
    dados_filtrados_regiao = dados_filtrados_regiao[dados_filtrados_regiao['Região de Circulação'].astype(str).isin(regioes_selecionadas)]

# 8. Filtro por UF (extraída dos 2 primeiros caracteres da Região de Circulação)
dados_filtrados_regiao['_UF'] = dados_filtrados_regiao['Região de Circulação'].astype(str).str[:2].str.strip()
ufs_unicas = sorted(dados_filtrados_regiao['_UF'].unique())
ufs_selecionadas = st.sidebar.multiselect('UF', options=ufs_unicas, default=[], key='filtro_uf')

dados_filtrados_uf = dados_filtrados_regiao.copy()
if ufs_selecionadas:
    dados_filtrados_uf = dados_filtrados_uf[dados_filtrados_uf['_UF'].isin(ufs_selecionadas)]

# 9. Filtro por Apólice (filtrado por todos os anteriores)
apolices_unicas = sorted(dados_filtrados_uf['N° Apólice'].unique())
apolices_selecionadas = st.sidebar.multiselect('Apólice(s)', options=apolices_unicas, default=[], key='filtro_apolice')

resultado_final_filtrado = dados_filtrados_uf.copy()
if apolices_selecionadas:
    resultado_final_filtrado = resultado_final_filtrado[resultado_final_filtrado['N° Apólice'].isin(apolices_selecionadas)]

# --- AJUSTE AQUI: Filtragem do Sinistro Geral ---
# Pegamos a lista de apólices que sobraram após TODOS os filtros acima
lista_apolices_filtradas = resultado_final_filtrado['N° Apólice'].unique()

# Filtramos a base de sinistros original para conter apenas essas apólices
df_sinistro_geral_filtrado = df_sinistros[df_sinistros['N° Apólice'].isin(lista_apolices_filtradas)].copy()

# Fazemos o merge para trazer os nomes de Representante e Corretor para a tabela de sinistros
df_sinistro_geral_com_rep_cor = pd.merge(
    df_sinistro_geral_filtrado,
    dados_exibicao[['N° Apólice', 'Representante', 'Corretor']],
    on='N° Apólice',
    how='left'
)

# Formata a coluna de valor para exibição (apenas se houver dados)
if not df_sinistro_geral_com_rep_cor.empty:
    df_sinistro_geral_com_rep_cor['Total Sinistro'] = df_sinistro_geral_com_rep_cor['Total Sinistro'].map(formatar_valor_br)

# --- Indicadores Chave (KPIs) ---

# sac.divider(label='Dados Gerais', icon=sac.BsIcon(name='gear', size=20), align='start', color='gray')
# 'https://nicedouble-streamlitantdcomponentsdemo-app-middmy.streamlit.app/'

# Âncora invisível no topo + botão flutuante (estilizado via ALLSEG_CSS)
st.markdown(
    '<div id="topo-pagina"></div>'
    '<a href="#topo-pagina" class="btn-topo" title="Voltar ao topo">&#8679;</a>',
    unsafe_allow_html=True
)

st.subheader("Dados Gerais")

# ── Resumo dos filtros ativos (só exibe se houver algum filtro selecionado) ───
_filtros_ativos = {
    'Representante':        representantes_selecionados,
    'Corretor':             corretores_selecionados,
    'Segurado':             segurados_selecionados,
    'Ramo':                 ramos_selecionados,
    'Utilização':           utilizacoes_selecionadas,
    'Tipo de Emissão':      tipos_emissao_selecionados,
    'Região de Circulação': regioes_selecionadas,
    'UF':                   ufs_selecionadas,
    'Apólice':              apolices_selecionadas,
}
_filtros_com_valor = {k: v for k, v in _filtros_ativos.items() if v}

if _filtros_com_valor:
    _partes = []
    for k, v in _filtros_com_valor.items():
        _vals = ', '.join(str(x) for x in v)
        _partes.append(f'<b>{k}:</b> {_vals}')
    _texto = '&nbsp;&nbsp;|&nbsp;&nbsp;'.join(_partes)
    st.markdown(
        f'<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;'
        f'padding:8px 14px;margin-bottom:8px;font-size:13px;color:#1E40AF;">'
        f'🔍 <b>Filtros ativos:</b>&nbsp;&nbsp;{_texto}</div>',
        unsafe_allow_html=True
    )

# ============= PARTE REFERENTE AO SLIDER PARA SELECIONAR ANO =============
col_esq, col_meio, col_dir = st.columns([4,1,1])

# Definir os limites do slider com base nos dados filtrados pela sidebar
ano_min_absoluto = int(resultado_final_filtrado['Ano Vigência'].min())
ano_max_absoluto = int(resultado_final_filtrado['Ano Vigência'].max())

with col_esq:
    # Criar o Slider de Intervalo (Range Slider)
    if ano_min_absoluto < ano_max_absoluto:
        # Título customizado com espaçamento para não colar no slider
        st.write("")
        st.markdown('<p class="section-label">Selecione o Intervalo de Anos (Início de Vigência Apólice)</p>', unsafe_allow_html=True)
        # Flag: se botão limpar foi clicado, força visualmente o valor padrão
        if st.session_state.get('resetar_slider', False):
            st.session_state['slider_anos'] = (ano_min_absoluto, ano_max_absoluto)
            st.session_state['resetar_slider'] = False

        anos_selecionados = st.slider(
            label='Seletor de Anos Vigência',
            label_visibility="collapsed",
            min_value=ano_min_absoluto,
            max_value=ano_max_absoluto,
            value=(ano_min_absoluto, ano_max_absoluto),
            step=1,
            key='slider_anos'
        )
    else:
        # Se só houver um ano, o intervalo é fixo nesse ano
        st.info(f"Período único disponível: {ano_min_absoluto}")
        anos_selecionados = (ano_min_absoluto, ano_max_absoluto)

# Filtrar o DataFrame com base no Slider (Este DF agora manda em tudo abaixo dele)
df_geral_periodo = resultado_final_filtrado[
    (resultado_final_filtrado['Ano Vigência'] >= anos_selecionados[0]) & 
    (resultado_final_filtrado['Ano Vigência'] <= anos_selecionados[1])
].copy()

# Converte as colunas de volta para numérico para somar usando o DF do período selecionado
df_para_soma = df_geral_periodo.copy()

df_para_soma['Soma Prêmio Pago por Apolice'] = df_para_soma['Soma Prêmio Pago por Apolice'].str.replace(
    '.', '').str.replace(',', '.').astype(float)
df_para_soma['Soma Sinistro Por Apolice'] = df_para_soma['Soma Sinistro Por Apolice'].str.replace(
    '.', '').str.replace(',', '.').astype(float)

# Calcula o percentual de sinistro total
total_premio = df_para_soma['Soma Prêmio Pago por Apolice'].sum()
total_sinistro = df_para_soma['Soma Sinistro Por Apolice'].sum()
percentual_sinistro_total = (total_sinistro / total_premio) if total_premio != 0 else 0

# --- CORREÇÃO DAS QUANTIDADES ---
# 1. Qtd. Apólices: Contar apólices únicas no DF filtrado pelo slider
qtd_apolice_geral = df_geral_periodo['N° Apólice'].nunique()

# 2. Qtd. Sinistros: Filtrar a base de sinistros para as apólices do período do slider
lista_apos_periodo = df_geral_periodo['N° Apólice'].unique()
df_sinistro_periodo_atualizado = df_sinistro_geral_filtrado[df_sinistro_geral_filtrado['N° Apólice'].isin(lista_apos_periodo)].copy()
# Pré-processa datas uma única vez — evita pd.to_datetime repetido nas seções de análise
if not df_sinistro_periodo_atualizado.empty:
    df_sinistro_periodo_atualizado['dt_aviso_dt']      = pd.to_datetime(df_sinistro_periodo_atualizado['dt_aviso'],      dayfirst=True, errors='coerce')
    df_sinistro_periodo_atualizado['dt_ocorrencia_dt'] = pd.to_datetime(df_sinistro_periodo_atualizado['dt_ocorrencia'], dayfirst=True, errors='coerce')
    df_sinistro_periodo_atualizado['Ano_Aviso']        = df_sinistro_periodo_atualizado['dt_aviso_dt'].dt.year
    df_sinistro_periodo_atualizado['AnoMes']           = df_sinistro_periodo_atualizado['dt_aviso_dt'].dt.to_period('M').astype(str)
qtd_sinistros_geral = df_sinistro_periodo_atualizado['nr_sinistro'].nunique()
# --------------------------------

# Colunas para informações do dados gerias
st.markdown("<br>", unsafe_allow_html=True) # Espaço antes dos KPIs

# Média de dias para aviso — dados gerais (sem outliers: descarta dias > período total da base)
# Período max cacheado — calcula uma única vez para toda a base
_periodo_max_geral = _calcular_periodo_max_aviso(
    tuple(df_sinistros['dt_aviso'].tolist()),
    tuple(df_sinistros['dt_ocorrencia'].tolist())
) if not df_sinistros.empty else 9999

# Média de dias cacheada por conjunto de apólices do período filtrado
media_dias_geral_str = _calcular_media_dias_aviso(
    tuple(df_sinistro_periodo_atualizado['N° Apólice'].tolist()),
    tuple(df_sinistro_periodo_atualizado['dt_aviso'].tolist()),
    tuple(df_sinistro_periodo_atualizado['dt_ocorrencia'].tolist()),
    _periodo_max_geral
) if not df_sinistro_periodo_atualizado.empty else "—"

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(label="Total Prêmio Pago", value=f"R$ {formatar_valor_br(total_premio)}")
with col2:
    st.metric(label="Total Sinistro", value=f"R$ {formatar_valor_br(total_sinistro)}")
with col3:
    st.metric(label="% Sinistralidade", value=f"{percentual_sinistro_total:.2%}")
with col4:
    st.metric(label="Qtd. Apólices", value=qtd_apolice_geral)
with col5:
    st.metric(label="Qtd. Sinistros", value=qtd_sinistros_geral)
with col6:
    st.metric(label="Média Dias p/ Aviso", value=media_dias_geral_str)

# ============= PARTE REFERENTE AO EVOLUÇÃO TEMPORAL - PREMIO X SINISTRO =============
# Agrupar os dados por ano para o gráfico
df_evolucao = df_para_soma.groupby('Ano Vigência').agg({
    'Soma Prêmio Pago por Apolice': 'sum',
    'Soma Sinistro Por Apolice': 'sum'
}).reset_index()

# Criar o gráfico de linhas com Plotly
fig_evolucao = go.Figure()

# Linha de Prêmios
fig_evolucao.add_trace(go.Scatter(
    x=df_evolucao['Ano Vigência'], 
    y=df_evolucao['Soma Prêmio Pago por Apolice'],
    mode='lines+markers',
    name='Total Prêmio',
    line=dict(color='#36A2EB', width=4),
    hovertemplate='Ano: %{x}<br>Prêmio: R$ %{y:,.2f}'
))

# Linha de Sinistros
fig_evolucao.add_trace(go.Scatter(
    x=df_evolucao['Ano Vigência'], 
    y=df_evolucao['Soma Sinistro Por Apolice'],
    mode='lines+markers',
    name='Total Sinistro',
    line=dict(color='red', width=4),
    hovertemplate='Ano: %{x}<br>Sinistro: R$ %{y:,.2f}'
))

fig_evolucao.update_layout(
    xaxis=dict(tickmode='linear', dtick=1), # Força a exibição de ano em ano
    yaxis_title="Valores (R$)",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=0, r=0, t=40, b=0)
)
# ============= PARTE REFERENTE AO EVOLUÇÃO TEMPORAL - PREMIO X SINISTRO =============


# ============= GRÁFICO DE BARRAS HORIZONTAIS - PRÊMIO X SINISTRO POR ANO =============

# Criar o gráfico de barras horizontais
fig_barras_h = go.Figure()

# Barra de Prêmios (Horizontal)
fig_barras_h.add_trace(go.Bar(
    y=df_evolucao['Ano Vigência'].astype(str), # Ano no eixo Y para ficar na horizontal
    x=df_evolucao['Soma Prêmio Pago por Apolice'],
    name='Total Prêmio',
    orientation='h',
    marker_color='#36A2EB',
    text=df_evolucao['Soma Prêmio Pago por Apolice'].apply(formatar_valor_br),
    textposition='auto'
))

# Barra de Sinistros (Horizontal)
fig_barras_h.add_trace(go.Bar(
    y=df_evolucao['Ano Vigência'].astype(str),
    x=df_evolucao['Soma Sinistro Por Apolice'],
    name='Total Sinistro',
    orientation='h',
    marker_color='red',
    text=df_evolucao['Soma Sinistro Por Apolice'].apply(formatar_valor_br),
    textposition='auto'
))

fig_barras_h.update_layout(
    barmode='group',
    xaxis_title="Valores (R$)",
    yaxis_title="Ano",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=0, r=0, t=30, b=0),
    height=400 # Você pode ajustar a altura conforme a quantidade de anos
)
# ============= GRÁFICO DE BARRAS HORIZONTAIS - PRÊMIO X SINISTRO POR ANO =============


# ============= PLOT DO GRAFICOS LINHAS E BARRAS 2 COLUNAS =============
st.markdown("<br>", unsafe_allow_html=True) # Espaço antes dos KPIs
col_linha_barra_1, col_linha_barra_2 = st.columns(2)
with col_linha_barra_1:
    # plot grafico linhas premio x sinistro
    st.markdown('<p class="section-label">Evolução Anual</p>', unsafe_allow_html=True)
    st.plotly_chart(fig_evolucao, use_container_width=True, config={'displayModeBar': False})
with col_linha_barra_2:
    # plot grafico barras premio x sinistro
    # st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-label">Prêmio x Sinistro Anual</p>', unsafe_allow_html=True)
    st.plotly_chart(fig_barras_h, use_container_width=True, config={'displayModeBar': False})
    st.markdown("<br><br>", unsafe_allow_html=True)


# ============= ANÁLISE CONSOLIDADA POR ANO (DADOS GERAIS) =============
# 1. Agrupamento por Ano (Prêmio, Sinistro e Qtd Apólices)
# Utilizamos o df_para_soma que já contém os dados filtrados
# ── Seletor de visão: Ano de Subscrição (UWY) × Ano do Acidente (AY) ─────────
with st.container(border=True):
    st.markdown(
        '<div style="font-size:12px;color:#64748B;margin-bottom:6px;">'
        '🔁 <b>A seleção abaixo altera somente</b> a tabela <b>Desempenho Consolidado por Ano</b> '
        'e o gráfico <b>Evolução da Sinistralidade (%)</b> dentro deste quadro.</div>',
        unsafe_allow_html=True
    )
    _visao_ano = st.radio(
        "**Visão de alocação de sinistros:**",
        options=["Ano de Subscrição (UWY)", "Ano do Acidente (AY)"],
        horizontal=True,
        key="radio_visao_ano",
        help=(
            "**Ano de Subscrição (UWY):** prêmio, sinistro e quantidade de sinistros alocados "
            "ao ano de vigência da apólice. Ideal para análise de subscrição — mostra o "
            "resultado técnico de cada safra de apólices.\n\n"
            "**Ano do Acidente (AY):** sinistros alocados ao ano em que o evento ocorreu, "
            "independente da vigência da apólice. Ideal para análise de exposição a "
            "risco e eventos climáticos/judiciais por período."
        )
    )

    # Descrição visual da visão selecionada
    if _visao_ano == "Ano de Subscrição (UWY)":
        st.caption(
            "📋 **Ano de Subscrição / Underwriting Year (UWY):** prêmio e sinistros agrupados pelo **ano de vigência da apólice**. "
            "Permite avaliar o resultado técnico de cada coorte de contratos subscritos."
        )
    else:
        st.caption(
            "📋 **Ano do Acidente / Accident Year (AY):** sinistros agrupados pelo **ano em que o evento ocorreu**. "
            "Prêmio mantido por ano de vigência. Permite analisar a concentração de eventos por período."
        )

    # ── Base de sinistros filtrada pelas apólices do período ─────────────────────
    lista_apos_ano = df_para_soma['N° Apólice'].unique()
    df_sin_filtrado_ano = df_sinistros[df_sinistros['N° Apólice'].isin(lista_apos_ano)].copy()

    # ── Cálculo conforme visão selecionada ───────────────────────────────────────
    if _visao_ano == "Ano de Subscrição (UWY)":
        # Ano de Subscrição (UWY): qtd sinistros pelo Ano Vigência da apólice
        _apo_uw = df_para_soma[['N° Apólice', 'Ano Vigência']].drop_duplicates('N° Apólice')
        _sin_uw = pd.merge(df_sin_filtrado_ano, _apo_uw, on='N° Apólice', how='left')
        qtd_sin_por_ano = _sin_uw.groupby('Ano Vigência')['nr_sinistro'].nunique().reset_index()
        qtd_sin_por_ano.rename(columns={'nr_sinistro': 'Qtd_Sinistros'}, inplace=True)
        df_ano_geral = df_para_soma.groupby('Ano Vigência').agg(
            Total_Premio=('Soma Prêmio Pago por Apolice', 'sum'),
            Total_Sinistro=('Soma Sinistro Por Apolice', 'sum'),
            Qtd_Apolices=('N° Apólice', 'nunique')
        ).reset_index()
        df_final_ano = pd.merge(df_ano_geral, qtd_sin_por_ano, on='Ano Vigência', how='left').fillna(0)
    else:
        # Ano do Acidente (AY): sinistros alocados ao ano de ocorrência
        if 'dt_ocorrencia_dt' in df_sin_filtrado_ano.columns:
            df_sin_filtrado_ano['Ano_Ocorrencia'] = df_sin_filtrado_ano['dt_ocorrencia_dt'].dt.year
        else:
            df_sin_filtrado_ano['Ano_Ocorrencia'] = pd.to_datetime(
                df_sin_filtrado_ano['dt_ocorrencia'], dayfirst=True, errors='coerce').dt.year
        # Sinistro por ano de ocorrência
        _sin_oc = df_sin_filtrado_ano.copy()
        _sin_oc['Total Sinistro'] = (_sin_oc['vl_sinistro_total'].fillna(0) + _sin_oc['vl_despesa_total'].fillna(0)
                                      + _sin_oc['vl_honorario_total'].fillna(0) - _sin_oc['vl_salvado_total'].fillna(0))
        _sin_oc_ano = _sin_oc.groupby('Ano_Ocorrencia').agg(
            Total_Sinistro_AY=('Total Sinistro', 'sum'),
            Qtd_Sinistros=('nr_sinistro', 'nunique')
        ).reset_index().rename(columns={'Ano_Ocorrencia': 'Ano Vigência'})
        df_ano_geral = df_para_soma.groupby('Ano Vigência').agg(
            Total_Premio=('Soma Prêmio Pago por Apolice', 'sum'),
            Qtd_Apolices=('N° Apólice', 'nunique')
        ).reset_index()
        df_final_ano = pd.merge(df_ano_geral, _sin_oc_ano, on='Ano Vigência', how='outer').fillna(0)
        df_final_ano.rename(columns={'Total_Sinistro_AY': 'Total_Sinistro'}, inplace=True)
        df_final_ano = df_final_ano.sort_values('Ano Vigência')

    df_final_ano['Qtd_Sinistros'] = df_final_ano['Qtd_Sinistros'].astype(int)

    # 4. Cálculo da Sinistralidade (numérico para o gráfico)
    df_final_ano['Sinistralidade_Num'] = (
        df_final_ano['Total_Sinistro'] / df_final_ano['Total_Premio'].replace(0, float('nan'))
    ).fillna(0)

    # 5. Formatação para a Tabela de Exibição
    df_ano_view = df_final_ano.copy()
    df_ano_view['Total_Premio'] = df_ano_view['Total_Premio'].map(formatar_valor_br)
    df_ano_view['Total_Sinistro'] = df_ano_view['Total_Sinistro'].map(formatar_valor_br)
    df_ano_view['% Sinistralidade'] = df_ano_view['Sinistralidade_Num'].map(lambda x: f"{x:.2%}")
    df_ano_view['Qtd_Sinistros'] = df_ano_view['Qtd_Sinistros'].astype(int)

    # 6. Gráfico de Visualização de Sinistralidade por Ano
    fig_sin_ano = px.line(
        df_final_ano,
        x='Ano Vigência',
        y='Sinistralidade_Num',
        markers=True,
        text=df_final_ano['Sinistralidade_Num'].map(lambda x: f"{x:.2%}"),
        labels={'Sinistralidade_Num': 'Sinistralidade', 'Ano Vigência': 'Ano'},
        template="plotly_white"
    )

    fig_sin_ano.update_traces(
        line_color='red', 
        textposition="top center",
        hovertemplate="Ano: %{x}<br>Sinistralidade: %{y:.2%}"
    )

    fig_sin_ano.update_layout(
        yaxis_tickformat='.0%', # Formata o eixo Y como porcentagem
        xaxis=dict(dtick=1),     # Garante que mostre ano a ano
        height=400,
        margin=dict(l=0, r=0, t=30, b=0)
    )

    # Exibição da Tabela ano ramo
    col_ano_1,col_ano_2 = st.columns(2)

    with col_ano_1:
        st.markdown('<p class="section-label">Desempenho Consolidado por Ano</p>', unsafe_allow_html=True)
        st.dataframe(df_ano_view[['Ano Vigência','Total_Premio', 'Total_Sinistro', '% Sinistralidade', 'Qtd_Apolices', 'Qtd_Sinistros']], 
                    hide_index=True, use_container_width=True)
    with col_ano_2:
        st.markdown('<p class="section-label">Evolução da Sinistralidade (%)</p>', unsafe_allow_html=True)
        st.plotly_chart(fig_sin_ano, use_container_width=True, config={'displayModeBar': False})

# --- Exibição dos Resultados ---
col_final_1, col_final_2 = st.columns(2)

with col_final_1:
    st.markdown('<p class="section-label">Sinistros</p>', unsafe_allow_html=True)
    # Trazemos os nomes de Representante e Corretor para o DF que já está filtrado por ANO
    df_sinistro_final_exibicao = pd.merge(
        df_sinistro_periodo_atualizado, # Este já está filtrado pelo Slider
        dados_exibicao[['N° Apólice', 'Representante', 'Corretor']],
        on='N° Apólice',
        how='left'
    )
    
    if not df_sinistro_final_exibicao.empty:
        # Adiciona Franquia Apólice por Cobertura — deduplica para evitar duplicatas no merge
        if not df_cobertura.empty:
            # Franquia por apólice + cobertura usando fuzzy match de nomes
            _cob_geral = df_cobertura[df_cobertura['N° Apólice'].isin(df_sinistro_final_exibicao['N° Apólice'].unique())]
            df_sinistro_final_exibicao = mapear_franquia_por_cobertura(df_sinistro_final_exibicao, _cob_geral)
        else:
            df_sinistro_final_exibicao['Franquia Apólice'] = 0.0
        # Formata para exibição
        # Formata todas as colunas de valor no padrão BR — igual aos DFs do app
        _colunas_valor = [
            'vl_sinistro_pago', 'vl_sinistro_pendente', 'vl_sinistro_total',
            'vl_despesa_pago', 'vl_despesa_pendente', 'vl_despesa_total',
            'vl_honorario_pago', 'vl_honorario_pendente', 'vl_honorario_total',
            'vl_salvado_pago', 'vl_salvado_pendente', 'vl_salvado_total',
            'Total Sinistro', 'Franquia Apólice'
        ]
        for _col in _colunas_valor:
            if _col in df_sinistro_final_exibicao.columns:
                df_sinistro_final_exibicao[_col] = df_sinistro_final_exibicao[_col].map(formatar_valor_br)
        # Colunas na mesma sequência dos DFs do app_homologacao
        colunas_base = [
            'nr_sinistro', 'nr_ramo', 'N° Apólice', 'nr_endosso', 'nm_cliente', 'Cobertura',
            'dt_aviso', 'dt_ocorrencia',
            'vl_sinistro_pago', 'vl_sinistro_pendente', 'vl_sinistro_total',
            'vl_despesa_pago', 'vl_despesa_pendente', 'vl_despesa_total',
            'vl_honorario_pago', 'vl_honorario_pendente', 'vl_honorario_total',
            'vl_salvado_pago', 'vl_salvado_pendente', 'vl_salvado_total',
            'status_processo', 'status_movimento', 'nm_causa', 'id_endosso', 't',
            'Total Sinistro', 'Representante', 'Corretor', 'Franquia Apólice'
        ]
        colunas_exibir = [c for c in colunas_base if c in df_sinistro_final_exibicao.columns]
        st.dataframe(df_sinistro_final_exibicao[colunas_exibir], hide_index=True)
    else:
        st.info("Nenhum sinistro no período selecionado.")
        
with col_final_2:
    st.markdown('<p class="section-label">Prêmios e Sinistros Apólices</p>', unsafe_allow_html=True)
    # Usamos o df_geral_periodo que contém o filtro do Slider de Ano
    if not df_geral_periodo.empty:
        st.dataframe(df_geral_periodo, hide_index=True)
    else:
        st.info("Nenhum dado encontrado com os filtros selecionados.")

# --- Dados de Prêmio e Sinistro por Tipo de Emissão (Dados Gerais) ---
st.markdown('<p class="section-label">Prêmio e Sinistro por Tipo de Emissão</p>', unsafe_allow_html=True)

if not df_geral_periodo.empty:
    df_tp_em = df_geral_periodo.copy()
    df_tp_em['Soma Prêmio Pago por Apolice'] = df_tp_em['Soma Prêmio Pago por Apolice'].str.replace('.', '').str.replace(',', '.').astype(float)
    df_tp_em['Soma Sinistro Por Apolice']    = df_tp_em['Soma Sinistro Por Apolice'].str.replace('.', '').str.replace(',', '.').astype(float)

    groupby_tp_emissao = df_tp_em.groupby('Tipo de Apólice').agg(
        Qtd_Apolices=('N° Apólice', 'nunique'),
        Total_Premio=('Soma Prêmio Pago por Apolice', 'sum'),
        Total_Sinistro=('Soma Sinistro Por Apolice', 'sum')
    ).reset_index()

    # Cruzamento com sinistros para Qtd_Sinistros
    df_sin_tp_contagem = df_sinistro_periodo_atualizado.merge(
        df_tp_em[['N° Apólice', 'Tipo de Apólice']],
        on='N° Apólice', how='left'
    )
    qtd_sin_tp = df_sin_tp_contagem.groupby('Tipo de Apólice')['nr_sinistro'].nunique().reset_index()
    qtd_sin_tp.rename(columns={'nr_sinistro': 'Qtd_Sinistros'}, inplace=True)

    groupby_tp_emissao = pd.merge(groupby_tp_emissao, qtd_sin_tp, on='Tipo de Apólice', how='left').fillna(0)
    groupby_tp_emissao['Qtd_Sinistros'] = groupby_tp_emissao['Qtd_Sinistros'].astype(int)
    groupby_tp_emissao['% Sinistralidade'] = groupby_tp_emissao.apply(
        lambda row: '{:.2%}'.format(row['Total_Sinistro'] / row['Total_Premio'])
        if row['Total_Premio'] != 0 else '0.00%', axis=1
    )
    groupby_tp_emissao['Total_Premio']   = groupby_tp_emissao['Total_Premio'].map(formatar_valor_br)
    groupby_tp_emissao['Total_Sinistro'] = groupby_tp_emissao['Total_Sinistro'].map(formatar_valor_br)
    groupby_tp_emissao = groupby_tp_emissao[
        ['Tipo de Apólice', 'Qtd_Apolices', 'Qtd_Sinistros', 'Total_Premio', 'Total_Sinistro', '% Sinistralidade']
    ].sort_values(by='Qtd_Apolices', ascending=False)

    st.dataframe(groupby_tp_emissao, hide_index=True, use_container_width=True)
else:
    st.info("Nenhum dado disponível para agrupar por Tipo de Emissão.")

# --- Dados de Prêmio e Sinistro por Utilização ---
col_pr_sin_util_1, col_pr_sin_util_2 = st.columns(2)

with col_pr_sin_util_1:
    st.markdown('<p class="section-label">Prêmio e Sinistro por Utilização</p>', unsafe_allow_html=True)

    if not df_geral_periodo.empty:
        # 1. Preparação dos dados numéricos para soma
        df_util = df_geral_periodo.copy()
        
        # Convertemos as strings formatadas de volta para float para permitir cálculos
        df_util['Soma Prêmio Pago por Apolice'] = df_util['Soma Prêmio Pago por Apolice'].str.replace(
            '.', '').str.replace(',', '.').astype(float)
        df_util['Soma Sinistro Por Apolice'] = df_util['Soma Sinistro Por Apolice'].str.replace(
            '.', '').str.replace(',', '.').astype(float)

        # 2. Agrupamento principal
        # Aqui contamos as apólices únicas e somamos os valores
        groupby_utilizacao = df_util.groupby('Utilização').agg(
            Qtd_Apolices=('N° Apólice', 'nunique'),
            Total_Premio=('Soma Prêmio Pago por Apolice', 'sum'),
            Total_Sinistro=('Soma Sinistro Por Apolice', 'sum')
        ).reset_index()

        # 3. Cruzamento para obter a Quantidade de Sinistros
        # Precisamos contar os sinistros na base de sinistros filtrada, usando a 'Utilização' que está no df_util
        df_sinistros_contagem = df_sinistro_periodo_atualizado.merge(
            df_util[['N° Apólice', 'Utilização']], 
            on='N° Apólice', 
            how='left'
        )
        
        qtd_sin_por_util = df_sinistros_contagem.groupby('Utilização')['nr_sinistro'].nunique().reset_index()
        qtd_sin_por_util.rename(columns={'nr_sinistro': 'Qtd_Sinistros'}, inplace=True)

        # 4. Merge final dos dados agrupados com a contagem de sinistros
        groupby_utilizacao = pd.merge(groupby_utilizacao, qtd_sin_por_util, on='Utilização', how='left').fillna(0)

        # 5. Cálculos de Performance
        groupby_utilizacao['% Sinistralidade'] = groupby_utilizacao.apply(
            lambda row: '{:.2%}'.format(row['Total_Sinistro'] / row['Total_Premio'])
            if row['Total_Premio'] != 0 else '0.00%', axis=1
        )

        # 6. Formatação para exibição
        groupby_utilizacao['Total_Premio'] = groupby_utilizacao['Total_Premio'].map(formatar_valor_br)
        groupby_utilizacao['Total_Sinistro'] = groupby_utilizacao['Total_Sinistro'].map(formatar_valor_br)
        
        # Converte Qtd_Sinistros para inteiro (caso o merge tenha gerado floats por causa de NaNs)
        groupby_utilizacao['Qtd_Sinistros'] = groupby_utilizacao['Qtd_Sinistros'].astype(int)

        # Reordenar colunas para ficar intuitivo
        ordem_colunas = ['Utilização', 'Qtd_Apolices', 'Qtd_Sinistros', 'Total_Premio', 'Total_Sinistro', '% Sinistralidade']
        groupby_utilizacao = groupby_utilizacao[ordem_colunas].sort_values(by='Qtd_Apolices', ascending=False)

        # Exibição
        st.dataframe(
            groupby_utilizacao,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Utilização":       st.column_config.Column(width=210),
                "Qtd_Apolices":     st.column_config.Column(width=50),
                "Qtd_Sinistros":    st.column_config.Column(width=50),
                "% Sinistralidade":  st.column_config.Column(width=50),
            })
    else:
        st.info("Nenhum dado disponível para agrupar por Utilização.")


with col_pr_sin_util_2:
    # === Gráfico de Sinistralidade por Utilização ===
    st.markdown('<p class="section-label">Gráfico Sinistralidade por Utilização</p>', unsafe_allow_html=True)

    # 1. Criamos o DF auxiliar para o gráfico
    df_grafico_util = groupby_utilizacao.copy()

    # 2. Convertemos a porcentagem para float para o gráfico (Removendo formatação BR)
    df_grafico_util['Sinistralidade_Float'] = df_grafico_util['% Sinistralidade'].str.replace('%', '').str.replace(',', '.').astype(float)

    # 3. FILTRO: Removemos a utilização com nome "0" e também valores zerados para limpar o visual
    df_grafico_util = df_grafico_util[
        (df_grafico_util['Utilização'].astype(str) != '0') & 
        (df_grafico_util['Sinistralidade_Float'] > 0)
    ]

    if not df_grafico_util.empty:
        # 4. Ordenamos para que a maior sinistralidade fique no topo do gráfico horizontal
        df_grafico_util = df_grafico_util.sort_values(by='Sinistralidade_Float', ascending=True)

        # 5. Criação do gráfico de barras horizontais
        fig_util_sin = px.bar(
            df_grafico_util,
            x='Sinistralidade_Float', # Valor no eixo X
            y='Utilização',           # Categoria no eixo Y
            orientation='h',          # Define como Horizontal
            text='% Sinistralidade',  # Rótulo de texto dentro/ao lado da barra
            labels={'Sinistralidade_Float': 'Sinistralidade (%)'},
            color='Sinistralidade_Float',
            color_continuous_scale='Reds',
        )

        fig_util_sin.update_traces(
            textposition='outside',   # Garante que o % apareça fora da barra
            hovertemplate="Utilização: %{y}<br>Sinistralidade: %{text}"
        )

        fig_util_sin.update_layout(
            xaxis_title="Sinistralidade (%)",
            yaxis_title="",
            coloraxis_showscale=False,
            margin=dict(l=0, r=50, t=30, b=0), # Aumentei a margem direita para o texto não cortar
            height=max(300, len(df_grafico_util) * 40) # Altura dinâmica baseada na quantidade de itens
        )

        st.plotly_chart(
            fig_util_sin,
            use_container_width=True,
            config={
                'displayModeBar': False})
    else:
        st.info("Sem dados de Sinistro.")


# ── Evolução da Sinistralidade (%) por Utilização ────────────────────────────
st.markdown('<p class="section-label">Evolução da Sinistralidade (%) por Utilização</p>', unsafe_allow_html=True)

if not df_para_soma.empty:
    df_util_ano = df_para_soma.groupby(['Ano Vigência', 'Utilização']).agg(
        Total_Premio=('Soma Prêmio Pago por Apolice', 'sum'),
        Total_Sinistro=('Soma Sinistro Por Apolice', 'sum')
    ).reset_index()
    df_util_ano['Sinistralidade'] = df_util_ano.apply(
        lambda row: row['Total_Sinistro'] / row['Total_Premio'] if row['Total_Premio'] != 0 else 0, axis=1
    )
    utils_com_sin = df_util_ano[df_util_ano['Sinistralidade'] > 0]['Utilização'].unique()
    df_util_ano = df_util_ano[
        (df_util_ano['Utilização'].astype(str) != '0') &
        (df_util_ano['Utilização'].isin(utils_com_sin))
    ]
    if not df_util_ano.empty:
        fig_sin_util_ano = go.Figure()
        for util in sorted(df_util_ano['Utilização'].unique()):
            df_u = df_util_ano[df_util_ano['Utilização'] == util].sort_values('Ano Vigência')
            fig_sin_util_ano.add_trace(go.Scatter(
                x=df_u['Ano Vigência'],
                y=df_u['Sinistralidade'],
                mode='lines+markers+text',
                name=str(util),
                text=df_u['Sinistralidade'].map(lambda x: f"{x:.1%}"),
                textposition='top center',
                textfont=dict(size=10),
                marker=dict(size=7),
                line=dict(width=2),
            ))
        fig_sin_util_ano.update_layout(
            xaxis=dict(title='Ano', tickmode='linear', dtick=1),
            yaxis=dict(title='Sinistralidade (%)', tickformat='.0%'),
            legend=dict(orientation='v', yanchor='top', y=1, xanchor='left', x=1.01, font=dict(size=10)),
            margin=dict(t=40, b=20, l=0, r=180),
            height=430,
            hovermode='x unified'
        )
        fig_sin_util_ano.update_traces(hovertemplate='%{y:.2%}')
        st.plotly_chart(fig_sin_util_ano, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("Sem dados suficientes para o gráfico de sinistralidade por utilização.")

# ============= ANÁLISE POR RAMO E COBERTURA =============
# 1. Agrupamento principal por Ramo (Prêmio, Sinistro e Qtd Apólices)
groupby_geral_ramo = df_para_soma.groupby('Ramo').agg(
    Total_Premio=('Soma Prêmio Pago por Apolice', 'sum'),
    Total_Sinistro=('Soma Sinistro Por Apolice', 'sum'),
    Qtd_Apolices=('N° Apólice', 'nunique')
).reset_index()

# 2. Busca a quantidade de sinistros por ramo para o período selecionado
# Usamos o df_sinistro_periodo_atualizado que você já definiu anteriormente
qtd_sin_geral_por_ramo = df_sinistro_periodo_atualizado.groupby('nr_ramo')['nr_sinistro'].nunique().reset_index()
qtd_sin_geral_por_ramo.rename(columns={'nr_ramo': 'Ramo', 'nr_sinistro': 'Qtd_Sinistros'}, inplace=True)

# 3. Une as informações de prêmio/apólice com a contagem de sinistros
groupby_geral_ramo = pd.merge(groupby_geral_ramo, qtd_sin_geral_por_ramo, on='Ramo', how='left').fillna(0)

# 4. Cálculo da Sinistralidade
groupby_geral_ramo['Sinistralidade'] = groupby_geral_ramo.apply(
    lambda row: row['Total_Sinistro'] / row['Total_Premio'] if row['Total_Premio'] != 0 else 0, axis=1
)

# 5. Criar DataFrame de exibição com formatações
df_geral_ramo_exibicao = groupby_geral_ramo.copy()
df_geral_ramo_exibicao['Total_Premio'] = df_geral_ramo_exibicao['Total_Premio'].map(formatar_valor_br)
df_geral_ramo_exibicao['Total_Sinistro'] = df_geral_ramo_exibicao['Total_Sinistro'].map(formatar_valor_br)
df_geral_ramo_exibicao['Sinistralidade'] = df_geral_ramo_exibicao['Sinistralidade'].map(lambda x: f"{x:.2%}")
df_geral_ramo_exibicao['Qtd_Sinistros'] = df_geral_ramo_exibicao['Qtd_Sinistros'].astype(int)

# Reordenar colunas para a tabela ficar organizada
colunas_geral_view = ['Ramo', 'Total_Premio', 'Total_Sinistro', 'Sinistralidade', 'Qtd_Apolices', 'Qtd_Sinistros', ]
df_geral_ramo_exibicao = df_geral_ramo_exibicao[colunas_geral_view]

# 6. Agrupamento por Cobertura (Geral - Mantendo sua lógica original)
df_sinistro_geral_cobertura = df_sinistro_periodo_atualizado.groupby('Cobertura', as_index=False).agg(**{
    'Total Sinistro': ('Total Sinistro', 'sum'),
    'Qtd Sinistros': ('nr_sinistro', 'nunique')
})

# 3. Preparação do Gráfico de Pizza Geral
df_pizza_geral = df_sinistro_geral_cobertura[df_sinistro_geral_cobertura['Total Sinistro'] > 0].copy()
fig_pizza_geral = px.pie(
    df_pizza_geral,
    values='Total Sinistro',
    names='Cobertura',
    hole=0.4,
    height=400
)
fig_pizza_geral.update_traces(textposition='outside', textinfo='percent+value')


# Defina a largura das barras e a posição (offset) para que fiquem coladas
bar_width = 0.45
offset_premio = -bar_width / 2
offset_sinistro = bar_width / 2

# Gráfico de colunas para prêmio e sinistro dos ramos
fig_ramo_geral = go.Figure(data=[
    go.Bar(
        name='Total Prêmio',
        x=groupby_geral_ramo['Ramo'],
        y=groupby_geral_ramo['Total_Premio'],
        marker_color='rgba(54, 162, 235, 0.8)',
        width=bar_width,
        offset=offset_premio,  # Desloca a barra para a esquerda
        
        # === Adicione estas linhas para o rótulo da barra de Prêmio ===
        text=groupby_geral_ramo['Total_Premio'].map(formatar_valor_br),
        textposition='outside',
        textfont=dict(
            color='black',
            size=12
        )
    ),
    go.Bar(
        name='Total Sinistro',
        x=groupby_geral_ramo['Ramo'],
        y=groupby_geral_ramo['Total_Sinistro'],
        marker_color='red',
        width=bar_width,
        offset=offset_sinistro, # Desloca a barra para a direita
        # === Adicione estas linhas para o rótulo da barra de Sinistro ===
        text=groupby_geral_ramo['Total_Sinistro'].map(formatar_valor_br),
        textposition='outside',
        textfont=dict(
            color='black',
            size=12
        )
    )
])

fig_ramo_geral.update_layout(
    xaxis=dict(
        title='Ramo',
        type='category', # <--- Adicione esta linha!
        tickmode='array', # <--- Adicione esta linha!
        tickvals=groupby_geral_ramo['Ramo'] # <--- Adicione esta linha!
    ),
    yaxis_title='Valores (R$)',
    barmode='overlay', # Usa o modo overlay para sobrepor as barras
    bargap=0.1,  # Controla o espaço entre os grupos
    # === Configuração da legenda ===
    legend=dict(
        orientation="h",  # Torna a legenda horizontal
        yanchor="top", # Ancoragem vertical: fundo da legenda
        y=-0.2,           # Posição vertical: ligeiramente acima do gráfico (você pode ajustar este valor)
        xanchor="center",  # Ancoragem horizontal: direita da legenda
        x=0.5               # Posição horizontal: no canto superior direito
    ),
    # === ADICIONE ESTA LINHA PARA REMOVER O ESPAÇO SUPERIOR ===
    margin=dict(t=0, b=0, l=0, r=0)
)
fig_ramo_geral.update_layout(barmode='group', margin=dict(t=20, b=0, l=0, r=0), height=400)

# Exibição em Colunas
c1, c2 = st.columns(2)
with c1:
    st.markdown('<p class="section-label">Prêmio e Sinistro por Ramo</p>', unsafe_allow_html=True)
    st.dataframe(df_geral_ramo_exibicao, hide_index=True, use_container_width=True)
with c2:
    st.markdown('<p class="section-label">Sinistros por Cobertura</p>', unsafe_allow_html=True)
    # Formatação apenas para exibição
    df_disp_cob = df_sinistro_geral_cobertura.copy()
    df_disp_cob['Total Sinistro'] = df_disp_cob['Total Sinistro'].map(formatar_valor_br)
    st.dataframe(df_disp_cob, hide_index=True, use_container_width=True)

# exibir grafico de linhas ramos e pizza das coberturas
c1, c2 = st.columns(2)
with c1:
    st.markdown('<p class="section-label">Prêmio e Sinistro por Ramo</p>', unsafe_allow_html=True)
    st.plotly_chart(fig_ramo_geral, use_container_width=True, config={'displayModeBar': False})
with c2:
    st.markdown('<p class="section-label">Sinistros por Cobertura</p>', unsafe_allow_html=True)
    st.plotly_chart(fig_pizza_geral, use_container_width=True, config={'displayModeBar': False})

# ── Evolução da Sinistralidade (%) por Ramo ──────────────────────────────────
st.markdown('<p class="section-label">Evolução da Sinistralidade (%) por Ramo</p>', unsafe_allow_html=True)

df_ramo_ano = df_para_soma.groupby(['Ano Vigência', 'Ramo']).agg(
    Total_Premio=('Soma Prêmio Pago por Apolice', 'sum'),
    Total_Sinistro=('Soma Sinistro Por Apolice', 'sum')
).reset_index()
df_ramo_ano['Sinistralidade'] = df_ramo_ano.apply(
    lambda row: row['Total_Sinistro'] / row['Total_Premio'] if row['Total_Premio'] != 0 else 0, axis=1
)
df_ramo_ano['Ramo'] = df_ramo_ano['Ramo'].astype(str)

ramos_com_sin = df_ramo_ano[df_ramo_ano['Sinistralidade'] > 0]['Ramo'].unique()
df_ramo_ano = df_ramo_ano[df_ramo_ano['Ramo'].isin(ramos_com_sin)]

if not df_ramo_ano.empty:
    fig_sin_ramo_ano = go.Figure()
    for ramo in sorted(df_ramo_ano['Ramo'].unique()):
        df_r = df_ramo_ano[df_ramo_ano['Ramo'] == ramo].sort_values('Ano Vigência')
        fig_sin_ramo_ano.add_trace(go.Scatter(
            x=df_r['Ano Vigência'],
            y=df_r['Sinistralidade'],
            mode='lines+markers+text',
            name=f'Ramo {ramo}',
            text=df_r['Sinistralidade'].map(lambda x: f"{x:.1%}"),
            textposition='top center',
            textfont=dict(size=11),
            marker=dict(size=8),
            line=dict(width=2),
        ))
    fig_sin_ramo_ano.update_layout(
        xaxis=dict(title='Ano', tickmode='linear', dtick=1),
        yaxis=dict(title='Sinistralidade (%)', tickformat='.0%'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(t=40, b=20, l=0, r=0),
        height=400,
        hovermode='x unified'
    )
    fig_sin_ramo_ano.update_traces(hovertemplate='%{y:.2%}')
    st.plotly_chart(fig_sin_ramo_ano, use_container_width=True, config={'displayModeBar': False})
else:
    st.info("Sem dados suficientes para o gráfico de sinistralidade por ramo.")

# 5. Detalhamento por Ramos Específicos (23, 28, 82)
ramos_alvo = [23, 28, 82]
ramos_com_dados = []
for r in ramos_alvo:
    if not df_sinistro_periodo_atualizado[df_sinistro_periodo_atualizado['nr_ramo'] == r].empty:
        ramos_com_dados.append(r)

# Condição: Só executa o loop de plotagem se houver 2 ou mais ramos com informações
if len(ramos_com_dados) >= 2:
    for r in ramos_com_dados:
        df_r_especifico = df_sinistro_periodo_atualizado[df_sinistro_periodo_atualizado['nr_ramo'] == r]
        
        df_cob_r = df_r_especifico.groupby('Cobertura', as_index=False).agg(**{
            'Total Sinistro': ('Total Sinistro', 'sum'),
            'Qtd Sinistros': ('nr_sinistro', 'nunique')
        })
        
        col_t, col_g = st.columns(2)
        with col_t:
            st.markdown(f'<p class="section-label">Dados de Sinistro por Cobertura - Ramo {r}</p>', unsafe_allow_html=True)
            df_cob_r_view = df_cob_r.copy()
            df_cob_r_view['Total Sinistro'] = df_cob_r_view['Total Sinistro'].map(formatar_valor_br)
            st.dataframe(df_cob_r_view, hide_index=True, use_container_width=True)
            
        with col_g:
            st.markdown(f'<p class="section-label">Gráfico Sinistro Por Cobertura - Ramo {r}</p>', unsafe_allow_html=True)
            fig_r = px.pie(df_cob_r, values='Total Sinistro', names='Cobertura', hole=0.4, height=300)
            fig_r.update_layout(
                margin=dict(t=20, b=20, l=0, r=0),
                annotations=[dict(text=f'{r}', x=0.5, y=0.5, font_size=15, showarrow=False)]
            )
            st.plotly_chart(fig_r, use_container_width=True, config={'displayModeBar': False})
# ============================================================================

def gerar_ranking_piores_avancado(df_base, coluna_agrupadora, limite_sinistralidade=0.50, min_apolices=2):
    """
    Calcula o Score de Criticidade 100 baseando-se em:
    - Volume Financeiro (30%)
    - Sinistralidade % (40%)
    - Frequência: Sinistros por Apólice (30%)
    """
    if df_base.empty:
        return pd.DataFrame()

    df_temp = df_base.copy()
    
    # Função interna para limpar valores que venham como string formatada
    def para_float(x):
        if isinstance(x, str):
            return float(x.replace('R$', '').replace('.', '').replace(',', '.').strip())
        return float(x)

    # Preparação dos dados numéricos
    df_temp['Premio_Num'] = df_temp['Soma Prêmio Pago por Apolice'].apply(para_float)
    df_temp['Sinistro_Num'] = df_temp['Soma Sinistro Por Apolice'].apply(para_float)

    # Agrupamento por Entidade (Segurado/Corretor/Representante)
    ranking = df_temp.groupby(coluna_agrupadora).agg(
        Total_Premio=('Premio_Num', 'sum'),
        Total_Sinistro=('Sinistro_Num', 'sum'),
        Qtd_Apolices=('N° Apólice', 'nunique'),
        # Contamos quantas apólices tiveram valor de sinistro > 0
        Qtd_Sinistros=('Sinistro_Num', lambda x: (x > 0).sum())
    ).reset_index()

    # Cálculo da Sinistralidade Real
    ranking['% Sinistralidade'] = ranking.apply(
        lambda x: x['Total_Sinistro'] / x['Total_Premio'] if x['Total_Premio'] > 0 else 0, axis=1
    )

    # FILTROS DE RELEVÂNCIA:
    # Removemos quem está "dentro da meta" e quem tem pouquíssimas apólices (evita casos isolados)
    ranking_filtrado = ranking[
        (ranking['% Sinistralidade'] > limite_sinistralidade) & 
        (ranking['Qtd_Apolices'] >= min_apolices)
    ].copy()

    if ranking_filtrado.empty:
        return pd.DataFrame()

    # CÁLCULO DA FREQUÊNCIA (Sinistros por Apólice)
    ranking_filtrado['Frequencia_Relativa'] = ranking_filtrado['Qtd_Sinistros'] / ranking_filtrado['Qtd_Apolices']

    # NORMALIZAÇÃO PARA O SCORE (0 a 1)
    def normalizar(serie):
        if (serie.max() - serie.min()) == 0: return 1.0
        return (serie - serie.min()) / (serie.max() - serie.min())

    # Pesos: 30% Volume, 40% Sinistralidade, 30% Frequência
    ranking_filtrado['Score'] = (
        (normalizar(ranking_filtrado['Total_Sinistro']) * 0.3) +
        (normalizar(ranking_filtrado['% Sinistralidade']) * 0.4) +
        (normalizar(ranking_filtrado['Frequencia_Relativa']) * 0.3)
    ) * 100

    # Ordenar pelos "Piores" (maior Score)
    ranking_filtrado = ranking_filtrado.sort_values(by='Score', ascending=False).head(10)

    # Formatação Final para exibição
    ranking_final = ranking_filtrado.copy()
    ranking_final['Total_Premio'] = ranking_final['Total_Premio'].apply(formatar_valor_br)
    ranking_final['Total_Sinistro'] = ranking_final['Total_Sinistro'].apply(formatar_valor_br)
    ranking_final['% Sinistralidade'] = ranking_final['% Sinistralidade'].map(lambda x: f"{x:.2%}")
    ranking_final['Score'] = ranking_final['Score'].map('{:,.1f}'.format)
    
    return ranking_final[[coluna_agrupadora, 'Qtd_Apolices', 'Qtd_Sinistros', 'Total_Premio', 'Total_Sinistro', '% Sinistralidade', 'Score']]

if not df_geral_periodo.empty:
    # 1. Prepara os dados numéricos
    df_regiao = df_geral_periodo.copy()
    df_regiao['Soma Prêmio Pago por Apolice'] = df_regiao['Soma Prêmio Pago por Apolice'].str.replace('.', '').str.replace(',', '.').astype(float)
    df_regiao['Soma Sinistro Por Apolice']    = df_regiao['Soma Sinistro Por Apolice'].str.replace('.', '').str.replace(',', '.').astype(float)

    # 2. Agrupamento por Região de Circulação
    groupby_regiao = df_regiao.groupby('Região de Circulação').agg(
        Qtd_Apolices=('N° Apólice', 'nunique'),
        Total_Premio=('Soma Prêmio Pago por Apolice', 'sum'),
        Total_Sinistro=('Soma Sinistro Por Apolice', 'sum')
    ).reset_index()

    # 3. Cruzamento com sinistros para Qtd_Sinistros
    df_sin_regiao_contagem = df_sinistro_periodo_atualizado.merge(
        df_regiao[['N° Apólice', 'Região de Circulação']],
        on='N° Apólice', how='left'
    )
    qtd_sin_regiao = df_sin_regiao_contagem.groupby('Região de Circulação')['nr_sinistro'].nunique().reset_index()
    qtd_sin_regiao.rename(columns={'nr_sinistro': 'Qtd_Sinistros'}, inplace=True)

    # 4. Merge e cálculos
    groupby_regiao = pd.merge(groupby_regiao, qtd_sin_regiao, on='Região de Circulação', how='left').fillna(0)
    groupby_regiao['Qtd_Sinistros']      = groupby_regiao['Qtd_Sinistros'].astype(int)
    groupby_regiao['Sinistralidade_Num'] = groupby_regiao.apply(
        lambda row: row['Total_Sinistro'] / row['Total_Premio'] if row['Total_Premio'] != 0 else 0, axis=1
    )

    # 5. DF de exibição formatado — ordenado por maior sinistralidade
    df_regiao_view = groupby_regiao.sort_values('Sinistralidade_Num', ascending=False).copy()
    df_regiao_view['% Sinistralidade'] = df_regiao_view['Sinistralidade_Num'].map(lambda x: f"{x:.2%}")
    df_regiao_view['Total_Premio']     = df_regiao_view['Total_Premio'].map(formatar_valor_br)
    df_regiao_view['Total_Sinistro']   = df_regiao_view['Total_Sinistro'].map(formatar_valor_br)
    df_regiao_view = df_regiao_view[
        ['Região de Circulação', 'Qtd_Apolices', 'Qtd_Sinistros', 'Total_Premio', 'Total_Sinistro', '% Sinistralidade']
    ]

    # ── BLOCO 1: DF regiões (esq) + Gráfico Top 10 piores (dir) ──────────────
    col_reg_df, col_reg_graf = st.columns(2)

    with col_reg_df:
        st.markdown('<p class="section-label">Prêmio e Sinistro por Região de Circulação</p>', unsafe_allow_html=True)
        st.dataframe(df_regiao_view, hide_index=True, use_container_width=True)

    with col_reg_graf:
        st.markdown('<p class="section-label">Top 10 Piores Regiões — Sinistralidade (%)</p>', unsafe_allow_html=True)
        # Top 10 piores regiões — barras horizontais escala Reds
        df_top10 = groupby_regiao[groupby_regiao['Sinistralidade_Num'] > 0].copy()
        df_top10 = df_top10.sort_values('Sinistralidade_Num', ascending=False).head(10)
        df_top10['% Sin Label'] = df_top10['Sinistralidade_Num'].map(lambda x: f"{x:.2%}")
        df_top10 = df_top10.sort_values('Sinistralidade_Num', ascending=True)

        if not df_top10.empty:
            fig_top10 = px.bar(
                df_top10,
                x='Sinistralidade_Num',
                y='Região de Circulação',
                orientation='h',
                text='% Sin Label',
                labels={'Sinistralidade_Num': 'Sinistralidade (%)'},
                color='Sinistralidade_Num',
                color_continuous_scale='Reds',
            )
            fig_top10.update_traces(
                textposition='outside',
                hovertemplate="Região: %{y}<br>Sinistralidade: %{text}"
            )
            fig_top10.update_layout(
                # title="Top 10 Piores Regiões — Sinistralidade (%)",
                xaxis_title="Sinistralidade (%)",
                yaxis_title="",
                coloraxis_showscale=False,
                margin=dict(l=0, r=80, t=40, b=0),
                height=420,
            )
            st.plotly_chart(fig_top10, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Sem regiões com sinistro no período selecionado.")

    # ── BLOCO 2: DF por UF (esq) + Mapa de calor (dir) ───────────────────────
    groupby_regiao['UF'] = groupby_regiao['Região de Circulação'].str[:2].str.strip()
    df_uf = groupby_regiao.groupby('UF').agg(
        Total_Premio=('Total_Premio', 'sum'),
        Total_Sinistro=('Total_Sinistro', 'sum'),
        Qtd_Apolices=('Qtd_Apolices', 'sum'),
        Qtd_Sinistros=('Qtd_Sinistros', 'sum')
    ).reset_index()
    df_uf['Sinistralidade_UF'] = df_uf.apply(
        lambda row: row['Total_Sinistro'] / row['Total_Premio'] if row['Total_Premio'] != 0 else 0, axis=1
    )

    col_uf_df, col_uf_mapa = st.columns(2)

    with col_uf_df:
        st.markdown('<p class="section-label">Sinistralidade por UF</p>', unsafe_allow_html=True)
        df_uf_view = df_uf.sort_values('Sinistralidade_UF', ascending=False).copy()
        df_uf_view['% Sinistralidade'] = df_uf_view['Sinistralidade_UF'].map(lambda x: f"{x:.2%}")
        df_uf_view['Total_Premio']     = df_uf_view['Total_Premio'].map(formatar_valor_br)
        df_uf_view['Total_Sinistro']   = df_uf_view['Total_Sinistro'].map(formatar_valor_br)
        df_uf_view = df_uf_view[
            ['UF', 'Qtd_Apolices', 'Qtd_Sinistros', 'Total_Premio', 'Total_Sinistro', '% Sinistralidade']
        ]
        st.dataframe(df_uf_view, hide_index=True, use_container_width=True)

    with col_uf_mapa:
        st.markdown('<p class="section-label">Mapa de Calor</p>', unsafe_allow_html=True)
        df_uf_mapa = df_uf.copy()
        df_uf_mapa['Sin_Pct']      = df_uf_mapa['Sinistralidade_UF'].map(lambda x: f"{x:.2%}")
        df_uf_mapa['Premio_fmt']   = df_uf_mapa['Total_Premio'].apply(formatar_valor_br)
        df_uf_mapa['Sinistro_fmt'] = df_uf_mapa['Total_Sinistro'].apply(formatar_valor_br)

        fig_mapa = px.choropleth(
            df_uf_mapa,
            geojson="https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
            locations='UF',
            featureidkey='properties.sigla',
            color='Sinistralidade_UF',
            color_continuous_scale='Reds',
            hover_name='UF',
            hover_data={
                'Sinistralidade_UF': False,
                'Sin_Pct': True,
                'Premio_fmt': True,
                'Sinistro_fmt': True,
                'Qtd_Apolices': True,
            },
            labels={
                'Sin_Pct': 'Sinistralidade',
                'Premio_fmt': 'Prêmio',
                'Sinistro_fmt': 'Sinistro',
                'Qtd_Apolices': 'Qtd Apólices',
            },
        )
        fig_mapa.update_geos(fitbounds="locations", visible=False)
        fig_mapa.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=420,
            coloraxis_colorbar=dict(
                title="Sinistralidade",
                tickformat=".0%",
                len=0.75
            )
        )
        st.plotly_chart(fig_mapa, use_container_width=True, config={'displayModeBar': False})
else:
    st.info("Nenhum dado disponível para agrupar por Região de Circulação.")

# --- SEÇÃO DE RANKING DE CRITICIDADE 🚩---
st.write("---")
st.subheader("⚠️ Análise de Criticidade (Top 10 Piores Resultados)")
st.text("""
Critério do Score (0-100): O ranking considera o impacto financeiro - total de sinistro (Peso 30%), a taxa de sinistralidade (Peso 40%) e a frequência de sinistros por apólice (Peso 30%). 
Filtro aplicado: Mínimo de 2 apólices e sinistralidade acima de 50%.
""")
# st.info("""
# **Critério do Score (0-100):** O ranking considera o impacto financeiro - total de sinistro (Peso 30%), a taxa de sinistralidade (Peso 40%) e a frequência de sinistros por apólice (Peso 30%). 
# *Filtro aplicado: Mínimo de 2 apólices e sinistralidade acima de 50%.*
# """)

# Geramos os rankings usando o DataFrame já filtrado pelo Slider de Ano (df_geral_periodo)
piores_seg = gerar_ranking_piores_avancado(df_geral_periodo, 'Segurado')
piores_cor = gerar_ranking_piores_avancado(df_geral_periodo, 'Corretor')
piores_rep = gerar_ranking_piores_avancado(df_geral_periodo, 'Representante')

# Interface em Abas para não ocupar muito espaço vertical
tab_seg, tab_cor, tab_rep = st.tabs(["Segurados Críticos", "Corretores Críticos", "Representantes Críticos"])

with tab_seg:
    if not piores_seg.empty:
        st.dataframe(piores_seg, hide_index=True, use_container_width=True)
    else:
        st.success("Nenhum segurado crítico identificado nos parâmetros atuais.")

with tab_cor:
    if not piores_cor.empty:
        st.dataframe(piores_cor, hide_index=True, use_container_width=True)
    else:
        st.success("Nenhum corretor crítico identificado nos parâmetros atuais.")

with tab_rep:
    if not piores_rep.empty:
        st.dataframe(piores_rep, hide_index=True, use_container_width=True)
    else:
        st.success("Nenhum representante crítico identificado nos parâmetros atuais.")


# =========== ranking dos 10 maiores por Volume de Prêmio e Quantidade de Emissões.============

def gerar_ranking_producao(df_base, coluna_agrupadora):
    """
    Gera o ranking dos 10 maiores por Volume de Prêmio, 
    incluindo dados de sinistro e % de sinistralidade.
    """
    if df_base.empty:
        return pd.DataFrame()

    df_temp = df_base.copy()
    
    # Conversão de valores para numérico (limpeza de strings se necessário)
    def para_float(x):
        if isinstance(x, str):
            return float(x.replace('R$', '').replace('.', '').replace(',', '.').strip())
        return float(x)

    df_temp['Premio_Num'] = df_temp['Soma Prêmio Pago por Apolice'].apply(para_float)
    df_temp['Sinistro_Num'] = df_temp['Soma Sinistro Por Apolice'].apply(para_float)

    # Agrupamento consolidado
    ranking = df_temp.groupby(coluna_agrupadora).agg(
        Qtd_Emissoes=('N° Apólice', 'nunique'),
        Total_Premio=('Premio_Num', 'sum'),
        Total_Sinistro=('Sinistro_Num', 'sum')
    ).reset_index()

    # Cálculo da Sinistralidade
    ranking['% Sinistralidade'] = ranking.apply(
        lambda x: x['Total_Sinistro'] / x['Total_Premio'] if x['Total_Premio'] > 0 else 0, axis=1
    )

    # Ordenação pelos maiores Prêmios
    ranking = ranking.sort_values(by='Total_Premio', ascending=False).head(10)

    # Formatação para o Streamlit
    ranking['Total_Premio'] = ranking['Total_Premio'].apply(formatar_valor_br)
    ranking['Total_Sinistro'] = ranking['Total_Sinistro'].apply(formatar_valor_br)
    ranking['% Sinistralidade'] = ranking['% Sinistralidade'].map(lambda x: f"{x:.2%}")
    
    return ranking

st.subheader("🏆 Top 10 Produção (Emissões e Prêmios)")
st.markdown('<p class="section-label">Este ranking destaca os parceiros com maior volume financeiro e quantidade de apólices emitidas.</p>', unsafe_allow_html=True)
# st.info("Este ranking destaca os parceiros com maior volume financeiro e quantidade de apólices emitidas.")

# Gerar os rankings de produção com a nova função
prod_seg = gerar_ranking_producao(df_geral_periodo, 'Segurado')
prod_cor = gerar_ranking_producao(df_geral_periodo, 'Corretor')
prod_rep = gerar_ranking_producao(df_geral_periodo, 'Representante')

# Interface em Abas
tab_p_seg, tab_p_cor, tab_p_rep = st.columns(3)

with tab_p_seg:
    st.markdown('<p class="section-label">Top Segurados</p>', unsafe_allow_html=True)
    if not prod_seg.empty:
        st.dataframe(
            prod_seg,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Segurado":        st.column_config.Column(width=180),
                "Qtd_Emissoes":    st.column_config.Column(width=50),
                "Total_Premio":    st.column_config.Column(width=100),
                "Total_Sinistro":  st.column_config.Column(width=100),
                "% Sinistralidade": st.column_config.Column(width=50),
            })
    else:
        st.warning("Sem dados de produção.")

with tab_p_cor:
    st.markdown('<p class="section-label">Top Corretores</p>', unsafe_allow_html=True)
    if not prod_cor.empty:
        st.dataframe(
            prod_cor,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Corretor":        st.column_config.Column(width=180),
                "Qtd_Emissoes":    st.column_config.Column(width=50),
                "Total_Premio":    st.column_config.Column(width=100),
                "Total_Sinistro":  st.column_config.Column(width=100),
                "% Sinistralidade": st.column_config.Column(width=50),
            })
    else:
        st.warning("Sem dados de produção.")

with tab_p_rep:
    st.markdown('<p class="section-label">Top Representantes</p>', unsafe_allow_html=True)
    if not prod_rep.empty:
        st.dataframe(
            prod_rep,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Representante":        st.column_config.Column(width=180),
                "Qtd_Emissoes":    st.column_config.Column(width=50),
                "Total_Premio":    st.column_config.Column(width=100),
                "Total_Sinistro":  st.column_config.Column(width=100),
                "% Sinistralidade": st.column_config.Column(width=50),
            })
    else:
        st.warning("Sem dados de produção.")



# ── BLOCO: Frequência × Severidade por Ano ───────────────────────────────────
st.write("---")
st.subheader("🔬 Decomposição: Frequência × Severidade por Ano")
st.caption("Entenda SE a sinistralidade piora por mais sinistros (frequência) ou por sinistros maiores (severidade).")

if not df_sinistro_periodo_atualizado.empty and not df_geral_periodo.empty:
    df_fs = df_sinistro_periodo_atualizado.copy()
    # usa df_para_soma (filtrado + slider, mesma base do Desempenho Consolidado)
    df_apo_fs = df_para_soma.copy()
    qtd_apo_ano = df_apo_fs.groupby('Ano Vigência').agg(
        Qtd_Apolices=('N° Apólice','nunique')
    ).reset_index().rename(columns={'Ano Vigência':'Ano'})

    df_fs_ano = df_fs.groupby('Ano Vigência').agg(
        Qtd_Sinistros=('nr_sinistro','nunique'),
        Total_Sinistro=('Total Sinistro','sum')
    ).reset_index().rename(columns={'Ano Vigência':'Ano'}) if 'Ano Vigência' in df_fs.columns else pd.DataFrame()

    if df_fs_ano.empty:
        if 'dt_aviso_dt' not in df_fs.columns:
            df_fs['dt_aviso_dt'] = pd.to_datetime(df_fs['dt_aviso'], dayfirst=True, errors='coerce')
        df_fs_merged = pd.merge(df_fs, df_apo_fs[['N° Apólice','Ano Vigência']].drop_duplicates(), on='N° Apólice', how='left')
        df_fs_ano = df_fs_merged.groupby('Ano Vigência').agg(
            Qtd_Sinistros=('nr_sinistro','nunique'),
            Total_Sinistro=('Total Sinistro','sum')
        ).reset_index().rename(columns={'Ano Vigência':'Ano'})

    df_fs_ano = pd.merge(df_fs_ano, qtd_apo_ano, on='Ano', how='inner')
    df_fs_ano = df_fs_ano[df_fs_ano['Qtd_Apolices'] > 0].copy()
    df_fs_ano['Frequencia']  = df_fs_ano['Qtd_Sinistros'] / df_fs_ano['Qtd_Apolices']
    df_fs_ano['Severidade']  = df_fs_ano.apply(
        lambda r: r['Total_Sinistro'] / r['Qtd_Sinistros'] if r['Qtd_Sinistros'] > 0 else 0, axis=1
    )
    df_fs_ano = df_fs_ano.sort_values('Ano')

    if not df_fs_ano.empty:
        col_fs1, col_fs2 = st.columns(2)

        with col_fs1:
            st.markdown("**Frequência de Sinistros por Apólice (sinistros/apólice/ano)**")
            import numpy as np
            fig_freq_ano = go.Figure()
            fig_freq_ano.add_trace(go.Scatter(
                x=df_fs_ano['Ano'], y=df_fs_ano['Frequencia'],
                mode='lines+markers+text',
                text=df_fs_ano['Frequencia'].map(lambda x: f"{x:.2f}"),
                textposition='top center', textfont=dict(size=10),
                marker=dict(size=8, color='#1A56A0'), line=dict(width=2.5, color='#1A56A0'),
                name='Frequência'
            ))
            # Linha de tendência
            if len(df_fs_ano) >= 3:
                coef_f = np.polyfit(df_fs_ano['Ano'].values, df_fs_ano['Frequencia'].values, 1)
                tend_f = np.polyval(coef_f, df_fs_ano['Ano'].values)
                fig_freq_ano.add_trace(go.Scatter(
                    x=df_fs_ano['Ano'], y=tend_f,
                    mode='lines', name='Tendência',
                    line=dict(color='red', width=2, dash='dash')
                ))
            fig_freq_ano.update_layout(
                xaxis=dict(title='Ano', tickmode='linear', dtick=1),
                yaxis=dict(title='Sinistros por Apólice'),
                legend=dict(orientation='h', y=1.15),
                margin=dict(t=20, b=20, l=0, r=0), height=340,
                hovermode='x unified'
            )
            st.plotly_chart(fig_freq_ano, use_container_width=True, config={'displayModeBar': False})

            if len(df_fs_ano) >= 2:
                var_freq = (df_fs_ano['Frequencia'].iloc[-1] - df_fs_ano['Frequencia'].iloc[-2]) / df_fs_ano['Frequencia'].iloc[-2] * 100
                if var_freq > 10:
                    st.error(f"📈 Frequência subindo {var_freq:+.1f}% — mais sinistros por apólice. Risco de seleção adversa.")
                elif var_freq < -10:
                    st.success(f"📉 Frequência caindo {var_freq:+.1f}% — menos sinistros por apólice.")
                else:
                    st.info(f"➡ Frequência estável ({var_freq:+.1f}% vs ano anterior).")

        with col_fs2:
            st.markdown("**Severidade Média por Sinistro (R$ médio por evento)**")
            fig_sev_ano = go.Figure()
            fig_sev_ano.add_trace(go.Scatter(
                x=df_fs_ano['Ano'], y=df_fs_ano['Severidade'],
                mode='lines+markers+text',
                text=df_fs_ano['Severidade'].map(lambda x: f"R${x/1000:.1f}k"),
                textposition='top center', textfont=dict(size=10),
                marker=dict(size=8, color='#F59E0B'), line=dict(width=2.5, color='#F59E0B'),
                name='Severidade'
            ))
            if len(df_fs_ano) >= 3:
                coef_s = np.polyfit(df_fs_ano['Ano'].values, df_fs_ano['Severidade'].values, 1)
                tend_s = np.polyval(coef_s, df_fs_ano['Ano'].values)
                fig_sev_ano.add_trace(go.Scatter(
                    x=df_fs_ano['Ano'], y=tend_s,
                    mode='lines', name='Tendência',
                    line=dict(color='red', width=2, dash='dash')
                ))
            fig_sev_ano.update_layout(
                xaxis=dict(title='Ano', tickmode='linear', dtick=1),
                yaxis=dict(title='R$ por Sinistro'),
                legend=dict(orientation='h', y=1.15),
                margin=dict(t=20, b=20, l=0, r=0), height=340,
                hovermode='x unified'
            )
            st.plotly_chart(fig_sev_ano, use_container_width=True, config={'displayModeBar': False})

            if len(df_fs_ano) >= 2:
                var_sev = (df_fs_ano['Severidade'].iloc[-1] - df_fs_ano['Severidade'].iloc[-2]) / df_fs_ano['Severidade'].iloc[-2] * 100
                if var_sev > 10:
                    st.error(f"📈 Severidade subindo {var_sev:+.1f}% — sinistros mais caros. Avaliar aumento de franquia.")
                elif var_sev < -10:
                    st.success(f"📉 Severidade caindo {var_sev:+.1f}% — sinistros menores.")
                else:
                    st.info(f"➡ Severidade estável ({var_sev:+.1f}% vs ano anterior).")

        # Diagnóstico combinado
        st.markdown("**📋 Diagnóstico Combinado**")
        if len(df_fs_ano) >= 2:
            subiu_freq = df_fs_ano['Frequencia'].iloc[-1] > df_fs_ano['Frequencia'].iloc[-2]
            subiu_sev  = df_fs_ano['Severidade'].iloc[-1]  > df_fs_ano['Severidade'].iloc[-2]
            if subiu_freq and subiu_sev:
                st.error("🔴 **Frequência E Severidade subindo** — deterioração ampla. Revisar critérios de aceitação e franquias.")
            elif subiu_freq and not subiu_sev:
                st.warning("🟡 **Mais sinistros, mas valores menores** — problema de seleção. Avaliar restrições de aceitação ou franquia por evento.")
            elif not subiu_freq and subiu_sev:
                st.warning("🟡 **Menos sinistros, mas mais caros** — eventos mais graves. Avaliar aumento de franquia mínima.")
            else:
                st.success("🟢 **Frequência e Severidade caindo** — melhora consistente da carteira.")
else:
    st.info("Nenhum dado disponível para análise de frequência e severidade.")

st.markdown("""
<div style="background:#F8FAFC;border-radius:10px;padding:18px;border:1px solid #E2E8F0;font-size:13px;color:#334155;">
<b>📖 Como entender esta análise</b><br><br>

<b>O que é:</b> A sinistralidade total pode subir por dois motivos completamente diferentes — porque ocorreram <i>mais sinistros</i> (frequência) ou porque cada sinistro ficou <i>mais caro</i> (severidade). Esta seção separa os dois efeitos para que a decisão de subscrição seja mais precisa.<br><br>

<b>Frequência</b> = Quantidade de sinistros ÷ Quantidade de apólices. Indica quantos sinistros ocorrem em média por apólice a cada ano. Se sobe, significa que mais segurados estão acionando o seguro — pode indicar seleção adversa (carteira com perfil de risco ruim) ou problema no critério de aceitação.<br><br>

<b>Severidade</b> = Total pago em sinistros ÷ Quantidade de sinistros. Indica o valor médio de cada sinistro. Se sobe, significa que os eventos estão ficando mais caros — pode refletir inflação de custos médicos/jurídicos, sinistros mais graves ou ausência de franquia adequada.<br><br>

<b>Como analisar:</b><br>
🔴 Frequência E Severidade subindo → problema amplo, revisar critérios de aceitação E franquias simultaneamente.<br>
🟡 Só Frequência subindo → mais sinistros, mas valores controlados. Restringir aceitação ou aplicar franquia por evento.<br>
🟡 Só Severidade subindo → menos sinistros, mas mais caros. Aumentar franquia mínima ou limite de cobertura.<br>
🟢 Ambas caindo → carteira saudável.<br><br>

<b>Como foi desenvolvido:</b> Agrupa os dados por Ano de Vigência da Apólice. A frequência usa quantidade de sinistros únicos (nr_sinistro) dividida pela quantidade de apólices únicas. A severidade usa o Total Sinistro (sinistro + despesa + honorário - salvado) dividido pela quantidade de sinistros. A linha tracejada vermelha é uma regressão linear simples sobre os anos disponíveis. Os alertas automáticos comparam o último ano completo com o penúltimo.
</div>
""", unsafe_allow_html=True)


# ── BLOCO: Desenvolvimento por Safra ─────────────────────────────────────────
st.write("---")
st.subheader("📊 Desenvolvimento da Sinistralidade por Safra")
st.caption(
    "Mostra como a sinistralidade de cada ano de vigência evolui à medida que novos sinistros são avisados. "
    "Anos recentes com sinistralidade baixa podem estar incompletos — observe o padrão de maturação."
)

if not df_sinistro_periodo_atualizado.empty and not df_geral_periodo.empty:
    df_saf = df_sinistro_periodo_atualizado.copy()
    # Usa colunas de data pré-calculadas — evita pd.to_datetime repetido
    if 'dt_aviso_dt' not in df_saf.columns:
        df_saf['dt_aviso_dt'] = pd.to_datetime(df_saf['dt_aviso'], dayfirst=True, errors='coerce')
    if 'Ano_Aviso' not in df_saf.columns:
        df_saf['Ano_Aviso'] = df_saf['dt_aviso_dt'].dt.year

    # Junta Ano Vigência da apólice — usa df_para_soma (filtrado + slider, mesma base do Desempenho Consolidado)
    df_apo_saf = df_para_soma[['N° Apólice','Ano Vigência','Soma Prêmio Pago por Apolice']].drop_duplicates('N° Apólice').copy()
    df_apo_saf['Premio_Num'] = pd.to_numeric(df_apo_saf['Soma Prêmio Pago por Apolice'], errors='coerce').fillna(0)
    df_premio_saf = df_apo_saf.groupby('Ano Vigência')['Premio_Num'].sum().reset_index()
    df_premio_saf.columns = ['Ano_Vigencia', 'Premio']

    df_saf = pd.merge(df_saf, df_apo_saf[['N° Apólice','Ano Vigência']], on='N° Apólice', how='left')
    df_saf.rename(columns={'Ano Vigência': 'Ano_Vigencia'}, inplace=True)

    df_saf_grp = df_saf.groupby(['Ano_Vigencia','Ano_Aviso'])['Total Sinistro'].sum().reset_index()
    df_saf_grp = pd.merge(df_saf_grp, df_premio_saf, on='Ano_Vigencia', how='left')
    df_saf_grp = df_saf_grp[df_saf_grp['Premio'] > 0].copy()
    df_saf_grp['Sin_Acum'] = df_saf_grp.groupby('Ano_Vigencia')['Total Sinistro'].cumsum()
    df_saf_grp['Sin_Rate_Acum'] = df_saf_grp['Sin_Acum'] / df_saf_grp['Premio']
    df_saf_grp['Lag'] = df_saf_grp['Ano_Aviso'] - df_saf_grp['Ano_Vigencia']

    # Tabela pivot: safra vs lag
    anos_vigencia = sorted(df_saf_grp['Ano_Vigencia'].dropna().unique())
    anos_vigencia = [a for a in anos_vigencia if a >= max(anos_vigencia) - 8]
    max_lag = int(df_saf_grp['Lag'].max()) if not df_saf_grp.empty else 5

    pivot_data = []
    for av in anos_vigencia:
        row = {'Safra': int(av)}
        df_v = df_saf_grp[df_saf_grp['Ano_Vigencia'] == av].copy()
        for lag in range(0, min(max_lag+1, 8)):
            df_lag = df_v[df_v['Lag'] == lag]
            row[f'Ano+{lag}'] = f"{df_lag['Sin_Rate_Acum'].values[0]:.1%}" if not df_lag.empty else "—"
        pivot_data.append(row)

    df_pivot = pd.DataFrame(pivot_data)

    col_saf1, col_saf2 = st.columns([1, 1])

    with col_saf1:
        st.markdown("**Tabela de Desenvolvimento — Sinistralidade Acumulada por Safra**")
        st.dataframe(df_pivot, hide_index=True, use_container_width=True)
        st.caption("Ano+0 = sinistros avisados no próprio ano da vigência. Ano+1 = avisados 1 ano depois. '—' = ainda sem dados.")

    with col_saf2:
        st.markdown("**Curvas de Maturação por Safra**")
        fig_saf = go.Figure()
        cores = ['#1A56A0','#36A2EB','#F59E0B','#16A34A','#DC2626','#9333EA','#0891B2','#EA580C','#BE185D']
        for i, av in enumerate(anos_vigencia):
            df_v = df_saf_grp[df_saf_grp['Ano_Vigencia'] == av].sort_values('Lag')
            if df_v.empty: continue
            fig_saf.add_trace(go.Scatter(
                x=df_v['Lag'],
                y=df_v['Sin_Rate_Acum'],
                mode='lines+markers',
                name=str(int(av)),
                line=dict(width=2, color=cores[i % len(cores)]),
                marker=dict(size=6),
                hovertemplate=f"Safra {int(av)}<br>Ano de desenvolvimento: %{{x}}<br>Sin. Acum: %{{y:.1%}}<extra></extra>"
            ))
        fig_saf.update_layout(
            xaxis=dict(title='Anos após vigência (ano de desenvolvimento)', tickmode='linear', dtick=1),
            yaxis=dict(title='Sinistralidade Acumulada (%)', tickformat='.0%'),
            legend=dict(title='Safra', orientation='v', x=1.01),
            margin=dict(t=20, b=20, l=0, r=60), height=380,
            hovermode='x unified'
        )
        st.plotly_chart(fig_saf, use_container_width=True, config={'displayModeBar': False})
        st.caption(
            "Curvas que ainda sobem indicam safras em desenvolvimento — sinistros ainda estão sendo avisados. "
            "Safras recentes (direita com poucos pontos) tendem a ter sinistralidade subestimada."
        )


    # ── Chain-Ladder: Projeção da sinistralidade final por safra ─────────
    st.write("---")
    st.subheader("🔮 Projeção Chain-Ladder — Sinistralidade Final Estimada")
    st.caption(
        "Usa o padrão histórico de desenvolvimento das safras completas para projetar "
        "a sinistralidade final das safras recentes ainda em desenvolvimento."
    )

    import numpy as np

    # Monta matriz de sinistralidade acumulada: linhas=safra, colunas=lag
    lags_disponiveis = sorted(df_saf_grp['Lag'].unique())
    safras_disponiveis = sorted(df_saf_grp['Ano_Vigencia'].dropna().unique())

    # Matriz numérica de sinistralidade acumulada
    matriz = {}
    for av in safras_disponiveis:
        df_v = df_saf_grp[df_saf_grp['Ano_Vigencia'] == av].sort_values('Lag')
        for _, row in df_v.iterrows():
            matriz[(av, int(row['Lag']))] = row['Sin_Rate_Acum']

    max_lag = int(max(lags_disponiveis))

    # Calcula fatores de desenvolvimento (link ratios) por lag
    # Fator lag→lag+1 = média ponderada de (Acum_lag+1 / Acum_lag) nas safras que têm ambos
    fatores = {}
    for lag in range(0, max_lag):
        numerador   = 0.0
        denominador = 0.0
        for av in safras_disponiveis:
            v0 = matriz.get((av, lag),   None)
            v1 = matriz.get((av, lag+1), None)
            if v0 is not None and v1 is not None and v0 > 0:
                # Pondera pelo prêmio da safra para dar mais peso às safras maiores
                premio_saf = df_premio_saf[df_premio_saf['Ano_Vigencia'] == av]['Premio'].values
                peso = float(premio_saf[0]) if len(premio_saf) > 0 else 1.0
                numerador   += v1 * peso
                denominador += v0 * peso
        if denominador > 0:
            fatores[lag] = numerador / denominador

    # Projeta cada safra incompleta até o lag máximo observado
    ano_atual = int(df_saf_grp['Ano_Vigencia'].max())
    rows_proj = []

    for av in safras_disponiveis:
        av = int(av)
        # Encontra último lag disponível para esta safra
        lags_saf = [lag for lag in lags_disponiveis if (av, int(lag)) in matriz]
        if not lags_saf:
            continue
        ultimo_lag = int(max(lags_saf))
        sin_atual  = matriz.get((av, ultimo_lag), None)
        if sin_atual is None:
            continue

        # Projeta do último lag até o máximo
        sin_proj = sin_atual
        for lag in range(ultimo_lag, max_lag):
            f = fatores.get(lag, None)
            if f is not None:
                sin_proj *= f

        ja_completa = ultimo_lag >= max_lag
        fator_total  = sin_proj / sin_atual if sin_atual > 0 else 1.0

        rows_proj.append({
            'Safra':               av,
            'Sin. Atual':          sin_atual,
            'Sin. Projetada':      sin_proj,
            'Fator Desenvolvimento': fator_total,
            'Último Ano':          ultimo_lag,
            'Status':              'Completa' if ja_completa else f'Em dev. (ano {ultimo_lag}/{max_lag})'
        })

    df_proj = pd.DataFrame(rows_proj).sort_values('Safra', ascending=False)

    if not df_proj.empty:
        col_cl1, col_cl2 = st.columns(2)

        with col_cl1:
            st.markdown("**Tabela de Projeção por Safra**")
            df_proj_view = df_proj.copy()
            df_proj_view['Sin. Atual']     = df_proj_view['Sin. Atual'].map(lambda x: f"{x:.1%}")
            df_proj_view['Sin. Projetada'] = df_proj_view['Sin. Projetada'].map(lambda x: f"{x:.1%}")
            df_proj_view['Fator Desenvolvimento'] = df_proj_view['Fator Desenvolvimento'].map(lambda x: f"{x:.3f}×")
            st.dataframe(df_proj_view, hide_index=True, use_container_width=True)
            st.caption(
                "Fator Desenvolvimento = quanto ainda deve crescer a sinistralidade. "
                "1.000× = safra completa. 1.400× = ainda deve crescer 40%."
            )

        with col_cl2:
            st.markdown("**Comparativo: Sinistralidade Atual × Projetada**")
            df_inc = df_proj[df_proj['Status'] != 'Completa'].copy()
            df_comp = df_proj.copy()

            fig_cl = go.Figure()
            fig_cl.add_trace(go.Bar(
                x=df_comp['Safra'].astype(str),
                y=df_comp['Sin. Atual'],
                name='Sinistralidade Atual',
                marker_color='#36A2EB',
                text=df_comp['Sin. Atual'].map(lambda x: f"{x:.1%}"),
                textposition='outside'
            ))
            fig_cl.add_trace(go.Bar(
                x=df_comp['Safra'].astype(str),
                y=df_comp['Sin. Projetada'] - df_comp['Sin. Atual'],
                name='Incremento Projetado',
                marker_color='#FCA5A5',
                text=(df_comp['Sin. Projetada'] - df_comp['Sin. Atual']).map(
                    lambda x: f"+{x:.1%}" if x > 0.001 else ""
                ),
                textposition='outside',
                base=df_comp['Sin. Atual']
            ))
            fig_cl.update_layout(
                barmode='stack',
                xaxis=dict(title='Safra'),
                yaxis=dict(title='Sinistralidade (%)', tickformat='.0%'),
                legend=dict(orientation='h', y=1.15),
                margin=dict(t=20, b=20, l=0, r=0), height=380,
                hovermode='x unified'
            )
            st.plotly_chart(fig_cl, use_container_width=True, config={'displayModeBar': False})

        # Alerta da safra mais recente
        ultima_safra = df_proj[df_proj['Status'] != 'Completa'].sort_values('Safra', ascending=False)
        if not ultima_safra.empty:
            row_ult = ultima_safra.iloc[0]
            sin_at  = row_ult['Sin. Atual'] if isinstance(row_ult['Sin. Atual'], float) else float(str(row_ult['Sin. Atual']).replace('%',''))/100
            sin_pj  = row_ult['Sin. Projetada'] if isinstance(row_ult['Sin. Projetada'], float) else float(str(row_ult['Sin. Projetada']).replace('%',''))/100
            # Recupera numérico do df original
            sin_at_n  = df_proj[df_proj['Safra'] == row_ult['Safra']]['Sin. Atual'].values[0]
            sin_pj_n  = df_proj[df_proj['Safra'] == row_ult['Safra']]['Sin. Projetada'].values[0]
            incremento = sin_pj_n - sin_at_n

            if sin_pj_n > 0.80:
                st.error(
                    f"🔴 **Safra {int(row_ult['Safra'])}: sinistralidade atual de {sin_at_n:.1%} "
                    f"deve atingir {sin_pj_n:.1%} quando completa** (+{incremento:.1%} ainda a ser avisado). "
                    f"Risco elevado — avaliar reajuste preventivo nas renovações."
                )
            elif sin_pj_n > 0.60:
                st.warning(
                    f"🟡 **Safra {int(row_ult['Safra'])}: sinistralidade atual de {sin_at_n:.1%} "
                    f"deve atingir {sin_pj_n:.1%} quando completa** (+{incremento:.1%} ainda a ser avisado). "
                    f"Monitorar — possível necessidade de reajuste."
                )
            else:
                st.success(
                    f"🟢 **Safra {int(row_ult['Safra'])}: sinistralidade atual de {sin_at_n:.1%} "
                    f"deve atingir {sin_pj_n:.1%} quando completa** (+{incremento:.1%} ainda a ser avisado). "
                    f"Dentro de parâmetros aceitáveis."
                )

    # Fatores de desenvolvimento históricos
    with st.expander("📊 Ver fatores de desenvolvimento históricos (Chain-Ladder)"):
        fat_data = [{'Ano → Ano+1': f"Ano+{lag} → Ano+{lag+1}", 'Fator Médio': f"{v:.4f}×", 'Significado': f"A sinistralidade cresce em média {(v-1)*100:.1f}% entre esses dois períodos"} for lag, v in sorted(fatores.items())]
        if fat_data:
            st.dataframe(pd.DataFrame(fat_data), hide_index=True, use_container_width=True)
            st.caption("Fatores ponderados pelo prêmio de cada safra. Quanto mais próximo de 1.000×, mais estável o desenvolvimento naquele estágio.")


else:
    st.info("Nenhum dado disponível para análise de desenvolvimento por safra.")

st.markdown("""
<div style="background:#F8FAFC;border-radius:10px;padding:18px;border:1px solid #E2E8F0;font-size:13px;color:#334155;">
<b>📖 Como entender esta análise</b><br><br>

<b>O que é:</b> Uma apólice de 2022 pode gerar sinistros que só serão avisados em 2023, 2024 ou até 2025. Isso significa que olhar apenas a sinistralidade do ano corrente de uma safra recente pode ser enganoso — parte dos sinistros ainda não apareceu. Esta análise mostra como a sinistralidade de cada <i>safra</i> (ano de vigência) evolui ao longo do tempo à medida que novos sinistros são avisados.<br><br>

<b>Como ler a tabela:</b><br>
• <b>Safra</b> = Ano de vigência da apólice (ex: 2022)<br>
• <b>Ano+0</b> = Sinistralidade acumulada considerando apenas sinistros avisados no próprio ano da vigência<br>
• <b>Ano+1</b> = Sinistralidade acumulada incluindo sinistros avisados até 1 ano depois<br>
• <b>Ano+2</b> = Inclui sinistros avisados até 2 anos depois, e assim por diante<br>
• <b>—</b> = Dados ainda não disponíveis (safra recente, ainda em desenvolvimento)<br><br>

<b>Como analisar:</b><br>
Uma safra que mostra 30% em Ano+0 e chega a 66% em Ano+2 significa que dois terços dos sinistros foram avisados com atraso. Isso é normal em RCO — processos judiciais e regulações demoram. O padrão histórico das safras mais antigas (que já estão completas) indica quanto as safras recentes ainda devem crescer.<br><br>

<b>Atenção aos anos recentes:</b> Safras dos últimos 1-2 anos sempre parecem ter sinistralidade baixa, mas é porque ainda estão em desenvolvimento. Compare com o padrão das safras anteriores para estimar o valor final.<br><br>

<b>Como foi desenvolvido:</b> Para cada sinistro, identifica o Ano de Vigência da apólice correspondente e o Ano de Aviso do sinistro. Calcula o <i>ano de desenvolvimento</i> (em inglês: <i>lag</i>), que é a diferença em anos. Acumula o Total Sinistro por safra à medida que o ano de desenvolvimento aumenta e divide pelo prêmio total daquela safra. O gráfico de curvas mostra uma linha por safra — curvas que ainda sobem indicam safras incompletas.
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO DE ANÁLISE DE TENDÊNCIA 📈
# ══════════════════════════════════════════════════════════════════════════════
st.write("---")
st.subheader("📈 Análise de Tendência da Sinistralidade")
st.caption("Sinistralidade por Ano de Vigência da Apólice — mesma base do Desempenho Consolidado.")

if not df_sinistro_periodo_atualizado.empty and not df_geral_periodo.empty:

    # ── Prepara base de sinistros com datas (para gráficos mensais) ─────────
    df_sin_tend = df_sinistro_periodo_atualizado.copy()
    # Usa colunas de data pré-calculadas — evita pd.to_datetime repetido
    if 'dt_aviso_dt' not in df_sin_tend.columns:
        df_sin_tend['dt_aviso_dt'] = pd.to_datetime(df_sin_tend['dt_aviso'], dayfirst=True, errors='coerce')
    if 'AnoMes' not in df_sin_tend.columns:
        df_sin_tend['AnoMes'] = df_sin_tend['dt_aviso_dt'].dt.to_period('M').astype(str)
    # Renomeia para compatibilidade com o restante do bloco
    df_sin_tend['dt_aviso'] = df_sin_tend['dt_aviso_dt']

    # ── Sinistralidade anual — MESMA BASE do Desempenho Consolidado ───────────
    # Usa df_para_soma (filtrado + slider) para consistência total com os outros DFs
    df_apo_tend = df_para_soma.copy()
    df_apo_tend['Premio_Num']   = pd.to_numeric(df_apo_tend['Soma Prêmio Pago por Apolice'], errors='coerce').fillna(0)
    df_apo_tend['Sinistro_Num'] = pd.to_numeric(df_apo_tend['Soma Sinistro Por Apolice'],   errors='coerce').fillna(0)

    df_tend_ano = df_apo_tend.groupby('Ano Vigência').agg(
        Premio=('Premio_Num',   'sum'),
        Total_Sinistro=('Sinistro_Num', 'sum')
    ).reset_index()
    df_tend_ano.rename(columns={'Ano Vigência': 'Ano'}, inplace=True)
    df_tend_ano = df_tend_ano[df_tend_ano['Premio'] > 0].copy()
    df_tend_ano['Sinistralidade'] = df_tend_ano['Total_Sinistro'] / df_tend_ano['Premio']
    df_tend_ano = df_tend_ano[df_tend_ano['Ano'] >= df_tend_ano['Ano'].max() - 9]  # últimos 10 anos

    # Sinistro por mês (últimos 24 meses)
    df_sin_mes = df_sin_tend.groupby('AnoMes').agg(
        Total_Sinistro=('Total Sinistro', 'sum'),
        Qtd_Sinistros=('nr_sinistro', 'nunique')
    ).reset_index().sort_values('AnoMes')
    df_sin_mes = df_sin_mes.tail(24).copy()
    df_sin_mes['MM3'] = df_sin_mes['Total_Sinistro'].rolling(3).mean()
    df_sin_mes['MM6'] = df_sin_mes['Total_Sinistro'].rolling(6).mean()

    # ── Linha 1: Sinistralidade anual + linha de tendência ───────────────────
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown("**Sinistralidade % Anual com Tendência Linear**")
        if len(df_tend_ano) >= 3:
            import numpy as np
            anos_num = df_tend_ano['Ano'].values
            sin_vals  = df_tend_ano['Sinistralidade'].values
            coef = np.polyfit(anos_num, sin_vals, 1)
            tendencia_vals = np.polyval(coef, anos_num)
            direcao = "📈 Subindo" if coef[0] > 0.01 else ("📉 Caindo" if coef[0] < -0.01 else "➡ Estável")
            variacao_pct = (tendencia_vals[-1] - tendencia_vals[0]) / abs(tendencia_vals[0]) * 100 if tendencia_vals[0] != 0 else 0

            fig_tend = go.Figure()
            fig_tend.add_trace(go.Scatter(
                x=df_tend_ano['Ano'], y=df_tend_ano['Sinistralidade'],
                mode='lines+markers+text',
                name='Sinistralidade Real',
                text=df_tend_ano['Sinistralidade'].map(lambda x: f"{x:.1%}"),
                textposition='top center', textfont=dict(size=10),
                marker=dict(size=8, color='#1A56A0'), line=dict(width=2.5, color='#1A56A0')
            ))
            fig_tend.add_trace(go.Scatter(
                x=df_tend_ano['Ano'], y=tendencia_vals,
                mode='lines', name=f'Tendência ({direcao})',
                line=dict(color='red', width=2, dash='dash'),
            ))
            fig_tend.update_layout(
                xaxis=dict(title='Ano', tickmode='linear', dtick=1),
                yaxis=dict(title='Sinistralidade (%)', tickformat='.0%'),
                legend=dict(orientation='h', y=1.15),
                margin=dict(t=20, b=20, l=0, r=0), height=360,
                hovermode='x unified'
            )
            st.plotly_chart(fig_tend, use_container_width=True, config={'displayModeBar': False})

            # Alerta de tendência
            if coef[0] > 0.05:
                st.error(f"⚠️ **Tendência de alta acelerada** — sinistralidade cresceu ~{variacao_pct:.1f}% no período. Avaliar aumento de prêmio.")
            elif coef[0] > 0.01:
                st.warning(f"⚠️ **Tendência de alta moderada** — sinistralidade cresceu ~{variacao_pct:.1f}% no período. Monitorar.")
            elif coef[0] < -0.01:
                st.success(f"✅ **Tendência de queda** — sinistralidade caiu ~{abs(variacao_pct):.1f}% no período. Bom resultado.")
            else:
                st.info("➡️ **Sinistralidade estável** no período analisado.")
        else:
            st.info("Dados insuficientes para calcular tendência (mínimo 3 anos).")

    with col_t2:
        st.markdown("**Evolução Mensal do Sinistro — Últimos 24 Meses**")
        fig_mes = go.Figure()
        fig_mes.add_trace(go.Bar(
            x=df_sin_mes['AnoMes'], y=df_sin_mes['Total_Sinistro'],
            name='Sinistro Mensal', marker_color='#CBD5E1', opacity=0.7
        ))
        fig_mes.add_trace(go.Scatter(
            x=df_sin_mes['AnoMes'], y=df_sin_mes['MM3'],
            mode='lines', name='Média Móvel 3M',
            line=dict(color='#1A56A0', width=2.5)
        ))
        fig_mes.add_trace(go.Scatter(
            x=df_sin_mes['AnoMes'], y=df_sin_mes['MM6'],
            mode='lines', name='Média Móvel 6M',
            line=dict(color='red', width=2, dash='dot')
        ))
        fig_mes.update_layout(
            xaxis=dict(title='', tickangle=-45, tickfont=dict(size=9)),
            yaxis=dict(title='R$ Sinistro'),
            legend=dict(orientation='h', y=1.15),
            margin=dict(t=20, b=60, l=0, r=0), height=360,
            hovermode='x unified', barmode='overlay'
        )
        st.plotly_chart(fig_mes, use_container_width=True, config={'displayModeBar': False})

    # ── Linha 2: Frequência mensal + Indicador de necessidade de reajuste ────
    col_t3, col_t4 = st.columns(2)

    with col_t3:
        st.markdown("**Frequência de Sinistros por Mês — Últimos 24 Meses**")
        df_sin_mes['MM3_Qtd'] = df_sin_mes['Qtd_Sinistros'].rolling(3).mean()
        fig_freq = go.Figure()
        fig_freq.add_trace(go.Bar(
            x=df_sin_mes['AnoMes'], y=df_sin_mes['Qtd_Sinistros'],
            name='Qtd Sinistros', marker_color='#FCA5A5', opacity=0.75
        ))
        fig_freq.add_trace(go.Scatter(
            x=df_sin_mes['AnoMes'], y=df_sin_mes['MM3_Qtd'],
            mode='lines', name='Média Móvel 3M',
            line=dict(color='#DC2626', width=2.5)
        ))
        fig_freq.update_layout(
            xaxis=dict(title='', tickangle=-45, tickfont=dict(size=9)),
            yaxis=dict(title='Qtd Sinistros'),
            legend=dict(orientation='h', y=1.15),
            margin=dict(t=20, b=60, l=0, r=0), height=340,
            hovermode='x unified'
        )
        st.plotly_chart(fig_freq, use_container_width=True, config={'displayModeBar': False})

    with col_t4:
        st.markdown("**Painel de Indicadores — Necessidade de Reajuste de Prêmio**")
        if len(df_tend_ano) >= 2:
            import numpy as np
            # Indicadores calculados
            # Exclui o ano atual se estiver incompleto (ano corrente com poucos meses)
            import datetime
            ano_atual = datetime.datetime.now().year
            df_tend_completo = df_tend_ano[df_tend_ano['Ano'] < ano_atual].copy()
            # Se não houver dados suficientes sem o ano atual, usa tudo
            if len(df_tend_completo) < 3:
                df_tend_completo = df_tend_ano.copy()

            anos_rec = df_tend_completo.tail(3)
            sin_media_3a = anos_rec['Sinistralidade'].mean()
            sin_ultimo   = df_tend_completo.iloc[-1]['Sinistralidade']
            sin_anterior = df_tend_completo.iloc[-2]['Sinistralidade']
            variacao_yoy = (sin_ultimo - sin_anterior) / sin_anterior * 100 if sin_anterior != 0 else 0

            coef2 = np.polyfit(df_tend_ano['Ano'].values, df_tend_ano['Sinistralidade'].values, 1)
            aceleracao = coef2[0] * 100  # % ao ano

            # Ticket médio por sinistro (últimos 12 meses)
            _data_max_tk = df_sin_tend['dt_aviso'].max()
            _corte_12m = _data_max_tk - pd.DateOffset(months=12)
            _corte_24m = _data_max_tk - pd.DateOffset(months=24)
            df_12m = df_sin_tend[df_sin_tend['dt_aviso'] >= _corte_12m]
            ticket_medio = df_12m['Total Sinistro'].sum() / max(df_12m['nr_sinistro'].nunique(), 1)

            # Ticket médio dos 12 meses ANTERIORES (meses 13 a 24) — janela mais
            # madura, menos afetada pela demora no aviso/envio dos sinistros recentes
            df_12m_ant = df_sin_tend[
                (df_sin_tend['dt_aviso'] >= _corte_24m) & (df_sin_tend['dt_aviso'] < _corte_12m)
            ]
            ticket_medio_ant = df_12m_ant['Total Sinistro'].sum() / max(df_12m_ant['nr_sinistro'].nunique(), 1)
            _var_ticket = ((ticket_medio - ticket_medio_ant) / ticket_medio_ant * 100) if ticket_medio_ant > 0 else 0

            # Score de reajuste (0 = sem necessidade, 100 = urgente)
            score = 0
            if sin_media_3a > 0.80: score += 40
            elif sin_media_3a > 0.60: score += 20
            elif sin_media_3a > 0.40: score += 10

            if variacao_yoy > 20: score += 30
            elif variacao_yoy > 10: score += 15
            elif variacao_yoy > 0: score += 5

            if aceleracao > 0.05: score += 30
            elif aceleracao > 0.02: score += 15

            score = min(score, 100)

            # Cor do score
            if score >= 70:
                cor_score = "#DC2626"
                veredicto = "🔴 REAJUSTE URGENTE"
                desc = "Sinistralidade elevada com tendência de alta. Necessário reajuste imediato de prêmio."
            elif score >= 40:
                cor_score = "#F59E0B"
                veredicto = "🟡 REAJUSTE RECOMENDADO"
                desc = "Tendência de deterioração identificada. Avaliar reajuste preventivo."
            else:
                cor_score = "#16A34A"
                veredicto = "🟢 PRÊMIO ADEQUADO"
                desc = "Sinistralidade dentro de parâmetros aceitáveis."

            st.markdown(f"""
            <div style="background:#F8FAFC;border-radius:10px;padding:18px;border:1px solid #E2E8F0;">
                <div style="text-align:center;font-size:52px;font-weight:bold;color:{cor_score};">{score}</div>
                <div style="text-align:center;font-size:13px;color:#64748B;margin-bottom:8px;">Score de Necessidade de Reajuste (0-100)</div>
                <div style="text-align:center;font-size:15px;font-weight:bold;color:{cor_score};margin-bottom:14px;">{veredicto}</div>
                <hr style="border:1px solid #E2E8F0;margin:10px 0;">
                <table style="width:100%;font-size:12px;color:#334155;">
                    <tr><td>📊 Sinistralidade média 3 anos</td><td style="text-align:right;font-weight:bold;">{sin_media_3a:.1%}</td></tr>
                    <tr><td>📅 Variação ano a ano</td><td style="text-align:right;font-weight:bold;">{variacao_yoy:+.1f}%</td></tr>
                    <tr><td>📈 Aceleração anual</td><td style="text-align:right;font-weight:bold;">{aceleracao:+.2f}% a.a.</td></tr>
                    <tr><td>💰 Ticket médio sinistro (últimos 12m)</td><td style="text-align:right;font-weight:bold;">R$ {ticket_medio:,.2f}</td></tr>
                    <tr><td>💰 Ticket médio sinistro (12m anteriores)</td><td style="text-align:right;font-weight:bold;">R$ {ticket_medio_ant:,.2f}</td></tr>
                    <tr><td>↕️ Variação do ticket médio</td><td style="text-align:right;font-weight:bold;color:{'#DC2626' if _var_ticket > 0 else '#16A34A'};">{_var_ticket:+.1f}%</td></tr>
                </table>
                <hr style="border:1px solid #E2E8F0;margin:10px 0;">
                <div style="font-size:11px;color:#64748B;">{desc}</div>
                <div style="font-size:10px;color:#94A3B8;margin-top:6px;">⚠️ O ticket médio dos últimos 12 meses pode estar subestimado pela demora no aviso/envio dos sinistros recentes. Use o ticket dos 12 meses anteriores (janela mais madura) como referência de comparação.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Dados insuficientes para calcular indicadores de reajuste.")
else:
    st.info("Nenhum dado disponível para análise de tendência.")

st.markdown("")
st.markdown("""
<div style="background:#F8FAFC;border-radius:10px;padding:18px;border:1px solid #E2E8F0;font-size:13px;color:#334155;">
<b>📖 Como entender esta análise</b><br><br>

<b>O que é:</b> Esta seção responde à pergunta: <i>a sinistralidade está melhorando ou piorando ao longo dos anos?</i> São quatro visualizações complementares que mostram a direção e a velocidade da mudança.<br><br>

<b>Sinistralidade % Anual com Tendência Linear:</b> Mostra a sinistralidade real de cada ano de vigência (linha azul) e uma linha de tendência calculada por regressão linear (linha vermelha tracejada). Se a linha vermelha sobe, a tendência é de piora. O alerta automático abaixo do gráfico classifica a velocidade: alta acelerada (acima de 5% ao ano), alta moderada (entre 1% e 5%), estável ou queda.<br><br>

<b>Evolução Mensal — Últimos 24 Meses:</b> Mostra o valor de sinistro mês a mês com duas médias móveis. A Média Móvel 3 meses (linha azul) reage mais rápido às variações recentes. A Média Móvel 6 meses (linha vermelha pontilhada) é mais suavizada. Quando a MM3 cruza acima da MM6, é um sinal de piora recente; quando cruza abaixo, é sinal de melhora.<br><br>

<b>Frequência de Sinistros por Mês:</b> Quantidade de sinistros únicos por mês com média móvel de 3 meses. Permite identificar se um aumento de custo vem de mais eventos ou de eventos maiores (combine com a seção de Frequência × Severidade acima).<br><br>

<b>Painel de Indicadores — Score de Reajuste (0-100):</b> Combina três fatores para gerar um score automático de necessidade de reajuste de prêmio:<br>
• Sinistralidade média dos últimos 3 anos (peso 40%): acima de 80% adiciona 40 pontos; acima de 60% adiciona 20 pontos<br>
• Variação ano a ano (peso 30%): acima de 20% adiciona 30 pontos; acima de 10% adiciona 15 pontos<br>
• Aceleração da tendência em % ao ano (peso 30%): acima de 5% ao ano adiciona 30 pontos; acima de 2% adiciona 15 pontos<br>
Score 70-100 = Reajuste Urgente | Score 40-69 = Reajuste Recomendado | Score 0-39 = Prêmio Adequado.<br><br>

<b>Ticket médio (últimos 12m vs 12m anteriores):</b> O painel mostra o custo médio por sinistro em duas janelas de 12 meses. A janela mais recente pode estar <i>subestimada</i> porque sinistros recentes ainda não foram avisados/enviados (atraso de comunicação). A janela dos 12 meses anteriores já está mais madura e serve de referência: se o ticket recente está muito abaixo do anterior, parte da diferença pode ser apenas atraso de aviso, e não melhora real de severidade.<br><br>

<b>Como foi desenvolvido:</b> A sinistralidade anual usa a mesma base do Desempenho Consolidado por Ano (Ano de Vigência da Apólice), garantindo consistência. As médias móveis mensais são calculadas sobre a data de aviso dos sinistros, que é o dado mais atual disponível. A regressão linear é calculada com numpy.polyfit sobre os anos disponíveis filtrados.
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAINEL DE DIAGNÓSTICO DE VARIAÇÃO DA SINISTRALIDADE — posicionado no final
# ══════════════════════════════════════════════════════════════════════════════
st.write("---")
st.subheader("🔎 Diagnóstico de Variação da Sinistralidade")
st.caption(
    "Identifica quais Ramos e Utilizações contribuíram para a variação recente da sinistralidade. "
    "Mostra as janelas de 60, 90 e 180 dias lado a lado, comparando cada período com o anterior equivalente, "
    "usando a data de aviso dos sinistros."
)

# ── Fragmento Streamlit: reexecuta APENAS a seção ao mudar o seletor, sem
#    recarregar a página inteira (ganho de performance — Streamlit >= 1.33).
_st_fragment = getattr(st, 'fragment', None) or getattr(st, 'experimental_fragment', None)
if _st_fragment is None:
    _st_fragment = lambda _f: _f  # versões antigas: comportamento original (rerun completo)

if not df_sinistro_periodo_atualizado.empty and not df_geral_periodo.empty:

    # ── Preparação compartilhada (executada uma única vez por recarga) ───────
    # Prepara base com datas
    _df_sin = df_sinistro_periodo_atualizado.copy()
    if 'dt_aviso_dt' not in _df_sin.columns:
        _df_sin['dt_aviso_dt'] = pd.to_datetime(_df_sin['dt_aviso'], dayfirst=True, errors='coerce')

    _data_max = _df_sin['dt_aviso_dt'].max()
    _mapa_apo = df_geral_periodo[['N° Apólice', 'Ramo', 'Utilização']].drop_duplicates('N° Apólice')
    _df_sin   = pd.merge(_df_sin, _mapa_apo, on='N° Apólice', how='left')

    _premio_total_geral = df_para_soma['Soma Prêmio Pago por Apolice'].sum()

    # ── Prepara base completa com trimestre e mês ─────────────────────────────
    _df_full = df_sinistro_periodo_atualizado.copy()
    if 'dt_aviso_dt' not in _df_full.columns:
        _df_full['dt_aviso_dt'] = pd.to_datetime(_df_full['dt_aviso'], dayfirst=True, errors='coerce')

    # Remove linhas com data de aviso inválida (NaT) — senão Ano/Trimestre viram
    # NaN e produzem strings 'nan T nan' que quebram o sorted() lá embaixo.
    _df_full = _df_full.dropna(subset=['dt_aviso_dt']).copy()

    _df_full['Ano']       = _df_full['dt_aviso_dt'].dt.year.astype(int)
    _df_full['Trimestre'] = _df_full['dt_aviso_dt'].dt.quarter.astype(int)
    _df_full['AnoTri']    = _df_full['Ano'].astype(str) + ' T' + _df_full['Trimestre'].astype(str)
    _df_full['AnoMes']    = _df_full['dt_aviso_dt'].dt.to_period('M').astype(str)

    # Junta Ramo e Utilização
    _df_full = pd.merge(_df_full, _mapa_apo, on='N° Apólice', how='left')

    # Prêmio trimestral e mensal — proporcional ao número de trimestres/meses
    _anos_base    = df_para_soma['Ano Vigência'].nunique() or 1
    _premio_total_full = df_para_soma['Soma Prêmio Pago por Apolice'].sum()
    _premio_por_tri = _premio_total_full / (_anos_base * 4)  # 4 trimestres por ano
    _premio_por_mes = _premio_total_full / (_anos_base * 12) # 12 meses por ano

    # ══ SEÇÃO 1 — Diagnóstico de Variação (fragmento isolado) ═══════════════
    @_st_fragment
    def _render_diag_variacao():
        # Item 3: seletor por botão de seleção (igual à Evolução Trimestral/Mensal)
        _agrupar = st.radio(
            'Agrupar por:',
            ['Ramo', 'Utilização'],
            horizontal=True,
            key='diag_agrupar_radio'
        )
        _cols_grp = [_agrupar]

        # Prêmio por grupo (proporcional à janela)
        _premio_grp = df_para_soma.groupby(_cols_grp, as_index=False).agg(
            Premio_Total=('Soma Prêmio Pago por Apolice', 'sum')
        )

        def _calcular_janela(janela):
            _ini_rec = _data_max - pd.Timedelta(days=janela)
            _ini_ant = _ini_rec - pd.Timedelta(days=janela)
            _rec = _df_sin[_df_sin['dt_aviso_dt'] > _ini_rec]
            _ant = _df_sin[(_df_sin['dt_aviso_dt'] > _ini_ant) & (_df_sin['dt_aviso_dt'] <= _ini_rec)]

            def _agg(df):
                if df.empty:
                    return pd.DataFrame(columns=_cols_grp + ['Total_Sinistro'])
                return df.groupby(_cols_grp, as_index=False).agg(Total_Sinistro=('Total Sinistro', 'sum'))

            _pj = _premio_grp.copy()
            _pj['Premio_J'] = _pj['Premio_Total'] * (janela / 365)
            _r = pd.merge(_pj, _agg(_rec), on=_cols_grp, how='left').fillna(0)
            _a = pd.merge(_pj, _agg(_ant), on=_cols_grp, how='left').fillna(0)
            _r[f'Sin_Rec'] = (_r['Total_Sinistro'] / _r['Premio_J'].replace(0, float('nan'))).fillna(0)
            _a[f'Sin_Ant'] = (_a['Total_Sinistro'] / _a['Premio_J'].replace(0, float('nan'))).fillna(0)
            _c = pd.merge(_r[_cols_grp + ['Sin_Rec']], _a[_cols_grp + ['Sin_Ant']], on=_cols_grp, how='outer').fillna(0)
            _c['Var_pp'] = (_c['Sin_Rec'] - _c['Sin_Ant']) * 100
            _sin_rec_g = _rec['Total Sinistro'].sum() / (_premio_total_geral * janela / 365) if _premio_total_geral > 0 else 0
            _sin_ant_g = _ant['Total Sinistro'].sum() / (_premio_total_geral * janela / 365) if _premio_total_geral > 0 else 0
            return _c, _sin_rec_g, _sin_ant_g, _ini_rec, _ini_ant

        _janelas = [60, 90, 180]
        _res = {j: _calcular_janela(j) for j in _janelas}

        # ── KPIs — um por janela ─────────────────────────────────────────────────
        st.markdown("**Sinistralidade por janela — período recente vs anterior**")
        _kcols = st.columns(3)
        for i, j in enumerate(_janelas):
            _, _srg, _sag, _ini_rec, _ini_ant = _res[j]
            _var = (_srg - _sag) * 100
            with _kcols[i]:
                st.markdown(
                    f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:14px 18px;">'
                    f'<div style="font-size:11px;color:#64748B;text-transform:uppercase;letter-spacing:.05em;">Últimos {j} dias</div>'
                    f'<div style="display:flex;align-items:baseline;gap:16px;margin:6px 0;">'
                    f'  <div>'
                    f'    <div style="font-size:11px;color:#64748B;">Recente</div>'
                    f'    <div style="font-size:26px;font-weight:700;color:#1E293B;">{_srg:.1%}</div>'
                    f'  </div>'
                    f'  <div style="color:#CBD5E1;font-size:20px;">→</div>'
                    f'  <div>'
                    f'    <div style="font-size:11px;color:#64748B;">Anterior</div>'
                    f'    <div style="font-size:26px;font-weight:700;color:#94A3B8;">{_sag:.1%}</div>'
                    f'  </div>'
                    f'</div>'
                    f'<div style="font-size:12px;font-weight:600;color:{"#DC2626" if _var > 0 else "#16A34A"};">'
                    f'  {"▲" if _var > 0 else "▼"} {abs(_var):.1f}pp {"piora" if _var > 0 else "melhora"}'
                    f'</div>'
                    f'<div style="font-size:10px;color:#94A3B8;margin-top:6px;">'
                    f'  Rec: {_ini_rec.strftime("%d/%m/%y")} a {_data_max.strftime("%d/%m/%y")}<br>'
                    f'  Ant: {_ini_ant.strftime("%d/%m/%y")} a {_ini_rec.strftime("%d/%m/%y")}'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.write("")
        st.markdown(f"**Variação da sinistralidade por {_agrupar} — 60 / 90 / 180 dias**")

        # ── 3 gráficos lado a lado ───────────────────────────────────────────────
        _gcols = st.columns(3)
        for i, j in enumerate(_janelas):
            _comp, _, _, _, _ = _res[j]
            _plot = _comp[_comp['Sin_Rec'] + _comp['Sin_Ant'] > 0].copy()

            # Garante rótulo como string categórica — evita escala numérica no eixo Y
            _plot['_label'] = _plot[_cols_grp[0]].astype(str)
            _plot = _plot.sort_values('Var_pp')

            _cores = ['#DC2626' if v > 0 else '#16A34A' for v in _plot['Var_pp']]
            _max_abs = max(abs(_plot['Var_pp']).max() if not _plot.empty else 1, 1) * 1.4

            _fig = go.Figure(go.Bar(
                x=_plot['Var_pp'],
                y=_plot['_label'],
                orientation='h',
                marker_color=_cores,
                text=_plot['Var_pp'].map(lambda x: f"{x:+.1f}pp"),
                textposition='outside',
            ))
            _fig.add_vline(x=0, line_width=1.5, line_color='#374151')
            _fig.update_layout(
                title=dict(text=f"Últimos {j} dias", font=dict(size=13)),
                xaxis=dict(title='Variação (pp)', ticksuffix='pp', range=[-_max_abs, _max_abs]),
                yaxis=dict(
                    title='',
                    tickfont=dict(size=11),
                    type='category',          # força eixo categórico — nunca interpola os rótulos
                    categoryorder='array',
                    categoryarray=_plot['_label'].tolist()
                ),
                margin=dict(t=40, b=20, l=10, r=50),
                height=max(220, len(_plot) * 50 + 80),
                plot_bgcolor='white'
            )
            with _gcols[i]:
                st.plotly_chart(_fig, use_container_width=True, config={'displayModeBar': False})

        # ── Tabela consolidada ───────────────────────────────────────────────────
        with st.expander("📋 Ver tabela detalhada de comparação"):
            _tbl_base = _res[60][0][_cols_grp].copy()
            for j in _janelas:
                _c = _res[j][0][_cols_grp + ['Sin_Rec','Sin_Ant','Var_pp']].copy()
                _c.columns = _cols_grp + [f'Sin_Rec_{j}', f'Sin_Ant_{j}', f'Var_{j}']
                _tbl_base = pd.merge(_tbl_base, _c, on=_cols_grp, how='outer').fillna(0)
            for j in _janelas:
                _tbl_base[f'Sin_Rec_{j}'] = _tbl_base[f'Sin_Rec_{j}'].map(lambda x: f"{x:.1%}")
                _tbl_base[f'Sin_Ant_{j}'] = _tbl_base[f'Sin_Ant_{j}'].map(lambda x: f"{x:.1%}")
                _tbl_base[f'Var_{j}']     = _tbl_base[f'Var_{j}'].map(lambda x: f"{x:+.1f}pp")
            _tbl_base.rename(columns={
                _cols_grp[0]: _agrupar,
                'Sin_Rec_60':'Rec.60d','Sin_Ant_60':'Ant.60d','Var_60':'Var.60d',
                'Sin_Rec_90':'Rec.90d','Sin_Ant_90':'Ant.90d','Var_90':'Var.90d',
                'Sin_Rec_180':'Rec.180d','Sin_Ant_180':'Ant.180d','Var_180':'Var.180d',
            }, inplace=True)
            st.dataframe(_tbl_base, hide_index=True, use_container_width=True)

        st.markdown("")
        st.markdown("""
<div style="background:#F8FAFC;border-radius:10px;padding:18px;border:1px solid #E2E8F0;font-size:13px;color:#334155;">
<b>📖 Como entender esta análise</b><br><br>

<b>O que é:</b> Esta seção responde à pergunta: <i>quais Ramos ou Utilizações puxaram a sinistralidade para cima (ou para baixo) recentemente?</i> Ela compara três janelas de tempo — 60, 90 e 180 dias — cada uma contra o período imediatamente anterior de mesma duração, usando a <b>data de aviso</b> dos sinistros.<br><br>

<b>Cartões de sinistralidade por janela:</b> Mostram a sinistralidade geral da carteira no período recente vs. o período anterior equivalente. A seta indica se houve piora (▲ vermelho) ou melhora (▼ verde), em pontos percentuais (pp). As datas de cada janela aparecem abaixo do indicador.<br><br>

<b>Gráficos de variação por Ramo/Utilização:</b> Cada barra mostra quanto a sinistralidade daquele grupo variou entre o período anterior e o recente, em pontos percentuais. Barras vermelhas à direita = grupos que pioraram; barras verdes à esquerda = grupos que melhoraram. Compare as três janelas: se um grupo aparece vermelho nas três, a piora é consistente e não pontual.<br><br>

<b>Tabela detalhada:</b> O expansor mostra, para cada grupo, a sinistralidade do período recente (Rec.), do anterior (Ant.) e a variação (Var.) em cada janela — útil para validar os gráficos com números exatos.<br><br>

<b>Como foi desenvolvido:</b> O prêmio de cada grupo é proporcionalizado ao tamanho da janela (ex.: prêmio anual × 60/365 para a janela de 60 dias). O sinistro é somado pela data de aviso dentro de cada janela. Sinistralidade = sinistro da janela ÷ prêmio proporcional. A variação em pp é a diferença entre a sinistralidade recente e a anterior. Janelas curtas (60d) reagem rápido mas oscilam mais; a janela de 180d é mais estável.<br><br>

<b>Atenção:</b> Como a análise usa a data de aviso, sinistros ocorridos recentemente mas ainda não avisados não aparecem — a janela mais recente pode estar subestimada.
</div>
""", unsafe_allow_html=True)

    # ══ SEÇÃO 2 — Evolução Trimestral e Mensal (fragmento isolado) ══════════
    @_st_fragment
    def _render_evolucao_tri_mensal():
        # ── Seletor de dimensão ───────────────────────────────────────────────────
        _dim = st.radio(
            "Analisar por:",
            ["Ramo", "Utilização"],
            horizontal=True,
            key="diag_dim_tend"
        )

        # ── Tab: Trimestral vs Mensal ─────────────────────────────────────────────
        _tab_tri, _tab_mes = st.tabs(["📅 Trimestral (período completo)", "📆 Mensal (últimos 12 meses)"])

        # ════ TRIMESTRAL ══════════════════════════════════════════════════════════
        with _tab_tri:
            _grp_tri = _df_full.groupby(['AnoTri', _dim], as_index=False).agg(
                Total_Sinistro=('Total Sinistro', 'sum'),
                Qtd_Sinistros=('nr_sinistro', 'nunique')
            )
            # Prêmio proporcional por trimestre por grupo
            _premio_dim = df_para_soma.groupby(_dim, as_index=False).agg(
                Premio_Dim=('Soma Prêmio Pago por Apolice', 'sum')
            )
            _n_tri_total = _df_full['AnoTri'].nunique() or 1
            _premio_dim['Premio_Tri'] = _premio_dim['Premio_Dim'] / (_anos_base * 4)

            _grp_tri = pd.merge(_grp_tri, _premio_dim[[_dim, 'Premio_Tri']], on=_dim, how='left')
            _grp_tri['Sinistralidade'] = (
                _grp_tri['Total_Sinistro'] / _grp_tri['Premio_Tri'].replace(0, float('nan'))
            ).fillna(0)
            _grp_tri['_label'] = _grp_tri[_dim].astype(str)

            # Ordena períodos corretamente (defensivo: ignora strings malformadas)
            def _ano_tri_key(_v):
                try:
                    _ano, _tri = str(_v).split(' T')
                    return (int(_ano), int(_tri))
                except (ValueError, AttributeError):
                    return (9999, 9)  # joga ao final
            _periodos_tri = sorted(_grp_tri['AnoTri'].unique(), key=_ano_tri_key)

            _fig_tri = go.Figure()
            for _grp_val in sorted(_grp_tri['_label'].unique()):
                _d = _grp_tri[_grp_tri['_label'] == _grp_val].copy()
                _d = _d.set_index('AnoTri').reindex(_periodos_tri).reset_index()
                _d['Sinistralidade'] = _d['Sinistralidade'].fillna(0)

                # Detecta tendência do último ano (últimos 4 trimestres)
                _ultimos = _d.tail(4)['Sinistralidade']
                _tend = (_ultimos.iloc[-1] - _ultimos.iloc[0]) if len(_ultimos) >= 2 else 0
                _cor_nome = "🔴" if _tend > 0.05 else ("🟡" if _tend > 0 else "🟢")

                _fig_tri.add_trace(go.Scatter(
                    x=_d['AnoTri'],
                    y=_d['Sinistralidade'],
                    mode='lines+markers',
                    name=f"{_cor_nome} {_grp_val}",
                    line=dict(width=2),
                    marker=dict(size=6),
                    hovertemplate=f"{_dim} {_grp_val}<br>%{{x}}: %{{y:.1%}}<extra></extra>"
                ))

            _fig_tri.update_layout(
                xaxis=dict(title='Trimestre', tickangle=-45, tickfont=dict(size=9)),
                yaxis=dict(title='Sinistralidade (%)', tickformat='.0%'),
                legend=dict(orientation='h', y=1.15),
                margin=dict(t=30, b=60, l=0, r=0),
                height=400,
                hovermode='x unified',
                plot_bgcolor='white'
            )
            st.plotly_chart(_fig_tri, use_container_width=True, config={'displayModeBar': False})

            # Alerta automático — quem mais subiu no último ano
            _tend_resumo = []
            for _grp_val in _grp_tri['_label'].unique():
                _d = _grp_tri[_grp_tri['_label'] == _grp_val].sort_values('AnoTri').tail(4)
                if len(_d) >= 2:
                    _delta = _d['Sinistralidade'].iloc[-1] - _d['Sinistralidade'].iloc[0]
                    _tend_resumo.append((_grp_val, _delta, _d['Sinistralidade'].iloc[-1]))

            if _tend_resumo:
                _tend_resumo.sort(key=lambda x: x[1], reverse=True)
                _pior = _tend_resumo[0]
                _melhor = _tend_resumo[-1]
                _col_al1, _col_al2 = st.columns(2)
                with _col_al1:
                    if _pior[1] > 0:
                        st.error(
                            f"🔴 **{_dim} {_pior[0]}** teve a maior alta: "
                            f"**+{_pior[1]:.1%}** nos últimos 4 trimestres "
                            f"(sinistralidade atual: {_pior[2]:.1%})"
                        )
                    else:
                        st.success(f"🟢 Todos os {_dim.lower()}s melhoraram ou estabilizaram.")
                with _col_al2:
                    if _melhor[1] < 0:
                        st.success(
                            f"🟢 **{_dim} {_melhor[0]}** teve a maior queda: "
                            f"**{_melhor[1]:.1%}** nos últimos 4 trimestres "
                            f"(sinistralidade atual: {_melhor[2]:.1%})"
                        )

        # ════ MENSAL (últimos 12 meses) ═══════════════════════════════════════════
        with _tab_mes:
            _data_12m = _data_max - pd.Timedelta(days=365)
            _df_12m = _df_full[_df_full['dt_aviso_dt'] >= _data_12m].copy()

            _grp_mes = _df_12m.groupby(['AnoMes', _dim], as_index=False).agg(
                Total_Sinistro=('Total Sinistro', 'sum'),
                Qtd_Sinistros=('nr_sinistro', 'nunique')
            )
            _premio_dim['Premio_Mes'] = _premio_dim['Premio_Dim'] / (_anos_base * 12)
            _grp_mes = pd.merge(_grp_mes, _premio_dim[[_dim, 'Premio_Mes']], on=_dim, how='left')
            _grp_mes['Sinistralidade'] = (
                _grp_mes['Total_Sinistro'] / _grp_mes['Premio_Mes'].replace(0, float('nan'))
            ).fillna(0)
            _grp_mes['_label'] = _grp_mes[_dim].astype(str)

            _periodos_mes = sorted(_grp_mes['AnoMes'].unique())

            _fig_mes = go.Figure()
            for _grp_val in sorted(_grp_mes['_label'].unique()):
                _d = _grp_mes[_grp_mes['_label'] == _grp_val].copy()
                _d = _d.set_index('AnoMes').reindex(_periodos_mes).reset_index()
                _d['Sinistralidade'] = _d['Sinistralidade'].fillna(0)

                # Média móvel 3 meses
                _d['MM3'] = _d['Sinistralidade'].rolling(3, min_periods=1).mean()

                _fig_mes.add_trace(go.Scatter(
                    x=_d['AnoMes'], y=_d['Sinistralidade'],
                    mode='markers', name=f"{_grp_val} (mensal)",
                    marker=dict(size=5), opacity=0.4,
                    showlegend=False,
                    hovertemplate=f"{_dim} {_grp_val}<br>%{{x}}: %{{y:.1%}}<extra></extra>"
                ))
                _fig_mes.add_trace(go.Scatter(
                    x=_d['AnoMes'], y=_d['MM3'],
                    mode='lines', name=f"{_grp_val} (MM3)",
                    line=dict(width=2.5),
                    hovertemplate=f"{_dim} {_grp_val} MM3<br>%{{x}}: %{{y:.1%}}<extra></extra>"
                ))

            _fig_mes.update_layout(
                xaxis=dict(title='Mês', tickangle=-45, tickfont=dict(size=9)),
                yaxis=dict(title='Sinistralidade (%)', tickformat='.0%'),
                legend=dict(orientation='h', y=1.15),
                margin=dict(t=30, b=60, l=0, r=0),
                height=400,
                hovermode='x unified',
                plot_bgcolor='white'
            )
            st.caption("Pontos = sinistralidade mensal bruta. Linhas = média móvel 3 meses (MM3) — suaviza variações pontuais.")
            st.plotly_chart(_fig_mes, use_container_width=True, config={'displayModeBar': False})

        st.markdown("")
        st.markdown("""
<div style="background:#F8FAFC;border-radius:10px;padding:18px;border:1px solid #E2E8F0;font-size:13px;color:#334155;">
<b>📖 Como entender esta análise</b><br><br>

<b>O que é:</b> Esta seção mostra a <i>trajetória</i> da sinistralidade de cada Ramo ou Utilização ao longo do tempo, em duas escalas: trimestral (período completo filtrado — direção de médio prazo) e mensal (últimos 12 meses — movimento recente).<br><br>

<b>Aba Trimestral:</b> Uma linha por grupo, com a sinistralidade de cada trimestre. O emoji ao lado do nome resume a tendência dos últimos 4 trimestres: 🔴 alta relevante (subiu mais de 5pp), 🟡 alta leve, 🟢 estável ou em queda. Os alertas automáticos abaixo do gráfico destacam o grupo com maior alta e o de maior queda no último ano.<br><br>

<b>Aba Mensal:</b> Os pontos são a sinistralidade mensal bruta (volátil por natureza); as linhas são a média móvel de 3 meses (MM3), que suaviza oscilações pontuais e revela a direção real. Acompanhe as linhas, não os pontos: linha subindo = deterioração em curso.<br><br>

<b>Como foi desenvolvido:</b> O sinistro é agrupado por trimestre/mês de <b>aviso</b> e por Ramo ou Utilização. O prêmio de cada grupo é distribuído uniformemente entre os períodos (prêmio total do grupo ÷ nº de anos da base × 4 trimestres ou × 12 meses). Sinistralidade do período = sinistro do período ÷ prêmio proporcional do grupo.<br><br>

<b>Atenção:</b> Por usar prêmio médio uniforme, grupos com forte crescimento ou queda de produção podem ter a sinistralidade distorcida em períodos específicos. Meses muito recentes tendem a aparecer melhores do que são, pela demora no aviso dos sinistros.
</div>
""", unsafe_allow_html=True)

    # ── Renderização ─────────────────────────────────────────────────────────
    _render_diag_variacao()

    st.write("---")
    st.markdown("### 📉 Evolução Trimestral e Mensal da Sinistralidade")
    st.caption(
        "Visão de tendência do período completo filtrado. "
        "Trimestral mostra a direção de médio prazo; mensal (últimos 12 meses) mostra o movimento recente. "
        "Identifique em qual Ramo ou Utilização a sinistralidade está subindo."
    )
    _render_evolucao_tri_mensal()

else:
    st.info("Nenhum dado disponível para análise de variação.")

# ─────────────────────────────────────────────────────────────────────────────
# 🕰️ ANÁLISE DE CAUDA HISTÓRICA — Sinistros antigos influenciando o período
# Objetivo: identificar sinistros cuja DATA DE OCORRÊNCIA é muito anterior à
# DATA DE AVISO, distorcendo a sinistralidade do período filtrado. Esses casos
# tipicamente representam avisos tardios (IBNR realizado) ou atualizações de
# reservas/pagamentos em sinistros antigos.
# ─────────────────────────────────────────────────────────────────────────────
st.write("---")
st.subheader("🕰️ Análise de Cauda Histórica — Sinistros Avisados com Atraso")
st.markdown(
    '<p class="section-label">Quantifica e visualiza o quanto sinistros com '
    'ocorrência em períodos passados estão pesando na sinistralidade dos '
    'avisos do período filtrado.</p>',
    unsafe_allow_html=True
)

# Garante que o decorador de fragmento esteja disponível neste escopo
_st_fragment_ch = getattr(st, 'fragment', None) or getattr(st, 'experimental_fragment', None)
if _st_fragment_ch is None:
    _st_fragment_ch = lambda _f: _f

if (not df_sinistro_periodo_atualizado.empty) and (not df_geral_periodo.empty):

    # ── Preparação compartilhada (executada uma única vez por recarga) ───────
    _df_ch_base = df_sinistro_periodo_atualizado.copy()

    # Garante colunas de data já parseadas
    if 'dt_aviso_dt' not in _df_ch_base.columns:
        _df_ch_base['dt_aviso_dt'] = pd.to_datetime(_df_ch_base['dt_aviso'], dayfirst=True, errors='coerce')
    if 'dt_ocorrencia_dt' not in _df_ch_base.columns:
        _df_ch_base['dt_ocorrencia_dt'] = pd.to_datetime(_df_ch_base['dt_ocorrencia'], dayfirst=True, errors='coerce')

    # Calcula lag (dias) entre aviso e ocorrência. Descarta linhas sem ambas datas.
    _df_ch_base = _df_ch_base.dropna(subset=['dt_aviso_dt', 'dt_ocorrencia_dt']).copy()
    _df_ch_base['lag_dias'] = (_df_ch_base['dt_aviso_dt'] - _df_ch_base['dt_ocorrencia_dt']).dt.days

    # Remove inconsistências: lag negativo (aviso antes da ocorrência — erro de
    # cadastro) e lag absurdo (> 10 anos — quase sempre cadastro errado).
    _df_ch_base = _df_ch_base[(_df_ch_base['lag_dias'] >= 0) & (_df_ch_base['lag_dias'] <= 3650)].copy()

    # Agrega por nr_sinistro (uma linha por sinistro, soma valores e pega max lag)
    if 'Total Sinistro' in _df_ch_base.columns:
        _agg_dict = {
            'lag_dias': 'max',
            'dt_ocorrencia_dt': 'min',
            'dt_aviso_dt': 'min',
            'Total Sinistro': 'sum',
        }
        # Inclui Ramo/Utilização se existirem
        for _c in ['Ramo', 'Utilização']:
            if _c in _df_ch_base.columns:
                _agg_dict[_c] = 'first'
        _df_ch = _df_ch_base.groupby('nr_sinistro', as_index=False).agg(_agg_dict)
    else:
        _df_ch = pd.DataFrame()

    # Premio total do período (usado para calcular impacto na sinistralidade)
    _premio_total_ch = df_para_soma['Soma Prêmio Pago por Apolice'].sum()

    if _df_ch.empty or _premio_total_ch <= 0:
        st.info("Não há sinistros com data de ocorrência e aviso válidas para analisar a cauda histórica no período selecionado.")
    else:

        @_st_fragment_ch
        def _render_cauda_historica():
            # ── Controles ────────────────────────────────────────────────────
            _col_ctrl_1, _col_ctrl_2 = st.columns([1, 3])
            with _col_ctrl_1:
                _limite_meses = st.radio(
                    "Considerar **cauda histórica** quando o aviso ocorreu mais de:",
                    options=[6, 12, 18, 24],
                    index=1,  # default: 12 meses
                    horizontal=True,
                    format_func=lambda x: f"{x} meses",
                    key="cauda_historica_threshold",
                    help=(
                        "Limite (em meses) entre a data de ocorrência e a data de "
                        "aviso. Avisos com defasagem acima desse valor são tratados como "
                        "cauda histórica (sinistros antigos avisados no período)."
                    )
                )
            _limite_dias = int(_limite_meses) * 30

            # Marca sinistros de cauda
            _df = _df_ch.copy()
            _df['eh_cauda'] = _df['lag_dias'] > _limite_dias

            # ── KPIs principais ─────────────────────────────────────────────
            _qtd_total       = len(_df)
            _valor_total     = _df['Total Sinistro'].sum()
            _qtd_cauda       = int(_df['eh_cauda'].sum())
            _valor_cauda     = _df.loc[_df['eh_cauda'], 'Total Sinistro'].sum()
            _pct_qtd_cauda   = (_qtd_cauda / _qtd_total * 100) if _qtd_total > 0 else 0
            _pct_valor_cauda = (_valor_cauda / _valor_total * 100) if _valor_total > 0 else 0
            _lag_medio       = _df['lag_dias'].mean()
            _lag_mediano     = _df['lag_dias'].median()

            # Sinistralidade com / sem cauda histórica
            _sin_com    = _valor_total / _premio_total_ch * 100
            _sin_sem    = (_valor_total - _valor_cauda) / _premio_total_ch * 100
            _impacto_pp = _sin_com - _sin_sem

            # Estilo dos cards (mesma estética dos painéis acima)
            _card_base = (
                "background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;"
                "padding:14px 16px;height:100%;"
            )
            _card_alert = (
                "background:#FEF2F2;border:1px solid #FECACA;border-radius:10px;"
                "padding:14px 16px;height:100%;"
            )

            _cor_impacto = "#DC2626" if _impacto_pp > 0.5 else ("#D97706" if _impacto_pp > 0.1 else "#059669")
            _card_impacto = _card_alert if _impacto_pp > 0.5 else _card_base

            _c1, _c2, _c3, _c4 = st.columns(4)
            with _c1:
                st.markdown(
                    f'<div style="{_card_base}">'
                    f'<div style="font-size:12px;color:#64748B;">⏱️ Defasagem média (ocorrência → aviso)</div>'
                    f'<div style="font-size:22px;font-weight:600;color:#0F172A;margin-top:4px;">{_lag_medio:.0f} dias</div>'
                    f'<div style="font-size:11px;color:#94A3B8;margin-top:2px;">mediana: {_lag_mediano:.0f} dias</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with _c2:
                st.markdown(
                    f'<div style="{_card_base}">'
                    f'<div style="font-size:12px;color:#64748B;">📌 Sinistros com cauda histórica</div>'
                    f'<div style="font-size:22px;font-weight:600;color:#0F172A;margin-top:4px;">{_qtd_cauda:,}</div>'
                    f'<div style="font-size:11px;color:#94A3B8;margin-top:2px;">{_pct_qtd_cauda:.1f}% dos {_qtd_total:,} sinistros do período</div>'
                    f'</div>'.replace(',', '.'),
                    unsafe_allow_html=True
                )
            with _c3:
                _cor_valor = "#DC2626" if _pct_valor_cauda > 15 else ("#D97706" if _pct_valor_cauda > 5 else "#0F172A")
                st.markdown(
                    f'<div style="{_card_base}">'
                    f'<div style="font-size:12px;color:#64748B;">💰 R$ representado pela cauda</div>'
                    f'<div style="font-size:22px;font-weight:600;color:{_cor_valor};margin-top:4px;">R$ {formatar_valor_br(_valor_cauda)}</div>'
                    f'<div style="font-size:11px;color:#94A3B8;margin-top:2px;">{_pct_valor_cauda:.1f}% do valor total avisado</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with _c4:
                st.markdown(
                    f'<div style="{_card_impacto}">'
                    f'<div style="font-size:12px;color:#64748B;">📊 Impacto na sinistralidade</div>'
                    f'<div style="font-size:22px;font-weight:600;color:{_cor_impacto};margin-top:4px;">{_impacto_pp:+.2f} pp</div>'
                    f'<div style="font-size:11px;color:#94A3B8;margin-top:2px;">{_sin_com:.1f}% com / {_sin_sem:.1f}% sem cauda</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Distribuição do lag por faixa ───────────────────────────────
            st.markdown(
                '<p class="section-label">Distribuição da defasagem entre ocorrência e aviso</p>',
                unsafe_allow_html=True
            )

            _faixas = [
                ('0–30 dias',     0,    30,    '#059669'),
                ('31–90 dias',    31,   90,    '#059669'),
                ('91–180 dias',   91,   180,   '#D97706'),
                ('181–365 dias',  181,  365,   '#D97706'),
                ('1–2 anos',      366,  730,   '#DC2626'),
                ('2–3 anos',      731,  1095,  '#DC2626'),
                ('> 3 anos',      1096, 99999, '#7F1D1D'),
            ]
            _rows_faixa = []
            for _label, _lo, _hi, _cor in _faixas:
                _mask = (_df['lag_dias'] >= _lo) & (_df['lag_dias'] <= _hi)
                _rows_faixa.append({
                    'Faixa':       _label,
                    'Qtd':         int(_mask.sum()),
                    'Valor':       float(_df.loc[_mask, 'Total Sinistro'].sum()),
                    'cor':         _cor,
                })
            _df_faixa = pd.DataFrame(_rows_faixa)

            _col_h1, _col_h2 = st.columns(2)
            with _col_h1:
                _fig_qtd = go.Figure(go.Bar(
                    x=_df_faixa['Qtd'],
                    y=_df_faixa['Faixa'],
                    orientation='h',
                    marker_color=_df_faixa['cor'],
                    text=_df_faixa['Qtd'].apply(lambda v: f'{int(v):,}'.replace(',', '.')),
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>Qtd: %{x}<extra></extra>',
                ))
                _fig_qtd.update_layout(
                    title=dict(text='Quantidade de sinistros por faixa de defasagem', font=dict(size=14)),
                    height=320,
                    margin=dict(l=10, r=30, t=40, b=10),
                    plot_bgcolor='white',
                    yaxis=dict(autorange='reversed'),
                    xaxis_title='Quantidade',
                )
                st.plotly_chart(_fig_qtd, use_container_width=True, config={'displayModeBar': False})

            with _col_h2:
                _fig_val = go.Figure(go.Bar(
                    x=_df_faixa['Valor'],
                    y=_df_faixa['Faixa'],
                    orientation='h',
                    marker_color=_df_faixa['cor'],
                    text=_df_faixa['Valor'].apply(lambda v: f'R$ {formatar_valor_br(v)}'),
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>',
                ))
                _fig_val.update_layout(
                    title=dict(text='Valor (R$) por faixa de defasagem', font=dict(size=14)),
                    height=320,
                    margin=dict(l=10, r=30, t=40, b=10),
                    plot_bgcolor='white',
                    yaxis=dict(autorange='reversed'),
                    xaxis_title='Valor (R$)',
                )
                st.plotly_chart(_fig_val, use_container_width=True, config={'displayModeBar': False})

            # ── Matriz Ano Ocorrência × Ano Aviso ───────────────────────────
            st.markdown(
                '<p class="section-label">Matriz Ano de Ocorrência × Ano de Aviso</p>',
                unsafe_allow_html=True
            )
            st.caption(
                "🎯 Diagonal = aviso no mesmo ano da ocorrência (normal). "
                "Abaixo da diagonal = avisos tardios (cauda histórica). "
                "Quanto mais valor abaixo da diagonal, maior o efeito de IBNR realizado no período."
            )

            _df_mat = _df.copy()
            _df_mat['Ano_Oc']  = _df_mat['dt_ocorrencia_dt'].dt.year
            _df_mat['Ano_Av']  = _df_mat['dt_aviso_dt'].dt.year

            _piv = _df_mat.pivot_table(
                index='Ano_Oc', columns='Ano_Av',
                values='Total Sinistro', aggfunc='sum', fill_value=0
            ).sort_index().sort_index(axis=1)

            if not _piv.empty:
                _piv_qtd = _df_mat.pivot_table(
                    index='Ano_Oc', columns='Ano_Av',
                    values='nr_sinistro', aggfunc='count', fill_value=0
                ).reindex(index=_piv.index, columns=_piv.columns, fill_value=0)

                # Texto exibido em cada célula: R$ + qtd
                _text = [
                    [
                        (f"R$ {formatar_valor_br(_piv.iat[i, j])}<br>{int(_piv_qtd.iat[i, j])} sin")
                        if _piv.iat[i, j] > 0 else ""
                        for j in range(len(_piv.columns))
                    ]
                    for i in range(len(_piv.index))
                ]
                _hover = [
                    [
                        (f"Ocorrência: {_piv.index[i]}<br>Aviso: {_piv.columns[j]}<br>"
                         f"R$ {formatar_valor_br(_piv.iat[i, j])}<br>"
                         f"{int(_piv_qtd.iat[i, j])} sinistros")
                        for j in range(len(_piv.columns))
                    ]
                    for i in range(len(_piv.index))
                ]

                _fig_mat = go.Figure(go.Heatmap(
                    z=_piv.values,
                    x=[str(c) for c in _piv.columns],
                    y=[str(i) for i in _piv.index],
                    text=_text,
                    texttemplate='%{text}',
                    textfont=dict(size=11),
                    customdata=_hover,
                    hovertemplate='%{customdata}<extra></extra>',
                    colorscale=[
                        [0.0,  '#F8FAFC'],
                        [0.1,  '#DBEAFE'],
                        [0.3,  '#93C5FD'],
                        [0.6,  '#3B82F6'],
                        [1.0,  '#1E40AF'],
                    ],
                    showscale=True,
                    colorbar=dict(title='R$', tickformat=',.0f'),
                ))
                _fig_mat.update_layout(
                    height=max(280, 60 + 60 * len(_piv.index)),
                    margin=dict(l=10, r=10, t=20, b=10),
                    xaxis=dict(title='Ano de Aviso', side='top'),
                    yaxis=dict(title='Ano de Ocorrência', autorange='reversed'),
                    plot_bgcolor='white',
                )
                st.plotly_chart(_fig_mat, use_container_width=True, config={'displayModeBar': False})

            # ── Top sinistros antigos com maior impacto ─────────────────────
            st.markdown(
                f'<p class="section-label">Top sinistros antigos (defasagem > {_limite_meses} meses) com maior impacto no período</p>',
                unsafe_allow_html=True
            )
            _df_top = _df[_df['eh_cauda']].copy()
            if _df_top.empty:
                st.info(f"Nenhum sinistro com defasagem superior a {_limite_meses} meses no período filtrado.")
            else:
                _df_top = _df_top.sort_values('Total Sinistro', ascending=False).head(15)
                _df_top['Defasagem (meses)'] = (_df_top['lag_dias'] / 30).round(1)
                _df_top['Ocorrência']  = _df_top['dt_ocorrencia_dt'].dt.strftime('%d/%m/%Y')
                _df_top['Aviso']       = _df_top['dt_aviso_dt'].dt.strftime('%d/%m/%Y')
                _df_top['Total Sinistro R$'] = _df_top['Total Sinistro'].apply(formatar_valor_br)

                _cols_show = ['nr_sinistro']
                for _c in ['Ramo', 'Utilização']:
                    if _c in _df_top.columns:
                        _cols_show.append(_c)
                _cols_show += ['Ocorrência', 'Aviso', 'Defasagem (meses)', 'Total Sinistro R$']

                _df_top_view = _df_top[_cols_show].rename(columns={
                    'nr_sinistro':         'N° Sinistro',
                    'Total Sinistro R$':   'Total Sinistro',
                })

                st.dataframe(
                    _df_top_view,
                    use_container_width=True,
                    hide_index=True
                )

            # ── Quadro "Como entender esta análise" ─────────────────────────
            st.markdown("")
            st.markdown("""
<div style="background:#F8FAFC;border-radius:10px;padding:18px;border:1px solid #E2E8F0;font-size:13px;color:#334155;">
<b>📖 Como entender esta análise</b><br><br>

<b>O que é:</b> Esta seção responde à pergunta: <i>quanto da sinistralidade que estou vendo no período veio de sinistros que aconteceram lá atrás e só foram avisados agora?</i> Em seguros, é normal o segurado demorar dias, meses (ou anos, em RC e Judicial) para comunicar um evento. Esses avisos tardios e atualizações de sinistros antigos compõem o que o mercado chama de <b>cauda histórica</b> (IBNR realizado).<br><br>

<b>Cartões (KPIs):</b><br>
• <b>Defasagem média / mediana:</b> média e mediana de dias entre <i>dt_ocorrencia</i> e <i>dt_aviso</i> — ou seja, quanto tempo o segurado demorou para avisar o sinistro depois do evento. A mediana é mais robusta — se ela está baixa e a média alta, há poucos sinistros muito antigos puxando a média para cima.<br>
• <b>Qtd. com cauda:</b> número de sinistros avisados no período cujo evento aconteceu há mais que o limite escolhido (6/12/18/24 meses), e o que isso representa em % da carteira.<br>
• <b>R$ da cauda:</b> valor financeiro desses sinistros antigos. É aqui que o impacto real aparece — um único sinistro grande de 2 anos atrás pode pesar mais que dezenas de avisos rápidos.<br>
• <b>Impacto na sinistralidade:</b> compara a sinistralidade do período <i>com</i> e <i>sem</i> os sinistros de cauda. Por exemplo, +4,8 pp significa que sua sinistralidade aparenta ser 4,8 pontos percentuais pior do que a do "negócio corrente". Vermelho = impacto material (&gt; 0,5 pp).<br><br>

<b>Distribuição da defasagem (barras horizontais):</b> mostra como os sinistros se distribuem por faixa de atraso entre a ocorrência e o aviso. Verde = aviso rápido (até 90 dias, esperado). Laranja = atraso intermediário (entre 3 e 12 meses, monitorar). Vermelho = cauda histórica (acima de 1 ano). A barra de quantidade revela frequência; a de R$ revela severidade — uma faixa pequena em qtd mas grande em R$ é onde mora o risco.<br><br>

<b>Matriz Ano de Ocorrência × Ano de Aviso (heatmap):</b> cada célula é o R$ total dos sinistros que ocorreram no ano da linha e foram avisados no ano da coluna. A <b>diagonal</b> (ano de ocorrência = ano de aviso) é o cenário ideal: aviso rápido. Tudo que está <b>abaixo da diagonal</b> é avisado depois — quanto mais "escuro" (azul mais intenso), maior o valor de cauda. Se a coluna do ano mais recente tem muito valor longe da diagonal, é sinal de que o período está sendo inflado por sinistros antigos.<br><br>

<b>Top sinistros antigos:</b> lista os 15 maiores sinistros de cauda no período, com data de ocorrência, data de aviso, defasagem em meses e valor. Use para investigar caso a caso — pode revelar concentrações em um corretor, ramo ou tipo de cobertura específico.<br><br>

<b>Como foi desenvolvido:</b> Para cada sinistro do período filtrado pelo slider, calcula-se a <i>defasagem</i> (em inglês: <i>lag</i>) = dt_aviso − dt_ocorrencia (em dias). Sinistros com defasagem negativa ou superior a 10 anos são descartados como erro de cadastro. O limite de cauda histórica é configurável (6, 12, 18 ou 24 meses); o padrão é 12 meses. A sinistralidade "sem cauda" é recalculada subtraindo o R$ dos sinistros acima do limite, mantendo o prêmio do período inalterado.<br><br>

<b>Atenção:</b> A análise depende da qualidade do preenchimento da data de ocorrência. Sinistros com dt_ocorrencia em branco são descartados — se sua base tem muitos casos assim, os números aqui subestimam o problema. Além disso, atualizações de reserva em sinistros antigos (movimentações financeiras sem novo aviso) não aparecem como "cauda" por este critério; para captar esse efeito, seria necessário comparar a base atual com snapshots anteriores.
</div>
""", unsafe_allow_html=True)

        _render_cauda_historica()

else:
    st.info("Nenhum dado disponível para análise de cauda histórica.")

# ─────────────────────────────────────────────────────────────────────────────
# 📊 ANÁLISE TEMPORAL DA CARTEIRA (alimentada por snapshots diários)
# Substitui o painel monolítico anterior. Estrutura em 5 abas:
#   1. 🎯 Visão Geral       — Painel Executivo + Evolução da Sinistralidade
#   2. 🔍 Por Segmento      — Ramo / Utilização ao longo do tempo
#   3. 📋 Drill-down        — Histórico individual + Top movimentados
#   4. 📐 Reserva & Atuarial — Aging + Run-off realizado vs projetado
#   5. 🚨 Alertas           — Spike + Mudanças de status + Novos/sumidos
#
# Schema do snapshot v2:
#   • tipo_registro='SINISTRO'    → linhas por nr_sinistro (valores financeiros)
#   • tipo_registro='AGG_CARTEIRA' → linhas por (Ramo × Utilização)
#                                    com qtd_apolices_vigentes e soma_premio
# ─────────────────────────────────────────────────────────────────────────────
st.write("---")
st.subheader("📊 Análise Temporal da Carteira")
st.markdown(
    '<p class="section-label">Painel multi-aba alimentado pelos snapshots '
    'diários da base (sinistros + carteira agregada). Cada aba responde a '
    'uma pergunta diferente sobre a evolução temporal da carteira.</p>',
    unsafe_allow_html=True
)

# ── Bloco de Download / Upload de snapshots (reaproveitado) ──────────────────
with st.expander("📥 Baixar snapshot consolidado  /  📤 Carregar snapshots para comparação", expanded=True):
    st.markdown(
        '<div style="font-size:12px;color:#64748B;margin-bottom:10px;">'
        '<b>Rotina diária recomendada:</b> '
        '(1) Faça upload do <code>sinistros_consolidado.parquet</code> salvo no seu Drive. '
        '(2) Baixe o novo consolidado (já inclui o dia de hoje automaticamente). '
        '(3) Substitua o arquivo no Drive pelo recém-baixado. '
        '<br>O app também aceita arquivos antigos no formato individual (<code>sinistros_AAAA-MM-DD.parquet</code>) — '
        'ele detecta automaticamente e mescla tudo num único consolidado.'
        '</div>',
        unsafe_allow_html=True
    )

    _col_dl, _col_up = st.columns([1, 2])

    with _col_up:
        _uploaded = st.file_uploader(
            "📤 Carregar snapshot(s) — consolidado ou individuais",
            type=['parquet'],
            accept_multiple_files=True,
            key="upload_snapshots",
            help=(
                "Aceita o arquivo único 'sinistros_consolidado.parquet' (recomendado) "
                "ou arquivos individuais no formato 'sinistros_AAAA-MM-DD.parquet'. "
                "Pode subir múltiplos arquivos de uma vez."
            )
        )
        if _uploaded:
            _novos = 0
            _ignorados_hoje = 0
            _erros = []
            for _file in _uploaded:
                try:
                    _df_uploaded = pd.read_parquet(_file)
                except Exception as _e:
                    _erros.append(f"`{_file.name}`: erro de leitura ({_e})")
                    continue
                # Validação relaxada: aceita arquivos com nr_sinistro OU tipo_registro
                # (schema v2 pode ter linhas só de AGG_CARTEIRA sem nr_sinistro)
                if ('nr_sinistro' not in _df_uploaded.columns) and ('tipo_registro' not in _df_uploaded.columns):
                    _erros.append(f"`{_file.name}`: schema desconhecido (faltam nr_sinistro e tipo_registro)")
                    continue

                # ── Enriquecimento retroativo p/ snapshots antigos (sem schema v2) ──
                # Adiciona tipo_registro e Ramo/Utilização via merge com dados_calc atual,
                # assumindo que o mapeamento N° Apólice → Ramo/Utilização é estável no tempo.
                if 'tipo_registro' not in _df_uploaded.columns:
                    _df_uploaded = _df_uploaded.copy()
                    _df_uploaded['tipo_registro'] = 'SINISTRO'
                if ('Ramo' not in _df_uploaded.columns or 'Utilização' not in _df_uploaded.columns) \
                   and 'N° Apólice' in _df_uploaded.columns \
                   and dados_calculados is not None and not dados_calculados.empty:
                    try:
                        _mapa = dados_calculados[['N° Apólice', 'Ramo', 'Utilização']].drop_duplicates('N° Apólice').copy()
                        # Coage N° Apólice para string em ambos os lados (snapshots antigos podem ter int64)
                        _mapa['N° Apólice'] = _mapa['N° Apólice'].astype(str)
                        _mapa = _coage_categoria_str(_mapa, ['Ramo', 'Utilização'])
                        _df_uploaded = _df_uploaded.copy()
                        _df_uploaded['N° Apólice'] = _df_uploaded['N° Apólice'].astype(str)
                        _df_uploaded = _df_uploaded.merge(_mapa, on='N° Apólice', how='left')
                        _df_uploaded = _coage_categoria_str(_df_uploaded, ['Ramo', 'Utilização'])
                    except Exception:
                        pass  # silenciosa — análises por segmento simplesmente terão menos cobertura

                # Detecta automaticamente: consolidado (com data_snapshot) vs individual
                if 'data_snapshot' in _df_uploaded.columns:
                    # Consolidado: extrai cada data e armazena separadamente
                    _df_uploaded['data_snapshot'] = pd.to_datetime(_df_uploaded['data_snapshot'], errors='coerce')
                    _datas_no_arquivo = _df_uploaded['data_snapshot'].dropna().dt.strftime('%Y-%m-%d').unique()
                    for _date_key in _datas_no_arquivo:
                        if _date_key == _HOJE_STR:
                            _ignorados_hoje += 1
                            continue
                        _df_dia = _df_uploaded[_df_uploaded['data_snapshot'].dt.strftime('%Y-%m-%d') == _date_key].copy()
                        _df_dia = _df_dia.drop(columns=['data_snapshot'])
                        st.session_state['snapshots_uploaded'][_date_key] = _df_dia
                        _novos += 1
                else:
                    # Arquivo individual: extrai data do nome do arquivo
                    _stem = _file.name.replace('.parquet', '')
                    _date_part = _stem.replace('sinistros_', '').replace('snapshot_sinistros_', '')
                    try:
                        _date_obj = pd.to_datetime(_date_part, format='%Y-%m-%d')
                        _date_key = _date_obj.strftime('%Y-%m-%d')
                    except Exception:
                        _erros.append(f"`{_file.name}`: nome fora do padrão (esperado sinistros_AAAA-MM-DD.parquet)")
                        continue
                    if _date_key == _HOJE_STR:
                        _ignorados_hoje += 1
                        continue
                    st.session_state['snapshots_uploaded'][_date_key] = _df_uploaded
                    _novos += 1

            # ── Feedback diferenciado por resultado ──────────────────────────
            if _novos > 0:
                _msg = f"✅ **{_novos} data(s) histórica(s) carregada(s) com sucesso.**"
                if _ignorados_hoje > 0:
                    _msg += f" ({_ignorados_hoje} entrada(s) de hoje ignorada(s) — comparar com hoje não faz sentido.)"
                st.success(_msg)
            elif _ignorados_hoje > 0 and not _erros:
                # Caso comum no início: usuário sobe o arquivo recém-baixado
                st.info(
                    f"ℹ️ **O(s) arquivo(s) enviado(s) contém(êm) apenas o dia de hoje "
                    f"({pd.to_datetime(_HOJE_STR).strftime('%d/%m/%Y')}).** "
                    "Não há histórico para adicionar — para a análise comparativa funcionar, "
                    "você precisa subir snapshots de **dias anteriores** (que você baixou em "
                    "execuções passadas). Se este é seu primeiro dia usando o recurso, basta "
                    "baixar o consolidado de hoje, salvar no Drive, e voltar amanhã."
                )
            if _erros:
                for _err in _erros:
                    st.error(f"❌ {_err}")

    with _col_dl:
        if not df_sinistros.empty:
            try:
                _snap_bytes, _qtd_linhas, _qtd_datas = _gerar_snapshot_bytes(df_sinistros, dados_calculados)
                # Indicador claro do que será baixado
                _qtd_hist = len(st.session_state.get('snapshots_uploaded', {}))
                if _qtd_hist == 0:
                    _aviso_dl = (
                        '<div style="font-size:11px;color:#D97706;margin-bottom:6px;">'
                        '⚠️ Nenhum histórico carregado — download terá só o dia de hoje. '
                        'Faça upload do consolidado anterior primeiro se quiser preservar histórico.'
                        '</div>'
                    )
                else:
                    _aviso_dl = (
                        f'<div style="font-size:11px;color:#059669;margin-bottom:6px;">'
                        f'✅ Download incluirá {_qtd_datas} dia(s): hoje + {_qtd_hist} histórico(s).'
                        f'</div>'
                    )
                st.markdown(_aviso_dl, unsafe_allow_html=True)

                st.download_button(
                    label=f"📥 Baixar consolidado ({_qtd_datas} dia(s))",
                    data=_snap_bytes,
                    file_name=f"sinistros_consolidado_{_HOJE_STR}.parquet",
                    mime="application/octet-stream",
                    use_container_width=True,
                    help="Arquivo Parquet único com todos os dias carregados + hoje. Salve no seu Drive substituindo o anterior."
                )
                st.caption(f"📦 ~{len(_snap_bytes)/1024:.0f} KB · {_qtd_linhas:,} linhas".replace(',', '.'))
            except Exception as _e:
                st.error(f"Não foi possível gerar o consolidado: {_e}")

    # Lista snapshots já carregados nesta sessão
    if st.session_state['snapshots_uploaded']:
        _datas_carregadas = sorted(st.session_state['snapshots_uploaded'].keys(), reverse=True)
        _datas_fmt = [pd.to_datetime(d).strftime('%d/%m/%Y') for d in _datas_carregadas]
        # Mostra primeiros 10 + "…" se houver mais
        if len(_datas_fmt) > 10:
            _lista_str = ", ".join(_datas_fmt[:10]) + f", … (+{len(_datas_fmt)-10} mais)"
        else:
            _lista_str = ", ".join(_datas_fmt)
        st.markdown(
            f'<div style="font-size:12px;color:#059669;margin-top:8px;">'
            f'✅ <b>{len(_datas_carregadas)} snapshot(s) ativo(s) na sessão:</b> {_lista_str}'
            f'</div>',
            unsafe_allow_html=True
        )
        _col_clr, _ = st.columns([1, 3])
        with _col_clr:
            if st.button("🗑️ Limpar snapshots carregados", key="btn_clear_snaps"):
                st.session_state['snapshots_uploaded'] = {}
                st.rerun()


# ── Inventário e decodificação dos snapshots para as abas ────────────────────
# Constrói duas estruturas-chave que as abas consomem:
#   _snap_dias            : list[Timestamp] — datas com snapshot disponível (inclui hoje)
#   _df_snap_sin_concat   : DataFrame — todas as linhas SINISTRO de todas as datas
#   _df_snap_agg_concat   : DataFrame — todas as linhas AGG_CARTEIRA de todas as datas
# A "data de hoje" é montada on-the-fly a partir de df_sinistros + dados_calculados.

def _separar_por_tipo(_df):
    """Separa um DataFrame de snapshot em (sin, agg) por tipo_registro."""
    if _df is None or _df.empty:
        return pd.DataFrame(), pd.DataFrame()
    if 'tipo_registro' not in _df.columns:
        # Retrocompat: assume tudo é SINISTRO
        return _df.copy(), pd.DataFrame()
    _sin = _df[_df['tipo_registro'] == 'SINISTRO'].copy()
    _agg = _df[_df['tipo_registro'] == 'AGG_CARTEIRA'].copy()
    return _sin, _agg

def _construir_snap_hoje():
    """Monta o 'snapshot virtual' do dia atual a partir das bases vivas."""
    if df_sinistros.empty:
        return pd.DataFrame(), pd.DataFrame()
    # SINISTRO de hoje (enriquecido com Ramo/Utilização)
    _cols = [c for c in [
        'nr_sinistro', 'N° Apólice', 'nr_ramo',
        'dt_aviso', 'dt_ocorrencia',
        'vl_sinistro_pago', 'vl_sinistro_pendente', 'vl_sinistro_total',
        'vl_despesa_pago', 'vl_despesa_pendente', 'vl_despesa_total',
        'vl_honorario_total', 'vl_salvado_total',
        'Total Sinistro',
        'status_processo', 'status_movimento'
    ] if c in df_sinistros.columns]
    _sin_hoje = df_sinistros[_cols].copy()
    if dados_calculados is not None and 'N° Apólice' in dados_calculados.columns:
        _mapa = dados_calculados[['N° Apólice', 'Ramo', 'Utilização']].drop_duplicates('N° Apólice').copy()
        _mapa['N° Apólice'] = _mapa['N° Apólice'].astype(str)
        _mapa = _coage_categoria_str(_mapa, ['Ramo', 'Utilização'])
        if 'N° Apólice' in _sin_hoje.columns:
            _sin_hoje['N° Apólice'] = _sin_hoje['N° Apólice'].astype(str)
            _sin_hoje = _sin_hoje.merge(_mapa, on='N° Apólice', how='left')
        _sin_hoje = _coage_categoria_str(_sin_hoje, ['Ramo', 'Utilização'])
    _sin_hoje['data_snapshot'] = pd.Timestamp(_HOJE_STR)
    # AGG_CARTEIRA de hoje
    _agg_hoje = pd.DataFrame()
    if dados_calculados is not None and not dados_calculados.empty:
        _dc = dados_calculados.copy()
        _dc = _coage_categoria_str(_dc, ['Ramo', 'Utilização'])
        _dc['_premio_num'] = pd.to_numeric(
            _dc['Soma Prêmio Pago por Apolice'].astype(str)
                .str.replace('.', '', regex=False).str.replace(',', '.', regex=False),
            errors='coerce'
        ).fillna(0)
        _agg_hoje = _dc.groupby(['Ramo', 'Utilização'], dropna=False).agg(
            qtd_apolices_vigentes=('N° Apólice', 'nunique'),
            soma_premio=('_premio_num', 'sum'),
        ).reset_index()
        _agg_hoje = _coage_categoria_str(_agg_hoje, ['Ramo', 'Utilização'])
        _agg_hoje['data_snapshot'] = pd.Timestamp(_HOJE_STR)
    return _sin_hoje, _agg_hoje

# Constrói coleções concatenadas
_sin_partes = []
_agg_partes = []
_snap_dias_set = set()

# Hoje (sempre disponível)
_s_hoje, _a_hoje = _construir_snap_hoje()
if not _s_hoje.empty:
    _sin_partes.append(_s_hoje)
    _snap_dias_set.add(_HOJE_STR)
if not _a_hoje.empty:
    _agg_partes.append(_a_hoje)

# Histórico em sessão
for _date_key, _df_hist in st.session_state.get('snapshots_uploaded', {}).items():
    if _date_key == _HOJE_STR:
        continue
    _h = _df_hist.copy()
    if 'data_snapshot' not in _h.columns:
        _h['data_snapshot'] = pd.Timestamp(_date_key)
    _s, _a = _separar_por_tipo(_h)
    if not _s.empty:
        _sin_partes.append(_s)
    if not _a.empty:
        _agg_partes.append(_a)
    _snap_dias_set.add(_date_key)

_df_snap_sin_concat = pd.concat(_sin_partes, ignore_index=True, sort=False) if _sin_partes else pd.DataFrame()
_df_snap_agg_concat = pd.concat(_agg_partes, ignore_index=True, sort=False) if _agg_partes else pd.DataFrame()
_snap_dias = sorted([pd.to_datetime(d) for d in _snap_dias_set])

# Garante numérico nas colunas de valor
for _c in ['vl_sinistro_pago', 'vl_sinistro_pendente', 'vl_sinistro_total',
           'vl_despesa_pago', 'vl_despesa_pendente', 'vl_despesa_total',
           'vl_honorario_total', 'vl_salvado_total', 'Total Sinistro']:
    if _c in _df_snap_sin_concat.columns:
        _df_snap_sin_concat[_c] = pd.to_numeric(_df_snap_sin_concat[_c], errors='coerce').fillna(0)

# ── Informativo: quantos dias acumulados ─────────────────────────────────────
_qtd_dias_disponiveis = len(_snap_dias)
_dias_historicos = _qtd_dias_disponiveis - 1  # excluindo hoje
if _dias_historicos <= 0:
    st.warning(
        "⚠️ **Você está apenas com o snapshot de hoje.** As 5 abas abaixo precisam "
        "de pelo menos 1 dia histórico para mostrar análises temporais. Suba seu "
        "consolidado antigo pelo botão acima ou volte amanhã após fazer o ciclo "
        "upload/download diário."
    )
else:
    _primeira = min(_snap_dias).strftime('%d/%m/%Y')
    _ultima = max(_snap_dias).strftime('%d/%m/%Y')
    st.success(
        f"✅ **{_qtd_dias_disponiveis} dia(s) de snapshot disponíveis** "
        f"({_primeira} → {_ultima}). Histórico de {_dias_historicos} dia(s) "
        f"para análise temporal."
    )

# ── Helpers compartilhados pelas abas (Onda 2) ───────────────────────────────
_st_fragment_temp = getattr(st, 'fragment', None) or getattr(st, 'experimental_fragment', None)
if _st_fragment_temp is None:
    _st_fragment_temp = lambda _f: _f

def _filtrar_janela(_snap_dias_list, _janela_dias=7):
    """Retorna os snapshots dentro de uma janela de N dias a partir do mais recente.
    Adaptativo: se há menos de N dias acumulados, usa todos. Retorna lista ordenada."""
    if not _snap_dias_list:
        return []
    _dias_sorted = sorted(_snap_dias_list)
    _ultimo = _dias_sorted[-1]
    _corte = _ultimo - pd.Timedelta(days=_janela_dias)
    _janela = [d for d in _dias_sorted if d >= _corte]
    return _janela

def _soma_componentes(_df, _cols):
    """Soma seguramente várias colunas numéricas de um DataFrame."""
    _total = 0.0
    for _c in _cols:
        if _c in _df.columns:
            _total += pd.to_numeric(_df[_c], errors='coerce').fillna(0).sum()
    return float(_total)

def _calcular_ritmos(_sin_concat, _agg_concat, _janela_dias_list):
    """Calcula os 6 KPIs do painel executivo entre primeiro e último snap da janela.
    Usa método (c): variação total / diferença em dias.
    Retorna dict com todos os indicadores ou None se não há dados suficientes."""
    if len(_janela_dias_list) < 2:
        return None
    _primeiro = _janela_dias_list[0]
    _ultimo = _janela_dias_list[-1]
    _dias_entre = max((_ultimo - _primeiro).days, 1)

    _sin_p = _sin_concat[_sin_concat['data_snapshot'] == _primeiro] if not _sin_concat.empty else pd.DataFrame()
    _sin_u = _sin_concat[_sin_concat['data_snapshot'] == _ultimo] if not _sin_concat.empty else pd.DataFrame()

    # Pagamentos (sinistro + despesa)
    _pago_p = _soma_componentes(_sin_p, ['vl_sinistro_pago', 'vl_despesa_pago'])
    _pago_u = _soma_componentes(_sin_u, ['vl_sinistro_pago', 'vl_despesa_pago'])
    _delta_pago = _pago_u - _pago_p
    _ritmo_pago = _delta_pago / _dias_entre

    # Reserva pendente (sinistro + despesa)
    _pend_p = _soma_componentes(_sin_p, ['vl_sinistro_pendente', 'vl_despesa_pendente'])
    _pend_u = _soma_componentes(_sin_u, ['vl_sinistro_pendente', 'vl_despesa_pendente'])
    _delta_pend = _pend_u - _pend_p
    _ritmo_pend = _delta_pend / _dias_entre

    # Net flow = variação total (passivo) por dia
    _total_p = _soma_componentes(_sin_p, ['Total Sinistro'])
    _total_u = _soma_componentes(_sin_u, ['Total Sinistro'])
    _delta_total = _total_u - _total_p
    _net_flow = _delta_total / _dias_entre

    # Taxa de aviso = sinistros novos no período / dias
    _set_p = set(_sin_p['nr_sinistro'].astype(str)) if 'nr_sinistro' in _sin_p.columns else set()
    _set_u = set(_sin_u['nr_sinistro'].astype(str)) if 'nr_sinistro' in _sin_u.columns else set()
    _novos = _set_u - _set_p
    _taxa_aviso = len(_novos) / _dias_entre

    # Taxa de encerramento = sinistros que mudaram para "Liquidado" no período
    _encerrados = 0
    if 'status_movimento' in _sin_p.columns and 'status_movimento' in _sin_u.columns:
        _comuns = _set_p & _set_u
        if _comuns:
            _map_p = _sin_p.set_index(_sin_p['nr_sinistro'].astype(str))['status_movimento'].to_dict()
            _map_u = _sin_u.set_index(_sin_u['nr_sinistro'].astype(str))['status_movimento'].to_dict()
            for _nrs in _comuns:
                _sp = str(_map_p.get(_nrs, '')).strip().lower()
                _su = str(_map_u.get(_nrs, '')).strip().lower()
                if 'liquid' not in _sp and 'liquid' in _su:
                    _encerrados += 1
    _taxa_encerramento = _encerrados / _dias_entre

    # Score composto
    _alertas = 0
    if _ritmo_pend > _ritmo_pago * 1.2 and _ritmo_pend > 0:
        _alertas += 1
    if _taxa_aviso > _taxa_encerramento * 1.5 and _taxa_aviso > 0.5:
        _alertas += 1
    if _net_flow > 0:
        _alertas += 1
    if _alertas == 0:
        _score_cor, _score_label = '#16A34A', '🟢 Saudável'
    elif _alertas == 1:
        _score_cor, _score_label = '#D97706', '🟡 Atenção'
    else:
        _score_cor, _score_label = '#DC2626', '🔴 Crítico'

    return {
        'ritmo_pago': _ritmo_pago,
        'ritmo_pend': _ritmo_pend,
        'net_flow': _net_flow,
        'taxa_aviso': _taxa_aviso,
        'taxa_encerramento': _taxa_encerramento,
        'score_cor': _score_cor,
        'score_label': _score_label,
        'dias_entre': _dias_entre,
        'primeiro': _primeiro,
        'ultimo': _ultimo,
        'qtd_dias': len(_janela_dias_list),
    }

def _card_ritmo(_titulo, _valor, _subtitulo, _cor='#0F172A'):
    """Renderiza um card de KPI no padrão visual da página."""
    _card_base = (
        "background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;"
        "padding:14px 16px;height:100%;"
    )
    st.markdown(
        f'<div style="{_card_base}">'
        f'<div style="font-size:12px;color:#64748B;">{_titulo}</div>'
        f'<div style="font-size:20px;font-weight:600;color:{_cor};margin-top:4px;">{_valor}</div>'
        f'<div style="font-size:11px;color:#94A3B8;margin-top:2px;">{_subtitulo}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

# ── 5 abas ───────────────────────────────────────────────────────────────────
_tab_visao, _tab_segmento, _tab_drill, _tab_reserva, _tab_alertas = st.tabs([
    "🎯 Visão Geral",
    "🔍 Por Segmento",
    "📋 Drill-down",
    "📐 Reserva & Atuarial",
    "🚨 Alertas",
])

# ─── ABA 1 — VISÃO GERAL ─────────────────────────────────────────────────────
with _tab_visao:
    @_st_fragment_temp
    def _render_aba_visao_geral():
        if len(_snap_dias) < 2:
            st.info("⏳ Aguardando ao menos 2 dias de snapshot para calcular ritmos e tendências.")
            return

        # ── Painel Executivo (6 cards de ritmo) ──────────────────────────────
        st.markdown(
            '<p class="section-label">⚡ Painel Executivo — Ritmo e Tendência</p>',
            unsafe_allow_html=True
        )
        _janela = _filtrar_janela(_snap_dias, _janela_dias=7)
        _ritmos = _calcular_ritmos(_df_snap_sin_concat, _df_snap_agg_concat, _janela)

        if _ritmos is None:
            st.info("Sem dados suficientes para calcular ritmos.")
        else:
            _aviso_janela = (
                f"📅 Calculado entre {_ritmos['primeiro'].strftime('%d/%m/%Y')} e "
                f"{_ritmos['ultimo'].strftime('%d/%m/%Y')} "
                f"({_ritmos['dias_entre']} dia(s), {_ritmos['qtd_dias']} snapshot(s))."
            )
            if _ritmos['qtd_dias'] < 7:
                _aviso_janela += " *Janela ainda em formação — precisão melhora com mais dias acumulados.*"
            st.caption(_aviso_janela)

            _c1, _c2, _c3 = st.columns(3)
            with _c1:
                _cor = '#DC2626' if _ritmos['ritmo_pago'] > 50000 else '#0F172A'
                _card_ritmo(
                    '⚡ Velocidade de pagamento',
                    f"R$ {formatar_valor_br(_ritmos['ritmo_pago'])}/dia",
                    'caixa saindo (sinistro + despesa)',
                    _cor
                )
            with _c2:
                _cor = '#DC2626' if _ritmos['ritmo_pend'] > 0 else '#059669'
                _sinal = '+' if _ritmos['ritmo_pend'] >= 0 else ''
                _card_ritmo(
                    '📈 Constituição de reserva',
                    f"{_sinal}R$ {formatar_valor_br(_ritmos['ritmo_pend'])}/dia",
                    'passivo crescendo (pendente)',
                    _cor
                )
            with _c3:
                _cor = '#DC2626' if _ritmos['net_flow'] > 0 else '#059669'
                _sinal = '+' if _ritmos['net_flow'] >= 0 else ''
                _card_ritmo(
                    '🔄 Net flow (Δ Total Sinistro)',
                    f"{_sinal}R$ {formatar_valor_br(_ritmos['net_flow'])}/dia",
                    'positivo = passivo crescendo',
                    _cor
                )

            _c4, _c5, _c6 = st.columns(3)
            with _c4:
                _card_ritmo(
                    '📌 Taxa de aviso',
                    f"{_ritmos['taxa_aviso']:.2f} sin/dia",
                    'sinistros novos por dia'
                )
            with _c5:
                _card_ritmo(
                    '✅ Taxa de encerramento',
                    f"{_ritmos['taxa_encerramento']:.2f} sin/dia",
                    'liquidados por dia'
                )
            with _c6:
                _card_ritmo(
                    '🚦 Score de saúde',
                    _ritmos['score_label'],
                    'baseado em ritmo + fluxo + balanço',
                    _ritmos['score_cor']
                )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")

        # ── Evolução Temporal da Sinistralidade — 2 sub-abas ─────────────────
        st.markdown(
            '<p class="section-label">📊 Evolução Temporal da Sinistralidade</p>',
            unsafe_allow_html=True
        )
        _sub_a, _sub_b = st.tabs([
            "🔒 Sinistralidade do MESMO período (revisão com o tempo)",
            "🔄 Sinistralidade INDEPENDENTE por snapshot"
        ])

        # ── Sub-aba A: Sinistralidade do mesmo período ───────────────────────
        with _sub_a:
            st.caption(
                "📌 Fixa o período do slider (lado esquerdo da página) e mostra como a "
                "sinistralidade *daquele mesmo período* foi sendo ajustada pra cima/baixo "
                "conforme novos snapshots chegaram. Revela o efeito da cauda histórica."
            )

            # Prêmio do período do slider (fixo, não varia entre snapshots)
            _premio_periodo_slider = df_para_soma['Soma Prêmio Pago por Apolice'].sum() if not df_para_soma.empty else 0

            if _premio_periodo_slider <= 0:
                st.info("Prêmio do período do slider é zero — impossível calcular sinistralidade.")
            else:
                # Filtra sinistros do período do slider (apolices visíveis no slider)
                _apolices_periodo = set(df_geral_periodo['N° Apólice'].astype(str).unique()) if not df_geral_periodo.empty else set()

                _pontos = []
                for _data in _snap_dias:
                    _sin_d = _df_snap_sin_concat[_df_snap_sin_concat['data_snapshot'] == _data].copy()
                    if _sin_d.empty:
                        continue
                    # Filtra apenas sinistros das apólices do período do slider
                    if 'N° Apólice' in _sin_d.columns and _apolices_periodo:
                        _sin_d['N° Apólice'] = _sin_d['N° Apólice'].astype(str)
                        _sin_d_filt = _sin_d[_sin_d['N° Apólice'].isin(_apolices_periodo)]
                    else:
                        _sin_d_filt = _sin_d
                    _total = pd.to_numeric(_sin_d_filt.get('Total Sinistro', 0), errors='coerce').fillna(0).sum()
                    _sinistralidade = (_total / _premio_periodo_slider) * 100
                    _pontos.append({'data': _data, 'sinistralidade': _sinistralidade, 'total_sinistro': _total})

                if not _pontos:
                    st.info("Sem pontos suficientes.")
                else:
                    _df_plot = pd.DataFrame(_pontos)
                    _fig = go.Figure()
                    _fig.add_trace(go.Scatter(
                        x=_df_plot['data'], y=_df_plot['sinistralidade'],
                        mode='lines+markers+text',
                        text=[f"{v:.1f}%" for v in _df_plot['sinistralidade']],
                        textposition='top center',
                        line=dict(color='#1a56db', width=2),
                        marker=dict(size=10, color='#1a56db'),
                        hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Sinistralidade: %{y:.2f}%<br>Total Sinistro: R$ %{customdata:,.2f}<extra></extra>',
                        customdata=_df_plot['total_sinistro']
                    ))
                    _fig.update_layout(
                        title=dict(
                            text=f'Sinistralidade do período fixo · Prêmio base: R$ {formatar_valor_br(_premio_periodo_slider)}',
                            font=dict(size=14)
                        ),
                        height=380,
                        margin=dict(l=20, r=20, t=50, b=20),
                        plot_bgcolor='white',
                        yaxis=dict(title='Sinistralidade (%)', gridcolor='#E2E8F0'),
                        xaxis=dict(title='Data do snapshot', gridcolor='#E2E8F0'),
                    )
                    st.plotly_chart(_fig, use_container_width=True, config={'displayModeBar': False})

                    if len(_pontos) >= 2:
                        _delta_pp = _pontos[-1]['sinistralidade'] - _pontos[0]['sinistralidade']
                        _cor_d = '#DC2626' if _delta_pp > 0 else '#059669'
                        _sinal = '+' if _delta_pp >= 0 else ''
                        st.markdown(
                            f'<div style="background:#F8FAFC;border-radius:8px;padding:10px 14px;font-size:13px;">'
                            f'<b>Variação acumulada da sinistralidade do mesmo período:</b> '
                            f'<span style="color:{_cor_d};font-weight:600;">{_sinal}{_delta_pp:.2f} pp</span> '
                            f'entre {_pontos[0]["data"].strftime("%d/%m/%Y")} e {_pontos[-1]["data"].strftime("%d/%m/%Y")}.'
                            f'</div>',
                            unsafe_allow_html=True
                        )

        # ── Sub-aba B: Sinistralidade independente ───────────────────────────
        with _sub_b:
            st.caption(
                "📌 Cada ponto = sinistralidade da carteira **inteira** naquele dia, "
                "usando toda a base do snapshot (sem filtro do slider). Numerador e "
                "denominador mudam juntos — movimento puro da carteira."
            )

            _pontos = []
            for _data in _snap_dias:
                _sin_d = _df_snap_sin_concat[_df_snap_sin_concat['data_snapshot'] == _data]
                _agg_d = _df_snap_agg_concat[_df_snap_agg_concat['data_snapshot'] == _data] if not _df_snap_agg_concat.empty else pd.DataFrame()
                _total_sin = pd.to_numeric(_sin_d.get('Total Sinistro', 0), errors='coerce').fillna(0).sum() if not _sin_d.empty else 0
                _premio = pd.to_numeric(_agg_d.get('soma_premio', 0), errors='coerce').fillna(0).sum() if not _agg_d.empty else 0
                if _premio > 0:
                    _sinistralidade = (_total_sin / _premio) * 100
                    _pontos.append({
                        'data': _data, 'sinistralidade': _sinistralidade,
                        'total_sinistro': _total_sin, 'premio': _premio
                    })

            if not _pontos:
                st.info(
                    "ℹ️ Sem dados de prêmio (AGG_CARTEIRA) nos snapshots disponíveis. "
                    "A sinistralidade independente requer snapshots gerados pela nova versão "
                    "do app (após a Onda 1). Snapshots antigos só serão usados aqui após você "
                    "rodar pelo menos um ciclo upload/download com a versão atual."
                )
            else:
                _df_plot = pd.DataFrame(_pontos)
                _fig = go.Figure()
                _fig.add_trace(go.Scatter(
                    x=_df_plot['data'], y=_df_plot['sinistralidade'],
                    mode='lines+markers+text',
                    text=[f"{v:.1f}%" for v in _df_plot['sinistralidade']],
                    textposition='top center',
                    line=dict(color='#7c1f4a', width=2),
                    marker=dict(size=10, color='#7c1f4a'),
                    hovertemplate=(
                        '<b>%{x|%d/%m/%Y}</b><br>Sinistralidade: %{y:.2f}%<br>'
                        'Total Sinistro: R$ %{customdata[0]:,.2f}<br>'
                        'Prêmio: R$ %{customdata[1]:,.2f}<extra></extra>'
                    ),
                    customdata=list(zip(_df_plot['total_sinistro'], _df_plot['premio']))
                ))
                _fig.update_layout(
                    title=dict(text='Sinistralidade da carteira inteira por snapshot', font=dict(size=14)),
                    height=380,
                    margin=dict(l=20, r=20, t=50, b=20),
                    plot_bgcolor='white',
                    yaxis=dict(title='Sinistralidade (%)', gridcolor='#E2E8F0'),
                    xaxis=dict(title='Data do snapshot', gridcolor='#E2E8F0'),
                )
                st.plotly_chart(_fig, use_container_width=True, config={'displayModeBar': False})

    _render_aba_visao_geral()

# ─── ABA 2 — POR SEGMENTO ────────────────────────────────────────────────────
with _tab_segmento:
    @_st_fragment_temp
    def _render_aba_segmento():
        if len(_snap_dias) < 2:
            st.info("⏳ Aguardando ao menos 2 dias de snapshot para análise por segmento.")
            return

        # Verifica cobertura de Ramo/Utilização nos snapshots
        _tem_ramo = 'Ramo' in _df_snap_sin_concat.columns and _df_snap_sin_concat['Ramo'].notna().any()
        if not _tem_ramo:
            st.warning(
                "Os snapshots disponíveis não contêm Ramo/Utilização. Faça o ciclo "
                "upload/download uma vez com a versão atual do app para enriquecer "
                "automaticamente o histórico via merge com dados_calculados."
            )
            return

        # Seletor de dimensão
        _dim = st.radio(
            "Agrupar por:",
            options=['Ramo', 'Utilização'],
            horizontal=True,
            key='seg_agrupar_radio'
        )

        # ── 1. Evolução por segmento — Total Sinistro ────────────────────────
        st.markdown(
            f'<p class="section-label">📈 Evolução do Total Sinistro por {_dim}</p>',
            unsafe_allow_html=True
        )
        _evol = _df_snap_sin_concat.groupby(['data_snapshot', _dim], as_index=False, dropna=False).agg(
            Total_Sinistro=('Total Sinistro', 'sum'),
            qtd_sinistros=('nr_sinistro', 'nunique')
        )
        _evol[_dim] = _evol[_dim].fillna('(não informado)').astype(str)

        _fig_evol = go.Figure()
        for _seg in sorted(_evol[_dim].unique()):
            _d = _evol[_evol[_dim] == _seg].sort_values('data_snapshot')
            _fig_evol.add_trace(go.Scatter(
                x=_d['data_snapshot'], y=_d['Total_Sinistro'],
                mode='lines+markers', name=_seg,
                hovertemplate=f'<b>{_seg}</b><br>%{{x|%d/%m/%Y}}<br>R$ %{{y:,.2f}}<br>%{{customdata}} sinistros<extra></extra>',
                customdata=_d['qtd_sinistros']
            ))
        _fig_evol.update_layout(
            height=420, margin=dict(l=20, r=20, t=30, b=20),
            plot_bgcolor='white',
            yaxis=dict(title='Total Sinistro (R$)', gridcolor='#E2E8F0'),
            xaxis=dict(title='Data do snapshot', gridcolor='#E2E8F0'),
            legend=dict(orientation='h', yanchor='bottom', y=-0.35, xanchor='center', x=0.5),
        )
        st.plotly_chart(_fig_evol, use_container_width=True, config={'displayModeBar': False})

        # ── 2. Variação % entre primeiro e último snapshot ───────────────────
        st.markdown(
            f'<p class="section-label">📊 Variação % do Total Sinistro por {_dim}</p>',
            unsafe_allow_html=True
        )
        _primeiro_dia = _snap_dias[0]
        _ultimo_dia = _snap_dias[-1]
        _evol_p = _evol[_evol['data_snapshot'] == _primeiro_dia].set_index(_dim)['Total_Sinistro']
        _evol_u = _evol[_evol['data_snapshot'] == _ultimo_dia].set_index(_dim)['Total_Sinistro']
        _var = pd.DataFrame({'Inicial': _evol_p, 'Final': _evol_u}).fillna(0)
        _var['Delta_R$'] = _var['Final'] - _var['Inicial']
        _var['Var_%'] = ((_var['Final'] - _var['Inicial']) / _var['Inicial'].replace(0, float('nan')) * 100).fillna(0)
        _var = _var.sort_values('Delta_R$', ascending=True)

        _fig_var = go.Figure()
        _fig_var.add_trace(go.Bar(
            x=_var['Delta_R$'], y=_var.index,
            orientation='h',
            marker_color=['#DC2626' if v > 0 else '#059669' for v in _var['Delta_R$']],
            text=[f"{'+' if v >= 0 else ''}R$ {formatar_valor_br(v)} ({p:+.1f}%)"
                  for v, p in zip(_var['Delta_R$'], _var['Var_%'])],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Δ R$: %{x:,.2f}<extra></extra>',
        ))
        _fig_var.update_layout(
            title=dict(
                text=f"Δ Total Sinistro entre {_primeiro_dia.strftime('%d/%m/%Y')} e {_ultimo_dia.strftime('%d/%m/%Y')}",
                font=dict(size=13)
            ),
            height=max(300, 60 + 35 * len(_var)),
            margin=dict(l=20, r=120, t=50, b=20),
            plot_bgcolor='white',
            xaxis=dict(title='Variação (R$)', gridcolor='#E2E8F0'),
        )
        st.plotly_chart(_fig_var, use_container_width=True, config={'displayModeBar': False})

        # ── 3. Composição da carteira ao longo do tempo (AGG_CARTEIRA) ───────
        if not _df_snap_agg_concat.empty and _dim in _df_snap_agg_concat.columns:
            st.markdown(
                f'<p class="section-label">🏛️ Composição da Carteira por {_dim} ao longo do tempo</p>',
                unsafe_allow_html=True
            )
            _col_a, _col_b = st.columns(2)
            with _col_a:
                _comp_qtd = _df_snap_agg_concat.groupby(['data_snapshot', _dim], as_index=False).agg(
                    qtd=('qtd_apolices_vigentes', 'sum')
                )
                _fig_cq = go.Figure()
                for _seg in sorted(_comp_qtd[_dim].unique()):
                    _d = _comp_qtd[_comp_qtd[_dim] == _seg].sort_values('data_snapshot')
                    _fig_cq.add_trace(go.Scatter(
                        x=_d['data_snapshot'], y=_d['qtd'],
                        mode='lines', name=_seg, stackgroup='one',
                        hovertemplate=f'<b>{_seg}</b><br>%{{y:,.0f}} apólices<extra></extra>'
                    ))
                _fig_cq.update_layout(
                    title=dict(text='Quantidade de apólices vigentes', font=dict(size=13)),
                    height=320, margin=dict(l=20, r=20, t=40, b=20),
                    plot_bgcolor='white', showlegend=False,
                    yaxis=dict(title='Qtd apólices', gridcolor='#E2E8F0'),
                )
                st.plotly_chart(_fig_cq, use_container_width=True, config={'displayModeBar': False})
            with _col_b:
                _comp_pre = _df_snap_agg_concat.groupby(['data_snapshot', _dim], as_index=False).agg(
                    premio=('soma_premio', 'sum')
                )
                _fig_cp = go.Figure()
                for _seg in sorted(_comp_pre[_dim].unique()):
                    _d = _comp_pre[_comp_pre[_dim] == _seg].sort_values('data_snapshot')
                    _fig_cp.add_trace(go.Scatter(
                        x=_d['data_snapshot'], y=_d['premio'],
                        mode='lines', name=_seg, stackgroup='one',
                        hovertemplate=f'<b>{_seg}</b><br>R$ %{{y:,.2f}}<extra></extra>'
                    ))
                _fig_cp.update_layout(
                    title=dict(text='Soma de prêmio', font=dict(size=13)),
                    height=320, margin=dict(l=20, r=20, t=40, b=20),
                    plot_bgcolor='white', showlegend=False,
                    yaxis=dict(title='Prêmio (R$)', gridcolor='#E2E8F0'),
                )
                st.plotly_chart(_fig_cp, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info(
                f"ℹ️ Composição da carteira por {_dim} requer snapshots da Onda 1+ "
                "(com AGG_CARTEIRA). Após um ciclo upload/download com a versão atual, "
                "este gráfico passa a funcionar."
            )

        # ── 4. Sinistralidade por segmento ao longo do tempo ─────────────────
        if not _df_snap_agg_concat.empty and _dim in _df_snap_agg_concat.columns:
            st.markdown(
                f'<p class="section-label">📐 Sinistralidade por {_dim} ao longo do tempo</p>',
                unsafe_allow_html=True
            )
            # Numerador (Total Sinistro por seg×data) + Denominador (soma_premio por seg×data)
            _num = _df_snap_sin_concat.groupby(['data_snapshot', _dim], as_index=False, dropna=False)['Total Sinistro'].sum()
            _den = _df_snap_agg_concat.groupby(['data_snapshot', _dim], as_index=False, dropna=False)['soma_premio'].sum()
            _num[_dim] = _num[_dim].fillna('(não informado)').astype(str)
            _den[_dim] = _den[_dim].fillna('(não informado)').astype(str)
            _sin_seg = _num.merge(_den, on=['data_snapshot', _dim], how='inner')
            _sin_seg['sinistralidade'] = (_sin_seg['Total Sinistro'] / _sin_seg['soma_premio'].replace(0, float('nan'))) * 100
            _sin_seg = _sin_seg.dropna(subset=['sinistralidade'])

            if _sin_seg.empty:
                st.info("Sem dados suficientes para calcular sinistralidade por segmento.")
            else:
                _fig_sin = go.Figure()
                for _seg in sorted(_sin_seg[_dim].unique()):
                    _d = _sin_seg[_sin_seg[_dim] == _seg].sort_values('data_snapshot')
                    _fig_sin.add_trace(go.Scatter(
                        x=_d['data_snapshot'], y=_d['sinistralidade'],
                        mode='lines+markers', name=_seg,
                        hovertemplate=f'<b>{_seg}</b><br>%{{x|%d/%m/%Y}}<br>Sin: %{{y:.2f}}%<extra></extra>'
                    ))
                _fig_sin.update_layout(
                    height=400, margin=dict(l=20, r=20, t=30, b=20),
                    plot_bgcolor='white',
                    yaxis=dict(title='Sinistralidade (%)', gridcolor='#E2E8F0'),
                    xaxis=dict(title='Data do snapshot', gridcolor='#E2E8F0'),
                    legend=dict(orientation='h', yanchor='bottom', y=-0.35, xanchor='center', x=0.5),
                )
                st.plotly_chart(_fig_sin, use_container_width=True, config={'displayModeBar': False})

    _render_aba_segmento()

# ─── ABA 3 — DRILL-DOWN ──────────────────────────────────────────────────────
with _tab_drill:
    @_st_fragment_temp
    def _render_aba_drill():
        if len(_snap_dias) < 2:
            st.info("⏳ Aguardando ao menos 2 dias de snapshot para análise de drill-down.")
            return

        if _df_snap_sin_concat.empty:
            st.info("Sem dados de sinistros nos snapshots.")
            return

        # ── Calcula deltas por sinistro (entre primeiro e último snapshot) ───
        _primeiro_dia = _snap_dias[0]
        _ultimo_dia = _snap_dias[-1]

        _sin_p = _df_snap_sin_concat[_df_snap_sin_concat['data_snapshot'] == _primeiro_dia].copy()
        _sin_u = _df_snap_sin_concat[_df_snap_sin_concat['data_snapshot'] == _ultimo_dia].copy()
        _sin_p['nr_sinistro'] = _sin_p['nr_sinistro'].astype(str)
        _sin_u['nr_sinistro'] = _sin_u['nr_sinistro'].astype(str)

        # Merge para calcular deltas (sinistros em comum)
        _cols_merge = ['nr_sinistro']
        for _c in ['vl_sinistro_pago', 'vl_sinistro_pendente', 'vl_despesa_pago',
                   'vl_despesa_pendente', 'Total Sinistro']:
            if _c in _sin_p.columns and _c in _sin_u.columns:
                _cols_merge.append(_c)
        _cols_extra = []
        for _c in ['Ramo', 'Utilização', 'dt_aviso', 'N° Apólice']:
            if _c in _sin_u.columns:
                _cols_extra.append(_c)

        _m = _sin_p[_cols_merge].merge(
            _sin_u[_cols_merge + _cols_extra].drop_duplicates('nr_sinistro'),
            on='nr_sinistro', how='inner', suffixes=('_old', '_now')
        )
        if 'Total Sinistro_old' in _m.columns and 'Total Sinistro_now' in _m.columns:
            _m['delta_total'] = _m['Total Sinistro_now'] - _m['Total Sinistro_old']
            _m['var_pct'] = ((_m['Total Sinistro_now'] - _m['Total Sinistro_old']) /
                             _m['Total Sinistro_old'].replace(0, float('nan')) * 100).fillna(0)
        else:
            _m['delta_total'] = 0
            _m['var_pct'] = 0

        # ── Sub-abas: Histórico individual + Rankings ────────────────────────
        _sub_h, _sub_c, _sub_r, _sub_v = st.tabs([
            "🔍 Histórico individual",
            "📈 Top que cresceram",
            "📉 Top que reduziram",
            "🌪️ Mais voláteis",
        ])

        # ── Sub-aba H: histórico individual ──────────────────────────────────
        with _sub_h:
            st.caption(
                "Selecione um sinistro e veja sua trajetória completa de vl_pago, "
                "vl_pendente e Total Sinistro através dos snapshots."
            )

            # Lista de opções com label informativo
            _sin_unicos = _df_snap_sin_concat.drop_duplicates('nr_sinistro').copy()
            _sin_unicos['nr_sinistro'] = _sin_unicos['nr_sinistro'].astype(str)

            def _format_opt(_nr):
                _row = _sin_unicos[_sin_unicos['nr_sinistro'] == _nr]
                if _row.empty:
                    return _nr
                _r = _row.iloc[0]
                _ramo = str(_r.get('Ramo', '')) if pd.notna(_r.get('Ramo', None)) else '-'
                _aviso = str(_r.get('dt_aviso', '')) if pd.notna(_r.get('dt_aviso', None)) else '-'
                return f"{_nr} · {_ramo} · {_aviso[:10] if _aviso else '-'}"

            _opcoes_nrs = sorted(_sin_unicos['nr_sinistro'].unique().tolist())
            _escolha_nr = st.selectbox(
                "Buscar sinistro:",
                options=_opcoes_nrs,
                format_func=_format_opt,
                key='drill_seletor_sinistro',
                help="Digite para filtrar por nr_sinistro. Mostra Ramo e data de aviso."
            )

            if _escolha_nr:
                _hist = _df_snap_sin_concat[
                    _df_snap_sin_concat['nr_sinistro'].astype(str) == _escolha_nr
                ].copy().sort_values('data_snapshot')

                if _hist.empty:
                    st.info("Sem histórico nos snapshots para esse sinistro.")
                else:
                    # Garante colunas numéricas
                    for _c in ['vl_sinistro_pago', 'vl_sinistro_pendente', 'Total Sinistro']:
                        if _c in _hist.columns:
                            _hist[_c] = pd.to_numeric(_hist[_c], errors='coerce').fillna(0)

                    # Cards de info do sinistro
                    _r0 = _hist.iloc[-1]
                    _col_a, _col_b, _col_c = st.columns(3)
                    with _col_a:
                        _ramo = _r0.get('Ramo', '-') if pd.notna(_r0.get('Ramo', None)) else '-'
                        _uti = _r0.get('Utilização', '-') if pd.notna(_r0.get('Utilização', None)) else '-'
                        st.markdown(
                            f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;'
                            f'border-radius:10px;padding:14px;">'
                            f'<div style="font-size:11px;color:#64748B;">SINISTRO</div>'
                            f'<div style="font-size:18px;font-weight:600;">{_escolha_nr}</div>'
                            f'<div style="font-size:11px;color:#94A3B8;margin-top:6px;">'
                            f'{_ramo} · {_uti}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    with _col_b:
                        _aviso_s = str(_r0.get('dt_aviso', '-'))
                        st.markdown(
                            f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;'
                            f'border-radius:10px;padding:14px;">'
                            f'<div style="font-size:11px;color:#64748B;">DATA DE AVISO</div>'
                            f'<div style="font-size:18px;font-weight:600;">{_aviso_s[:10]}</div>'
                            f'<div style="font-size:11px;color:#94A3B8;margin-top:6px;">'
                            f'{len(_hist)} snapshot(s) com este sinistro</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    with _col_c:
                        _total_atual = _hist.iloc[-1].get('Total Sinistro', 0)
                        _total_inicial = _hist.iloc[0].get('Total Sinistro', 0)
                        _delta = _total_atual - _total_inicial
                        _cor = '#DC2626' if _delta > 0 else ('#059669' if _delta < 0 else '#0F172A')
                        _sinal = '+' if _delta >= 0 else ''
                        st.markdown(
                            f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;'
                            f'border-radius:10px;padding:14px;">'
                            f'<div style="font-size:11px;color:#64748B;">Δ TOTAL NO PERÍODO</div>'
                            f'<div style="font-size:18px;font-weight:600;color:{_cor};">'
                            f'{_sinal}R$ {formatar_valor_br(_delta)}</div>'
                            f'<div style="font-size:11px;color:#94A3B8;margin-top:6px;">'
                            f'Atual: R$ {formatar_valor_br(_total_atual)}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Gráfico de evolução
                    _fig_h = go.Figure()
                    if 'vl_sinistro_pago' in _hist.columns:
                        _fig_h.add_trace(go.Scatter(
                            x=_hist['data_snapshot'], y=_hist['vl_sinistro_pago'],
                            mode='lines+markers', name='Pago (sinistro)',
                            line=dict(color='#059669', width=2),
                            hovertemplate='Pago: R$ %{y:,.2f}<extra></extra>'
                        ))
                    if 'vl_sinistro_pendente' in _hist.columns:
                        _fig_h.add_trace(go.Scatter(
                            x=_hist['data_snapshot'], y=_hist['vl_sinistro_pendente'],
                            mode='lines+markers', name='Pendente (reserva)',
                            line=dict(color='#D97706', width=2),
                            hovertemplate='Pendente: R$ %{y:,.2f}<extra></extra>'
                        ))
                    if 'Total Sinistro' in _hist.columns:
                        _fig_h.add_trace(go.Scatter(
                            x=_hist['data_snapshot'], y=_hist['Total Sinistro'],
                            mode='lines+markers', name='Total Sinistro',
                            line=dict(color='#1a56db', width=3),
                            hovertemplate='Total: R$ %{y:,.2f}<extra></extra>'
                        ))
                    _fig_h.update_layout(
                        title=dict(text=f"Trajetória do sinistro {_escolha_nr}", font=dict(size=14)),
                        height=400, margin=dict(l=20, r=20, t=50, b=20),
                        plot_bgcolor='white',
                        yaxis=dict(title='Valor (R$)', gridcolor='#E2E8F0'),
                        xaxis=dict(title='Data do snapshot', gridcolor='#E2E8F0'),
                        hovermode='x unified',
                        legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5),
                    )
                    st.plotly_chart(_fig_h, use_container_width=True, config={'displayModeBar': False})

                    # Tabela com snapshots numéricos
                    with st.expander("📋 Tabela com valores de cada snapshot", expanded=False):
                        _cols_tab = ['data_snapshot']
                        for _c in ['vl_sinistro_pago', 'vl_sinistro_pendente',
                                   'vl_despesa_pago', 'vl_despesa_pendente', 'Total Sinistro',
                                   'status_processo', 'status_movimento']:
                            if _c in _hist.columns:
                                _cols_tab.append(_c)
                        _hist_view = _hist[_cols_tab].copy()
                        _hist_view['data_snapshot'] = _hist_view['data_snapshot'].dt.strftime('%d/%m/%Y')
                        for _c in _cols_tab:
                            if _c.startswith('vl_') or _c == 'Total Sinistro':
                                _hist_view[_c] = _hist_view[_c].apply(lambda v: f"R$ {formatar_valor_br(v)}")
                        st.dataframe(_hist_view, use_container_width=True, hide_index=True)

        # ── Sub-aba C: Top que CRESCERAM ─────────────────────────────────────
        with _sub_c:
            st.caption(
                f"Sinistros com maior aumento de Total Sinistro entre "
                f"{_primeiro_dia.strftime('%d/%m/%Y')} e {_ultimo_dia.strftime('%d/%m/%Y')}."
            )
            if _m.empty or 'delta_total' not in _m.columns:
                st.info("Sem dados de delta calculáveis.")
            else:
                _cresceram = _m[_m['delta_total'] > 0.01].sort_values('delta_total', ascending=False).head(20).copy()
                if _cresceram.empty:
                    st.info("Nenhum sinistro com aumento detectado no período.")
                else:
                    _cols_show = ['nr_sinistro']
                    if 'Ramo' in _cresceram.columns: _cols_show.append('Ramo')
                    if 'Utilização' in _cresceram.columns: _cols_show.append('Utilização')
                    _cresceram['Δ Total R$'] = _cresceram['delta_total'].apply(
                        lambda v: f"+R$ {formatar_valor_br(v)}"
                    )
                    _cresceram['Var %'] = _cresceram['var_pct'].apply(lambda v: f"{v:+.1f}%")
                    if 'Total Sinistro_now' in _cresceram.columns:
                        _cresceram['Total Atual'] = _cresceram['Total Sinistro_now'].apply(
                            lambda v: f"R$ {formatar_valor_br(v)}"
                        )
                    _cols_show += ['Δ Total R$', 'Var %', 'Total Atual']
                    _cols_show = [c for c in _cols_show if c in _cresceram.columns]
                    st.dataframe(
                        _cresceram[_cols_show].rename(columns={'nr_sinistro': 'N° Sinistro'}),
                        use_container_width=True, hide_index=True
                    )

        # ── Sub-aba R: Top que REDUZIRAM ─────────────────────────────────────
        with _sub_r:
            st.caption(
                "Sinistros com maior redução de Total Sinistro no período "
                "(encerramentos favoráveis, salvados, recuperações)."
            )
            if _m.empty or 'delta_total' not in _m.columns:
                st.info("Sem dados de delta calculáveis.")
            else:
                _reduziram = _m[_m['delta_total'] < -0.01].sort_values('delta_total', ascending=True).head(20).copy()
                if _reduziram.empty:
                    st.info("Nenhum sinistro com redução detectada no período.")
                else:
                    _cols_show = ['nr_sinistro']
                    if 'Ramo' in _reduziram.columns: _cols_show.append('Ramo')
                    if 'Utilização' in _reduziram.columns: _cols_show.append('Utilização')
                    _reduziram['Δ Total R$'] = _reduziram['delta_total'].apply(
                        lambda v: f"R$ {formatar_valor_br(v)}"
                    )
                    _reduziram['Var %'] = _reduziram['var_pct'].apply(lambda v: f"{v:+.1f}%")
                    if 'Total Sinistro_now' in _reduziram.columns:
                        _reduziram['Total Atual'] = _reduziram['Total Sinistro_now'].apply(
                            lambda v: f"R$ {formatar_valor_br(v)}"
                        )
                    _cols_show += ['Δ Total R$', 'Var %', 'Total Atual']
                    _cols_show = [c for c in _cols_show if c in _reduziram.columns]
                    st.dataframe(
                        _reduziram[_cols_show].rename(columns={'nr_sinistro': 'N° Sinistro'}),
                        use_container_width=True, hide_index=True
                    )

        # ── Sub-aba V: Mais VOLÁTEIS ─────────────────────────────────────────
        with _sub_v:
            st.caption(
                "Sinistros que oscilaram mais ao longo dos snapshots. "
                "Calculado por coeficiente de variação (desvio padrão / média) "
                "do Total Sinistro. Requer pelo menos 3 snapshots com o mesmo sinistro."
            )
            if 'Total Sinistro' not in _df_snap_sin_concat.columns:
                st.info("Sem coluna Total Sinistro nos snapshots.")
            else:
                _por_sin = _df_snap_sin_concat.copy()
                _por_sin['nr_sinistro'] = _por_sin['nr_sinistro'].astype(str)
                _por_sin['Total Sinistro'] = pd.to_numeric(_por_sin['Total Sinistro'], errors='coerce').fillna(0)
                _stats = _por_sin.groupby('nr_sinistro').agg(
                    n_pontos=('data_snapshot', 'nunique'),
                    media=('Total Sinistro', 'mean'),
                    desvio=('Total Sinistro', 'std'),
                    min_v=('Total Sinistro', 'min'),
                    max_v=('Total Sinistro', 'max'),
                ).reset_index()
                _stats = _stats[(_stats['n_pontos'] >= 3) & (_stats['media'] > 0)]
                _stats['CV'] = (_stats['desvio'] / _stats['media']).fillna(0)
                _stats['Range R$'] = _stats['max_v'] - _stats['min_v']

                if _stats.empty:
                    st.info(
                        "ℹ️ Volatilidade requer sinistros presentes em pelo menos 3 snapshots. "
                        "Você precisa de mais dias de histórico acumulado."
                    )
                else:
                    _stats = _stats.sort_values('CV', ascending=False).head(20).copy()
                    # Enriquece com Ramo/Utilização do último snapshot
                    if 'Ramo' in _sin_u.columns:
                        _info = _sin_u[['nr_sinistro', 'Ramo', 'Utilização']].drop_duplicates('nr_sinistro')
                        _stats = _stats.merge(_info, on='nr_sinistro', how='left')

                    _stats['CV (%)'] = (_stats['CV'] * 100).apply(lambda v: f"{v:.1f}%")
                    _stats['Range R$'] = _stats['Range R$'].apply(lambda v: f"R$ {formatar_valor_br(v)}")
                    _stats['Média R$'] = _stats['media'].apply(lambda v: f"R$ {formatar_valor_br(v)}")
                    _cols_show = ['nr_sinistro']
                    if 'Ramo' in _stats.columns: _cols_show.append('Ramo')
                    if 'Utilização' in _stats.columns: _cols_show.append('Utilização')
                    _cols_show += ['n_pontos', 'CV (%)', 'Range R$', 'Média R$']
                    st.dataframe(
                        _stats[_cols_show].rename(columns={
                            'nr_sinistro': 'N° Sinistro',
                            'n_pontos': 'Snapshots'
                        }),
                        use_container_width=True, hide_index=True
                    )

    _render_aba_drill()

# ─── ABA 4 — RESERVA & ATUARIAL ──────────────────────────────────────────────
with _tab_reserva:
    @_st_fragment_temp
    def _render_aba_reserva():
        if _df_snap_sin_concat.empty:
            st.info("Sem dados de sinistros nos snapshots.")
            return

        _ultimo_dia = _snap_dias[-1]
        _sin_u = _df_snap_sin_concat[_df_snap_sin_concat['data_snapshot'] == _ultimo_dia].copy()
        _sin_u['nr_sinistro'] = _sin_u['nr_sinistro'].astype(str)

        # ── 1. Aging das reservas pendentes ──────────────────────────────────
        st.markdown(
            '<p class="section-label">📅 Aging das Reservas Pendentes</p>',
            unsafe_allow_html=True
        )
        st.caption(
            f"Distribuição da reserva ativa hoje ({_ultimo_dia.strftime('%d/%m/%Y')}) "
            f"por idade do sinistro (dt_aviso → hoje). Reservas em sinistros antigos sem "
            f"movimentação são red flags operacionais."
        )

        if 'dt_aviso' not in _sin_u.columns:
            st.info("Sem coluna dt_aviso — não é possível calcular o aging.")
        else:
            _sin_u['dt_aviso_dt'] = pd.to_datetime(_sin_u['dt_aviso'], dayfirst=True, errors='coerce')
            _sin_u['vl_pendente_total'] = (
                pd.to_numeric(_sin_u.get('vl_sinistro_pendente', 0), errors='coerce').fillna(0)
                + pd.to_numeric(_sin_u.get('vl_despesa_pendente', 0), errors='coerce').fillna(0)
            )
            # Apenas sinistros com pendente > 0
            _sin_pend = _sin_u[_sin_u['vl_pendente_total'] > 0.01].copy()
            _sin_pend['idade_dias'] = (_ultimo_dia - _sin_pend['dt_aviso_dt']).dt.days
            _sin_pend = _sin_pend.dropna(subset=['idade_dias'])

            if _sin_pend.empty:
                st.info("Nenhum sinistro com reserva pendente ativa.")
            else:
                _faixas_idade = [
                    ('0–3 meses',    0,   90,    '#059669'),
                    ('3–6 meses',    91,  180,   '#10B981'),
                    ('6–12 meses',   181, 365,   '#D97706'),
                    ('1–2 anos',     366, 730,   '#F59E0B'),
                    ('2–3 anos',     731, 1095,  '#DC2626'),
                    ('3–5 anos',     1096,1825,  '#991B1B'),
                    ('> 5 anos',     1826,99999, '#7F1D1D'),
                ]
                _rows = []
                for _lab, _lo, _hi, _cor in _faixas_idade:
                    _mask = (_sin_pend['idade_dias'] >= _lo) & (_sin_pend['idade_dias'] <= _hi)
                    _rows.append({
                        'Faixa': _lab,
                        'Qtd':   int(_mask.sum()),
                        'Pendente R$': float(_sin_pend.loc[_mask, 'vl_pendente_total'].sum()),
                        'cor':   _cor,
                    })
                _df_aging = pd.DataFrame(_rows)
                _df_aging['Pct R$'] = (_df_aging['Pendente R$'] / max(_df_aging['Pendente R$'].sum(), 1)) * 100

                _col_a, _col_b = st.columns(2)
                with _col_a:
                    _fig_aq = go.Figure(go.Bar(
                        x=_df_aging['Qtd'], y=_df_aging['Faixa'],
                        orientation='h', marker_color=_df_aging['cor'],
                        text=_df_aging['Qtd'].apply(lambda v: f'{int(v):,}'.replace(',', '.')),
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>Qtd: %{x}<extra></extra>',
                    ))
                    _fig_aq.update_layout(
                        title=dict(text='Quantidade de sinistros por idade', font=dict(size=13)),
                        height=320, margin=dict(l=10, r=30, t=40, b=10),
                        plot_bgcolor='white', yaxis=dict(autorange='reversed'),
                        xaxis_title='Quantidade',
                    )
                    st.plotly_chart(_fig_aq, use_container_width=True, config={'displayModeBar': False})
                with _col_b:
                    _fig_av = go.Figure(go.Bar(
                        x=_df_aging['Pendente R$'], y=_df_aging['Faixa'],
                        orientation='h', marker_color=_df_aging['cor'],
                        text=_df_aging.apply(lambda r: f'R$ {formatar_valor_br(r["Pendente R$"])} ({r["Pct R$"]:.1f}%)', axis=1),
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>',
                    ))
                    _fig_av.update_layout(
                        title=dict(text='Valor R$ de reserva pendente por idade', font=dict(size=13)),
                        height=320, margin=dict(l=10, r=30, t=40, b=10),
                        plot_bgcolor='white', yaxis=dict(autorange='reversed'),
                        xaxis_title='Valor (R$)',
                    )
                    st.plotly_chart(_fig_av, use_container_width=True, config={'displayModeBar': False})

                # Alerta: % da reserva em sinistros antigos (> 2 anos)
                _antigos_pct = _df_aging[_df_aging['Faixa'].isin(['2–3 anos', '3–5 anos', '> 5 anos'])]['Pct R$'].sum()
                _cor_a = '#DC2626' if _antigos_pct > 20 else ('#D97706' if _antigos_pct > 10 else '#059669')
                st.markdown(
                    f'<div style="background:#F8FAFC;border-left:3px solid {_cor_a};'
                    f'padding:10px 14px;border-radius:6px;font-size:13px;">'
                    f'🎯 <b>{_antigos_pct:.1f}%</b> da reserva pendente total está em sinistros com mais de 2 anos. '
                    f'{"Acima de 20% é red flag operacional — esses casos merecem investigação direta." if _antigos_pct > 20 else "Patamar saudável." if _antigos_pct < 10 else "Atenção: monitorar tendência."}'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")

        # ── 2. Ticket médio de pagamento ao longo do tempo ───────────────────
        st.markdown(
            '<p class="section-label">💰 Ticket Médio de Pagamento ao Longo do Tempo</p>',
            unsafe_allow_html=True
        )
        st.caption(
            "Desembolso médio por sinistro pago em cada snapshot. Tendência crescente "
            "indica aumento de severidade (sinistros mais caros, mesmo com frequência estável)."
        )

        _pontos_tk = []
        for _dia in _snap_dias:
            _sd = _df_snap_sin_concat[_df_snap_sin_concat['data_snapshot'] == _dia].copy()
            if _sd.empty:
                continue
            _sd['pago_total'] = (
                pd.to_numeric(_sd.get('vl_sinistro_pago', 0), errors='coerce').fillna(0)
                + pd.to_numeric(_sd.get('vl_despesa_pago', 0), errors='coerce').fillna(0)
            )
            _com_pago = _sd[_sd['pago_total'] > 0.01]
            if len(_com_pago) == 0:
                continue
            _pontos_tk.append({
                'data': _dia,
                'ticket_medio': _com_pago['pago_total'].sum() / len(_com_pago),
                'qtd_com_pago': len(_com_pago),
                'total_pago': _com_pago['pago_total'].sum(),
            })

        if len(_pontos_tk) < 2:
            st.info("Sem snapshots suficientes para calcular evolução do ticket médio.")
        else:
            _df_tk = pd.DataFrame(_pontos_tk)
            _fig_tk = go.Figure()
            _fig_tk.add_trace(go.Scatter(
                x=_df_tk['data'], y=_df_tk['ticket_medio'],
                mode='lines+markers+text',
                text=[f"R$ {formatar_valor_br(v)}" for v in _df_tk['ticket_medio']],
                textposition='top center',
                line=dict(color='#1a56db', width=2),
                marker=dict(size=10, color='#1a56db'),
                hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Ticket médio: R$ %{y:,.2f}<br>'
                              'Sinistros com pgto: %{customdata[0]:,}<br>'
                              'Total pago: R$ %{customdata[1]:,.2f}<extra></extra>',
                customdata=list(zip(_df_tk['qtd_com_pago'], _df_tk['total_pago']))
            ))
            _fig_tk.update_layout(
                height=380, margin=dict(l=20, r=20, t=20, b=20),
                plot_bgcolor='white',
                yaxis=dict(title='Ticket médio (R$)', gridcolor='#E2E8F0'),
                xaxis=dict(title='Data do snapshot', gridcolor='#E2E8F0'),
            )
            st.plotly_chart(_fig_tk, use_container_width=True, config={'displayModeBar': False})

            _delta_tk_pct = ((_df_tk.iloc[-1]['ticket_medio'] - _df_tk.iloc[0]['ticket_medio']) /
                             max(_df_tk.iloc[0]['ticket_medio'], 1)) * 100
            _cor_tk = '#DC2626' if _delta_tk_pct > 2 else ('#059669' if _delta_tk_pct < -2 else '#0F172A')
            st.markdown(
                f'<div style="background:#F8FAFC;border-radius:8px;padding:10px 14px;font-size:13px;">'
                f'<b>Variação acumulada do ticket médio:</b> '
                f'<span style="color:{_cor_tk};font-weight:600;">{_delta_tk_pct:+.2f}%</span> '
                f'entre {_df_tk.iloc[0]["data"].strftime("%d/%m/%Y")} e {_df_tk.iloc[-1]["data"].strftime("%d/%m/%Y")}.'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")

        # ── 3. Run-off realizado por safra de aviso ──────────────────────────
        st.markdown(
            '<p class="section-label">📐 Run-off Realizado por Safra (Ano de Aviso)</p>',
            unsafe_allow_html=True
        )
        st.caption(
            "Triângulo de run-off populado pelos snapshots. Para cada safra (Ano de Aviso), "
            "mostra como o Total Sinistro evoluiu em cada data de snapshot. Curva crescente "
            "= safra ainda desenvolvendo; estável = madura. Compare com a projeção do "
            "Chain Ladder em outras seções."
        )

        if 'dt_aviso' not in _df_snap_sin_concat.columns:
            st.info("Sem coluna dt_aviso — não é possível calcular o run-off.")
        else:
            _runoff = _df_snap_sin_concat.copy()
            _runoff['dt_aviso_dt'] = pd.to_datetime(_runoff['dt_aviso'], dayfirst=True, errors='coerce')
            _runoff['Safra'] = _runoff['dt_aviso_dt'].dt.year
            _runoff = _runoff.dropna(subset=['Safra'])
            _runoff['Total Sinistro'] = pd.to_numeric(_runoff['Total Sinistro'], errors='coerce').fillna(0)

            _evol_safra = _runoff.groupby(['data_snapshot', 'Safra'], as_index=False).agg(
                Total_Sin=('Total Sinistro', 'sum'),
                qtd=('nr_sinistro', 'nunique')
            )
            _evol_safra['Safra'] = _evol_safra['Safra'].astype(int)

            # Limita às 8 safras mais recentes pra não poluir o gráfico
            _safras_top = sorted(_evol_safra['Safra'].unique())[-8:]
            _evol_safra = _evol_safra[_evol_safra['Safra'].isin(_safras_top)]

            _fig_ro = go.Figure()
            for _safra in sorted(_evol_safra['Safra'].unique()):
                _d = _evol_safra[_evol_safra['Safra'] == _safra].sort_values('data_snapshot')
                _fig_ro.add_trace(go.Scatter(
                    x=_d['data_snapshot'], y=_d['Total_Sin'],
                    mode='lines+markers', name=str(_safra),
                    hovertemplate=f'<b>Safra {_safra}</b><br>%{{x|%d/%m/%Y}}<br>'
                                  f'R$ %{{y:,.2f}}<br>%{{customdata}} sinistros<extra></extra>',
                    customdata=_d['qtd']
                ))
            _fig_ro.update_layout(
                height=420, margin=dict(l=20, r=20, t=30, b=20),
                plot_bgcolor='white',
                yaxis=dict(title='Total Sinistro acumulado (R$)', gridcolor='#E2E8F0'),
                xaxis=dict(title='Data do snapshot', gridcolor='#E2E8F0'),
                legend=dict(orientation='h', yanchor='bottom', y=-0.35, xanchor='center', x=0.5,
                            title='Safra (Ano de Aviso)'),
            )
            st.plotly_chart(_fig_ro, use_container_width=True, config={'displayModeBar': False})

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")

        # ── 4. Taxa de adequação de reserva ──────────────────────────────────
        st.markdown(
            '<p class="section-label">⚖️ Taxa de Adequação de Reserva</p>',
            unsafe_allow_html=True
        )
        st.caption(
            "Para cada sinistro presente no primeiro e no último snapshot, compara a "
            "reserva inicial (1º snap) com o que foi efetivamente pago no período. "
            "Adequação = pago acumulado ÷ reserva inicial. Próximo de 100% = bem reservado; "
            "abaixo = super-reserva; muito acima = sub-reserva."
        )

        if len(_snap_dias) < 2:
            st.info("Precisa de pelo menos 2 snapshots para análise de adequação.")
        else:
            _primeiro_dia = _snap_dias[0]
            _sin_p = _df_snap_sin_concat[_df_snap_sin_concat['data_snapshot'] == _primeiro_dia].copy()
            _sin_p['nr_sinistro'] = _sin_p['nr_sinistro'].astype(str)
            _sin_p['pendente_inicial'] = (
                pd.to_numeric(_sin_p.get('vl_sinistro_pendente', 0), errors='coerce').fillna(0)
                + pd.to_numeric(_sin_p.get('vl_despesa_pendente', 0), errors='coerce').fillna(0)
            )
            _sin_p['pago_inicial'] = (
                pd.to_numeric(_sin_p.get('vl_sinistro_pago', 0), errors='coerce').fillna(0)
                + pd.to_numeric(_sin_p.get('vl_despesa_pago', 0), errors='coerce').fillna(0)
            )
            _sin_u_copy = _sin_u.copy()
            _sin_u_copy['pago_atual'] = (
                pd.to_numeric(_sin_u_copy.get('vl_sinistro_pago', 0), errors='coerce').fillna(0)
                + pd.to_numeric(_sin_u_copy.get('vl_despesa_pago', 0), errors='coerce').fillna(0)
            )
            _ad = _sin_p[['nr_sinistro', 'pendente_inicial', 'pago_inicial']].merge(
                _sin_u_copy[['nr_sinistro', 'pago_atual']], on='nr_sinistro', how='inner'
            )
            _ad['pago_no_periodo'] = _ad['pago_atual'] - _ad['pago_inicial']
            _ad_relevante = _ad[(_ad['pendente_inicial'] > 0) & (_ad['pago_no_periodo'] > 0)]

            if _ad_relevante.empty:
                st.info(
                    "Nenhum sinistro teve, simultaneamente, reserva inicial > 0 e pagamento no período. "
                    "Análise de adequação requer mais snapshots acumulados."
                )
            else:
                _ad_relevante = _ad_relevante.copy()
                _ad_relevante['taxa_adeq'] = (_ad_relevante['pago_no_periodo'] /
                                              _ad_relevante['pendente_inicial']) * 100

                _media_geral = (_ad_relevante['pago_no_periodo'].sum() /
                                _ad_relevante['pendente_inicial'].sum()) * 100
                _mediana = _ad_relevante['taxa_adeq'].median()
                _super_reserva = (_ad_relevante['taxa_adeq'] < 80).sum()
                _bem_reservado = ((_ad_relevante['taxa_adeq'] >= 80) & (_ad_relevante['taxa_adeq'] <= 120)).sum()
                _sub_reserva = (_ad_relevante['taxa_adeq'] > 120).sum()

                _ck1, _ck2, _ck3, _ck4 = st.columns(4)
                with _ck1:
                    _card_ritmo('🎯 Taxa média ponderada',
                                f"{_media_geral:.1f}%",
                                f'(pago no período / reserva inicial)')
                with _ck2:
                    _card_ritmo('📊 Taxa mediana',
                                f"{_mediana:.1f}%",
                                f'{len(_ad_relevante):,} sinistros analisados'.replace(',', '.'))
                with _ck3:
                    _card_ritmo('🟢 Super-reservados (<80%)',
                                f"{_super_reserva:,}".replace(',', '.'),
                                'reserva folgada para o que foi pago',
                                '#059669')
                with _ck4:
                    _card_ritmo('🔴 Sub-reservados (>120%)',
                                f"{_sub_reserva:,}".replace(',', '.'),
                                'pagamento acima da reserva — atenção',
                                '#DC2626')

    _render_aba_reserva()

# ─── ABA 5 — ALERTAS ─────────────────────────────────────────────────────────
with _tab_alertas:
    @_st_fragment_temp
    def _render_aba_alertas():
        if len(_snap_dias) < 2:
            st.info("⏳ Aguardando ao menos 2 dias de snapshot para detecção de alertas.")
            return

        _ultimo_dia = _snap_dias[-1]
        _penultimo_dia = _snap_dias[-2]
        _dias_entre = max((_ultimo_dia - _penultimo_dia).days, 1)

        st.markdown(
            f'<div style="background:#EFF6FF;border-left:3px solid #1a56db;padding:10px 14px;'
            f'border-radius:6px;font-size:13px;color:#1E3A8A;margin-bottom:14px;">'
            f'🔍 <b>Comparando:</b> snapshot de <b>{_penultimo_dia.strftime("%d/%m/%Y")}</b> '
            f'com o de <b>{_ultimo_dia.strftime("%d/%m/%Y")}</b> '
            f'(intervalo de {_dias_entre} dia{"s" if _dias_entre > 1 else ""}).'
            f'</div>',
            unsafe_allow_html=True
        )

        _sin_p = _df_snap_sin_concat[_df_snap_sin_concat['data_snapshot'] == _penultimo_dia].copy()
        _sin_u = _df_snap_sin_concat[_df_snap_sin_concat['data_snapshot'] == _ultimo_dia].copy()
        _sin_p['nr_sinistro'] = _sin_p['nr_sinistro'].astype(str)
        _sin_u['nr_sinistro'] = _sin_u['nr_sinistro'].astype(str)

        # Garante numérico
        for _df_, _c in [(_sin_p, 'Total Sinistro'), (_sin_u, 'Total Sinistro'),
                         (_sin_p, 'vl_sinistro_pendente'), (_sin_u, 'vl_sinistro_pendente'),
                         (_sin_p, 'vl_despesa_pendente'), (_sin_u, 'vl_despesa_pendente')]:
            if _c in _df_.columns:
                _df_[_c] = pd.to_numeric(_df_[_c], errors='coerce').fillna(0)

        _set_p = set(_sin_p['nr_sinistro'])
        _set_u = set(_sin_u['nr_sinistro'])

        # ── 1. Spike detector (variação anormal entre últimos 2 snapshots) ───
        st.markdown(
            '<p class="section-label">🚨 Spike Detector — Variações Anormais</p>',
            unsafe_allow_html=True
        )
        _col_t1, _col_t2 = st.columns(2)
        with _col_t1:
            _thr_pct = st.number_input(
                "Threshold de variação %:",
                min_value=5, max_value=100, value=30, step=5,
                key='spike_thr_pct',
                help='Sinistros com variação acima desse % entram no alerta.'
            )
        with _col_t2:
            _thr_rs = st.number_input(
                "Threshold de variação R$:",
                min_value=1000, max_value=1_000_000, value=50_000, step=5_000,
                key='spike_thr_rs',
                help='Sinistros com variação absoluta acima desse R$ entram no alerta.'
            )

        if 'Total Sinistro' in _sin_p.columns and 'Total Sinistro' in _sin_u.columns:
            _m_spike = _sin_p[['nr_sinistro', 'Total Sinistro']].merge(
                _sin_u[['nr_sinistro', 'Total Sinistro'] +
                       [c for c in ['Ramo', 'Utilização', 'dt_aviso'] if c in _sin_u.columns]],
                on='nr_sinistro', how='inner', suffixes=('_p', '_u')
            )
            _m_spike['delta'] = _m_spike['Total Sinistro_u'] - _m_spike['Total Sinistro_p']
            _m_spike['var_pct'] = (_m_spike['delta'] / _m_spike['Total Sinistro_p'].replace(0, float('nan')) * 100).fillna(0)

            # Aciona se var > thr_pct E |delta| > thr_rs (ambas as condições)
            _spike = _m_spike[
                (_m_spike['var_pct'].abs() >= _thr_pct) &
                (_m_spike['delta'].abs() >= _thr_rs)
            ].copy()

            if _spike.empty:
                st.success(
                    f"✅ Nenhum sinistro com variação ≥ {_thr_pct}% **e** "
                    f"≥ R$ {formatar_valor_br(_thr_rs)} entre os últimos 2 snapshots."
                )
            else:
                _spike = _spike.sort_values('delta', key=lambda c: c.abs(), ascending=False).head(20)
                st.markdown(
                    f'<div style="background:#FEF2F2;border-left:3px solid #DC2626;'
                    f'padding:10px 14px;border-radius:6px;font-size:13px;">'
                    f'⚠️ <b>{len(_spike)} sinistro(s)</b> com variação anormal detectada.'
                    f'</div>',
                    unsafe_allow_html=True
                )
                _spike['Δ R$'] = _spike['delta'].apply(
                    lambda v: f"{'+' if v > 0 else ''}R$ {formatar_valor_br(v)}"
                )
                _spike['Var %'] = _spike['var_pct'].apply(lambda v: f"{v:+.1f}%")
                _spike['Total Atual'] = _spike['Total Sinistro_u'].apply(
                    lambda v: f"R$ {formatar_valor_br(v)}"
                )
                _cols_spike = ['nr_sinistro']
                for _c in ['Ramo', 'Utilização', 'dt_aviso']:
                    if _c in _spike.columns:
                        _cols_spike.append(_c)
                _cols_spike += ['Δ R$', 'Var %', 'Total Atual']
                st.dataframe(
                    _spike[_cols_spike].rename(columns={'nr_sinistro': 'N° Sinistro'}),
                    use_container_width=True, hide_index=True
                )

        st.markdown("---")

        # ── 2. Mudanças de status ────────────────────────────────────────────
        st.markdown(
            '<p class="section-label">🔄 Mudanças de Status</p>',
            unsafe_allow_html=True
        )
        st.caption(
            "Sinistros que mudaram status_processo ou status_movimento entre o "
            "snapshot anterior e o atual. Útil pra acompanhar liquidações em curso "
            "e mudanças operacionais."
        )

        if 'status_movimento' in _sin_p.columns and 'status_movimento' in _sin_u.columns:
            _cols_st = ['nr_sinistro', 'status_movimento']
            if 'status_processo' in _sin_p.columns: _cols_st.append('status_processo')

            _m_st = _sin_p[_cols_st].merge(
                _sin_u[_cols_st + [c for c in ['Ramo', 'Total Sinistro'] if c in _sin_u.columns]],
                on='nr_sinistro', how='inner', suffixes=('_antes', '_depois')
            )
            _mask_mudou = _m_st['status_movimento_antes'].astype(str) != _m_st['status_movimento_depois'].astype(str)
            if 'status_processo_antes' in _m_st.columns:
                _mask_mudou |= (_m_st['status_processo_antes'].astype(str) != _m_st['status_processo_depois'].astype(str))
            _st_changes = _m_st[_mask_mudou].copy()

            if _st_changes.empty:
                st.info("Nenhuma mudança de status detectada entre os últimos 2 snapshots.")
            else:
                _st_changes['Status Movimento'] = (
                    _st_changes['status_movimento_antes'].astype(str) + ' → ' +
                    _st_changes['status_movimento_depois'].astype(str)
                )
                _cols_show = ['nr_sinistro', 'Status Movimento']
                if 'status_processo_antes' in _st_changes.columns:
                    _st_changes['Status Processo'] = (
                        _st_changes['status_processo_antes'].astype(str) + ' → ' +
                        _st_changes['status_processo_depois'].astype(str)
                    )
                    _cols_show.append('Status Processo')
                if 'Ramo' in _st_changes.columns:
                    _cols_show.append('Ramo')
                if 'Total Sinistro' in _st_changes.columns:
                    _st_changes['Total R$'] = _st_changes['Total Sinistro'].apply(
                        lambda v: f"R$ {formatar_valor_br(v)}"
                    )
                    _cols_show.append('Total R$')
                st.dataframe(
                    _st_changes[_cols_show].head(30).rename(columns={'nr_sinistro': 'N° Sinistro'}),
                    use_container_width=True, hide_index=True
                )
                if len(_st_changes) > 30:
                    st.caption(f"Mostrando 30 de {len(_st_changes)} mudanças no total.")
        else:
            st.info("Sem coluna status_movimento nos snapshots.")

        st.markdown("---")

        # ── 3. Sinistros novos ───────────────────────────────────────────────
        _novos = _set_u - _set_p
        _sumidos = _set_p - _set_u

        _col_n, _col_s = st.columns(2)
        with _col_n:
            st.markdown(
                f'<p class="section-label">🆕 Sinistros Novos ({len(_novos)})</p>',
                unsafe_allow_html=True
            )
            if not _novos:
                st.info("Nenhum sinistro novo desde o último snapshot.")
            else:
                _df_novos = _sin_u[_sin_u['nr_sinistro'].isin(_novos)].copy()
                _cols_n = ['nr_sinistro']
                for _c in ['Ramo', 'dt_aviso', 'Total Sinistro']:
                    if _c in _df_novos.columns:
                        _cols_n.append(_c)
                if 'Total Sinistro' in _df_novos.columns:
                    _df_novos['Total R$'] = _df_novos['Total Sinistro'].apply(
                        lambda v: f"R$ {formatar_valor_br(v)}"
                    )
                    _cols_n = [c if c != 'Total Sinistro' else 'Total R$' for c in _cols_n]
                st.dataframe(
                    _df_novos[_cols_n].head(15).rename(columns={'nr_sinistro': 'N° Sinistro'}),
                    use_container_width=True, hide_index=True
                )
                if len(_df_novos) > 15:
                    st.caption(f"Mostrando 15 de {len(_df_novos)} no total.")

        with _col_s:
            st.markdown(
                f'<p class="section-label">👻 Sinistros Sumidos ({len(_sumidos)})</p>',
                unsafe_allow_html=True
            )
            if not _sumidos:
                st.info("Nenhum sinistro desapareceu da base.")
            else:
                _df_sumidos = _sin_p[_sin_p['nr_sinistro'].isin(_sumidos)].copy()
                _cols_s = ['nr_sinistro']
                for _c in ['Ramo', 'dt_aviso', 'Total Sinistro']:
                    if _c in _df_sumidos.columns:
                        _cols_s.append(_c)
                if 'Total Sinistro' in _df_sumidos.columns:
                    _df_sumidos['Total R$'] = _df_sumidos['Total Sinistro'].apply(
                        lambda v: f"R$ {formatar_valor_br(v)}"
                    )
                    _cols_s = [c if c != 'Total Sinistro' else 'Total R$' for c in _cols_s]
                st.dataframe(
                    _df_sumidos[_cols_s].head(15).rename(columns={'nr_sinistro': 'N° Sinistro'}),
                    use_container_width=True, hide_index=True
                )
                if len(_df_sumidos) > 15:
                    st.caption(f"Mostrando 15 de {len(_df_sumidos)} no total.")

        st.markdown("---")

        # ── 4. Reservas constituídas recentemente (aumento de pendente) ──────
        st.markdown(
            '<p class="section-label">📈 Reservas Constituídas/Aumentadas Recentemente</p>',
            unsafe_allow_html=True
        )
        st.caption(
            "Sinistros que tiveram aumento de vl_pendente (sinistro + despesa) entre os "
            "últimos 2 snapshots. Indica avaliação técnica de que ainda há custo a vir — "
            "sinal antecipado de pressão futura na carteira."
        )

        _cols_pend = ['nr_sinistro', 'vl_sinistro_pendente', 'vl_despesa_pendente']
        _cols_pend = [c for c in _cols_pend if c in _sin_p.columns and c in _sin_u.columns]
        if len(_cols_pend) >= 2:
            _m_p = _sin_p[_cols_pend].merge(
                _sin_u[_cols_pend + [c for c in ['Ramo', 'dt_aviso'] if c in _sin_u.columns]],
                on='nr_sinistro', how='inner', suffixes=('_p', '_u')
            )
            _m_p['pendente_total_p'] = (
                _m_p.get('vl_sinistro_pendente_p', 0) + _m_p.get('vl_despesa_pendente_p', 0)
            )
            _m_p['pendente_total_u'] = (
                _m_p.get('vl_sinistro_pendente_u', 0) + _m_p.get('vl_despesa_pendente_u', 0)
            )
            _m_p['delta_pend'] = _m_p['pendente_total_u'] - _m_p['pendente_total_p']
            _aumentou = _m_p[_m_p['delta_pend'] > 0.01].sort_values('delta_pend', ascending=False).head(15).copy()
            if _aumentou.empty:
                st.success("✅ Nenhuma constituição/aumento de reserva detectado no período.")
            else:
                _aumentou['Δ Reserva R$'] = _aumentou['delta_pend'].apply(
                    lambda v: f"+R$ {formatar_valor_br(v)}"
                )
                _aumentou['Reserva Atual'] = _aumentou['pendente_total_u'].apply(
                    lambda v: f"R$ {formatar_valor_br(v)}"
                )
                _cols_show = ['nr_sinistro']
                for _c in ['Ramo', 'dt_aviso']:
                    if _c in _aumentou.columns:
                        _cols_show.append(_c)
                _cols_show += ['Δ Reserva R$', 'Reserva Atual']
                st.dataframe(
                    _aumentou[_cols_show].rename(columns={'nr_sinistro': 'N° Sinistro'}),
                    use_container_width=True, hide_index=True
                )
                _total_constituido = _m_p[_m_p['delta_pend'] > 0]['delta_pend'].sum()
                st.markdown(
                    f'<div style="background:#FEF3C7;border-left:3px solid #D97706;'
                    f'padding:10px 14px;border-radius:6px;font-size:13px;">'
                    f'📊 <b>Total constituído/aumentado no período:</b> R$ {formatar_valor_br(_total_constituido)} '
                    f'({(_m_p["delta_pend"] > 0.01).sum()} sinistros).'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("Sem colunas de pendente nos snapshots para este alerta.")

    _render_aba_alertas()

st.write("---")
st.caption("Desenvolvido por Alex Sousa.")

# Instruções para executar o Streamlit:
# python -m streamlit run nome_do_arquivo.py
# ---
# **Para executar este aplicativo Streamlit:**
# 1. Abra o terminal ou prompt de comando.
# 2. Navegue até o diretório onde você salvou o arquivo.
# 5. Execute o comando: `python -m streamlit nome_do_arquivo.py`
# Se o Streamlit não estiver instalado, execute: `pip install streamlit pandas openpyxl`
