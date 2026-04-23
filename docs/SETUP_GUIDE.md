# SF UX Orchestrator v2 — Setup Guide

For Salesforce Experience Architects. No prior engineering experience required.
Estimated time: 30–45 minutes on first setup.

---

## What this tool does

SF UX Orchestrator takes your design review notes and turns them into a structured
presentation showing Agentforce conversation flows across Web, SMS, and Email channels.
You run it from the command line using Claude Code.

Pipeline at a glance:

```
Your transcript  →  onboarding  →  ingestion  →  generate  →  push (Figma)  →  export  →  presentation.pptx
```

---

## Prerequisites

Before starting, confirm you have:

- A **Salesforce laptop** on the corporate network (or VPN)
- A **Figma Professional or Org account** with access to create files
- Access to the **SLDS Agentic Experiences** Figma library (request from your design ops team if not already in your Figma)
- **Node.js 18+** — check with `node --version`; install from https://nodejs.org if missing
- **Python 3.10+** — check with `python3 --version`; install from https://python.org if missing

---

## Step 1 — Install Claude Code (Salesforce)

> If you previously installed Claude Code via `npm` or `brew`, uninstall those first:
> ```
> npm uninstall -g @anthropic-ai/claude-code
> brew uninstall claude-code
> ```
> Then open a fresh terminal window before continuing.

Open Terminal (`⌘ Space` → type `Terminal` → Enter) and run:

```bash
curl -fsSL https://plugins.codegen.salesforceresearch.ai/claude/install.sh | bash
```

The installer will:
1. Check your system
2. Install the Claude Code binary
3. Open a browser tab for Google sign-in — **sign in with your @salesforce.com account**
4. Exchange your Google token for a Salesforce LLM key
5. Write everything to `~/.claude/settings.json` automatically

When it finishes you'll see:

```
[✔] LLM Key has been updated in the ~/.claude/settings.json
==> Installation complete!
```

Then run:

```bash
source ~/.zshrc
```

**Verify it worked:**

```bash
mkdir -p ~/claude && cd ~/claude && claude --version
```

**Troubleshooting:**

- `~/.cache/claude` permission error → `sudo chown -R $(whoami) ~/.cache/claude` then re-run
- Token expired later → visit https://eng-ai-model-gateway.sfproxy.devx-preprod.aws-esvc1-useast2.aws.sfdc.cl/ and re-run the installer

---

## Step 2 — Clone the repo and install dependencies

```bash
git clone https://github.com/bfurgason-lgtm/sf-ux-orchestrator-v2.git
cd sf-ux-orchestrator-v2
```

Install Python dependencies:

```bash
pip3 install -r requirements.txt
```

Install Node dependencies:

```bash
npm install
```

---

## Step 3 — Set up your `.env` file

The pipeline needs two credentials in a `.env` file at the repo root.

```bash
cp .env.example .env
```

Then open `.env` and fill in the two values:

```
FIGMA_ACCESS_TOKEN=your_token_here
ANTHROPIC_API_KEY=your_key_here
```

### Getting your Figma access token

1. Go to https://www.figma.com and sign in
2. Click your profile picture → **Settings**
3. Scroll to **Personal access tokens**
4. Click **Generate new token**, give it a name (e.g. `sf-ux-orchestrator`)
5. Copy the token — you won't be able to see it again
6. Paste it as `FIGMA_ACCESS_TOKEN` in `.env`

### Getting your Anthropic API key

This key is used by the ingestion agent to extract decisions from your transcripts
using Claude. Without it the tool still works, but conflict detection between
decisions is disabled and extraction is less accurate.

1. Go to https://console.anthropic.com and sign in (create a free account if needed)
2. Navigate to **API Keys** → **Create Key**
3. Copy the key and paste it as `ANTHROPIC_API_KEY` in `.env`

---

## Step 4 — Create your Figma file and get the file key

The pipeline writes frames into a Figma file you own. You need to create that file
manually and paste its key into your project config.

1. Open **Figma Desktop** (not the browser — the plugin step requires the desktop app)
2. Create a new file: **File → New File**
3. Name it something like `NovaMed Health — Agentforce Flows`
4. Copy the file key from the URL:
   - The URL looks like: `https://www.figma.com/design/AbCdEfGhIjKl/My-File`
   - The file key is the segment between `/design/` and the next `/` — e.g. `AbCdEfGhIjKl`

You'll paste this into your project config after running onboarding (Step 6).

---

## Step 5 — Enable the SLDS Agentic Experiences library in your Figma file

The plugin draws frames using real SLDS components. Your Figma file needs to have
the SLDS Agentic Experiences library enabled.

1. In your new Figma file, open the **Assets** panel (left sidebar, grid icon)
2. Click the **book icon** (Libraries) at the top of the Assets panel
3. Find **SLDS 2 - Agentic Experiences** in the list
4. Toggle it on
5. Close the libraries panel

If you don't see the library, ask your design ops team to share it with your Figma org.

---

## Step 6 — Run onboarding for your client

From the repo root, run:

```bash
python3 agents/onboarding.py
```

Answer the six questions. Example for a healthcare client:

```
1/6  What is your org or client name?
> NovaMed Health

2/6  Which channels are in scope? (web / sms / email — comma-separated)
> web, sms

3/6  What Salesforce field is used to look up a customer's order?
> Appointment_ID__c

4/6  What order status values does your system use?
> Scheduled, In Progress, Completed, Cancelled, No-Show

5/6  What happens when an order can't be found?
> Offer to search by patient name or phone number

6/6  Any additional edge cases to document?
> Duplicate Appointment, Provider Cancellation
```

Onboarding creates `projects/novamed-health/` with all the config files.

**Now paste your Figma file key:**

Open `projects/<your-client>/project.json` and fill in the `file_key` and `file_url` fields:

```json
"figma": {
  "file_key": "AbCdEfGhIjKl",
  "file_url": "https://www.figma.com/design/AbCdEfGhIjKl/",
  ...
}
```

---

## Step 7 — Add your transcript and run ingestion

Drop your design review notes, meeting transcript, or requirements doc into:

```
projects/<your-client>/transcripts/
```

Supported formats: `.txt`, `.md`, `.pdf`, `.docx`

Then run:

```bash
python3 agents/ingestion.py --project projects/<your-client>
```

This extracts UX decisions from your transcript, detects conflicts, and writes
`decisions.json`. Each run reports how many decisions were added and the current
source-of-truth version.

---

## Step 8 — Generate screen payloads

```bash
python3 orchestrate.py generate --project projects/<your-client> --channels web sms
```

This reads your `manifest.json`, builds a frame payload for each step and channel,
and saves them to `exports/pending/`. It also writes `build_spec.json` to your
project folder.

If your `manifest.json` only has the stub from onboarding (empty `flows: []`),
you'll need to populate the flows first — see the sample at `samples/wolverine/manifest.json`
for the full structure, or work with Claude Code to generate flows from your decisions.

---

## Step 9 — Push frames to Figma (plugin step)

This step uses a locally-generated Figma plugin to draw the frames in your file.

**Run the server:**

```bash
python3 orchestrate.py push --project projects/<your-client>
```

This builds the plugin into `exports/plugin/` and starts a local server on port 7070,
then prints instructions. While it waits, switch to Figma Desktop.

**Install and run the plugin (one-time per file):**

1. Open your Figma file in **Figma Desktop**
2. Menu bar → **Plugins → Development → Import plugin from manifest...**
3. Navigate to `exports/plugin/manifest.json` in the repo and select it
4. Menu bar → **Plugins → Development → SF UX Orchestrator → Run**

The plugin fetches the pending frames from `localhost:7070`, draws them in your
Figma file, and reports back. The terminal will confirm completion.

> The plugin only needs to be imported once per Figma file. On subsequent runs,
> you can go straight to **Plugins → Development → SF UX Orchestrator → Run**.

---

## Step 10 — Export frames as PNGs

```bash
python3 orchestrate.py export --project projects/<your-client>
```

This pulls the rendered frames from Figma at 2x resolution and saves them to
`exports/<your-client>/screens/`.

---

## Step 11 — Generate the presentation

```bash
node generate_presentation.js --project projects/<your-client>
```

Reads your manifest and the exported PNGs, builds the slide deck, and writes it to:

```
exports/<your-client>/presentation.pptx
```

Open it in PowerPoint or Keynote.

---

## Step 12 — Check for drift after changes

If you add new transcripts and re-run ingestion, run this to see which artifacts
are out of date and need to be regenerated:

```bash
python3 agents/change_propagation.py --project projects/<your-client>
```

It prints a report and recommends the regeneration order. Nothing is changed
automatically — you decide what to rerun.

---

## Quick reference — full pipeline

```bash
# First time
python3 agents/onboarding.py

# Each time you have new transcripts
python3 agents/ingestion.py --project projects/<client>

# Generate + Figma + export + presentation
python3 orchestrate.py generate --project projects/<client> --channels web sms
python3 orchestrate.py push     --project projects/<client>
python3 orchestrate.py export   --project projects/<client>
node generate_presentation.js   --project projects/<client>

# Check for drift
python3 agents/change_propagation.py --project projects/<client>
```

---

## Project folder structure

After onboarding, your project folder looks like this:

```
projects/<client>/
├── config.user.json       — your answers from onboarding
├── manifest.json          — flow definitions (edit this to add steps)
├── project.json           — Figma file config (paste your file key here)
├── decisions.json         — extracted decisions from transcripts
├── artifact_versions.json — tracks which artifacts are current
├── build_spec.json        — generated after first 'generate' run
├── transcripts/           — drop your .txt / .md / .pdf / .docx files here
└── change_report_v*.md    — drift reports from change propagation
```

---

## Troubleshooting

**`Could not create Figma file` on generate**
You haven't set `figma.file_key` in `project.json`. Create a file in Figma Desktop
manually and paste the key — see Step 4.

**Plugin doesn't appear in Figma**
Make sure you're using **Figma Desktop**, not the browser. The plugin API is only
available in the desktop app.

**`ANTHROPIC_API_KEY not set` warning during ingestion**
Ingestion still works but uses simpler rule-based extraction. Add your Anthropic
API key to `.env` for Claude-powered extraction and conflict detection.

**Claude Code token expired**
Visit https://eng-ai-model-gateway.sfproxy.devx-preprod.aws-esvc1-useast2.aws.sfdc.cl/
and re-run the installer:
```bash
curl -fsSL https://plugins.codegen.salesforceresearch.ai/claude/install.sh | bash
```

**Port 7070 already in use during push**
Another process is using that port. Pass a different one:
```bash
python3 orchestrate.py push --project projects/<client> --port 7071
```
