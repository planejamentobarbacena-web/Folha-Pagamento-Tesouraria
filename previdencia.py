import streamlit as st
import pandas as pd
import io


def render():

    arquivo = st.file_uploader(
        "Envie o arquivo da Previdência (CSV ou Excel)",
        type=["csv", "xls", "xlsx"],
        key="arquivo_previdencia"
    )

    if not arquivo:
        return

    nome_arquivo = arquivo.name.lower()

    # =============================
    # LEITURA
    # =============================
    if nome_arquivo.endswith(".csv"):
        df = pd.read_csv(
            arquivo,
            sep=";",
            encoding="utf-8",
            dtype=str
        )
    else:
        df = pd.read_excel(
            arquivo,
            dtype=str
        )

    df.columns = df.columns.str.strip()

    # =============================
    # EXTRAIR FONTE (8 últimos dígitos)
    # =============================
    df["Fonte de Recurso"] = df["ORGANOGRAMA"].str.replace(".", "", regex=False).str[-8:]

    mapa_fontes = {
        "15401070": "FUNDEB",
        "15400000": "FUNDEB",
        "25401070": "FUNDEB",
        "25400000": "FUNDEB"
        }

    df["Fonte de Recurso"] = (
        df["Fonte de Recurso"]
        .replace(mapa_fontes)
    )

    # =============================
    # TRATAR VALORES NUMÉRICOS
    # =============================
    def tratar_valor(coluna):
        return (
            coluna
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

    df["SEGURADO"] = tratar_valor(df["Evento Previd."])
    df["PATRONAL"] = tratar_valor(df["Fundo (28,00%)"])

    # =============================
    # AGRUPAR POR FONTE
    # =============================
    resumo = df.groupby("Fonte de Recurso")[["SEGURADO", "PATRONAL"]].sum().reset_index()

    resumo["TOTAL"] = resumo["SEGURADO"] + resumo["PATRONAL"]

    # =============================
    # FORMATAR PARA EXIBIÇÃO
    # =============================
    def formatar_moeda(valor):
        return f"R${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    resumo_exibir = resumo.copy()

    for col in ["SEGURADO", "PATRONAL", "TOTAL"]:
        resumo_exibir[col] = resumo_exibir[col].apply(formatar_moeda)

    # =============================
    # MOSTRAR NA TELA
    # =============================
    st.subheader("🏦 Consolidado Previdência por Fonte")
    st.dataframe(resumo_exibir, use_container_width=True)

    # =============================
    # GERAR EXCEL
    # =============================
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        resumo.to_excel(writer, sheet_name="Previdencia", index=False)

        workbook = writer.book
        formato_moeda = workbook.add_format({'num_format': 'R$ #,##0.00'})

        worksheet = writer.sheets["Previdencia"]
        worksheet.set_column("B:D", 18, formato_moeda)

    st.download_button(
        label="📥 Baixar planilha da Previdência",
        data=output.getvalue(),
        file_name="fechamento_previdencia.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )