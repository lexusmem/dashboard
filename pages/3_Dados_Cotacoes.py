import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# Configura a página para layout amplo (consistente com as demais)
st.set_page_config(layout='wide', page_title='Dados Cotações — Allseg', page_icon='📝')

# Link de volta para a página principal na sidebar
st.sidebar.header('Navegação')
st.sidebar.page_link("app.py", label="🏠  Início (Apólice / Segurado)")
st.sidebar.page_link("pages/2_Dados_Gerais.py", label="📊  Dados Gerais")

st.sidebar.caption(
    "O painel de cotações roda de forma independente das demais páginas. "
    "O upload do arquivo é solicitado abaixo, dentro do próprio painel, "
    "apenas quando esta página é acessada."
)

# ── Carrega o dashboard HTML standalone ──────────────────────────────────────
# O dashboard de cotações é um HTML autossuficiente (Tailwind + Chart.js +
# PapaParse + SheetJS) que lê o arquivo de cotações no próprio navegador.
# Nenhum dado é solicitado até esta página ser aberta — o uploader é interno
# ao HTML e só aparece aqui.
_HTML_PATH = Path(__file__).parent / "dashboard_rc_nibus_allseg_seguradora.html"

if not _HTML_PATH.exists():
    st.error(
        "Arquivo do dashboard de cotações não encontrado. "
        "Confirme que **dashboard_rc_nibus_allseg_seguradora.html** está na pasta "
        "`pages/`, ao lado deste arquivo."
    )
    st.stop()

_html = _HTML_PATH.read_text(encoding='utf-8')

# Renderiza o dashboard embutido. scrolling=True permite rolar o painel inteiro;
# a altura é generosa para acomodar KPIs, gráficos e a tabela sem cortar.
components.html(_html, height=2400, scrolling=True)
