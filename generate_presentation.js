/**
 * Presentation Generator — config-driven, works for any client project.
 *
 * Usage:
 *   node generate_presentation.js --project projects/<client>
 *   node generate_presentation.js --project samples/wolverine   (legacy)
 *
 * Reads:
 *   <project>/manifest.json      — step metadata, email bodies, edge case notes
 *   <project>/config.user.json   — client name, channels, presentation filename
 *   core/config.defaults.json    — fallback values for any missing user config key
 *
 * Writes:
 *   exports/<client_slug>/<presentation_filename>
 *   <project>/artifact_versions.json              — records generation version
 */

const PptxGenJS = require("pptxgenjs");
const path      = require("path");
const fs        = require("fs");

// ─── CLI args ─────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
const projectFlagIdx = args.indexOf("--project");
if (projectFlagIdx === -1 || !args[projectFlagIdx + 1]) {
  console.error("Usage: node generate_presentation.js --project <project-dir>");
  process.exit(1);
}

const PROJECT_DIR  = path.resolve(args[projectFlagIdx + 1]);
const REPO_ROOT    = path.resolve(__dirname);

// ─── Config loader ────────────────────────────────────────────────────────────

function loadConfig() {
  const defaultsPath = path.join(REPO_ROOT, "core", "config.defaults.json");
  const defaults = JSON.parse(fs.readFileSync(defaultsPath, "utf8"));

  const userPath = path.join(PROJECT_DIR, "config.user.json");
  const user = fs.existsSync(userPath)
    ? JSON.parse(fs.readFileSync(userPath, "utf8"))
    : {};

  return { ...defaults, ...user };
}

const CONFIG = loadConfig();

// ─── Manifest loader ──────────────────────────────────────────────────────────

function loadManifest() {
  // build_spec.json wraps manifest under a "manifest" key; manifest.json is the raw form
  const buildSpecPath = path.join(PROJECT_DIR, "build_spec.json");
  const manifestPath  = path.join(PROJECT_DIR, "manifest.json");

  if (fs.existsSync(buildSpecPath)) {
    const bs = JSON.parse(fs.readFileSync(buildSpecPath, "utf8"));
    return bs.manifest || bs;
  }
  if (fs.existsSync(manifestPath)) {
    return JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  }
  throw new Error(`No manifest.json or build_spec.json found in ${PROJECT_DIR}`);
}

const MANIFEST = loadManifest();

// ─── Derived paths ────────────────────────────────────────────────────────────

// Prefer config, then manifest brand, then "client"
const _manifestClientName = (() => {
  try {
    const meta = MANIFEST.initiative_metadata || {};
    return (meta.brand_context && meta.brand_context.primary_brand) || meta.name || null;
  } catch (_) { return null; }
})();
const CLIENT_NAME = (CONFIG.client_name !== "Unnamed Client" && CONFIG.client_name)
  || _manifestClientName
  || "Client";
const CLIENT_SLUG = CONFIG.exports_slug
  || CLIENT_NAME.toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, "");
const PPTX_NAME   = CONFIG.presentation_filename || `${CLIENT_SLUG}_presentation.pptx`;
const SCREENS_DIR = path.join(REPO_ROOT, "exports", CLIENT_SLUG, "screens");
const OUT_PATH    = path.join(REPO_ROOT, "exports", CLIENT_SLUG, PPTX_NAME);
const CHANNELS    = CONFIG.channels || ["web"];

// ─── Design tokens ────────────────────────────────────────────────────────────

const T = {
  W: 13.33,
  H: 7.5,
  BG: "0A1628",
  BG_PILL: "1E3A5F",
  BG_PILL_ACTIVE: "0070D2",
  BG_PILL_EDGE: "C23934",
  ACCENT: "0070D2",
  ACCENT_LIGHT: "54A0FF",
  WHITE: "FFFFFF",
  GRAY_LIGHT: "8CA0B3",
  GRAY_MED: "5A6C7D",
  ARROW: "3E6B94",
  FONT: "Calibri",
  FONT_TITLE_SIZE: 28,
  FONT_SUBTITLE_SIZE: 13,
  FONT_PILL_SIZE: 8.5,
  FONT_LABEL_SIZE: 7.5,
  FONT_BODY_SIZE: 12,
  FONT_EDGE_TITLE_SIZE: 22,
  FONT_EDGE_BODY_SIZE: 11,
  MARGIN_X: 0.35,
  MARGIN_TOP: 0.25,
  TITLE_H: 0.55,
  PILL_AREA_TOP: 1.08,
  PILL_H: 0.30,
  PILL_ROW_H: 0.38,
  ARROW_W: 0.22,
  FRAME_TOP: 1.58,
  FRAME_BOTTOM_MARGIN: 0.18,
  PILL_RADIUS: 0.05,
};

// ─── Step metadata from manifest ──────────────────────────────────────────────

/**
 * Returns step metadata arrays derived from the manifest's first flow matching
 * the given topic, or the first flow if topic is not specified.
 *
 * Returns { allSteps, mainSteps, edgeSteps, emailSteps }
 */
function stepsFromManifest(topic) {
  const flows = MANIFEST.flows || [];
  const flow = topic
    ? flows.find(f => f.topic === topic) || flows[0]
    : flows[0];

  if (!flow) return { allSteps: [], mainSteps: [], edgeSteps: [], emailSteps: [] };

  const allSteps = (flow.steps || []).map(s => ({
    num:  s.step_number,
    name: (s.step_name || `Step ${s.step_number}`).replace(/_/g, " "),
    edge: !!s.is_edge_case,
    raw:  s,
  }));

  const mainSteps  = allSteps.filter(s => !s.edge);
  const edgeSteps  = allSteps.filter(s => s.edge).sort((a, b) => {
    const pa = a.raw.edge_case_priority || 99;
    const pb = b.raw.edge_case_priority || 99;
    return pa - pb;
  });

  // Email steps: non-edge steps that have an email channel payload
  const emailSteps = mainSteps.filter(s => s.raw.channels && s.raw.channels.email);

  return { allSteps, mainSteps, edgeSteps, emailSteps };
}

/**
 * Build the emailMessages array for the email slide
 * from manifest step data for the given flow topic.
 */
function emailMessagesFromManifest(topic) {
  const flows = MANIFEST.flows || [];
  const flow = topic
    ? flows.find(f => f.topic === topic) || flows[0]
    : flows[0];

  if (!flow) return [];

  const AVATAR_COLORS = ["E8A838", "0070D2", "45A049", "C23934", "7B5EA7"];
  const messages = [];

  (flow.steps || []).filter(s => !s.is_edge_case && s.channels && s.channels.email).forEach((s, idx) => {
    const em = s.channels.email;
    const name  = em.sender_name  || "Sender";
    const email = em.sender_email || "";
    const initials = name.split(" ").map(w => w[0]).join("").toUpperCase().slice(0, 2);

    messages.push({
      avatarColor: AVATAR_COLORS[idx % AVATAR_COLORS.length],
      initials,
      senderName: `${name} <${email}>`,
      toAddress:  em.to_address  || "",
      timestamp:  em.timestamp   || "",
      body:       em.body        || "",
    });
  });

  return messages;
}

/**
 * Build EDGE_STEPS-style array from manifest edge case steps for a flow topic.
 */
function edgeStepDescriptionsFromManifest(topic) {
  const { edgeSteps } = stepsFromManifest(topic);

  return edgeSteps.map(s => {
    const raw = s.raw;
    const apexMethods = (raw.proto_bot && raw.proto_bot.apex_methods) || [];

    // Build description from design_notes + proto_bot info, or fall back to utterances
    let desc = raw.design_notes || "";
    if (raw.utterances && raw.utterances.agent) {
      desc += (desc ? "\n\n" : "") + `Agent: "${raw.utterances.agent}"`;
    }
    if (apexMethods.length) {
      desc += "\n\nApex: " + apexMethods.join("\n");
    }

    return {
      num:      s.num,
      name:     s.name,
      subtitle: `Edge Case — Step ${s.num}`,
      description: desc || `Edge case: ${s.name}`,
    };
  });
}

// ─── Image helpers ────────────────────────────────────────────────────────────

function imgPath(flowTopic, stepNum, channel) {
  return path.join(SCREENS_DIR, `${flowTopic}_step-${stepNum}_${channel}@2x.png`);
}

function imgExists(flowTopic, stepNum, channel) {
  return fs.existsSync(imgPath(flowTopic, stepNum, channel));
}

function aspectFit(imgW, imgH, boxW, boxH, cx, cy) {
  const scale = Math.min(boxW / imgW, boxH / imgH);
  const w = imgW * scale;
  const h = imgH * scale;
  return { w, h, x: cx - w / 2, y: cy - h / 2 };
}

const FRAME_DIMS = {
  web:   { w: 680,  h: 1258 },
  sms:   { w: 780,  h: 1688 },
  email: { w: 1420, h: 328  },
};

// Per-step email heights derived from manifest (approximated from email body length),
// or use defaults from prior measured exports if available.
function emailStepHeight(stepNum) {
  const MEASURED = { 1: 328, 2: 480, 6: 480, 7: 480 };
  return MEASURED[stepNum] || 480;
}

// ─── Slide builders (unchanged visual logic, client-agnostic inputs) ──────────

function addBackground(slide) {
  slide.addShape("rect", {
    x: 0, y: 0, w: T.W, h: T.H,
    fill: { color: T.BG },
    line: { color: T.BG },
  });
}

function addTitleBar(slide, title, subtitle) {
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
  slide.addShape("rect", {
    x: T.MARGIN_X, y: 0.90,
    w: T.W - T.MARGIN_X * 2, h: 0.025,
    fill: { color: T.ACCENT },
    line: { color: T.ACCENT },
  });
}

function addPillRow(slide, steps, startX, rowY) {
  const usableW = T.W - T.MARGIN_X * 2;
  const n = steps.length;
  const arrowCount = n - 1;
  const totalArrowW = arrowCount * T.ARROW_W;
  const pillW = (usableW - totalArrowW) / n;

  let x = startX;

  steps.forEach((step, i) => {
    const fillColor   = step.active ? (step.edge ? T.BG_PILL_EDGE : T.BG_PILL_ACTIVE) : T.BG_PILL;
    const borderColor = step.active ? (step.edge ? T.BG_PILL_EDGE : T.ACCENT) : T.ARROW;
    const textColor   = step.active ? T.WHITE : T.GRAY_LIGHT;
    const stepLabel   = `${step.num}. ${step.name}`;

    slide.addShape("roundRect", {
      x, y: rowY,
      w: pillW, h: T.PILL_H,
      rectRadius: T.PILL_RADIUS,
      fill: { color: fillColor },
      line: { color: borderColor, w: step.active ? 1.5 : 0.75 },
    });
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

    if (i < steps.length - 1) {
      const arrowY = rowY + T.PILL_H / 2;
      slide.addShape("line", { x, y: arrowY, w: T.ARROW_W, h: 0, line: { color: T.ARROW, w: 1 } });
      slide.addShape("triangle", {
        x: x + T.ARROW_W - 0.07, y: arrowY - 0.055,
        w: 0.07, h: 0.11,
        flipH: false, rotate: 90,
        fill: { color: T.ARROW },
        line: { color: T.ARROW },
      });
      x += T.ARROW_W;
    }
  });

  return rowY + T.PILL_ROW_H;
}

function buildMainFlowSlide(pptx, flowTopic, steps, mainStepsAll, channel, channelLabel, isOverflow) {
  const slide = pptx.addSlide();
  addBackground(slide);

  const slideTitle = isOverflow ? `${channelLabel} Channel (cont.)` : `${channelLabel} Channel`;
  const subtitle   = `${flowTopic.replace(/_/g, " ")} Flow — ${steps.length} Step${steps.length > 1 ? "s" : ""}`;
  addTitleBar(slide, slideTitle, subtitle);

  const pillSteps = mainStepsAll.map(s => ({ ...s, active: steps.some(st => st.num === s.num) }));
  addPillRow(slide, pillSteps, T.MARGIN_X, T.PILL_AREA_TOP);

  const frameAreaTop = T.FRAME_TOP;
  const frameAreaH   = T.H - frameAreaTop - T.FRAME_BOTTOM_MARGIN;
  const n = steps.length;
  const usableW = T.W - T.MARGIN_X * 2;
  const cellW   = usableW / n;
  const imgPad  = 0.12;

  steps.forEach((step, i) => {
    const cellX = T.MARGIN_X + i * cellW;
    const boxW  = cellW - imgPad * 2;
    const boxH  = frameAreaH - 0.28;
    const cx    = cellX + cellW / 2;
    const cy    = frameAreaTop + boxH / 2;
    const dims  = FRAME_DIMS[channel];
    const fit   = aspectFit(dims.w, dims.h, boxW, boxH, cx, cy);

    if (imgExists(flowTopic, step.num, channel)) {
      slide.addImage({ path: imgPath(flowTopic, step.num, channel), x: fit.x, y: fit.y, w: fit.w, h: fit.h });
    }
    slide.addText(`Step ${step.num}`, {
      x: cellX, y: T.H - 0.32, w: cellW, h: 0.22,
      fontSize: T.FONT_LABEL_SIZE, fontFace: T.FONT,
      color: T.GRAY_LIGHT, align: "center", valign: "middle",
    });
  });
}

function buildEmailFlowSlide(pptx, flowTopic, steps, emailPillStepsAll, channelLabel, messages) {
  const slide = pptx.addSlide();
  addBackground(slide);
  addTitleBar(slide, `${channelLabel} Channel`, `${flowTopic.replace(/_/g, " ")} Flow — ${steps.length} Turn${steps.length !== 1 ? "s" : ""}`);

  const pillSteps = emailPillStepsAll.map(s => ({ ...s, active: steps.some(st => st.num === s.num) }));
  addPillRow(slide, pillSteps, T.MARGIN_X, T.PILL_AREA_TOP);

  const contentTop = T.FRAME_TOP;
  const contentH   = T.H - contentTop - T.FRAME_BOTTOM_MARGIN;
  const usableW    = T.W - T.MARGIN_X * 2;
  const colGap     = 0.30;
  const colW       = (usableW - colGap) / 2;

  const CARD_BG     = "FFFFFF";
  const CARD_BORDER = "D8DDE6";
  const TEXT_DARK   = "1D1D1F";
  const TEXT_MED    = "5A6C7D";
  const CARD_GAP    = 0.14;
  const AVATAR_D    = 0.34;
  const PAD_H       = 0.18;
  const PAD_V       = 0.16;
  const LINE_H      = 0.155;

  function cardHeight(msg) {
    const lines = msg.body.split("\n").reduce((acc, line) => acc + Math.max(1, Math.ceil(line.length / 62)), 0);
    return PAD_V + AVATAR_D + 0.08 + (lines * LINE_H) + PAD_V;
  }

  function drawCard(x, y, w, msg) {
    const h = cardHeight(msg);
    slide.addShape("roundRect", { x, y, w, h, rectRadius: 0.06, fill: { color: CARD_BG }, line: { color: CARD_BORDER, w: 0.75 } });

    slide.addShape("ellipse", { x: x + PAD_H, y: y + PAD_V, w: AVATAR_D, h: AVATAR_D, fill: { color: msg.avatarColor }, line: { color: msg.avatarColor } });
    slide.addText(msg.initials, { x: x + PAD_H, y: y + PAD_V, w: AVATAR_D, h: AVATAR_D, fontSize: 9, fontFace: T.FONT, bold: true, color: CARD_BG, align: "center", valign: "middle" });

    const headerX = x + PAD_H + AVATAR_D + 0.10;
    const headerW = w - PAD_H - AVATAR_D - 0.10 - PAD_H;

    slide.addText(msg.senderName, { x: headerX, y: y + PAD_V, w: headerW - 1.20, h: 0.17, fontSize: 8.5, fontFace: T.FONT, bold: true, color: TEXT_DARK, valign: "middle" });
    slide.addText(msg.timestamp,  { x: x + w - 1.35, y: y + PAD_V, w: 1.25, h: 0.17, fontSize: 7, fontFace: T.FONT, color: TEXT_MED, align: "right", valign: "middle" });
    slide.addText(`to ${msg.toAddress}`, { x: headerX, y: y + PAD_V + 0.17, w: headerW, h: 0.14, fontSize: 7, fontFace: T.FONT, color: TEXT_MED, valign: "middle" });

    const bodyY = y + PAD_V + AVATAR_D + 0.08;
    slide.addText(msg.body, { x: x + PAD_H, y: bodyY, w: w - PAD_H * 2, h: h - (bodyY - y) - PAD_V, fontSize: 8.5, fontFace: T.FONT, color: TEXT_DARK, valign: "top", wrap: true, lineSpacingMultiple: 1.25 });

    return h + CARD_GAP;
  }

  const colXs   = [T.MARGIN_X, T.MARGIN_X + colW + colGap];
  const colTops = [contentTop, contentTop];
  const colYs   = [contentTop, contentTop];
  let col = 0;

  messages.forEach(msg => {
    const h = cardHeight(msg);
    if (col === 0 && colYs[0] + h > contentTop + contentH) col = 1;
    drawCard(colXs[col], colYs[col], colW, msg);
    colYs[col] += h + CARD_GAP;
  });

  if (colYs[1] > colTops[1]) {
    slide.addShape("line", {
      x: T.MARGIN_X + colW + colGap / 2, y: contentTop, w: 0, h: contentH,
      line: { color: T.ARROW, w: 0.75 },
    });
  }
}

function buildEdgeCaseSlide(pptx, flowTopic, edgeStep) {
  const slide = pptx.addSlide();
  addBackground(slide);
  addTitleBar(slide, edgeStep.name, edgeStep.subtitle);

  const contentTop = 1.05;
  const contentH   = T.H - contentTop - T.FRAME_BOTTOM_MARGIN;
  const colGap = 0.30;
  const leftW  = 5.20;
  const rightX = T.MARGIN_X + leftW + colGap;
  const rightW = T.W - rightX - T.MARGIN_X;

  slide.addText(edgeStep.description, {
    x: T.MARGIN_X, y: contentTop,
    w: leftW, h: contentH,
    fontSize: T.FONT_EDGE_BODY_SIZE,
    fontFace: T.FONT,
    color: T.GRAY_LIGHT,
    valign: "top", wrap: true,
    lineSpacingMultiple: 1.25,
  });

  const dims = FRAME_DIMS["web"];
  const boxW = rightW - 0.10;
  const boxH = contentH;
  const cx   = rightX + rightW / 2;
  const cy   = contentTop + contentH / 2;
  const fit  = aspectFit(dims.w, dims.h, boxW, boxH, cx, cy);

  if (imgExists(flowTopic, edgeStep.num, "web")) {
    slide.addImage({ path: imgPath(flowTopic, edgeStep.num, "web"), x: fit.x, y: fit.y, w: fit.w, h: fit.h });
  }

  slide.addShape("line", {
    x: T.MARGIN_X + leftW + colGap / 2, y: contentTop, w: 0, h: contentH,
    line: { color: T.ARROW, w: 0.75 },
  });
}

function buildCoverSlide(pptx, flowTopic) {
  const slide = pptx.addSlide();
  addBackground(slide);

  slide.addShape("rect", { x: 0, y: 0, w: T.W, h: 0.08, fill: { color: T.ACCENT }, line: { color: T.ACCENT } });

  // Flow topic as big title (replaces hardcoded "WISMO")
  const topicDisplay = flowTopic.replace(/_/g, " ");
  slide.addText(topicDisplay, {
    x: 1.0, y: 1.8, w: T.W - 2.0, h: 1.0,
    fontSize: 56, fontFace: T.FONT, bold: true,
    color: T.WHITE, align: "center", valign: "middle",
  });

  // Subtitle from manifest flow_metadata or generic
  const flows = MANIFEST.flows || [];
  const flow  = flows.find(f => f.topic === flowTopic) || flows[0] || {};
  const persona = (flow.flow_metadata && flow.flow_metadata.primary_persona) || "Customer";
  slide.addText(persona, {
    x: 1.0, y: 2.75, w: T.W - 2.0, h: 0.45,
    fontSize: 20, fontFace: T.FONT, color: T.ACCENT_LIGHT, align: "center",
  });

  slide.addText("Agentforce Conversation Flow — Channel Design Readout", {
    x: 1.0, y: 3.25, w: T.W - 2.0, h: 0.35,
    fontSize: 13, fontFace: T.FONT, color: T.GRAY_LIGHT, align: "center",
  });

  slide.addShape("rect", { x: T.W / 2 - 1.5, y: 3.70, w: 3.0, h: 0.025, fill: { color: T.ACCENT }, line: { color: T.ACCENT } });

  const channelNames = CHANNELS.map(c => c.charAt(0).toUpperCase() + c.slice(1));
  slide.addText(`${CLIENT_NAME}  ·  ${channelNames.join(" · ")}  ·  Spring ${new Date().getFullYear()}`, {
    x: 1.0, y: 3.82, w: T.W - 2.0, h: 0.30,
    fontSize: 11, fontFace: T.FONT, color: T.GRAY_MED, align: "center",
  });

  const chipW = 1.0;
  const chipH = 0.28;
  const totalChipsW = channelNames.length * chipW + (channelNames.length - 1) * 0.2;
  let cx = (T.W - totalChipsW) / 2;
  channelNames.forEach(ch => {
    slide.addShape("roundRect", { x: cx, y: 4.30, w: chipW, h: chipH, rectRadius: 0.06, fill: { color: T.BG_PILL }, line: { color: T.ACCENT, w: 1 } });
    slide.addText(ch, { x: cx, y: 4.30, w: chipW, h: chipH, fontSize: 10, fontFace: T.FONT, bold: true, color: T.WHITE, align: "center", valign: "middle" });
    cx += chipW + 0.2;
  });

  slide.addText(`${CLIENT_NAME}  ·  Agentforce`, {
    x: T.MARGIN_X, y: T.H - 0.30, w: T.W - T.MARGIN_X * 2, h: 0.22,
    fontSize: 8, fontFace: T.FONT, color: T.GRAY_MED, align: "right",
  });
}

function buildSectionDivider(pptx, label, sub) {
  const slide = pptx.addSlide();
  addBackground(slide);

  slide.addShape("rect", { x: 0, y: 0, w: T.W, h: 0.08, fill: { color: T.ACCENT }, line: { color: T.ACCENT } });
  slide.addText(label, {
    x: 1.0, y: 2.6, w: T.W - 2.0, h: 0.8,
    fontSize: 42, fontFace: T.FONT, bold: true, color: T.WHITE, align: "center", valign: "middle",
  });
  if (sub) {
    slide.addText(sub, { x: 1.0, y: 3.45, w: T.W - 2.0, h: 0.35, fontSize: 14, fontFace: T.FONT, color: T.GRAY_LIGHT, align: "center" });
  }
  slide.addShape("rect", { x: T.W / 2 - 1.0, y: 3.88, w: 2.0, h: 0.025, fill: { color: T.ACCENT }, line: { color: T.ACCENT } });
}

// ─── artifact_versions writer ─────────────────────────────────────────────────

function recordArtifactVersion(sotVersion, outPath) {
  const avPath = path.join(PROJECT_DIR, "artifact_versions.json");
  let data = {};
  if (fs.existsSync(avPath)) {
    try { data = JSON.parse(fs.readFileSync(avPath, "utf8")); } catch (_) {}
  }
  data.presentation = {
    source_of_truth_version: sotVersion,
    generated_at: new Date().toISOString(),
    path: outPath,
  };
  fs.writeFileSync(avPath, JSON.stringify(data, null, 2));
}

function decisionsVersion() {
  const dPath = path.join(PROJECT_DIR, "decisions.json");
  if (!fs.existsSync(dPath)) return 0;
  try {
    return JSON.parse(fs.readFileSync(dPath, "utf8")).source_of_truth_version || 0;
  } catch (_) { return 0; }
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const pptx = new PptxGenJS();
  pptx.layout = "LAYOUT_WIDE";
  pptx.author = "SF UX Orchestrator v2";

  const flows = MANIFEST.flows || [];
  if (flows.length === 0) {
    console.error("No flows found in manifest.");
    process.exit(1);
  }

  for (const flow of flows) {
    const flowTopic = flow.topic;
    pptx.title = `${flowTopic.replace(/_/g, " ")} — Agentforce Flow Readout`;

    const { mainSteps, edgeSteps, emailSteps } = stepsFromManifest(flowTopic);
    const emailMessages = emailMessagesFromManifest(flowTopic);
    const edgeDescriptions = edgeStepDescriptionsFromManifest(flowTopic);

    // Cover slide per flow
    buildCoverSlide(pptx, flowTopic);

    // Per-channel sections
    const flowChannels = (flow.channels || CHANNELS).filter(c => CHANNELS.includes(c));

    for (const channel of flowChannels) {
      const stepsForChannel = channel === "email" ? emailSteps : mainSteps;
      if (stepsForChannel.length === 0) continue;

      const channelLabel = channel.charAt(0).toUpperCase() + channel.slice(1);
      const turnLabel = channel === "email"
        ? `${flowTopic.replace(/_/g, " ")} Main Flow — ${stepsForChannel.length} Turn${stepsForChannel.length !== 1 ? "s" : ""}`
        : `${flowTopic.replace(/_/g, " ")} Main Flow — Steps 1–${stepsForChannel.length}`;

      buildSectionDivider(pptx, `${channelLabel} Channel`, turnLabel);

      // Chunk into slides of ≤6 steps
      const chunks = [];
      for (let i = 0; i < stepsForChannel.length; i += 6) {
        chunks.push(stepsForChannel.slice(i, i + 6));
      }

      chunks.forEach((chunk, ci) => {
        if (channel === "email") {
          buildEmailFlowSlide(pptx, flowTopic, chunk, stepsForChannel, channelLabel, emailMessages);
        } else {
          buildMainFlowSlide(pptx, flowTopic, chunk, mainSteps, channel, channelLabel, ci > 0);
        }
      });
    }

    // Edge case section (web only, if any edge steps exist)
    if (edgeDescriptions.length > 0) {
      buildSectionDivider(pptx, "Edge Cases", `Web Channel — Exception Paths`);
      for (const edgeStep of edgeDescriptions) {
        buildEdgeCaseSlide(pptx, flowTopic, edgeStep);
      }
    }
  }

  fs.mkdirSync(path.dirname(OUT_PATH), { recursive: true });
  await pptx.writeFile({ fileName: OUT_PATH });
  console.log(`✓ Saved: ${OUT_PATH}`);

  // Record this generation in artifact_versions.json
  const sotVersion = decisionsVersion();
  recordArtifactVersion(sotVersion, OUT_PATH);
  if (sotVersion > 0) {
    console.log(`  artifact_versions.json updated (source_of_truth_version: ${sotVersion})`);
  }
}

main().catch(err => { console.error(err); process.exit(1); });
