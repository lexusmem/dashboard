import streamlit as st
import pandas as pd
import io
import base64
import logging
import plotly.graph_objects as go
import plotly.express as px
import streamlit_antd_components as sac
from datetime import datetime

st.set_page_config(layout='wide', page_title='Painel Allseg', page_icon='📊')

ALLSEG_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
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
html, body, [class*="css"] { font-family: var(--font-main) !important; color: var(--text-primary) !important; }
.stApp { background-color: var(--bg-page) !important; }
.main .block-container { max-width: 96% !important; padding: 1.5rem 2rem 10rem !important; }
[data-testid="stMetric"] { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; box-shadow: var(--shadow-md) !important; }
[data-testid="stDataFrame"], [data-testid="stPlotlyChart"] > div { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; box-shadow: var(--shadow-md) !important; }
[data-testid="stHeader"], [data-testid="stToolbar"], footer { display: none !important; }
</style>
"""
st.markdown(ALLSEG_CSS, unsafe_allow_html=True)

st.markdown('<a href="#topo-pagina" class="btn-topo" title="Voltar ao topo">↑</a>', unsafe_allow_html=True)

# ==================== UPLOAD E CARREGAMENTO (seu código original) ====================
dados_ja_carregados = ('dados_calculados' in st.session_state and 'df_sinistros' in st.session_state and 'df_cobertura' in st.session_state and
                       not st.session_state['dados_calculados'].empty and not st.session_state['df_sinistros'].empty)

if not dados_ja_carregados:
    st.sidebar.header("📂 Carregar Arquivos")
    st.sidebar.caption("Faça o upload dos três arquivos TXT")
    upload_apolice = st.sidebar.file_uploader("apolice_endosso.txt", type=["txt", "csv"])
    upload_cobertura = st.sidebar.file_uploader("cobertura_agrupada.txt", type=["txt", "csv"])
    upload_sinistro = st.sidebar.file_uploader("sinistro.txt", type=["txt", "csv"])
    if not upload_apolice or not upload_sinistro or not upload_cobertura:
        st.info("👈 Faça o upload dos três arquivos TXT na barra lateral.")
        st.stop()
else:
    upload_apolice = upload_sinistro = upload_cobertura = None

# Suas funções originais (carregar_e_processar_dados, carregar_cobertura, etc.)
@st.cache_data
def carregar_e_processar_dados_sinistro(arquivo):
    # ... Cole aqui o conteúdo completo da sua função original ...
    try:
        if isinstance(arquivo, io.BytesIO):
            arquivo.seek(0)
            fonte = arquivo
        elif hasattr(arquivo, 'read'):
            fonte = io.BytesIO(arquivo.read())
        else:
            fonte = arquivo
        aba_sinistro = pd.read_csv(fonte, sep=';', encoding='latin-1', decimal=',', low_memory=False)
        colunas_valor = ['vl_sinistro_total', 'vl_despesa_total', 'vl_honorario_total', 'vl_salvado_total']
        for col in colunas_valor:
            aba_sinistro[col] = pd.to_numeric(aba_sinistro[col], errors='coerce').fillna(0)
        aba_sinistro['Total Sinistro'] = (aba_sinistro['vl_sinistro_total'] + aba_sinistro['vl_despesa_total'] +
                                          aba_sinistro['vl_honorario_total'] - aba_sinistro['vl_salvado_total'])
        aba_sinistro.rename(columns={'cd_apolice': 'N° Apólice'}, inplace=True)
        return aba_sinistro.fillna(0)
    except Exception as e:
        st.error(f"Erro ao carregar sinistros: {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_e_processar_dados(arquivo_apolice, arquivo_sinistro):
    # ... Cole aqui o conteúdo completo da sua função original ...
    # (mantive o resto igual)
    # ... (seu código completo desta função)
    pass  # Substitua pelo seu código completo original

@st.cache_data
def carregar_cobertura(arquivo):
    try:
        if isinstance(arquivo, io.BytesIO):
            arquivo.seek(0)
            fonte = arquivo
        elif hasattr(arquivo, 'read'):
            fonte = io.BytesIO(arquivo.read())
        else:
            fonte = arquivo
        df = pd.read_csv(fonte, sep=';', encoding='latin-1', decimal=',', low_memory=False)
        df.rename(columns={'cd_apolice': 'N° Apólice', 'nm_comercial': 'Cobertura Apólice', 'vl_franquia': 'Franquia Apólice'}, inplace=True)
        df['Franquia Apólice'] = pd.to_numeric(df['Franquia Apólice'], errors='coerce').fillna(0)
        df = df.sort_values('nr_endosso', ascending=False)
        df = df.drop_duplicates(subset=['N° Apólice', 'Cobertura Apólice'], keep='first')
        return df[['N° Apólice', 'Cobertura Apólice', 'Franquia Apólice']]
    except Exception as e:
        st.error(f"Erro ao carregar coberturas: {e}")
        return pd.DataFrame()

def formatar_valor_br(valor):
    if pd.isna(valor):
        return ""
    valor_us = f"{valor:,.2f}"
    return valor_us.replace(",", "X").replace(".", ",").replace("X", ".")

# Carregamento dos dados (seu código original)
if dados_ja_carregados:
    dados_calculados = st.session_state['dados_calculados']
    df_sinistros = st.session_state['df_sinistros']
    df_cobertura = st.session_state.get('df_cobertura', pd.DataFrame())
else:
    # ... seu código de BytesIO e carregamento ...
    dados_calculados = carregar_e_processar_dados(...)  # mantenha seu código
    # ... (mantenha todo o bloco de carregamento e session_state)
    st.rerun()

# Preparação dados_exibicao (seu código original)
dados_exibicao = dados_calculados.copy()
# ... (seu código de formatação % Sin etc. permanece igual)

# Filtro Apólice (seu código)
st.sidebar.header('Filtro Apólice')
apolices_filtro_apolice = sorted(dados_exibicao['N° Apólice'].unique())
apolices_selecionadas_filtro_apolice = st.sidebar.selectbox('Apólice', options=apolices_filtro_apolice, index=0)

# ... (todo seu código de filtro por apólice, KPIs, tabelas etc. até chegar no df_sinistro_apolice) ...

# ==================== CORREÇÃO FRANQUIA - APÓLICE ====================
if not df_cobertura.empty:
    df_franquia_ap = df_cobertura[df_cobertura['N° Apólice'] == apolices_selecionadas_filtro_apolice][['Cobertura Apólice', 'Franquia Apólice']].rename(columns={'Cobertura Apólice': 'Cobertura'})
    df_sinistro_apolice = pd.merge(df_sinistro_apolice, df_franquia_ap, on='Cobertura', how='left')
    df_sinistro_apolice['Franquia Apólice'] = df_sinistro_apolice['Franquia Apólice'].fillna(0)

# ==================== CORREÇÃO FRANQUIA - SEGURADO ====================
if not df_cobertura.empty and not df_sinistro_segurado.empty:
    df_franquia_seg = df_cobertura[
        df_cobertura['N° Apólice'].isin(df_sinistro_segurado['N° Apólice'].unique())
    ][['N° Apólice', 'Cobertura Apólice', 'Franquia Apólice']].rename(columns={'Cobertura Apólice': 'Cobertura'})
    
    df_sinistro_segurado = pd.merge(
        df_sinistro_segurado,
        df_franquia_seg,
        on=['N° Apólice', 'Cobertura'],
        how='left'
    )
    df_sinistro_segurado['Franquia Apólice'] = df_sinistro_segurado['Franquia Apólice'].fillna(0)
else:
    df_sinistro_segurado['Franquia Apólice'] = 0.0

# Formatação final das colunas (seu código original)
# ... aplique .map(formatar_valor_br) nas colunas de valor ...

# Restante do seu código (gráficos, tabelas do segurado, etc.) permanece igual
st.write("---")
st.caption("Desenvolvido por Alex Sousa.")
