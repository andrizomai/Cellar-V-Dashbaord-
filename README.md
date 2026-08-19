# Cellar V — Business Health Dashboard

Analytics App submission for the Quantic MSBA **Communicating with Data** project.

**Stakeholder:** Andre, owner of Cellar V (cellar-v.com.sg), a Singapore wine bar & retail shop.
**Decision:** where to focus limited time/budget next across the whole business — tightening
in-person discount/margin discipline, growing membership, or fixing the dormant online channel.
**Data:**
- In-person POS sales report, 2026-01-01 to 2026-08-17 (`data/raw/sales_report.csv`), parsed into
  clean `data/pos_*.csv` / `data/pos_summary.json` files by `data/build_data.py`.
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
- `data/raw/` — the original POS exports (product list, sales report) as downloaded
- `data/build_data.py` — parses the raw sales report into the clean `pos_*` files below
- `data/pos_summary.json` — top-line POS KPIs (gross/net/total sales, profit, transactions, etc.)
- `data/pos_category_sales.csv`, `pos_top_products.csv`, `pos_discounts.csv`, `pos_payment_methods.csv`,
  `pos_catalog_composition.csv` — derived POS breakdowns
- `data/products.csv`, `orders.csv`, `monthly_sales.csv`, `customers_summary.csv` — the online
  (Shopify) side, from the earlier analysis

## The headline finding

The physical wine bar is a real, healthy business — **SGD 105,770 in sales across 807 transactions**
over 7.5 months (about SGD 462/day), with a **64.8% gross margin** on net sales — while the online
Shopify store's entire **3-year revenue history (SGD 176)** is less than half of one average day's
in-person sales. The bigger levers are **in-person discount discipline** (SGD 23,580 given away,
19.5% of gross sales, concentrated in Liquor and Champagne/Sparkling) and **membership conversion**
(members spend 2.2× more per item, but only 16 people signed up in 7.5 months). Fixing the online
store's stock-outs is still worth doing — just not first.

## Next steps for submission

- Deploy to [Streamlit Community Cloud](https://streamlit.io/cloud) for a public link (preferred by the rubric), or push this folder to a public GitHub repo.
- Record the 5-10 min presentation walking through the dashboard and the recommendation — the earlier `presentation/script.md` will need updating for the new narrative.
- Include a link to the deployed app (or repo) in the submitted PDF, per the assignment's Submission & Grading section.
