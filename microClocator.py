import streamlit as st
import pandas as pd

# Streamlit page configuration (visually appealing layout)
st.set_page_config(page_title="Gene Locator Portal", layout="wide")

# Title and description
st.title("Prekovic Lab Gene TSS Portal for MicroC")
st.markdown("""
Enter your gene list below, select the desired cell line, and click **Process**.  
You'll receive a neatly formatted table showing the Transcription Start Sites (TSS) and Copy Numbers.
""")

# Load external CSV directly (your Dropbox direct link)
cn_df = pd.read_csv(
    "https://www.dropbox.com/scl/fi/fpnvolwlhozzqyvu7qh3q/Omics_Absolute_CN_Gene_Public_24Q4_subsetted.csv?rlkey=tn5hwmm01u6ww29t2nv81cf54&st=rd7e84ex&dl=1"
)

# Load and filter mart_export.txt based on Ensembl Canonical == 1
mart_df = pd.read_csv("mart_export.txt", sep='\t')
mart_df = mart_df[mart_df["Ensembl Canonical"] == 1][['Gene name', 'Transcription start site (TSS)', 'Strand']].dropna()
mart_df.columns = ['Gene', 'TSS', 'Strand']

# User inputs (visually appealing sections)
with st.sidebar:
    st.header("Input Options")
    gene_input = st.text_area("📋 Paste gene list (one per line):", height=250)
    cell_line = st.selectbox("🧬 Select Cell Line:", cn_df.columns[1:])
    process_button = st.button("🚀 Process")

# Main content processing
if process_button:
    gene_list = [gene.strip() for gene in gene_input.splitlines() if gene.strip()]
    
    # Match genes with mart_df
    gene_data = mart_df[mart_df['Gene'].isin(gene_list)].copy()

    # Adjust TSS based on strand direction (+ or -)
    gene_data['Adjusted TSS'] = gene_data.apply(
        lambda row: row['TSS'] if row['Strand'] == 1 else f"-{row['TSS']}", axis=1
    )

    # Extract copy number data
    cn_subset = cn_df[cn_df['Gene'].isin(gene_list)][['Gene', cell_line]]
    cn_subset.columns = ['Gene', 'Copy Number']

    # Merge dataframes and clearly indicate missing values
    final_df = pd.merge(gene_data, cn_subset, on='Gene', how='left').fillna('N/A')

    # Improved highlighting for copy numbers
    def highlight_copy_number(val):
        try:
            val_float = float(val)
            if val_float > 5:
                color = '#FF6666'  # Strong Red for high values
            elif val_float < 2:
                color = '#66CC66'  # Strong Green for low values
            else:
                color = '#FFDD44'  # Yellow for intermediate
            return f'background-color: {color}; color: black'
        except:
            return 'background-color: #EEEEEE; color: #AAAAAA'  # Grey for N/A

    styled_df = final_df[['Gene', 'Adjusted TSS', 'Copy Number']].style.applymap(
        highlight_copy_number, subset=['Copy Number']
    ).set_properties(**{
        'border': '1px solid black',
        'padding': '6px',
        'text-align': 'center'
    })

    # Display final dataframe with attractive formatting
    st.subheader("📌 Results:")
    st.dataframe(styled_df, use_container_width=True, height=500)

    # Offer CSV download option for convenience
    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Download Results as CSV",
        csv,
        "gene_results.csv",
        "text/csv",
        key='download-csv'
    )
else:
    st.info("ℹ️ Awaiting your input. Enter genes, select a cell line, then hit **Process**!")

# Footer
st.markdown("---")
st.markdown("🔗 [Prekovic Lab Website](https://www.prekovic-lab.org/) | ✉️ [Contact](mailto:s.prekovic@umcutrecht.nl)")
