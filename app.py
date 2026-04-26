from flask import Flask, jsonify, request, render_template, send_file
import pandas as pd
from fpdf import FPDF
import os, io
from datetime import date

app = Flask(__name__)

def load_data():
    df = pd.read_csv("data.csv")
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month"]      = df["order_date"].dt.to_period("M")
    df["quarter"]    = df["order_date"].dt.to_period("Q")
    return df

def filter_df(df, start="2025-01-01", end="2025-12-31"):
    mask = (df["order_date"] >= pd.to_datetime(start)) & (df["order_date"] <= pd.to_datetime(end))
    return df[mask].copy()

@app.route("/")
def index():
    return render_template("index.html")

# ── KPIs (filterable) ─────────────────────────────────────
@app.route("/api/kpis")
def kpis():
    df = filter_df(load_data(), request.args.get("start_date","2025-01-01"), request.args.get("end_date","2025-12-31"))
    return jsonify({
        "total_sales":      round(float(df["total_price"].sum()), 2),
        "total_orders":     int(len(df)),
        "avg_order_value":  round(float(df["total_price"].mean()), 2) if len(df) else 0,
        "unique_customers": int(df["customer_id"].nunique()),
    })

# ── Monthly Sales ─────────────────────────────────────────
@app.route("/api/sales_by_month")
def sales_by_month():
    df = filter_df(load_data(), request.args.get("start_date","2025-01-01"), request.args.get("end_date","2025-12-31"))
    monthly = df.groupby("month")["total_price"].sum().reset_index()
    monthly["month"] = monthly["month"].astype(str)
    return jsonify({"labels": monthly["month"].tolist(), "values": [round(v,2) for v in monthly["total_price"].tolist()]})

# ── Quarterly Sales ───────────────────────────────────────
@app.route("/api/sales_by_quarter")
def sales_by_quarter():
    df = filter_df(load_data(), request.args.get("start_date","2025-01-01"), request.args.get("end_date","2025-12-31"))
    q = df.groupby("quarter")["total_price"].sum().reset_index()
    q["quarter"] = q["quarter"].astype(str)
    return jsonify({"labels": q["quarter"].tolist(), "values": [round(v,2) for v in q["total_price"].tolist()]})

# ── Category Sales ────────────────────────────────────────
@app.route("/api/top_products")
def top_products():
    df = filter_df(load_data(), request.args.get("start_date","2025-01-01"), request.args.get("end_date","2025-12-31"))
    top = df.groupby("product_category")["total_price"].sum().sort_values(ascending=False).reset_index()
    return jsonify({"labels": top["product_category"].tolist(), "values": [round(v,2) for v in top["total_price"].tolist()]})

# ── Top 5 Products Detail ─────────────────────────────────
@app.route("/api/top_products_detail")
def top_products_detail():
    df = filter_df(load_data(), request.args.get("start_date","2025-01-01"), request.args.get("end_date","2025-12-31"))
    top = df.groupby("product_name")["total_price"].sum().sort_values(ascending=False).head(5).reset_index()
    return jsonify({"labels": top["product_name"].tolist(), "values": [round(v,2) for v in top["total_price"].tolist()]})

# ── Report ────────────────────────────────────────────────
@app.route("/api/generate_report")
def generate_report():
    start_date = request.args.get("start_date", "2025-01-01")
    end_date   = request.args.get("end_date",   "2025-12-31")
    fmt        = request.args.get("format",     "csv")

    df       = load_data()
    filtered = filter_df(df, start_date, end_date)

    if len(filtered) == 0:
        return jsonify({"error": "No data found for selected date range"}), 404

    total_sales      = round(float(filtered["total_price"].sum()), 2)
    total_orders     = int(len(filtered))
    avg_order_value  = round(float(filtered["total_price"].mean()), 2)
    unique_customers = int(filtered["customer_id"].nunique())

    cat_summary = filtered.groupby("product_category")["total_price"].sum().sort_values(ascending=False).reset_index()

    # ── PREVIEW ───────────────────────────────────────────
    if fmt == "preview":
        return jsonify({
            "total_sales":      total_sales,
            "total_orders":     total_orders,
            "avg_order_value":  avg_order_value,
            "unique_customers": unique_customers,
            "top_category":     filtered.groupby("product_category")["total_price"].sum().idxmax(),
            "num_categories":   int(filtered["product_category"].nunique()),
            "category_breakdown": cat_summary.rename(columns={"total_price":"total_price","product_category":"product_category"}).to_dict(orient="records"),
        })

    # ── CSV ───────────────────────────────────────────────
    if fmt == "csv":
        output = io.StringIO()
        output.write(f"E-Commerce Sales Report\n")
        output.write(f"Period: {start_date} to {end_date}\n")
        output.write(f"Generated: {date.today()}\n\n")
        output.write(f"SUMMARY\n")
        output.write(f"Total Sales,Rs. {total_sales:,.2f}\n")
        output.write(f"Total Orders,{total_orders}\n")
        output.write(f"Average Order Value,Rs. {avg_order_value:,.2f}\n")
        output.write(f"Unique Customers,{unique_customers}\n\n")
        output.write("SALES BY CATEGORY\n")
        cat_summary.to_csv(output, index=False)
        output.write("\nDETAILED ORDERS\n")
        filtered[["order_id","customer_id","product_name","product_category","order_date","quantity","unit_price","total_price"]].to_csv(output, index=False)
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()), mimetype="text/csv", as_attachment=True,
                         download_name=f"sales_report_{start_date}_to_{end_date}.csv")

    # ── PDF ───────────────────────────────────────────────
    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_font("Arial","B",20)
    pdf.set_fill_color(41,37,36); pdf.set_text_color(255,255,255)
    pdf.cell(0,15,"E-Commerce Sales Insights Report",ln=True,align="C",fill=True)
    pdf.ln(3)

    # Date printed + period
    pdf.set_font("Arial","",10); pdf.set_text_color(107,114,128)
    pdf.cell(0,7,f"Report Period: {start_date}  to  {end_date}",ln=True,align="C")
    pdf.cell(0,7,f"Generated on: {date.today().strftime('%d %B %Y')}",ln=True,align="C")
    pdf.ln(6)

    # KPIs
    pdf.set_font("Arial","B",14); pdf.set_text_color(0,0,0)
    pdf.cell(0,10,"Key Performance Indicators",ln=True)
    pdf.set_draw_color(79,70,229); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(4)
    kpis_list=[("Total Sales",f"Rs. {total_sales:,.2f}"),("Total Orders",str(total_orders)),
               ("Average Order Value",f"Rs. {avg_order_value:,.2f}"),("Unique Customers",str(unique_customers))]
    pdf.set_font("Arial","",12)
    for label,value in kpis_list:
        pdf.set_fill_color(242,247,244)
        pdf.cell(95,10,f"  {label}",border=0,fill=True)
        pdf.set_font("Arial","B",12); pdf.cell(95,10,value,border=0,fill=True,ln=True)
        pdf.set_font("Arial","",12); pdf.ln(1)

    # Category breakdown
    pdf.set_font("Arial","B",14); pdf.cell(0,10,"Sales by Category",ln=True)
    pdf.set_draw_color(79,70,229); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(4)
    pdf.set_font("Arial","B",11); pdf.set_fill_color(41,37,36); pdf.set_text_color(229,231,235)
    pdf.cell(95,9,"Category",fill=True); pdf.cell(95,9,"Total Sales",fill=True,ln=True)
    pdf.set_text_color(0,0,0); pdf.set_font("Arial","",11); fill=False
    for _,row in cat_summary.iterrows():
        pdf.set_fill_color(242,247,244) if fill else pdf.set_fill_color(255,255,255)
        pdf.cell(95,9,str(row["product_category"]),fill=True)
        pdf.cell(95,9,f"Rs. {row['total_price']:,.2f}",fill=True,ln=True)
        fill=not fill

    # Dashboard charts
    pdf.ln(6)
    pdf.set_font("Arial","B",14); pdf.set_text_color(0,0,0)
    pdf.cell(0,10,"Dashboard Charts",ln=True)
    pdf.set_draw_color(79,70,229); pdf.line(10,pdf.get_y(),200,pdf.get_y()); pdf.ln(4)
    chart_files=[
        ("static/charts/monthly_sales.png","Monthly Sales Trend"),
        ("static/charts/category_sales.png","Sales by Category"),
        ("static/charts/top_products.png","Top Products"),
        ("static/charts/quarterly_sales.png","Quarterly Sales"),
    ]
    for path, title in chart_files:
        if os.path.exists(path):
            pdf.set_font("Arial","B",11); pdf.cell(0,8,title,ln=True)
            pdf.image(path, x=10, w=190); pdf.ln(4)

    # Footer
    pdf.set_font("Arial","I",9); pdf.set_text_color(168,162,158)
    pdf.cell(0,10,"Generated by E-Commerce Sales Insights Dashboard",align="C",ln=True)

    pdf_path=f"report_{start_date}_to_{end_date}.pdf"
    pdf.output(pdf_path)
    return send_file(pdf_path, mimetype="application/pdf", as_attachment=True,
                     download_name=f"sales_report_{start_date}_to_{end_date}.pdf")

if __name__ == "__main__":
    app.run(debug=True)