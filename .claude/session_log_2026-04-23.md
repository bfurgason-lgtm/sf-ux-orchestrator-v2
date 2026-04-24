# Session Log — 2026-04-23

Two chat conversations. Picked up from where the 2026-04-22 session left off (Figma plugin working for web channel, SMS and email not yet tested).

---

## Conversation 1 — Presentation Generator + Email Channel

### Goal
Build a PowerPoint presentation of the WISMO Agentforce flow across all three channels, and fix outstanding issues with the email channel Figma renderer.

### What Was Built

#### 1. WISMO Presentation Generator (`generate_presentation.js`)
- Built from scratch using `pptxgenjs`
- Output: `exports/wolverine/WISMO_presentation.pptx`
- Slide structure:
  - Cover slide (dark navy, Salesforce blue tokens, channel chips)
  - Section divider per channel (Web, SMS, Email)
  - Main flow slides: pill row (steps 1–5 with active highlight + arrows), Figma frame screenshots at aspect-fit
  - Edge case slides (steps 6–7): left column description + right column web frame
- Design tokens: dark navy bg, Salesforce blue accent, Calibri font, gray pills, red for edge case pills
- Max 6 frames per slide with overflow to next page

#### 2. Email Sender/Recipient Direction Fix
- Steps 2–5 were rendering with customer as sender and Wolverine as recipient — backwards
- Fixed `manifest.json`: all agent-reply steps set to `sender_name=Wolverine Support`, `sender_email=orders@wolverine.com`, `to_address=jsmith@acme.com`
- Re-rendered four affected frames in Figma and re-exported PNGs

#### 3. Email Slide Layout Iterations
- **Attempt 1:** Stacked PNGs flush (no gap) in two columns — email frames too small to read at slide scale
- **Attempt 2:** Per-step aspect ratio correction with real pixel heights per step — better but still unreadable
- **Attempt 3:** Left col = step 1 PNG, right col = step 2 PNG — same readability problem

#### 4. PNG Export Pipeline Fix
- `exporter.py` was passing `'PNG'` to the Figma API which requires lowercase `'png'`
- Fixed format param to `.lower()` before sending

---

## Conversation 2 — Email Flow Redesign + Presentation Polish

### Goal
Rethink the email channel entirely: condense the conversation to fewer turns, fix turn-taking logic (agent shouldn't need to verify identity when sender email is present), and find a presentation format that actually reads at slide scale.

### What Was Built / Changed

#### 1. WISMO Email Flow — Collapsed to 2 Turns
- Original: 5 separate emails (customer asks → agent asks for order # → agent confirms order → agent gives status → agent closes). Customer would have to send/receive 5 emails — unacceptable UX.
- New design:
  - **Step 1 (customer → agent):** Jane Smith asks about her order via email. Sender email (`jsmith@acme.com`) present — sufficient PII to look up the account.
  - **Step 2 (agent → customer):** Wolverine Support replies in a single message — identity confirmed by sender email, order found, status + tracking number provided, conversation closed.
- Steps 3–5 removed from manifest and from `project.json` / `acknowledged/` exports
- Edge cases (steps 6 & 7) sender direction also fixed (were still showing customer as sender)

#### 2. Thread Reply Rendering in Figma Plugin
- Added `thread_reply` field to email payload schema
- `plugin_builder.py` `createEmailScreen()` now renders a quoted reply section below the agent card:
  - Gray background section
  - Green customer avatar
  - Customer sender name + email bold
  - Timestamp
  - Quoted body text at slightly smaller size
- `screen_generator.py` passes `thread_reply` through to plugin payload
- Re-generated and re-exported `WISMO_step-2_email`, `WISMO_step-6_email`, `WISMO_step-7_email` — confirmed working in Figma

#### 3. `generate_presentation.js` — Email Slide Redesign
- Moved away from PNGs for email entirely
- **Final approved structure:** Two-column newspaper card layout
  - Messages flow chronologically: left column top-to-bottom, overflow to right column top-to-bottom
  - Each message is a drawn card: colored avatar circle (orange = customer, blue = agent), bold sender name + email, "to" address, timestamp top-right, body text
  - Card heights calculated dynamically from line count
  - Thin vertical divider only drawn when both columns have content
- `WISMO_STEPS` (5-step web/sms) and `WISMO_EMAIL_STEPS` (2-turn email) now separate — web and SMS retain full 5-step progression with 6-per-page overflow; email uses card layout
- `WISMO_EMAIL_MESSAGES` array in `main()` drives right-side card content — data-driven, not hardcoded per column

#### 4. `generate` Pipeline Bug Fixed
- `orchestrate.py generate` was defaulting to `max_screens=1`, silently skipping all steps after the first
- Fix: always pass `--screens 10` (or higher) when regenerating email-only

#### 5. `project.json` State Management
- Cleared stale `generated_frames` entries for email steps 2, 3, 4, 5 so regeneration would run
- Fixed trailing comma JSON parse error introduced during manual edit

---

## Files Modified Today

| File | Change |
|---|---|
| `generate_presentation.js` | Built from scratch; multiple layout iterations; final card-based email layout |
| `integrations/figma/plugin_builder.py` | Added thread reply rendering to email screen |
| `integrations/figma/screen_generator.py` | Pass `thread_reply` field through to plugin payload |
| `integrations/figma/exporter.py` | Fix format param case for Figma API |
| `samples/wolverine/manifest.json` | Collapse WISMO email to 2 turns; fix steps 6–7 sender direction |
| `samples/wolverine/project.json` | Clear stale email frame entries; fix trailing comma |
| `samples/wolverine/build_spec.json` | Regenerated |
| `exports/acknowledged/WISMO_step-2_email.json` | Updated with new body + thread_reply |
| `exports/acknowledged/WISMO_step-6_email.json` | Corrected sender direction + thread_reply |
| `exports/acknowledged/WISMO_step-7_email.json` | Corrected sender direction + thread_reply |
| `exports/acknowledged/WISMO_step-3/4/5_email.json` | Deleted (steps no longer exist) |
| `exports/wolverine/WISMO_presentation.pptx` | Regenerated multiple times |
| `package.json` / `package-lock.json` | Added pptxgenjs dependency |

---

## Commits Today

| Hash | Message |
|---|---|
| `4983364` | Add WISMO presentation generator (pptxgenjs) + fix PNG export |
| `9efa9f7` | Record last_export_at timestamp after WISMO frame export |
| `d6f2d08` | Fix pill spacing and rebuild email slide as two-column stacked layout |
| `11382c5` | Fix email slide: per-step aspect ratio + flush thread layout |
| `38bc716` | Fix email sender/recipient direction for WISMO steps 2-5 |
| `18c68cc` | Collapse WISMO email to 2-turn thread, add quoted reply rendering |

---

## Current State (end of session)

**Working:**
- Web channel: 5-step presentation slides with cumulative conversation progression, pill row, Figma PNGs
- SMS channel: same as web
- Email channel: 2-turn card layout — approved structure, left-to-right newspaper flow
- Figma email frames: thread reply section rendering correctly (agent card + quoted customer message below)
- Presentation generates cleanly end-to-end: `node generate_presentation.js`

**Outstanding:**
- Email `WISMO_EMAIL_MESSAGES` array only has 2 messages (customer inquiry + agent resolution). User noted the conversation feels incomplete — a customer acknowledgment and agent close should be added as additional cards.
- Edge case email slides (steps 6 & 7) use the same card structure but their message content has not been updated to match — currently showing default fallback.
- `--screens` flag footgun: `orchestrate.py generate` defaults to `max_screens=1` — must always pass `--screens 10` when regenerating multi-step flows.

---

## Next Steps (Conversation 2)
1. Add customer acknowledgment + agent close turns to `WISMO_EMAIL_MESSAGES`
2. Build equivalent card message arrays for edge case email slides (steps 6 & 7)
3. Defective_Returns email flow — same 2-turn collapse treatment
4. Consider whether `max_screens` default in `orchestrate.py` should be raised or removed

---

## Conversation 3 — End-to-End Product Test, Cleanup Pass, Setup Guide Rewrite

### Goal
Confirm the tool works for any client (not just Wolverine), fix five cosmetic issues
found during testing, and replace the stale setup documentation with a guide that
reflects the actual pipeline.

### 1. End-to-end product test — NovaMed Health

Ran the full pipeline as a first-time Experience Architect using a completely
fictional client: **NovaMed Health** — healthcare appointment scheduling.
Different industry, different field names (`Appointment_ID__c`), different
statuses (Scheduled, In Progress, Completed, Cancelled, No-Show).

Stages tested:
- `agents/onboarding.py` — 6-turn dialogue, created `projects/novamed-health/`
- Wrote a fictional design review transcript, ran `agents/ingestion.py`
- Built a full NovaMed `manifest.json` (4 main steps + 2 edge cases)
- `orchestrate.py generate` — pending payloads written (expected, no real Figma key)
- `node generate_presentation.js` — generated `exports/novamed-health/presentation.pptx`
- `agents/change_propagation.py` — correctly reported NovaMed client name, detected `figma_pngs` stale

Result: zero Wolverine contamination in any NovaMed output. Pipeline is fully client-agnostic.

Five issues found and reported:
1. Ingestion bumped `source_of_truth_version` on no-op re-runs
2. `file_manager.py` error message pointed to `samples/` instead of `projects/`
3. Wolverine placeholder values in core templates
4. `orchestrate.py` docstring used `samples/wolverine` as only example
5. Stale `WISMO_EMAIL_MESSAGES` variable name in `generate_presentation.js` comment

### 2. Five-fix cleanup pass

Commit: `28566a4`

- **Ingestion version bump** (`agents/ingestion.py`): `source_of_truth_version`
  now only increments when `stats["added"] > 0`. Verified: same transcript run
  twice stays at v1.
- **file_manager error message**: `samples/<project>` → `projects/<project>`
- **Wolverine placeholders removed** from all five flagged templates plus two
  additional ones found in the same scan (`support_response.json`,
  `conversation_thread.json`). All replaced with `{brand_name}`, `{product_name}`,
  `yourcompany`, `example.com` equivalents.
- **orchestrate.py docstring**: all four example lines updated to `projects/<client>`
- **generate_presentation.js comment**: `WISMO_EMAIL_MESSAGES-style array`
  → `emailMessages array`

Remaining legitimate Wolverine references (intentional, not touched):
- `generate_presentation.js` legacy usage note pointing to `samples/wolverine`
- `manifest_v0_5.json` schema description `"e.g., 'Wolverine Worldwide', 'Acme Corp'"`
- `plugin_builder.py` provenance comment about SLDS component key source

### 3. Setup guide audit and rewrite

Audit found: existing `docs/SETUP_GUIDE.md` described a completely different
architecture (Cursor MCP, Drive monitoring, `core/monitors/`, `cursor-agent` CLI)
that doesn't exist in the codebase. `requirements.txt` had ~20 unused packages.
No `.env.example`. No mention of Claude Code anywhere.

Gaps closed:
- Full Salesforce-specific Claude Code install path documented (see below)
- Figma personal access token — where to generate, where to paste
- Anthropic API key — where to generate, what it's used for, graceful without it
- Figma file setup — create file, extract key from URL, paste into `project.json`
- SLDS Agentic Experiences library — how to enable in the Figma file
- Plugin install flow — Figma Desktop only, exact menu path
- Full 12-step pipeline walkthrough with NovaMed examples
- Troubleshooting section covering the most likely failure modes

Salesforce Claude Code installer (discovered from internal Slack doc):
```
curl -fsSL https://plugins.codegen.salesforceresearch.ai/claude/install.sh | bash
```
Single command: installs binary, opens Google SSO, exchanges token for Salesforce
LLM key, writes `~/.claude/settings.json` automatically. No manual token pasting.
Token expiry: revisit `https://eng-ai-model-gateway.sfproxy.devx-preprod.aws-esvc1-useast2.aws.sfdc.cl/` and re-run installer.

Commit: `377a921`

Files changed:
- `docs/SETUP_GUIDE.md` — full rewrite, 12 steps
- `requirements.txt` — trimmed to 3 real deps (`requests`, `python-dotenv`, `anthropic`)
- `.env.example` — new committed template
- `.gitignore` — `!.env.example` added

### 4. Missing files committed

Commit: `a14057d`

Six-agent pipeline files built in a previous session were never fully staged:
`agents/onboarding.py`, `agents/change_propagation.py`, `agents/utils/`,
`core/config.defaults.json`, `.cursorrules`, and integrations updates to
`plugin_server.py` and `screen_generator.py`.

---

## Commits (Conversation 3)

| Hash | Message |
|---|---|
| `28566a4` | fix: cosmetic cleanup, remove Wolverine references from templates and docs, fix ingestion version bump logic |
| `377a921` | docs: rewrite SETUP_GUIDE for actual pipeline, add .env.example, trim requirements.txt |
| `a14057d` | chore: commit missing agent files and integrations updates from six-agent build |

---

## Current State (end of day)

**Working end-to-end for any client:**
- Onboarding → ingestion → generate → presentation pipeline is fully config-driven
- Wolverine is a reference example only; no hardcoded client data in source
- Setup guide reflects the actual tool
- All agent files committed to main

**Not yet wired:**
- `manifest.json` population after onboarding — users must hand-edit or use Wolverine as reference
- Figma file key not collected during onboarding — user must manually edit `project.json`
- `slds.agentic_file_key` in `project.json` stub is not wired to `plugin_builder.py`
  (SLDS component keys are still hardcoded)

---

## Next Steps

### High priority
1. **Turn 7 in onboarding — Figma file URL**: ask for the Figma file URL during
   onboarding, parse the key, write it to `project.json` automatically. Eliminates
   the manual edit step that currently breaks first-time users.

2. **Manifest population flow**: after onboarding, `manifest.json` has `"flows": []`.
   Options: (a) a manifest builder agent that generates flow stubs from `decisions.json`,
   (b) extend onboarding with flow definition turns, (c) document the manual path
   more clearly in SETUP_GUIDE.

3. **Rewrite README.md**: current README describes the old architecture and is
   misleading. Should describe the actual tool, link to SETUP_GUIDE, show the
   quick-start command sequence.

### Medium priority
4. **SLDS component key portability**: hardcoded keys in `plugin_builder.py` were
   sourced from the Wolverine Figma file. A new org's library may have different
   keys. Wire `slds.agentic_file_key` from `project.json` into `plugin_builder.py`
   and add a validation step.

5. **Dead env var**: `FIGMA_REFERENCE_FILE_KEY` is in the old `.env` but nothing
   in the codebase reads it. Remove from documentation.

6. **ingestion.py Claude model version**: hardcoded `claude-sonnet-4-6` should
   come from config/defaults.

### Lower priority
7. **samples/acme-corp/manifest.json**: minimal stub with no flows — either flesh
   out as a second reference example or remove.

8. **projects/ tracking strategy**: `projects/` is entirely untracked. Consider
   committing `config.user.json`, `manifest.json`, `decisions.json`, and
   `artifact_versions.json` per client while excluding screen exports.

9. **WISMO email outstanding** (from Conversation 2):
   - Add customer acknowledgment + agent close turns to `WISMO_EMAIL_MESSAGES`
   - Update edge case email slides (steps 6 & 7) message content
   - Defective_Returns email flow — same 2-turn collapse treatment
