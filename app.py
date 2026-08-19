"""
Cellar V — Business Health Dashboard
Communicating with Data (Analytics App path)

Stakeholders: Cellar V's owner and its investors.
Decision this dashboard supports: where the business should prioritize its
limited time and capital next — tightening in-person discount/margin
discipline, growing membership, or reviving the dormant online channel.

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

st.set_page_config(page_title="Cellar V — Business Health", layout="wide")


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
period_start_date = period_start.split(" ")[0]
period_end_date = period_end.split(" ")[0]
period_days = (pd.Timestamp("2026-08-17") - pd.Timestamp("2026-01-01")).days + 1
avg_daily_sales = pos_total / period_days

pos_category = pos_category.sort_values("gross_sales_sgd", ascending=False)
pos_category["discount_rate"] = pos_category["discount_sgd"].abs() / pos_category["gross_sales_sgd"]

illustrative_recovery = pos_gross * 0.05  # a 5pp tighter discount rate, held out explicitly as illustrative

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("Cellar V — Business Health Dashboard")
st.caption(
    "Prepared for Cellar V's owner and investors · Decision: where the business should prioritize "
    "its limited time and capital next — in-person discount discipline, membership growth, or the "
    f"dormant online channel · POS data: **{period_start_date} to {period_end_date}** · "
    "Online data: Shopify, pulled **2026-08-11**"
)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["The Full Picture", "Where the Money Comes From", "Margin & Membership",
     "Online Channel", "Recommendation", "Assumptions & Limitations"]
)

# ---------------------------------------------------------------------------
# TAB 1 — The Full Picture
# ---------------------------------------------------------------------------
with tab1:
    st.subheader("The wine bar is healthy. The website isn't part of that story yet.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("In-person sales, last 7.5 months", f"SGD {pos_total:,.0f}")
    c2.metric("Gross profit, last 7.5 months", f"SGD {pos_profit:,.0f}", help=f"{gross_margin_net:.0%} margin on net sales")
    c3.metric("Transactions", f"{pos_txns:,}", help=f"SGD {pos_avg_txn:,.2f} average sale")
    c4.metric("Guests served", f"{pos_pax:,}")

    st.markdown("##### Two channels, two very different results")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown(f"**In-person (POS), {period_start_date} – {period_end_date}**")
            st.markdown(f"### SGD {pos_total:,.0f}")
            st.markdown(f"{pos_txns:,} transactions · {pos_pax:,} guests · about SGD {avg_daily_sales:,.0f} a day")
    with col2:
        with st.container(border=True):
            st.markdown("**Online (Shopify), 3-year lifetime**")
            st.markdown(f"### SGD {lifetime_revenue:,.0f}")
            st.markdown(f"{lifetime_orders} orders total · nothing in the last {days_since_last_sale} days")

    with st.container(border=True):
        st.markdown(
            f"Put simply: the online store's entire three-year history — SGD {lifetime_revenue:,.0f} — "
            f"doesn't add up to half of what the wine bar takes in on a single average day "
            f"(about SGD {avg_daily_sales:,.0f}). Cellar V isn't a business in trouble; it's a business "
            f"whose website hasn't caught up with it yet. That changes the question this dashboard is "
            f"really answering — not *how do we fix the online store*, but *where should the next dollar "
            f"and the next hour of attention go, across the whole business.*"
        )

# ---------------------------------------------------------------------------
# TAB 2 — Where the Money Comes From
# ---------------------------------------------------------------------------
with tab2:
    st.subheader("Red wine, sold in person, is what Cellar V actually is")

    top_cat = pos_category.iloc[0]
    st.markdown(
        f"{top_cat['tab']} wine alone brought in SGD {top_cat['gross_sales_sgd']:,.0f} — "
        f"{top_cat['gross_sales_sgd']/pos_gross:.0%} of every sales dollar — across "
        f"{int(top_cat['quantity_sold'])} bottles and glasses. That's more than every other "
        f"category put together."
    )

    left, right = st.columns(2)
    with left:
        st.markdown("##### Gross sales by category, last 7.5 months")
        fig_cat = px.bar(
            pos_category, x="gross_sales_sgd", y="tab", orientation="h",
            labels={"gross_sales_sgd": "Gross sales (SGD)", "tab": ""},
            text=pos_category["gross_sales_sgd"].map(lambda v: f"SGD {v:,.0f}"),
        )
        fig_cat.update_traces(marker_color=BLUE, textposition="outside", cliponaxis=False,
                               hovertemplate="%{y}<br>SGD %{x:,.0f}<extra></extra>")
        fig_cat.update_layout(**PLOTLY_LAYOUT, height=360, showlegend=False)
        fig_cat.update_layout(margin=dict(l=110, r=90, t=40, b=10))
        fig_cat.update_yaxes(categoryorder="total ascending")
        fig_cat.update_xaxes(range=[0, pos_category["gross_sales_sgd"].max() * 1.22])
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
        f"For scale: the full product list runs to {int(pos_catalog['sku_count'].sum())} items across "
        f"{len(pos_catalog)} categories. Even so, the ten best-selling products above already account "
        f"for SGD {top10['gross_sales_sgd'].sum():,.0f} — about {top10['gross_sales_sgd'].sum()/pos_gross:.0%} "
        f"of all sales — and nearly all of them are Italian or French reds."
    )

# ---------------------------------------------------------------------------
# TAB 3 — Margin & Membership
# ---------------------------------------------------------------------------
with tab3:
    st.subheader("The bigger opportunity is in the room, not on the website")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Discount given away", f"SGD {pos_discount:,.0f}", delta=f"{discount_rate:.1%} of gross sales", delta_color="inverse")
    c2.metric("Gross margin, net sales", f"{gross_margin_net:.0%}")
    c3.metric("Member vs non-member value per item", f"{member_multiple:.1f}x", help=f"SGD {member_avg_item:,.2f} vs SGD {nonmember_avg_item:,.2f} per item sold")
    c4.metric("New members, last 7.5 months", f"{pos_signups}", help="About 2 a month")

    left, right = st.columns(2)
    with left:
        st.markdown("##### Discount rate by category")
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
        st.markdown("##### Average value per item: member vs non-member")
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

    with st.container(border=True):
        st.markdown(
            f"Cellar V gave away SGD {pos_discount:,.0f} in discounts over the period — roughly one "
            f"dollar in five of gross sales. Liquor and Champagne/Sparkling are discounted hardest, "
            f"each losing close to a quarter to a third of their value to markdowns, while food is "
            f"barely discounted at all. Meanwhile, members spend {member_multiple:.1f} times more per "
            f"item than non-members — yet only {pos_signups} people joined as members over seven and a "
            f"half months, about two a month. That's a lever that's mostly sitting untouched."
        )

# ---------------------------------------------------------------------------
# TAB 4 — Online Channel
# ---------------------------------------------------------------------------
with tab4:
    st.subheader("The website is a smaller fix, but still a real one")

    c1, c2, c3 = st.columns(3)
    c1.metric("Active listings", f"{n_active}")
    c2.metric("Listings out of stock", f"{n_oos}", delta=f"{oos_rate:.0%} of catalog", delta_color="inverse")
    c3.metric("'Best seller' listings out of stock", f"{n_bestsellers_oos} of {n_bestsellers}",
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
        st.markdown("##### Stock status by price tier, online catalog")
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

    with st.container(border=True):
        st.markdown(
            f"{n_bestsellers_oos} of the {n_bestsellers} products Cellar V flags as a 'Best seller' "
            f"online are currently out of stock, and only {purchase_rate:.0%} of the {total_customers} "
            f"people who've created an account have ever completed a purchase. Fixing this is "
            f"inexpensive and straightforward — it just shouldn't be first in line. At "
            f"SGD {lifetime_revenue:,.0f} lifetime, it's a rounding error next to what the wine bar "
            f"does in person (see *The Full Picture*)."
        )

# ---------------------------------------------------------------------------
# TAB 5 — Recommendation
# ---------------------------------------------------------------------------
with tab5:
    st.subheader("Recommendation")
    st.markdown(
        f"""
The clearest opportunity isn't the website — it's tightening how the business runs day to day, in the room.

**For the owner:**
1. Rein in discounting on Liquor and Champagne/Sparkling specifically — the two categories giving
   away the largest share of their value, roughly a quarter to a third — starting with a plain review
   of what "Custom Discount" is meant to cover and when staff should actually use it.
2. Make membership sign-up part of the conversation at checkout, rather than something guests have to
   ask about themselves. Members already spend {member_multiple:.1f} times more per item than
   non-members, but only {pos_signups} people joined in seven and a half months against
   {pos_txns:,} transactions — most guests are simply never being asked.
3. Separately, restock or take down the {n_bestsellers_oos} out-of-stock "Best seller" listings on
   Shopify. It's a cheap, quick fix — just not the one that moves the needle most.

**For investors, the case for prioritizing this first:** a modest five-percentage-point tightening of
the discount rate — from {discount_rate:.1%} toward roughly {discount_rate - 0.05:.0%} — would recover
on the order of SGD {illustrative_recovery:,.0f} over a comparable period *(an illustration of scale,
not a forecast — see Assumptions)*. That single lever is worth several times the online channel's
entire three-year revenue of SGD {lifetime_revenue:,.0f}. The website is worth fixing, but it isn't
where the return is.

**What to watch:** the discount rate for Liquor and Champagne/Sparkling specifically (today, well
above food's under-2% baseline), new member sign-ups per month (today, about two), and — lower
priority — the online out-of-stock rate (today, {oos_rate:.0%}).
"""
    )

# ---------------------------------------------------------------------------
# TAB 6 — Assumptions & Limitations
# ---------------------------------------------------------------------------
with tab6:
    st.subheader("Assumptions & Limitations")
    st.markdown(
        f"""
- This covers {period_start_date} to {period_end_date} — about seven and a half months, not a full
  year. The recovery figure in the Recommendation is an illustration of what today's numbers imply,
  not a forecast of a full year or of how guests would actually respond to less discounting.
- "Custom Discount" is a single, undifferentiated line in the POS export (SGD {pos_discount:,.0f}
  across 972 uses). It likely mixes happy-hour pricing, staff comps, corporate deals, and genuine
  promotions together, so the {discount_rate:.1%} figure is a ceiling on discretionary discounting —
  not evidence that any one promotion was a mistake.
- The member-versus-non-member comparison is a per-item average, not a per-customer or per-visit
  figure, and it's correlational rather than causal: members may simply be more frequent or more
  affluent regulars who'd spend more regardless of membership status. The {member_multiple:.1f}x gap
  is a reason to test a more active sign-up ask, not proof that membership itself drives spending.
- The online and in-person catalogs run on separate systems with different pricing and only partial
  overlap in what they sell, so they're never merged into one blended view here. The in-person product
  list also has no live stock data, so the out-of-stock analysis in this dashboard applies to the
  online store only.
- Online inventory is a single snapshot from 2026-08-11, not a time series — some items may already be
  restocked by the time this is read. The rate (roughly {oos_rate:.0%} of active listings) is the
  signal that matters, not any one product's status on that particular date.
- Stock-outs correlate with the online channel's conversion drought, but other explanations — traffic,
  pricing, checkout friction — haven't been ruled out. Restocking is the cheapest, most confident first
  test for that channel specifically, not a guaranteed fix.
"""
    )

st.divider()
st.caption(
    "Cellar V · Communicating with Data (MSBA) · Data sources: in-person POS sales report "
    f"({period_start_date}–{period_end_date}) and Cellar V Shopify Admin API (pulled 2026-08-11)"
)
