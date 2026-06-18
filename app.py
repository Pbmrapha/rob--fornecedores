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
# FUNÇÃO PARA ACHAR COLUNA
# =========================
def achar_coluna(df, palavras_chave):
    for col in df.columns:
        for palavra in palavras_chave:
            if palavra in col.lower():
                return col
    return None

# =========================
# PROCESSAMENTO
# =========================
if st.button("🚀 Rodar robô"):

    if principal_file and fm_file and fma_file:

        principal = pd.read_excel(principal_file, dtype=str)
        fm = pd.read_excel(fm_file, dtype=str)
        fma = pd.read_excel(fma_file, dtype=str)

        # =========================
        # LIMPEZA E PADRONIZAÇÃO
        # =========================
        for df in [principal, fm, fma]:
            df.columns = df.columns.str.strip()

            # ---- CNPJ ----
            cnpj_col = achar_coluna(df, ["cnpj"])
            if cnpj_col:
                df[cnpj_col] = df[cnpj_col].apply(limpar_cnpj)
                df.rename(columns={cnpj_col: "CNPJ"}, inplace=True)

        # =========================
        # SEGMENTAÇÃO
        # =========================
        principal["segmentacao"] = ""

        principal.loc[principal["CNPJ"].isin(fm["CNPJ"]), "segmentacao"] = "FM"
        principal.loc[principal["CNPJ"].isin(fma["CNPJ"]), "segmentacao"] = "FMA"

        # =========================
        # NOVOS FORNECEDORES
        # =========================
        todos = pd.concat([fm, fma], ignore_index=True)
        novos = todos[~todos["CNPJ"].isin(principal["CNPJ"])].copy()

        novos["segmentacao"] = novos["CNPJ"].apply(
            lambda x: "FM" if x in fm["CNPJ"].values else "FMA"
        )

        # =========================
        # JUNTAR TUDO
        # =========================
        final = pd.concat([principal, novos], ignore_index=True)

        # remover duplicados
        final = final.drop_duplicates(subset=["CNPJ"], keep="first")

        # =========================
        # ORDENAR POR NOME (ROBUSTO)
        # =========================
        nome_col = achar_coluna(final, ["razao", "nome"])

        if nome_col:
            final[nome_col] = final[nome_col].fillna("")
            final = final.sort_values(by=nome_col)
        else:
            st.warning("Não achei coluna de nome/razão social para ordenar.")

        # =========================
        # DOWNLOAD
        # =========================
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
