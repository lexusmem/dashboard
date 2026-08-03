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
    # Os status "pendente de retorno" NÃO entram aqui: são contados no KPI
    # "Cotações/Propostas Notificadas", para não haver dupla contagem.
}


def _eh_emitida(status):
    s = str(status).lower()
    return any(t in s for t in _STATUS_EMITIDA)


def _eh_subscricao(status):
    return str(status).strip().lower() in _STATUS_SUBSCRICAO


def _eh_expirada(status):
    return 'expirad' in str(status).lower()


def _eh_emitida_estrita(status):
    """Status exatamente 'emitida' (para o KPI de Apólices Emitidas)."""
    return str(status).strip().lower() == 'emitida'


def _eh_notificada(status):
    """Cotação/proposta pendente de retorno (notificada)."""
    s = str(status).strip().lower()
    return s in ('cotação pendente de retorno', 'cotacao pendente de retorno',
                 'proposta pendente de retorno')


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

    # Subscritor (proposta tem prioridade sobre cotação) — usado nos gráficos
    sub_cot = _primeira_col(raw, 'Subscritor')
    sub_prop = _primeira_col(raw, 'Subscritor_proposta', 'Subscritor Proposta')
    sub_cot = sub_cot if sub_cot is not None else pd.Series([''] * len(raw))
    sub_prop = sub_prop if sub_prop is not None else pd.Series([''] * len(raw))
    df['Subscritor'] = sub_prop.fillna('').replace('', np.nan)\
        .fillna(sub_cot).replace('', 'Sem Subscritor Atribuído').fillna('Sem Subscritor Atribuído')

    # Coluna Subscritor ORIGINAL (só a coluna 'Subscritor' do arquivo, sem a
    # prioridade da proposta). É a que representa quem analisou a cotação — usada
    # tanto no filtro de subscritor quanto na análise de efetivação, para que
    # filtrar por um subscritor traga TODAS as cotações que ele analisou,
    # inclusive as emitidas (que no campo combinado migrariam para o subscritor
    # da proposta).
    _sub_orig = sub_cot.fillna('').astype(str).str.strip()
    df['Subscritor Analista'] = _sub_orig.replace({'': 'Sem Subscritor', 'nan': 'Sem Subscritor'})
    df['Analisada_Subscricao'] = _sub_orig.ne('') & _sub_orig.str.lower().ne('nan')

    # Subscritor da PROPOSTA (coluna Subscritor_proposta): quem assumiu a cotação
    # quando ela virou proposta. Papel distinto do analista da cotação.
    _sub_prop_orig = sub_prop.fillna('').astype(str).str.strip()
    df['Subscritor Proposta'] = _sub_prop_orig.replace({'': 'Sem Subscritor Proposta', 'nan': 'Sem Subscritor Proposta'})

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


# ── Upload (só nesta página) — some após carregar, reabre por botão ──────────
# Guarda os dados carregados em session_state para que o uploader deixe de ser
# exibido depois do carregamento. Um botão "Atualizar arquivo" reabre o uploader,
# que volta a se fechar assim que um novo arquivo é lido.
_TEXTO_UPLOAD = (
    "Carregar arquivo contendo os dados extraídos do relatório Analítico "
    "**ID_142 - Portal do Corretor - Gestão**, disponível no admseg (.xlsx, .xls ou .csv)"
)

def _ler_arquivo(_arq):
    try:
        return _carregar(_arq.getvalue(), _arq.name), None
    except ImportError as e:
        if 'openpyxl' in str(e):
            return None, (
                "Para ler arquivos **.xlsx** é necessário o pacote `openpyxl`, que não está "
                "instalado neste ambiente.\n\n"
                "**Como resolver:** adicione uma linha `openpyxl` ao `requirements.txt` do "
                "projeto e faça o deploy novamente.\n\n"
                "**Alternativa imediata:** exporte o arquivo do Portal como **.csv** e carregue-o "
                "aqui — CSV não exige `openpyxl`."
            )
        return None, f"Dependência ausente ao ler o arquivo: {e}"
    except Exception as e:
        return None, f"Não foi possível ler o arquivo: {e}"

# Estado inicial
if 'cot_df' not in st.session_state:
    st.session_state['cot_df'] = None
if 'cot_mostrar_uploader' not in st.session_state:
    st.session_state['cot_mostrar_uploader'] = True

# Uploader visível: primeira carga ou quando o usuário pediu para trocar
if st.session_state['cot_mostrar_uploader']:
    arquivo = st.file_uploader(_TEXTO_UPLOAD, type=['xlsx', 'xls', 'csv'], key='upload_cotacoes')
    if arquivo is not None:
        _df_lido, _erro = _ler_arquivo(arquivo)
        if _erro:
            st.error(_erro)
            st.stop()
        if _df_lido.empty:
            st.warning("O arquivo foi lido, mas não contém linhas de cotação.")
            st.stop()
        # Guarda e fecha o uploader
        st.session_state['cot_df'] = _df_lido
        st.session_state['cot_nome'] = arquivo.name
        st.session_state['cot_mostrar_uploader'] = False
        st.rerun()

# Sem dados ainda: instrui e para
if st.session_state['cot_df'] is None:
    st.info("⬆️ Carregue o arquivo de cotações para visualizar o painel. "
            "Nenhum dado é solicitado nas outras páginas — o upload acontece apenas aqui.")
    st.stop()

df = st.session_state['cot_df']

# ── Filtros dinâmicos ────────────────────────────────────────────────────────
# Cabeçalho dos filtros com o botão de trocar arquivo à direita, na mesma linha.
# Chaves dos filtros multiselect (usadas também pelo botão "Limpar filtros")
_FILTRO_KEYS_COT = ['f_ano_cot', 'f_perfil_cot', 'f_prod_cot', 'f_corr_cot',
                    'f_rep_cot', 'f_sub_cot', 'f_sub_prop_cot']

# Reset dos filtros ANTES de instanciar os widgets. Apagar a key de um
# multiselect só limpa o campo se for feito antes de o widget ser criado no
# rerun — se o pop for feito dentro do próprio botão (que roda DEPOIS dos
# widgets na ordem do script), o Streamlit reinstancia o valor e o campo
# continua preenchido. Por isso o botão apenas liga a flag e dá rerun; a
# limpeza efetiva acontece aqui no topo, antes dos multiselect.
if st.session_state.get('cot_limpar_filtros', False):
    for _k in _FILTRO_KEYS_COT:
        st.session_state.pop(_k, None)
    st.session_state['cot_limpar_filtros'] = False

_hcol1, _hcol2, _hcol3 = st.columns([4, 1, 1])
with _hcol1:
    st.markdown("#### 🔎 Filtros")
with _hcol2:
    if st.button("🧹 Limpar filtros", use_container_width=True):
        st.session_state['cot_limpar_filtros'] = True
        st.rerun()
with _hcol3:
    if st.button("🔄 Atualizar arquivo", use_container_width=True):
        st.session_state['cot_mostrar_uploader'] = True
        st.rerun()
c1, c2, c3, c4 = st.columns(4)
c5, c6, c7, c8 = st.columns(4)

# Filtros multiselect (ponto 3) — vazio significa "todos"
_anos = sorted([int(a) for a in df['Ano'].dropna().unique()])
with c1:
    f_ano = st.multiselect('Ano de Criação', _anos, key='f_ano_cot', placeholder='Todos')
with c2:
    f_perfil = st.multiselect('Perfil de Frota', _ORDEM_PERFIL, key='f_perfil_cot', placeholder='Todos')
with c3:
    f_produto = st.multiselect('Tipo de Produto', sorted(df['Produto'].dropna().unique()), key='f_prod_cot', placeholder='Todos')
with c4:
    f_corretor = st.multiselect('Corretor', sorted(df['Corretor'].dropna().unique()), key='f_corr_cot', placeholder='Todos')
with c5:
    f_rep = st.multiselect('Representante', sorted(df['Representante'].dropna().unique()), key='f_rep_cot', placeholder='Todos')
with c6:
    f_sub = st.multiselect('Subscritor (analista da cotação)', sorted(df['Subscritor Analista'].dropna().unique()), key='f_sub_cot', placeholder='Todos')
with c7:
    f_sub_prop = st.multiselect('Subscritor (da proposta)', sorted(df['Subscritor Proposta'].dropna().unique()), key='f_sub_prop_cot', placeholder='Todos')

d = df.copy()
if f_ano:       d = d[d['Ano'].isin(f_ano)]
if f_perfil:    d = d[d['Perfil Frota'].isin(f_perfil)]
if f_produto:   d = d[d['Produto'].isin(f_produto)]
if f_corretor:  d = d[d['Corretor'].isin(f_corretor)]
if f_rep:       d = d[d['Representante'].isin(f_rep)]
if f_sub:       d = d[d['Subscritor Analista'].isin(f_sub)]
if f_sub_prop:  d = d[d['Subscritor Proposta'].isin(f_sub_prop)]

if d.empty:
    st.warning("Nenhuma cotação corresponde aos filtros selecionados.")
    st.stop()

# ── KPIs ─────────────────────────────────────────────────────────────────────
_total = len(d)
# Apólices Emitidas: considera SOMENTE status exatamente 'emitida' (ponto 1)
_emit = d[d['Status'].map(_eh_emitida_estrita)]
_subs = d[d['Status'].map(_eh_subscricao)]
# Notificadas: pendentes de retorno (cotação ou proposta) — substitui Expiradas
_notif = d[d['Status'].map(_eh_notificada)]

_n_emit, _n_subs, _n_notif = len(_emit), len(_subs), len(_notif)
_veic = int(d['Veículos'].sum())
_prem_emit = _emit['Prêmio'].sum()
_prem_subs = _subs['Prêmio'].sum()
_prem_notif = _notif['Prêmio'].sum()
_conv = (_n_emit / _total * 100) if _total > 0 else 0
_ticket = (_prem_emit / _n_emit) if _n_emit > 0 else 0

st.markdown("#### 📊 Indicadores")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Cotações/Propostas", f"{_total:,}".replace(',', '.'),
          help=f"{_veic:,} veículos demandados".replace(',', '.'))
k2.metric("Apólices Emitidas", f"{_n_emit:,}".replace(',', '.'),
          help=f"Taxa de conversão: {_conv:.1f}%".replace('.', ','))
k3.metric("Prêmio Total Emitido (R$)", formatar_valor_br(_prem_emit),
          help=f"Ticket médio: R$ {formatar_valor_br(_ticket)}")
k4.metric("Em Subscrição/Análise", f"{_n_subs:,}".replace(',', '.'),
          help=f"Volume esteira: R$ {formatar_valor_br(_prem_subs)}")
k5.metric("Com Pendências Notificadas", f"{_n_notif:,}".replace(',', '.'),
          help=f"Pendentes de retorno · R$ {formatar_valor_br(_prem_notif)}")

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
    fig1.update_traces(texttemplate='%{y:,.0f}', textposition='outside', textfont_size=10)
    fig1.update_layout(barmode='group', height=360,
                       legend=dict(orientation='h', y=1.1), **_layout)
    st.plotly_chart(fig1, use_container_width=True)

with g2:
    st.markdown("**Evolução Temporal por Produto** · cotações por modalidade")
    _ev_prod = d[d['Ano'].notna()].groupby(['Ano', 'Produto']).size().reset_index(name='Cotações')
    _ev_prod['Ano'] = _ev_prod['Ano'].astype(int).astype(str)
    fig2 = px.bar(_ev_prod, x='Ano', y='Cotações', color='Produto', height=360, text_auto='.0f')
    fig2.update_traces(textposition='inside', textfont_size=9)
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
    fig3.update_traces(texttemplate='%{x:,.0f}', textposition='outside', textfont_size=10)
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
    fig4.update_traces(texttemplate='%{y:.1f}%', textposition='outside', textfont_size=10)
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
    fig5.update_traces(texttemplate='%{x:,.0f}', textposition='outside', textfont_size=9)
    fig5.update_layout(barmode='group', height=380, legend=dict(orientation='h', y=1.1), **_layout)
    st.plotly_chart(fig5, use_container_width=True)

with g6:
    st.markdown("**Atuação dos Subscritores** · demandas analisadas e efetivadas")
    # Exclui registros sem subscritor atribuído (ponto 4)
    _SEM_SUB = ('Sem Subscritor', 'Sem Subscritor Atribuído', 'Sem Subscritor Proposta')
    _d_sub = d[~d['Subscritor'].isin(_SEM_SUB)]
    _emit_sub = _emit[~_emit['Subscritor'].isin(_SEM_SUB)]
    _cs = _d_sub.groupby('Subscritor').size().reset_index(name='Demandas')
    _es = _emit_sub.groupby('Subscritor').size().reset_index(name='Emitidas')
    _sub = _cs.merge(_es, on='Subscritor', how='left').fillna(0)\
        .sort_values('Demandas', ascending=False).head(12).sort_values('Demandas', ascending=True)
    fig6 = go.Figure()
    fig6.add_bar(y=_sub['Subscritor'], x=_sub['Demandas'], name='Demandas', orientation='h', marker_color=_AZUL)
    fig6.add_bar(y=_sub['Subscritor'], x=_sub['Emitidas'], name='Emitidas', orientation='h', marker_color=_VERDE)
    fig6.update_traces(texttemplate='%{x:,.0f}', textposition='outside', textfont_size=9)
    fig6.update_layout(barmode='group', height=380, legend=dict(orientation='h', y=1.1), **_layout)
    st.plotly_chart(fig6, use_container_width=True)

# ── Gráfico 7 e 8: Status e Top Corretores ───────────────────────────────────
g7, g8 = st.columns(2)

with g7:
    st.markdown("**Visão Geral por Status** · estágio atual das cotações")
    _stt = d.groupby('Status').size().reset_index(name='Qtd').sort_values('Qtd', ascending=False)
    fig7 = px.pie(_stt, names='Status', values='Qtd', hole=0.45, height=380)
    fig7.update_traces(textinfo='percent+value', textfont_size=10)
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
    fig8.update_traces(texttemplate='%{x:,.0f}', textposition='outside', textfont_size=9)
    fig8.update_layout(barmode='group', height=380, legend=dict(orientation='h', y=1.1), **_layout)
    st.plotly_chart(fig8, use_container_width=True)

st.write("---")

# ── Análise de Efetivação da Subscrição ──────────────────────────────────────
# Cotações com a coluna "Subscritor" preenchida = analisadas pela subscrição.
# Dessas, quantas foram efetivadas (status emitida). Cruzado por perfil e produto.
st.markdown("#### 🔍 Efetivação da Subscrição — cotações analisadas que viraram apólice")
st.caption(
    "Considera analisadas pela subscrição as cotações com a coluna **Subscritor** "
    "preenchida. Entre elas, as **efetivadas** são as que atingiram status de emitida."
)

_analisadas = d[d['Analisada_Subscricao']]
_analisadas_emit = _analisadas[_analisadas['Status'].map(_eh_emitida_estrita)]

_n_analisadas = len(_analisadas)
_n_efetivadas = len(_analisadas_emit)
_taxa_efet = (_n_efetivadas / _n_analisadas * 100) if _n_analisadas > 0 else 0

sc1, sc2, sc3 = st.columns(3)
sc1.metric("Cotações Analisadas pela Subscrição", f"{_n_analisadas:,}".replace(',', '.'))
sc2.metric("Analisadas que viraram Apólice", f"{_n_efetivadas:,}".replace(',', '.'))
sc3.metric("Taxa de Efetivação", f"{_taxa_efet:.1f}%".replace('.', ','))

if _n_analisadas == 0:
    st.info("Nenhuma cotação analisada pela subscrição (coluna Subscritor preenchida) "
            "no recorte de filtros atual.")
else:
    def _resumo_efetivacao(_dim):
        _an = _analisadas.groupby(_dim).size().reset_index(name='Analisadas')
        _ef = _analisadas_emit.groupby(_dim).size().reset_index(name='Efetivadas')
        _res = _an.merge(_ef, on=_dim, how='left').fillna(0)
        _res['Efetivadas'] = _res['Efetivadas'].astype(int)
        _res['Taxa de Efetivação'] = _res.apply(
            lambda r: r['Efetivadas'] / r['Analisadas'] if r['Analisadas'] > 0 else 0, axis=1)
        return _res.sort_values('Analisadas', ascending=False)

    se1, se2 = st.columns(2)

    # Por Perfil de Frota
    with se1:
        st.markdown("**Por Perfil de Frota**")
        _ef_perfil = _resumo_efetivacao('Perfil Frota')
        # ordena pela ordem natural das faixas
        _ef_perfil['__ord'] = _ef_perfil['Perfil Frota'].map(
            {p: i for i, p in enumerate(_ORDEM_PERFIL)}).fillna(99)
        _ef_perfil = _ef_perfil.sort_values('__ord')

        fig_efp = go.Figure()
        fig_efp.add_bar(x=_ef_perfil['Perfil Frota'], y=_ef_perfil['Analisadas'],
                        name='Analisadas', marker_color=_AZUL)
        fig_efp.add_bar(x=_ef_perfil['Perfil Frota'], y=_ef_perfil['Efetivadas'],
                        name='Efetivadas', marker_color=_VERDE)
        fig_efp.update_traces(texttemplate='%{y:,.0f}', textposition='outside', textfont_size=10)
        fig_efp.update_layout(barmode='group', height=340,
                              legend=dict(orientation='h', y=1.12), **_layout)
        st.plotly_chart(fig_efp, use_container_width=True)

        _tp = _ef_perfil[['Perfil Frota', 'Analisadas', 'Efetivadas', 'Taxa de Efetivação']].copy()
        _tp['Taxa de Efetivação'] = _tp['Taxa de Efetivação'].map(lambda x: f"{x:.1%}".replace('.', ','))
        st.dataframe(_tp, hide_index=True, use_container_width=True)

    # Por Produto
    with se2:
        st.markdown("**Por Tipo de Produto**")
        _ef_prod = _resumo_efetivacao('Produto')

        fig_efpr = go.Figure()
        fig_efpr.add_bar(x=_ef_prod['Produto'], y=_ef_prod['Analisadas'],
                         name='Analisadas', marker_color=_AZUL)
        fig_efpr.add_bar(x=_ef_prod['Produto'], y=_ef_prod['Efetivadas'],
                         name='Efetivadas', marker_color=_VERDE)
        fig_efpr.update_traces(texttemplate='%{y:,.0f}', textposition='outside', textfont_size=10)
        fig_efpr.update_layout(barmode='group', height=340,
                               legend=dict(orientation='h', y=1.12), **_layout)
        st.plotly_chart(fig_efpr, use_container_width=True)

        _tpr = _ef_prod[['Produto', 'Analisadas', 'Efetivadas', 'Taxa de Efetivação']].copy()
        _tpr['Taxa de Efetivação'] = _tpr['Taxa de Efetivação'].map(lambda x: f"{x:.1%}".replace('.', ','))
        st.dataframe(_tpr, hide_index=True, use_container_width=True)

    # Cruzamento Perfil × Produto (taxa de efetivação)
    st.markdown("**Taxa de Efetivação: Perfil de Frota × Produto**")
    _an_cru = _analisadas.groupby(['Perfil Frota', 'Produto']).size().reset_index(name='Analisadas')
    _ef_cru = _analisadas_emit.groupby(['Perfil Frota', 'Produto']).size().reset_index(name='Efetivadas')
    _cru = _an_cru.merge(_ef_cru, on=['Perfil Frota', 'Produto'], how='left').fillna(0)
    _cru['Taxa'] = _cru.apply(lambda r: r['Efetivadas'] / r['Analisadas'] * 100 if r['Analisadas'] > 0 else 0, axis=1)
    _piv = _cru.pivot_table(index='Perfil Frota', columns='Produto', values='Taxa', aggfunc='first')
    _piv = _piv.reindex([p for p in _ORDEM_PERFIL if p in _piv.index])
    if not _piv.empty:
        fig_heat = px.imshow(_piv, color_continuous_scale='Greens', aspect='auto',
                             height=320, text_auto='.0f',
                             labels=dict(color='Taxa de Efetivação (%)'))
        fig_heat.update_layout(**_layout)
        st.plotly_chart(fig_heat, use_container_width=True)
        st.caption("Percentual de cotações analisadas que viraram apólice, por combinação "
                   "de perfil de frota e produto. Células mais escuras = maior efetivação.")

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
