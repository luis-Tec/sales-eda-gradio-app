<div align="right">
  <a href="README.md"><strong>English</strong></a> | <a href="README.es.md">Español</a>
</div>

# Interactive Sales EDA & Data Cleaning App (Python + Gradio)

A modular web application built with **Python, Pandas, Matplotlib, and Gradio** to automate data quality diagnostics, standardization/cleaning, exploratory data analysis (EDA), outlier detection, and validated record entry for retail sales datasets.

---

## Key Features

1. **Data Quality Diagnostics**
   - Automatic inspection of data types, missing/null counts, exact duplicates, and duplicate sale IDs.
   - Detection of logical inconsistencies (negative quantities/prices, unstandardized text, invalid dates).

2. **Automated Cleaning & Standardization**
   - Exact duplicate removal and sale ID deduplication.
   - Date conversion to **ISO 8601** (`YYYY-MM-DD`).
   - Negative value correction via absolute value and text normalization.
   - Imputation of missing numeric values (median) and categorical fields (`"Desconocido"`).

3. **Exploratory Analysis & Visualizations (6 Matplotlib Charts)**
   - Descriptive statistics (mean, median, min, max, mode).
   - Dynamic real-time filtering across any column.
   - Grouped aggregations by category, product, salesperson, region, payment method, and frequent-customer flag.
   - **Outlier Detection** using the **Interquartile Range (IQR)** method.
   - 6 analytical charts: Revenue by Category, Top 10 Products, Historical Sales Trend, Payment Method Distribution, Revenue by Region, and Salesperson Performance.

4. **Validated Data Entry & CSV Export**
   - Interactive form with field validation (dates, Costa Rica provinces, payment methods, positive numbers) and automatic sequential IDs.
   - One-click export of the cleaned and updated dataset to CSV.

---

## Tech Stack

- **Language:** Python 3.10+
- **Data Processing:** Pandas
- **Visualization:** Matplotlib
- **Web UI:** Gradio

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/luis-Tec/sales-eda-gradio-app.git
cd sales-eda-gradio-app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the Gradio app
python app.py
```

Open the local URL shown in your terminal (usually `http://127.0.0.1:7860`) and upload the sample dataset at `data/ventas_tienda_tecnologia_ampliado.csv` (or any compatible sales CSV).

---

## Repository Structure

```text
├── app.py                                      # Modular Gradio + Pandas + Matplotlib application
├── data/
│   └── ventas_tienda_tecnologia_ampliado.csv   # Sample technology store sales dataset
├── requirements.txt
└── .gitignore
```
