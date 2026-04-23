"""
Generates the Figma plugin files (manifest.json + code.js) into exports/plugin/.
The plugin is headless — no UI iframe — and communicates entirely via HTTP to
the local plugin_server.py instance running during `orchestrate.py push`.

Plugin places real SLDS Agentic Experiences library components using
figma.importComponentByKeyAsync() for production-quality output.
"""
import json
from pathlib import Path

# SLDS 2 - Agentic Experiences component keys (discovered from library in Wolverine file)
SLDS_KEYS = {
    "feedPanel":    "47443262e3d3ca2c01723aa73ed6650c44086381",
    "agentMessage": "4f89db7196e0d41880c6a2b2bb7908ce403173b6",
    "userMessage":  "379d6763d4edc0460a108e96176aa63c80404e7c",
    "welcome":      "b0e160e0d34247af67553a845193b1c42facad35",
    "disclaimer":   "d2ff9d418379534c8e3bbec22e717736e12b82df",
    "agentAvatar":  "acff7615fd4e208badc057f155bc6c88ac981700",
    "iconAdd":      "fd07a7487ccaf564d59ef15a20bdbfb50ee37dab",
    "iconSend":     "f220047998f767de38b970aa6c3273064e6ad006",
}

_CODE_JS_TEMPLATE = r"""
// SF UX Orchestrator — auto-generated Figma plugin
// Builds auto-layout chat screens using SLDS Agentforce avatar component.

const SERVER_URL = "{SERVER_URL}";

const SLDS = {
  feedPanel:    "{SLDS_feedPanel}",
  agentMessage: "{SLDS_agentMessage}",
  userMessage:  "{SLDS_userMessage}",
  welcome:      "{SLDS_welcome}",
  disclaimer:   "{SLDS_disclaimer}",
  agentAvatar:  "{SLDS_agentAvatar}",
  iconAdd:      "{SLDS_iconAdd}",
  iconSend:     "{SLDS_iconSend}",
};

// ── Auto-layout helpers ───────────────────────────────────────────────────────

function setHorizontalAL(node, gap, padTop, padRight, padBottom, padLeft, align) {
  node.layoutMode = "HORIZONTAL";
  node.itemSpacing = gap || 0;
  node.paddingTop    = padTop    || 0;
  node.paddingRight  = padRight  || 0;
  node.paddingBottom = padBottom || 0;
  node.paddingLeft   = padLeft   || 0;
  node.primaryAxisAlignItems   = "MIN";
  node.counterAxisAlignItems   = align || "CENTER";
  node.primaryAxisSizingMode   = "FIXED";
  node.counterAxisSizingMode   = "AUTO";
}

function setVerticalAL(node, gap, padTop, padRight, padBottom, padLeft) {
  node.layoutMode = "VERTICAL";
  node.itemSpacing = gap || 0;
  node.paddingTop    = padTop    || 0;
  node.paddingRight  = padRight  || 0;
  node.paddingBottom = padBottom || 0;
  node.paddingLeft   = padLeft   || 0;
  node.primaryAxisAlignItems   = "MIN";
  node.counterAxisAlignItems   = "MIN";
  node.primaryAxisSizingMode   = "AUTO";
  node.counterAxisSizingMode   = "FIXED";
}

// Spacer — a zero-height fixed node used to fill horizontal space in HORIZONTAL layout
function hSpacer(w) {
  const s = figma.createFrame();
  s.name = "spacer";
  s.resize(w, 1);
  s.fills = [];
  s.layoutGrow = 1;
  return s;
}

// Returns "10:03 AM" for message index 3 (base 10:00 AM).
function msgTimestamp(index) {
  var totalMins = 600 + index;
  var h = Math.floor(totalMins / 60);
  var m = totalMins % 60;
  var ampm = h < 12 ? "AM" : "PM";
  if (h > 12) h -= 12;
  if (h === 0) h = 12;
  return h + ":" + (m < 10 ? "0" + m : m) + " " + ampm;
}

// Builds one message row as a vertical auto-layout frame (bubble + timestamp).
// For agent: HORIZONTAL row (avatar | bubble-column). For user: right-aligned bubble-column.
async function buildMessageRow(text, role, frameW, msgIndex) {
  const AVATAR_D      = 28;
  const AVATAR_GAP    = 8;
  const BUBBLE_PAD_X  = 12;
  const BUBBLE_PAD_Y  = 10;
  const BUBBLE_RADIUS = 12;
  const FONT_SIZE     = 13;
  const LINE_H        = FONT_SIZE * 1.5;
  const TS_SIZE       = 11;
  const isAgent       = role === "agent";
  const SIDE_PAD      = 12;

  // Max bubble width
  const maxBubbleW = Math.round(frameW * 0.72);

  // ── Bubble frame (vertical AL: text inside with padding) ─────────────────
  const bubble = figma.createFrame();
  bubble.name = role + "/bubble";
  bubble.cornerRadius = BUBBLE_RADIUS;
  bubble.fills = isAgent
    ? [{ type: "SOLID", color: { r: 0.945, g: 0.945, b: 0.945 } }]
    : [{ type: "SOLID", color: { r: 0.922, g: 0.937, b: 1.0 } }];
  bubble.layoutMode = "VERTICAL";
  bubble.paddingTop    = BUBBLE_PAD_Y;
  bubble.paddingBottom = BUBBLE_PAD_Y;
  bubble.paddingLeft   = BUBBLE_PAD_X;
  bubble.paddingRight  = BUBBLE_PAD_X;
  bubble.primaryAxisSizingMode   = "AUTO";
  bubble.counterAxisSizingMode   = "FIXED";
  bubble.resize(maxBubbleW, 10);

  const txt = figma.createText();
  txt.name = "text";
  txt.fontName = { family: "Inter", style: "Regular" };
  txt.fontSize = FONT_SIZE;
  txt.lineHeight = { unit: "PIXELS", value: LINE_H };
  txt.textAutoResize = "HEIGHT";
  txt.resize(maxBubbleW - BUBBLE_PAD_X * 2, 20);
  txt.characters = text;
  txt.fills = [{ type: "SOLID", color: { r: 0.11, g: 0.11, b: 0.11 } }];
  bubble.appendChild(txt);
  // Let text hug height inside the auto-layout bubble
  txt.layoutSizingVertical = "HUG";

  // ── Timestamp ────────────────────────────────────────────────────────────
  const tsLabel = figma.createText();
  tsLabel.name = "timestamp";
  tsLabel.fontName = { family: "Inter", style: "Regular" };
  tsLabel.fontSize = TS_SIZE;
  tsLabel.textAutoResize = "WIDTH_AND_HEIGHT";
  tsLabel.characters = (isAgent ? "Agent · " : "You · ") + msgTimestamp(msgIndex);
  tsLabel.fills = [{ type: "SOLID", color: { r: 0.5, g: 0.5, b: 0.5 } }];
  if (!isAgent) tsLabel.textAlignHorizontal = "RIGHT";

  // ── Bubble column (bubble + timestamp stacked) ───────────────────────────
  const col = figma.createFrame();
  col.name = role + "/bubble-col";
  col.fills = [];
  col.layoutMode = "VERTICAL";
  col.itemSpacing = 4;
  col.primaryAxisSizingMode   = "AUTO";
  col.counterAxisSizingMode   = "FIXED";
  col.resize(maxBubbleW, 10);
  col.appendChild(bubble);
  bubble.layoutSizingVertical   = "HUG";
  bubble.layoutSizingHorizontal = "FILL";
  col.appendChild(tsLabel);
  tsLabel.layoutSizingVertical   = "HUG";
  tsLabel.layoutSizingHorizontal = "FILL";

  // ── Row frame ────────────────────────────────────────────────────────────
  const row = figma.createFrame();
  row.name = role + "/row";
  row.fills = [];
  row.layoutMode = "HORIZONTAL";
  row.itemSpacing = AVATAR_GAP;
  row.paddingLeft   = SIDE_PAD;
  row.paddingRight  = SIDE_PAD;
  row.primaryAxisSizingMode   = "FIXED";
  row.counterAxisSizingMode   = "AUTO";
  row.resize(frameW, 10);
  row.primaryAxisAlignItems   = isAgent ? "MIN" : "MAX";
  row.counterAxisAlignItems   = "MIN";

  if (isAgent) {
    // Avatar on the left
    var avNode;
    try {
      const avComp = await figma.importComponentByKeyAsync(SLDS.agentAvatar);
      avNode = avComp.createInstance();
    } catch(e) {
      avNode = figma.createEllipse();
      avNode.resize(AVATAR_D, AVATAR_D);
      avNode.fills = [{ type: "SOLID", color: { r: 0.051, g: 0.149, b: 0.275 } }];
    }
    avNode.name = "avatar";
    row.appendChild(avNode);
    avNode.layoutSizingHorizontal = "FIXED";
    avNode.layoutSizingVertical   = "FIXED";
    row.appendChild(col);
    col.layoutSizingHorizontal = "FILL";
    col.layoutSizingVertical   = "HUG";
  } else {
    row.appendChild(col);
    col.layoutSizingHorizontal = "HUG";
    col.layoutSizingVertical   = "HUG";
  }

  return row;
}

async function createChatScreen(payload) {
  const W = payload.frame_width;
  const H = payload.frame_height;

  await figma.loadFontAsync({ family: "Inter", style: "Regular" });
  await figma.loadFontAsync({ family: "Inter", style: "Medium" });
  await figma.loadFontAsync({ family: "Inter", style: "Semi Bold" });

  // ── Outer frame — vertical AL: header | scroll-area | footer ─────────────
  const outer = figma.createFrame();
  outer.name = payload.frame_name;
  outer.resize(W, H);
  outer.x = payload.x || 0;
  outer.y = payload.y || 0;
  outer.clipsContent = true;
  outer.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];
  outer.layoutMode = "VERTICAL";
  outer.itemSpacing = 0;
  outer.primaryAxisSizingMode = "FIXED";
  outer.counterAxisSizingMode = "FIXED";
  outer.primaryAxisAlignItems = "MIN";
  outer.counterAxisAlignItems = "MIN";

  // ── Header (horizontal AL) ────────────────────────────────────────────────
  const header = figma.createFrame();
  header.name = "Header";
  header.fills = [{ type: "SOLID", color: { r: 0.953, g: 0.953, b: 0.953 } }];
  setHorizontalAL(header, 8, 0, 16, 0, 12, "CENTER");
  header.primaryAxisSizingMode = "FIXED";
  header.counterAxisSizingMode = "FIXED";
  header.resize(W, 56);
  header.strokeAlign = "INSIDE";
  header.strokes = [{ type: "SOLID", color: { r: 0.851, g: 0.851, b: 0.851 } }];
  header.strokeWeight = 1;
  header.strokeTopWeight    = 0;
  header.strokeLeftWeight   = 0;
  header.strokeRightWeight  = 0;
  header.strokeBottomWeight = 1;


  // Header avatar
  var headerAv;
  try {
    const avComp = await figma.importComponentByKeyAsync(SLDS.agentAvatar);
    headerAv = avComp.createInstance();
  } catch(e) {
    headerAv = figma.createEllipse();
    headerAv.resize(28, 28);
    headerAv.fills = [{ type: "SOLID", color: { r: 0.051, g: 0.149, b: 0.275 } }];
  }
  headerAv.name = "avatar";
  header.appendChild(headerAv);
  headerAv.layoutSizingHorizontal = "FIXED";
  headerAv.layoutSizingVertical   = "FIXED";

  const headerTitle = figma.createText();
  headerTitle.name = "agent-name";
  headerTitle.fontName = { family: "Inter", style: "Semi Bold" };
  headerTitle.fontSize = 14;
  headerTitle.characters = "Agentforce";
  headerTitle.fills = [{ type: "SOLID", color: { r: 0.11, g: 0.11, b: 0.11 } }];
  headerTitle.textAutoResize = "WIDTH_AND_HEIGHT";
  header.appendChild(headerTitle);

  // Spacer pushes status dot to right
  const headerSpacer = figma.createFrame();
  headerSpacer.name = "spacer";
  headerSpacer.fills = [];
  headerSpacer.resize(1, 1);
  headerSpacer.layoutGrow = 1;
  header.appendChild(headerSpacer);

  // Online status dot
  const dot = figma.createEllipse();
  dot.name = "online-dot";
  dot.resize(8, 8);
  dot.fills = [{ type: "SOLID", color: { r: 0.102, g: 0.651, b: 0.314 } }];
  header.appendChild(dot);
  dot.layoutSizingHorizontal = "FIXED";
  dot.layoutSizingVertical   = "FIXED";

  outer.appendChild(header);
  header.layoutSizingVertical = "FIXED";

  // ── Scroll area (vertical AL, holds all message rows) ────────────────────
  const scrollArea = figma.createFrame();
  scrollArea.name = "Messages";
  scrollArea.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];
  scrollArea.layoutMode = "VERTICAL";
  scrollArea.itemSpacing = 4;
  scrollArea.paddingTop    = 12;
  scrollArea.paddingBottom = 12;
  scrollArea.primaryAxisSizingMode   = "AUTO";
  scrollArea.counterAxisSizingMode   = "FIXED";
  scrollArea.primaryAxisAlignItems   = "MAX";
  scrollArea.counterAxisAlignItems   = "MIN";
  scrollArea.resize(W, H - 56 - 64);
  scrollArea.clipsContent = true;

  outer.appendChild(scrollArea);
  scrollArea.layoutSizingVertical = "FILL";

  const messages = payload.messages || [];
  for (var i = 0; i < messages.length; i++) {
    const row = await buildMessageRow(messages[i].text, messages[i].role, W, i);
    scrollArea.appendChild(row);
    row.layoutSizingHorizontal = "FILL";
    row.layoutSizingVertical   = "HUG";
  }

  // ── Footer (horizontal AL input bar) ─────────────────────────────────────
  const footer = figma.createFrame();
  footer.name = "Footer";
  footer.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];
  setHorizontalAL(footer, 8, 12, 12, 12, 12, "CENTER");
  footer.primaryAxisSizingMode = "FIXED";
  footer.counterAxisSizingMode = "FIXED";
  footer.resize(W, 64);
  footer.strokes = [{ type: "SOLID", color: { r: 0.851, g: 0.851, b: 0.851 } }];
  footer.strokeWeight = 1;
  footer.strokeTopWeight    = 1;
  footer.strokeLeftWeight   = 0;
  footer.strokeRightWeight  = 0;
  footer.strokeBottomWeight = 0;

  outer.appendChild(footer);
  footer.layoutSizingVertical = "FIXED";

  // Add icon (left)
  var addIcon;
  try {
    const addComp = await figma.importComponentByKeyAsync(SLDS.iconAdd);
    addIcon = addComp.createInstance();
  } catch(e) {
    addIcon = figma.createFrame();
    addIcon.resize(32, 32);
    addIcon.fills = [];
  }
  addIcon.name = "add-icon";
  footer.appendChild(addIcon);
  addIcon.layoutSizingHorizontal = "FIXED";
  addIcon.layoutSizingVertical   = "FIXED";

  // Input pill
  const inputPill = figma.createFrame();
  inputPill.name = "input-field";
  inputPill.cornerRadius = 20;
  inputPill.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];
  inputPill.strokes = [{ type: "SOLID", color: { r: 0.8, g: 0.8, b: 0.8 } }];
  inputPill.strokeWeight = 1;
  setHorizontalAL(inputPill, 0, 0, 12, 0, 12, "CENTER");
  inputPill.primaryAxisSizingMode = "FIXED";
  inputPill.counterAxisSizingMode = "FIXED";
  inputPill.resize(W - 32 - 32 - 8 - 8 - 24, 40);
  inputPill.layoutGrow = 1;
  footer.appendChild(inputPill);
  inputPill.layoutSizingHorizontal = "FILL";
  inputPill.layoutSizingVertical   = "FIXED";

  const phTxt = figma.createText();
  phTxt.name = "placeholder";
  phTxt.fontName = { family: "Inter", style: "Regular" };
  phTxt.fontSize = 13;
  phTxt.characters = "Ask a follow-up...";
  phTxt.fills = [{ type: "SOLID", color: { r: 0.6, g: 0.6, b: 0.6 } }];
  phTxt.textAutoResize = "HEIGHT";
  inputPill.appendChild(phTxt);
  phTxt.layoutGrow = 1;

  // Send icon (right)
  var sendIcon;
  try {
    const sendComp = await figma.importComponentByKeyAsync(SLDS.iconSend);
    sendIcon = sendComp.createInstance();
  } catch(e) {
    sendIcon = figma.createFrame();
    sendIcon.resize(32, 32);
    sendIcon.fills = [];
  }
  sendIcon.name = "send-icon";
  footer.appendChild(sendIcon);
  sendIcon.layoutSizingHorizontal = "FIXED";
  sendIcon.layoutSizingVertical   = "FIXED";

  return outer;
}

async function createEmailScreen(payload) {
  var emailFont = "SF Pro Text";
  try {
    await figma.loadFontAsync({ family: "SF Pro Text", style: "Regular" });
    await figma.loadFontAsync({ family: "SF Pro Text", style: "Semibold" });
  } catch(e) {
    emailFont = "Helvetica Neue";
    await figma.loadFontAsync({ family: "Helvetica Neue", style: "Regular" });
    await figma.loadFontAsync({ family: "Helvetica Neue", style: "Medium" });
  }
  var boldStyle  = emailFont === "SF Pro Text" ? "Semibold" : "Medium";
  var plainStyle = "Regular";

  const W = payload.frame_width  || 710;
  const H = payload.frame_height || 280;

  // ── Outer frame ──────────────────────────────────────────────────────────────
  const outer = figma.createFrame();
  outer.name = payload.frame_name;
  outer.resize(W, H);
  outer.x = payload.x || 0;
  outer.y = payload.y || 0;
  outer.clipsContent = true;
  outer.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];
  outer.layoutMode = "VERTICAL";
  outer.itemSpacing = 0;
  outer.primaryAxisSizingMode = "AUTO";
  outer.counterAxisSizingMode = "FIXED";
  outer.primaryAxisAlignItems = "MIN";
  outer.counterAxisAlignItems = "MIN";

  // ── Email card ───────────────────────────────────────────────────────────────
  const card = figma.createFrame();
  card.name = "emailCard";
  card.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];
  card.layoutMode = "VERTICAL";
  card.itemSpacing = 0;
  card.paddingTop    = 0;
  card.paddingBottom = 0;
  card.paddingLeft   = 0;
  card.paddingRight  = 0;
  card.primaryAxisSizingMode = "AUTO";
  card.counterAxisSizingMode = "FIXED";
  card.primaryAxisAlignItems = "MIN";
  card.counterAxisAlignItems = "MIN";
  card.strokes = [{ type: "SOLID", color: { r: 0.878, g: 0.878, b: 0.878 } }];
  card.strokeWeight = 1;
  card.strokeTopWeight    = 0;
  card.strokeLeftWeight   = 0;
  card.strokeRightWeight  = 0;
  card.strokeBottomWeight = 1;
  card.resize(W, 10);

  // ── Header row (avatar | sender block | spacer | timestamp | chevron) ────────
  const header = figma.createFrame();
  header.name = "row_header";
  header.fills = [];
  header.layoutMode = "HORIZONTAL";
  header.itemSpacing = 12;
  header.paddingTop    = 16;
  header.paddingBottom = 12;
  header.paddingLeft   = 16;
  header.paddingRight  = 16;
  header.primaryAxisSizingMode = "FIXED";
  header.counterAxisSizingMode = "AUTO";
  header.primaryAxisAlignItems = "MIN";
  header.counterAxisAlignItems = "MIN";
  header.resize(W, 10);

  // Avatar
  const avatar = figma.createEllipse();
  avatar.name = "avatar";
  avatar.resize(40, 40);
  avatar.fills = [{ type: "SOLID", color: { r: 0.6, g: 0.6, b: 0.6 } }];

  header.appendChild(avatar);
  avatar.layoutSizingHorizontal = "FIXED";
  avatar.layoutSizingVertical   = "FIXED";

  // Sender block (vertical AL)
  const senderBlock = figma.createFrame();
  senderBlock.name = "senderBlock";
  senderBlock.fills = [];
  senderBlock.layoutMode = "VERTICAL";
  senderBlock.itemSpacing = 2;
  senderBlock.paddingTop    = 0;
  senderBlock.paddingBottom = 0;
  senderBlock.paddingLeft   = 0;
  senderBlock.paddingRight  = 0;
  senderBlock.primaryAxisSizingMode = "AUTO";
  senderBlock.counterAxisSizingMode = "AUTO";

  const senderName = figma.createText();
  senderName.name = "sender-name";
  senderName.fontName = { family: emailFont, style: plainStyle };
  senderName.fontSize = 13;
  senderName.characters = (payload.sender_name || "User") + " <" + (payload.sender_email || "") + ">";
  senderName.fills = [{ type: "SOLID", color: { r: 0.067, g: 0.067, b: 0.067 } }];
  senderName.textAutoResize = "WIDTH_AND_HEIGHT";

  const toLine = figma.createText();
  toLine.name = "to-line";
  toLine.fontName = { family: emailFont, style: plainStyle };
  toLine.fontSize = 12;
  toLine.characters = "to " + (payload.to_address || "");
  toLine.fills = [{ type: "SOLID", color: { r: 0.4, g: 0.4, b: 0.4 } }];
  toLine.textAutoResize = "WIDTH_AND_HEIGHT";

  senderBlock.appendChild(senderName);
  senderBlock.appendChild(toLine);

  header.appendChild(senderBlock);
  senderBlock.layoutSizingHorizontal = "HUG";
  senderBlock.layoutSizingVertical   = "HUG";

  // Spacer
  const hdrSpacer = figma.createFrame();
  hdrSpacer.name = "spacer";
  hdrSpacer.fills = [];
  hdrSpacer.resize(1, 1);
  hdrSpacer.layoutGrow = 1;
  header.appendChild(hdrSpacer);

  // Timestamp + chevron block
  const tsBlock = figma.createFrame();
  tsBlock.name = "tsBlock";
  tsBlock.fills = [];
  tsBlock.layoutMode = "HORIZONTAL";
  tsBlock.itemSpacing = 6;
  tsBlock.paddingTop    = 0;
  tsBlock.paddingBottom = 0;
  tsBlock.paddingLeft   = 0;
  tsBlock.paddingRight  = 0;
  tsBlock.primaryAxisSizingMode = "AUTO";
  tsBlock.counterAxisSizingMode = "AUTO";
  tsBlock.primaryAxisAlignItems = "MIN";
  tsBlock.counterAxisAlignItems = "CENTER";

  const tsLabel = figma.createText();
  tsLabel.name = "timestamp";
  tsLabel.fontName = { family: emailFont, style: plainStyle };
  tsLabel.fontSize = 12;
  tsLabel.characters = payload.timestamp || "";
  tsLabel.fills = [{ type: "SOLID", color: { r: 0.4, g: 0.4, b: 0.4 } }];
  tsLabel.textAutoResize = "WIDTH_AND_HEIGHT";

  const chevron = figma.createRectangle();
  chevron.name = "chevron";
  chevron.resize(16, 16);
  chevron.cornerRadius = 3;
  chevron.fills = [];
  chevron.strokes = [{ type: "SOLID", color: { r: 0.8, g: 0.8, b: 0.8 } }];
  chevron.strokeWeight = 1.5;

  tsBlock.appendChild(tsLabel);
  tsBlock.appendChild(chevron);
  chevron.layoutSizingHorizontal = "FIXED";
  chevron.layoutSizingVertical   = "FIXED";

  header.appendChild(tsBlock);
  tsBlock.layoutSizingHorizontal = "HUG";
  tsBlock.layoutSizingVertical   = "HUG";

  card.appendChild(header);
  header.layoutSizingHorizontal = "FILL";
  header.layoutSizingVertical   = "HUG";

  // ── Body row ─────────────────────────────────────────────────────────────────
  const bodyRow = figma.createFrame();
  bodyRow.name = "row_body";
  bodyRow.fills = [];
  bodyRow.layoutMode = "VERTICAL";
  bodyRow.itemSpacing = 0;
  bodyRow.paddingTop    = 0;
  bodyRow.paddingBottom = 16;
  bodyRow.paddingLeft   = 68;
  bodyRow.paddingRight  = 16;
  bodyRow.primaryAxisSizingMode = "AUTO";
  bodyRow.counterAxisSizingMode = "FIXED";
  bodyRow.primaryAxisAlignItems = "MIN";
  bodyRow.counterAxisAlignItems = "MIN";
  bodyRow.resize(W, 10);

  const bodyTxt = figma.createText();
  bodyTxt.name = "body-text";
  bodyTxt.fontName = { family: emailFont, style: plainStyle };
  bodyTxt.fontSize = 13;
  bodyTxt.lineHeight = { unit: "PIXELS", value: 20 };
  bodyTxt.textAutoResize = "HEIGHT";
  bodyTxt.resize(W - 68 - 16, 20);
  bodyTxt.characters = payload.body || "";
  bodyTxt.fills = [{ type: "SOLID", color: { r: 0.067, g: 0.067, b: 0.067 } }];

  bodyRow.appendChild(bodyTxt);
  bodyTxt.layoutSizingHorizontal = "FILL";
  bodyTxt.layoutSizingVertical   = "HUG";

  card.appendChild(bodyRow);
  bodyRow.layoutSizingHorizontal = "FILL";
  bodyRow.layoutSizingVertical   = "HUG";

  outer.appendChild(card);
  card.layoutSizingHorizontal = "FILL";
  card.layoutSizingVertical   = "HUG";

  return outer;
}

async function createSmsScreen(payload) {
  const W = payload.frame_width  || 390;
  const H = payload.frame_height || 844;

  await figma.loadFontAsync({ family: "Inter", style: "Regular" });
  await figma.loadFontAsync({ family: "Inter", style: "Semi Bold" });

  // ── Outer frame ──────────────────────────────────────────────────────────────
  const outer = figma.createFrame();
  outer.name = payload.frame_name;
  outer.resize(W, H);
  outer.x = payload.x || 0;
  outer.y = payload.y || 0;
  outer.clipsContent = true;
  outer.fills = [{ type: "SOLID", color: { r: 0, g: 0, b: 0 } }];
  outer.layoutMode = "VERTICAL";
  outer.itemSpacing = 0;
  outer.primaryAxisSizingMode = "FIXED";
  outer.counterAxisSizingMode = "FIXED";
  outer.primaryAxisAlignItems = "MIN";
  outer.counterAxisAlignItems = "MIN";

  // ── Status Bar (44px) ────────────────────────────────────────────────────────
  const statusBar = figma.createFrame();
  statusBar.name = "statusBar";
  statusBar.fills = [{ type: "SOLID", color: { r: 0, g: 0, b: 0 } }];
  statusBar.layoutMode = "HORIZONTAL";
  statusBar.itemSpacing = 0;
  statusBar.paddingTop    = 14;
  statusBar.paddingBottom = 0;
  statusBar.paddingLeft   = 16;
  statusBar.paddingRight  = 16;
  statusBar.primaryAxisSizingMode = "FIXED";
  statusBar.counterAxisSizingMode = "FIXED";
  statusBar.primaryAxisAlignItems = "MIN";
  statusBar.counterAxisAlignItems = "CENTER";
  statusBar.resize(W, 44);

  const timeText = figma.createText();
  timeText.name = "time";
  timeText.fontName = { family: "Inter", style: "Semi Bold" };
  timeText.fontSize = 15;
  timeText.characters = "9:41";
  timeText.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];
  timeText.textAutoResize = "WIDTH_AND_HEIGHT";
  statusBar.appendChild(timeText);

  const statusSpacer = figma.createFrame();
  statusSpacer.name = "spacer";
  statusSpacer.fills = [];
  statusSpacer.resize(1, 1);
  statusSpacer.layoutGrow = 1;
  statusBar.appendChild(statusSpacer);

  const statusIcons = figma.createText();
  statusIcons.name = "status-icons";
  statusIcons.fontName = { family: "Inter", style: "Regular" };
  statusIcons.fontSize = 12;
  statusIcons.characters = "▮▮▮ ◈ ▮";
  statusIcons.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];
  statusIcons.textAutoResize = "WIDTH_AND_HEIGHT";
  statusBar.appendChild(statusIcons);

  outer.appendChild(statusBar);
  statusBar.layoutSizingVertical = "FIXED";

  // ── Nav Bar (44px) ───────────────────────────────────────────────────────────
  const navBar = figma.createFrame();
  navBar.name = "navBar";
  navBar.fills = [{ type: "SOLID", color: { r: 0, g: 0, b: 0 } }];
  navBar.layoutMode = "HORIZONTAL";
  navBar.itemSpacing = 0;
  navBar.paddingTop    = 0;
  navBar.paddingBottom = 0;
  navBar.paddingLeft   = 8;
  navBar.paddingRight  = 16;
  navBar.primaryAxisSizingMode = "FIXED";
  navBar.counterAxisSizingMode = "FIXED";
  navBar.primaryAxisAlignItems = "MIN";
  navBar.counterAxisAlignItems = "CENTER";
  navBar.resize(W, 44);
  navBar.strokes = [{ type: "SOLID", color: { r: 0.2, g: 0.2, b: 0.2 } }];
  navBar.strokeWeight = 0.5;
  navBar.strokeTopWeight    = 0;
  navBar.strokeLeftWeight   = 0;
  navBar.strokeRightWeight  = 0;
  navBar.strokeBottomWeight = 0.5;

  const backChevron = figma.createText();
  backChevron.name = "back-chevron";
  backChevron.fontName = { family: "Inter", style: "Regular" };
  backChevron.fontSize = 28;
  backChevron.characters = "‹";
  backChevron.fills = [{ type: "SOLID", color: { r: 0, g: 0.478, b: 1 } }];
  backChevron.textAutoResize = "WIDTH_AND_HEIGHT";
  navBar.appendChild(backChevron);

  const navSpacer1 = figma.createFrame();
  navSpacer1.name = "spacer";
  navSpacer1.fills = [];
  navSpacer1.resize(1, 1);
  navSpacer1.layoutGrow = 1;
  navBar.appendChild(navSpacer1);

  const contactName = figma.createText();
  contactName.name = "contact-name";
  contactName.fontName = { family: "Inter", style: "Semi Bold" };
  contactName.fontSize = 17;
  contactName.characters = payload.agent_name || "Agent";
  contactName.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];
  contactName.textAutoResize = "WIDTH_AND_HEIGHT";
  navBar.appendChild(contactName);

  const navSpacer2 = figma.createFrame();
  navSpacer2.name = "spacer";
  navSpacer2.fills = [];
  navSpacer2.resize(1, 1);
  navSpacer2.layoutGrow = 1;
  navBar.appendChild(navSpacer2);

  const videoIcon = figma.createRectangle();
  videoIcon.name = "video-icon";
  videoIcon.resize(22, 16);
  videoIcon.cornerRadius = 3;
  videoIcon.fills = [];
  videoIcon.strokes = [{ type: "SOLID", color: { r: 0, g: 0.478, b: 1 } }];
  videoIcon.strokeWeight = 1.5;
  navBar.appendChild(videoIcon);
  videoIcon.layoutSizingHorizontal = "FIXED";
  videoIcon.layoutSizingVertical   = "FIXED";

  outer.appendChild(navBar);
  navBar.layoutSizingVertical = "FIXED";

  // ── Messages Area (FILL) ─────────────────────────────────────────────────────
  const messagesArea = figma.createFrame();
  messagesArea.name = "messagesArea";
  messagesArea.fills = [{ type: "SOLID", color: { r: 0, g: 0, b: 0 } }];
  messagesArea.layoutMode = "VERTICAL";
  messagesArea.itemSpacing = 8;
  messagesArea.paddingTop    = 16;
  messagesArea.paddingBottom = 16;
  messagesArea.paddingLeft   = 16;
  messagesArea.paddingRight  = 16;
  messagesArea.primaryAxisSizingMode = "AUTO";
  messagesArea.counterAxisSizingMode = "FIXED";
  messagesArea.primaryAxisAlignItems = "MIN";
  messagesArea.counterAxisAlignItems = "MIN";
  messagesArea.resize(W, H - 44 - 44 - 83);

  // Row: agent label
  const rowAgentLabel = figma.createFrame();
  rowAgentLabel.name = "row_agentLabel";
  rowAgentLabel.fills = [];
  rowAgentLabel.layoutMode = "HORIZONTAL";
  rowAgentLabel.itemSpacing = 0;
  rowAgentLabel.paddingTop    = 0;
  rowAgentLabel.paddingBottom = 0;
  rowAgentLabel.paddingLeft   = 40;
  rowAgentLabel.paddingRight  = 0;
  rowAgentLabel.primaryAxisSizingMode = "FIXED";
  rowAgentLabel.counterAxisSizingMode = "AUTO";
  rowAgentLabel.primaryAxisAlignItems = "MIN";
  rowAgentLabel.counterAxisAlignItems = "MIN";
  rowAgentLabel.resize(W - 32, 16);

  const agentLabelTxt = figma.createText();
  agentLabelTxt.name = "agent-label";
  agentLabelTxt.fontName = { family: "Inter", style: "Regular" };
  agentLabelTxt.fontSize = 12;
  agentLabelTxt.characters = "Agent";
  agentLabelTxt.fills = [{ type: "SOLID", color: { r: 0.557, g: 0.557, b: 0.576 } }];
  agentLabelTxt.textAutoResize = "WIDTH_AND_HEIGHT";
  rowAgentLabel.appendChild(agentLabelTxt);

  messagesArea.appendChild(rowAgentLabel);
  rowAgentLabel.layoutSizingHorizontal = "FILL";
  rowAgentLabel.layoutSizingVertical   = "HUG";

  // Rows: one per message (agent left with avatar, user right blue bubble)
  var bubbleTxtW = Math.round(W * 0.72) - 32 - 8 - 24;
  var userBubbleTxtW = Math.round(W * 0.72) - 24;
  var smsMessages = payload.messages || [];

  for (var mi = 0; mi < smsMessages.length; mi++) {
    var msg = smsMessages[mi];
    var isAgent = msg.role === "agent";

    var msgRow = figma.createFrame();
    msgRow.name = isAgent ? "row_agentBubble" : "row_userBubble";
    msgRow.fills = [];
    msgRow.layoutMode = "HORIZONTAL";
    msgRow.itemSpacing = 8;
    msgRow.paddingTop    = 0;
    msgRow.paddingBottom = 0;
    msgRow.paddingLeft   = 0;
    msgRow.paddingRight  = 0;
    msgRow.primaryAxisSizingMode = "FIXED";
    msgRow.counterAxisSizingMode = "AUTO";
    msgRow.primaryAxisAlignItems = isAgent ? "MIN" : "MAX";
    msgRow.counterAxisAlignItems = "MIN";
    msgRow.resize(W - 32, 10);

    var msgBubble = figma.createFrame();
    msgBubble.name = "bubble";
    msgBubble.cornerRadius = 18;
    msgBubble.fills = isAgent
      ? [{ type: "SOLID", color: { r: 0.11, g: 0.11, b: 0.118 } }]
      : [{ type: "SOLID", color: { r: 0, g: 0.478, b: 1 } }];
    msgBubble.layoutMode = "VERTICAL";
    msgBubble.itemSpacing = 0;
    msgBubble.paddingTop    = 12;
    msgBubble.paddingBottom = 12;
    msgBubble.paddingLeft   = 12;
    msgBubble.paddingRight  = 12;
    msgBubble.primaryAxisSizingMode = "AUTO";
    msgBubble.counterAxisSizingMode = "AUTO";

    var msgTxt = figma.createText();
    msgTxt.name = "bubble-text";
    msgTxt.fontName = { family: "Inter", style: "Regular" };
    msgTxt.fontSize = 17;
    msgTxt.textAutoResize = "HEIGHT";
    msgTxt.resize(isAgent ? bubbleTxtW : userBubbleTxtW, 20);
    msgTxt.characters = msg.text;
    msgTxt.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];
    msgBubble.appendChild(msgTxt);
    msgTxt.layoutSizingVertical = "HUG";

    if (isAgent) {
      var av = figma.createEllipse();
      av.name = "avatar";
      av.resize(32, 32);
      av.fills = [{ type: "SOLID", color: { r: 0.227, g: 0.227, b: 0.235 } }];
      msgRow.appendChild(av);
      av.layoutSizingHorizontal = "FIXED";
      av.layoutSizingVertical   = "FIXED";
    }

    msgRow.appendChild(msgBubble);
    msgBubble.layoutSizingHorizontal = "HUG";
    msgBubble.layoutSizingVertical   = "HUG";

    messagesArea.appendChild(msgRow);
    msgRow.layoutSizingHorizontal = "FILL";
    msgRow.layoutSizingVertical   = "HUG";
  }

  // Row: timestamp — always last, tight under final bubble
  const rowTimestamp = figma.createFrame();
  rowTimestamp.name = "row_timestamp";
  rowTimestamp.fills = [];
  rowTimestamp.layoutMode = "HORIZONTAL";
  rowTimestamp.itemSpacing = 0;
  rowTimestamp.paddingTop    = 0;
  rowTimestamp.paddingBottom = 0;
  rowTimestamp.paddingLeft   = 0;
  rowTimestamp.paddingRight  = 0;
  rowTimestamp.primaryAxisSizingMode = "FIXED";
  rowTimestamp.counterAxisSizingMode = "AUTO";
  rowTimestamp.primaryAxisAlignItems = "CENTER";
  rowTimestamp.counterAxisAlignItems = "CENTER";
  rowTimestamp.resize(W - 32, 16);

  const tsText = figma.createText();
  tsText.name = "timestamp";
  tsText.fontName = { family: "Inter", style: "Regular" };
  tsText.fontSize = 12;
  tsText.characters = "Today 9:41";
  tsText.fills = [{ type: "SOLID", color: { r: 0.557, g: 0.557, b: 0.576 } }];
  tsText.textAutoResize = "WIDTH_AND_HEIGHT";
  rowTimestamp.appendChild(tsText);

  messagesArea.appendChild(rowTimestamp);
  rowTimestamp.layoutSizingHorizontal = "FILL";
  rowTimestamp.layoutSizingVertical   = "HUG";

  // Rows: quick replies (from payload.quick_replies array)
  var quickReplies = payload.quick_replies || [];
  for (var qi = 0; qi < quickReplies.length; qi++) {
    const rowQR = figma.createFrame();
    rowQR.name = "row_quickReply";
    rowQR.fills = [];
    rowQR.layoutMode = "HORIZONTAL";
    rowQR.itemSpacing = 0;
    rowQR.paddingTop    = 0;
    rowQR.paddingBottom = 0;
    rowQR.paddingLeft   = 16;
    rowQR.paddingRight  = 16;
    rowQR.primaryAxisSizingMode = "FIXED";
    rowQR.counterAxisSizingMode = "AUTO";
    rowQR.primaryAxisAlignItems = "MIN";
    rowQR.counterAxisAlignItems = "CENTER";
    rowQR.resize(W - 32, 44);

    const qrBtn = figma.createFrame();
    qrBtn.name = "quick-reply-btn";
    qrBtn.cornerRadius = 22;
    qrBtn.fills = [{ type: "SOLID", color: { r: 0, g: 0.478, b: 1 } }];
    qrBtn.layoutMode = "HORIZONTAL";
    qrBtn.paddingTop    = 0;
    qrBtn.paddingBottom = 0;
    qrBtn.paddingLeft   = 20;
    qrBtn.paddingRight  = 20;
    qrBtn.itemSpacing   = 0;
    qrBtn.primaryAxisSizingMode = "AUTO";
    qrBtn.counterAxisSizingMode = "FIXED";
    qrBtn.primaryAxisAlignItems = "CENTER";
    qrBtn.counterAxisAlignItems = "CENTER";
    qrBtn.resize(100, 44);

    const qrLabel = figma.createText();
    qrLabel.name = "label";
    qrLabel.fontName = { family: "Inter", style: "Semi Bold" };
    qrLabel.fontSize = 15;
    qrLabel.characters = quickReplies[qi];
    qrLabel.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];
    qrLabel.textAutoResize = "WIDTH_AND_HEIGHT";
    qrBtn.appendChild(qrLabel);
    qrLabel.layoutSizingVertical = "HUG";

    rowQR.appendChild(qrBtn);
    qrBtn.layoutSizingHorizontal = "HUG";
    qrBtn.layoutSizingVertical   = "FIXED";

    messagesArea.appendChild(rowQR);
    rowQR.layoutSizingHorizontal = "FILL";
    rowQR.layoutSizingVertical   = "HUG";
  }

  outer.appendChild(messagesArea);
  messagesArea.layoutSizingVertical = "FILL";

  // ── Input Bar (83px) ────────────────────────────────────────────────────────
  const inputBar = figma.createFrame();
  inputBar.name = "inputBar";
  inputBar.fills = [{ type: "SOLID", color: { r: 0, g: 0, b: 0 } }];
  inputBar.layoutMode = "HORIZONTAL";
  inputBar.itemSpacing = 12;
  inputBar.paddingTop    = 12;
  inputBar.paddingBottom = 20;
  inputBar.paddingLeft   = 16;
  inputBar.paddingRight  = 16;
  inputBar.primaryAxisSizingMode = "FIXED";
  inputBar.counterAxisSizingMode = "FIXED";
  inputBar.primaryAxisAlignItems = "MIN";
  inputBar.counterAxisAlignItems = "CENTER";
  inputBar.resize(W, 83);
  inputBar.strokes = [{ type: "SOLID", color: { r: 0.2, g: 0.2, b: 0.2 } }];
  inputBar.strokeWeight = 0.5;
  inputBar.strokeTopWeight    = 0.5;
  inputBar.strokeLeftWeight   = 0;
  inputBar.strokeRightWeight  = 0;
  inputBar.strokeBottomWeight = 0;

  var camIcon = figma.createRectangle();
  camIcon.name = "camera-icon";
  camIcon.resize(28, 28);
  camIcon.cornerRadius = 6;
  camIcon.fills = [{ type: "SOLID", color: { r: 0.557, g: 0.557, b: 0.576 } }];
  inputBar.appendChild(camIcon);
  camIcon.layoutSizingHorizontal = "FIXED";
  camIcon.layoutSizingVertical   = "FIXED";

  var appIcon = figma.createRectangle();
  appIcon.name = "app-icon";
  appIcon.resize(28, 28);
  appIcon.cornerRadius = 6;
  appIcon.fills = [{ type: "SOLID", color: { r: 0.557, g: 0.557, b: 0.576 } }];
  inputBar.appendChild(appIcon);
  appIcon.layoutSizingHorizontal = "FIXED";
  appIcon.layoutSizingVertical   = "FIXED";

  const smsInputField = figma.createFrame();
  smsInputField.name = "input-field";
  smsInputField.cornerRadius = 18;
  smsInputField.fills = [{ type: "SOLID", color: { r: 0.11, g: 0.11, b: 0.118 } }];
  smsInputField.strokes = [{ type: "SOLID", color: { r: 0.2, g: 0.2, b: 0.2 } }];
  smsInputField.strokeWeight = 0.5;
  smsInputField.layoutMode = "HORIZONTAL";
  smsInputField.paddingTop    = 0;
  smsInputField.paddingBottom = 0;
  smsInputField.paddingLeft   = 14;
  smsInputField.paddingRight  = 14;
  smsInputField.itemSpacing   = 0;
  smsInputField.primaryAxisSizingMode = "FIXED";
  smsInputField.counterAxisSizingMode = "FIXED";
  smsInputField.primaryAxisAlignItems = "MIN";
  smsInputField.counterAxisAlignItems = "CENTER";
  smsInputField.resize(200, 36);

  const smsPhTxt = figma.createText();
  smsPhTxt.name = "placeholder";
  smsPhTxt.fontName = { family: "Inter", style: "Regular" };
  smsPhTxt.fontSize = 17;
  smsPhTxt.characters = "iMessage";
  smsPhTxt.fills = [{ type: "SOLID", color: { r: 0.557, g: 0.557, b: 0.576 } }];
  smsPhTxt.textAutoResize = "HEIGHT";
  smsInputField.appendChild(smsPhTxt);
  smsPhTxt.layoutGrow = 1;

  inputBar.appendChild(smsInputField);
  smsInputField.layoutSizingHorizontal = "FILL";
  smsInputField.layoutSizingVertical   = "FIXED";

  const micIcon = figma.createRectangle();
  micIcon.name = "mic-icon";
  micIcon.resize(28, 28);
  micIcon.cornerRadius = 14;
  micIcon.fills = [{ type: "SOLID", color: { r: 0.557, g: 0.557, b: 0.576 } }];
  inputBar.appendChild(micIcon);
  micIcon.layoutSizingHorizontal = "FIXED";
  micIcon.layoutSizingVertical   = "FIXED";

  outer.appendChild(inputBar);
  inputBar.layoutSizingVertical = "FIXED";

  return outer;
}

(async () => {
  try {
    figma.notify("Fetching frames from orchestrator...");
    const resp = await fetch(SERVER_URL + "/frames");
    if (!resp.ok) throw new Error("Server returned " + resp.status);
    const frames = await resp.json();

    if (!frames || frames.length === 0) {
      figma.notify("No pending frames found.");
      figma.closePlugin();
      return;
    }

    figma.notify("Creating " + frames.length + " frame(s)...");

    const created = [];
    let firstError = null;
    for (let i = 0; i < frames.length; i++) {
      const payload = frames[i];
      console.log("[SF UX Orchestrator] build spec:", JSON.stringify(payload, null, 2));
      try {
        let node;
        if (payload.channel === "email") {
          node = await createEmailScreen(payload);
        } else if (payload.channel === "sms") {
          node = await createSmsScreen(payload);
        } else {
          node = await createChatScreen(payload);
        }
        created.push({ name: payload.frame_name, id: node.id });
      } catch(e) {
        console.error("Frame failed:", payload.frame_name, e);
        if (!firstError) firstError = payload.frame_name + ": " + (e && e.message ? e.message : String(e));
      }
    }

    await fetch(SERVER_URL + "/complete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(created),
    });

    if (firstError) {
      figma.notify("Error — " + firstError, { error: true, timeout: 10000 });
    } else {
      figma.notify("Done — " + created.length + " of " + frames.length + " frame(s) created.");
    }
    figma.closePlugin();

  } catch(e) {
    figma.notify("Plugin error: " + e.message, { error: true });
    figma.closePlugin();
  }
})();
""".lstrip()


def build_plugin(
    output_dir: Path,
    server_url: str = "http://localhost:7070",
    plugin_name: str = "SF UX Orchestrator",
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_manifest(output_dir, plugin_name, server_url)
    _write_code_js(output_dir, server_url)


def _write_manifest(output_dir: Path, plugin_name: str, server_url: str) -> None:
    manifest = {
        "name": plugin_name,
        "id": "sf-ux-orchestrator-push",
        "api": "1.0.0",
        "editorType": ["figma"],
        "main": "code.js",
        "networkAccess": {
            "allowedDomains": ["none"],
            "devAllowedDomains": [server_url],
        },
    }
    path = output_dir / "manifest.json"
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)


def _write_code_js(output_dir: Path, server_url: str) -> None:
    code = _CODE_JS_TEMPLATE.replace("{SERVER_URL}", server_url)
    for name, key in SLDS_KEYS.items():
        code = code.replace("{SLDS_" + name + "}", key)
    path = output_dir / "code.js"
    with open(path, "w") as f:
        f.write(code)
