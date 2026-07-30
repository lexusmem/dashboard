import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from allseg_theme import aplicar_tema

# Configura a página para layout amplo (consistente com as demais)
st.set_page_config(layout='wide', page_title='Dados Cotações — Allseg', page_icon='📝')

# Aplica o tema padrão do painel: esconde a navegação automática do Streamlit,
# o header/toolbar/footer nativos e estiliza sidebar e page_links como no app.
aplicar_tema()

# Remove o padding superior do container para o dashboard começar no topo e
# ocupar a largura total (sem parecer um "site dentro do site").
st.markdown("""
<style>
[data-testid="stAppViewContainer"] .main .block-container {
    padding-top: 0rem !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
    max-width: 100% !important;
}
iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Navegação na sidebar (mesmo padrão das demais páginas) ───────────────────
st.sidebar.header('Navegação')
st.sidebar.page_link("app.py", label="📋  Apólice / Segurado")
st.sidebar.page_link("pages/2_Dados_Gerais.py", label="📊  Dados Gerais")
st.sidebar.page_link("pages/3_Dados_Cotacoes.py", label="📝  Dados Cotações")

# ── Carrega o dashboard HTML standalone ──────────────────────────────────────
# HTML autossuficiente (Tailwind + Chart.js + PapaParse + SheetJS) que lê o
# arquivo de cotações no próprio navegador. Nenhum dado é solicitado até esta
# página ser aberta — o uploader é interno ao HTML.
_HTML_PATH = Path(__file__).parent / "dashboard_rc_nibus_allseg_seguradora.html"

if not _HTML_PATH.exists():
    st.error(
        "Arquivo do dashboard de cotações não encontrado. "
        "Confirme que **dashboard_rc_nibus_allseg_seguradora.html** está na pasta "
        "`pages/`, ao lado deste arquivo."
    )
    st.stop()

_html = _HTML_PATH.read_text(encoding='utf-8')

# Renderiza o dashboard embutido ocupando a largura total. scrolling=True
# permite rolar o painel inteiro; a altura é generosa para KPIs, gráficos e
# tabela sem cortar.
components.html(_html, height=2400, scrolling=True)
