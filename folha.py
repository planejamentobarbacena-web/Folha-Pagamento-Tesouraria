import streamlit as st
import pandas as pd
import io


def render():

    # =============================
    # UPLOAD
    # =============================
    arquivo = st.file_uploader(
        "Envie o arquivo da folha (CSV ou Excel)",
        type=["csv", "xls", "xlsx"]
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
    # FILTRAR EVENTOS
    # =============================
    df = df[df["Tipo Evento"].isin(["VENCIMENTO", "DESCONTO"])].copy()

    # =============================
    # SEPARAR ESTRUTURA
    # =============================
    df["codigo_completo"] = df["Estrutura organizacional"].str.split(" - ").str[0]
    df["Estrutura"] = df["Estrutura organizacional"].str.split(" - ").str[1]

    df["Organograma"] = df["codigo_completo"].str[:8]
    df["Fonte de Recurso"] = df["codigo_completo"].str[8:]

    df.drop(columns=["codigo_completo"], inplace=True)

    # =============================
    # MAPA DE FONTES
    # =============================
    mapa_fontes = {
        "15401070": "FUNDEB",
        "15400000": "FUNDEB",
        "25401070": "FUNDEB",
        "25400000": "FUNDEB"
        }

    df["Fonte de Recurso"] = (
        df["Fonte de Recurso"]
        .astype(str)
        .str.strip()
        .replace(mapa_fontes)
    )

    # =============================
    # TRATAR VALORES
    # =============================
    df["Valor calculado"] = (
        df["Valor calculado"]
        .str.replace(" P", "", regex=False)
        .str.replace(" D", "", regex=False)
    )

    df["Valor_num"] = (
        df["Valor calculado"]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    # =============================
    # SEPARAR BASES
    # =============================
    vencimentos = df[df["Tipo Evento"] == "VENCIMENTO"].copy()
    descontos = df[df["Tipo Evento"] == "DESCONTO"].copy()

    # =============================
    # SOMAS POR FONTE
    # =============================
    total_vencimentos = (
        vencimentos
        .groupby("Fonte de Recurso")["Valor_num"]
        .sum()
        .reset_index()
        .rename(columns={"Valor_num": "Total Vencimentos"})
    )

    total_descontos = (
        descontos
        .groupby("Fonte de Recurso")["Valor_num"]
        .sum()
        .reset_index()
        .rename(columns={"Valor_num": "Total Descontos"})
    )

    totais = (
        total_vencimentos
        .merge(total_descontos, on="Fonte de Recurso", how="left")
        .fillna(0)
    )

    totais["Liquido + Vale"] = (
        totais["Total Vencimentos"]
        - totais["Total Descontos"]
    )

    # =============================
    # VALE
    # =============================
    vale = vencimentos[
        vencimentos["Evento"].isin([
            "AUXILIO ALIMENTACAO",
            "AUXILIO ALIMENTACAO MÊS ANT"
        ])
    ]

    vale_por_fonte = (
        vale
        .groupby("Fonte de Recurso")["Valor_num"]
        .sum()
        .reset_index()
        .rename(columns={"Valor_num": "Vale"})
    )

    aba_vencimentos = (
        totais
        .merge(vale_por_fonte, on="Fonte de Recurso", how="left")
        .fillna(0)
    )

    aba_vencimentos["Liquido"] = (
        aba_vencimentos["Liquido + Vale"]
        - aba_vencimentos["Vale"]
    )

    aba_vencimentos = aba_vencimentos[
        ["Fonte de Recurso", "Liquido", "Vale", "Liquido + Vale"]
    ]

    # =============================
    # DESCONTOS POR EVENTO
    # =============================
    aba_descontos = (
        descontos
        .pivot_table(
            index="Evento",
            columns="Fonte de Recurso",
            values="Valor_num",
            aggfunc="sum",
            fill_value=0
        )
        .reset_index()
    )

    # =============================
    # FORMATAR MOEDA
    # =============================
    def formatar_moeda(valor):
        return f"R${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    aba_vencimentos_exibir = aba_vencimentos.copy()
    for col in ["Liquido", "Vale", "Liquido + Vale"]:
        aba_vencimentos_exibir[col] = aba_vencimentos_exibir[col].apply(formatar_moeda)

    aba_descontos_exibir = aba_descontos.copy()
    for col in aba_descontos_exibir.columns[1:]:
        aba_descontos_exibir[col] = aba_descontos_exibir[col].apply(formatar_moeda)

    # =============================
    # EXIBIÇÃO
    # =============================
    st.subheader("📊 Vencimentos por Fonte")
    st.dataframe(aba_vencimentos_exibir, use_container_width=True)

    st.subheader("📉 Descontos por Evento")
    st.dataframe(aba_descontos_exibir, use_container_width=True)

    # =============================
    # EXPORTAÇÃO EXCEL
    # =============================
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        aba_vencimentos.to_excel(writer, sheet_name="Vencimentos", index=False)
        aba_descontos.to_excel(writer, sheet_name="Descontos", index=False)

        workbook = writer.book
        formato_moeda = workbook.add_format({'num_format': 'R$ #,##0.00'})

        ws_v = writer.sheets["Vencimentos"]
        ws_v.set_column("B:D", 18, formato_moeda)

        ws_d = writer.sheets["Descontos"]
        ws_d.set_column(1, 100, 18, formato_moeda)

    st.download_button(
        label="📥 Baixar planilha de fechamento",
        data=output.getvalue(),
        file_name="fechamento_folha.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )