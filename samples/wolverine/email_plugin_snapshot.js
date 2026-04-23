// Email screen renderer snapshot — locked 2026-04-23
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
  chevron.fills = [{ type: "SOLID", color: { r: 0.8, g: 0.8, b: 0.8 } }];

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
