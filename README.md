# Cellar V — Business Health Dashboard

Analytics App submission for the Quantic MSBA **Communicating with Data** project.

**Stakeholders:** Cellar V's owner and its investors (cellar-v.com.sg, a Singapore wine bar & retail shop).
**Decision:** where to focus limited time/capital next across the whole business — tightening
in-person discount/margin discipline, growing membership, or fixing the dormant online channel.
**Data:**
- In-person POS sales reports, full year 2025 plus 2026 year-to-date through 2026-08-17
  (`data/raw/sales_report_2025.csv`, `sales_report_2026.csv`), combined into clean `data/pos_*.csv` /
  `pos_summary.json` / `pos_by_year.json` files by `data/build_data.py`.
- Cellar V Shopify Admin API (online products, orders, customers, monthly sales), pulled 2026-08-11.

Order/customer records from the online store are anonymized — no real names or emails — since this
may be shared publicly for grading. **Note:** the POS data does include real revenue, profit, and
discount figures for the business — worth reviewing before making the deployed link/repo public if
you'd rather not disclose those.

## Run it locally

```bash
cd cellar-v-dashboard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`.

To refresh the POS-derived files after updating the raw exports in `data/raw/`:

```bash
python3 data/build_data.py
```

## What's inside

- `app.py` — the Streamlit dashboard, 6 tabs: The Full Picture, Where the Money Comes From,
  Margin & Membership, Online Channel, Recommendation, Assumptions & Limitations
- `data/raw/` — the original POS exports (product list, 2025 sales report, 2026 sales report) as downloaded
- `data/build_data.py` — parses and combines both years' sales reports into the clean `pos_*` files below
- `data/pos_summary.json` — combined top-line POS KPIs (gross/net/total sales, profit, transactions, etc.)
- `data/pos_by_year.json` — the same KPIs broken out separately by year, for the year-over-year view
- `data/pos_category_sales.csv`, `pos_top_products.csv`, `pos_discounts.csv`, `pos_payment_methods.csv`,
  `pos_catalog_composition.csv` — derived POS breakdowns
- `data/products.csv`, `orders.csv`, `monthly_sales.csv`, `customers_summary.csv` — the online
  (Shopify) side, from the earlier analysis

## The headline finding

The physical wine bar is a real, healthy business — **SGD 293,467 in sales across 2,363 transactions**
from January 2025 through August 2026 (about SGD 494/day), with a **65% gross margin** on net sales —
while the online Shopify store's entire **3-year revenue history (SGD 176)** is less than half of one
average day's in-person sales. The bigger levers are **in-person discount discipline** (SGD 66,613
given away, 19.8% of gross sales — consistent in both 2025 and 2026 separately — concentrated in
Liquor and Champagne/Sparkling) and **membership conversion** (members spend 2.5× more per item, but
only 41 people signed up as members across the full period). Fixing the online store's stock-outs is
still worth doing — just not first.

Submission Process

- Pushed this folder to a public GitHub repo.
- Recorded the 5-10 min presentation walking through the dashboard and the recommendation.
- Include a link to the deployed app (or repo) in the submitted PDF, per the assignment's Submission & Grading section.
