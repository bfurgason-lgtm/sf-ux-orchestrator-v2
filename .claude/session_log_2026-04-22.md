# Session Log — 2026-04-22

## Goal
Build a Figma plugin that generates production-quality Agentforce conversation flow screens using real SLDS 2 Agentic Experiences components, driven by the existing manifest.json → screen_generator.py pipeline.

---

## What Was Built

### 1. Figma Plugin Infrastructure (exports/plugin/)
- Fixed `manifest.json` validation errors: added `editorType`, changed `allowedDomains` to `["none"]`, added `devAllowedDomains`
- Established that `plugin_builder.py` regenerates both files on every `push` — all plugin changes MUST go in the `_CODE_JS_TEMPLATE` string there
- Switched from raw primitive drawing to `figma.importComponentByKeyAsync()` with real SLDS keys

### 2. SLDS Component Key Discovery (exports/plugin/discover.js)
- Built a one-shot discovery script that scanned placed instances on the Wolverine Figma canvas
- Enabled "SLDS 2 - Agentic Experiences" library in the Wolverine file
- Extracted all component keys:
  - `agentAvatar`:  `acff7615fd4e208badc057f155bc6c88ac981700`
  - `agentMessage`: `4f89db7196e0d41880c6a2b2bb7908ce403173b6`
  - `userMessage`:  `379d6763d4edc0460a108e96176aa63c80404e7c`
  - `feedPanel`:    `47443262e3d3ca2c01723aa73ed6650c44086381`
  - `welcome`:      `b0e160e0d34247af67553a845193b1c42facad35`
  - `disclaimer`:   `d2ff9d418379534c8e3bbec22e717736e12b82df`

### 3. screen_generator.py — Rewritten
- Changed payload format from raw Figma shape tree to flat message array:
  - Chat: `{frame_name, channel, frame_width, frame_height, x, y, messages:[{role,text}]}`
  - Email: `{...subject, body}`
- Removed all raw rectangle/text/ellipse node building from Python
- plugin_server.py updated to match new `frame_name` field (was `frame.name`)

### 4. plugin_builder.py — Full JS Template Rewrite (multiple iterations)
Progressed through several approaches:

**Attempt 1:** Raw primitives (rectangles, ellipses, text) — worked but 50% quality, no consistency  
**Attempt 2:** SLDS Feed Panel as container + message components — Feed Panel had uncontrollable placeholder content ("Curabitur..."), action "Label" buttons showed  
**Attempt 3:** Custom chrome + SLDS message components — components' widths couldn't be overridden for right-alignment  
**Attempt 4:** Fully custom bubble drawing with SLDS avatar only — gave pixel control, added timestamps, production footer  
**Attempt 5 (current):** Auto-layout frames throughout — outer frame (vertical AL) containing Header / Messages / Footer, each message row as horizontal AL with avatar + bubble column

### 5. Auto-Layout Implementation (current state)
- `outer` frame: vertical AL, fixed W×H, clips content
- `Header`: horizontal AL, fixed 56px tall, SLDS avatar + title + spacer + online dot
- `Messages`: vertical AL, hugs height, clips to frame
- Each `row`: horizontal AL, hugs height, agent=left-aligned, user=right-aligned
- `bubble`: vertical AL with padding, hugs height, corner radius 12
- `timestamp`: fixed-size text below each bubble, progressive clock (10:00 AM +1min per message)
- `Footer`: horizontal AL, fixed 72px, input pill (horizontal AL) with attach circle, placeholder text, send button

### 6. Bugs Discovered and Fixed (Figma Plugin API)
| Error | Fix |
|---|---|
| `editorType` missing | Added to manifest and plugin_builder template |
| `allowedDomains` invalid | Changed to `["none"]` |
| Frames blank after creation | x/y must be set AFTER `appendChild()` |
| Fill color crashes | Alpha goes as `opacity` on fill, not inside `color:{r,g,b}` |
| `Unexpected token ...` | Figma JS engine doesn't support spread syntax — use explicit assignment |
| `Inter SemiBold` not found | Correct name is `"Semi Bold"` (with space) |
| `counterAxisSizingMode = "HUG"` invalid | Frame-level sizing uses `"AUTO"` not `"HUG"` |
| `layoutSizingVertical = "AUTO"` invalid | Child-level sizing uses `"HUG"/"FILL"/"FIXED"` not `"AUTO"` |
| `strokeAlign` invalid on rectangles | Remove it |
| Off-canvas text `.height` returns NaN | Estimate height mathematically |
| `FILL` on unsupported node | `layoutSizingHorizontal/Vertical = "FILL"` only works after `appendChild()` |
| Children of vertical AL default to `FILL` height | Must explicitly set `layoutSizingVertical = "HUG"` after appending |

---

## Current State (end of session)

**Working:**
- Header renders correctly with SLDS avatar, title, online dot
- Agent bubbles left-aligned with avatar, gray background
- User bubbles right-aligned, blue tint background
- Progressive timestamps (10:00 AM, 10:01 AM...)
- Footer with pill input, attach button, send button
- Auto-layout structure visible in Figma layers panel
- 9 frames generated for Wolverine WISMO + Defective_Returns flows (web channel)

**Still in progress:**
- Bubble height hugging — `layoutSizingVertical = "HUG"` on rows/messages not yet confirmed working (last run when session ended)
- SMS and email channels not yet tested with new plugin
- Timestamps showing but position may need tuning once height is resolved

---

## Files Modified This Session
- `integrations/figma/plugin_builder.py` — complete rewrite of JS template
- `integrations/figma/screen_generator.py` — complete rewrite (flat payload format)
- `integrations/figma/plugin_server.py` — minor fix to frame name field
- `exports/plugin/manifest.json` — regenerated (points to code.js, correct networkAccess)
- `exports/plugin/code.js` — regenerated from template
- `exports/plugin/discover.js` — new file (one-shot component discovery)
- `samples/wolverine/project.json` — reset multiple times for regeneration
- `.claude/memory/project_overview.md` — updated with full file map, SLDS keys, workflow commands
- `.claude/memory/feedback_figma_plugin.md` — new file, all Figma API gotchas

---

## Workflow to Run Next Session
```bash
# 1. Kill any stale server
kill $(lsof -ti:7070) 2>/dev/null

# 2. Reset project (if regenerating from scratch)
# Edit samples/wolverine/project.json: set last_frame_y:0, generated_frames:[]
# Delete exports/pending/*.json

# 3. Generate payloads
python3 orchestrate.py generate --project samples/wolverine --channels web

# 4. Start server
python3 orchestrate.py push --project samples/wolverine &

# 5. In Figma: Plugins → Development → SF UX Orchestrator → Run
```

## Next Steps
1. Confirm bubble hug height is working correctly
2. Tune layout spacing and padding
3. Test SMS and email channels
4. Consider adding branding support (custom persona name, avatar)
5. Google Slides integration — pipe generated screens into presentation template
