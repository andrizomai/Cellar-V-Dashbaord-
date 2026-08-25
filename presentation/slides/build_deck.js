/*
 * Cellar V — Business Health data story deck.
 * Palette and fonts taken from the reference deck (Cellar_V_Data_Story.pptx)
 * supplied by the user; content matches the current Streamlit dashboard
 * (app.py) and its combined 2025+2026 POS data.
 */
const pptxgen = require("pptxgenjs");

// ---------------------------------------------------------------------------
// Palette (extracted from reference.pptx theme) + fonts
// ---------------------------------------------------------------------------
const WINE = "5C1A2B";       // primary
const WINE_DARK = "471421";  // deep shade
const BERRY = "6E3345";      // secondary
const GOLD = "C9A227";       // accent
const GOLD_LIGHT = "E3B96B";
const INK = "2B2420";        // near-black warm text
const MUTED = "6B655C";      // warm gray body text
const CREAM = "FDFCFA";      // page background
const SAND = "E5DCD3";       // tint background
const TAN = "D8C9B6";
const WHITE = "FFFFFF";
const RED = "E34948";        // critical/negative

const HEAD_FONT = "Cambria";
const BODY_FONT = "Calibri";

const W = 13.333, H = 7.5;
const MARGIN = 0.5;

function newPres() {
  const p = new pptxgen();
  p.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
  p.defineSlideMaster({ title: "CREAM", background: { color: CREAM } });
  return p;
}

function bgSlide(p, color) {
  const s = p.addSlide();
  s.background = { color };
  return s;
}

function pageNumber(s, n) {
  s.addText(String(n).padStart(2, "0"), {
    x: W - 1.0, y: H - 0.55, w: 0.6, h: 0.35,
    fontFace: BODY_FONT, fontSize: 10, color: MUTED, align: "right",
  });
  s.addText("CELLAR V", {
    x: MARGIN, y: H - 0.55, w: 3, h: 0.35,
    fontFace: BODY_FONT, fontSize: 10, color: MUTED, charSpacing: 2,
  });
}

function eyebrow(s, text, opts = {}) {
  s.addText(text.toUpperCase(), {
    x: opts.x ?? MARGIN, y: opts.y ?? 0.45, w: opts.w ?? 8, h: 0.35,
    fontFace: BODY_FONT, fontSize: 12, bold: true, color: opts.color ?? GOLD,
    charSpacing: 2, margin: 0,
  });
}

function sectionTitle(s, text, opts = {}) {
  s.addText(text, {
    x: opts.x ?? MARGIN, y: opts.y ?? 0.8, w: opts.w ?? 11.3, h: opts.h ?? 1.0,
    fontFace: HEAD_FONT, fontSize: opts.size ?? 30, bold: true, color: opts.color ?? INK,
    margin: 0, lineSpacingMultiple: 1.05,
  });
}

function statTile(s, x, y, w, h, value, label, opts = {}) {
  s.addShape("roundRect", {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: opts.fill ?? WHITE }, line: { color: TAN, width: 1 },
    shadow: { type: "outer", color: "000000", opacity: 0.12, blur: 6, offset: 2, angle: 90 },
  });
  s.addText(value, {
    x: x + 0.15, y: y + 0.12, w: w - 0.3, h: h - 0.62,
    fontFace: HEAD_FONT, fontSize: opts.valueSize ?? 26, bold: true,
    color: opts.valueColor ?? WINE, align: "left", valign: "bottom", margin: 0,
  });
  s.addText(label, {
    x: x + 0.15, y: y + h - 0.48, w: w - 0.3, h: 0.4,
    fontFace: BODY_FONT, fontSize: 11, color: MUTED, align: "left", valign: "top", margin: 0,
  });
}

function readCallout(s, x, y, w, h, text) {
  s.addShape("roundRect", {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: SAND }, line: { type: "none" },
  });
  s.addText([
    { text: "READ  ", options: { bold: true, color: WINE, fontSize: 11, charSpacing: 1 } },
    { text: text, options: { color: INK, fontSize: 13 } },
  ], {
    x: x + 0.25, y: y + 0.18, w: w - 0.5, h: h - 0.36,
    fontFace: BODY_FONT, valign: "top", margin: 0, lineSpacingMultiple: 1.15,
  });
}

function speakerNotes(s, text) {
  s.addNotes(text);
}

// Hand-drawn horizontal bar chart (native shapes, not a chart object) — used
// instead of addChart() because Keynote (the only renderer available for QA
// on this machine) does not reliably import native PPTX chart objects, and
// this project has no working LibreOffice/PowerPoint to cross-check against.
// Shapes render identically everywhere, so this trades chart-object editing
// for guaranteed visual correctness.
function hBarChart(s, x, y, w, h, opts) {
  const { title, categories, values, color, valueFormat } = opts;
  const fmt = valueFormat || ((v) => String(v));
  s.addText(title, {
    x, y, w, h: 0.32, fontFace: HEAD_FONT, fontSize: 13, color: INK, margin: 0,
  });
  const labelW = opts.labelW ?? 1.9;
  const valueW = 0.9;
  const barMaxW = w - labelW - valueW;
  const plotY = y + 0.42;
  const plotH = h - 0.42;
  const n = categories.length;
  const rowH = plotH / n;
  const barH = Math.min(0.3, rowH * 0.5);
  const maxValue = Math.max(...values, 0.0001);
  const x0 = x + labelW;
  categories.forEach((cat, i) => {
    const rowY = plotY + i * rowH;
    const val = values[i];
    const barW = Math.max((val / maxValue) * barMaxW, 0.02);
    s.addText(cat, {
      x, y: rowY, w: labelW - 0.12, h: rowH,
      fontFace: BODY_FONT, fontSize: 10.5, color: MUTED, align: "right", valign: "middle", margin: 0,
    });
    s.addShape("roundRect", {
      x: x0, y: rowY + (rowH - barH) / 2, w: barW, h: barH, rectRadius: 0.02,
      fill: { color: opts.colorFn ? opts.colorFn(cat, i) : color }, line: { type: "none" },
    });
    s.addText(fmt(val), {
      x: x0 + barW + 0.06, y: rowY, w: valueW - 0.06, h: rowH,
      fontFace: BODY_FONT, fontSize: 10, bold: true, color: INK, align: "left", valign: "middle", margin: 0,
    });
  });
}

// Hand-drawn stacked vertical bar chart (native shapes) — see hBarChart note.
function stackedColChart(s, x, y, w, h, opts) {
  const { title, categories, series } = opts; // series: [{name, color, values}]
  s.addText(title, {
    x, y, w: w - 2.2, h: 0.32, fontFace: HEAD_FONT, fontSize: 13, color: INK, margin: 0,
  });
  // legend
  let lx = x + w - 2.1;
  series.forEach((ser) => {
    s.addShape("rect", { x: lx, y: y + 0.06, w: 0.16, h: 0.16, fill: { color: ser.color }, line: { type: "none" } });
    s.addText(ser.name, { x: lx + 0.22, y: y - 0.02, w: 1.0, h: 0.3, fontFace: BODY_FONT, fontSize: 9.5, color: MUTED, margin: 0, valign: "middle" });
    lx += 1.05;
  });

  const n = categories.length;
  const gap = 0.28;
  const marginL = 0.1, marginR = 0.1;
  const usable = w - marginL - marginR;
  const colW = (usable - (n - 1) * gap) / n;
  const plotBottom = y + h - 0.35;
  const plotTop = y + 0.7;
  const plotH = plotBottom - plotTop;
  const totals = categories.map((_, i) => series.reduce((sum, ser) => sum + ser.values[i], 0));
  const maxTotal = Math.max(...totals, 1);

  categories.forEach((cat, i) => {
    const cx = x + marginL + i * (colW + gap);
    let cumH = 0;
    series.forEach((ser) => {
      const val = ser.values[i];
      const segH = (val / maxTotal) * plotH;
      if (val > 0) {
        s.addShape("rect", {
          x: cx, y: plotBottom - cumH - segH, w: colW, h: segH,
          fill: { color: ser.color }, line: { color: CREAM, width: 1 },
        });
        if (segH > 0.22) {
          s.addText(String(val), {
            x: cx, y: plotBottom - cumH - segH, w: colW, h: segH,
            fontFace: BODY_FONT, fontSize: 9.5, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0,
          });
        }
      }
      cumH += segH;
    });
    s.addText(cat, {
      x: cx - 0.15, y: plotBottom + 0.06, w: colW + 0.3, h: 0.3,
      fontFace: BODY_FONT, fontSize: 9.5, color: MUTED, align: "center", margin: 0,
    });
  });
  s.addShape("line", { x, y: plotBottom, w, h: 0, line: { color: TAN, width: 1 } });
}

// ===========================================================================
const p = newPres();
let n = 0;

// --- SLIDE 1: Title ---------------------------------------------------------
{
  const s = bgSlide(p, WINE);
  s.addShape("rect", { x: 0, y: 0, w: W, h: H, fill: { color: WINE }, line: { type: "none" } });
  s.addText("MSBA  ·  COMMUNICATING WITH DATA", {
    x: MARGIN, y: 1.0, w: 10, h: 0.4,
    fontFace: BODY_FONT, fontSize: 13, bold: true, color: GOLD_LIGHT, charSpacing: 2, margin: 0,
  });
  s.addText([
    { text: "Cellar V:\n", options: { color: WHITE } },
    { text: "Where Should the Next Dollar Go?", options: { color: GOLD_LIGHT } },
  ], {
    x: MARGIN, y: 1.5, w: 11.5, h: 2.6,
    fontFace: HEAD_FONT, fontSize: 48, bold: true, margin: 0, lineSpacingMultiple: 1.05,
  });
  s.addText(
    "A data story built on 19 months of point-of-sale history (2025 through 2026 year-to-date) " +
    "and Cellar V's Shopify store — presented as the Analytics App project.",
    {
      x: MARGIN, y: 4.15, w: 9.5, h: 0.9,
      fontFace: BODY_FONT, fontSize: 15, color: "E7DCD5", margin: 0, lineSpacingMultiple: 1.2,
    }
  );
  s.addShape("line", { x: MARGIN, y: 5.35, w: 3, h: 0, line: { color: GOLD, width: 1.5 } });
  s.addText("Presented by Andre  ·  Owner, Cellar V", {
    x: MARGIN, y: 5.55, w: 8, h: 0.4,
    fontFace: BODY_FONT, fontSize: 14, bold: true, color: WHITE, margin: 0,
  });
  s.addText("Prepared for Cellar V's owner and investors", {
    x: MARGIN, y: 5.92, w: 8, h: 0.35,
    fontFace: BODY_FONT, fontSize: 12, color: "E7DCD5", margin: 0,
  });
  s.addText("cellar-v.com.sg   ·   January 2025 – August 2026", {
    x: MARGIN, y: H - 0.7, w: 8, h: 0.35,
    fontFace: BODY_FONT, fontSize: 11, color: GOLD_LIGHT, margin: 0,
  });
  speakerNotes(s,
    "Hi, my name is Andre. [Hold your government-issued ID up to the camera here, per the " +
    "assignment requirements, and state your name clearly.] Today I'm presenting a data story " +
    "for Cellar V, the Singapore wine bar and retail shop I run — built for both myself as owner " +
    "and for our investors. I'll walk through a live analytics app built on our combined 2025-2026 " +
    "point-of-sale data and our Shopify store, answering one question: across the whole business, " +
    "where should we focus next."
  );
}

// --- SLIDE 2: The Business Case --------------------------------------------
{
  n++;
  const s = bgSlide(p, CREAM);
  eyebrow(s, "The Business Case");
  sectionTitle(s, "Two years of real transaction data —\nbut no single view of where to focus next.", { size: 27, h: 1.3 });
  s.addText(
    "Cellar V runs a physical wine bar on a POS system logging every transaction — 2,363 of them " +
    "since the start of 2025, spanning wine, sake, liquor, beer and food — plus a Shopify store for " +
    "online sales. Revenue looks healthy in person, but the channel split, discount leakage, category " +
    "mix and membership behaviour all sit outside daily view. So the executive question becomes:",
    {
      x: MARGIN, y: 2.25, w: 7.3, h: 1.5,
      fontFace: BODY_FONT, fontSize: 14, color: INK, margin: 0, lineSpacingMultiple: 1.25,
    }
  );
  s.addShape("roundRect", {
    x: MARGIN, y: 3.85, w: 7.3, h: 1.35, rectRadius: 0.08,
    fill: { color: WINE }, line: { type: "none" },
  });
  s.addText(
    "\u201CWhere should Cellar V\u2019s owner and investors put the next dollar and the next hour of " +
    "attention \u2014 in-person discipline, membership growth, or the online channel?\u201D",
    {
      x: MARGIN + 0.3, y: 3.95, w: 6.7, h: 1.15,
      fontFace: HEAD_FONT, italic: true, fontSize: 16, color: WHITE, valign: "middle", margin: 0, lineSpacingMultiple: 1.2,
    }
  );

  // Right-side stakeholder / decision / data-answers stack
  const rx = 8.15, rw = 4.65;
  const rows = [
    ["STAKEHOLDER", "Owner + Investors", "Andre (owner-operator) and Cellar V\u2019s capital stakeholders"],
    ["DECISION", "Where to prioritize\nnext-quarter focus", "In-person discipline, membership growth, or the online channel"],
    ["DATA ANSWERS", "4 signal layers", "Channel comparison \u00b7 category mix \u00b7 discount & membership economics \u00b7 online health"],
  ];
  let ry = 1.55;
  rows.forEach(([label, big, small]) => {
    s.addText(label, { x: rx, y: ry, w: rw, h: 0.3, fontFace: BODY_FONT, fontSize: 11, bold: true, color: GOLD_LIGHT === GOLD_LIGHT ? "A7842A" : GOLD, charSpacing: 1.5, margin: 0 });
    s.addText(big, { x: rx, y: ry + 0.28, w: rw, h: 0.55, fontFace: HEAD_FONT, fontSize: 17, bold: true, color: WINE, margin: 0, lineSpacingMultiple: 1.0 });
    s.addText(small, { x: rx, y: ry + 0.85, w: rw, h: 0.7, fontFace: BODY_FONT, fontSize: 11.5, color: MUTED, margin: 0, lineSpacingMultiple: 1.15 });
    ry += 1.72;
  });

  pageNumber(s, n + 1);
  speakerNotes(s,
    "Cellar V is a Singapore wine bar and retail shop, running on a POS system that logs every " +
    "transaction, plus a Shopify store online. The stakeholders here are me as owner-operator and " +
    "our investors. The decision each quarter is where to put limited time and capital: in-person " +
    "discount discipline, membership growth, or the dormant online channel. The data needs to answer " +
    "four things: how the two channels compare, where revenue actually comes from, where margin is " +
    "leaking, and which customers are worth investing in."
  );
}

// --- SLIDE 3: The Narrative --------------------------------------------------
{
  n++;
  const s = bgSlide(p, CREAM);
  eyebrow(s, "The Narrative");
  sectionTitle(s, "Five story points, each answering one\nexecutive question in turn.", { size: 27, h: 1.3 });

  const items = [
    ["01", "The Full Picture", "Is the business healthy?", "Channel comparison \u2014 in-person vs. online, and year over year."],
    ["02", "Where the Money\nComes From", "What\u2019s actually selling?", "Revenue by category \u2014 wine mix and SKU concentration."],
    ["03", "Margin &\nMembership", "What\u2019s it costing us,\nand who\u2019s valuable?", "Discount rate by category, plus member vs. non-member value."],
    ["04", "The Online\nChannel", "Should we fix\nthe website?", "Stock-outs and conversion on the Shopify store."],
    ["05", "The\nRecommendation", "So what do\nwe do?", "Three prioritized levers with expected impact."],
  ];
  const colW = 2.26, gap = 0.12, startX = MARGIN, y0 = 2.35, colH = 4.15;
  items.forEach(([num, title, q, desc], i) => {
    const x = startX + i * (colW + gap);
    s.addShape("roundRect", {
      x, y: y0, w: colW, h: colH, rectRadius: 0.08,
      fill: { color: i === 4 ? WINE : WHITE }, line: { color: TAN, width: i === 4 ? 0 : 1 },
    });
    s.addText(num, {
      x: x + 0.18, y: y0 + 0.18, w: colW - 0.36, h: 0.55,
      fontFace: HEAD_FONT, fontSize: 26, bold: true, color: i === 4 ? GOLD_LIGHT : GOLD, margin: 0,
    });
    s.addText(title, {
      x: x + 0.18, y: y0 + 0.75, w: colW - 0.36, h: 0.85,
      fontFace: HEAD_FONT, fontSize: 15, bold: true, color: i === 4 ? WHITE : INK, margin: 0, lineSpacingMultiple: 1.05,
    });
    s.addText(q, {
      x: x + 0.18, y: y0 + 1.65, w: colW - 0.36, h: 0.65,
      fontFace: BODY_FONT, italic: true, fontSize: 11.5, color: i === 4 ? GOLD_LIGHT : WINE, margin: 0, lineSpacingMultiple: 1.1,
    });
    s.addText(desc, {
      x: x + 0.18, y: y0 + 2.35, w: colW - 0.36, h: 1.65,
      fontFace: BODY_FONT, fontSize: 10.5, color: i === 4 ? "E7DCD5" : MUTED, margin: 0, lineSpacingMultiple: 1.2,
    });
  });

  pageNumber(s, n + 1);
  speakerNotes(s,
    "I'll walk through this as five story points, each answering one executive question and " +
    "handing off to the next: the full picture across both channels, where the money comes from, " +
    "where margin leaks and who's valuable, whether the online channel is worth fixing, and finally " +
    "the recommendation."
  );
}

// --- SLIDE 4: The Artefact ---------------------------------------------------
{
  n++;
  const s = bgSlide(p, CREAM);
  eyebrow(s, "The Artefact");
  sectionTitle(s, "A lightweight Streamlit app, built on\ncombined POS and Shopify data.", { size: 27, h: 1.3 });
  s.addText(
    "Six linked tabs mirror the story points on this deck, reading live from the combined 2025-2026 " +
    "POS exports and the Shopify Admin API. The figures on the following slides come directly from " +
    "this app.",
    {
      x: MARGIN, y: 2.3, w: 11.3, h: 0.8,
      fontFace: BODY_FONT, fontSize: 14, color: INK, margin: 0, lineSpacingMultiple: 1.25,
    }
  );

  const tabs = [
    ["1", "The Full Picture", "Channel comparison & by-year KPIs"],
    ["2", "Where the Money\nComes From", "Revenue by category & top SKUs"],
    ["3", "Margin &\nMembership", "Discount rate by category & member value"],
    ["4", "Online Channel", "Stock status & conversion"],
    ["5", "Recommendation", "Three prioritized levers"],
    ["6", "Assumptions &\nLimitations", "What would change this analysis"],
  ];
  const colW = 3.65, gap = 0.2, startX = MARGIN, y0 = 3.25, colH = 1.35;
  tabs.forEach(([num, title, desc], i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = startX + col * (colW + gap);
    const y = y0 + row * (colH + 0.18);
    s.addShape("roundRect", { x, y, w: colW, h: colH, rectRadius: 0.08, fill: { color: WHITE }, line: { color: TAN, width: 1 } });
    s.addShape("ellipse", { x: x + 0.2, y: y + 0.18, w: 0.4, h: 0.4, fill: { color: WINE }, line: { type: "none" } });
    s.addText(num, { x: x + 0.2, y: y + 0.18, w: 0.4, h: 0.4, fontFace: HEAD_FONT, bold: true, fontSize: 14, color: WHITE, align: "center", valign: "middle", margin: 0 });
    s.addText(title, { x: x + 0.72, y: y + 0.1, w: colW - 0.9, h: 0.6, fontFace: HEAD_FONT, bold: true, fontSize: 12, color: INK, margin: 0, lineSpacingMultiple: 1.02 });
    s.addText(desc, { x: x + 0.2, y: y + 0.82, w: colW - 0.4, h: 0.48, fontFace: BODY_FONT, fontSize: 9.5, color: MUTED, margin: 0, lineSpacingMultiple: 1.1 });
  });

  s.addText("\u25b6  Live demo: this is the point in the recording where I switch to screen-share and walk through the app itself.", {
    x: MARGIN, y: y0 + 2 * (colH + 0.18) + 0.15, w: 11.3, h: 0.35,
    fontFace: BODY_FONT, italic: true, fontSize: 12, color: WINE, margin: 0,
  });

  pageNumber(s, n + 1);
  speakerNotes(s,
    "I built this as a lightweight Streamlit app connected to our combined POS export and the " +
    "Shopify API \u2014 six linked tabs mirroring the story points on this deck. [This is the cue to " +
    "switch to your screen share and demo the live app for a couple of minutes before returning to " +
    "the slides for the recommendation.]"
  );
}

// --- SLIDE 5: Story 01 - The Full Picture -----------------------------------
{
  n++;
  const s = bgSlide(p, CREAM);
  eyebrow(s, "Story 01 \u00b7 The Full Picture");
  sectionTitle(s, "Is the business healthy?", { size: 27, h: 0.6 });
  s.addText("January 2025 \u2013 August 2026  \u00b7  2,363 transactions  \u00b7  4,618 guests", {
    x: MARGIN, y: 1.42, w: 10, h: 0.35, fontFace: BODY_FONT, fontSize: 13, color: MUTED, margin: 0,
  });

  // Two big channel boxes
  const boxY = 1.95, boxH = 1.75;
  s.addShape("roundRect", { x: MARGIN, y: boxY, w: 5.55, h: boxH, rectRadius: 0.08, fill: { color: WINE }, line: { type: "none" } });
  s.addText("IN-PERSON (POS)", { x: MARGIN + 0.25, y: boxY + 0.18, w: 5, h: 0.3, fontFace: BODY_FONT, bold: true, fontSize: 11, color: GOLD_LIGHT, charSpacing: 1.5, margin: 0 });
  s.addText("S$293,467", { x: MARGIN + 0.25, y: boxY + 0.45, w: 5, h: 0.75, fontFace: HEAD_FONT, bold: true, fontSize: 38, color: WHITE, margin: 0 });
  s.addText("2,363 transactions \u00b7 about S$494 a day", { x: MARGIN + 0.25, y: boxY + 1.28, w: 5, h: 0.4, fontFace: BODY_FONT, fontSize: 12, color: "E7DCD5", margin: 0 });

  const box2X = MARGIN + 5.75;
  s.addShape("roundRect", { x: box2X, y: boxY, w: 5.55, h: boxH, rectRadius: 0.08, fill: { color: WHITE }, line: { color: TAN, width: 1 } });
  s.addText("ONLINE (SHOPIFY), 3-YEAR LIFETIME", { x: box2X + 0.25, y: boxY + 0.18, w: 5, h: 0.3, fontFace: BODY_FONT, bold: true, fontSize: 11, color: MUTED, charSpacing: 1.5, margin: 0 });
  s.addText("S$176", { x: box2X + 0.25, y: boxY + 0.45, w: 5, h: 0.75, fontFace: HEAD_FONT, bold: true, fontSize: 38, color: RED, margin: 0 });
  s.addText("2 orders total \u00b7 nothing in the last 551 days", { x: box2X + 0.25, y: boxY + 1.28, w: 5, h: 0.4, fontFace: BODY_FONT, fontSize: 12, color: MUTED, margin: 0 });

  // By-year mini table
  const tblY = 4.1;
  s.addText("BY YEAR", { x: MARGIN, y: tblY, w: 4, h: 0.3, fontFace: BODY_FONT, bold: true, fontSize: 11, color: GOLD, charSpacing: 1.5, margin: 0 });
  s.addTable(
    [
      [
        { text: "", options: { fill: { color: SAND } } },
        { text: "Gross sales", options: { bold: true, color: INK, fill: { color: SAND } } },
        { text: "Transactions", options: { bold: true, color: INK, fill: { color: SAND } } },
        { text: "Avg. sale", options: { bold: true, color: INK, fill: { color: SAND } } },
        { text: "Discount rate", options: { bold: true, color: INK, fill: { color: SAND } } },
      ],
      [
        { text: "2025 (full year)", options: { bold: true, color: WINE } },
        "S$215,232", "1,556", "S$120.63", "20.0%",
      ],
      [
        { text: "2026 (YTD, through Aug 17)", options: { bold: true, color: WINE } },
        "S$120,617", "807", "S$131.07", "19.5%",
      ],
    ],
    {
      x: MARGIN, y: tblY + 0.35, w: 11.3, h: 1.15,
      fontFace: BODY_FONT, fontSize: 12, color: INK, border: { type: "solid", color: TAN, pt: 0.75 },
      autoPage: false, valign: "middle",
      colW: [3.5, 2, 2, 2, 1.8],
    }
  );

  readCallout(s, MARGIN, 5.75, 11.3, 1.1,
    "The online store\u2019s entire three-year history (S$176) doesn\u2019t add up to half of what the wine " +
    "bar takes in on a single average day (S$494). This isn\u2019t a business in trouble \u2014 it\u2019s a " +
    "business whose website hasn\u2019t caught up with it yet."
  );

  pageNumber(s, n + 1);
  speakerNotes(s,
    "Since the start of 2025, Cellar V has done S$293,467 in-person across 2,363 transactions \u2014 " +
    "about S$494 a day. Compare that to the online store's entire three-year history: S$176, nothing " +
    "in the last 551 days. And the year-over-year numbers show this isn't a one-off \u2014 the discount " +
    "rate and average sale land in a similar range in both 2025 and 2026. The business is healthy; " +
    "the open question is where the next dollar and hour of attention should go."
  );
}

// --- SLIDE 6: Story 02 - Where the Money Comes From -------------------------
{
  n++;
  const s = bgSlide(p, CREAM);
  eyebrow(s, "Story 02 \u00b7 Where the Money Comes From");
  sectionTitle(s, "What\u2019s actually selling?", { size: 27, h: 0.6 });

  // Chart: category gross sales
  hBarChart(s, MARGIN, 1.55, 6.6, 4.55, {
    title: "Gross sales by category, Jan 2025 \u2013 Aug 2026",
    categories: ["Red", "White", "Food", "Other", "Champagne/Sparkling", "Sake", "Liquor", "Rose"],
    values: [198895, 36879, 31589, 27486, 20579, 11096, 8104, 1220],
    color: WINE,
    valueFormat: (v) => v.toLocaleString("en-US"),
    labelW: 1.8,
  });

  // Right column stats
  const rx = 7.85, rw = 4.95;
  statTile(s, rx, 1.55, rw, 1.35, "59%", "of all revenue is Red wine alone \u2014 S$198,895 across 1,995 bottles and glasses");
  statTile(s, rx, 3.05, rw, 1.35, "19%", "of revenue from just the top 10 SKUs \u2014 3% of the 310-item catalog");
  statTile(s, rx, 4.55, rw, 1.35, "S$11,376", "Top seller: Collefrisio In&Out Montepulciano d\u2019Abruzzo DOC 2019");

  readCallout(s, MARGIN, 6.25, 11.3, 0.85,
    "This is a Red-wine bar with a food and white-wine halo, not a broad multi-category retailer \u2014 " +
    "the top sellers are almost entirely Italian reds from Collefrisio and Ca\u2019Botta."
  );

  pageNumber(s, n + 1);
  speakerNotes(s,
    "Red wine is the business \u2014 59% of all revenue, S$198,895, more than every other category " +
    "combined. Food and white wine round out a distant second and third. And it's concentrated: the " +
    "top 10 SKUs, mostly Amarone-style and Collefrisio reds, generate about a fifth of total sales " +
    "from just 3% of the catalog."
  );
}

// --- SLIDE 7: Story 03 - Margin & Membership --------------------------------
{
  n++;
  const s = bgSlide(p, CREAM);
  eyebrow(s, "Story 03 \u00b7 Margin & Membership");
  sectionTitle(s, "What\u2019s it costing us \u2014 and who\u2019s valuable?", { size: 25, h: 0.6 });

  const tileY = 1.55, tileH = 1.05, tileW = 2.7, gap = 0.15;
  statTile(s, MARGIN, tileY, tileW, tileH, "S$66,613", "given away in discounts \u2014 19.8% of gross sales", { valueSize: 22 });
  statTile(s, MARGIN + (tileW + gap), tileY, tileW, tileH, "65%", "gross margin on net sales", { valueSize: 22 });
  statTile(s, MARGIN + 2 * (tileW + gap), tileY, tileW, tileH, "2.5x", "higher average sale from members vs. non-members", { valueSize: 22 });
  statTile(s, MARGIN + 3 * (tileW + gap), tileY, tileW, tileH, "41", "new members in 19 months \u2014 about 2 a month", { valueSize: 22 });

  // Discount rate by category chart
  hBarChart(s, MARGIN, 2.85, 6.6, 3.35, {
    title: "Discount rate by category (Rose excluded \u2014 tiny base)",
    categories: ["Food", "Other", "White", "Sake", "Red", "Champagne/Sparkling", "Liquor"],
    values: [0.016, 0.104, 0.211, 0.216, 0.225, 0.263, 0.308],
    color: GOLD,
    valueFormat: (v) => `${Math.round(v * 100)}%`,
    labelW: 1.8,
  });

  readCallout(s, 6.95, 2.85, 5.85, 3.35,
    "Liquor (31%) and Champagne/Sparkling (26%) are discounted furthest above Food\u2019s under-2% " +
    "baseline \u2014 and the pattern holds separately in both 2025 and 2026, so it isn\u2019t a one-off. " +
    "Meanwhile, member transactions already make up 28% of the till, averaging 2.5x more per sale " +
    "than non-members \u2014 but only 41 people joined as members across the whole 19-month period."
  );

  pageNumber(s, n + 1);
  speakerNotes(s,
    "Here's the leak. We gave away S$66,613 in discounts since the start of 2025 \u2014 19.8% of gross " +
    "sales \u2014 and it's not even: Liquor is discounted 31%, Champagne and Sparkling 26%, while Food " +
    "stays disciplined under 2%. And this rate is nearly identical in 2025 and 2026 separately, so " +
    "it's a pattern, not noise. On the other side, member transactions already average 2.5 times more " +
    "than non-member transactions and make up over a quarter of the till \u2014 but we've only signed up " +
    "41 new members in a year and a half. That's the most under-leveraged lever we have."
  );
}

// --- SLIDE 8: Story 04 - The Online Channel ---------------------------------
{
  n++;
  const s = bgSlide(p, CREAM);
  eyebrow(s, "Story 04 \u00b7 The Online Channel");
  sectionTitle(s, "Should we fix the website?", { size: 27, h: 0.6 });

  const tileY = 1.55, tileH = 1.05, tileW = 2.7, gap = 0.15;
  statTile(s, MARGIN, tileY, tileW, tileH, "44%", "of the 64 active online listings are out of stock", { valueSize: 22, valueColor: RED });
  statTile(s, MARGIN + (tileW + gap), tileY, tileW, tileH, "7 of 27", "\u2018Best seller\u2019-tagged listings out of stock", { valueSize: 22, valueColor: RED });
  statTile(s, MARGIN + 2 * (tileW + gap), tileY, tileW, tileH, "25%", "of registered accounts have ever purchased", { valueSize: 22 });
  statTile(s, MARGIN + 3 * (tileW + gap), tileY, tileW, tileH, "S$176", "lifetime online revenue \u2014 3 full years", { valueSize: 22 });

  stackedColChart(s, MARGIN, 2.85, 6.6, 3.35, {
    title: "Stock status by price tier, online catalog",
    categories: ["<S$50", "S$50-70", "S$70-100", "S$100-150", "S$150+"],
    series: [
      { name: "In stock", color: "2E7D32", values: [12, 15, 6, 3, 0] },
      { name: "Out of stock", color: RED, values: [2, 9, 9, 5, 3] },
    ],
  });

  readCallout(s, 6.95, 2.85, 5.85, 3.35,
    "A real, cheap fix \u2014 restock or unpublish the out-of-stock \u2018Best seller\u2019 listings first. But at " +
    "S$176 lifetime, the online channel is a rounding error next to the S$293,467 in-person business. " +
    "Worth doing \u2014 just not worth doing first."
  );

  pageNumber(s, n + 1);
  speakerNotes(s,
    "The Shopify store itself has a fixable problem: 44% of active listings are out of stock, " +
    "including a quarter of the products we ourselves tag as best-sellers, and only a quarter of " +
    "registered accounts have ever purchased. It's a real, low-cost fix. But at S$176 in lifetime " +
    "revenue against a business doing roughly S$300,000 in-person over the same stretch, it's not " +
    "where the leverage is."
  );
}

// --- SLIDE 9: Story 05 - The Recommendation ---------------------------------
{
  n++;
  const s = bgSlide(p, CREAM);
  eyebrow(s, "Story 05 \u00b7 The Recommendation");
  sectionTitle(s, "Three levers, in priority order.", { size: 27, h: 0.6 });

  const levers = [
    ["1", "Tighten discount\ngovernance", "Cap discretionary discounts on Liquor (31%) and Champagne/Sparkling (26%); require a plain review of what \u201cCustom Discount\u201d actually covers and when staff should use it.", "Illustrative: ~S$16,800 recoverable over a comparable period at a 5-point tighter rate"],
    ["2", "Make membership\npart of checkout", "Add an active sign-up ask at the till, not a passive option. Members already average 2.5x more per sale \u2014 even modest conversion gains compound.", "Target: ~2 \u2192 5+ new members a month"],
    ["3", "Restock the online\nbest-sellers", "Restock or take down the 7 out-of-stock \u2018Best seller\u2019 listings on Shopify so featured pages are actually purchasable.", "Cheap, quick fix \u2014 just not the highest-leverage one"],
  ];
  const colW = 3.63, gap = 0.2, y0 = 1.65, colH = 4.9;
  levers.forEach(([num, title, desc, impact], i) => {
    const x = MARGIN + i * (colW + gap);
    s.addShape("roundRect", { x, y: y0, w: colW, h: colH, rectRadius: 0.08, fill: { color: i === 0 ? WINE : WHITE }, line: { color: TAN, width: i === 0 ? 0 : 1 } });
    s.addShape("ellipse", { x: x + 0.25, y: y0 + 0.25, w: 0.55, h: 0.55, fill: { color: i === 0 ? GOLD : WINE }, line: { type: "none" } });
    s.addText(num, { x: x + 0.25, y: y0 + 0.25, w: 0.55, h: 0.55, fontFace: HEAD_FONT, bold: true, fontSize: 20, color: WHITE, align: "center", valign: "middle", margin: 0 });
    s.addText(title, { x: x + 0.25, y: y0 + 0.95, w: colW - 0.5, h: 0.85, fontFace: HEAD_FONT, bold: true, fontSize: 16, color: i === 0 ? WHITE : INK, margin: 0, lineSpacingMultiple: 1.05 });
    s.addText(desc, { x: x + 0.25, y: y0 + 1.85, w: colW - 0.5, h: 2.05, fontFace: BODY_FONT, fontSize: 11.5, color: i === 0 ? "E7DCD5" : MUTED, margin: 0, lineSpacingMultiple: 1.25 });
    s.addShape("line", { x: x + 0.25, y: y0 + colH - 1.05, w: colW - 0.5, h: 0, line: { color: i === 0 ? GOLD : TAN, width: 1 } });
    s.addText(impact, { x: x + 0.25, y: y0 + colH - 0.9, w: colW - 0.5, h: 0.8, fontFace: BODY_FONT, italic: true, bold: true, fontSize: 11, color: i === 0 ? GOLD_LIGHT : WINE, margin: 0, lineSpacingMultiple: 1.15 });
  });

  pageNumber(s, n + 1);
  speakerNotes(s,
    "Three moves, in priority order. First, tighten discount governance on Liquor and " +
    "Champagne/Sparkling \u2014 that alone is worth an estimated S$16,800 over a comparable period, " +
    "several times the online channel's entire lifetime revenue. Second, make membership sign-up " +
    "part of the checkout flow \u2014 members already spend 2.5 times more per sale. Third, restock the " +
    "handful of out-of-stock best-sellers online \u2014 cheap, but not where the leverage is."
  );
}

// --- SLIDE 10: Assumptions & What Would Change This -------------------------
{
  n++;
  const s = bgSlide(p, CREAM);
  eyebrow(s, "Assumptions & Limitations");
  sectionTitle(s, "What would change this analysis.", { size: 27, h: 0.6 });

  const items = [
    ["Partial-year 2026", "The recovery estimate is an illustration of what the combined numbers imply today \u2014 not a forecast of how guests would respond to less discounting."],
    ["\u201CCustom Discount\u201d is one bucket", "It likely mixes happy-hour pricing, staff comps, and genuine promotions together. The 19.8% rate is a ceiling on discretionary discounting, not proof any one promotion was wrong."],
    ["Member value is correlational", "Members may simply be more frequent or affluent regulars who\u2019d spend more regardless. The 2.5x gap is a reason to test a more active ask, not proof membership itself drives spending."],
    ["Two catalogs, not merged", "The online and in-person product lists run on separate systems with different pricing \u2014 the out-of-stock analysis applies to the online store only, which has no live in-person equivalent."],
  ];
  const colW = 5.5, rowH = 2.15, gap = 0.3;
  items.forEach(([title, body], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = MARGIN + col * (colW + gap);
    const y = 1.65 + row * (rowH + 0.25);
    s.addShape("roundRect", { x, y, w: colW, h: rowH, rectRadius: 0.08, fill: { color: WHITE }, line: { color: TAN, width: 1 } });
    s.addText(title, { x: x + 0.25, y: y + 0.2, w: colW - 0.5, h: 0.45, fontFace: HEAD_FONT, bold: true, fontSize: 14, color: WINE, margin: 0 });
    s.addText(body, { x: x + 0.25, y: y + 0.68, w: colW - 0.5, h: rowH - 0.9, fontFace: BODY_FONT, fontSize: 11.5, color: MUTED, margin: 0, lineSpacingMultiple: 1.2 });
  });

  pageNumber(s, n + 1);
  speakerNotes(s,
    "A few honest caveats before I close. Our 2026 figures are year-to-date, not a full year, so the " +
    "recovery estimate is illustrative, not a forecast. The discount line in our POS export is one " +
    "undifferentiated bucket, so I can't yet tell genuine promotions from staff comps. The member " +
    "spending gap is correlational, not proven causal. And the online and in-person catalogs are " +
    "separate systems that I haven't merged into one view."
  );
}

// --- SLIDE 11: Next 90 Days --------------------------------------------------
{
  n++;
  const s = bgSlide(p, CREAM);
  eyebrow(s, "Next 90 Days");
  sectionTitle(s, "Roadmap & the KPIs I\u2019ll track weekly.", { size: 27, h: 0.6 });

  const months = [
    ["Month 1", "Roll out discount policy tiers; launch a POS membership sign-up prompt."],
    ["Month 2", "Track discount rate by category and new sign-ups weekly in the app."],
    ["Month 3", "Review the wine assortment against sell-through; re-measure gross margin."],
  ];
  const colW = 3.63, gap = 0.2, y0 = 1.65, colH = 1.7;
  months.forEach(([m, desc], i) => {
    const x = MARGIN + i * (colW + gap);
    s.addShape("roundRect", { x, y: y0, w: colW, h: colH, rectRadius: 0.08, fill: { color: SAND }, line: { type: "none" } });
    s.addText(m, { x: x + 0.25, y: y0 + 0.18, w: colW - 0.5, h: 0.35, fontFace: HEAD_FONT, bold: true, fontSize: 15, color: WINE, margin: 0 });
    s.addText(desc, { x: x + 0.25, y: y0 + 0.6, w: colW - 0.5, h: colH - 0.8, fontFace: BODY_FONT, fontSize: 12, color: INK, margin: 0, lineSpacingMultiple: 1.2 });
  });

  s.addText("TARGET KPIS", { x: MARGIN, y: 3.75, w: 6, h: 0.3, fontFace: BODY_FONT, bold: true, fontSize: 11, color: GOLD, charSpacing: 1.5, margin: 0 });
  const kpis = [
    ["19.8% \u2192 <15%", "Blended discount rate"],
    ["2/mo \u2192 5+/mo", "New member sign-ups"],
    ["65% \u2192 68%+", "Gross margin on net sales"],
  ];
  kpis.forEach(([big, label], i) => {
    const x = MARGIN + i * (colW + gap);
    s.addText(big, { x, y: 4.1, w: colW, h: 0.65, fontFace: HEAD_FONT, bold: true, fontSize: 26, color: WINE, margin: 0 });
    s.addText(label, { x, y: 4.75, w: colW, h: 0.4, fontFace: BODY_FONT, fontSize: 12, color: MUTED, margin: 0 });
  });

  readCallout(s, MARGIN, 5.55, 11.3, 1.15,
    "All three KPIs are live tiles in the Streamlit app, filtered by date range \u2014 so progress against " +
    "this baseline can be re-checked any week without waiting for a new report."
  );

  pageNumber(s, n + 1);
  speakerNotes(s,
    "Over the next 90 days: roll out the discount policy and the POS sign-up prompt in month one, " +
    "track the discount rate by category and new sign-ups weekly through month two, then revisit the " +
    "wine assortment and re-measure gross margin in month three. My targets: bring the blended " +
    "discount rate under 15%, more than double the monthly sign-up pace, and push gross margin from " +
    "65% toward 68% or better."
  );
}

// --- SLIDE 12: Close ----------------------------------------------------------
{
  n++;
  const s = bgSlide(p, WINE);
  s.addShape("rect", { x: 0, y: 0, w: W, h: H, fill: { color: WINE }, line: { type: "none" } });
  s.addText(
    "The biggest lever isn\u2019t more\nmarketing spend.",
    { x: MARGIN, y: 1.9, w: 11, h: 1.5, fontFace: HEAD_FONT, bold: true, fontSize: 36, color: WHITE, margin: 0, lineSpacingMultiple: 1.08 }
  );
  s.addText(
    "It\u2019s tightening what we\u2019re already giving away at the till \u2014 and turning our best guests into members.",
    { x: MARGIN, y: 3.35, w: 9.5, h: 1.0, fontFace: BODY_FONT, italic: true, fontSize: 17, color: GOLD_LIGHT, margin: 0, lineSpacingMultiple: 1.25 }
  );
  s.addShape("line", { x: MARGIN, y: 4.75, w: 3, h: 0, line: { color: GOLD, width: 1.5 } });
  s.addText("Thank you", { x: MARGIN, y: 5.0, w: 6, h: 0.55, fontFace: HEAD_FONT, bold: true, fontSize: 24, color: WHITE, margin: 0 });
  s.addText("Andre  \u00b7  Cellar V, Singapore  \u00b7  drink@cellar-v.com.sg", {
    x: MARGIN, y: 5.55, w: 8, h: 0.4, fontFace: BODY_FONT, fontSize: 13, color: "E7DCD5", margin: 0,
  });
  speakerNotes(s,
    "That's the story: Cellar V's biggest lever isn't more marketing spend \u2014 it's tightening what " +
    "we're already giving away at the till, and turning our best guests into members. Thank you \u2014 " +
    "happy to answer any questions."
  );
}

p.writeFile({ fileName: "Cellar_V_Data_Story.pptx" }).then(() => {
  console.log("Wrote Cellar_V_Data_Story.pptx");
});
