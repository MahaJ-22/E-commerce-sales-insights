# E-Commerce Sales Insights

A web-based Business Intelligence dashboard built for the TCS iON Industry Project. Analyzes 1,200 simulated e-commerce transactions and presents interactive visualizations, KPIs, and downloadable reports.

---

## Features

- Interactive dashboard with 4 Chart.js visualizations
- KPI cards: Total Sales, Orders, Average Order Value, Unique Customers
- Dynamic filtering by Quarter, Month, or custom date range
- PDF report generation (with embedded charts) and CSV export
- Report preview before download

---

## Project Structure

```
ecommerce-dashboard/
├── app.py                  # Flask backend + API endpoints
├── data.py                 # Synthetic dataset generator
├── data.csv                # Generated dataset (1,200 rows)
├── analysis.py             # EDA script (Matplotlib + Seaborn)
├── ecommerce_analysis.ipynb  # Jupyter Notebook for EDA
├── static/
│   └── charts/             # Saved chart images (used in PDF reports)
├── templates/
│   └── index.html          # Frontend dashboard
├── .gitignore
└── README.md
```

---

## Requirements

- Python 3.8+
- pip packages:

```
flask
pandas
matplotlib
seaborn
fpdf2
```

Install all dependencies:

```bash
pip install flask pandas matplotlib seaborn fpdf2
```

---

## How to Run

**1. Clone the repository**

```bash
git clone https://github.com/your-username/ecommerce-dashboard.git
cd ecommerce-dashboard
```

**2. (Optional) Generate the dataset**

The `data.csv` file is already included. To regenerate it:

```bash
python data.py
```

**3. (Optional) Run EDA and regenerate charts**

```bash
python analysis.py
```

Or open the Jupyter Notebook:

```bash
jupyter notebook ecommerce_analysis.ipynb
```

**4. Start the Flask server**

```bash
python app.py
```

**5. Open in browser**

```
http://127.0.0.1:5000
```

---

## API Endpoints

| Endpoint | Method | Parameters | Description |
|---|---|---|---|
| `/api/kpis` | GET | `start_date`, `end_date` | Returns KPI summary |
| `/api/sales_by_month` | GET | `start_date`, `end_date` | Monthly sales data |
| `/api/sales_by_quarter` | GET | `start_date`, `end_date` | Quarterly sales data |
| `/api/top_products` | GET | `start_date`, `end_date` | Sales by category |
| `/api/top_products_detail` | GET | `start_date`, `end_date` | Top 5 products by revenue |
| `/api/generate_report` | GET | `start_date`, `end_date`, `format` | Generate PDF or CSV report |

`format` accepts: `pdf`, `csv`, `preview`

---

## Dataset

Synthetically generated with `data.py`. Contains 1,200 rows covering Financial Year 2025.

| Column | Description |
|---|---|
| order_id | Unique order identifier |
| customer_id | Customer identifier |
| product_id | Product identifier |
| order_date | Date of order (2025) |
| product_name | Name of the product |
| product_category | Category (Electronics, Clothing, Home & Kitchen, Books, Sports) |
| quantity | Units ordered |
| unit_price | Price per unit |
| total_price | quantity × unit_price |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3 |
| Backend | Flask |
| Data Analysis | pandas, Matplotlib, Seaborn |
| Report Generation | FPDF2 (PDF), pandas (CSV) |
| Frontend | HTML, CSS, JavaScript |
| Charts | Chart.js |
| Notebook | Jupyter |
| Version Control | Git & GitHub |

---

## TCS iON Project

This project was developed as part of the TCS iON Industry Project program.  
All third-party libraries and tools retain their respective copyright ownership.
