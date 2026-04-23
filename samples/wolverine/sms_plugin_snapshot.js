// SMS screen renderer snapshot — locked 2026-04-23
// This is the approved createSmsScreen function from plugin_builder.py.
// Do not edit. Reference only.

async function createSmsScreen(payload) {
  const W = payload.frame_width  || 390;
  const H = payload.frame_height || 844;

  await figma.loadFontAsync({ family: "Inter", style: "Regular" });
  await figma.loadFontAsync({ family: "Inter", style: "Semi Bold" });

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

  var bubbleTxtW = Math.round(W * 0.72) - 32 - 8 - 24;

  const rowAgentBubble = figma.createFrame();
  rowAgentBubble.name = "row_agentBubble";
  rowAgentBubble.fills = [];
  rowAgentBubble.layoutMode = "HORIZONTAL";
  rowAgentBubble.itemSpacing = 8;
  rowAgentBubble.paddingTop    = 0;
  rowAgentBubble.paddingBottom = 0;
  rowAgentBubble.paddingLeft   = 0;
  rowAgentBubble.paddingRight  = 0;
  rowAgentBubble.primaryAxisSizingMode = "FIXED";
  rowAgentBubble.counterAxisSizingMode = "AUTO";
  rowAgentBubble.primaryAxisAlignItems = "MIN";
  rowAgentBubble.counterAxisAlignItems = "MIN";
  rowAgentBubble.resize(W - 32, 10);

  const smsAvatar = figma.createEllipse();
  smsAvatar.name = "avatar";
  smsAvatar.resize(32, 32);
  smsAvatar.fills = [{ type: "SOLID", color: { r: 0.227, g: 0.227, b: 0.235 } }];

  const smsBubble = figma.createFrame();
  smsBubble.name = "bubble";
  smsBubble.cornerRadius = 18;
  smsBubble.fills = [{ type: "SOLID", color: { r: 0.11, g: 0.11, b: 0.118 } }];
  smsBubble.layoutMode = "VERTICAL";
  smsBubble.itemSpacing = 0;
  smsBubble.paddingTop    = 12;
  smsBubble.paddingBottom = 12;
  smsBubble.paddingLeft   = 12;
  smsBubble.paddingRight  = 12;
  smsBubble.primaryAxisSizingMode = "AUTO";
  smsBubble.counterAxisSizingMode = "AUTO";

  var smsMessages = payload.messages || [];
  var firstAgentMsg = null;
  for (var mi = 0; mi < smsMessages.length; mi++) {
    if (smsMessages[mi].role === "agent") { firstAgentMsg = smsMessages[mi]; break; }
  }
  var bubbleContent = firstAgentMsg ? firstAgentMsg.text : "How can I help you today?";

  const smsBubbleTxt = figma.createText();
  smsBubbleTxt.name = "bubble-text";
  smsBubbleTxt.fontName = { family: "Inter", style: "Regular" };
  smsBubbleTxt.fontSize = 17;
  smsBubbleTxt.textAutoResize = "HEIGHT";
  smsBubbleTxt.resize(bubbleTxtW, 20);
  smsBubbleTxt.characters = bubbleContent;
  smsBubbleTxt.fills = [{ type: "SOLID", color: { r: 1, g: 1, b: 1 } }];
  smsBubble.appendChild(smsBubbleTxt);
  smsBubbleTxt.layoutSizingVertical = "HUG";

  rowAgentBubble.appendChild(smsAvatar);
  smsAvatar.layoutSizingHorizontal = "FIXED";
  smsAvatar.layoutSizingVertical   = "FIXED";

  rowAgentBubble.appendChild(smsBubble);
  smsBubble.layoutSizingHorizontal = "HUG";
  smsBubble.layoutSizingVertical   = "HUG";

  messagesArea.appendChild(rowAgentBubble);
  rowAgentBubble.layoutSizingHorizontal = "FILL";
  rowAgentBubble.layoutSizingVertical   = "HUG";

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

  outer.appendChild(messagesArea);
  messagesArea.layoutSizingVertical = "FILL";

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
