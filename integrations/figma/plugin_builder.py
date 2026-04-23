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
  await figma.loadFontAsync({ family: "Inter", style: "Medium" });
  await figma.loadFontAsync({ family: "Inter", style: "Regular" });

  const frame = figma.createFrame();
  frame.name = payload.frame_name;
  frame.resize(payload.frame_width, payload.frame_height);
  frame.x = payload.x || 0;
  frame.y = payload.y || 0;
  frame.clipsContent = true;
  frame.fills = [{ type: "SOLID", color: { r: 0.957, g: 0.957, b: 0.957 } }];

  const card = figma.createFrame();
  card.name = "email/card";
  card.resize(payload.frame_width - 48, payload.frame_height - 48);
  frame.appendChild(card);
  card.x = 24;
  card.y = 24;
  card.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];
  card.cornerRadius = 8;

  const subject = figma.createText();
  subject.name = "email/subject";
  subject.resize(card.width - 48, 28);
  card.appendChild(subject);
  subject.x = 24;
  subject.y = 24;
  subject.fontName = { family: "Inter", style: "Medium" };
  subject.fontSize = 16;
  subject.characters = payload.subject || "Email";

  const body = figma.createText();
  body.name = "email/body";
  body.textAutoResize = "HEIGHT";
  body.resize(card.width - 48, 20);
  card.appendChild(body);
  body.x = 24;
  body.y = 64;
  body.fontName = { family: "Inter", style: "Regular" };
  body.fontSize = 13;
  body.characters = payload.body || "";

  return frame;
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
