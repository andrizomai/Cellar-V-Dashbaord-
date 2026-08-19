"""
Parses the raw POS exports (data/raw/) into clean, small CSVs the dashboard
reads directly. Run once whenever the raw exports are refreshed:

    python3 data/build_data.py
"""
import csv
import json
from pathlib import Path

RAW = Path(__file__).parent / "raw"
OUT = Path(__file__).parent


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
    header = rows[start + 1] if has_header_row else None
    data = []
    for row in rows[data_start:]:
        if not row or all(c.strip() == "" for c in row):
            break
        data.append(row)
    return header, data


def money(s):
    return float(s.replace(",", "").replace("$", "").strip())


def main():
    sales_rows = read_rows(RAW / "sales_report.csv")

    # --- top-line summary (key/value pairs near the top of the file) -----
    summary_keys = {
        "Gross Sales": "gross_sales",
        "Total Discount Given": "total_discount",
        "Net Sales": "net_sales",
        "Total GST": "total_gst",
        "Total Sales": "total_sales",
        "Total Cost": "total_cost",
        "Gross Profit": "gross_profit",
        "Number of Sales Transactions": "transactions",
        "Average Sales/Transaction": "avg_sale_per_transaction",
        "Dine In/Takeaway": "dine_in_takeaway",
        "Total Pax": "total_pax",
        "Total Customer Sign Ups": "customer_signups",
        "Member/Non-Member Sales": "member_nonmember_sales",
        "Member/Non-Member Sales Quantity": "member_nonmember_qty",
    }
    summary = {}
    for row in sales_rows:
        if row and row[0].strip() in summary_keys:
            summary[summary_keys[row[0].strip()]] = row[1].strip()

    period_row = sales_rows[1][0]  # "01/01/2026 00:00:00 - 17/08/2026 23:59:59"
    summary["period"] = period_row

    member_sales = summary["member_nonmember_sales"].split("/")
    member_qty = summary["member_nonmember_qty"].split("/")
    summary["member_sales_sgd"] = float(member_sales[0])
    summary["nonmember_sales_sgd"] = float(member_sales[1])
    summary["member_qty"] = int(member_qty[0])
    summary["nonmember_qty"] = int(member_qty[1])

    with open(OUT / "pos_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # --- payment methods ---------------------------------------------------
    header, data = find_section(sales_rows, "Total Settlement by Payment Method", has_header_row=False)
    with open(OUT / "pos_payment_methods.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["method", "amount_sgd"])
        for row in data:
            if row[0].strip() == "Total Settlement":
                continue
            w.writerow([row[0].strip(), money(row[1])])

    # --- sales by tab (top-level channel/category within the wine bar) ----
    header, data = find_section(sales_rows, "Sales by Tab")
    with open(OUT / "pos_category_sales.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tab", "gross_sales_sgd", "quantity_sold", "discount_sgd"])
        for row in data:
            w.writerow([row[0].strip(), money(row[1]), int(row[2]), money(row[3])])

    # --- sales by product (top N by gross sales) ---------------------------
    header, data = find_section(sales_rows, "Sales by Product")
    products = []
    for row in data:
        name, category, gross, barcode, qty, cost, discount, profit = row
        products.append({
            "product_name": name.strip(),
            "category": category.strip(),
            "gross_sales_sgd": money(gross),
            "quantity_sold": int(qty),
            "total_cost_sgd": money(cost),
            "total_discount_sgd": money(discount) if discount.strip() else 0.0,
            "total_profit_sgd": money(profit),
        })
    products.sort(key=lambda p: p["gross_sales_sgd"], reverse=True)
    with open(OUT / "pos_top_products.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(products[0].keys()))
        w.writeheader()
        w.writerows(products[:20])

    # --- discount info -------------------------------------------------
    header, data = find_section(sales_rows, "Discount Information")
    with open(OUT / "pos_discounts.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["discount_name", "amount_sgd", "count"])
        for row in data:
            w.writerow([row[0].strip(), money(row[1]), int(row[2])])

    # --- product catalog composition (Product List CSV) --------------------
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

    print("Wrote:", OUT / "pos_summary.json")
    print("Wrote:", OUT / "pos_payment_methods.csv")
    print("Wrote:", OUT / "pos_category_sales.csv")
    print("Wrote:", OUT / "pos_top_products.csv")
    print("Wrote:", OUT / "pos_discounts.csv")
    print("Wrote:", OUT / "pos_catalog_composition.csv")
    print("\nSummary:", json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
