import streamlit as st
import folha
import previdencia

st.set_page_config(
    page_title="Consolidação de Folha e Previdência",
    layout="centered"
)

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

/* Texto interno da aba (aqui é o que realmente controla o tamanho) */
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

