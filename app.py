"""
Cellar V — Online Store Health Dashboard
Communicating with Data (Analytics App path)

Stakeholder: Andre, owner of Cellar V (cellar-v.com.sg), a Singapore wine
bar & retail shop on Shopify.
Decision this dashboard supports: where to focus limited time and budget
first — fixing catalog/inventory gaps or driving new traffic — to get the
online store converting again.

Data: pulled live from the Cellar V Shopify Admin API (products, orders,
customers, sales) on 2026-08-11. Order/customer records are anonymized
(no real names or emails) since this app may be shared publicly for
grading. See the "Assumptions & Limitations" tab for caveats.
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"

# ---------------------------------------------------------------------------
# Palette (validated categorical + status colors)
# ---------------------------------------------------------------------------
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
MAGENTA, GREEN, VIOLET, RED = "#e87ba4", "#008300", "#4a3aa7", "#e34948"
STATUS_GOOD, STATUS_CRITICAL = "#0ca30c", "#d03b3b"
INK, INK_SECONDARY, MUTED, GRID = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
SURFACE = "#fcfcfb"

PLOTLY_LAYOUT = dict(
    font=dict(family="system-ui, -apple-system, 'Segoe UI', sans-serif", color=INK, size=13),
    plot_bgcolor=SURFACE,
    paper_bgcolor=SURFACE,
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(gridcolor=GRID, zerolinecolor=MUTED, linecolor=MUTED),
    yaxis=dict(gridcolor=GRID, zerolinecolor=MUTED, linecolor=MUTED),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    hoverlabel=dict(bgcolor="white", font_size=13),
)

st.set_page_config(page_title="Cellar V — Online Store Health", page_icon="🍷", layout="wide")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    products = pd.read_csv(DATA_DIR / "products.csv")
    products["is_bestseller"] = products["tags"].str.contains("Best seller")
    products["in_stock"] = products["inventory"] > 0
    bins = [0, 50, 70, 100, 150, 10_000]
    labels = ["<$50", "$50-70", "$70-100", "$100-150", "$150+"]
    products["price_tier"] = pd.cut(products["price_sgd"], bins=bins, labels=labels, right=False)

    orders = pd.read_csv(DATA_DIR / "orders.csv", parse_dates=["created_at"])
    monthly = pd.read_csv(DATA_DIR / "monthly_sales.csv", parse_dates=["month"])
    customers = pd.read_csv(DATA_DIR / "customers_summary.csv")
    return products, orders, monthly, customers


products, orders, monthly, customers = load_data()

active = products[products["status"] == "ACTIVE"].copy()
n_active = len(active)
n_oos = int((~active["in_stock"]).sum())
oos_rate = n_oos / n_active

bestsellers = active[active["is_bestseller"]]
n_bestsellers = len(bestsellers)
n_bestsellers_oos = int((~bestsellers["in_stock"]).sum())
bestseller_oos_rate = n_bestsellers_oos / n_bestsellers

lifetime_revenue = orders["total_price_sgd"].sum()
lifetime_orders = len(orders)
last_sale_date = orders["created_at"].max()
days_since_last_sale = (pd.Timestamp("2026-08-11") - last_sale_date).days

total_customers = customers["customers_signed_up"].sum()
customers_who_ordered = customers["customers_with_orders"].sum()
purchase_rate = customers_who_ordered / total_customers


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🍷 Cellar V — Online Store Health Dashboard")
st.caption(
    "Stakeholder: **Andre, owner of Cellar V** · Decision: where to focus limited time and "
    "budget first to get the online store converting again · Data pulled live from the "
    "Cellar V Shopify Admin API on **2026-08-11**"
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["📉 The Problem", "📦 Catalog & Inventory", "✅ Recommendation", "⚠️ Assumptions & Limitations"]
)

# ---------------------------------------------------------------------------
# TAB 1 — The Problem
# ---------------------------------------------------------------------------
with tab1:
    st.subheader("The online store has essentially stopped converting")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lifetime online revenue", f"SGD {lifetime_revenue:,.0f}")
    c2.metric("Lifetime online orders", f"{lifetime_orders}")
    c3.metric("Days since last online sale", f"{days_since_last_sale}")
    c4.metric("Registered customers who ever bought", f"{purchase_rate:.0%}", help=f"{customers_who_ordered} of {total_customers} accounts")

    st.markdown("##### Monthly online sales, last 3 years")
    fig = go.Figure()
    fig.add_bar(
        x=monthly["month"], y=monthly["total_sales_sgd"],
        marker_color=BLUE, name="Online sales (SGD)",
        hovertemplate="%{x|%b %Y}<br>SGD %{y:,.0f}<extra></extra>",
    )
    fig.update_layout(**PLOTLY_LAYOUT, height=360, yaxis_title="SGD", showlegend=False,
                       title="Two orders in 37 months — nothing since Feb 2025")
    st.plotly_chart(fig, use_container_width=True, theme=None)

    st.info(
        f"In 3 years of Shopify order history, Cellar V has recorded **{lifetime_orders} online orders** "
        f"totaling **SGD {lifetime_revenue:,.0f}**, both in early 2025. The store has not converted a single "
        f"online sale in the **{days_since_last_sale} days** since. Of the **{total_customers} customers** "
        f"who have created an account, only **{customers_who_ordered} ({purchase_rate:.0%})** have ever purchased — "
        f"the other {total_customers - customers_who_ordered} are dormant leads with zero follow-up conversion."
    )

# ---------------------------------------------------------------------------
# TAB 2 — Catalog & Inventory
# ---------------------------------------------------------------------------
with tab2:
    st.subheader("The catalog isn't the constraint — availability is")

    c1, c2, c3 = st.columns(3)
    c1.metric("Active SKUs listed", f"{n_active}")
    c2.metric("Active SKUs out of stock", f"{n_oos}", delta=f"{oos_rate:.0%} of catalog", delta_color="inverse")
    c3.metric("'Best seller'-tagged SKUs out of stock", f"{n_bestsellers_oos} of {n_bestsellers}",
              delta=f"{bestseller_oos_rate:.0%}", delta_color="inverse")

    left, right = st.columns(2)

    with left:
        st.markdown("##### Stock status by price tier")
        tier_status = (
            active.groupby(["price_tier", "in_stock"], observed=True).size()
            .reset_index(name="count")
        )
        tier_status["status"] = tier_status["in_stock"].map({True: "In stock", False: "Out of stock"})
        order = ["<$50", "$50-70", "$70-100", "$100-150", "$150+"]
        fig2 = px.bar(
            tier_status, x="price_tier", y="count", color="status",
            category_orders={"price_tier": order, "status": ["In stock", "Out of stock"]},
            color_discrete_map={"In stock": STATUS_GOOD, "Out of stock": STATUS_CRITICAL},
            labels={"price_tier": "Price tier", "count": "SKUs"},
        )
        fig2.update_traces(hovertemplate="%{x}<br>%{y} SKUs<extra></extra>")
        fig2.update_layout(**PLOTLY_LAYOUT, height=340, legend_title_text="")
        st.plotly_chart(fig2, use_container_width=True, theme=None)

    with right:
        st.markdown("##### Out-of-stock rate: best-sellers vs rest of catalog")
        cmp = pd.DataFrame({
            "group": ["Tagged 'Best seller'", "Rest of catalog"],
            "oos_rate": [
                bestseller_oos_rate,
                (n_oos - n_bestsellers_oos) / (n_active - n_bestsellers),
            ],
        })
        fig3 = px.bar(cmp, x="group", y="oos_rate", color="group",
                       color_discrete_map={"Tagged 'Best seller'": BLUE, "Rest of catalog": ORANGE})
        fig3.update_traces(hovertemplate="%{x}<br>%{y:.0%} out of stock<extra></extra>")
        fig3.update_layout(**PLOTLY_LAYOUT, height=340, yaxis_tickformat=".0%",
                            yaxis_title="Out-of-stock rate", xaxis_title="", showlegend=False)
        st.plotly_chart(fig3, use_container_width=True, theme=None)

    st.warning(
        f"**{n_bestsellers_oos} of {n_bestsellers}** products Cellar V itself tags as *'Best seller'* "
        f"currently show **zero inventory** — including flagship bottles like *Collefrisio Anniversary "
        f"Montepulciano* and *Collefrisio Confronto Gift Box Set*. A visitor who lands on a featured, "
        f"highly-tagged product has roughly a **1 in 4 chance** of hitting a page they can't buy from."
    )

# ---------------------------------------------------------------------------
# TAB 3 — Recommendation
# ---------------------------------------------------------------------------
with tab3:
    st.subheader("Recommendation")
    st.markdown(
        f"""
**Fix availability before spending on new traffic.**

- **What:** Restock or unpublish the **{n_bestsellers_oos} out-of-stock "Best seller"** SKUs first
  (they carry the tag customers are told to trust), then work down the remaining
  **{n_oos - n_bestsellers_oos}** out-of-stock active SKUs, prioritizing the **under-\\$50 / \\$50-70**
  tiers where Cellar V's only two real conversions (SGD 76 and SGD 100) actually happened.
- **Who:** Andre, as the person who controls both purchasing/restocking and the Shopify
  catalog — this is a single-owner fix, not a marketing-team project.
- **Metric to watch:** the **active-catalog out-of-stock rate**, currently **{oos_rate:.0%}**
  ({n_oos} of {n_active} SKUs). Target: under 15% within one restock cycle. A secondary metric
  is **days since last online sale** (currently **{days_since_last_sale}**) — it should start
  resetting toward zero once "Best seller" pages are actually purchasable again.
- **Why this first, not ad spend:** with **{purchase_rate:.0%}** of the {total_customers}
  registered accounts having ever purchased and **{oos_rate:.0%}** of the live catalog
  unavailable, the evidence points to a broken storefront experience, not a traffic problem.
  Spending on Meta/Google ads to drive more visitors to a catalog that's often out of stock
  would spend money to make the conversion problem more visible, not solve it.
"""
    )

# ---------------------------------------------------------------------------
# TAB 4 — Assumptions & Limitations
# ---------------------------------------------------------------------------
with tab4:
    st.subheader("Assumptions & Limitations")
    st.markdown(
        """
- **Online-only view.** All revenue and order figures here come from the Shopify online
  storefront only. Cellar V also sells in person at the physical wine bar/retail shop and that
  revenue is not in this dataset — so "the business is failing" would be the wrong conclusion.
  The correct, narrower conclusion is that **the online channel specifically** is not converting.
- **Inventory is a single snapshot**, taken 2026-08-11, not a time series. Some out-of-stock
  items may already be restocked by the time this is graded; the *rate* (currently ~44% of
  active SKUs) is the durable signal, not any single product's status on this exact date.
- **Two-order sample size.** With only two historical online orders, no statistically robust
  claim about *what* converts (price point, wine type, etc.) can be made — the SGD 76/SGD 100
  price range for the two real sales is a directional hint, not a validated pattern. Confirming
  it would require restocking best-sellers first and observing whether conversions resume.
- **Customer count reflects Shopify accounts only** (8 total) — it does not capture social
  media followers, walk-in regulars, or mailing-list subscribers who aren't checkout accounts,
  so it understates Cellar V's total reachable audience.
- **No causal claim on why conversion stalled.** Stock-outs correlate with the conversion
  drought but other explanations (traffic volume, pricing, checkout friction, payment options)
  aren't ruled out here. Fixing availability is the lowest-cost, highest-confidence first step,
  not a guaranteed fix — it should be the first test, watched against the metrics in the
  Recommendation tab, not treated as a proven solution.
"""
    )

st.divider()
st.caption("Cellar V · Communicating with Data (MSBA) · Data source: Cellar V Shopify Admin API, pulled 2026-08-11")
