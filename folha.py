import streamlit as st
import pandas as pd
import io


def render():

    st.title("Fechamento da Folha")

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
        df = pd.read_excel(arquivo, dtype=str)

    df.columns = df.columns.str.strip()

    # =============================
    # FILTRAR EVENTOS
    # =============================
    df = df[df["Tipo Evento"].isin(["VENCIMENTO", "DESCONTO"])].copy()

    # =============================
    # SEPARAR ESTRUTURA
    # =============================
    df["codigo_completo"] = df["Estrutura organizacional"].str.split(" - ").str[0]

    df["Código Secretaria"] = df["codigo_completo"].str[:2]
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
    # VENCIMENTOS POR FONTE
    # =============================
    total_vencimentos = (
        vencimentos.groupby("Fonte de Recurso")["Valor_num"]
        .sum()
        .reset_index()
        .rename(columns={"Valor_num": "Total Vencimentos"})
    )

    total_descontos = (
        descontos.groupby("Fonte de Recurso")["Valor_num"]
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

    # VALE
    vale = vencimentos[
        vencimentos["Evento"].isin([
            "AUXILIO ALIMENTACAO",
            "AUXILIO ALIMENTACAO MÊS ANT"
        ])
    ]

    vale_por_fonte = (
        vale.groupby("Fonte de Recurso")["Valor_num"]
        .sum()
        .reset_index()
        .rename(columns={"Valor_num": "Vale"})
    )

    # IRRF
    irrf = descontos[
        descontos["Evento"].str.contains("I.R.R.F", case=False, na=False)
    ]

    irrf_por_fonte = (
        irrf.groupby("Fonte de Recurso")["Valor_num"]
        .sum()
        .reset_index()
        .rename(columns={"Valor_num": "IRRF"})
    )

    aba_vencimentos = (
        totais
        .merge(vale_por_fonte, on="Fonte de Recurso", how="left")
        .merge(irrf_por_fonte, on="Fonte de Recurso", how="left")
        .fillna(0)
    )

    aba_vencimentos["Liquido"] = (
        aba_vencimentos["Liquido + Vale"]
        - aba_vencimentos["Vale"]
    )

    aba_vencimentos = aba_vencimentos[
        ["Fonte de Recurso", "Liquido", "Vale", "Liquido + Vale", "IRRF"]
    ]

    # =============================
    # RETENÇÕES À CREDORES
    # =============================
    mapa_classificacao = {
        "ASS.DOS S. PUB.MUNICIPAIS": "ASPM",
        "ASPM - SEDE SOCIAL": "ASPM",
        "TAXA MANUTENCAO UNIMED": "ASPM",
        "UNIMED DEPENTES INDIRETOS": "ASPM",
        "UNIMED INDIVIDUAL": "ASPM",
        "FUNDO RESERVA UNIMED": "ASPM",
        "ASPM - CARTÃO DE TODOS": "ASPM",
        "UNIMED INTERNACAO II": "ASPM",
        "ASPM UNIMED": "ASPM",
        "UNIMED INTERNACAO I": "ASPM",
        "CEF CONSIG.PREFEITURA": "CAIXA ECONÔMICA",
        "CONSIGNACAO BCO ITAU": "ITAÚ",
        "SIND. SERV.PUBL. MUNIC.": "SINDICATO DOS SERVIDORES",
        "SICOOB CONSIGNAÇÃO": "SICOOB CONSIGNADO",
        "PREVISUL": "PREVISUL",
        "SIND. UTE": "SIND. UTE",
        "BANCO BRASIL CONSIGNACAO": "BANCO DO BRASIL",
        "CONSIGNADO SICREDI": "CONSIGNADO SICREDI",
        "ASSOCIACAO GUARDA MUNIC.": "ASSOCIAÇÃO DOS GUARDAS",
        "FARMACIA (ASS GUARDA MUN)": "ASSOCIAÇÃO DOS GUARDAS",
        "VERTCON SEGUROS": "VERTCON",
        "CONSIG BRADESCO": "BRADESCO",
        "CAPEMISA PREV/ SEG/EMPR": "CAPEMISA"
    }

    descontos["Credor"] = descontos["Evento"].map(mapa_classificacao)

    consignacoes = descontos[descontos["Credor"].notna()].copy()

    aba_repasses = (
        consignacoes.pivot_table(
            index="Credor",
            columns="Fonte de Recurso",
            values="Valor_num",
            aggfunc="sum",
            fill_value=0
        ).reset_index()
    )

    # =============================
    # DESCONTOS POR EVENTO
    # =============================
    aba_descontos = (
        descontos.pivot_table(
            index="Evento",
            columns="Fonte de Recurso",
            values="Valor_num",
            aggfunc="sum",
            fill_value=0
        ).reset_index()
    )

    # =============================
    # FORMATAÇÃO
    # =============================
    def formatar_moeda(valor):
        return f"R${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    for df_exibir in [aba_vencimentos, aba_repasses, aba_descontos]:
        for col in df_exibir.columns[1:]:
            df_exibir[col] = df_exibir[col].apply(formatar_moeda)

    # =============================
    # EXIBIÇÃO NA TELA
    # =============================
    st.subheader("📊 Vencimentos por Fonte")
    st.dataframe(aba_vencimentos, use_container_width=True)

    st.subheader("🏦 Retenções à Credores")
    st.dataframe(aba_repasses, use_container_width=True)

    st.subheader("📉 Descontos por Evento")
    st.dataframe(aba_descontos, use_container_width=True)

    # =============================
    # ALERTA APÓS DESCONTOS
    # =============================
    nao_classificados = descontos[descontos["Credor"].isna()]["Evento"].unique()

    if len(nao_classificados) > 0:
        st.error("⚠️ ATENÇÃO: EXISTEM DESCONTOS NÃO CLASSIFICADOS PARA RETENÇÃO À CREDORES")

        st.markdown("### Eventos não mapeados:")
        st.dataframe(
            pd.DataFrame(nao_classificados, columns=["Evento não classificado"]),
            use_container_width=True
        )

    # =============================
    # EXPORTAÇÃO EXCEL
    # =============================
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        aba_vencimentos.to_excel(writer, sheet_name="Vencimentos", index=False)
        aba_repasses.to_excel(writer, sheet_name="Retencoes_Credores", index=False)
        aba_descontos.to_excel(writer, sheet_name="Descontos", index=False)

    st.download_button(
        label="📥 Baixar planilha de fechamento",
        data=output.getvalue(),
        file_name="fechamento_folha.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
   render()
