# Presentation script — Cellar V Online Store Health Dashboard

Target length: **7 minutes** (assignment allows 5-10). Read this as a guide, not a
script to recite word-for-word — talk it, don't read it.

---

## 0:00–0:30 — Open (required elements)

- State your name.
- Hold your government-issued ID up to the camera, clearly legible, for a few seconds.
- One line on the setup: *"I'm going to walk through a business case for Cellar V,
  a wine bar and retail shop I run in Singapore, and a dashboard I built to support
  a real decision I'm facing as the owner."*

## 0:30–1:15 — The business case (stakeholder + decision)

- Stakeholder: **me, as the owner of Cellar V** — not a hypothetical.
- Decision: **where to spend limited time and budget first** — fixing the online
  store, or paying to drive more traffic to it.
- Say this plainly: *"I pulled live data directly from our Shopify store — real
  orders, real inventory, real customer accounts — to see what the data actually
  supports, rather than guess."*

## 1:15–3:00 — Walk the dashboard: The Problem tab

- Share your screen, open the dashboard, land on **The Problem** tab.
- Call out the four KPI tiles in order: lifetime revenue (SGD 176), lifetime
  orders (2), days since last sale (551), % of customers who ever bought (25%).
- Point at the monthly sales chart: *"Two bars in three years of history — both
  in early 2025 — then nothing."*
- Land the insight in one sentence: *"The online channel isn't underperforming,
  it's effectively dormant."*

## 3:00–4:30 — Walk the dashboard: Catalog & Inventory tab

- Switch tabs. Call out: 64 active SKUs, 44% out of stock, 26% of "Best seller"
  tagged wines out of stock.
- Point at the two charts: stock status by price tier, and the best-seller vs.
  rest-of-catalog comparison.
- Land the second insight: *"The catalog isn't the constraint — a customer who
  finds a product we've flagged as a best-seller has roughly a 1-in-4 chance of
  landing on something they can't actually buy."*

## 4:30–5:45 — Course concepts you applied (rubric explicitly grades this)

Name 3–4 concepts and say *what choice each one drove*, e.g.:

- **User-centric design** — the dashboard is organized around the *stakeholder's
  decision* (where to focus first), not around "here's every metric I could
  pull." That's why it's four short tabs, not a wall of charts.
- **Storytelling with data (Knaflic)** — the tab order *is* the narrative arc:
  problem → root cause → recommendation → caveats. I open with the headline
  number (551 days), not a methodology slide, because the audience's first
  question is "how bad is it," not "how was this built."
- **Visual encoding / reducing clutter (Bertin, Few)** — stock status uses a
  fixed **green = in stock / red = out of stock** color pair everywhere, and I
  avoided a dual-axis chart when comparing sales and order count — that's why
  the sales trend only shows one measure at a time.
- **Summarization over raw detail** — the KPI tiles show *percentages and
  totals*, not a table of all 70 SKUs; the full catalog is in the underlying
  data for anyone who wants to drill in, but the story leads with the summary.

## 5:45–6:45 — Recommendation

- Read directly off the **Recommendation** tab: what (restock the 7 out-of-stock
  best-sellers first), who (me, since I control both purchasing and the
  catalog), and the metric to watch (out-of-stock rate, target under 15%).
- Say *why this beats the alternative*: *"Before spending on Meta or Google ads
  to drive more visitors, I want to fix the experience those visitors would
  land on — otherwise I'm paying to make the same conversion problem more
  visible, not solving it."*

## 6:45–7:15 — Assumptions & limitations

- Pick the two that matter most to say out loud: this is *online-only* (the
  physical wine bar's revenue isn't in this data, so this isn't "the business
  is failing"), and the *two-order sample* means the price-tier pattern is a
  hint, not a validated finding.

## 7:15–7:30 — Close

- One sentence: *"Next step is restocking those best-sellers and watching
  whether the out-of-stock rate and days-since-last-sale actually move."*
- Thank the viewer / sign off.

---

### Delivery notes
- Keep your face visible in a webcam window the whole time (screen + face, per
  the assignment requirement).
- Don't read the KPI numbers off the screen verbatim in a monotone — say what
  they *mean* (e.g. "that's a quarter of a year with zero sales," not just
  "551").
- If you go over ~9 minutes in a runthrough, cut from the course-concepts
  section first — it's valuable but the most compressible.
