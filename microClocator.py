import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prekovic Lab Gene TSS Portal", layout="wide")

st.title("Prekovic Lab Gene TSS Portal for MicroC")

try:
    # Explicitly load files
    cn_df = pd.read_csv("GeneCount.csv")
    mart_df = pd.read_csv("mart_export.txt", sep='\t')

    # Filter canonical TSS entries
    mart_df = mart_df[mart_df["Ensembl Canonical"] == 1][['Gene name', 'Transcription start site (TSS)', 'Strand']]
    mart_df.columns = ['Gene', 'TSS', 'Strand']
except Exception as e:
    st.error(f"Error loading files: {e}")
    st.stop()

gene_input = st.text_area("📋 Paste gene list (one per line)", height=200)

if not gene_input:
    st.info("Enter your gene list above.")
    st.stop()

if cn_df.shape[1] < 2:
    st.error("Your copy number CSV seems corrupted or improperly formatted (less than 2 columns). Check file content!")
    st.stop()

cell_line = st.selectbox("🧬 Select Cell Line", cn_df.columns[1:])

if st.button("🚀 Process"):
    gene_list = [gene.strip() for gene in gene_input.splitlines() if gene.strip()]
    if not gene_list:
        st.error("Please provide valid gene names.")
        st.stop()

    gene_data = mart_df[mart_df['Gene'].isin(gene_list)].copy()
    gene_data['Adjusted TSS'] = gene_data.apply(
        lambda row: row['TSS'] if row['Strand'] == 1 else f"-{row['TSS']}", axis=1
    )

    cn_subset = cn_df[cn_df['Gene'].isin(gene_list)][['Gene', cell_line]]
    cn_subset.columns = ['Gene', 'Copy Number']

    final_df = pd.merge(gene_data, cn_subset, on='Gene', how='left').fillna('N/A')

    styled_df = final_df[['Gene', 'Adjusted TSS', 'Copy Number']].style.set_properties(**{
        'text-align': 'center',
        'border': '1px solid black'
    })

    st.subheader("📌 Results")
    st.dataframe(styled_df, use_container_width=True)

    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Download CSV",
        data=csv,
        file_name="gene_tss_results.csv",
        mime="text/csv"
    )
