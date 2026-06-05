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
# ── Seletor de visão: Underwriting Year × Accident Year ──────────────────────
_visao_ano = st.radio(
    "**Visão de alocação de sinistros:**",
    options=["Underwriting Year", "Accident Year"],
    horizontal=True,
    key="radio_visao_ano",
    help=(
        "**Underwriting Year:** prêmio, sinistro e quantidade de sinistros alocados "
        "ao ano de vigência da apólice. Ideal para análise de subscrição — mostra o "
        "resultado técnico de cada safra de apólices.\n\n"
        "**Accident Year:** sinistros alocados ao ano em que o evento ocorreu, "
        "independente da vigência da apólice. Ideal para análise de exposição a "
        "risco e eventos climáticos/judiciais por período."
    )
)

# Descrição visual da visão selecionada
if _visao_ano == "Underwriting Year":
    st.caption(
        "📋 **Underwriting Year (UWY):** prêmio e sinistros agrupados pelo **ano de vigência da apólice**. "
        "Permite avaliar o resultado técnico de cada coorte de contratos subscritos."
    )
else:
    st.caption(
        "📋 **Accident Year (AY):** sinistros agrupados pelo **ano em que o evento ocorreu**. "
        "Prêmio mantido por ano de vigência. Permite analisar a concentração de eventos por período."
    )

# ── Base de sinistros filtrada pelas apólices do período ─────────────────────
lista_apos_ano = df_para_soma['N° Apólice'].unique()
df_sin_filtrado_ano = df_sinistros[df_sinistros['N° Apólice'].isin(lista_apos_ano)].copy()

# ── Cálculo conforme visão selecionada ───────────────────────────────────────
if _visao_ano == "Underwriting Year":
    # Underwriting Year: qtd sinistros pelo Ano Vigência da apólice
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
    # Accident Year: sinistros alocados ao ano de ocorrência
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
                hovertemplate=f"Safra {int(av)}<br>Lag: %{{x}} anos<br>Sin. Acum: %{{y:.1%}}<extra></extra>"
            ))
        fig_saf.update_layout(
            xaxis=dict(title='Anos após vigência (Lag)', tickmode='linear', dtick=1),
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
            'Último Lag':          ultimo_lag,
            'Status':              'Completa' if ja_completa else f'Em dev. (lag {ultimo_lag}/{max_lag})'
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
        fat_data = [{'Lag → Lag+1': f"Ano+{lag} → Ano+{lag+1}", 'Fator Médio': f"{v:.4f}×", 'Significado': f"A sinistralidade cresce em média {(v-1)*100:.1f}% entre esses dois períodos"} for lag, v in sorted(fatores.items())]
        if fat_data:
            st.dataframe(pd.DataFrame(fat_data), hide_index=True, use_container_width=True)
            st.caption("Fatores ponderados pelo prêmio de cada safra. Quanto mais próximo de 1.000×, mais estável o desenvolvimento naquele lag.")


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

<b>Como foi desenvolvido:</b> Para cada sinistro, identifica o Ano de Vigência da apólice correspondente e o Ano de Aviso do sinistro. Calcula o lag (diferença em anos). Acumula o Total Sinistro por safra à medida que o lag aumenta e divide pelo prêmio total daquela safra. O gráfico de curvas mostra uma linha por safra — curvas que ainda sobem indicam safras incompletas.
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
            df_12m = df_sin_tend[df_sin_tend['dt_aviso'] >= df_sin_tend['dt_aviso'].max() - pd.DateOffset(months=12)]
            ticket_medio = df_12m['Total Sinistro'].sum() / max(df_12m['nr_sinistro'].nunique(), 1)

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
                    <tr><td>💰 Ticket médio sinistro (12m)</td><td style="text-align:right;font-weight:bold;">R$ {ticket_medio:,.2f}</td></tr>
                </table>
                <hr style="border:1px solid #E2E8F0;margin:10px 0;">
                <div style="font-size:11px;color:#64748B;">{desc}</div>
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

<b>Como foi desenvolvido:</b> A sinistralidade anual usa a mesma base do Desempenho Consolidado por Ano (Ano de Vigência da Apólice), garantindo consistência. As médias móveis mensais são calculadas sobre a data de aviso dos sinistros, que é o dado mais atual disponível. A regressão linear é calculada com numpy.polyfit sobre os anos disponíveis filtrados.
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAINEL DE DIAGNÓSTICO DE VARIAÇÃO DA SINISTRALIDADE
# ══════════════════════════════════════════════════════════════════════════════
st.write("---")
st.subheader("🔎 Diagnóstico de Variação da Sinistralidade")
st.caption(
    "Identifica quais Ramos e Utilizações contribuíram para a variação recente da sinistralidade. "
    "Compara três janelas de tempo (60 / 90 / 180 dias) com o período anterior equivalente, "
    "usando a data de aviso dos sinistros."
)

if not df_sinistro_periodo_atualizado.empty and not df_geral_periodo.empty:

    _col_d1, _ = st.columns([1, 3])
    with _col_d1:
        _agrupar = st.selectbox(
            "Agrupar por",
            options=["Ramo", "Utilização"],
            key="diag_agrupar"
        )

    _cols_grp = [_agrupar]

    # Prepara base com datas
    _df_sin = df_sinistro_periodo_atualizado.copy()
    if 'dt_aviso_dt' not in _df_sin.columns:
        _df_sin['dt_aviso_dt'] = pd.to_datetime(_df_sin['dt_aviso'], dayfirst=True, errors='coerce')

    _data_max = _df_sin['dt_aviso_dt'].max()

    # Mapa apólice → Ramo / Utilização
    _mapa_apo = df_geral_periodo[['N° Apólice', 'Ramo', 'Utilização']].drop_duplicates('N° Apólice')
    _df_sin = pd.merge(_df_sin, _mapa_apo, on='N° Apólice', how='left')

    # Prêmio por grupo
    _premio_grp = df_para_soma.groupby(_cols_grp, as_index=False).agg(
        Premio_Total=('Soma Prêmio Pago por Apolice', 'sum')
    )
    _premio_total_geral = df_para_soma['Soma Prêmio Pago por Apolice'].sum()

    def _calcular_janela(janela):
        """Calcula sinistralidade recente vs anterior para uma janela em dias."""
        _ini_rec = _data_max - pd.Timedelta(days=janela)
        _ini_ant = _ini_rec - pd.Timedelta(days=janela)
        _rec = _df_sin[_df_sin['dt_aviso_dt'] > _ini_rec]
        _ant = _df_sin[(_df_sin['dt_aviso_dt'] > _ini_ant) & (_df_sin['dt_aviso_dt'] <= _ini_rec)]

        def _agg(df):
            if df.empty:
                return pd.DataFrame(columns=_cols_grp + ['Total_Sinistro','Qtd_Sinistros'])
            return df.groupby(_cols_grp, as_index=False).agg(
                Total_Sinistro=('Total Sinistro', 'sum'),
                Qtd_Sinistros=('nr_sinistro', 'nunique')
            )

        _s_rec = _agg(_rec)
        _s_ant = _agg(_ant)

        _premio_j = _premio_grp.copy()
        _premio_j['Premio_J'] = _premio_j['Premio_Total'] * (janela / 365)

        _r = pd.merge(_premio_j, _s_rec, on=_cols_grp, how='left').fillna(0)
        _a = pd.merge(_premio_j, _s_ant, on=_cols_grp, how='left').fillna(0)

        _r[f'Sin_Rec_{janela}'] = (_r['Total_Sinistro'] / _r['Premio_J'].replace(0, float('nan'))).fillna(0)
        _a[f'Sin_Ant_{janela}'] = (_a['Total_Sinistro'] / _a['Premio_J'].replace(0, float('nan'))).fillna(0)

        _c = pd.merge(_r[_cols_grp + [f'Sin_Rec_{janela}']], _a[_cols_grp + [f'Sin_Ant_{janela}']], on=_cols_grp, how='outer').fillna(0)
        _c[f'Var_{janela}'] = (_c[f'Sin_Rec_{janela}'] - _c[f'Sin_Ant_{janela}']) * 100

        # KPIs gerais da janela
        _sin_rec_g = _rec['Total Sinistro'].sum() / (_premio_total_geral * janela / 365) if _premio_total_geral > 0 else 0
        _sin_ant_g = _ant['Total Sinistro'].sum() / (_premio_total_geral * janela / 365) if _premio_total_geral > 0 else 0

        return _c, _sin_rec_g, _sin_ant_g, _ini_rec, _ini_ant

    _janelas = [60, 90, 180]
    _resultados = {j: _calcular_janela(j) for j in _janelas}

    # ── KPIs — uma coluna por janela ─────────────────────────────────────────
    st.markdown("**Sinistralidade geral por janela de comparação**")
    _kcols = st.columns(3)
    for i, j in enumerate(_janelas):
        _, _sin_rec_g, _sin_ant_g, _ini_rec, _ini_ant = _resultados[j]
        _var = (_sin_rec_g - _sin_ant_g) * 100
        with _kcols[i]:
            st.metric(
                f"Últimos {j} dias",
                f"{_sin_rec_g:.1%}",
                delta=f"{_var:+.1f}pp vs {j}d anteriores",
                delta_color="inverse"
            )
            st.caption(
                "Recente: " + _ini_rec.strftime('%d/%m/%y') + " a " + _data_max.strftime('%d/%m/%y') +
                "  |  Anterior: " + _ini_ant.strftime('%d/%m/%y') + " a " + _ini_rec.strftime('%d/%m/%y')
            )

    st.write("")

    # ── Gráficos — um por janela, lado a lado ────────────────────────────────
    st.markdown(f"**Contribuição de cada {_agrupar} por janela**")
    _gcols = st.columns(3)

    for i, j in enumerate(_janelas):
        _comp, _, _, _ini_rec, _ = _resultados[j]
        _comp_plot = _comp[_comp[f'Sin_Rec_{j}'] + _comp[f'Sin_Ant_{j}'] > 0].copy()

        # Garante que o rótulo é string do valor real (ramo 23, não 40)
        _comp_plot['_label'] = _comp_plot[_cols_grp[0]].astype(str)
        _comp_plot = _comp_plot.sort_values(f'Var_{j}')

        _cores = ['#DC2626' if v > 0 else '#16A34A' for v in _comp_plot[f'Var_{j}']]

        _fig = go.Figure(go.Bar(
            x=_comp_plot[f'Var_{j}'],
            y=_comp_plot['_label'],
            orientation='h',
            marker_color=_cores,
            text=_comp_plot[f'Var_{j}'].map(lambda x: f"{x:+.1f}pp"),
            textposition='outside',
        ))
        _fig.add_vline(x=0, line_width=1.5, line_color='#374151')
        _max_abs = max(abs(_comp_plot[f'Var_{j}']).max(), 1) * 1.4
        _fig.update_layout(
            title=dict(text=f"Últimos {j} dias", font=dict(size=13)),
            xaxis=dict(
                title='Variação (pp)',
                ticksuffix='pp',
                range=[-_max_abs, _max_abs]  # eixo simétrico e fixo por janela
            ),
            yaxis=dict(title='', tickfont=dict(size=10)),
            margin=dict(t=40, b=20, l=0, r=50),
            height=max(220, len(_comp_plot) * 40 + 80),
            plot_bgcolor='white'
        )
        with _gcols[i]:
            st.plotly_chart(_fig, use_container_width=True, config={'displayModeBar': False})

    # ── Tabela comparativa consolidada ───────────────────────────────────────
    with st.expander("📋 Ver tabela detalhada de comparação"):
        _base_tbl = _resultados[180][0][_cols_grp].copy()
        for j in _janelas:
            _c = _resultados[j][0]
            _base_tbl = pd.merge(_base_tbl, _c[_cols_grp + [f'Sin_Rec_{j}', f'Sin_Ant_{j}', f'Var_{j}']], on=_cols_grp, how='outer').fillna(0)

        # Formata
        for j in _janelas:
            _base_tbl[f'Sin_Rec_{j}'] = _base_tbl[f'Sin_Rec_{j}'].map(lambda x: f"{x:.1%}")
            _base_tbl[f'Sin_Ant_{j}'] = _base_tbl[f'Sin_Ant_{j}'].map(lambda x: f"{x:.1%}")
            _base_tbl[f'Var_{j}']     = _base_tbl[f'Var_{j}'].map(lambda x: f"{x:+.1f}pp")

        _base_tbl.rename(columns={
            _cols_grp[0]: _agrupar,
            'Sin_Rec_60': 'Sin. Rec. 60d', 'Sin_Ant_60': 'Sin. Ant. 60d', 'Var_60': 'Var. 60d',
            'Sin_Rec_90': 'Sin. Rec. 90d', 'Sin_Ant_90': 'Sin. Ant. 90d', 'Var_90': 'Var. 90d',
            'Sin_Rec_180': 'Sin. Rec. 180d','Sin_Ant_180': 'Sin. Ant. 180d','Var_180': 'Var. 180d',
        }, inplace=True)
        st.dataframe(_base_tbl, hide_index=True, use_container_width=True)

else:
    st.info("Nenhum dado disponível para análise de variação.")


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
