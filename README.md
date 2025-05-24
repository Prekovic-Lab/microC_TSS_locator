# MicroC Finder 🔬

[![Open App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://microcfinder.streamlit.app/)

**MicroC Finder** is a streamlined web application developed specifically for the **Prekovic Lab**, designed for rapid retrieval and visualization of **Transcription Start Sites (TSS)** and **Absolute Copy Numbers** for user-provided genes across various cell lines.

---

## Features

- ** Easy Gene Input:** Directly paste lists of gene names.
- ** Cell Line Specificity:** Quickly select and analyze genes in chosen cell lines.
- ** Instant Results:** Obtain accurate TSS positions, genomic coordinates, and absolute copy numbers in seconds.
- ** Visual Identification:** Automatically highlights genes with significantly altered absolute copy numbers.

---

## Quick Start

1. **Paste** your gene list into the text box.
2. **Select** your desired cell line from the dropdown menu.
3. Click the **"Process"** button.
4. View and download your results instantly.

---

## Data Sources

- **Gene Coordinates:** Ensembl BioMart canonical transcript export.
- **Copy Number Data:** Public Omics absolute copy number datasets.

---

## Requirements

- Python ≥ 3.8
- Streamlit
- pandas

Install via:

```bash
pip install -r requirements.txt
