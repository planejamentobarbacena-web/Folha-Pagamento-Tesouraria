import streamlit as st
import folha
import previdencia

st.set_page_config(
    page_title="Consolidação de Folha e Previdência",
    layout="centered"
)

# =============================
# TRADUÇÃO DO FILE UPLOADER
# =============================
st.markdown("""
<style>

/* Esconde textos padrão */
[data-testid="stFileUploader"] section div div div span {
    display: none;
}

/* Texto personalizado */
[data-testid="stFileUploader"] section div div div::before {
    content: "Arraste o arquivo aqui ou clique em Procurar";
    font-size: 16px;
    color: #444;
}

/* Botão */
[data-testid="stFileUploader"] button {
    text-indent: -9999px;
    line-height: 0;
}

[data-testid="stFileUploader"] button::after {
    content: "Procurar arquivo";
    text-indent: 0;
    display: block;
    line-height: initial;
}

</style>
""", unsafe_allow_html=True)

# =============================
# CABEÇALHO PRINCIPAL
# =============================
st.markdown("""
<div style="
    background: linear-gradient(90deg, #1F4E79, #2E6FA3);
    padding: 18px;
    border-radius: 8px;
    margin-bottom: 25px;
    text-align: center;
">
    <h2 style="color:white; margin:0 0 5px 0;">
        Consolidação - Folha e Previdência
    </h2>
    <span style="color:#E5EEF7;">
        Folha de Pagamento - Módulo Tesouraria
    </span>
</div>
""", unsafe_allow_html=True)

# =============================
# ESTILO PERSONALIZADO DAS ABAS
# =============================
st.markdown("""
<style>

/* Espaçamento entre abas */
.stTabs [data-baseweb="tab-list"] {
    gap: 30px;
}

/* Botão da aba */
.stTabs [data-baseweb="tab"] {
    padding: 22px 55px;
    border-radius: 10px 10px 0 0;
    background-color: #E5EEF7;
}

/* Texto da aba */
.stTabs [data-baseweb="tab"] p {
    font-size: 24px !important;
    font-weight: 600;
    margin: 0;
}

/* Hover */
.stTabs [data-baseweb="tab"]:hover {
    background-color: #cfddeb;
}

/* Aba ativa */
.stTabs [aria-selected="true"] {
    background-color: #1F4E79 !important;
}

.stTabs [aria-selected="true"] p {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# =============================
# ABAS PRINCIPAIS
# =============================
tab1, tab2 = st.tabs(["📊 Folha", "🏦 Previdência"])

with tab1:
    folha.render()

with tab2:
    previdencia.render()
