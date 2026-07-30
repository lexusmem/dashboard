import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from allseg_theme import aplicar_tema

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: DADOS COTAÇÕES — análise das cotações/propostas do Portal do Corretor
# Reescrita 100% nativa em Streamlit + Plotly (sem HTML/iframe).
# O arquivo de cotações só é solicitado ao acessar esta página (uploader próprio).
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(layout='wide', page_title='Dados Cotações — Allseg', page_icon='📝')
aplicar_tema()

# ── Navegação na sidebar (padrão das demais páginas) ─────────────────────────
st.sidebar.header('Navegação')
st.sidebar.page_link("app.py", label="📋  Apólice / Segurado")
st.sidebar.page_link("pages/2_Dados_Gerais.py", label="📊  Dados Gerais")
st.sidebar.page_link("pages/3_Dados_Cotacoes.py", label="📝  Dados Cotações")

st.title("📝 Análise de Cotações e Propostas")
st.caption("Painel comercial e de subscrição — RC Ônibus · dados extraídos do Portal do Corretor")


# ── Utilitários ──────────────────────────────────────────────────────────────
def formatar_valor_br(v):
    try:
        return f"{float(v):,.2f}".replace(',', '#').replace('.', ',').replace('#', '.')
    except (ValueError, TypeError):
        return "0,00"


def _primeira_col(df, *nomes):
    """Retorna a primeira coluna existente dentre os nomes alternativos."""
    for n in nomes:
        if n in df.columns:
            return df[n]
    return None


def _perfil_frota(n):
    if n == 1:
        return '1 Veículo'
    if 2 <= n <= 10:
        return '2 a 10 Veículos'
    if 11 <= n <= 30:
        return '11 a 30 Veículos'
    if n > 30:
        return '31+ Veículos'
    return '1 Veículo'


_ORDEM_PERFIL = ['1 Veículo', '2 a 10 Veículos', '11 a 30 Veículos', '31+ Veículos']

# Regras de status (idênticas ao dashboard original)
_STATUS_EMITIDA = ('emitid', 'efetivad', 'integrad')
_STATUS_SUBSCRICAO = {
    'subscrição', 'subscricao', 'subscrição proposta', 'subscricao proposta',
    'em análise', 'em analise', 'em análise proposta', 'em analise proposta',
    'cotação pendente de retorno', 'cotacao pendente de retorno',
    'proposta pendente de retorno',
}


def _eh_emitida(status):
    s = str(status).lower()
    return any(t in s for t in _STATUS_EMITIDA)


def _eh_subscricao(status):
    return str(status).strip().lower() in _STATUS_SUBSCRICAO


def _eh_expirada(status):
    return 'expirad' in str(status).lower()


@st.cache_data(show_spinner=False)
def _carregar(arquivo_bytes, nome):
    """Lê o arquivo (xlsx/xls/csv) e normaliza as colunas."""
    import io
    if nome.lower().endswith(('.xlsx', '.xls')):
        raw = pd.read_excel(io.BytesIO(arquivo_bytes))
    else:
        # CSV — tenta separadores comuns
        for sep in (';', ','):
            try:
                raw = pd.read_csv(io.BytesIO(arquivo_bytes), sep=sep, encoding='utf-8-sig')
                if raw.shape[1] > 1:
                    break
            except Exception:
                continue
        else:
            raw = pd.read_csv(io.BytesIO(arquivo_bytes))

    df = pd.DataFrame()
    df['Cotação']       = _primeira_col(raw, 'Cotação', 'Cotacao')
    df['Produto']       = _primeira_col(raw, 'Produto')
    df['Corretor']      = _primeira_col(raw, 'Corretor')
    df['Representante'] = _primeira_col(raw, 'Representante')
    df['Cliente']       = _primeira_col(raw, 'Cliente')
    df['Documento']     = _primeira_col(raw, 'Documento', 'CNPJ/CPF')
    df['Status']        = _primeira_col(raw, 'Status_Cotacão', 'Status_Cotacao', 'Status')
    df['Apólice']       = _primeira_col(raw, 'Apólice', 'Apolice')

    # Prêmio — trata tanto valores já numéricos (float do Excel) quanto texto
    # em formato brasileiro ("1.234,56"). Só aplica a limpeza BR quando o dado
    # vem como texto, para não corromper floats (ex.: 5257.0 -> 52570).
    premio = _primeira_col(raw, 'Prêmio', 'Prêmio Total', 'valor premio liquido', 'Valor Prêmio')
    if premio is None:
        premio = pd.Series([0] * len(raw))
    if pd.api.types.is_numeric_dtype(premio):
        df['Prêmio'] = pd.to_numeric(premio, errors='coerce').fillna(0.0)
    else:
        _p = (premio.astype(str)
              .str.replace(r'[^\d.,-]', '', regex=True)
              .str.replace('.', '', regex=False)   # remove separador de milhar
              .str.replace(',', '.', regex=False))  # vírgula decimal -> ponto
        df['Prêmio'] = pd.to_numeric(_p, errors='coerce').fillna(0.0)

    # Veículos
    veic = _primeira_col(raw, 'num_veiculo', 'num_veiculos', 'Veículos', 'Qtd Veículos')
    if veic is None:
        veic = pd.Series([1] * len(raw))
    df['Veículos'] = pd.to_numeric(
        veic.astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(1).astype(int)
    df['Veículos'] = df['Veículos'].replace(0, 1)

    # Subscritor (proposta tem prioridade sobre cotação)
    sub_cot = _primeira_col(raw, 'Subscritor')
    sub_prop = _primeira_col(raw, 'Subscritor_proposta', 'Subscritor Proposta')
    sub_cot = sub_cot if sub_cot is not None else pd.Series([''] * len(raw))
    sub_prop = sub_prop if sub_prop is not None else pd.Series([''] * len(raw))
    df['Subscritor'] = sub_prop.fillna('').replace('', np.nan)\
        .fillna(sub_cot).replace('', 'Sem Subscritor Atribuído').fillna('Sem Subscritor Atribuído')

    # Data de criação e ano
    criacao = _primeira_col(raw, 'Criação', 'Criacao')
    if criacao is not None:
        dt = pd.to_datetime(criacao, errors='coerce', dayfirst=True)
        df['Data Criação'] = dt
        df['Ano'] = dt.dt.year
    else:
        df['Data Criação'] = pd.NaT
        df['Ano'] = np.nan

    # Defaults textuais
    df['Produto'] = df['Produto'].fillna('RCO Ônibus').replace('', 'RCO Ônibus')
    df['Corretor'] = df['Corretor'].fillna('Não Informado').replace('', 'Não Informado')
    df['Representante'] = df['Representante'].fillna('Direto / Outros').replace('', 'Direto / Outros')
    df['Cliente'] = df['Cliente'].fillna('Não Informado').replace('', 'Não Informado')
    df['Status'] = df['Status'].fillna('Outros').replace('', 'Outros')
    df['Apólice'] = df['Apólice'].fillna('-').replace('', '-')
    df['Perfil Frota'] = df['Veículos'].map(_perfil_frota)

    return df


# ── Upload (só nesta página) ─────────────────────────────────────────────────
arquivo = st.file_uploader(
    "Selecione a planilha de Cotações / Propostas (.xlsx, .xls ou .csv extraído do Portal do Corretor)",
    type=['xlsx', 'xls', 'csv'],
    key='upload_cotacoes'
)

if arquivo is None:
    st.info("⬆️ Carregue o arquivo de cotações para visualizar o painel. "
            "Nenhum dado é solicitado nas outras páginas — o upload acontece apenas aqui.")
    st.stop()

try:
    df = _carregar(arquivo.getvalue(), arquivo.name)
except Exception as e:
    st.error(f"Não foi possível ler o arquivo: {e}")
    st.stop()

if df.empty:
    st.warning("O arquivo foi lido, mas não contém linhas de cotação.")
    st.stop()

# ── Filtros dinâmicos ────────────────────────────────────────────────────────
st.markdown("#### 🔎 Filtros")
c1, c2, c3, c4, c5, c6 = st.columns(6)

_anos = sorted([int(a) for a in df['Ano'].dropna().unique()])
with c1:
    f_ano = st.selectbox('Ano de Criação', ['Todos'] + _anos, key='f_ano_cot')
with c2:
    f_perfil = st.selectbox('Perfil de Frota', ['Todos'] + _ORDEM_PERFIL, key='f_perfil_cot')
with c3:
    f_produto = st.selectbox('Tipo de Produto', ['Todos'] + sorted(df['Produto'].dropna().unique()), key='f_prod_cot')
with c4:
    f_corretor = st.selectbox('Corretor', ['Todos'] + sorted(df['Corretor'].dropna().unique()), key='f_corr_cot')
with c5:
    f_rep = st.selectbox('Representante', ['Todos'] + sorted(df['Representante'].dropna().unique()), key='f_rep_cot')
with c6:
    f_sub = st.selectbox('Subscritor', ['Todos'] + sorted(df['Subscritor'].dropna().unique()), key='f_sub_cot')

d = df.copy()
if f_ano != 'Todos':       d = d[d['Ano'] == f_ano]
if f_perfil != 'Todos':    d = d[d['Perfil Frota'] == f_perfil]
if f_produto != 'Todos':   d = d[d['Produto'] == f_produto]
if f_corretor != 'Todos':  d = d[d['Corretor'] == f_corretor]
if f_rep != 'Todos':       d = d[d['Representante'] == f_rep]
if f_sub != 'Todos':       d = d[d['Subscritor'] == f_sub]

if d.empty:
    st.warning("Nenhuma cotação corresponde aos filtros selecionados.")
    st.stop()

# ── KPIs ─────────────────────────────────────────────────────────────────────
_total = len(d)
_emit = d[d['Status'].map(_eh_emitida)]
_subs = d[d['Status'].map(_eh_subscricao)]
_exp  = d[d['Status'].map(_eh_expirada)]

_n_emit, _n_subs, _n_exp = len(_emit), len(_subs), len(_exp)
_veic = int(d['Veículos'].sum())
_prem_emit = _emit['Prêmio'].sum()
_prem_subs = _subs['Prêmio'].sum()
_prem_exp  = _exp['Prêmio'].sum()
_conv = (_n_emit / _total * 100) if _total > 0 else 0
_ticket = (_prem_emit / _n_emit) if _n_emit > 0 else 0

st.markdown("#### 📊 Indicadores")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Cotações/Propostas", f"{_total:,}".replace(',', '.'),
          help=f"{_veic:,} veículos demandados".replace(',', '.'))
k2.metric("Apólices Emitidas", f"{_n_emit:,}".replace(',', '.'),
          help=f"Taxa de conversão: {_conv:.1f}%".replace('.', ','))
k3.metric("Prêmio Emitido (R$)", formatar_valor_br(_prem_emit),
          help=f"Ticket médio: R$ {formatar_valor_br(_ticket)}")
k4.metric("Em Subscrição/Análise", f"{_n_subs:,}".replace(',', '.'),
          help=f"Volume esteira: R$ {formatar_valor_br(_prem_subs)}")
k5.metric("Cotações Expiradas", f"{_n_exp:,}".replace(',', '.'),
          help=f"Prêmio expirado: R$ {formatar_valor_br(_prem_exp)}")

st.caption(f"Taxa de conversão: **{_conv:.1f}%**".replace('.', ',') +
           f"  ·  Ticket médio emitido: **R$ {formatar_valor_br(_ticket)}**")

_AZUL, _VERDE, _LARANJA = '#0284c7', '#10b981', '#f59e0b'
_layout = dict(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
               margin=dict(t=30, b=10, l=10, r=10))

st.write("---")

# ── Gráfico 1 e 2: Evolução temporal ─────────────────────────────────────────
g1, g2 = st.columns(2)

with g1:
    st.markdown("**Evolução Temporal Ano a Ano** · cotações solicitadas vs. emitidas")
    _por_ano = d.groupby('Ano').size().reset_index(name='Cotações')
    _emit_ano = _emit.groupby('Ano').size().reset_index(name='Emitidas')
    _ev = _por_ano.merge(_emit_ano, on='Ano', how='left').fillna(0)
    _ev = _ev[_ev['Ano'].notna()].sort_values('Ano')
    _ev['Ano'] = _ev['Ano'].astype(int).astype(str)
    fig1 = go.Figure()
    fig1.add_bar(x=_ev['Ano'], y=_ev['Cotações'], name='Cotações Solicitadas', marker_color=_AZUL)
    fig1.add_bar(x=_ev['Ano'], y=_ev['Emitidas'], name='Apólices Emitidas', marker_color=_VERDE)
    fig1.update_layout(barmode='group', height=360,
                       legend=dict(orientation='h', y=1.1), **_layout)
    st.plotly_chart(fig1, use_container_width=True)

with g2:
    st.markdown("**Evolução Temporal por Produto** · cotações por modalidade")
    _ev_prod = d[d['Ano'].notna()].groupby(['Ano', 'Produto']).size().reset_index(name='Cotações')
    _ev_prod['Ano'] = _ev_prod['Ano'].astype(int).astype(str)
    fig2 = px.bar(_ev_prod, x='Ano', y='Cotações', color='Produto', height=360)
    fig2.update_layout(barmode='stack', legend=dict(orientation='h', y=1.1), **_layout)
    st.plotly_chart(fig2, use_container_width=True)

# ── Gráfico 3 e 4: Produto e Perfil de Frota ─────────────────────────────────
g3, g4 = st.columns(2)

with g3:
    st.markdown("**Desempenho por Tipo de Produto** · cotações vs. emitidas")
    _pp = d.groupby('Produto').size().reset_index(name='Cotações')
    _pe = _emit.groupby('Produto').size().reset_index(name='Emitidas')
    _prod = _pp.merge(_pe, on='Produto', how='left').fillna(0).sort_values('Cotações', ascending=True)
    fig3 = go.Figure()
    fig3.add_bar(y=_prod['Produto'], x=_prod['Cotações'], name='Cotações', orientation='h', marker_color=_AZUL)
    fig3.add_bar(y=_prod['Produto'], x=_prod['Emitidas'], name='Emitidas', orientation='h', marker_color=_VERDE)
    fig3.update_layout(barmode='group', height=360, legend=dict(orientation='h', y=1.1), **_layout)
    st.plotly_chart(fig3, use_container_width=True)

with g4:
    st.markdown("**Análise por Perfil de Frota** · % do volume cotado vs. taxa de conversão")
    _cot_perf = d.groupby('Perfil Frota').size()
    _emit_perf = _emit.groupby('Perfil Frota').size()
    _rows = []
    for p in _ORDEM_PERFIL:
        c = int(_cot_perf.get(p, 0))
        e = int(_emit_perf.get(p, 0))
        pct_vol = (c / _total * 100) if _total > 0 else 0
        pct_conv = (e / c * 100) if c > 0 else 0
        _rows.append({'Perfil': p, '% Volume Cotado': round(pct_vol, 1), '% Conversão': round(pct_conv, 1)})
    _pf = pd.DataFrame(_rows)
    fig4 = go.Figure()
    fig4.add_bar(x=_pf['Perfil'], y=_pf['% Volume Cotado'], name='% do Volume Total Cotado', marker_color=_AZUL)
    fig4.add_bar(x=_pf['Perfil'], y=_pf['% Conversão'], name='% Taxa de Conversão', marker_color=_VERDE)
    fig4.update_layout(barmode='group', height=360, yaxis=dict(ticksuffix='%', range=[0, 100]),
                       legend=dict(orientation='h', y=1.1), **_layout)
    st.plotly_chart(fig4, use_container_width=True)

# ── Gráfico 5 e 6: Representante e Subscritor ────────────────────────────────
g5, g6 = st.columns(2)

with g5:
    st.markdown("**Volume por Representante Comercial** · cotações vs. emitidas")
    _cr = d.groupby('Representante').size().reset_index(name='Cotações')
    _er = _emit.groupby('Representante').size().reset_index(name='Emitidas')
    _rep = _cr.merge(_er, on='Representante', how='left').fillna(0)\
        .sort_values('Cotações', ascending=False).head(12).sort_values('Cotações', ascending=True)
    fig5 = go.Figure()
    fig5.add_bar(y=_rep['Representante'], x=_rep['Cotações'], name='Cotações', orientation='h', marker_color=_AZUL)
    fig5.add_bar(y=_rep['Representante'], x=_rep['Emitidas'], name='Emitidas', orientation='h', marker_color=_VERDE)
    fig5.update_layout(barmode='group', height=380, legend=dict(orientation='h', y=1.1), **_layout)
    st.plotly_chart(fig5, use_container_width=True)

with g6:
    st.markdown("**Atuação dos Subscritores** · demandas analisadas e efetivadas")
    _cs = d.groupby('Subscritor').size().reset_index(name='Demandas')
    _es = _emit.groupby('Subscritor').size().reset_index(name='Emitidas')
    _sub = _cs.merge(_es, on='Subscritor', how='left').fillna(0)\
        .sort_values('Demandas', ascending=False).head(12).sort_values('Demandas', ascending=True)
    fig6 = go.Figure()
    fig6.add_bar(y=_sub['Subscritor'], x=_sub['Demandas'], name='Demandas', orientation='h', marker_color=_AZUL)
    fig6.add_bar(y=_sub['Subscritor'], x=_sub['Emitidas'], name='Emitidas', orientation='h', marker_color=_VERDE)
    fig6.update_layout(barmode='group', height=380, legend=dict(orientation='h', y=1.1), **_layout)
    st.plotly_chart(fig6, use_container_width=True)

# ── Gráfico 7 e 8: Status e Top Corretores ───────────────────────────────────
g7, g8 = st.columns(2)

with g7:
    st.markdown("**Visão Geral por Status** · estágio atual das cotações")
    _stt = d.groupby('Status').size().reset_index(name='Qtd').sort_values('Qtd', ascending=False)
    fig7 = px.pie(_stt, names='Status', values='Qtd', hole=0.45, height=380)
    fig7.update_layout(**_layout)
    st.plotly_chart(fig7, use_container_width=True)

with g8:
    st.markdown("**Top Corretores** · cotações vs. emitidas")
    _cc = d.groupby('Corretor').size().reset_index(name='Cotações')
    _ec = _emit.groupby('Corretor').size().reset_index(name='Emitidas')
    _corr = _cc.merge(_ec, on='Corretor', how='left').fillna(0)\
        .sort_values('Cotações', ascending=False).head(10).sort_values('Cotações', ascending=True)
    fig8 = go.Figure()
    fig8.add_bar(y=_corr['Corretor'], x=_corr['Cotações'], name='Cotações', orientation='h', marker_color=_AZUL)
    fig8.add_bar(y=_corr['Corretor'], x=_corr['Emitidas'], name='Emitidas', orientation='h', marker_color=_VERDE)
    fig8.update_layout(barmode='group', height=380, legend=dict(orientation='h', y=1.1), **_layout)
    st.plotly_chart(fig8, use_container_width=True)

st.write("---")

# ── Tabela operacional ───────────────────────────────────────────────────────
st.markdown("#### 📋 Listagem Operacional de Propostas & Cotações")
_tab = d.copy()
_tab['Data Criação'] = _tab['Data Criação'].dt.strftime('%d/%m/%Y').fillna('-')
_tab['Prêmio (R$)'] = _tab['Prêmio'].map(formatar_valor_br)
_cols_tab = ['Data Criação', 'Produto', 'Cliente', 'Corretor', 'Subscritor',
             'Perfil Frota', 'Prêmio (R$)', 'Status', 'Apólice']
st.dataframe(_tab[_cols_tab], hide_index=True, use_container_width=True, height=420)
st.caption(f"{len(_tab):,} registros após filtros.".replace(',', '.'))
