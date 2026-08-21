"""
Parses the raw POS exports (data/raw/) into clean, small CSVs the dashboard
reads directly, combining the 2025 full-year report with the 2026
year-to-date report into one continuous history. Run once whenever the raw
exports are refreshed:

    python3 data/build_data.py
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

RAW = Path(__file__).parent / "raw"
OUT = Path(__file__).parent

REPORTS = [
    {"label": "2025", "path": RAW / "sales_report_2025.csv"},
    {"label": "2026 YTD", "path": RAW / "sales_report_2026.csv"},
]


def read_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [row for row in csv.reader(f)]


def find_section(rows, header_label, has_header_row=True):
    """Return the rows belonging to a labelled section. If has_header_row,
    the row right after the title is a column-header row to skip; data rows
    follow until a blank line or EOF."""
    start = None
    for i, row in enumerate(rows):
        if row and row[0].strip() == header_label:
            start = i
            break
    if start is None:
        raise ValueError(f"section not found: {header_label}")
    data_start = start + 2 if has_header_row else start + 1
    data = []
    for row in rows[data_start:]:
        if not row or all(c.strip() == "" for c in row):
            break
        data.append(row)
    return data


def money(s):
    return float(s.replace(",", "").replace("$", "").strip())


def parse_report(path):
    rows = read_rows(path)

    summary_keys = {
        "Gross Sales": "gross_sales",
        "Total Discount Given": "total_discount",
        "Net Sales": "net_sales",
        "Total GST": "total_gst",
        "Total Sales": "total_sales",
        "Total Cost": "total_cost",
        "Gross Profit": "gross_profit",
        "Number of Sales Transactions": "transactions",
        "Total Pax": "total_pax",
        "Total Customer Sign Ups": "customer_signups",
        "Member/Non-Member Sales": "member_nonmember_sales",
        "Member/Non-Member Sales Quantity": "member_nonmember_qty",
    }
    summary = {}
    for row in rows:
        if row and row[0].strip() in summary_keys:
            summary[summary_keys[row[0].strip()]] = row[1].strip()
    summary["period"] = rows[1][0]

    member_sales = summary["member_nonmember_sales"].split("/")
    member_qty = summary["member_nonmember_qty"].split("/")
    summary["member_sales_sgd"] = float(member_sales[0])
    summary["nonmember_sales_sgd"] = float(member_sales[1])
    summary["member_qty"] = int(member_qty[0])
    summary["nonmember_qty"] = int(member_qty[1])
    for k in ("gross_sales", "total_discount", "net_sales", "total_gst",
              "total_sales", "total_cost", "gross_profit"):
        summary[k] = money(summary[k])
    summary["transactions"] = int(summary["transactions"])
    summary["total_pax"] = int(summary["total_pax"])
    summary["customer_signups"] = int(summary["customer_signups"])

    payment = {}
    for row in find_section(rows, "Total Settlement by Payment Method", has_header_row=False):
        if row[0].strip() == "Total Settlement":
            continue
        payment[row[0].strip()] = money(row[1])

    category = {}
    for row in find_section(rows, "Sales by Tab"):
        tab, gross, qty, disc = row
        category[tab.strip()] = {
            "gross_sales_sgd": money(gross),
            "quantity_sold": int(qty),
            "discount_sgd": money(disc),
        }

    products = {}
    for row in find_section(rows, "Sales by Product"):
        name, cat, gross, barcode, qty, cost, disc, profit = row
        name = name.strip()
        products[name] = {
            "category": cat.strip(),
            "gross_sales_sgd": money(gross),
            "quantity_sold": int(qty),
            "total_cost_sgd": money(cost),
            "total_discount_sgd": money(disc) if disc.strip() else 0.0,
            "total_profit_sgd": money(profit),
        }

    discount_name, discount_amount, discount_count = find_section(rows, "Discount Information")[0]

    return {
        "summary": summary,
        "payment": payment,
        "category": category,
        "products": products,
        "discount": {"name": discount_name.strip(), "amount": money(discount_amount), "count": int(discount_count)},
    }


def main():
    parsed = [{"label": r["label"], **parse_report(r["path"])} for r in REPORTS]

    # --- combined top-line summary ------------------------------------------
    additive = ["gross_sales", "total_discount", "net_sales", "total_gst", "total_sales",
                "total_cost", "gross_profit", "transactions", "total_pax", "customer_signups",
                "member_sales_sgd", "nonmember_sales_sgd", "member_qty", "nonmember_qty"]
    combined = {k: sum(p["summary"][k] for p in parsed) for k in additive}
    combined["avg_sale_per_transaction"] = combined["total_sales"] / combined["transactions"]

    period_starts = [p["summary"]["period"].split(" - ")[0] for p in parsed]
    period_ends = [p["summary"]["period"].split(" - ")[1] for p in parsed]

    def to_sortable(d):
        day, month, year = d.split(" ")[0].split("/")
        return year, month, day

    earliest = min(period_starts, key=to_sortable)
    latest = max(period_ends, key=to_sortable)
    combined["period"] = f"{earliest} - {latest}"

    with open(OUT / "pos_summary.json", "w") as f:
        json.dump(combined, f, indent=2)

    # --- by-year summary, for a year-over-year view --------------------------
    by_year = []
    for p in parsed:
        s = p["summary"]
        by_year.append({
            "label": p["label"],
            "period": s["period"],
            "gross_sales_sgd": s["gross_sales"],
            "total_sales_sgd": s["total_sales"],
            "total_discount_sgd": s["total_discount"],
            "discount_rate": s["total_discount"] / s["gross_sales"],
            "gross_profit_sgd": s["gross_profit"],
            "net_sales_sgd": s["net_sales"],
            "gross_margin_net": s["gross_profit"] / s["net_sales"],
            "transactions": s["transactions"],
            "avg_sale_per_transaction": s["total_sales"] / s["transactions"],
            "total_pax": s["total_pax"],
            "customer_signups": s["customer_signups"],
        })
    with open(OUT / "pos_by_year.json", "w") as f:
        json.dump(by_year, f, indent=2)

    # --- combined payment methods --------------------------------------------
    payment_totals = defaultdict(float)
    for p in parsed:
        for method, amount in p["payment"].items():
            payment_totals[method] += amount
    with open(OUT / "pos_payment_methods.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["method", "amount_sgd"])
        for method, amount in sorted(payment_totals.items(), key=lambda kv: -kv[1]):
            w.writerow([method, round(amount, 2)])

    # --- combined category (tab) sales ---------------------------------------
    cat_totals = defaultdict(lambda: {"gross_sales_sgd": 0.0, "quantity_sold": 0, "discount_sgd": 0.0})
    for p in parsed:
        for tab, vals in p["category"].items():
            cat_totals[tab]["gross_sales_sgd"] += vals["gross_sales_sgd"]
            cat_totals[tab]["quantity_sold"] += vals["quantity_sold"]
            cat_totals[tab]["discount_sgd"] += vals["discount_sgd"]
    with open(OUT / "pos_category_sales.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tab", "gross_sales_sgd", "quantity_sold", "discount_sgd"])
        for tab, vals in cat_totals.items():
            w.writerow([tab, round(vals["gross_sales_sgd"], 2), vals["quantity_sold"], round(vals["discount_sgd"], 2)])

    # --- combined product sales (top N by gross sales) ------------------------
    product_totals = defaultdict(lambda: {"category": "", "gross_sales_sgd": 0.0, "quantity_sold": 0,
                                           "total_cost_sgd": 0.0, "total_discount_sgd": 0.0, "total_profit_sgd": 0.0})
    for p in parsed:
        for name, vals in p["products"].items():
            entry = product_totals[name]
            entry["category"] = vals["category"]
            entry["gross_sales_sgd"] += vals["gross_sales_sgd"]
            entry["quantity_sold"] += vals["quantity_sold"]
            entry["total_cost_sgd"] += vals["total_cost_sgd"]
            entry["total_discount_sgd"] += vals["total_discount_sgd"]
            entry["total_profit_sgd"] += vals["total_profit_sgd"]
    ranked = sorted(
        ({"product_name": name, **vals} for name, vals in product_totals.items()),
        key=lambda r: r["gross_sales_sgd"], reverse=True,
    )
    with open(OUT / "pos_top_products.csv", "w", newline="") as f:
        fieldnames = ["product_name", "category", "gross_sales_sgd", "quantity_sold",
                      "total_cost_sgd", "total_discount_sgd", "total_profit_sgd"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in ranked[:20]:
            r = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()}
            w.writerow(r)

    # --- combined discounts ---------------------------------------------------
    disc_amount = sum(p["discount"]["amount"] for p in parsed)
    disc_count = sum(p["discount"]["count"] for p in parsed)
    with open(OUT / "pos_discounts.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["discount_name", "amount_sgd", "count"])
        w.writerow(["Custom Discount", round(disc_amount, 2), disc_count])

    # --- product catalog composition (Product List CSV, unchanged by year) ---
    catalog_rows = read_rows(RAW / "product_list.csv")
    cat_header = catalog_rows[0]
    idx = {name.strip('"').strip(): i for i, name in enumerate(cat_header)}
    counts = {}
    for row in catalog_rows[1:]:
        if not row or not row[0].strip():
            continue
        tab = row[idx["Tab"]].strip()
        counts[tab] = counts.get(tab, 0) + 1
    with open(OUT / "pos_catalog_composition.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tab", "sku_count"])
        for tab, n in sorted(counts.items(), key=lambda kv: -kv[1]):
            w.writerow([tab, n])

    print("Wrote pos_summary.json, pos_by_year.json, pos_payment_methods.csv,")
    print("      pos_category_sales.csv, pos_top_products.csv, pos_discounts.csv,")
    print("      pos_catalog_composition.csv")
    print("\nCombined period:", combined["period"])
    print("Combined gross sales: SGD {:,.2f}".format(combined["gross_sales"]))
    print("Combined transactions:", combined["transactions"])


if __name__ == "__main__":
    main()
