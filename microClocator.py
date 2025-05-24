import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Prekovic Lab Gene TSS Portal", layout="wide")
st.title("🔬 Prekovic Lab Gene TSS Portal")

@st.cache_data
def load_data():
    cn_df = pd.read_csv("GeneCount.csv")
    mart_df = pd.read_csv("mart_export.txt", sep='\t')
    mart_df = mart_df[mart_df["Ensembl Canonical"] == 1][[
        'Gene name', 'Chromosome/scaffold name', 'Transcription start site (TSS)', 
        'Gene start (bp)', 'Gene end (bp)'
    ]].dropna()
    mart_df.columns = ['Gene', 'Chr', 'TSS', 'Gene Start', 'Gene End']
    return cn_df, mart_df

cn_df, mart_df = load_data()

gene_input = st.text_area("📋 Paste your gene list (one per line):", height=150)
cell_lines = cn_df['cell_line_display_name'].unique()
cell_line = st.selectbox("🧬 Select Cell Line:", cell_lines)

if st.button("🚀 Process"):
    gene_list = [gene.strip() for gene in gene_input.splitlines() if gene.strip()]
    if not gene_list:
        st.error("⚠️ Please provide a valid list of genes.")
        st.stop()

    # Filter mart file for gene info
    gene_data = mart_df[mart_df['Gene'].isin(gene_list)].copy()

    # Identify missing genes explicitly
    found_genes = gene_data['Gene'].tolist()
    missing_genes = list(set(gene_list) - set(found_genes))

    # Extract copy number data clearly and efficiently
    available_genes_in_cn = [gene for gene in gene_list if gene in cn_df.columns]
    cn_subset = cn_df.loc[cn_df['cell_line_display_name'] == cell_line, available_genes_in_cn]
    cn_subset = cn_subset.T.reset_index()
    cn_subset.columns = ['Gene', 'Copy Number']

    # Merge data
    final_df = pd.merge(gene_data, cn_subset, on='Gene', how='left')

    # Report missing genes explicitly
    if missing_genes:
        missing_df = pd.DataFrame({
            'Gene': missing_genes,
            'Chr': 'N/A',
            'TSS': 'N/A',
            'Gene Start': 'N/A',
            'Gene End': 'N/A',
            'Copy Number': 'N/A'
        })
        final_df = pd.concat([final_df, missing_df], ignore_index=True)

    numeric_cn = pd.to_numeric(final_df['Copy Number'], errors='coerce')
    mean_cn = numeric_cn.mean()

    # Highlighting logic exactly as requested
    def highlight_cn(val):
        try:
            val_float = float(val)
            if val_float >= 2 * mean_cn:
                return 'background-color: #FF6666; color: black'  # red
            elif val_float <= 0.5 * mean_cn:
                return 'background-color: #6699FF; color: black'  # blue
            else:
                return ''
        except:
            return ''

    final_df = final_df[['Gene', 'Chr', 'TSS', 'Gene Start', 'Gene End', 'Copy Number']]
    styled_df = final_df.style.applymap(
        highlight_cn, subset=['Copy Number']
    ).set_properties(**{'text-align': 'center', 'border': '1px solid #aaa'})

    st.subheader("📌 Results")
    st.dataframe(styled_df, use_container_width=True, height=600)

    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download CSV", csv, "gene_tss_results.csv", "text/csv")

else:
    st.info("ℹ️ Enter genes, select cell line, and click **Process**.")

st.markdown("---")
st.markdown("🔗 [Prekovic Lab](https://www.prekovic-lab.org) | ✉️ [Contact](mailto:s.prekovic@umcutrecht.nl)")
