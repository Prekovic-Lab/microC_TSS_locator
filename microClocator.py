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

# User input fields
gene_input = st.text_area("📋 Paste your gene list (one per line):", height=150)
cell_lines = cn_df['cell_line_display_name'].unique()
cell_line = st.selectbox("🧬 Select Cell Line:", cell_lines)

if st.button("🚀 Process"):
    gene_list = [gene.strip() for gene in gene_input.splitlines() if gene.strip()]
    if not gene_list:
        st.error("⚠️ Please provide a valid list of genes.")
        st.stop()

    # Filter gene data from mart_export
    gene_data = mart_df[mart_df['Gene'].isin(gene_list)].copy()

    # Copy number extraction (optimized)
    cn_subset = cn_df.loc[cn_df['cell_line_display_name'] == cell_line, gene_list]
    cn_subset = cn_subset.T.reset_index()
    cn_subset.columns = ['Gene', 'Copy Number']

    # Merge clearly
    final_df = pd.merge(gene_data, cn_subset, on='Gene', how='left').fillna('N/A')

    # Calculate mean copy number and define coloring
    numeric_copy_numbers = pd.to_numeric(final_df['Copy Number'], errors='coerce')
    mean_cn = numeric_copy_numbers.mean()

    def highlight_outliers(val):
        try:
            val_float = float(val)
            if val_float > mean_cn * 1.5:
                return 'background-color: #FF6666; color: black'  # red for too high
            elif val_float < mean_cn * 0.5:
                return 'background-color: #6699FF; color: black'  # blue for too low
            else:
                return ''
        except:
            return ''

    # Reordering columns as requested
    final_df = final_df[['Gene', 'Chr', 'TSS', 'Gene Start', 'Gene End', 'Copy Number']]

    # Style dataframe
    styled_df = final_df.style.applymap(
        highlight_outliers, subset=['Copy Number']
    ).set_properties(**{
        'text-align': 'center',
        'border': '1px solid #ddd'
    })

    # Display results
    st.subheader("📌 Results")
    st.dataframe(styled_df, use_container_width=True, height=600)

    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download CSV", csv, "gene_tss_results.csv", "text/csv")

else:
    st.info("ℹ️ Enter genes, select a cell line, and click **Process**.")

st.markdown("---")
st.markdown("🔗 [Prekovic Lab](https://www.prekovic-lab.org) | ✉️ [Contact](mailto:s.prekovic@umcutrecht.nl)")
