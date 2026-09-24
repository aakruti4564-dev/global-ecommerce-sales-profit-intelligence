# Global E-Commerce Sales & Profit Intelligence

**Student:** Aakruti Rakesh Yadav  
**Internship:** IBM SkillsBuild / BharatCares – Data Analytics with AI  
**Project type:** Business Intelligence / Data Analytics

## 1. Problem Statement

The objective is to transform global e-commerce transaction data into actionable business insights. The project evaluates sales, profitability, product categories, regions, customer segments, discounts and shipping costs so that decision-makers can identify performance drivers, risks, opportunities and possible actions.

## 2. Dataset

Selected dataset: **Global E-Commerce Sales & Customer Data**

Kaggle source:
https://www.kaggle.com/datasets/muhammadaammartufail/global-e-commerce-sales-and-customer-data

The public dataset contains 2,000 transactions from January 2023 to December 2025, 15 fields, 20 countries, 5 regions, 4 product categories and 3 customer segments. The dataset is synthetic and intended for educational/portfolio analysis.

## 3. Important note about the internship requirement

The internship session says the final project must use a new dataset and must NOT reuse the exact dataset used during the masterclasses. Verify that this dataset was not your masterclass learning dataset before submitting.

## 4. Business Questions

1. What are total sales, profit, orders and average order value?
2. Which product categories drive sales and profit?
3. Which regions generate the most profit?
4. Which regions have a high shipping-cost burden?
5. Which customer segment contributes the most profit?
6. How do sales and profit change over time?
7. Where are loss-making transactions concentrated?
8. How do discounts relate to profitability?
9. What actions should management consider?

## 5. KPIs

- Total Sales
- Total Profit
- Profit Margin %
- Orders
- Unique Customers
- Units Sold
- Average Order Value
- Average Discount %
- Total Shipping Cost
- Loss-Making Orders

## 6. Methodology

Raw data
→ data-quality checks
→ duplicate/missing-value handling
→ data-type conversion
→ feature engineering
→ KPI calculation
→ category/region/segment analysis
→ monthly trend analysis
→ business insights
→ recommended actions
→ dashboard/report

## 7. How to run

1. Download the CSV from the Kaggle source above.
2. Save it in the same folder as `project.py`.
3. Keep the filename exactly:
   `global_ecommerce_sales.csv`
4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Run:

```bash
python project.py
```

The script creates an `outputs/` folder containing:
- `cleaned_ecommerce_sales.csv`
- `kpi_summary.csv`
- `category_summary.csv`
- `region_summary.csv`
- `segment_summary.csv`
- `monthly_summary.csv`
- `product_summary.csv`
- `monthly_sales_trend.png`
- `category_sales.png`
- `region_profit.png`
- `dashboard.html`
- `final_insights.txt`

## 8. Final submission files

According to the internship session, the four main files are:

1. Project code: `.py` or `.ipynb`
2. `requirements.txt`
3. Project report: `.docx` or `.pdf`
4. `README.md`

You also need the **GitHub repository URL** in the submission form.

The session states that ZIP files are not accepted and that the dataset source link must be included in README.

## 9. GitHub structure

```text
global-ecommerce-project/
├── project.py
├── requirements.txt
├── README.md
└── Project_Report.pdf
```

The dataset itself is not one of the four required form uploads. If you put the CSV in GitHub, check the internship form instructions first; the meeting emphasized the four required files.

## 10. Important submission warning

The transcript does NOT contain the actual submission-form URL. The instructors said the form link would be shared through the WhatsApp group/resource document. Do not submit to an unverified link.

## 11. Expected business-story structure

Fact → Insight → Risk/Opportunity → Action.

The dashboard should not simply display many charts. It should make the important business message easy to understand.
