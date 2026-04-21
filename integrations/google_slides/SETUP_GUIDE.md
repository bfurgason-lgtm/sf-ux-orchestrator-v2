# Google Slides Integration Setup Guide

The sf-ux-orchestrator now includes automated Google Slides presentation generation with three-tier structure and flow diagrams. This guide walks you through the complete setup process.

## 🎯 Overview

The Google Slides integration automatically generates structured presentations from your manifest data, featuring:

- **Three-Tier Structure**: Persona examples, requirements flows, and technical details
- **Automated Flow Diagrams**: Visual representations of conversation flows with decision points
- **Multi-Format Export**: PDF, PowerPoint, and PNG formats
- **Drive Integration**: Automatic export to your Google Drive folders
- **SLDS Compliance**: Design system integration and brand consistency

## 📋 Prerequisites

1. **Google Cloud Console Access**: Admin access to create projects and enable APIs
2. **Google Account**: Account with Google Slides and Drive permissions
3. **Python Environment**: Python 3.7+ with required packages
4. **Manifest v0.5**: Enhanced manifest with `google_slides` configuration

## 🔧 Setup Steps

### Step 1: Google Cloud Console Setup

1. **Create or Select Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Note your Project ID

2. **Enable Required APIs**
   - Navigate to **APIs & Services** > **Library**
   - Search for and enable:
     - Google Slides API
     - Google Drive API (for file exports)

3. **Create OAuth2 Credentials**
   - Go to **APIs & Services** > **Credentials**
   - Click **+ CREATE CREDENTIALS** > **OAuth client ID**
   - Choose **Desktop application** as application type
   - Name it "SF UX Orchestrator Slides"
   - Download the JSON file

### Step 2: Install Dependencies

```bash
cd integrations/google_slides
pip install -r requirements.txt
```

**Required packages:**
- `google-api-python-client==2.108.0`
- `google-auth-httplib2==0.2.0`
- `google-auth-oauthlib==1.1.0`
- `google-auth==2.23.4`
- `Pillow==10.1.0` (for image handling)
- `reportlab==4.0.7` (for PDF generation)

### Step 3: Configure Credentials

1. **Save Credentials File**
   ```bash
   # Save downloaded OAuth2 JSON as:
   mv ~/Downloads/client_secret_*.json integrations/google_slides/credentials.json
   ```

2. **Verify File Location**
   ```bash
   ls -la integrations/google_slides/credentials.json
   ```

### Step 4: First-Time Authentication

Run the authentication flow to create your token:

```python
from integrations.google_slides import GoogleSlidesClient

# This will open browser for OAuth consent
client = GoogleSlidesClient()
print("Authentication successful!")
```

**Expected flow:**
1. Browser opens to Google OAuth consent screen
2. Sign in with your Google account
3. Grant permissions to the application
4. `token.json` file is automatically created
5. Future runs use the saved token

### Step 5: Configure Manifest

Add Google Slides configuration to your manifest:

```json
{
  "schema_version": "0.5",
  "initiative_metadata": {
    "name": "Your Initiative Name"
  },
  "google_slides": {
    "auto_generate": true,
    "template_style": "three_tier",
    "include_flow_diagrams": true,
    "persona_examples": true,
    "export_formats": ["pdf", "pptx"],
    "custom_branding": {
      "logo_url": null,
      "color_scheme": {
        "primary": "#1B4B66",
        "secondary": "#4A90C2",
        "accent": "#5CB85C"
      }
    }
  },
  "flows": [
    // Your conversation flows
  ]
}
```

## 🧪 Testing Your Setup

### Quick Test

```python
from integrations.google_slides import generate_presentation_from_manifest
import json

# Load your manifest
with open('samples/wolverine/manifest.json', 'r') as f:
    manifest = json.load(f)

# Add Google Slides config for testing
manifest['google_slides'] = {
    'auto_generate': True,
    'template_style': 'three_tier',
    'include_flow_diagrams': True,
    'persona_examples': True,
    'export_formats': ['pdf']
}

# Generate presentation
result = generate_presentation_from_manifest(manifest)

if result['success']:
    print(f"✅ Presentation created: {result['presentation']['presentation_url']}")
else:
    print(f"❌ Error: {result['error']}")
```

### Full Integration Test

```bash
# Run the comprehensive test suite
python3 test_google_slides_integration.py
```

### Test with Wolverine Manifest

```python
from integrations.google_slides.orchestrator_integration import SlidesOrchestrator

orchestrator = SlidesOrchestrator()

# Load Wolverine manifest
with open('samples/wolverine/manifest.json', 'r') as f:
    manifest = json.load(f)

# Enable slides generation
manifest['google_slides'] = {'auto_generate': True}

# Generate presentation
result = orchestrator.generate_presentation(manifest)
print(orchestrator.format_orchestrator_report(result))
```

## 🎨 Customization Options

### Template Styles

- **`three_tier`** (recommended): Persona examples → Requirements flows → Technical details
- **`linear`**: Sequential slide progression
- **`custom`**: User-defined template structure

### Flow Diagram Types

- **`main`**: Clean, persona-agnostic requirement flows
- **`edge_cases`**: Exception handling and escalation scenarios  
- **`persona_comparison`**: Brand personality variations side-by-side

### Export Formats

- **`pdf`**: Standard PDF for sharing and printing
- **`pptx`**: Editable PowerPoint format
- **`png`**: Individual slide images

### Brand Customization

```json
{
  "custom_branding": {
    "logo_url": "https://your-domain.com/logo.png",
    "color_scheme": {
      "primary": "#003366",    // Main brand color
      "secondary": "#0066CC",  // Secondary brand color  
      "accent": "#00AA44"      // Accent/highlight color
    }
  }
}
```

## 🔄 Orchestrator Integration

The Google Slides integration works seamlessly with the main orchestrator pipeline:

1. **Manifest Detection**: Drive monitor detects changes
2. **Validation**: Schema v0.5 validation with slides config
3. **Figma Generation**: Creates visual designs  
4. **Slides Generation**: Auto-generates presentation (if enabled)
5. **Export & Sync**: Saves to Drive exports folder
6. **Reporting**: Includes slides status in completion report

### Enable Auto-Generation

Set `google_slides.auto_generate: true` in your manifest to enable automatic presentation generation after Figma exports complete.

### Drive Integration

Presentations are automatically exported to your configured Drive exports folder:

```json
{
  "drive": {
    "exports_folder": "/path/to/exports",
    "auto_sync": true
  }
}
```

## 🚨 Troubleshooting

### Common Issues

**1. Authentication Errors**
```
Error: Credentials not found
```
**Solution**: Ensure `credentials.json` is in the correct location and run first-time auth.

**2. API Quotas Exceeded**
```
Error: Quota exceeded for quota metric 'Write requests'
```
**Solution**: Google Slides API has daily quotas. Wait 24 hours or request quota increase.

**3. Permission Denied**
```
Error: The caller does not have permission
```
**Solution**: Re-run OAuth flow to ensure all required permissions are granted.

**4. Template Loading Errors**
```
Error: Template not found
```
**Solution**: Verify template files exist in `core/templates/slides/` directory.

### Debug Mode

Enable verbose logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your slides generation code here
```

### Check Setup Status

```python
from integrations.google_slides.orchestrator_integration import SlidesOrchestrator

orchestrator = SlidesOrchestrator()
setup_info = orchestrator.get_setup_instructions()

print(f"Credentials found: {setup_info['credentials_exists']}")
print(f"Credentials path: {setup_info['credentials_path']}")
```

## 📚 API Reference

### Main Functions

- `generate_presentation_from_manifest(manifest_data, credentials_path=None)`
- `GoogleSlidesClient(credentials_path, token_path)`
- `PresentationBuilder(slides_client, template_path)`
- `FlowDiagramGenerator(slides_client)`

### Configuration Schema

See `core/schemas/manifest_v0_5.json` for complete `google_slides` configuration options.

## 🎉 Ready to Use!

Once setup is complete, the Google Slides integration will:

1. ✅ Automatically generate presentations from your manifests
2. ✅ Create persona-agnostic flows for requirements gathering
3. ✅ Generate edge case detail slides for technical teams
4. ✅ Show persona comparisons for stakeholder buy-in
5. ✅ Export to multiple formats and sync to Drive
6. ✅ Integrate seamlessly with your existing Figma pipeline

**Next**: Run your first end-to-end test with the Wolverine sample manifest!