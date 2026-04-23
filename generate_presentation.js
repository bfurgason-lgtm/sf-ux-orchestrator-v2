/**
 * WISMO Flow Presentation Generator
 * Usage: node generate_presentation.js
 * Output: exports/wolverine/WISMO_presentation.pptx
 */

const PptxGenJS = require("pptxgenjs");
const path = require("path");
const fs = require("fs");

// ─── Design tokens (from reference_design_analysis.json + project convention) ──
const T = {
  // Slide dimensions (16:9 widescreen inches)
  W: 13.33,
  H: 7.5,

  // Colors
  BG: "0A1628",          // dark navy — slide background
  BG_PILL: "1E3A5F",     // pill background (unfilled)
  BG_PILL_ACTIVE: "0070D2", // Salesforce blue — active/current pill
  BG_PILL_EDGE: "C23934", // red for edge case pills
  ACCENT: "0070D2",      // Salesforce blue
  ACCENT_LIGHT: "54A0FF",
  WHITE: "FFFFFF",
  GRAY_LIGHT: "8CA0B3",
  GRAY_MED: "5A6C7D",
  ARROW: "3E6B94",       // connector arrow color

  // Typography
  FONT: "Calibri",
  FONT_TITLE_SIZE: 28,
  FONT_SUBTITLE_SIZE: 13,
  FONT_PILL_SIZE: 8.5,
  FONT_LABEL_SIZE: 7.5,
  FONT_BODY_SIZE: 12,
  FONT_EDGE_TITLE_SIZE: 22,
  FONT_EDGE_BODY_SIZE: 11,

  // Layout
  MARGIN_X: 0.35,
  MARGIN_TOP: 0.25,
  TITLE_H: 0.55,
  PILL_AREA_TOP: 1.08,  // breathing room below accent rule
  PILL_H: 0.30,
  PILL_ROW_H: 0.38,
  ARROW_W: 0.22,
  FRAME_TOP: 1.58,      // pills bottom (1.08+0.30) + 0.20 gap
  FRAME_BOTTOM_MARGIN: 0.18,
  PILL_RADIUS: 0.05,
};

const SCREENS_DIR = path.join(__dirname, "exports/wolverine/screens");
const OUT_PATH    = path.join(__dirname, "exports/wolverine/WISMO_presentation.pptx");

// WISMO step metadata from manifest
const WISMO_STEPS = [
  { num: 1, name: "Greeting",           edge: false },
  { num: 2, name: "ID Collection",      edge: false },
  { num: 3, name: "Order Confirm",      edge: false },
  { num: 4, name: "Status Retrieval",   edge: false },
  { num: 5, name: "Resolution",         edge: false },
  { num: 6, name: "Unmatched Order",    edge: true  },
  { num: 7, name: "Partial Shipment",   edge: true  },
];

const EDGE_STEPS = [
  {
    num: 6,
    name: "Unmatched Order",
    subtitle: "Edge Case — Step 6",
    description:
      "When the customer provides an order number or email that returns no match, " +
      "the agent surfaces an empathetic error state instead of a dead end.\n\n" +
      "What makes this different from the happy path:\n" +
      "• No order record is found in the Salesforce Order object\n" +
      "• Agent offers alternative lookup (email vs. order number)\n" +
      "• Escalation path to 1-800-WOLVERINE if both fail\n" +
      "• A Case record is created to log the failed search attempt\n\n" +
      "Apex: SupportService.logFailedSearch()\n" +
      "OrderTrackingService.suggestAlternatives()",
  },
  {
    num: 7,
    name: "Partial Shipment",
    subtitle: "Edge Case — Step 7",
    description:
      "When an order ships in multiple packages, the standard single-shipment " +
      "status display is insufficient. This step surfaces a split-shipment view.\n\n" +
      "What makes this different from the happy path:\n" +
      "• ShipmentService.getMultipleShipments() returns count > 1\n" +
      "• Each package has its own tracking number and ETA\n" +
      "• UI shows a breakdown card instead of a single status pill\n" +
      "• Second delivery window communicated explicitly\n\n" +
      "Apex: ShipmentService.getMultipleShipments()\n" +
      "DeliveryService.calculateArrivalWindows()",
  },
];

// ─── Helpers ────────────────────────────────────────────────────────────────

function imgPath(flow, stepNum, channel) {
  return path.join(SCREENS_DIR, `${flow}_step-${stepNum}_${channel}@2x.png`);
}

function imgExists(flow, stepNum, channel) {
  return fs.existsSync(imgPath(flow, stepNum, channel));
}

// Aspect-fit an image into a bounding box, return {w, h, x, y} centered
function aspectFit(imgW, imgH, boxW, boxH, cx, cy) {
  const scale = Math.min(boxW / imgW, boxH / imgH);
  const w = imgW * scale;
  const h = imgH * scale;
  return { w, h, x: cx - w / 2, y: cy - h / 2 };
}

// Native pixel dimensions per channel (from PIL check)
const FRAME_DIMS = {
  web:   { w: 680,  h: 1258 },
  sms:   { w: 780,  h: 1688 },
  email: { w: 1420, h: 328  },
};

// ─── Slide builders ─────────────────────────────────────────────────────────

function addBackground(slide) {
  slide.addShape("rect", {
    x: 0, y: 0, w: T.W, h: T.H,
    fill: { color: T.BG },
    line: { color: T.BG },
  });
}

// Thin accent bar under the title area
function addTitleBar(slide, title, subtitle) {
  // Title
  slide.addText(title, {
    x: T.MARGIN_X, y: T.MARGIN_TOP,
    w: T.W - T.MARGIN_X * 2, h: 0.40,
    fontSize: T.FONT_TITLE_SIZE,
    fontFace: T.FONT,
    bold: true,
    color: T.WHITE,
    valign: "middle",
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: T.MARGIN_X, y: T.MARGIN_TOP + 0.40,
      w: T.W - T.MARGIN_X * 2, h: 0.22,
      fontSize: T.FONT_SUBTITLE_SIZE,
      fontFace: T.FONT,
      color: T.GRAY_LIGHT,
      valign: "top",
    });
  }
  // Accent rule — sits between subtitle and pill row with clear breathing room
  slide.addShape("rect", {
    x: T.MARGIN_X, y: 0.90,
    w: T.W - T.MARGIN_X * 2, h: 0.025,
    fill: { color: T.ACCENT },
    line: { color: T.ACCENT },
  });
}

/**
 * Draw the pill row for steps.
 * steps: array of { num, name, edge, active }
 * Returns the y-bottom of the pill row.
 */
function addPillRow(slide, steps, startX, rowY) {
  const usableW = T.W - T.MARGIN_X * 2;
  const n = steps.length;
  const arrowCount = n - 1;
  const totalArrowW = arrowCount * T.ARROW_W;
  const pillW = (usableW - totalArrowW) / n;

  let x = startX;

  steps.forEach((step, i) => {
    const fillColor = step.active
      ? (step.edge ? T.BG_PILL_EDGE : T.BG_PILL_ACTIVE)
      : T.BG_PILL;
    const borderColor = step.active
      ? (step.edge ? T.BG_PILL_EDGE : T.ACCENT)
      : T.ARROW;
    const textColor = step.active ? T.WHITE : T.GRAY_LIGHT;
    const stepLabel = `${step.num}. ${step.name}`;

    // Pill rectangle
    slide.addShape("roundRect", {
      x, y: rowY,
      w: pillW, h: T.PILL_H,
      rectRadius: T.PILL_RADIUS,
      fill: { color: fillColor },
      line: { color: borderColor, w: step.active ? 1.5 : 0.75 },
    });

    // Step number label
    slide.addText(stepLabel, {
      x: x + 0.04, y: rowY + 0.01,
      w: pillW - 0.08, h: T.PILL_H - 0.02,
      fontSize: T.FONT_PILL_SIZE,
      fontFace: T.FONT,
      bold: step.active,
      color: textColor,
      align: "center",
      valign: "middle",
      wrap: true,
    });

    x += pillW;

    // Arrow connector (not after last pill)
    if (i < steps.length - 1) {
      const arrowY = rowY + T.PILL_H / 2;
      slide.addShape("line", {
        x, y: arrowY,
        w: T.ARROW_W, h: 0,
        line: { color: T.ARROW, w: 1 },
      });
      // Arrowhead triangle
      slide.addShape("triangle", {
        x: x + T.ARROW_W - 0.07, y: arrowY - 0.055,
        w: 0.07, h: 0.11,
        flipH: false,
        rotate: 90,
        fill: { color: T.ARROW },
        line: { color: T.ARROW },
      });
      x += T.ARROW_W;
    }
  });

  return rowY + T.PILL_ROW_H;
}

/**
 * Main flow slide: title + pill row + N frame images (web & sms).
 */
function buildMainFlowSlide(pptx, steps, channel, channelLabel, isOverflow) {
  const slide = pptx.addSlide();
  addBackground(slide);

  const slideTitle = isOverflow
    ? `${channelLabel} Channel (cont.)`
    : `${channelLabel} Channel`;
  const subtitle = `WISMO Flow — ${steps.length} Step${steps.length > 1 ? "s" : ""}`;
  addTitleBar(slide, slideTitle, subtitle);

  const allSteps = WISMO_STEPS.slice(0, 5).map(s => ({
    ...s,
    active: steps.some(st => st.num === s.num),
  }));
  addPillRow(slide, allSteps, T.MARGIN_X, T.PILL_AREA_TOP);

  const frameAreaTop = T.FRAME_TOP;
  const frameAreaH = T.H - frameAreaTop - T.FRAME_BOTTOM_MARGIN;
  const n = steps.length;
  const usableW = T.W - T.MARGIN_X * 2;
  const cellW = usableW / n;
  const imgPad = 0.12;

  steps.forEach((step, i) => {
    const cellX = T.MARGIN_X + i * cellW;
    const boxW = cellW - imgPad * 2;
    const boxH = frameAreaH - 0.28;
    const cx = cellX + cellW / 2;
    const cy = frameAreaTop + boxH / 2;

    const dims = FRAME_DIMS[channel];
    const fit = aspectFit(dims.w, dims.h, boxW, boxH, cx, cy);

    if (imgExists("WISMO", step.num, channel)) {
      slide.addImage({
        path: imgPath("WISMO", step.num, channel),
        x: fit.x, y: fit.y,
        w: fit.w, h: fit.h,
      });
    }

    slide.addText(`Step ${step.num}`, {
      x: cellX, y: T.H - 0.32,
      w: cellW, h: 0.22,
      fontSize: T.FONT_LABEL_SIZE,
      fontFace: T.FONT,
      color: T.GRAY_LIGHT,
      align: "center",
      valign: "middle",
    });
  });
}

/**
 * Email flow slide — two-column stacked layout.
 * Left column: steps 1–3 stacked top-to-bottom.
 * Right column: steps 4–5 stacked top-to-bottom.
 * Each email frame is rendered full column width with a step label above it.
 */
function buildEmailFlowSlide(pptx, steps, channelLabel) {
  const slide = pptx.addSlide();
  addBackground(slide);

  addTitleBar(slide, `${channelLabel} Channel`, `WISMO Flow — ${steps.length} Steps`);

  const allSteps = WISMO_STEPS.slice(0, 5).map(s => ({
    ...s,
    active: steps.some(st => st.num === s.num),
  }));
  addPillRow(slide, allSteps, T.MARGIN_X, T.PILL_AREA_TOP);

  const contentTop = T.FRAME_TOP;
  const contentH = T.H - contentTop - T.FRAME_BOTTOM_MARGIN;
  const usableW = T.W - T.MARGIN_X * 2;
  const colGap = 0.35;
  const colW = (usableW - colGap) / 2;

  // Email frame renders at full column width
  const dims = FRAME_DIMS["email"];
  const imgH = colW / (dims.w / dims.h); // maintain aspect ratio
  const labelH = 0.20;
  const labelSize = 8;
  const itemGap = 0.16; // vertical gap between stacked items

  // Split steps: left col = first 3, right col = remainder
  const leftSteps  = steps.slice(0, 3);
  const rightSteps = steps.slice(3);

  function renderColumn(colSteps, colX) {
    let y = contentTop;
    colSteps.forEach((step, i) => {
      // Step label
      slide.addText(`Step ${step.num} — ${step.name}`, {
        x: colX, y,
        w: colW, h: labelH,
        fontSize: labelSize,
        fontFace: T.FONT,
        bold: true,
        color: T.GRAY_LIGHT,
        valign: "middle",
      });
      y += labelH;

      // Email screenshot — full col width
      if (imgExists("WISMO", step.num, "email")) {
        slide.addImage({
          path: imgPath("WISMO", step.num, "email"),
          x: colX, y,
          w: colW, h: imgH,
        });
      }
      y += imgH;

      // Gap between items (not after last)
      if (i < colSteps.length - 1) y += itemGap;
    });
  }

  // Left column
  renderColumn(leftSteps, T.MARGIN_X);

  // Thin divider
  slide.addShape("line", {
    x: T.MARGIN_X + colW + colGap / 2,
    y: contentTop,
    w: 0, h: contentH,
    line: { color: T.ARROW, w: 0.75 },
  });

  // Right column
  renderColumn(rightSteps, T.MARGIN_X + colW + colGap);
}

/**
 * Edge case slide: two-column, left=title+desc, right=single frame (web only).
 */
function buildEdgeCaseSlide(pptx, edgeStep) {
  const slide = pptx.addSlide();
  addBackground(slide);

  // Header
  addTitleBar(slide, edgeStep.name, edgeStep.subtitle);

  const contentTop = 1.05;
  const contentH = T.H - contentTop - T.FRAME_BOTTOM_MARGIN;
  const colGap = 0.30;
  const leftW = 5.20;
  const rightX = T.MARGIN_X + leftW + colGap;
  const rightW = T.W - rightX - T.MARGIN_X;

  // Left column: description
  slide.addText(edgeStep.description, {
    x: T.MARGIN_X, y: contentTop,
    w: leftW, h: contentH,
    fontSize: T.FONT_EDGE_BODY_SIZE,
    fontFace: T.FONT,
    color: T.GRAY_LIGHT,
    valign: "top",
    wrap: true,
    lineSpacingMultiple: 1.25,
  });

  // Right column: large frame image
  const dims = FRAME_DIMS["web"];
  const boxW = rightW - 0.10;
  const boxH = contentH;
  const cx = rightX + rightW / 2;
  const cy = contentTop + contentH / 2;
  const fit = aspectFit(dims.w, dims.h, boxW, boxH, cx, cy);

  if (imgExists("WISMO", edgeStep.num, "web")) {
    slide.addImage({
      path: imgPath("WISMO", edgeStep.num, "web"),
      x: fit.x, y: fit.y,
      w: fit.w, h: fit.h,
    });
  }

  // Thin vertical divider between columns
  slide.addShape("line", {
    x: T.MARGIN_X + leftW + colGap / 2,
    y: contentTop,
    w: 0, h: contentH,
    line: { color: T.ARROW, w: 0.75 },
  });
}

// ─── Cover slide ─────────────────────────────────────────────────────────────

function buildCoverSlide(pptx) {
  const slide = pptx.addSlide();
  addBackground(slide);

  // Large accent bar top
  slide.addShape("rect", {
    x: 0, y: 0, w: T.W, h: 0.08,
    fill: { color: T.ACCENT },
    line: { color: T.ACCENT },
  });

  // Main title
  slide.addText("WISMO", {
    x: 1.0, y: 1.8,
    w: T.W - 2.0, h: 1.0,
    fontSize: 56,
    fontFace: T.FONT,
    bold: true,
    color: T.WHITE,
    align: "center",
    valign: "middle",
  });

  slide.addText("Where Is My Order", {
    x: 1.0, y: 2.75,
    w: T.W - 2.0, h: 0.45,
    fontSize: 20,
    fontFace: T.FONT,
    color: T.ACCENT_LIGHT,
    align: "center",
  });

  slide.addText("Agentforce Conversation Flow — Channel Design Readout", {
    x: 1.0, y: 3.25,
    w: T.W - 2.0, h: 0.35,
    fontSize: 13,
    fontFace: T.FONT,
    color: T.GRAY_LIGHT,
    align: "center",
  });

  // Divider
  slide.addShape("rect", {
    x: T.W / 2 - 1.5, y: 3.70,
    w: 3.0, h: 0.025,
    fill: { color: T.ACCENT },
    line: { color: T.ACCENT },
  });

  slide.addText("Wolverine Worldwide  ·  Web · SMS · Email  ·  Spring 2026", {
    x: 1.0, y: 3.82,
    w: T.W - 2.0, h: 0.30,
    fontSize: 11,
    fontFace: T.FONT,
    color: T.GRAY_MED,
    align: "center",
  });

  // Channel chips
  const chips = ["Web", "SMS", "Email"];
  const chipW = 1.0;
  const chipH = 0.28;
  const totalChipsW = chips.length * chipW + (chips.length - 1) * 0.2;
  let cx = (T.W - totalChipsW) / 2;
  chips.forEach(ch => {
    slide.addShape("roundRect", {
      x: cx, y: 4.30,
      w: chipW, h: chipH,
      rectRadius: 0.06,
      fill: { color: T.BG_PILL },
      line: { color: T.ACCENT, w: 1 },
    });
    slide.addText(ch, {
      x: cx, y: 4.30,
      w: chipW, h: chipH,
      fontSize: 10,
      fontFace: T.FONT,
      bold: true,
      color: T.WHITE,
      align: "center",
      valign: "middle",
    });
    cx += chipW + 0.2;
  });

  // Footer
  slide.addText("Wolverine Worldwide  ·  Agentforce", {
    x: T.MARGIN_X, y: T.H - 0.30,
    w: T.W - T.MARGIN_X * 2, h: 0.22,
    fontSize: 8,
    fontFace: T.FONT,
    color: T.GRAY_MED,
    align: "right",
  });
}

// ─── Section divider ─────────────────────────────────────────────────────────

function buildSectionDivider(pptx, label, sub) {
  const slide = pptx.addSlide();
  addBackground(slide);

  slide.addShape("rect", {
    x: 0, y: 0, w: T.W, h: 0.08,
    fill: { color: T.ACCENT },
    line: { color: T.ACCENT },
  });

  slide.addText(label, {
    x: 1.0, y: 2.6,
    w: T.W - 2.0, h: 0.8,
    fontSize: 42,
    fontFace: T.FONT,
    bold: true,
    color: T.WHITE,
    align: "center",
    valign: "middle",
  });

  if (sub) {
    slide.addText(sub, {
      x: 1.0, y: 3.45,
      w: T.W - 2.0, h: 0.35,
      fontSize: 14,
      fontFace: T.FONT,
      color: T.GRAY_LIGHT,
      align: "center",
    });
  }

  slide.addShape("rect", {
    x: T.W / 2 - 1.0, y: 3.88,
    w: 2.0, h: 0.025,
    fill: { color: T.ACCENT },
    line: { color: T.ACCENT },
  });
}

// ─── Main ────────────────────────────────────────────────────────────────────

async function main() {
  const pptx = new PptxGenJS();

  pptx.layout = "LAYOUT_WIDE";
  pptx.title  = "WISMO — Agentforce Flow Readout";
  pptx.author = "SF UX Orchestrator v2";

  // Cover
  buildCoverSlide(pptx);

  // Main flow steps (1–5) per channel
  const CHANNELS = [
    { key: "web",   label: "Web" },
    { key: "sms",   label: "SMS" },
    { key: "email", label: "Email" },
  ];

  const mainSteps = WISMO_STEPS.filter(s => !s.edge); // steps 1–5

  for (const { key, label } of CHANNELS) {
    buildSectionDivider(
      pptx,
      `${label} Channel`,
      `WISMO Main Flow — Steps 1–${mainSteps.length}`
    );

    // Max 6 per slide — here mainSteps is 5, so always one slide
    const chunks = [];
    for (let i = 0; i < mainSteps.length; i += 6) {
      chunks.push(mainSteps.slice(i, i + 6));
    }
    chunks.forEach((chunk, ci) => {
      if (key === "email") {
        buildEmailFlowSlide(pptx, chunk, label);
      } else {
        buildMainFlowSlide(pptx, chunk, key, label, ci > 0);
      }
    });
  }

  // Edge case section (web only)
  buildSectionDivider(
    pptx,
    "Edge Cases",
    "Web Channel — Exception Paths"
  );

  for (const edgeStep of EDGE_STEPS) {
    buildEdgeCaseSlide(pptx, edgeStep);
  }

  // Write file
  fs.mkdirSync(path.dirname(OUT_PATH), { recursive: true });
  await pptx.writeFile({ fileName: OUT_PATH });
  console.log(`✓ Saved: ${OUT_PATH}`);
}

main().catch(err => { console.error(err); process.exit(1); });
