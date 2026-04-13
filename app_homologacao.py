import streamlit as st
import pandas as pd
import io
import base64
import logging
import plotly.graph_objects as go
import plotly.express as px
import streamlit_antd_components as sac

# Configura a página para layout amplo
st.set_page_config(layout='wide')

st.markdown("""
    <style>
    /* Forçar o contentor principal a permitir scroll sempre */
    .main .block-container {
        overflow-y: visible !important;
        max-width: 95% !important;
        padding-bottom: 10rem !important;
    }
    /* Estilizar a barra de rolagem para garantir que ela apareça */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 5px;
    }
    /* Oculta a navegação automática de páginas gerada pelo Streamlit no topo da sidebar */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)


# --- Upload dos arquivos na Sidebar ---
from datetime import datetime

# Verifica se os dados já estão carregados no session_state
dados_ja_carregados = (
    'dados_calculados' in st.session_state and
    'df_sinistros'     in st.session_state and
    not st.session_state['dados_calculados'].empty and
    not st.session_state['df_sinistros'].empty
)

if not dados_ja_carregados:
    # Mostra os uploaders apenas enquanto os dados não estiverem carregados
    st.sidebar.header("📂 Carregar Arquivos")
    st.sidebar.caption("Faça o upload dos dois arquivos TXT para carregar o dashboard.")

    upload_apolice  = st.sidebar.file_uploader("apolice_endosso.txt", type=["txt", "csv"])
    upload_sinistro = st.sidebar.file_uploader("sinistro.txt",        type=["txt", "csv"])

    if not upload_apolice or not upload_sinistro:
        st.info("👈 Faça o upload dos dois arquivos TXT na barra lateral para iniciar o dashboard.")
        st.stop()
else:
    # Dados já carregados — sidebar limpa, sem nenhuma referência aos arquivos
    upload_apolice  = None
    upload_sinistro = None

# Função para processar os dados de sinistro.
# DF com dados de Sinistros por apólice:
@st.cache_data
def carregar_e_processar_dados_sinistro(arquivo):
    try:
        # Aceita BytesIO já preparado, objeto de upload ou caminho local (string)
        if isinstance(arquivo, io.BytesIO):
            arquivo.seek(0)   # garante que está no início
            fonte = arquivo
        elif hasattr(arquivo, 'read'):
            fonte = io.BytesIO(arquivo.read())
        else:
            fonte = arquivo
        aba_sinistro = pd.read_csv(
            fonte,
            sep=';',
            encoding='latin-1',
            decimal=',',
            low_memory=False
        )

        # Garante que as colunas de valor são numéricas (proteção extra)
        colunas_valor = [
            'vl_sinistro_total', 'vl_despesa_total',
            'vl_honorario_total', 'vl_salvado_total'
        ]
        for col in colunas_valor:
            aba_sinistro[col] = pd.to_numeric(aba_sinistro[col], errors='coerce').fillna(0)

        # Cálculo unificado do Sinistro
        aba_sinistro['Total Sinistro'] = (
            aba_sinistro['vl_sinistro_total'] +
            aba_sinistro['vl_despesa_total'] +
            aba_sinistro['vl_honorario_total'] -
            aba_sinistro['vl_salvado_total']
        )

        # Limpeza e Renomeação
        aba_sinistro.reset_index(drop=True, inplace=True)
        aba_sinistro.rename(columns={'cd_apolice': 'N° Apólice'}, inplace=True)

        return aba_sinistro.fillna(0)

    except Exception as e:
        st.error(f"Erro ao carregar sinistros: {e}")
        return pd.DataFrame()


# Dados agrupado de apólices e sinistros:
@st.cache_data
def carregar_e_processar_dados(arquivo_apolice, arquivo_sinistro):
    """
    Carrega e processa os dados dos arquivos TXT separados por ";".
    Esta função é cacheada para evitar recarregar e reprocessar os dados
    a cada interação do usuário, tornando a aplicação mais rápida.
    """
    try:
        # Aceita BytesIO já preparado, objeto de upload ou caminho local (string)
        if isinstance(arquivo_apolice, io.BytesIO):
            arquivo_apolice.seek(0)
            fonte_apolice = arquivo_apolice
        elif hasattr(arquivo_apolice, 'read'):
            fonte_apolice = io.BytesIO(arquivo_apolice.read())
        else:
            fonte_apolice = arquivo_apolice
        # Carrega o arquivo apolice_endosso.txt
        aba_apolice_endosso = pd.read_csv(
            fonte_apolice,
            sep=';',
            encoding='latin-1',
            decimal=',',
            low_memory=False
        )

        # Garante que vl_tarifario_pago é numérico (proteção extra)
        aba_apolice_endosso['vl_tarifario_pago'] = pd.to_numeric(
            aba_apolice_endosso['vl_tarifario_pago'], errors='coerce'
        ).fillna(0)

        # Fazer a soma dos prêmios agrupado por apólice:
        soma_por_apolice = aba_apolice_endosso.groupby('cd_apolice')['vl_tarifario_pago'].sum().reset_index()
        # reset_index cria coluna com index por linha

        soma_por_apolice.rename(columns={'cd_apolice': 'N° Apólice', 'vl_tarifario_pago': 'Soma Prêmio Pago por Apolice'}, inplace=True)
        # inplace=true faz alteração na propria variavel sem necessidade de cria uma nova variavel com a alteração.

        # Dados adicionais dos dados das apólices:
        colunas_adicionais = [
            'cd_apolice',
            'nm_estipulante',
            'dt_ini_vig_apo',
            'dt_fim_vig_apo',
            'nm_auto_utilizacao',
            'nm_corretor',
            'nm_representante',
            'nr_ramo',
            'nm_tp_apolice',
            'nm_tp_cobranca',
            'nm_regiao_circulacao',
            'nm_uf_cliente',
            'nm_cidade',
            'nm_produto'
        ]

        # Selecionar as colunas adicionais, eliminando duplicatas por 'cd_apolice'
        dados_adicionais = aba_apolice_endosso[colunas_adicionais].drop_duplicates(subset='cd_apolice')
        # seleciona as colunas indicadas em colunas adicionais no data frame criado "aba_apolice_endosso"
        # e remove as duplicadas e considera apolice indicado no subset
        

        dados_adicionais.rename(
            columns={'cd_apolice': 'N° Apólice', 'nm_tp_apolice': 'Tipo de Apólice', 'nm_tp_cobranca': 'Tipo de Cobrança',
            'nm_regiao_circulacao': 'Região de Circulação', 'nm_auto_utilizacao': 'Utilização', 'dt_ini_vig_apo': 'Inicio Vigência Apólice',
            'dt_fim_vig_apo' : 'Fim Vigência Apólice', 'nm_uf_cliente': 'Estado', 'nm_cidade': 'Cidade', 'nm_estipulante': 'Segurado',
            'nm_produto': 'Produto', 'nm_corretor':'Corretor', 'nm_representante':'Representante','nr_ramo':'Ramo'}, inplace=True)

        # Garante que a coluna é do tipo data
        dados_adicionais['Inicio Vigência Apólice'] = pd.to_datetime(dados_adicionais['Inicio Vigência Apólice'], dayfirst=True)
        # Cria a coluna numérica do ano
        dados_adicionais['Ano Vigência'] = dados_adicionais['Inicio Vigência Apólice'].dt.year

        # Merge dos dados de prêmio com os dados adicionais
        premio_com_dados = pd.merge(
            soma_por_apolice,
            dados_adicionais,
            on='N° Apólice',
            how='left'
        )
        # how='left' (Esquerda): Garante que o que as colunas da tabela que tem dados de apolice e dinheiro (prêmio) nunca suma.
        # Mesmo que os dados adicionais estejam incompletos, a linha da apólice continua lá com o valor somado.


        # Carrega o arquivo sinistro.txt
        df_sinistros_detalhado = carregar_e_processar_dados_sinistro(arquivo_sinistro)

        # Soma dos sinistros por apólice (chama a função que cria os dados de sinistro):
        soma_sinistro_por_apolice = df_sinistros_detalhado.groupby('N° Apólice')['Total Sinistro'].sum().reset_index()
        soma_sinistro_por_apolice.rename(columns={'Total Sinistro': 'Soma Sinistro Por Apolice'}, inplace=True)
        
        # Merge dos resultados finais
        resultado_final = pd.merge(
            premio_com_dados,
            soma_sinistro_por_apolice,
            on='N° Apólice',
            how='outer'
        ).fillna(0) # Preenche valores NaN com 0

        return resultado_final
    
    except Exception as e:
        st.error(f"Erro no processamento geral: {e}")
        return pd.DataFrame()


# Função de Formatação de Valores para o padrão Brasileiro
def formatar_valor_br(valor):
    """
    Formata um valor numérico para o padrão monetário brasileiro (R$ X.XXX,XX).
    Lida com valores NaN retornando uma string vazia.
    """
    if pd.isna(valor):
        return ""
    # Formata como float com 2 casas decimais e separador de milhar (padrão US)
    valor_us_format = f"{valor:,.2f}"
    # Inverte os separadores para o padrão brasileiro
    valor_br_format = valor_us_format.replace(
        ",", "X").replace(".", ",").replace("X", ".")
    return valor_br_format

# --- Aplicação Streamlit ---
# Carrega do session_state se já existir, senão processa os uploads
if dados_ja_carregados:
    dados_calculados = st.session_state['dados_calculados']
    df_sinistros     = st.session_state['df_sinistros']
else:
    # Lê os bytes uma única vez para evitar problema de ponteiro consumido
    bytes_apolice  = upload_apolice.read()  if hasattr(upload_apolice,  'read') else None
    bytes_sinistro = upload_sinistro.read() if hasattr(upload_sinistro, 'read') else None

    fonte_apolice  = io.BytesIO(bytes_apolice)  if bytes_apolice  is not None else upload_apolice
    fonte_sinistro = io.BytesIO(bytes_sinistro) if bytes_sinistro is not None else upload_sinistro

    dados_calculados = carregar_e_processar_dados(fonte_apolice, io.BytesIO(bytes_sinistro) if bytes_sinistro is not None else upload_sinistro)
    if dados_calculados.empty:
        st.stop()
    df_sinistros = carregar_e_processar_dados_sinistro(fonte_sinistro)
    if df_sinistros.empty:
        st.stop()
    # Salva no session_state e força rerun para esconder os uploaders imediatamente
    st.session_state['dados_calculados'] = dados_calculados
    st.session_state['df_sinistros']     = df_sinistros
    st.session_state['data_upload']      = datetime.now().strftime('%d/%m/%Y %H:%M')
    st.rerun()

# Cria uma cópia para exibição e cálculos de porcentagem/formatação
# Converte para object antes de formatar para evitar TypeError no pandas 2.x+
dados_exibicao = dados_calculados.copy()
dados_exibicao['Soma Prêmio Pago por Apolice'] = dados_exibicao['Soma Prêmio Pago por Apolice'].astype(object)
dados_exibicao['Soma Sinistro Por Apolice']     = dados_exibicao['Soma Sinistro Por Apolice'].astype(object)

# Cria o percentual de sinistro, tratando divisão por zero
dados_exibicao['% Sin'] = dados_exibicao.apply(
    lambda row: '{:.2%}'.format(
        row['Soma Sinistro Por Apolice'] / row['Soma Prêmio Pago por Apolice'])
    if row['Soma Prêmio Pago por Apolice'] != 0 else '0.00%', axis=1
)

# Formata as colunas para exibição
dados_exibicao['Soma Prêmio Pago por Apolice'] = dados_exibicao['Soma Prêmio Pago por Apolice'].map(formatar_valor_br)
dados_exibicao['Soma Sinistro Por Apolice']     = dados_exibicao['Soma Sinistro Por Apolice'].map(formatar_valor_br)

# Reordenar as colunas para que 'Soma Sinistro Por Apolice' e '% Sin' fiquem nas posições desejadas
colunas = list(dados_exibicao.columns)

# Remove as colunas que vamos inserir manualmente, se existirem
for col in ['Soma Sinistro Por Apolice', '% Sin']:
    if col in colunas:
        colunas.remove(col)

# Insere nas posições desejadas
colunas.insert(2, 'Soma Sinistro Por Apolice')
colunas.insert(3, '% Sin')

# Reordena o DataFrame
dados_exibicao = dados_exibicao[colunas]

# Ordenando por numero da apólice inicialmente
dados_exibicao = dados_exibicao.sort_values('N° Apólice')


# copia do DF da base de sinistro para utilizar
df_sinistro_utilizar = df_sinistros.copy()


# '''
# imagem sidebar
#
#
#
#
#
#
# '''


def img_to_base64(image_path):
    """Convert image to base64."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        logging.error(f"Error converting image to base64: {str(e)}")
        return None


# Load and display sidebar image
img_path = r'C:\Users\alex.sousa\Documents\Dados_Sinistros\image\lexus_gemine_II-Photoroom_menor80.png'
img_base64 = img_to_base64(img_path)
if img_base64:
    st.sidebar.markdown(
        # essa função para colocar glowing effect na imagem
        # f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
        f'<img src="data:image/png;base64,{img_base64}" style="width: 100px; height: auto; display: block; margin-left: auto; margin-right: auto; margin-top: -40px;margin-bottom: 5px">',
        unsafe_allow_html=True,
    )

# '''
# imagem sidebar
#
#
#
#
#
#
# '''


# '''
# para baixo trabalho filtro apólice
#
#
#
#
#
#
# '''


# ── PÁGINA 1: APÓLICE / SEGURADO ────────────────────────────────────────────

# --- Filtragem dados da Apólice ---
st.sidebar.header('Filtro Apólice')

# Filtro por Apólice - Obtém as apólices únicas
apolices_filtro_apolice = sorted(dados_exibicao['N° Apólice'].unique())

# Define o índice padrão para selectbox
default_index_apolice = 0 if apolices_filtro_apolice else None

apolices_selecionadas_filtro_apolice = st.sidebar.selectbox(
    'Apólice',
    options=apolices_filtro_apolice,
    index=default_index_apolice  # Selecionar o primeiro registro por padrão
)

# Link para a página de Dados Gerais na sidebar
st.sidebar.markdown("---")
st.sidebar.header('Dados Gerais')
st.sidebar.page_link("pages/2_Dados_Gerais.py", label="📊  Dados Gerais")

st.subheader(f'Dados Apólice - {apolices_selecionadas_filtro_apolice}')
dados_filtrados_filtro_apolice = dados_exibicao.copy()
if apolices_selecionadas_filtro_apolice:
    dados_filtrados_filtro_apolice = dados_filtrados_filtro_apolice[
        dados_filtrados_filtro_apolice['N° Apólice'] == apolices_selecionadas_filtro_apolice]

# Converte as colunas de volta para numérico para somar
# É importante fazer isso em uma cópia para não afetar a exibição formatada
df_para_filtro_apolice = dados_filtrados_filtro_apolice.copy()
df_para_filtro_apolice['Soma Prêmio Pago por Apolice'] = df_para_filtro_apolice['Soma Prêmio Pago por Apolice'].str.replace(
    '.', '').str.replace(',', '.').astype(float)
df_para_filtro_apolice['Soma Sinistro Por Apolice'] = df_para_filtro_apolice['Soma Sinistro Por Apolice'].str.replace(
    '.', '').str.replace(',', '.').astype(float)

total_premio_filtro_apolice = df_para_filtro_apolice['Soma Prêmio Pago por Apolice'].sum(
)
total_sinistro_filtro_apolice = df_para_filtro_apolice['Soma Sinistro Por Apolice'].sum(
)

# Calcula o percentual de sinistro total
percentual_sinistro_total_filtro_apolice = (
    total_sinistro_filtro_apolice / total_premio_filtro_apolice) if total_premio_filtro_apolice != 0 else 0

# criação do de DF com dados de sinistro de apólice selecionada.
df_sinistro_apolice = df_sinistro_utilizar.loc[df_sinistro_utilizar['N° Apólice'] == apolices_selecionadas_filtro_apolice]

# Quantidade de sinistros por apólice
qtd_sinistros_apólice = df_sinistro_apolice['nr_sinistro'].nunique()

# Df para apresentação de sinistro por cobertura NA APOLICE
if df_sinistro_apolice.empty:
    df_sinistro_apolice_cobertura = pd.DataFrame({
        'Cobertura' : [''],
        'Total Sinistro' : [''],
        'Qtd Sinistro' : ['']
    })
else:
    df_sinistro_apolice_cobertura = df_sinistro_apolice.groupby('Cobertura', as_index=False).agg(**{
        'Total Sinistro': ('Total Sinistro', 'sum'),
        'Qtd Sinistros': ('nr_sinistro', 'nunique')
    })
    df_sinistro_apolice_cobertura['Total Sinistro'] = (df_sinistro_apolice_cobertura['Total Sinistro'].map(formatar_valor_br))

# Tipo de Emissão da apólice selecionada
tipo_emissao_apolice = list(dados_filtrados_filtro_apolice['Tipo de Apólice'].unique())
tipo_emissao_valor = str(tipo_emissao_apolice[0]).title() if tipo_emissao_apolice else "—"

col_apl_1, col_apl_2, col_apl_3, col_apl_4, col_apl_5 = st.columns(5)

with col_apl_1:
    st.metric(label="Total Prêmio Pago",
              value=f"R$ {formatar_valor_br(total_premio_filtro_apolice)}")
with col_apl_2:
    st.metric(label="Total Sinistro",
              value=f"R$ {formatar_valor_br(total_sinistro_filtro_apolice)}")
with col_apl_3:
    st.metric(label="% Sinistro Total",
              value=f"{percentual_sinistro_total_filtro_apolice:.2%}")
with col_apl_4:
    st.metric(label='Qtd Sinistro', value=qtd_sinistros_apólice)
with col_apl_5:
    st.metric(label='Tipo de Emissão', value=tipo_emissao_valor)


# st.subheader('Segurado: ')
# st.caption('Segurado: ')
# st.write('Segurado: ')
# st.text('Segurado: ')
# st.markdown("**Segurado:**")

col_seg_1, col_cor_2, col_rep_3, col_util_4 = st.columns(4)

segurado = list(dados_filtrados_filtro_apolice['Segurado'].unique())
corretor = list(dados_filtrados_filtro_apolice['Corretor'].unique())
representante = list(
    dados_filtrados_filtro_apolice['Representante'].unique())
utilização = list(
    dados_filtrados_filtro_apolice['Utilização'].unique())


with col_seg_1:
    st.markdown("<p style='margin-bottom: 0;'>Segurado</p>",
                unsafe_allow_html=True)
    st.markdown(
        f"<h6 style='margin-top: 0; margin-bottom: 0.2rem;'>{str(segurado[0]).title()}</h6>", unsafe_allow_html=True)
with col_cor_2:
    st.markdown("<p style='margin-bottom: 0;'>Corretor</p>",
                unsafe_allow_html=True)
    st.markdown(
        f"<h6 style='margin-top: 0; margin-bottom: 0.2rem;'>{str(corretor[0]).title()}</h6>", unsafe_allow_html=True)
with col_rep_3:
    st.markdown("<p style='margin-bottom: 0;'>Representante</p>",
                unsafe_allow_html=True)
    st.markdown(
        f"<h6 style='margin-top: 0; margin-bottom: 0.2rem;'>{str(representante[0]).title()}</h6>", unsafe_allow_html=True)
with col_util_4:
    st.markdown("<p style='margin-bottom: 0;'>Utilização</p>",
                unsafe_allow_html=True)
    st.markdown(
        f"<h6 style='margin-top: 0; margin-bottom: 0.2rem;'>{str(utilização[0]).title()}</h6>", unsafe_allow_html=True)

st.text("Dados da Apólice")
st.dataframe(dados_filtrados_filtro_apolice, hide_index=True)

col_cob_sin_1, col_cob_sin_2 = st.columns(2)

# Formatar como numero as colunas do df de dados da apólice
df_sinistro_apolice['vl_sinistro_pago'] = (df_sinistro_apolice['vl_sinistro_pago'].map(formatar_valor_br))
df_sinistro_apolice['vl_sinistro_pendente'] = (df_sinistro_apolice['vl_sinistro_pendente'].map(formatar_valor_br))
df_sinistro_apolice['vl_sinistro_total'] = (df_sinistro_apolice['vl_sinistro_total'].map(formatar_valor_br))
df_sinistro_apolice['vl_despesa_pago'] = (df_sinistro_apolice['vl_despesa_pago'].map(formatar_valor_br))
df_sinistro_apolice['vl_despesa_pendente'] = (df_sinistro_apolice['vl_despesa_pendente'].map(formatar_valor_br))
df_sinistro_apolice['vl_despesa_total'] = (df_sinistro_apolice['vl_despesa_total'].map(formatar_valor_br))
df_sinistro_apolice['vl_honorario_pago'] = (df_sinistro_apolice['vl_honorario_pago'].map(formatar_valor_br))
df_sinistro_apolice['vl_honorario_pendente'] = (df_sinistro_apolice['vl_honorario_pendente'].map(formatar_valor_br))
df_sinistro_apolice['vl_honorario_total'] = (df_sinistro_apolice['vl_honorario_total'].map(formatar_valor_br))
df_sinistro_apolice['vl_salvado_pago'] = (df_sinistro_apolice['vl_salvado_pago'].map(formatar_valor_br))
df_sinistro_apolice['vl_salvado_pendente'] = (df_sinistro_apolice['vl_salvado_pendente'].map(formatar_valor_br))
df_sinistro_apolice['vl_salvado_total'] = (df_sinistro_apolice['vl_salvado_total'].map(formatar_valor_br))
df_sinistro_apolice['Total Sinistro'] = (df_sinistro_apolice['Total Sinistro'].map(formatar_valor_br))

with col_cob_sin_1:
    st.text("Dados de Sinistro")
    if not df_sinistro_apolice.empty:
        st.dataframe(df_sinistro_apolice, hide_index=True)
    else:
        st.info("Apólice não possui sinistro.")


with col_cob_sin_2:
    st.text("Sinistro Por Cobertura")
    if not df_sinistro_apolice_cobertura.empty:
        st.dataframe(df_sinistro_apolice_cobertura, hide_index=True)
    else:
        st.info("Apólice não possui sinistro.")

#
#
#
#
# DADOS DO SEGURADO PARA APRESENTAÇÃO
#
#
#
#

st.subheader(f'Dados do Segurado - {str(segurado[0]).title()}')

# 1. Preparação dos Dados do Segurado (Numéricos para cálculos)
# df_segurado_calculo = dados_calculados[dados_calculados['Segurado'] == segurado[0]].copy()
# df_sinistro_segurado = df_sinistros[df_sinistros['nm_cliente'] == segurado[0]].copy()


# 1. Preparação dos Dados do Segurado (Filtro inicial numérico)
df_segurado_calculo = dados_calculados[dados_calculados['Segurado'] == segurado[0]].copy()
df_sinistro_segurado = df_sinistros[df_sinistros['nm_cliente'] == segurado[0]].copy()

# 2. Criar a coluna de percentual de sinistro (MANTENDO COMO NÚMERO para cálculos)
df_segurado_calculo['% Sin'] = df_segurado_calculo.apply(
    lambda row: row['Soma Sinistro Por Apolice'] / row['Soma Prêmio Pago por Apolice'] 
    if row['Soma Prêmio Pago por Apolice'] != 0 else 0, axis=1
)

# --- AQUI ESTÁ O PULO DO GATO: Cálculos de Totais ---
# Fazemos os cálculos usando o DF que ainda tem NÚMEROS (antes da formatação de R$)
total_pr_segurado = df_segurado_calculo['Soma Prêmio Pago por Apolice'].sum()
total_sinistro_segurado = df_segurado_calculo['Soma Sinistro Por Apolice'].sum()
sinistralidade_segurado = (total_sinistro_segurado / total_pr_segurado) if total_pr_segurado != 0 else 0

# 3. Criar uma CÓPIA para exibição e aplicar a formatação visual
df_segurado_exibicao = df_segurado_calculo.copy()

df_segurado_exibicao['Soma Prêmio Pago por Apolice'] = df_segurado_exibicao['Soma Prêmio Pago por Apolice'].map(formatar_valor_br)
df_segurado_exibicao['Soma Sinistro Por Apolice'] = df_segurado_exibicao['Soma Sinistro Por Apolice'].map(formatar_valor_br)
df_segurado_exibicao['% Sin'] = df_segurado_exibicao['% Sin'].map(lambda x: '{:.2%}'.format(x))

# 4. Reordenar as colunas para seguir a sequência exata de 'dados_exibicao' (df_geral_periodo)
colunas_referencia = [
    'N° Apólice', 'Soma Prêmio Pago por Apolice', 'Soma Sinistro Por Apolice', '% Sin',
    'Segurado', 'Inicio Vigência Apólice', 'Fim Vigência Apólice', 'Utilização',
    'Corretor', 'Representante', 'Ramo', 'Tipo de Apólice', 'Tipo de Cobrança',
    'Região de Circulação', 'Estado', 'Cidade', 'Produto', 'Ano Vigência'
]
# Filtra apenas as colunas que existem no df (evita erro se alguma coluna estiver ausente)
colunas_referencia = [c for c in colunas_referencia if c in df_segurado_exibicao.columns]
df_segurado_exibicao = df_segurado_exibicao[colunas_referencia]

# KPIs do Segurado
total_pr_segurado = df_segurado_calculo['Soma Prêmio Pago por Apolice'].sum()
total_sinistro_segurado = df_segurado_calculo['Soma Sinistro Por Apolice'].sum()
sinistralidade_segurado = (total_sinistro_segurado / total_pr_segurado) if total_pr_segurado != 0 else 0
qtd_apolice_segurado = df_segurado_calculo['N° Apólice'].nunique()
qtd_sinistros_segurado = df_sinistro_segurado['nr_sinistro'].nunique()

seg_apl_1, seg_apl_2, seg_apl_3, seg_apl_4, seg_apl_5 = st.columns(5)
with seg_apl_1:
    st.metric(label="Total Prêmio Pago", value=f"R$ {formatar_valor_br(total_pr_segurado)}")
with seg_apl_2:
    st.metric(label="Total Sinistro", value=f"R$ {formatar_valor_br(total_sinistro_segurado)}")
with seg_apl_3:
    st.metric(label="% Sinistro Total", value=f"{sinistralidade_segurado:.2%}")
with seg_apl_4:
    st.metric(label='Qtd. Apolices', value=qtd_apolice_segurado)
with seg_apl_5:
    st.metric(label='Qtd Sinistros', value=qtd_sinistros_segurado)

# --- NOVO: Prêmio x Sinistro / Desempenho Consolidado por Ano ---
col_graf_seg_1, col_graf_seg_2 = st.columns(2)

with col_graf_seg_1:
    # --- GRÁFICO CORRIGIDO: EVOLUÇÃO POR ANO DO SEGURADO ---
    st.subheader(f"Evolução Anual - Segurado")

    # 1. Preparar os dados (utilizando a coluna 'Ano Vigência' já existente)
    df_evolucao_segurado = df_segurado_calculo.copy()

    # 2. Agrupar por Ano Vigência
    df_anual_seg = df_evolucao_segurado.groupby('Ano Vigência').agg({
        'Soma Prêmio Pago por Apolice': 'sum',
        'Soma Sinistro Por Apolice': 'sum'
    }).reset_index()

    # 3. Garantir ordenação e tipo string para o eixo X
    df_anual_seg = df_anual_seg.sort_values('Ano Vigência')
    df_anual_seg['Ano'] = df_anual_seg['Ano Vigência'].astype(str)

    # 4. Criar o gráfico seguindo o estilo do fig_evolucao (Linhas com Marcadores)
    fig_evolucao_seg = go.Figure()

    fig_evolucao_seg.add_trace(go.Scatter(
        x=df_anual_seg['Ano'], 
        y=df_anual_seg['Soma Prêmio Pago por Apolice'],
        mode='lines+markers', 
        name='Prêmio Líquido', 
        line=dict(color='#36A2EB', width=3)
    ))

    fig_evolucao_seg.add_trace(go.Scatter(
        x=df_anual_seg['Ano'], 
        y=df_anual_seg['Soma Sinistro Por Apolice'],
        mode='lines+markers', 
        name='Sinistro', 
        line=dict(color='red', width=3)
    ))

    fig_evolucao_seg.update_layout(
        xaxis_title='Ano',
        yaxis_title='Valor (R$)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=60, b=20),
        hovermode="x unified"
    )

    st.plotly_chart(fig_evolucao_seg, use_container_width=True, config={'displayModeBar': False})

with col_graf_seg_2:
    st.subheader("Prêmio x Sinistro - Segurado")
    
    # Agrupamento por Ano para o Segurado
    df_ano_seg = df_segurado_calculo.groupby('Ano Vigência').agg({
        'Soma Prêmio Pago por Apolice': 'sum',
        'Soma Sinistro Por Apolice': 'sum'
    }).reset_index()
    
    # Garantir que o Ano seja string para o eixo Y
    df_ano_seg['Ano Vigência'] = df_ano_seg['Ano Vigência'].astype(str)

    fig_barras_h_seg = go.Figure()

    # Barra de Prêmios (Horizontal)
    fig_barras_h_seg.add_trace(go.Bar(
        y=df_ano_seg['Ano Vigência'], 
        x=df_ano_seg['Soma Prêmio Pago por Apolice'],
        name='Total Prêmio',
        orientation='h',
        marker_color='#36A2EB',
        text=df_ano_seg['Soma Prêmio Pago por Apolice'].apply(formatar_valor_br),
        textposition='auto'
    ))

    # Barra de Sinistros (Horizontal)
    fig_barras_h_seg.add_trace(go.Bar(
        y=df_ano_seg['Ano Vigência'],
        x=df_ano_seg['Soma Sinistro Por Apolice'],
        name='Total Sinistro',
        orientation='h',
        marker_color='red',
        text=df_ano_seg['Soma Sinistro Por Apolice'].apply(formatar_valor_br),
        textposition='auto'
    ))

    fig_barras_h_seg.update_layout(
        barmode='group',
        xaxis_title="Valores (R$)",
        yaxis_title="Ano",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=30, b=0),
        height=400 
    )

    st.plotly_chart(fig_barras_h_seg, use_container_width=True, config={'displayModeBar': False})


col_graf_seg_3, col_graf_seg_4 = st.columns(2)

with col_graf_seg_3:
    # --- TABELA: DESEMPENHO CONSOLIDADO POR ANO (SEGURADO) ---
    # 1. Agrupamento dos dados por Ano de Vigência
    df_consolidado_ano_seg = df_segurado_calculo.groupby('Ano Vigência').agg({
        'Soma Prêmio Pago por Apolice': 'sum',
        'Soma Sinistro Por Apolice': 'sum'
    }).reset_index()

    # 2. Cálculos de Sinistralidade
    df_consolidado_ano_seg['% Sinistralidade'] = df_consolidado_ano_seg.apply(
        lambda row: row['Soma Sinistro Por Apolice'] / row['Soma Prêmio Pago por Apolice'] 
        if row['Soma Prêmio Pago por Apolice'] != 0 else 0, axis=1
    )

    # 3. Criação de um DF para exibição com formatação brasileira
    df_consolidado_view = df_consolidado_ano_seg.copy()

    # Aplicando as formatações
    df_consolidado_view['Soma Prêmio Pago por Apolice'] = df_consolidado_view['Soma Prêmio Pago por Apolice'].map(formatar_valor_br)
    df_consolidado_view['Soma Sinistro Por Apolice'] = df_consolidado_view['Soma Sinistro Por Apolice'].map(formatar_valor_br)
    df_consolidado_view['% Sinistralidade'] = df_consolidado_view['% Sinistralidade'].map(lambda x: f"{x:.2%}")

    # Ajuste de nomes de colunas para a visualização
    df_consolidado_view.rename(columns={
        'Ano Vigência': 'Ano',
        'Soma Prêmio Pago por Apolice': 'Total Prêmio',
        'Soma Sinistro Por Apolice': 'Total Sinistro'
    }, inplace=True)
  
    st.subheader(f"Desempenho Consolidado por Ano - Segurado")
    # 4. Exibição da Tabela
    st.dataframe(df_consolidado_view, hide_index=True, use_container_width=True)

with col_graf_seg_4:
    st.subheader("Evolução da Sinistralidade (%)  - Segurado")
    
    # Cálculo da Sinistralidade por Ano
    df_ano_seg['% Sin'] = (df_ano_seg['Soma Sinistro Por Apolice'] / df_ano_seg['Soma Prêmio Pago por Apolice']).fillna(0)
    
    # Gráfico de Linha (Evolução)
    fig_line_sin_seg = px.line(
        df_ano_seg, 
        x='Ano Vigência', 
        y='% Sin', 
        markers=True,
        text=df_ano_seg['% Sin'].map(lambda x: f"{x:.2%}")
    )
    
    fig_line_sin_seg.update_traces(textposition="top center", line_color='red')
    fig_line_sin_seg.update_yaxes(tickformat=".1%")
    fig_line_sin_seg.update_layout(
        height=400, 
        margin=dict(t=30, b=20, l=0, r=0),
        xaxis_title="Ano",
        yaxis_title="Sinistralidade (%)"
    )
    st.plotly_chart(fig_line_sin_seg, use_container_width=True, config={'displayModeBar': False})


# --- Prêmio e Sinistro por Utilização ---
col_util_1, col_util_2 = st.columns(2)

with col_util_1:
    st.text("Desempenho por Utilização - Segurado")
    df_util_seg = df_segurado_calculo.groupby('Utilização').agg({
        'Soma Prêmio Pago por Apolice': 'sum',
        'Soma Sinistro Por Apolice': 'sum'
    }).reset_index()
    
    # Tabela formatada
    df_util_view = df_util_seg.copy()
    df_util_view['Sinistralidade'] = (df_util_view['Soma Sinistro Por Apolice'] / df_util_view['Soma Prêmio Pago por Apolice']).map(lambda x: f"{x:.2%}")
    df_util_view['Soma Prêmio Pago por Apolice'] = df_util_view['Soma Prêmio Pago por Apolice'].map(formatar_valor_br)
    df_util_view['Soma Sinistro Por Apolice'] = df_util_view['Soma Sinistro Por Apolice'].map(formatar_valor_br)
    st.dataframe(df_util_view, hide_index=True, use_container_width=True)

with col_util_2:
    st.subheader("Sinistralidade por Utilização - Segurado")

    # 1. Criamos o DF auxiliar para o gráfico a partir do df_util_seg já agrupado
    df_grafico_util_seg = df_util_seg.copy()

    # 2. Cálculo da sinistralidade como float para o gráfico
    df_grafico_util_seg['Sinistralidade_Float'] = df_grafico_util_seg.apply(
        lambda row: row['Soma Sinistro Por Apolice'] / row['Soma Prêmio Pago por Apolice']
        if row['Soma Prêmio Pago por Apolice'] != 0 else 0, axis=1
    )

    # 3. Colunas de texto formatado para exibir no rótulo
    df_grafico_util_seg['% Sinistralidade'] = df_grafico_util_seg['Sinistralidade_Float'].map(lambda x: f"{x:.2%}")

    # 4. FILTRO: Remove utilização "0" e valores zerados para limpar o visual
    df_grafico_util_seg = df_grafico_util_seg[
        (df_grafico_util_seg['Utilização'].astype(str) != '0') &
        (df_grafico_util_seg['Sinistralidade_Float'] > 0)
    ]

    if not df_grafico_util_seg.empty:
        # 5. Ordena para que a maior sinistralidade fique no topo do gráfico horizontal
        df_grafico_util_seg = df_grafico_util_seg.sort_values(by='Sinistralidade_Float', ascending=True)

        # 6. Criação do gráfico de barras horizontais (idêntico ao fig_util_sin dos Dados Gerais)
        fig_util_seg = px.bar(
            df_grafico_util_seg,
            x='Sinistralidade_Float',
            y='Utilização',
            orientation='h',
            text='% Sinistralidade',
            labels={'Sinistralidade_Float': 'Sinistralidade (%)'},
            color='Sinistralidade_Float',
            color_continuous_scale='Reds',
        )

        fig_util_seg.update_traces(
            textposition='outside',
            hovertemplate="Utilização: %{y}<br>Sinistralidade: %{text}"
        )

        fig_util_seg.update_layout(
            xaxis_title="Sinistralidade (%)",
            yaxis_title="",
            coloraxis_showscale=False,
            margin=dict(l=0, r=50, t=30, b=0),
            height=max(300, len(df_grafico_util_seg) * 40)
        )

        st.plotly_chart(fig_util_seg, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("Sem dados de Sinistro.")


# 1. Agrupamento de prêmios, sinistros e contagem de apólices únicas
groupby_segurado_ramo = df_segurado_calculo.groupby('Ramo').agg(
    Total_Premio=('Soma Prêmio Pago por Apolice', 'sum'),
    Total_Sinistro=('Soma Sinistro Por Apolice', 'sum'),
    Qtd_Apolices=('N° Apólice', 'nunique')
).reset_index()

# 2. Busca a quantidade de sinistros por ramo (cruzando com a base de sinistros do segurado)
qtd_sin_por_ramo = df_sinistro_segurado.groupby('nr_ramo')['nr_sinistro'].nunique().reset_index()
qtd_sin_por_ramo.rename(columns={'nr_ramo': 'Ramo', 'nr_sinistro': 'Qtd_Sinistros'}, inplace=True)

# 3. Une as informações
groupby_segurado_ramo = pd.merge(groupby_segurado_ramo, qtd_sin_por_ramo, on='Ramo', how='left').fillna(0)

# 4. Cálculo da Sinistralidade
groupby_segurado_ramo['Sinistralidade'] = groupby_segurado_ramo.apply(
    lambda row: row['Total_Sinistro'] / row['Total_Premio'] if row['Total_Premio'] != 0 else 0, axis=1
)

# 5. Criar DataFrame de exibição com as formatações solicitadas
df_ramo_segurado_view = groupby_segurado_ramo.copy()
df_ramo_segurado_view['Total_Premio'] = df_ramo_segurado_view['Total_Premio'].map(formatar_valor_br)
df_ramo_segurado_view['Total_Sinistro'] = df_ramo_segurado_view['Total_Sinistro'].map(formatar_valor_br)
df_ramo_segurado_view['Sinistralidade'] = df_ramo_segurado_view['Sinistralidade'].map(lambda x: f"{x:.2%}")
df_ramo_segurado_view['Qtd_Sinistros'] = df_ramo_segurado_view['Qtd_Sinistros'].astype(int)

# Reordenar colunas para a tabela
colunas_view = ['Ramo', 'Qtd_Apolices', 'Qtd_Sinistros', 'Total_Premio', 'Total_Sinistro', 'Sinistralidade']
df_ramo_segurado_view = df_ramo_segurado_view[colunas_view]



# Defina a largura das barras e a posição (offset) para que fiquem coladas
bar_width = 0.45
offset_premio = -bar_width / 2
offset_sinistro = bar_width / 2

fig = go.Figure(data=[
    go.Bar(
        name='Total Prêmio',
        x=groupby_segurado_ramo['Ramo'],
        y=groupby_segurado_ramo['Total_Premio'],
        marker_color='rgba(54, 162, 235, 0.8)',
        width=bar_width,
        offset=offset_premio,  # Desloca a barra para a esquerda
        
        # === Adicione estas linhas para o rótulo da barra de Prêmio ===
        text=groupby_segurado_ramo['Total_Premio'].map(formatar_valor_br),
        textposition='outside',
        textfont=dict(
            color='black',
            size=12
        )
    ),
    go.Bar(
        name='Total Sinistro',
        x=groupby_segurado_ramo['Ramo'],
        y=groupby_segurado_ramo['Total_Sinistro'],
        marker_color='red',
        width=bar_width,
        offset=offset_sinistro, # Desloca a barra para a direita
        # === Adicione estas linhas para o rótulo da barra de Sinistro ===
        text=groupby_segurado_ramo['Total_Sinistro'].map(formatar_valor_br),
        textposition='outside',
        textfont=dict(
            color='black',
            size=12
        )
    )
])

fig.update_layout(
    xaxis=dict(
        title='Ramo',
        type='category', # <--- Adicione esta linha!
        tickmode='array', # <--- Adicione esta linha!
        tickvals=groupby_segurado_ramo['Ramo'] # <--- Adicione esta linha!
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

# dados de sinistro por cobertura NO SEGURADO
if df_sinistro_segurado.empty:
    df_sinistro_segurado_cobertura = pd.DataFrame({
        'Cobertura' : [''],
        'Total Sinistro' : [''],
        'Qtd Sinistro' : ['']
    })
else:
    df_sinistro_segurado_cobertura = df_sinistro_segurado.groupby('Cobertura', as_index=False).agg(**{
        'Total Sinistro': ('Total Sinistro', 'sum'),
        'Qtd Sinistros': ('nr_sinistro', 'nunique')
    })
    df_sinistro_segurado_cobertura['Total Sinistro'] = (df_sinistro_segurado_cobertura['Total Sinistro'].map(formatar_valor_br))


# GRÁFICO DE PIZZA - SINISTRO POR COBERTURA
# Garanta que a coluna 'Total Sinistro' seja numérica para o gráfico
df_para_grafico = df_sinistro_segurado_cobertura.copy()
# Apenas converta se não for string vazia
df_para_grafico = df_para_grafico[df_para_grafico['Total Sinistro'] != '']
df_para_grafico['Total Sinistro'] = df_para_grafico['Total Sinistro'].str.replace(
    '.', '').str.replace(',', '.').astype(float)
    
# gráfico de pizza
fig_pizza = None # Inicializa a variável do gráfico

# Verifique se o DataFrame não está vazio antes de criar o gráfico
if not df_para_grafico.empty:
    fig_pizza = px.pie(
        df_para_grafico,
        values='Total Sinistro',
        names='Cobertura',
        # title='Distribuição de Sinistro por Cobertura',
        hole=0.4, # Cria um gráfico de rosca
        height=400
    )
    
    # Atualiza o layout para melhorar a aparência
    fig_pizza.update_traces(textposition='outside', textinfo='percent+value')
    fig_pizza.update_layout(showlegend=True) # Exibe a legenda


dados_chart_1, dados_chart_2 = st.columns(2)

with dados_chart_1:
    st.text("Sinistro por Ramo")
    # Exibe a tabela formatada (com Qtd Apolices, Qtd Sinistros e % Sinistralidade)
    st.dataframe(df_ramo_segurado_view, hide_index=True, use_container_width=True) 

with dados_chart_2:
    st.text("Sinistros por Cobertura")
    # Exibe a tabela de coberturas que você criou anteriormente (df_sinistro_segurado_cobertura)
    st.dataframe(df_sinistro_segurado_cobertura, hide_index=True, use_container_width=True)

seg_chart_1, seg_chart_2 = st.columns(2)

with seg_chart_1:
    st.text("Gráfico Sinistro Por Ramo")
    if fig:
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info('Segurado sem Sinistro')
with seg_chart_2:
    st.text("Gráfico Sinistro Por Cobertura")
    if fig_pizza: # Verifica se o gráfico foi criado antes de exibi-lo
        st.plotly_chart(fig_pizza, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("Segurado sem Sinistro")

# Lista dos ramos que desejamos detalhar
ramos_detalhar = [23, 28, 82]

# Verificar quantos ramos possuem dados antes de plotar
ramos_ativos = []

for r in ramos_detalhar:
    # Filtra temporariamente para ver se há dados
    if not df_sinistro_segurado[df_sinistro_segurado['nr_ramo'] == r].empty:
        ramos_ativos.append(r)

# Condição: Só apresenta se existir no mínimo 2 ramos com sinistro (conforme seu pedido)
if len(ramos_ativos) >= 2:
    
    for ramo in ramos_ativos:
        # 1. Filtra os dados (já sabemos que não está vazio por causa da verificação acima)
        df_sinistro_ramo = df_sinistro_segurado[df_sinistro_segurado['nr_ramo'] == ramo].copy()
        
        # 2. Agrupamento por Cobertura
        df_cobertura_ramo = df_sinistro_ramo.groupby('Cobertura', as_index=False).agg(**{
            'Total Sinistro': ('Total Sinistro', 'sum'),
            'Qtd Sinistros': ('nr_sinistro', 'nunique')
        })
        
        # 3. Preparação do Gráfico (Removendo zeros)
        df_pizza_ramo = df_cobertura_ramo[df_cobertura_ramo['Total Sinistro'] > 0].copy()
        
        # 4. Formatação para exibição na tabela
        df_cobertura_ramo_exibicao = df_cobertura_ramo.copy()
        df_cobertura_ramo_exibicao['Total Sinistro'] = df_cobertura_ramo_exibicao['Total Sinistro'].map(formatar_valor_br)
        
        # 5. Layout e Plotagem
        # st.markdown(f"---") # Linha separadora entre ramos
        col_ramo_tab, col_ramo_chart = st.columns(2)
        
        with col_ramo_tab:
            st.text(f"Dados de Sinistro por Cobertura - Ramo {ramo}")
            st.dataframe(df_cobertura_ramo_exibicao, hide_index=True, use_container_width=True)
            
        with col_ramo_chart:
            st.text(f"Gráfico Sinistro Por Cobertura - Ramo {ramo}")
            if not df_pizza_ramo.empty:
                fig_ramo = px.pie(
                    df_pizza_ramo,
                    values='Total Sinistro',
                    names='Cobertura',
                    hole=0.4,
                    height=300 # tamanho do grafico pizza
                )
                fig_ramo.update_traces(textposition='outside', textinfo='percent+value')
                fig_ramo.update_layout(
                    margin=dict(t=20, b=20, l=0, r=0),
                    annotations=[dict(text=f'{ramo}', x=0.5, y=0.5, font_size=15, showarrow=False)] # texto de dentro do grafico piza o numero do ramo
                )
                st.plotly_chart(fig_ramo, use_container_width=True, config={'displayModeBar': False})

#
#
#
#
# DADOS DO SEGURADO PARA APRESENTAÇÃO
#
#
#
#

#
#
#
#
# DADOS DE SINISTRO
#
#
#
#

df_segurado_calculo['Soma Prêmio Pago por Apolice'] = (df_segurado_calculo['Soma Prêmio Pago por Apolice'].map(formatar_valor_br))
df_segurado_calculo['Soma Sinistro Por Apolice'] = (df_segurado_calculo['Soma Sinistro Por Apolice'].map(formatar_valor_br))

# Formatar como numero as colunas do df de dados da apólice
df_sinistro_segurado['vl_sinistro_pago'] = (df_sinistro_segurado['vl_sinistro_pago'].map(formatar_valor_br))
df_sinistro_segurado['vl_sinistro_pendente'] = (df_sinistro_segurado['vl_sinistro_pendente'].map(formatar_valor_br))
df_sinistro_segurado['vl_sinistro_total'] = (df_sinistro_segurado['vl_sinistro_total'].map(formatar_valor_br))
df_sinistro_segurado['vl_despesa_pago'] = (df_sinistro_segurado['vl_despesa_pago'].map(formatar_valor_br))
df_sinistro_segurado['vl_despesa_pendente'] = (df_sinistro_segurado['vl_despesa_pendente'].map(formatar_valor_br))
df_sinistro_segurado['vl_despesa_total'] = (df_sinistro_segurado['vl_despesa_total'].map(formatar_valor_br))
df_sinistro_segurado['vl_honorario_pago'] = (df_sinistro_segurado['vl_honorario_pago'].map(formatar_valor_br))
df_sinistro_segurado['vl_honorario_pendente'] = (df_sinistro_segurado['vl_honorario_pendente'].map(formatar_valor_br))
df_sinistro_segurado['vl_honorario_total'] = (df_sinistro_segurado['vl_honorario_total'].map(formatar_valor_br))
df_sinistro_segurado['vl_salvado_pago'] = (df_sinistro_segurado['vl_salvado_pago'].map(formatar_valor_br))
df_sinistro_segurado['vl_salvado_pendente'] = (df_sinistro_segurado['vl_salvado_pendente'].map(formatar_valor_br))
df_sinistro_segurado['vl_salvado_total'] = (df_sinistro_segurado['vl_salvado_total'].map(formatar_valor_br))
df_sinistro_segurado['Total Sinistro'] = (df_sinistro_segurado['Total Sinistro'].map(formatar_valor_br))


df_apolices_segurado_1, df_sinistro_segurado_2 = st.columns(2)

with df_apolices_segurado_1:
    # st.text('Dados das Apólices')
    # st.dataframe(df_segurado_calculo, hide_index=True)
    st.text("Dados das Apólices do Segurado")
    st.dataframe(df_segurado_exibicao, hide_index=True)
with df_sinistro_segurado_2:
    st.text("Dados de Sinistro")
    st.dataframe(df_sinistro_segurado, hide_index=True)

# --- Desempenho por Tipo de Emissão — Segurado ---
st.text("Desempenho por Tipo de Emissão - Segurado")

# Usa df_segurado_calculo (ainda numérico — a formatação ocorreu em df_segurado_exibicao)
# Precisamos de uma cópia numérica antes das formatações de display
df_seg_tp_emissao = dados_calculados[dados_calculados['Segurado'] == segurado[0]].copy()

# Agrupamento por Tipo de Apólice
df_tp_emissao_seg = df_seg_tp_emissao.groupby('Tipo de Apólice').agg(
    Qtd_Apolices=('N° Apólice', 'nunique'),
    Total_Premio=('Soma Prêmio Pago por Apolice', 'sum'),
    Total_Sinistro=('Soma Sinistro Por Apolice', 'sum')
).reset_index()

# Cruzamento com sinistros para obter Qtd_Sinistros
df_sin_seg_tp = df_sinistros[df_sinistros['nm_cliente'] == segurado[0]].copy()
qtd_sin_tp_seg = df_seg_tp_emissao.merge(
    df_sin_seg_tp[['N° Apólice', 'nr_sinistro']],
    on='N° Apólice', how='left'
).groupby('Tipo de Apólice')['nr_sinistro'].nunique().reset_index()
qtd_sin_tp_seg.rename(columns={'nr_sinistro': 'Qtd_Sinistros'}, inplace=True)

df_tp_emissao_seg = pd.merge(df_tp_emissao_seg, qtd_sin_tp_seg, on='Tipo de Apólice', how='left').fillna(0)
df_tp_emissao_seg['Qtd_Sinistros'] = df_tp_emissao_seg['Qtd_Sinistros'].astype(int)
df_tp_emissao_seg['% Sinistralidade'] = df_tp_emissao_seg.apply(
    lambda row: '{:.2%}'.format(row['Total_Sinistro'] / row['Total_Premio'])
    if row['Total_Premio'] != 0 else '0.00%', axis=1
)
df_tp_emissao_seg['Total_Premio']   = df_tp_emissao_seg['Total_Premio'].map(formatar_valor_br)
df_tp_emissao_seg['Total_Sinistro'] = df_tp_emissao_seg['Total_Sinistro'].map(formatar_valor_br)
df_tp_emissao_seg = df_tp_emissao_seg[['Tipo de Apólice', 'Qtd_Apolices', 'Qtd_Sinistros', 'Total_Premio', 'Total_Sinistro', '% Sinistralidade']]

st.dataframe(df_tp_emissao_seg, hide_index=True, use_container_width=True)

#
#
#
#
# FIM DADOS DE SINISTRO
#
#
#
#


# st.divider()

# '''
# para cima trabalho filtro apólice
#
#
#
#
#
#
# '''


st.write("---")
st.caption("Desenvolvido por Alex Sousa.")
