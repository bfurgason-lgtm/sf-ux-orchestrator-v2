---
name: Email slide layout — approved card structure
description: Approved layout for email channel slides in the WISMO presentation generator
type: project
---

Approved layout as of 2026-04-23 (commit ~18c68cc, further refined same session).

**Structure:** Two-column newspaper flow. Messages render as cards chronologically — left column top-to-bottom, overflow into right column top-to-bottom. No PNGs used for email slides.

**Each card contains:**
- Colored avatar circle with initials (orange `E8A838` = customer, blue `0070D2` = agent)
- Bold sender name + email address
- "to" address line below sender
- Timestamp top-right
- Body text with line wrapping

**Implementation:** `buildEmailFlowSlide(pptx, steps, channelLabel, messages)` in `generate_presentation.js`. Messages array is passed in from `main()` as `WISMO_EMAIL_MESSAGES`. Card heights are calculated dynamically from line count.

**Feedback (outstanding):** Structure is right but conversation content is incomplete — more turns should be added to the messages array to reflect the full exchange (e.g. customer acknowledgment, agent close). Currently only 2 messages: customer inquiry + agent resolution.

**Why:** Email is async/threaded — doesn't suit a screenshot-per-step approach. Cards are more readable at presentation scale than PNG thumbnails of email frames.
