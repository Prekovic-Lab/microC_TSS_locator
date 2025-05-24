import streamlit as st
import pandas as pd

# Streamlit page setup
st.set_page_config(page_title="Prekovic Lab Gene TSS Locator", layout="wide")
st.title("🔬 Prekovic Lab Gene TSS Portal")

# Load data safely with error handling
try:
    cn_df = pd.read_csv("GeneCount.csv")
    mart_df = pd.read_csv("mart_export.txt", sep='\t')
    mart_df = mart_df[mart_df["Ensembl Canonical"] == 1][['Gene name', 'Transcription start site (TSS)', 'Strand']].dropna()
    mart_df.columns = ['Gene', 'TSS', 'Strand']
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# User inputs clearly presented
gene_input = st.text_area("Paste your gene list (one per line)", height=200)
cell_line = st.selectbox("Select Cell Line", cn_df.columns[1:])

if st.button("Process"):
    gene_list = [gene.strip() for gene in gene_input.splitlines() if gene.strip()]
    
    gene_data = mart_df[mart_df['Gene'].isin(gene_list)].copy()
    gene_data['Adjusted TSS'] = gene_data.apply(
        lambda row: row['TSS'] if row['Strand'] == 1 else f"-{row['TSS']}", axis=1
    )

    cn_subset = cn_df[cn_df['Gene'].isin(gene_list)][['Gene', cell_line]]
    cn_subset.columns = ['Gene', 'Copy Number']

    final_df = pd.merge(gene_data, cn_subset, on='Gene', how='left').fillna('N/A')

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
    ).set_properties(**{
        'text-align': 'center',
        'border': '1px solid black'
    })

    st.subheader("📌 Results")
    st.dataframe(styled_df, use_container_width=True, height=500)

    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Download CSV",
        data=csv,
        file_name="gene_tss_results.csv",
        mime="text/csv"
    )
else:
    st.info("Enter genes, select cell line, and click **Process** to see results.")

st.markdown("---")
st.markdown("🔗 [Prekovic Lab](https://www.prekovic-lab.org) | ✉️ [Contact](mailto:s.prekovic@umcutrecht.nl)")
