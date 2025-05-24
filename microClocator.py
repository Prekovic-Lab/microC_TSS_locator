import streamlit as st
import pandas as pd

# Streamlit page setup
st.set_page_config(page_title="Gene TSS Locator", layout="wide")

# Main title and description
st.title("🔬 Prekovic Lab Gene TSS Portal for MicroC")
st.markdown("""
Enter your gene list, select the desired cell line, and click **Process**.  
The output table provides clearly formatted Transcription Start Sites (TSS) and copy numbers.
""")

# Load copy number data from Dropbox (direct link)
cn_df = pd.read_csv(
    "https://www.dropbox.com/scl/fi/fpnvolwlhozzqyvu7qh3q/Omics_Absolute_CN_Gene_Public_24Q4_subsetted.csv?rlkey=tn5hwmm01u6ww29t2nv81cf54&st=rd7e84ex&dl=1"
)

# Load and filter mart data (Ensembl Canonical == 1)
mart_df = pd.read_csv("mart_export.txt", sep='\t')
mart_df = mart_df[mart_df["Ensembl Canonical"] == 1][['Gene name', 'Transcription start site (TSS)', 'Strand']].dropna()
mart_df.columns = ['Gene', 'TSS', 'Strand']

# Inputs clearly visible without sidebar
gene_input = st.text_area("📋 Paste your gene list (one gene per line):", height=200)
cell_line = st.selectbox("🧬 Select Cell Line:", cn_df.columns[1:])
process_button = st.button("🚀 Process")

# Process data after clicking the button
if process_button:
    gene_list = [gene.strip() for gene in gene_input.splitlines() if gene.strip()]
    
    # Match gene data from Mart export
    gene_data = mart_df[mart_df['Gene'].isin(gene_list)].copy()

    # Adjust TSS based on strand orientation
    gene_data['Adjusted TSS'] = gene_data.apply(
        lambda row: row['TSS'] if row['Strand'] == 1 else f"-{row['TSS']}", axis=1
    )

    # Retrieve copy numbers for selected cell line
    cn_subset = cn_df[cn_df['Gene'].isin(gene_list)][['Gene', cell_line]]
    cn_subset.columns = ['Gene', 'Copy Number']

    # Merge into one dataframe, clearly mark missing values
    final_df = pd.merge(gene_data, cn_subset, on='Gene', how='left').fillna('N/A')

    # Color highlighting based on copy number
    def highlight_copy_number(val):
        try:
            val_float = float(val)
            if val_float > 5:
                color = '#FF6666'  # High: Red
            elif val_float < 2:
                color = '#66CC66'  # Low: Green
            else:
                color = '#FFDD44'  # Intermediate: Yellow
            return f'background-color: {color}; color: black'
        except:
            return 'background-color: #DDDDDD; color: #666666'  # N/A: Grey

    # Styling dataframe
    styled_df = final_df[['Gene', 'Adjusted TSS', 'Copy Number']].style.applymap(
        highlight_copy_number, subset=['Copy Number']
    ).set_properties(**{
        'border': '1px solid #888888',
        'padding': '6px',
        'text-align': 'center'
    })

    # Display styled dataframe
    st.subheader("📌 Results")
    st.dataframe(styled_df, use_container_width=True, height=500)

    # Provide CSV download
    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Results as CSV",
        data=csv,
        file_name="gene_results.csv",
        mime="text/csv"
    )

else:
    st.info("ℹ️ Please input your gene list, select a cell line, and click **Process**.")

# Footer
st.markdown("---")
st.markdown("🔗 [Prekovic Lab](https://www.prekovic-lab.org/) | ✉️ [Contact](mailto:s.prekovic@umcutrecht.nl)")
