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

# ... (todo o CSS ALLSEG_CSS permanece igual) ...
st.markdown(ALLSEG_CSS, unsafe_allow_html=True)

st.markdown(
    '<a href="#topo-pagina" class="btn-topo" title="Voltar ao topo">&#8679;</a>',
    unsafe_allow_html=True
)

# --- Upload e carregamento (permanece igual) ---
# ... (todo o código de upload, session_state, funções carregar_e_processar_dados, etc. permanece igual até a parte de exibição) ...

# ====================== CORREÇÃO PRINCIPAL ======================

# Após carregar df_sinistro_segurado

# Adiciona Franquia por Cobertura no df_sinistro_segurado
if not df_cobertura.empty and not df_sinistro_segurado.empty:
    df_franquia_cob_seg = df_cobertura[
        df_cobertura['N° Apólice'].isin(df_sinistro_segurado['N° Apólice'].unique())
    ][['N° Apólice', 'Cobertura Apólice', 'Franquia Apólice']].rename(
        columns={'Cobertura Apólice': 'Cobertura'}
    ).copy()
    
    # Merge correto: por Apólice + Cobertura
    df_sinistro_segurado = pd.merge(
        df_sinistro_segurado,
        df_franquia_cob_seg,
        on=['N° Apólice', 'Cobertura'],
        how='left'
    )
    df_sinistro_segurado['Franquia Apólice'] = df_sinistro_segurado['Franquia Apólice'].fillna(0)
else:
    df_sinistro_segurado['Franquia Apólice'] = 0.0

# Formatação das colunas (permanece igual)
df_sinistro_segurado['vl_sinistro_pago'] = (df_sinistro_segurado['vl_sinistro_pago'].map(formatar_valor_br))
# ... (resto das formatações de valores permanece igual) ...
df_sinistro_segurado['Total Sinistro'] = (df_sinistro_segurado['Total Sinistro'].map(formatar_valor_br))
df_sinistro_segurado['Franquia Apólice'] = df_sinistro_segurado['Franquia Apólice'].map(formatar_valor_br)

# ====================== FIM DA CORREÇÃO ======================

# Restante do código do Segurado (tabelas, gráficos, etc.) permanece igual...

# =============================================================================

# No final do arquivo, na parte de Dados de Sinistro do Segurado:
with df_sinistro_segurado_2:
    st.markdown('<p class="section-label">Dados de Sinistro do Segurado</p>', unsafe_allow_html=True)
    df_sinistro_segurado = pd.merge(
        df_sinistro_segurado,
        dados_exibicao[['N° Apólice', 'Representante', 'Corretor']].drop_duplicates('N° Apólice'),
        on='N° Apólice', how='left'
    )
    _cols_seg = ['nr_sinistro', 'nr_ramo', 'N° Apólice', 'nr_endosso', 'nm_cliente', 'Cobertura', 
                 'dt_aviso', 'dt_ocorrencia', 'vl_sinistro_pago', 'vl_sinistro_pendente', 
                 'vl_sinistro_total', 'vl_despesa_pago', 'vl_despesa_pendente', 'vl_despesa_total',
                 'vl_honorario_pago', 'vl_honorario_pendente', 'vl_honorario_total', 
                 'vl_salvado_pago', 'vl_salvado_pendente', 'vl_salvado_total', 
                 'status_processo', 'status_movimento', 'nm_causa', 'id_endosso', 't', 
                 'Total Sinistro', 'Representante', 'Corretor', 'Franquia Apólice']
    _cols_seg = [c for c in _cols_seg if c in df_sinistro_segurado.columns]
    st.dataframe(df_sinistro_segurado[_cols_seg], hide_index=True)

st.write("---")
st.caption("Desenvolvido por Alex Sousa.")
