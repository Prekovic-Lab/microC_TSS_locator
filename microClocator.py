import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prekovic Lab Gene TSS Portal", layout="wide")

st.title("🔬 Prekovic Lab Gene TSS Portal")

@st.cache_data
def load_data():
    cn_df = pd.read_csv("GeneCount.csv")
    mart_df = pd.read_csv("mart_export.txt", sep='\t')
    mart_df = mart_df[mart_df["Ensembl Canonical"] == 1][['Gene name', 'Transcription start site (TSS)', 'Strand']]
    mart_df.columns = ['Gene', 'TSS', 'Strand']
    return cn_df, mart_df

cn_df, mart_df = load_data()

# Input fields
gene_input = st.text_area("📋 Paste your gene list (one per line):", height=150)

# Correctly select cell lines (optimized clearly!)
cell_lines = cn_df['cell_line_display_name'].unique()
cell_line = st.selectbox("🧬 Select Cell Line:", cell_lines)

if st.button("🚀 Process"):
    gene_list = [gene.strip() for gene in gene_input.splitlines() if gene.strip()]
    if not gene_list:
        st.error("⚠️ Please provide a valid list of genes.")
        st.stop()

    # Filter mart file for gene info
    gene_data = mart_df[mart_df['Gene'].isin(gene_list)].copy()
    gene_data['Adjusted TSS'] = gene_data.apply(
        lambda row: row['TSS'] if row['Strand'] == 1 else f"-{row['TSS']}", axis=1
    )

    # Efficient extraction of copy number values per selected cell line
    cn_subset = cn_df.loc[cn_df['cell_line_display_name'] == cell_line, gene_list]
    cn_subset = cn_subset.T.reset_index()
    cn_subset.columns = ['Gene', 'Copy Number']

    # Merge gene info with copy number clearly
    final_df = pd.merge(gene_data, cn_subset, on='Gene', how='left').fillna('N/A')

    # Highlighting optimized
    def highlight_copy_number(val):
        try:
            val_float = float(val)
            if val_float > 5:
                return 'background-color: #FF6666; color: black'
            elif val_float < 2:
                return 'background-color: #66CC66; color: black'
            else:
                return 'background-color: #FFDD44; color: black'
        except:
            return 'background-color: #DDDDDD; color: black'

    styled_df = final_df[['Gene', 'Adjusted TSS', 'Copy Number']].style.applymap(
        highlight_copy_number, subset=['Copy Number']
    ).set_properties(**{'text-align': 'center', 'border': '1px solid #aaa'})

    st.subheader("📌 Results")
    st.dataframe(styled_df, use_container_width=True, height=500)

    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download CSV", csv, "gene_tss_results.csv", "text/csv")

else:
    st.info("ℹ️ Enter genes, select cell line, and click **Process**.")

st.markdown("---")
st.markdown("🔗 [Prekovic Lab](https://www.prekovic-lab.org) | ✉️ [Contact](mailto:s.prekovic@umcutrecht.nl)")
