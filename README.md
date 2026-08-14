# Cellar V — Online Store Health Dashboard

Analytics App submission for the Quantic MSBA **Communicating with Data** project.

**Stakeholder:** Andre, owner of Cellar V (cellar-v.com.sg), a Singapore wine bar & retail shop.
**Decision:** where to focus limited time/budget first — fixing the catalog/inventory, or paying for more traffic — to get the online store converting again.
**Data:** pulled live from the Cellar V Shopify Admin API on 2026-08-11 (products, orders, customers, monthly sales). Order and customer records are anonymized — no real names or emails — since this may be shared publicly for grading.

## Run it locally

```bash
cd cellar-v-dashboard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`.

## What's inside

- `app.py` — the Streamlit dashboard (4 tabs: The Problem, Catalog & Inventory, Recommendation, Assumptions & Limitations)
- `data/products.csv` — full live product catalog (70 SKUs minus one test/draft listing), with price, inventory, tags
- `data/orders.csv` — the store's 2 lifetime online orders (customer names anonymized)
- `data/monthly_sales.csv` — 37 months of online sales totals
- `data/customers_summary.csv` — customer signups vs. customers who ever purchased, by month

## The headline finding

Cellar V's Shopify store has converted **2 online orders (SGD 176) in 3 years**, with nothing
in the last 551 days, while **44% of its 64 active product listings are out of stock** —
including a quarter of the SKUs it tags as "Best seller." The dashboard argues for fixing
availability before spending on ads to drive more traffic.

## Next steps for submission

- Deploy to [Streamlit Community Cloud](https://streamlit.io/cloud) for a public link (preferred by the rubric), or push this folder to a public GitHub repo.
- Record the 5-10 min presentation walking through the dashboard and the recommendation.
- Include a link to the deployed app (or repo) in the submitted PDF, per the assignment's Submission & Grading section.
