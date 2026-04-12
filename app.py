from flask import Flask, jsonify, request, render_template, send_file
import pandas as pd
from fpdf import FPDF
import os
import io

app = Flask(__name__)

# ══════════════════════════════════════════════════════════
# LOAD & PREPARE DATA
# ══════════════════════════════════════════════════════════

def load_data():
    df = pd.read_csv("data.csv")
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month"]      = df["order_date"].dt.to_period("M")
    df["quarter"]    = df["order_date"].dt.to_period("Q")
    return df

# ══════════════════════════════════════════════════════════
# MAIN PAGE
# ══════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")

# ══════════════════════════════════════════════════════════
# API 1 — KPIs
# ══════════════════════════════════════════════════════════

@app.route("/api/kpis")
def kpis():
    df = load_data()
    data = {
        "total_sales":      round(float(df["total_price"].sum()), 2),
        "total_orders":     int(len(df)),
        "avg_order_value":  round(float(df["total_price"].mean()), 2),
        "unique_customers": int(df["customer_id"].nunique()),
    }
    return jsonify(data)

# ══════════════════════════════════════════════════════════
# API 2 — MONTHLY SALES
# ══════════════════════════════════════════════════════════

@app.route("/api/sales_by_month")
def sales_by_month():
    df = load_data()
    monthly = (
        df.groupby("month")["total_price"]
        .sum()
        .reset_index()
    )
    monthly["month"] = monthly["month"].astype(str)
    data = {
        "labels": monthly["month"].tolist(),
        "values": [round(v, 2) for v in monthly["total_price"].tolist()],
    }
    return jsonify(data)

# ══════════════════════════════════════════════════════════
# API 3 — TOP PRODUCTS
# ══════════════════════════════════════════════════════════

@app.route("/api/top_products")
def top_products():
    df = load_data()
    top = (
        df.groupby("product_category")["total_price"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    data = {
        "labels": top["product_category"].tolist(),
        "values": [round(v, 2) for v in top["total_price"].tolist()],
    }
    return jsonify(data)

# ══════════════════════════════════════════════════════════
# API 4 — TOP 5 PRODUCTS BY NAME
# ══════════════════════════════════════════════════════════

@app.route("/api/top_products_detail")
def top_products_detail():
    df = load_data()
    top = (
        df.groupby("product_name")["total_price"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )
    data = {
        "labels": top["product_name"].tolist(),
        "values": [round(v, 2) for v in top["total_price"].tolist()],
    }
    return jsonify(data)

# ══════════════════════════════════════════════════════════
# API 5 — QUARTERLY SALES
# ══════════════════════════════════════════════════════════

@app.route("/api/sales_by_quarter")
def sales_by_quarter():
    df = load_data()
    quarterly = (
        df.groupby("quarter")["total_price"]
        .sum()
        .reset_index()
    )
    quarterly["quarter"] = quarterly["quarter"].astype(str)
    data = {
        "labels": quarterly["quarter"].tolist(),
        "values": [round(v, 2) for v in quarterly["total_price"].tolist()],
    }
    return jsonify(data)

# ══════════════════════════════════════════════════════════
# API 6 — GENERATE REPORT (PDF or CSV)
# ══════════════════════════════════════════════════════════

@app.route("/api/generate_report")
def generate_report():
    df         = load_data()
    start_date = request.args.get("start_date", "2023-01-01")
    end_date   = request.args.get("end_date",   "2023-12-31")
    fmt        = request.args.get("format",     "csv")

    # Filter by date range
    mask = (
        (df["order_date"] >= pd.to_datetime(start_date)) &
        (df["order_date"] <= pd.to_datetime(end_date))
    )
    filtered = df[mask].copy()

    if len(filtered) == 0:
        return jsonify({"error": "No data found for selected date range"}), 404

    # ── KPIs for the filtered period ─────────────────────
    total_sales     = round(float(filtered["total_price"].sum()), 2)
    total_orders    = int(len(filtered))
    avg_order_value = round(float(filtered["total_price"].mean()), 2)
    unique_customers= int(filtered["customer_id"].nunique())

    # ── Category breakdown ────────────────────────────────
    cat_summary = (
        filtered.groupby("product_category")["total_price"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    # ════════════════════════════════════════════════════
    # CSV REPORT
    # ════════════════════════════════════════════════════
    if fmt == "csv":
        output = io.StringIO()
        output.write(f"E-Commerce Sales Report\n")
        output.write(f"Period: {start_date} to {end_date}\n\n")
        output.write(f"SUMMARY\n")
        output.write(f"Total Sales,${total_sales:,.2f}\n")
        output.write(f"Total Orders,{total_orders}\n")
        output.write(f"Average Order Value,${avg_order_value:,.2f}\n")
        output.write(f"Unique Customers,{unique_customers}\n\n")
        output.write(f"SALES BY CATEGORY\n")
        cat_summary.to_csv(output, index=False)
        output.write(f"\nDETAILED ORDERS\n")
        filtered[["order_id","customer_id","product_name",
                  "product_category","order_date",
                  "quantity","unit_price","total_price"]].to_csv(output, index=False)
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"sales_report_{start_date}_to_{end_date}.csv"
        )

    # ════════════════════════════════════════════════════
    # PDF REPORT
    # ════════════════════════════════════════════════════
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 20)
    pdf.set_fill_color(79, 70, 229)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, "E-Commerce Sales Insights Report", ln=True, align="C", fill=True)
    pdf.ln(3)

    # Period
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, f"Report Period: {start_date}  to  {end_date}", ln=True, align="C")
    pdf.ln(6)

    # KPI Section
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Key Performance Indicators", ln=True)
    pdf.set_draw_color(79, 70, 229)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    kpis_list = [
        ("Total Sales",         f"${total_sales:,.2f}"),
        ("Total Orders",        str(total_orders)),
        ("Average Order Value", f"${avg_order_value:,.2f}"),
        ("Unique Customers",    str(unique_customers)),
    ]

    pdf.set_font("Arial", "", 12)
    for label, value in kpis_list:
        pdf.set_fill_color(243, 244, 246)
        pdf.cell(95, 10, f"  {label}", border=0, fill=True)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(95, 10, value, border=0, fill=True, ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.ln(1)

    pdf.ln(6)

    # Category Breakdown
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Sales by Category", ln=True)
    pdf.set_draw_color(79, 70, 229)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_font("Arial", "B", 11)
    pdf.set_fill_color(79, 70, 229)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(95, 9, "Category", fill=True)
    pdf.cell(95, 9, "Total Sales", fill=True, ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 11)
    fill = False
    for _, row in cat_summary.iterrows():
        pdf.set_fill_color(243, 244, 246) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.cell(95, 9, str(row["product_category"]), fill=True)
        pdf.cell(95, 9, f"${row['total_price']:,.2f}", fill=True, ln=True)
        fill = not fill

    pdf.ln(6)

    # Footer
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "Generated by E-Commerce Sales Insights Dashboard", align="C", ln=True)

    # Save and send
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"sales_report_{start_date}_to_{end_date}.pdf"
    )

# ══════════════════════════════════════════════════════════
# RUN SERVER
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(debug=True)