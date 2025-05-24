import streamlit as st
import pandas as pd

st.title("Lab Gene Portal")

# Load external CSV directly
cn_df = pd.read_csv("https://drive.google.com/file/d/14YLHm_7oeoL6SK2lSrgPYoASggkGvkdh/view?usp=sharing")

mart_df = pd.read_csv("mart_export.txt", sep='\t')
mart_df = mart_df[['Gene name', 'Transcription start site (TSS)', 'Strand']].dropna()
mart_df.columns = ['Gene', 'TSS', 'Strand']

gene_input = st.text_area("Paste your gene list (one per line)")
cell_line = st.selectbox("Select Cell Line", cn_df.columns[1:])

if st.button("Process"):
    gene_list = [gene.strip() for gene in gene_input.splitlines() if gene.strip()]
    gene_data = mart_df[mart_df['Gene'].isin(gene_list)].copy()

    gene_data['Adjusted TSS'] = gene_data.apply(
        lambda row: row['TSS'] if row['Strand'] == 1 else f"-{row['TSS']}", axis=1
    )

    cn_subset = cn_df[cn_df['Gene'].isin(gene_list)][['Gene', cell_line]]
    cn_subset.columns = ['Gene', 'Copy Number']

    final_df = pd.merge(gene_data, cn_subset, on='Gene', how='left')

    def highlight_copy_number(val):
        if pd.isna(val):
            return 'background-color: white'
        elif val > 5:
            return 'background-color: #FF9999'
        elif val < 2:
            return 'background-color: #99FF99'
        else:
            return 'background-color: #FFFF99'

    styled_df = final_df[['Gene', 'Adjusted TSS', 'Copy Number']].style.applymap(
        highlight_copy_number, subset=['Copy Number']
    )

    st.dataframe(styled_df, width=700, height=400)
