import streamlit as st
import pandas as pd

st.title("🤖 Robô de Consolidação de Fornecedores")

# =========================
# UPLOAD DOS ARQUIVOS
# =========================
principal_file = st.file_uploader("Planilha Principal", type=["xlsx"])
fm_file = st.file_uploader("Planilha FM", type=["xlsx"])
fma_file = st.file_uploader("Planilha FMA", type=["xlsx"])

# =========================
# FUNÇÃO CNPJ
# =========================
def limpar_cnpj(cnpj):
    if pd.isna(cnpj):
        return ""
    cnpj = str(cnpj)
    cnpj = ''.join(filter(str.isdigit, cnpj))
    return cnpj.zfill(14)

# =========================
# PROCESSAMENTO
# =========================
if st.button("🚀 Rodar robô"):

    if principal_file and fm_file and fma_file:

        principal = pd.read_excel(principal_file, dtype=str)
        fm = pd.read_excel(fm_file, dtype=str)
        fma = pd.read_excel(fma_file, dtype=str)

        # limpar CNPJ
        for df in [principal, fm, fma]:
            df["CNPJ"] = df["CNPJ"].apply(limpar_cnpj)

        # segmentação
        principal["segmentacao"] = ""

        principal.loc[principal["CNPJ"].isin(fm["CNPJ"]), "segmentacao"] = "FM"
        principal.loc[principal["CNPJ"].isin(fma["CNPJ"]), "segmentacao"] = "FMA"

        # novos fornecedores
        todos = pd.concat([fm, fma], ignore_index=True)
        novos = todos[~todos["CNPJ"].isin(principal["CNPJ"])]

        novos["segmentacao"] = novos["CNPJ"].apply(
            lambda x: "FM" if x in fm["CNPJ"].values else "FMA"
        )

        # juntar tudo
        final = pd.concat([principal, novos], ignore_index=True)

        # remover duplicados
        final = final.drop_duplicates(subset=["CNPJ"], keep="first")

        # ordenar
        col_nome = "Razao Social"
        final[col_nome] = final[col_nome].fillna("")
        final = final.sort_values(by=col_nome)

        # download
        st.success("Processo concluído!")

        output_file = "planilha_final.xlsx"
        final.to_excel(output_file, index=False)

        with open(output_file, "rb") as file:
            st.download_button(
                label="📥 Baixar planilha final",
                data=file,
                file_name="planilha_final.xlsx"
            )

    else:
        st.error("Envie as 3 planilhas antes de rodar.")