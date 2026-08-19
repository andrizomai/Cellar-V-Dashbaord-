"""
Cellar V — Business Health Dashboard
Communicating with Data (Analytics App path)

Stakeholder: Andre, owner of Cellar V (cellar-v.com.sg), a Singapore wine
bar & retail shop.
Decision this dashboard supports: where to focus limited time and budget
next across the whole business — tightening in-person discount/margin
discipline, growing membership, or fixing the dormant online channel.

Data:
- In-person POS sales report, 2026-01-01 to 2026-08-17 (data/raw/sales_report.csv,
  parsed by data/build_data.py into the pos_*.csv / pos_summary.json files).
- Cellar V Shopify Admin API (online products, orders, customers, sales),
  pulled 2026-08-11. Order/customer records are anonymized (no real names
  or emails) since this app may be shared publicly for grading.
See the "Assumptions & Limitations" tab for caveats on both sources.
"""

import json
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

st.set_page_config(page_title="Cellar V — Business Health", page_icon="🍷", layout="wide")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data
def load_online_data():
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


@st.cache_data
def load_pos_data():
    with open(DATA_DIR / "pos_summary.json") as f:
        summary = json.load(f)
    category = pd.read_csv(DATA_DIR / "pos_category_sales.csv")
    top_products = pd.read_csv(DATA_DIR / "pos_top_products.csv")
    discounts = pd.read_csv(DATA_DIR / "pos_discounts.csv")
    payment = pd.read_csv(DATA_DIR / "pos_payment_methods.csv")
    catalog_comp = pd.read_csv(DATA_DIR / "pos_catalog_composition.csv")
    return summary, category, top_products, discounts, payment, catalog_comp


products, orders, monthly, customers = load_online_data()
pos, pos_category, pos_top_products, pos_discounts, pos_payment, pos_catalog = load_pos_data()

# --- online-channel derived stats ------------------------------------------
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

# --- in-person POS derived stats --------------------------------------------
pos_gross = float(pos["gross_sales"])
pos_discount = abs(float(pos["total_discount"]))
pos_net = float(pos["net_sales"])
pos_total = float(pos["total_sales"])
pos_cost = float(pos["total_cost"])
pos_profit = float(pos["gross_profit"])
pos_txns = int(pos["transactions"])
pos_avg_txn = float(pos["avg_sale_per_transaction"])
pos_pax = int(pos["total_pax"])
pos_signups = int(pos["customer_signups"])

discount_rate = pos_discount / pos_gross
gross_margin_net = pos_profit / pos_net

member_sales = pos["member_sales_sgd"]
nonmember_sales = pos["nonmember_sales_sgd"]
member_qty = pos["member_qty"]
nonmember_qty = pos["nonmember_qty"]
member_avg_item = member_sales / member_qty
nonmember_avg_item = nonmember_sales / nonmember_qty
member_multiple = member_avg_item / nonmember_avg_item

period_start, period_end = pos["period"].split(" - ")
period_days = (pd.Timestamp("2026-08-17") - pd.Timestamp("2026-01-01")).days + 1
avg_daily_sales = pos_total / period_days

pos_category = pos_category.sort_values("gross_sales_sgd", ascending=False)
pos_category["discount_rate"] = pos_category["discount_sgd"].abs() / pos_category["gross_sales_sgd"]

illustrative_recovery = pos_gross * 0.05  # a 5pp tighter discount rate, held out explicitly as illustrative

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🍷 Cellar V — Business Health Dashboard")
st.caption(
    "Stakeholder: **Andre, owner of Cellar V** · Decision: where to focus limited time and budget "
    "next — in-person discount/margin discipline, membership growth, or the dormant online channel · "
    f"POS data: **{period_start.split(' ')[0]} to {period_end.split(' ')[0]}** · "
    "Online data: Shopify Admin API, pulled **2026-08-11**"
)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["🍷 The Full Picture", "💰 Where the Money Comes From", "🎯 Margin & Membership",
     "💻 Online Channel", "✅ Recommendation", "⚠️ Assumptions & Limitations"]
)

# ---------------------------------------------------------------------------
# TAB 1 — The Full Picture
# ---------------------------------------------------------------------------
with tab1:
    st.subheader("Cellar V is a thriving in-person wine bar with a dormant online channel")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("In-person total sales (7.5 mo)", f"SGD {pos_total:,.0f}")
    c2.metric("Gross profit (7.5 mo)", f"SGD {pos_profit:,.0f}", help=f"{gross_margin_net:.0%} margin on net sales")
    c3.metric("Transactions", f"{pos_txns:,}", help=f"SGD {pos_avg_txn:,.2f} average sale")
    c4.metric("Guests served (pax)", f"{pos_pax:,}")

    st.markdown("##### Two channels, two very different stories")
    col1, col2 = st.columns(2)
    with col1:
        st.success(
            f"**In-person (POS), {period_start.split(' ')[0]} – {period_end.split(' ')[0]}**\n\n"
            f"### SGD {pos_total:,.0f}\n"
            f"{pos_txns:,} transactions · {pos_pax:,} guests · SGD {avg_daily_sales:,.0f}/day average"
        )
    with col2:
        st.error(
            f"**Online (Shopify), 3-year lifetime**\n\n"
            f"### SGD {lifetime_revenue:,.0f}\n"
            f"{lifetime_orders} orders total · nothing in the last {days_since_last_sale} days"
        )

    st.info(
        f"The online store's **entire 3-year revenue history (SGD {lifetime_revenue:,.0f})** is less than "
        f"half of what the physical wine bar takes in on a **single average day** (SGD {avg_daily_sales:,.0f}). "
        f"The business is healthy — it just isn't the online channel driving it. That reframes the question "
        f"from *'how do we save the online store'* to *'where does another hour of Andre's attention return "
        f"the most, across the whole business.'*"
    )

# ---------------------------------------------------------------------------
# TAB 2 — Where the Money Comes From
# ---------------------------------------------------------------------------
with tab2:
    st.subheader("Red wine, sold in person, is the business")

    top_cat = pos_category.iloc[0]
    st.markdown(
        f"**{top_cat['tab']}** alone accounts for **SGD {top_cat['gross_sales_sgd']:,.0f}** "
        f"({top_cat['gross_sales_sgd']/pos_gross:.0%} of gross sales) across {int(top_cat['quantity_sold'])} "
        f"items sold — more than every other category combined."
    )

    left, right = st.columns(2)
    with left:
        st.markdown("##### Gross sales by category (7.5 months)")
        fig_cat = px.bar(
            pos_category, x="gross_sales_sgd", y="tab", orientation="h",
            labels={"gross_sales_sgd": "Gross sales (SGD)", "tab": ""},
            text=pos_category["gross_sales_sgd"].map(lambda v: f"SGD {v:,.0f}"),
        )
        fig_cat.update_traces(marker_color=BLUE, textposition="outside",
                               hovertemplate="%{y}<br>SGD %{x:,.0f}<extra></extra>")
        fig_cat.update_layout(**PLOTLY_LAYOUT, height=360, showlegend=False)
        fig_cat.update_layout(margin=dict(l=110, r=60, t=40, b=10))
        fig_cat.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig_cat, use_container_width=True, theme=None)

    with right:
        st.markdown("##### Top 10 products by gross sales")
        top10 = pos_top_products.head(10).sort_values("gross_sales_sgd")
        fig_top = px.bar(
            top10, x="gross_sales_sgd", y="product_name", orientation="h",
            labels={"gross_sales_sgd": "Gross sales (SGD)", "product_name": ""},
        )
        fig_top.update_traces(marker_color=ORANGE,
                               hovertemplate="%{y}<br>SGD %{x:,.0f}<extra></extra>")
        fig_top.update_layout(**PLOTLY_LAYOUT, height=360, showlegend=False)
        fig_top.update_layout(margin=dict(l=260, r=20, t=40, b=10))
        fig_top.update_yaxes(tickfont=dict(size=10))
        st.plotly_chart(fig_top, use_container_width=True, theme=None)

    st.caption(
        f"Catalog breadth for context: Andre's POS product list carries {int(pos_catalog['sku_count'].sum())} "
        f"items across {len(pos_catalog)} tabs — but the top 10 products above already account for "
        f"SGD {top10['gross_sales_sgd'].sum():,.0f} ({top10['gross_sales_sgd'].sum()/pos_gross:.0%} of gross sales), "
        f"almost entirely Italian and French reds."
    )

# ---------------------------------------------------------------------------
# TAB 3 — Margin & Membership
# ---------------------------------------------------------------------------
with tab3:
    st.subheader("The real margin lever is discounting and membership, not the website")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Discount given away", f"SGD {pos_discount:,.0f}", delta=f"{discount_rate:.1%} of gross sales", delta_color="inverse")
    c2.metric("Gross margin (net sales)", f"{gross_margin_net:.0%}")
    c3.metric("Member vs non-member value/item", f"{member_multiple:.1f}×", help=f"SGD {member_avg_item:,.2f} vs SGD {nonmember_avg_item:,.2f} per item sold")
    c4.metric("New member sign-ups (7.5 mo)", f"{pos_signups}", help="≈2 per month")

    left, right = st.columns(2)
    with left:
        st.markdown("##### Discount rate by category (share of that category's gross sales)")
        disc_sorted = pos_category.sort_values("discount_rate", ascending=True)
        fig_disc = px.bar(
            disc_sorted, x="discount_rate", y="tab", orientation="h",
            labels={"discount_rate": "Discount rate", "tab": ""},
        )
        fig_disc.update_traces(marker_color=ORANGE, hovertemplate="%{y}<br>%{x:.1%} discounted<extra></extra>")
        fig_disc.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=False)
        fig_disc.update_layout(margin=dict(l=110, r=20, t=40, b=10))
        fig_disc.update_xaxes(tickformat=".0%")
        st.plotly_chart(fig_disc, use_container_width=True, theme=None)

    with right:
        st.markdown("##### Average value per item sold: member vs non-member")
        member_df = pd.DataFrame({
            "group": ["Member", "Non-member"],
            "avg_value": [member_avg_item, nonmember_avg_item],
        })
        fig_mem = px.bar(member_df, x="group", y="avg_value",
                          color="group", color_discrete_map={"Member": BLUE, "Non-member": ORANGE},
                          labels={"avg_value": "SGD per item", "group": ""})
        fig_mem.update_traces(hovertemplate="%{x}<br>SGD %{y:,.2f}/item<extra></extra>")
        fig_mem.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=False)
        st.plotly_chart(fig_mem, use_container_width=True, theme=None)

    st.warning(
        f"Cellar V gave away **SGD {pos_discount:,.0f}** in discounts over the period — **{discount_rate:.1%} of "
        f"gross sales** — with **Liquor** and **Champagne/Sparkling** discounted proportionally the most "
        f"(over a third and a quarter of their gross sales respectively), while **Food** is barely discounted "
        f"at all (under 2%). Meanwhile, members spend **{member_multiple:.1f}×** more per item than non-members, "
        f"yet only **{pos_signups}** new members signed up in 7.5 months — roughly 2 a month."
    )

# ---------------------------------------------------------------------------
# TAB 4 — Online Channel
# ---------------------------------------------------------------------------
with tab4:
    st.subheader("The online store: a smaller but still real quick win")

    c1, c2, c3 = st.columns(3)
    c1.metric("Active SKUs listed", f"{n_active}")
    c2.metric("Active SKUs out of stock", f"{n_oos}", delta=f"{oos_rate:.0%} of catalog", delta_color="inverse")
    c3.metric("'Best seller'-tagged SKUs out of stock", f"{n_bestsellers_oos} of {n_bestsellers}",
              delta=f"{bestseller_oos_rate:.0%}", delta_color="inverse")

    left, right = st.columns(2)
    with left:
        st.markdown("##### Monthly online sales, last 3 years")
        fig = go.Figure()
        fig.add_bar(
            x=monthly["month"], y=monthly["total_sales_sgd"],
            marker_color=BLUE, name="Online sales (SGD)",
            hovertemplate="%{x|%b %Y}<br>SGD %{y:,.0f}<extra></extra>",
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=320, yaxis_title="SGD", showlegend=False,
                           title="Two orders in 37 months")
        st.plotly_chart(fig, use_container_width=True, theme=None)

    with right:
        st.markdown("##### Stock status by price tier (online catalog)")
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
        fig2.update_layout(**PLOTLY_LAYOUT, height=320, legend_title_text="")
        st.plotly_chart(fig2, use_container_width=True, theme=None)

    st.info(
        f"**{n_bestsellers_oos} of {n_bestsellers}** products Cellar V tags as *'Best seller'* on Shopify "
        f"show zero inventory, and **{purchase_rate:.0%}** of the {total_customers} registered online accounts "
        f"have ever purchased. This is a real, low-cost fix — but at SGD {lifetime_revenue:,.0f} lifetime, "
        f"it's a rounding error next to the in-person business (see *The Full Picture*)."
    )

# ---------------------------------------------------------------------------
# TAB 5 — Recommendation
# ---------------------------------------------------------------------------
with tab5:
    st.subheader("Recommendation")
    st.markdown(
        f"""
**Fix in-person margin leakage and membership conversion first — that's where the dollars are.
Restocking the online catalog is still worth doing, but as a low-cost second step.**

- **What:**
  1. Tighten discount discipline on **Liquor** and **Champagne/Sparkling** — the two categories
     discounted proportionally hardest (over a third and a quarter of their gross sales) — starting
     with a review of what "Custom Discount" is actually being applied to and when.
  2. Turn membership sign-up into an active ask at checkout, not a passive option. Members spend
     **{member_multiple:.1f}×** more per item than non-members, but only **{pos_signups}** people
     joined in 7.5 months against **{pos_txns:,}** transactions.
  3. Separately, restock or unpublish the **{n_bestsellers_oos}** out-of-stock "Best seller" SKUs
     on Shopify — a cheap fix, just not the highest-leverage one.
- **Who:** Andre and front-of-house staff for the discount/membership ask (a daily operating habit,
  not a one-off project); Andre alone for the Shopify catalog cleanup.
- **Metric to watch:** the **category discount rate** for Liquor and Champagne/Sparkling (currently
  well above the Food category's under-2% baseline), and **new member sign-ups per month** (currently
  ≈2). On the online side, the **out-of-stock rate** (currently {oos_rate:.0%}).
- **Why this ordering:** a modest 5-percentage-point tightening of the overall discount rate — from
  {discount_rate:.1%} toward roughly {discount_rate - 0.05:.0%} — would recover on the order of
  **SGD {illustrative_recovery:,.0f}** over a comparable period *(illustrative, not a forecast — see
  Assumptions)*, dwarfing the online channel's entire 3-year revenue of SGD {lifetime_revenue:,.0f}.
  The website fix is real and worth doing, but it shouldn't be first in line for Andre's time.
"""
    )

# ---------------------------------------------------------------------------
# TAB 6 — Assumptions & Limitations
# ---------------------------------------------------------------------------
with tab6:
    st.subheader("Assumptions & Limitations")
    st.markdown(
        f"""
- **The POS window is partial-year and not annualized.** Figures cover **{period_start.split(' ')[0]} to
  {period_end.split(' ')[0]}** (about 7.5 months) only. Any recovery estimate in the Recommendation tab is
  explicitly **illustrative** — it applies today's discount rate math to today's sales base, not a forecast
  of a full year or of how customers would react to less discounting.
- **"Custom Discount" is one undifferentiated bucket** in the POS export (SGD {pos_discount:,.0f} across
  972 applications). It may include happy-hour set pricing, staff comps, corporate deals, and genuine
  promotions all mixed together — so the {discount_rate:.1%} figure is a ceiling on discretionary discounting,
  not proof that any specific promotion was a mistake.
- **Member-vs-non-member is a per-item average, not a per-customer or per-visit figure**, and it's
  correlational: members may simply be more affluent or more frequent regulars who would spend more
  regardless of membership status. The {member_multiple:.1f}× gap is a reason to test a more active
  sign-up ask, not proof that membership itself causes higher spend.
- **The online and in-person catalogs are separate systems** (Shopify for online retail, a different POS
  for the wine bar) with different pricing structures and only partial SKU overlap — they are not merged
  into one blended catalog anywhere in this dashboard, and the in-person product list has no live stock
  data (unlike the online catalog), so the same out-of-stock analysis can't be run for the physical bar.
- **Inventory (online) is a single snapshot**, taken 2026-08-11, not a time series — some items may already
  be restocked by the time this is reviewed; the *rate* (~{oos_rate:.0%} of active SKUs) is the durable
  signal, not any one product's status on that exact date.
- **No causal claim on why online conversion stalled.** Stock-outs correlate with the online conversion
  drought but other explanations (traffic, pricing, checkout friction) aren't ruled out — restocking is the
  lowest-cost, highest-confidence first test for that channel specifically, not a guaranteed fix.
"""
    )

st.divider()
st.caption(
    "Cellar V · Communicating with Data (MSBA) · Data sources: in-person POS sales report "
    f"({period_start.split(' ')[0]}–{period_end.split(' ')[0]}) and Cellar V Shopify Admin API (pulled 2026-08-11)"
)
