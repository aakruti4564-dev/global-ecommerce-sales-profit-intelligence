"""
IBM SkillsBuild / BharatCares Final Project
Project: Global E-Commerce Sales & Profit Intelligence

Run:
    python project.py

The script accepts a local `global_ecommerce_sales.csv`.
If the file is not present, it attempts to download a public mirror of the
same dataset. For the final submission, it is safer to download the dataset
yourself from Kaggle and keep the CSV beside this script.

Outputs are written to ./outputs/
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "global_ecommerce_sales.csv"
OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

KAGGLE_URL = "https://www.kaggle.com/datasets/muhammadaammartufail/global-e-commerce-sales-and-customer-data"
RAW_MIRROR = "https://raw.githubusercontent.com/ester-oborges/global_ecommerce_dashboard/main/global_ecommerce_sales.csv"

EXPECTED_COLUMNS = [
    "Order_ID", "Order_Date", "Customer_Name", "Customer_Segment",
    "Country", "Region", "Product_Category", "Product_Name", "Quantity",
    "Unit_Price", "Discount_Percent", "Total_Sales", "Shipping_Cost",
    "Profit", "Payment_Method"
]

def load_data():
    if not DATA_FILE.exists():
        try:
            import urllib.request
            urllib.request.urlretrieve(RAW_MIRROR, DATA_FILE)
        except Exception as exc:
            raise FileNotFoundError(
                "Dataset not found. Download the Kaggle dataset and save it as "
                f"'{DATA_FILE.name}' beside project.py. Kaggle source: {KAGGLE_URL}"
            ) from exc

    df = pd.read_csv(DATA_FILE)
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")
    return df

def clean_data(df):
    df = df.copy()
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    numeric_cols = [
        "Quantity", "Unit_Price", "Discount_Percent",
        "Total_Sales", "Shipping_Cost", "Profit"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove exact duplicates.
    before = len(df)
    df = df.drop_duplicates()
    duplicates_removed = before - len(df)

    # Remove rows where critical analytical fields are unavailable.
    critical = ["Order_ID", "Order_Date", "Product_Category", "Region",
                "Total_Sales", "Profit"]
    missing_before = int(df[critical].isna().sum().sum())
    df = df.dropna(subset=critical)

    # Keep values in sensible business ranges.
    df = df[df["Quantity"] > 0]
    df = df[df["Unit_Price"] >= 0]
    df = df[df["Discount_Percent"].between(0, 100)]

    # Derived fields.
    df["Year"] = df["Order_Date"].dt.year
    df["Month"] = df["Order_Date"].dt.month
    df["Month_Name"] = df["Order_Date"].dt.strftime("%b")
    df["Quarter"] = "Q" + df["Order_Date"].dt.quarter.astype(str)
    df["Profit_Margin_%"] = np.where(
        df["Total_Sales"] != 0,
        df["Profit"] / df["Total_Sales"] * 100,
        np.nan
    )
    df["Shipping_%_of_Sales"] = np.where(
        df["Total_Sales"] != 0,
        df["Shipping_Cost"] / df["Total_Sales"] * 100,
        np.nan
    )

    quality = {
        "rows_original": before,
        "duplicate_rows_removed": duplicates_removed,
        "critical_missing_values_removed": missing_before,
        "rows_after_cleaning": len(df),
    }
    return df, quality

def create_summaries(df):
    total_sales = df["Total_Sales"].sum()
    total_profit = df["Profit"].sum()
    orders = df["Order_ID"].nunique()
    customers = df["Customer_Name"].nunique()
    units = df["Quantity"].sum()

    kpis = pd.DataFrame({
        "KPI": [
            "Total Sales", "Total Profit", "Profit Margin %",
            "Orders", "Unique Customers", "Units Sold",
            "Average Order Value", "Average Discount %",
            "Total Shipping Cost", "Loss-Making Orders"
        ],
        "Value": [
            total_sales, total_profit,
            (total_profit / total_sales * 100) if total_sales else np.nan,
            orders, customers, units,
            total_sales / orders if orders else np.nan,
            df["Discount_Percent"].mean(),
            df["Shipping_Cost"].sum(),
            int((df["Profit"] < 0).sum())
        ]
    })
    kpis.to_csv(OUTPUT_DIR / "kpi_summary.csv", index=False)

    category = (
        df.groupby("Product_Category", as_index=False)
        .agg(
            Orders=("Order_ID", "nunique"),
            Units=("Quantity", "sum"),
            Sales=("Total_Sales", "sum"),
            Profit=("Profit", "sum"),
            Avg_Discount=("Discount_Percent", "mean"),
            Shipping_Cost=("Shipping_Cost", "sum")
        )
    )
    category["Profit_Margin_%"] = category["Profit"] / category["Sales"] * 100
    category["Sales_Share_%"] = category["Sales"] / total_sales * 100
    category.sort_values("Profit", ascending=False).to_csv(
        OUTPUT_DIR / "category_summary.csv", index=False
    )

    region = (
        df.groupby(["Region"], as_index=False)
        .agg(
            Orders=("Order_ID", "nunique"),
            Customers=("Customer_Name", "nunique"),
            Sales=("Total_Sales", "sum"),
            Profit=("Profit", "sum"),
            Shipping_Cost=("Shipping_Cost", "sum"),
            Avg_Discount=("Discount_Percent", "mean")
        )
    )
    region["Profit_Margin_%"] = region["Profit"] / region["Sales"] * 100
    region["Shipping_%_of_Sales"] = region["Shipping_Cost"] / region["Sales"] * 100
    region.sort_values("Profit", ascending=False).to_csv(
        OUTPUT_DIR / "region_summary.csv", index=False
    )

    segment = (
        df.groupby("Customer_Segment", as_index=False)
        .agg(
            Orders=("Order_ID", "nunique"),
            Customers=("Customer_Name", "nunique"),
            Sales=("Total_Sales", "sum"),
            Profit=("Profit", "sum"),
            Avg_Discount=("Discount_Percent", "mean")
        )
    )
    segment["Profit_Margin_%"] = segment["Profit"] / segment["Sales"] * 100
    segment.to_csv(OUTPUT_DIR / "segment_summary.csv", index=False)

    # Create an explicit month column before grouping.
    # This avoids the pandas FutureWarning/KeyError caused by grouping
    # directly on df["Order_Date"].dt.to_period("M").
    df["Order_Month"] = df["Order_Date"].dt.to_period("M")

    monthly = (
        df.groupby("Order_Month", as_index=False)
        .agg(
            Orders=("Order_ID", "nunique"),
            Sales=("Total_Sales", "sum"),
            Profit=("Profit", "sum"),
            Units=("Quantity", "sum")
        )
    )
    monthly["Month"] = monthly["Order_Month"].astype(str)
    monthly = monthly.drop(columns=["Order_Month"])
    monthly.to_csv(OUTPUT_DIR / "monthly_summary.csv", index=False)

    product = (
        df.groupby(["Product_Name", "Product_Category"], as_index=False)
        .agg(
            Orders=("Order_ID", "nunique"),
            Units=("Quantity", "sum"),
            Sales=("Total_Sales", "sum"),
            Profit=("Profit", "sum"),
            Avg_Discount=("Discount_Percent", "mean")
        )
    )
    product["Profit_Margin_%"] = product["Profit"] / product["Sales"] * 100
    product.sort_values("Profit", ascending=False).to_csv(
        OUTPUT_DIR / "product_summary.csv", index=False
    )

    return kpis, category, region, segment, monthly, product

def make_charts(df, category, region, monthly):
    plt.figure(figsize=(10, 5))
    plt.plot(monthly["Month"], monthly["Sales"], marker="o")
    plt.title("Monthly Sales Trend")
    plt.xlabel("Month")
    plt.ylabel("Sales (USD)")
    plt.xticks(rotation=60, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "monthly_sales_trend.png", dpi=160)
    plt.close()

    plt.figure(figsize=(9, 5))
    x = category.sort_values("Sales", ascending=False)
    plt.bar(x["Product_Category"], x["Sales"])
    plt.title("Sales by Product Category")
    plt.xlabel("Category")
    plt.ylabel("Sales (USD)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "category_sales.png", dpi=160)
    plt.close()

    plt.figure(figsize=(9, 5))
    x = region.sort_values("Profit", ascending=False)
    plt.bar(x["Region"], x["Profit"])
    plt.title("Profit by Region")
    plt.xlabel("Region")
    plt.ylabel("Profit (USD)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "region_profit.png", dpi=160)
    plt.close()

def generate_insights(kpis, category, region, segment, monthly, product, quality):
    def val(name):
        return float(kpis.loc[kpis["KPI"] == name, "Value"].iloc[0])

    top_cat = category.loc[category["Profit"].idxmax()]
    low_margin_cat = category.loc[category["Profit_Margin_%"].idxmin()]
    top_region = region.loc[region["Profit"].idxmax()]
    high_shipping_region = region.loc[region["Shipping_%_of_Sales"].idxmax()]
    top_segment = segment.loc[segment["Profit"].idxmax()]
    best_month = monthly.loc[monthly["Profit"].idxmax()]
    worst_month = monthly.loc[monthly["Profit"].idxmin()]

    lines = [
        "GLOBAL E-COMMERCE SALES & PROFIT INTELLIGENCE",
        "",
        "DATA QUALITY",
        f"Original rows: {quality['rows_original']}",
        f"Duplicate rows removed: {quality['duplicate_rows_removed']}",
        f"Rows after cleaning: {quality['rows_after_cleaning']}",
        "",
        "EXECUTIVE KPIs",
        f"Total Sales: ${val('Total Sales'):,.2f}",
        f"Total Profit: ${val('Total Profit'):,.2f}",
        f"Profit Margin: {val('Profit Margin %'):.2f}%",
        f"Orders: {val('Orders'):,.0f}",
        f"Unique Customers: {val('Unique Customers'):,.0f}",
        f"Units Sold: {val('Units Sold'):,.0f}",
        f"Average Order Value: ${val('Average Order Value'):,.2f}",
        f"Average Discount: {val('Average Discount %'):.2f}%",
        f"Loss-Making Orders: {val('Loss-Making Orders'):,.0f}",
        "",
        "BUSINESS INSIGHTS",
        f"1. Highest-profit category: {top_cat['Product_Category']} "
        f"(${top_cat['Profit']:,.2f} profit; {top_cat['Profit_Margin_%']:.2f}% margin).",
        f"2. Lowest category profit margin: {low_margin_cat['Product_Category']} "
        f"({low_margin_cat['Profit_Margin_%']:.2f}%).",
        f"3. Highest-profit region: {top_region['Region']} "
        f"(${top_region['Profit']:,.2f}).",
        f"4. Highest shipping-cost burden: {high_shipping_region['Region']} "
        f"({high_shipping_region['Shipping_%_of_Sales']:.2f}% of sales).",
        f"5. Highest-profit customer segment: {top_segment['Customer_Segment']} "
        f"(${top_segment['Profit']:,.2f}).",
        f"6. Highest-profit month: {best_month['Month']} "
        f"(${best_month['Profit']:,.2f}).",
        f"7. Lowest-profit month: {worst_month['Month']} "
        f"(${worst_month['Profit']:,.2f}).",
        "",
        "RECOMMENDED ACTIONS",
        "- Protect profitable categories and regions while checking whether growth is sustainable.",
        "- Investigate categories with low profit margin rather than optimizing sales volume alone.",
        "- Review shipping-cost burden in high-cost regions.",
        "- Use discount analysis to identify cases where discounts reduce margin without enough volume benefit.",
        "- Segment customers and prioritize retention/upsell based on profitability and purchase frequency.",
    ]
    (OUTPUT_DIR / "final_insights.txt").write_text("\n".join(lines), encoding="utf-8")

def create_html_dashboard(kpis, category, region, monthly):
    k = {r.KPI: r.Value for r in kpis.itertuples()}
    cat_rows = category.sort_values("Profit", ascending=False).to_dict("records")
    reg_rows = region.sort_values("Profit", ascending=False).to_dict("records")
    mon_rows = monthly.to_dict("records")

    def money(x):
        return f"${x:,.2f}"
    cards = f"""
    <div class="cards">
      <div class="card"><b>Total Sales</b><span>{money(k['Total Sales'])}</span></div>
      <div class="card"><b>Total Profit</b><span>{money(k['Total Profit'])}</span></div>
      <div class="card"><b>Profit Margin</b><span>{k['Profit Margin %']:.2f}%</span></div>
      <div class="card"><b>Orders</b><span>{int(k['Orders']):,}</span></div>
      <div class="card"><b>Customers</b><span>{int(k['Unique Customers']):,}</span></div>
    </div>
    """

    def table(rows, fields):
        head = "".join(f"<th>{f}</th>" for f in fields)
        body = ""
        for r in rows:
            body += "<tr>" + "".join(
                f"<td>{r.get(f, '') if not isinstance(r.get(f, ''), (float, np.floating)) else f'{r[f]:,.2f}'}</td>"
                for f in fields
            ) + "</tr>"
        return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Global E-Commerce Intelligence</title>
<style>
body{{font-family:Arial,sans-serif;background:#f5f7fb;margin:0;color:#1f2937}}
header{{background:#111827;color:white;padding:28px 40px}}
main{{padding:28px 40px;max-width:1200px;margin:auto}}
.cards{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px}}
.card{{background:white;border-radius:12px;padding:18px;box-shadow:0 2px 8px #0001}}
.card b{{display:block;color:#6b7280;font-size:13px;margin-bottom:8px}}
.card span{{font-size:24px;font-weight:700}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:22px}}
.panel{{background:white;border-radius:12px;padding:20px;box-shadow:0 2px 8px #0001}}
img{{width:100%;border-radius:8px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th,td{{padding:8px;border-bottom:1px solid #e5e7eb;text-align:left}}
</style></head>
<body>
<header><h1>Global E-Commerce Sales & Profit Intelligence</h1>
<p>IBM SkillsBuild / BharatCares final project</p></header>
<main>
{cards}
<div class="grid">
<div class="panel"><h2>Monthly Sales</h2><img src="monthly_sales_trend.png"></div>
<div class="panel"><h2>Sales by Category</h2><img src="category_sales.png"></div>
<div class="panel"><h2>Profit by Region</h2><img src="region_profit.png"></div>
<div class="panel"><h2>Executive Interpretation</h2>
<p>Use this dashboard to identify performance, drivers, risks and opportunities. 
The detailed recommendations are in <code>final_insights.txt</code>.</p></div>
</div>
<div class="panel" style="margin-top:22px"><h2>Category Analysis</h2>
{table(cat_rows, ['Product_Category','Orders','Sales','Profit','Profit_Margin_%'])}</div>
<div class="panel" style="margin-top:22px"><h2>Regional Analysis</h2>
{table(reg_rows, ['Region','Orders','Sales','Profit','Profit_Margin_%','Shipping_%_of_Sales'])}</div>
</main></body></html>"""
    (OUTPUT_DIR / "dashboard.html").write_text(html, encoding="utf-8")

def main():
    df_raw = load_data()
    df, quality = clean_data(df_raw)
    kpis, category, region, segment, monthly, product = create_summaries(df)
    make_charts(df, category, region, monthly)
    generate_insights(kpis, category, region, segment, monthly, product, quality)
    create_html_dashboard(kpis, category, region, monthly)

    df.to_csv(OUTPUT_DIR / "cleaned_ecommerce_sales.csv", index=False)
    print("Project completed.")
    print(f"Outputs saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
