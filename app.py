"""
Cellar V — Business Health Dashboard
Communicating with Data (Analytics App path)

Stakeholders: Cellar V's owner and its investors.
Decision this dashboard supports: where the business should prioritize its
limited time and capital next — tightening in-person discount/margin
discipline, growing membership, or reviving the dormant online channel.

Data:
- In-person POS sales reports, full year 2025 plus year-to-date 2026 through
  2026-08-17 (data/raw/sales_report_2025.csv, sales_report_2026.csv), parsed
  and combined by data/build_data.py into the pos_*.csv / pos_summary.json /
  pos_by_year.json files.
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
BLUE, ORANGE = "#2a78d6", "#eb6834"
STATUS_GOOD, STATUS_CRITICAL = "#0ca30c", "#d03b3b"
INK, MUTED, GRID = "#0b0b0b", "#898781", "#e1e0d9"
SURFACE = "#fcfcfb"

PLOTLY_LAYOUT = dict(
    font=dict(family="system-ui, -apple-system, 'Segoe UI', sans-serif", color=INK, size=13),
    plot_bgcolor=SURFACE,
    paper_bgcolor=SURFACE,
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(gridcolor=GRID, zerolinecolor=MUTED, linecolor=MUTED, automargin=True),
    yaxis=dict(gridcolor=GRID, zerolinecolor=MUTED, linecolor=MUTED, automargin=True),
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
    with open(DATA_DIR / "pos_by_year.json") as f:
        by_year = json.load(f)
    category_by_year = pd.read_csv(DATA_DIR / "pos_category_by_year.csv")
    products_by_year = pd.read_csv(DATA_DIR / "pos_products_by_year.csv")
    discounts = pd.read_csv(DATA_DIR / "pos_discounts.csv")
    catalog_comp = pd.read_csv(DATA_DIR / "pos_catalog_composition.csv")
    return summary, by_year, category_by_year, products_by_year, discounts, catalog_comp


products, orders, monthly, customers = load_online_data()
pos_combined, pos_by_year, pos_category_by_year, pos_products_by_year, pos_discounts, pos_catalog = load_pos_data()
by_year = pd.DataFrame(pos_by_year)
by_year["discount_rate"] = by_year["discount_rate"].abs()

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

# --- period selection --------------------------------------------------------
# The POS exports arrive one file per year, so the honest unit of filtering is a
# reporting period, not an arbitrary date range. "Combined" sums the periods and
# reproduces the headline figures exactly (see data/build_data.py).
COMBINED = "Combined (Jan 2025 – Aug 2026)"
PERIOD_LABELS = {"2025": "2025 (full year)", "2026 YTD": "2026 (year to date, through 17 Aug)"}
PERIOD_OPTIONS = [COMBINED] + [PERIOD_LABELS[r["label"]] for r in pos_by_year]
LABEL_FOR_OPTION = {PERIOD_LABELS[k]: k for k in PERIOD_LABELS}

selected_period = st.session_state.get("period_filter", COMBINED) or COMBINED
is_combined = selected_period == COMBINED
selected_label = None if is_combined else LABEL_FOR_OPTION[selected_period]

if is_combined:
    pos = dict(pos_combined)
else:
    row = by_year[by_year["label"] == selected_label].iloc[0]
    pos = {
        "gross_sales": row["gross_sales_sgd"], "total_discount": row["total_discount_sgd"],
        "net_sales": row["net_sales_sgd"], "total_sales": row["total_sales_sgd"],
        "total_cost": row["total_cost_sgd"], "gross_profit": row["gross_profit_sgd"],
        "transactions": row["transactions"], "avg_sale_per_transaction": row["avg_sale_per_transaction"],
        "total_pax": row["total_pax"], "customer_signups": row["customer_signups"],
        "member_sales_sgd": row["member_sales_sgd"], "nonmember_sales_sgd": row["nonmember_sales_sgd"],
        "member_qty": row["member_qty"], "nonmember_qty": row["nonmember_qty"],
        "period": row["period"],
    }

# --- in-person POS derived stats --------------------------------------------
pos_gross = float(pos["gross_sales"])
pos_discount = abs(float(pos["total_discount"]))
pos_net = float(pos["net_sales"])
pos_total = float(pos["total_sales"])
pos_profit = float(pos["gross_profit"])
pos_txns = int(pos["transactions"])
pos_avg_txn = float(pos["avg_sale_per_transaction"])
pos_pax = int(pos["total_pax"])
pos_signups = int(pos["customer_signups"])

discount_rate = pos_discount / pos_gross
gross_margin_net = pos_profit / pos_net

member_sales = pos["member_sales_sgd"]
nonmember_sales = pos["nonmember_sales_sgd"]
# The POS export's "Sales Quantity" for member/non-member is a transaction count, not an
# item count — member_txns + nonmember_txns equals total transactions exactly in both years.
member_txns = pos["member_qty"]
nonmember_txns = pos["nonmember_qty"]
member_avg_txn = member_sales / member_txns
nonmember_avg_txn = nonmember_sales / nonmember_txns
member_multiple = member_avg_txn / nonmember_avg_txn
member_txn_share = member_txns / pos_txns

period_start, period_end = pos["period"].split(" - ")
period_start_date = period_start.split(" ")[0]
period_end_date = period_end.split(" ")[0]
period_start_ts = pd.to_datetime(period_start_date, dayfirst=True)
period_end_ts = pd.to_datetime(period_end_date, dayfirst=True)
period_days = (period_end_ts - period_start_ts).days + 1
avg_daily_sales = pos_total / period_days
period_span_label = (
    "January 2025 through August 2026" if is_combined
    else ("2025" if selected_label == "2025" else "2026 to date")
)

# --- category / product frames for the selected period ------------------------
_cat_src = pos_category_by_year if is_combined else \
    pos_category_by_year[pos_category_by_year["period"] == selected_label]
pos_category = (
    _cat_src.groupby("tab", as_index=False)[["gross_sales_sgd", "quantity_sold", "discount_sgd"]]
    .sum().sort_values("gross_sales_sgd", ascending=False)
)
pos_category["discount_abs"] = pos_category["discount_sgd"].abs()
pos_category["discount_rate"] = pos_category["discount_abs"] / pos_category["gross_sales_sgd"]

_prod_src = pos_products_by_year if is_combined else \
    pos_products_by_year[pos_products_by_year["period"] == selected_label]
pos_top_products = (
    _prod_src.groupby("product_name", as_index=False)["gross_sales_sgd"].sum()
    .sort_values("gross_sales_sgd", ascending=False)
)

# Discounting is best attacked where the dollars are, not where the rate is steepest:
# a steep rate on a tiny category is worth little. Target the three categories giving
# away the most money, and size the opportunity on those alone — so the quantified
# impact matches the actions actually recommended.
disc_ranked = pos_category.sort_values("discount_abs", ascending=False)
top_disc_cat = disc_ranked.iloc[0]
targeted = disc_ranked.head(3)
targeted_names = list(targeted["tab"])
targeted_phrase = ", ".join(targeted_names[:-1]) + f" and {targeted_names[-1]}"
targeted_recovery = float((targeted["gross_sales_sgd"] * 0.05).sum())
targeted_discount_share = float(targeted["discount_abs"].sum() / pos_discount)
# For contrast: what tightening *everything* by 5 points would yield.
illustrative_recovery = pos_gross * 0.05

# Prose fragments that have to agree with whichever period is selected.
period_phrase = "since the start of 2025" if is_combined else f"in {period_span_label}"
months_in_period = round(period_days / 30.44)
signups_per_month = pos_signups / (period_days / 30.44)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("Cellar V — Business Health Dashboard")
st.caption(
    "Prepared for Cellar V's owner and investors · Decision: where the business should prioritize "
    "its limited time and capital next — in-person discount discipline, membership growth, or the "
    f"dormant online channel · POS data: **{period_start_date} to {period_end_date}** "
    "· Online data: Shopify, pulled **2026-08-11**"
)

filter_col, note_col = st.columns([2, 3])
with filter_col:
    st.radio(
        "Reporting period", PERIOD_OPTIONS, key="period_filter",
        horizontal=True, label_visibility="collapsed",
    )
with note_col:
    st.caption(
        "Switching period re-cuts every in-person figure and chart below. The Online Channel tab "
        "always shows the Shopify store's full lifetime, which the POS periods don't apply to."
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
    c1.metric(f"In-person sales, {period_span_label}", f"SGD {pos_total:,.0f}")
    c2.metric("Gross profit, same period", f"SGD {pos_profit:,.0f}", help=f"{gross_margin_net:.0%} margin on net sales")
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
    st.caption(
        f"The daily figure spreads sales across all {period_days} calendar days in the period, "
        "including any the bar was closed — so it understates a real trading day, which only makes "
        "the gap with the online channel wider."
    )

    st.markdown("##### By year")
    yr_cols = st.columns(len(by_year))
    for col, (_, row) in zip(yr_cols, by_year.iterrows()):
        with col:
            with st.container(border=True):
                label = "2025 (full year)" if row["label"] == "2025" else "2026 (year to date, through Aug 17)"
                st.markdown(f"**{label}**")
                st.markdown(f"### SGD {row['gross_sales_sgd']:,.0f}")
                st.markdown(
                    f"{int(row['transactions']):,} transactions · SGD {row['avg_sale_per_transaction']:,.2f} "
                    f"average sale · {row['discount_rate']:.1%} discount rate"
                )
    st.caption(
        "2026 is a partial year, so its total isn't directly comparable to 2025's full-year total — "
        "but the rate metrics (average sale, discount rate) land in a similar range in both years, "
        "which is exactly what makes the discounting pattern on the Margin & Membership tab worth "
        "acting on: it isn't a one-off, it shows up year after year."
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
        st.markdown(f"##### Gross sales by category, {period_span_label}")
        fig_cat = px.bar(
            pos_category, x="gross_sales_sgd", y="tab", orientation="h",
            labels={"gross_sales_sgd": "Gross sales (SGD)", "tab": ""},
            text=pos_category["gross_sales_sgd"].map(lambda v: f"{v/1000:,.1f}k"),
        )
        fig_cat.update_traces(marker_color=BLUE, textposition="outside", cliponaxis=False,
                               hovertemplate="%{y}<br>SGD %{x:,.0f}<extra></extra>")
        fig_cat.update_layout(**PLOTLY_LAYOUT, height=360, showlegend=False)
        fig_cat.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        fig_cat.update_yaxes(categoryorder="total ascending", automargin=True)
        fig_cat.update_xaxes(range=[0, pos_category["gross_sales_sgd"].max() * 1.18], automargin=True)
        st.plotly_chart(fig_cat, use_container_width=True, theme=None)

    with right:
        st.markdown("##### Top 10 products by gross sales")
        top10 = pos_top_products.head(10).sort_values("gross_sales_sgd").copy()
        top10["short_name"] = top10["product_name"].map(
            lambda s: s if len(s) <= 34 else s[:33].rstrip() + "…"
        )
        fig_top = px.bar(
            top10, x="gross_sales_sgd", y="short_name", orientation="h",
            labels={"gross_sales_sgd": "Gross sales (SGD)", "short_name": ""},
            custom_data=["product_name"],
        )
        fig_top.update_traces(marker_color=ORANGE,
                               hovertemplate="%{customdata[0]}<br>SGD %{x:,.0f}<extra></extra>")
        fig_top.update_layout(**PLOTLY_LAYOUT, height=360, showlegend=False)
        fig_top.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        fig_top.update_yaxes(tickfont=dict(size=10), automargin=True)
        st.plotly_chart(fig_top, use_container_width=True, theme=None)

    st.caption(
        f"For scale: the full product list runs to {int(pos_catalog['sku_count'].sum())} items across "
        f"{len(pos_catalog)} categories. Even so, the ten best-selling products above already account "
        f"for SGD {top10['gross_sales_sgd'].sum():,.0f} — about {top10['gross_sales_sgd'].sum()/pos_gross:.0%} "
        f"of all sales — and nearly all of them are Italian reds."
    )

# ---------------------------------------------------------------------------
# TAB 3 — Margin & Membership
# ---------------------------------------------------------------------------
with tab3:
    st.subheader("The bigger opportunity is in the room, not on the website")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Discount given away", f"SGD {pos_discount:,.0f}", delta=f"{discount_rate:.1%} of gross sales", delta_color="inverse")
    c2.metric("Gross margin, net sales", f"{gross_margin_net:.0%}")
    c3.metric("Member vs non-member average sale", f"{member_multiple:.1f}x", help=f"SGD {member_avg_txn:,.2f} vs SGD {nonmember_avg_txn:,.2f} average transaction value")
    c4.metric(f"New members, {period_span_label}", f"{pos_signups}",
              help=f"About {signups_per_month:.0f} a month across {months_in_period} months")

    left, right = st.columns(2)
    with left:
        st.markdown("##### Where the discount money actually goes")
        disc_sorted = pos_category.sort_values("discount_abs", ascending=True)
        fig_disc = px.bar(
            disc_sorted, x="discount_abs", y="tab", orientation="h",
            labels={"discount_abs": "Discount given away (SGD)", "tab": ""},
            text=disc_sorted.apply(
                lambda r: f"{r['discount_abs']/1000:,.1f}k  ({r['discount_rate']:.0%})", axis=1),
            custom_data=["discount_rate", "gross_sales_sgd"],
        )
        fig_disc.update_traces(
            marker_color=ORANGE, textposition="outside", cliponaxis=False,
            hovertemplate="%{y}<br>SGD %{x:,.0f} discounted<br>"
                          "%{customdata[0]:.1%} of its SGD %{customdata[1]:,.0f} gross<extra></extra>",
        )
        fig_disc.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=False)
        fig_disc.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        fig_disc.update_xaxes(range=[0, pos_category["discount_abs"].max() * 1.35])
        st.plotly_chart(fig_disc, use_container_width=True, theme=None)
        st.caption("Bars are dollars given away; the percentage in each label is that category's discount rate.")

    with right:
        st.markdown("##### Average transaction value: member vs non-member")
        member_df = pd.DataFrame({
            "group": ["Member", "Non-member"],
            "avg_value": [member_avg_txn, nonmember_avg_txn],
        })
        fig_mem = px.bar(member_df, x="group", y="avg_value",
                          color="group", color_discrete_map={"Member": BLUE, "Non-member": ORANGE},
                          labels={"avg_value": "SGD per transaction", "group": ""})
        fig_mem.update_traces(hovertemplate="%{x}<br>SGD %{y:,.2f}/transaction<extra></extra>")
        fig_mem.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=False)
        st.plotly_chart(fig_mem, use_container_width=True, theme=None)

    _by_rate = pos_category.sort_values("discount_rate", ascending=False).iloc[0]
    st.caption(
        f"Rate and dollars point at different categories, which is why this chart leads with dollars. "
        f"**{_by_rate['tab']}** has the steepest *rate* ({_by_rate['discount_rate']:.0%}), but on only "
        f"SGD {_by_rate['gross_sales_sgd']:,.0f} of sales it gives away SGD {_by_rate['discount_abs']:,.0f}. "
        f"**{top_disc_cat['tab']}** is discounted less steeply ({top_disc_cat['discount_rate']:.0%}) but on a "
        f"far larger base, so it accounts for SGD {top_disc_cat['discount_abs']:,.0f} — "
        f"{top_disc_cat['discount_abs']/pos_discount:.0%} of every discount dollar in this period. "
        f"Chasing the steepest rate is not the same as recovering the most margin."
    )

    with st.container(border=True):
        st.markdown(
            f"Cellar V gave away SGD {pos_discount:,.0f} in discounts {period_phrase} — roughly "
            f"one dollar in five of gross sales, and remarkably steady year to year (about "
            f"{by_year.iloc[0]['discount_rate']:.1%} in 2025, {by_year.iloc[1]['discount_rate']:.1%} so "
            f"far in 2026). The steepest *rates* sit on small categories, but the money is concentrated: "
            f"**{targeted_phrase}** together account for {targeted_discount_share:.0%} of every "
            f"discount dollar, so that is where discipline pays. Food, by contrast, is barely discounted "
            f"at all. Meanwhile, member transactions already make up {member_txn_share:.0%} of the till, "
            f"averaging {member_multiple:.1f} times more per sale than non-member transactions — yet only "
            f"{pos_signups} people joined as members over that stretch, about "
            f"{signups_per_month:.0f} a month. That's a lever that's mostly sitting untouched."
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
1. Start discount discipline with **{top_disc_cat['tab']}**, not with the steepest-rate category.
   {top_disc_cat['tab']} is discounted at {top_disc_cat['discount_rate']:.0%} — unremarkable next to the
   worst rate on the board — but on such a large base that it alone accounts for
   SGD {top_disc_cat['discount_abs']:,.0f}, or {top_disc_cat['discount_abs']/pos_discount:.0%} of every
   discount dollar. Together, **{targeted_phrase}** carry
   {targeted_discount_share:.0%} of all discounting. Begin with a plain review of what
   "Custom Discount" is meant to cover on those, and when staff should actually apply it.
2. Make membership sign-up part of the conversation at checkout, rather than something guests have to
   ask about themselves. Members already average {member_multiple:.1f} times more per sale than
   non-members, but only {pos_signups} people joined as members {period_phrase}, against
   {pos_txns:,} transactions over the same stretch — most guests are simply never being asked.
3. Separately, restock or take down the {n_bestsellers_oos} out-of-stock "Best seller" listings on
   Shopify. It's a cheap, quick fix — just not the one that moves the needle most.

**For investors, the case for prioritizing this first:** tightening the discount rate by five
percentage points on just those three categories would recover on the order of
**SGD {targeted_recovery:,.0f}** over a comparable period *(an illustration of scale, not a forecast —
see Assumptions)*. Applied across every category it would be about SGD {illustrative_recovery:,.0f},
but that would mean touching food, which is already disciplined at under 2%. Either figure dwarfs the
online channel's entire three-year revenue of SGD {lifetime_revenue:,.0f} — the website is worth
fixing, but it isn't where the return is.

**What to watch:** discount *dollars* by category — especially {top_disc_cat['tab']}, since that is
where the money actually leaves — alongside the rate; new member sign-ups per month (today, about
{signups_per_month:.0f}); and, lower priority, the online out-of-stock rate (today, {oos_rate:.0%}).
"""
    )

# ---------------------------------------------------------------------------
# TAB 6 — Assumptions & Limitations
# ---------------------------------------------------------------------------
with tab6:
    st.subheader("Assumptions & Limitations")
    st.markdown(
        f"""
- The underlying POS data covers 01/01/2025 to 17/08/2026 — a full calendar year (2025) plus 2026
  year-to-date through August 17, not two complete years. The By Year breakdown on the first tab
  keeps 2026 separate for exactly this reason: its total isn't a full-year figure and shouldn't be
  read as one, and the reporting-period filter at the top of the page exists so the two are never
  accidentally compared as equals. The recovery estimate in the Recommendation is an illustration
  of what the numbers imply, not a forecast of how guests would respond to less discounting.
- "Custom Discount" is a single, undifferentiated line in the POS export
  (SGD {abs(float(pos_combined['total_discount'])):,.0f} across
  {int(pos_discounts.iloc[0]['count']):,} uses across both years). It likely mixes happy-hour
  pricing, staff comps, corporate deals, and genuine promotions together, so the discount rate here
  is a ceiling on discretionary discounting — not evidence that any one promotion was a mistake.
  That said, the rate is close to identical in 2025 and 2026 separately, which is what makes it
  look like a pattern rather than noise.
- The recovery figures assume a five-point rate cut leaves volume unchanged, which is the optimistic
  case. Some of that discounting is presumably doing work — winning a table, moving slow stock, keeping
  a regular loyal — so a portion of the "recovered" margin would show up as lost sales instead. The
  honest read is an upper bound on the prize, and a reason to test the change on a few categories
  before rolling it out rather than a number to bank.
- The member-versus-non-member comparison is an average-transaction-value figure (member and
  non-member transaction counts sum exactly to total transactions in both years' exports), not a
  per-customer lifetime-value figure — a member who visits often is counted once per visit, not once
  overall. It's also correlational rather than causal: members may simply be more frequent or more
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
- The 2025 and 2026 POS reports are combined by matching identical product names between the two
  years' exports. Where a wine's listing name changed between years (a new vintage added to the name,
  for instance), the two years show up as separate line items rather than one combined total — so a
  handful of individual product totals in the Where the Money Comes From tab may understate a wine's
  true two-year total, even though the category- and business-level totals elsewhere are unaffected.
"""
    )

st.divider()
st.caption(
    "Cellar V · Communicating with Data (MSBA) · Data sources: in-person POS sales reports, "
    "2025 full year plus 2026 year-to-date (01/01/2025–17/08/2026), "
    "and Cellar V Shopify Admin API (pulled 2026-08-11). "
    f"Currently viewing: {selected_period}."
)
