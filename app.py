import streamlit as st
import pandas as pd

st.title("RPA de Consolidação de Fornecedores")

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

```
if principal_file and fm_file and fma_file:

    principal = pd.read_excel(principal_file, dtype=str)
    fm = pd.read_excel(fm_file, dtype=str)
    fma = pd.read_excel(fma_file, dtype=str)

    # =========================
    # LIMPEZA E PADRONIZAÇÃO
    # =========================
    for df in [principal, fm, fma]:

        df.columns = df.columns.str.strip()

        cnpj_col = achar_coluna(df, ["cnpj"])

        if cnpj_col:
            df[cnpj_col] = df[cnpj_col].apply(limpar_cnpj)
            df.rename(columns={cnpj_col: "CNPJ"}, inplace=True)

    # =========================
    # CONJUNTOS DE CNPJ
    # =========================
    fm_cnpjs = set(fm["CNPJ"])
    fma_cnpjs = set(fma["CNPJ"])

    # =========================
    # SEGMENTAÇÃO PRINCIPAL
    # =========================
    principal["segmentacao"] = ""

    for i, cnpj in principal["CNPJ"].items():

        esta_fm = cnpj in fm_cnpjs
        esta_fma = cnpj in fma_cnpjs

        if esta_fm and esta_fma:
            principal.at[i, "segmentacao"] = "FM + FMA"

        elif esta_fm:
            principal.at[i, "segmentacao"] = "FM"

        elif esta_fma:
            principal.at[i, "segmentacao"] = "FMA"

    # =========================
    # NOVOS FORNECEDORES
    # =========================
    todos = pd.concat([fm, fma], ignore_index=True)

    novos = todos[
        ~todos["CNPJ"].isin(principal["CNPJ"])
    ].copy()

    def definir_segmentacao(cnpj):

        esta_fm = cnpj in fm_cnpjs
        esta_fma = cnpj in fma_cnpjs

        if esta_fm and esta_fma:
            return "FM + FMA"

        elif esta_fm:
            return "FM"

        elif esta_fma:
            return "FMA"

        return ""

    novos["segmentacao"] = novos["CNPJ"].apply(definir_segmentacao)

    # =========================
    # JUNTAR TUDO
    # =========================
    final = pd.concat([principal, novos], ignore_index=True)

    # remover duplicados
    final = final.drop_duplicates(subset=["CNPJ"], keep="first")

    # =========================
    # ORDENAR POR NOME
    # =========================
    nome_col = achar_coluna(final, ["razao", "nome"])

    if nome_col:
        final[nome_col] = final[nome_col].fillna("")
        final = final.sort_values(by=nome_col)
    else:
        st.warning(
            "Não achei coluna de nome/razão social para ordenar."
        )

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
```

        st.error("Envie as 3 planilhas antes de rodar.")
