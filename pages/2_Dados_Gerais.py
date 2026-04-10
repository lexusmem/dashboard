import streamlit as st
import pandas as pd
import io
import base64
import logging
import plotly.graph_objects as go
import plotly.express as px
import streamlit_antd_components as sac
from datetime import datetime

st.set_page_config(layout='wide')

st.markdown("""
    <style>
    .main .block-container {
        overflow-y: visible !important;
        max-width: 95% !important;
        padding-bottom: 10rem !important;
    }
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-thumb { background: #888; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

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

# Prepara dados_exibicao
dados_exibicao = dados_calculados.copy()
dados_exibicao['Soma Prêmio Pago por Apolice'] = dados_exibicao['Soma Prêmio Pago por Apolice'].astype(object)
dados_exibicao['Soma Sinistro Por Apolice']     = dados_exibicao['Soma Sinistro Por Apolice'].astype(object)
dados_exibicao['% Sin'] = dados_exibicao.apply(
    lambda row: '{:.2%}'.format(row['Soma Sinistro Por Apolice'] / row['Soma Prêmio Pago por Apolice'])
    if row['Soma Prêmio Pago por Apolice'] != 0 else '0.00%', axis=1
)
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
st.sidebar.markdown("---")
if st.sidebar.button("📋  Ir para Apólice / Segurado", use_container_width=True):
    st.switch_page("app_homologacao.py")
st.sidebar.markdown("---")

# --- Lógica de Filtragem Hierárquica na Sidebar ---
st.sidebar.header('Filtros Dados Gerais')

# Botão para Resetar Filtros — limpa todas as keys do session_state
_filtro_keys = ['filtro_rep', 'filtro_cor', 'filtro_seg', 'filtro_ramo', 'filtro_util', 'filtro_tp_emissao', 'filtro_regiao', 'filtro_uf', 'filtro_apolice']

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

st.write("---")
st.subheader("Dados Gerais")

# ============= PARTE REFERENTE AO SLIDER PARA SELECIONAR ANO =============
col_esq, col_meio, col_dir = st.columns([4,1,1])

# Definir os limites do slider com base nos dados filtrados pela sidebar
ano_min_absoluto = int(resultado_final_filtrado['Ano Vigência'].min())
ano_max_absoluto = int(resultado_final_filtrado['Ano Vigência'].max())

with col_esq:
    # Criar o Slider de Intervalo (Range Slider)
    if ano_min_absoluto < ano_max_absoluto:
        # Título customizado com espaçamento para não colar no slider
        st.text("Selecione o Intervalo de Anos (Início de Vigência Apólice)")
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
df_sinistro_periodo_atualizado = df_sinistro_geral_filtrado[df_sinistro_geral_filtrado['N° Apólice'].isin(lista_apos_periodo)]
qtd_sinistros_geral = df_sinistro_periodo_atualizado['nr_sinistro'].nunique()
# --------------------------------

# Colunas para informações do dados gerias
st.markdown("<br>", unsafe_allow_html=True) # Espaço antes dos KPIs
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(label="Total Prêmio Pago", value=f"R$ {formatar_valor_br(total_premio)}")
with col2:
    st.metric(label="Total Sinistro", value=f"R$ {formatar_valor_br(total_sinistro)}")
with col3:
    st.metric(label="% Sinistralidade", value=f"{percentual_sinistro_total:.2%}")
with col4:
    st.metric(label="Qtd. Apólices", value=qtd_apolice_geral) # Agora atualiza com o slider!
with col5:
    st.metric(label="Qtd. Sinistros", value=qtd_sinistros_geral) # Agora atualiza com o slider!

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
    st.subheader("Evolução Anual")
    st.plotly_chart(fig_evolucao, use_container_width=True, config={'displayModeBar': False})
with col_linha_barra_2:
    # plot grafico barras premio x sinistro
    # st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Prêmio x Sinistro Anual")
    st.plotly_chart(fig_barras_h, use_container_width=True, config={'displayModeBar': False})
    st.markdown("<br><br>", unsafe_allow_html=True)


# ============= ANÁLISE CONSOLIDADA POR ANO (DADOS GERAIS) =============
# 1. Agrupamento por Ano (Prêmio, Sinistro e Qtd Apólices)
# Utilizamos o df_para_soma que já contém os dados filtrados
df_ano_geral = df_para_soma.groupby('Ano Vigência').agg(
    Total_Premio=('Soma Prêmio Pago por Apolice', 'sum'),
    Total_Sinistro=('Soma Sinistro Por Apolice', 'sum'),
    Qtd_Apolices=('N° Apólice', 'nunique')
).reset_index()

# 2. Busca a quantidade de sinistros por ano
# Filtramos a base de sinistros para as apólices que pertencem ao período selecionado
lista_apos_ano = df_para_soma['N° Apólice'].unique()
df_sin_filtrado_ano = df_sinistros[df_sinistros['N° Apólice'].isin(lista_apos_ano)].copy()

# Extraímos o ano da data de ocorrência para contagem correta
df_sin_filtrado_ano['Ano_Ocorrencia'] = pd.to_datetime(df_sin_filtrado_ano['dt_ocorrencia'], dayfirst=True).dt.year

qtd_sin_por_ano = df_sin_filtrado_ano.groupby('Ano_Ocorrencia')['nr_sinistro'].nunique().reset_index()
qtd_sin_por_ano.rename(columns={'Ano_Ocorrencia': 'Ano Vigência', 'nr_sinistro': 'Qtd_Sinistros'}, inplace=True)

# 3. Cruzamento dos dados de Prêmio e Sinistro
df_final_ano = pd.merge(df_ano_geral, qtd_sin_por_ano, on='Ano Vigência', how='left').fillna(0)

# 4. Cálculo da Sinistralidade (numérico para o gráfico)
df_final_ano['Sinistralidade_Num'] = df_final_ano.apply(
    lambda row: (row['Total_Sinistro'] / row['Total_Premio']) if row['Total_Premio'] != 0 else 0, axis=1
)

# 5. Formatação para a Tabela de Exibição
df_ano_view = df_final_ano.copy()
df_ano_view['Total_Premio'] = df_ano_view['Total_Premio'].map(formatar_valor_br) # Usa sua função de formatação
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
    st.subheader("Desempenho Consolidado por Ano")
    st.dataframe(df_ano_view[['Ano Vigência','Total_Premio', 'Total_Sinistro', '% Sinistralidade', 'Qtd_Apolices', 'Qtd_Sinistros']], 
                hide_index=True, use_container_width=True)
with col_ano_2:
    st.subheader("Evolução da Sinistralidade (%)")
    st.plotly_chart(fig_sin_ano, use_container_width=True, config={'displayModeBar': False})

# --- Exibição dos Resultados ---
col_final_1, col_final_2 = st.columns(2)

with col_final_1:
    st.subheader("Sinistros")
    # Trazemos os nomes de Representante e Corretor para o DF que já está filtrado por ANO
    df_sinistro_final_exibicao = pd.merge(
        df_sinistro_periodo_atualizado, # Este já está filtrado pelo Slider
        dados_exibicao[['N° Apólice', 'Representante', 'Corretor']],
        on='N° Apólice',
        how='left'
    )
    
    if not df_sinistro_final_exibicao.empty:
        # Formata para exibição
        df_sinistro_final_exibicao['Total Sinistro'] = df_sinistro_final_exibicao['Total Sinistro'].map(formatar_valor_br)
        st.dataframe(df_sinistro_final_exibicao, hide_index=True)
    else:
        st.info("Nenhum sinistro no período selecionado.")
        
with col_final_2:
    st.subheader("Prêmios e Sinistros Apólices")
    # Usamos o df_geral_periodo que contém o filtro do Slider de Ano
    if not df_geral_periodo.empty:
        st.dataframe(df_geral_periodo, hide_index=True)
    else:
        st.info("Nenhum dado encontrado com os filtros selecionados.")

# --- Dados de Prêmio e Sinistro por Tipo de Emissão (Dados Gerais) ---
st.subheader("Prêmio e Sinistro por Tipo de Emissão")

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
    st.subheader("Prêmio e Sinistro por Utilização")

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
    st.subheader("Gráfico Sinistralidade por Utilização")

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
    st.subheader("Prêmio e Sinistro por Ramo")
    st.dataframe(df_geral_ramo_exibicao, hide_index=True, use_container_width=True)
with c2:
    st.subheader("Sinistros por Cobertura")
    # Formatação apenas para exibição
    df_disp_cob = df_sinistro_geral_cobertura.copy()
    df_disp_cob['Total Sinistro'] = df_disp_cob['Total Sinistro'].map(formatar_valor_br)
    st.dataframe(df_disp_cob, hide_index=True, use_container_width=True)

# exibir grafico de linhas ramos e pizza das coberturas
c1, c2 = st.columns(2)
with c1:
    st.subheader("Prêmio e Sinistro por Ramo")
    st.plotly_chart(fig_ramo_geral, use_container_width=True, config={'displayModeBar': False})
with c2:
    st.subheader("Sinistros por Cobertura")
    st.plotly_chart(fig_pizza_geral, use_container_width=True, config={'displayModeBar': False})

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
            st.text(f"Dados de Sinistro por Cobertura - Ramo {r}")
            df_cob_r_view = df_cob_r.copy()
            df_cob_r_view['Total Sinistro'] = df_cob_r_view['Total Sinistro'].map(formatar_valor_br)
            st.dataframe(df_cob_r_view, hide_index=True, use_container_width=True)
            
        with col_g:
            st.text(f"Gráfico Sinistro Por Cobertura - Ramo {r}")
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
        st.subheader("Prêmio e Sinistro por Região de Circulação")
        st.dataframe(df_regiao_view, hide_index=True, use_container_width=True)

    with col_reg_graf:
        st.subheader("Top 10 Piores Regiões — Sinistralidade (%)")
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
        st.subheader("Sinistralidade por UF")
        df_uf_view = df_uf.sort_values('Sinistralidade_UF', ascending=False).copy()
        df_uf_view['% Sinistralidade'] = df_uf_view['Sinistralidade_UF'].map(lambda x: f"{x:.2%}")
        df_uf_view['Total_Premio']     = df_uf_view['Total_Premio'].map(formatar_valor_br)
        df_uf_view['Total_Sinistro']   = df_uf_view['Total_Sinistro'].map(formatar_valor_br)
        df_uf_view = df_uf_view[
            ['UF', 'Qtd_Apolices', 'Qtd_Sinistros', 'Total_Premio', 'Total_Sinistro', '% Sinistralidade']
        ]
        st.dataframe(df_uf_view, hide_index=True, use_container_width=True)

    with col_uf_mapa:
        st.subheader("Mapa de Calor")
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
st.text("Este ranking destaca os parceiros com maior volume financeiro e quantidade de apólices emitidas.")
# st.info("Este ranking destaca os parceiros com maior volume financeiro e quantidade de apólices emitidas.")

# Gerar os rankings de produção com a nova função
prod_seg = gerar_ranking_producao(df_geral_periodo, 'Segurado')
prod_cor = gerar_ranking_producao(df_geral_periodo, 'Corretor')
prod_rep = gerar_ranking_producao(df_geral_periodo, 'Representante')

# Interface em Abas
tab_p_seg, tab_p_cor, tab_p_rep = st.columns(3)

with tab_p_seg:
    st.text('Top Segurados')
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
    st.text('Top Corretores')
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
    st.text('Top Representantes')
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
st.write("---")
st.caption("Desenvolvido por Alex Sousa.")
