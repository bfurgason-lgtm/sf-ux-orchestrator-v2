# Enhanced Narrative Orchestrator v2.0 - Setup Guide

Complete setup instructions for the Enhanced Narrative Orchestrator with SLDS integration, Drive monitoring, and automated Figma pipeline execution.

## 🎯 Prerequisites

### Required Software
- **Figma Desktop App** (latest version)
- **Cursor IDE** with MCP support enabled
- **Python 3.10+** for validation and monitoring tools
- **Google Drive** access for manifest synchronization

### Recommended Tools
- **Git** for version control
- **Node.js 18+** (for potential npm integrations)
- **VS Code** (as fallback IDE)

## 📋 Pre-Setup Checklist

- [ ] Figma Desktop installed and signed in
- [ ] Cursor IDE installed with latest updates
- [ ] Google Drive access confirmed
- [ ] Python 3.10+ available in PATH
- [ ] Administrative access for MCP server setup

## 🚀 Installation Steps

### Step 1: Clone and Initialize Project

```bash
# Clone the enhanced orchestrator repository  
git clone https://github.com/your-org/sf-ux-orchestrator-v2.git
cd sf-ux-orchestrator-v2

# Verify project structure
ls -la
```

**Expected output:**
```
.cursor/          # Cursor configuration
core/             # Core system files
integrations/     # SLDS and Drive integrations
samples/          # Example manifests
exports/          # Generated assets
docs/             # Documentation
```

### Step 2: Python Environment Setup

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt

# Verify installation
python --version
python -c "import json, pathlib, datetime; print('✅ Python dependencies ready')"
```

### Step 3: Figma Desktop Configuration

1. **Open Figma Desktop App**
   - Launch Figma Desktop (not browser version)
   - Sign in to your Figma account
   - Ensure you have edit access to target Figma files

2. **Enable Dev Mode**
   - In any Figma file, click the "Dev Mode" toggle (top right)
   - Accept any prompts about enabling developer features
   - Verify the Dev Mode panel appears on the right

3. **Start MCP Server**
   - In Figma Dev Mode panel, look for "MCP Server" or "Plugin API" section
   - Click "Start Server" or similar option
   - Default server should start at `http://127.0.0.1:3845/mcp`

4. **Verify MCP Connection**
   ```bash
   # Test MCP server connectivity
   curl http://127.0.0.1:3845/mcp
   
   # Expected response: JSON with server info
   ```

### Step 4: Cursor IDE Configuration

1. **Open Project in Cursor**
   ```bash
   # Open the project in Cursor
   cursor ~/Documents/GitHub/sf-ux-orchestrator-v2
   ```

2. **Verify MCP Configuration**
   - Check `.cursor/mcp.json` exists and is correctly configured:
   ```json
   {
     "mcpServers": {
       "figma": {
         "url": "http://127.0.0.1:3845/mcp",
         "description": "Figma desktop MCP server"
       }
     }
   }
   ```

3. **Test MCP Connection in Cursor**
   - Open Cursor's command palette (Cmd/Ctrl + Shift + P)
   - Search for "MCP" commands
   - Verify Figma MCP server appears as connected

### Step 5: Google Drive Integration

1. **Choose Integration Method**
   
   **Option A: Enhanced Drive Integration (Recommended)**
   ```bash
   # Set up local Drive monitoring
   python core/monitors/watch_drive.py --help
   
   # Configure your Drive project folder
   export DRIVE_PROJECT_FOLDER="/path/to/your/google-drive/project-folder"
   ```

   **Option B: Manual File Management**
   - Create a dedicated Google Drive folder for manifests
   - Download/upload manifest files manually as needed
   - Update manifest paths in your projects

2. **Test Drive Monitoring** (Enhanced Integration Only)
   ```bash
   # Start monitoring in test mode
   python core/monitors/watch_drive.py "$DRIVE_PROJECT_FOLDER" --interval 10 --verbose
   
   # In another terminal, create a test manifest
   echo '{"test": true}' > "$DRIVE_PROJECT_FOLDER/test-manifest.json"
   
   # Verify monitoring detects the change
   ```

### Step 6: SLDS Integration Setup

1. **Verify SLDS Validator**
   ```bash
   # Test SLDS validation system
   python integrations/slds/validator.py samples/wolverine/manifest.json
   
   # Expected: Validation report with compliance scores
   ```

2. **Check Design Token Reference**
   ```bash
   # Verify SLDS tokens are loaded
   python -c "
   import json
   with open('core/schemas/slds_tokens.json') as f:
       tokens = json.load(f)
   print(f'✅ Loaded {len(tokens)} SLDS token categories')
   "
   ```

3. **Test Component Validation**
   ```bash
   # Run component pattern validation
   python integrations/slds/validator.py samples/acme-corp/manifest.json --verbose
   ```

## ✅ Verification Tests

### Test 1: Basic Figma Connection
```bash
# In Cursor, test Figma MCP tools
# This should work without errors:
cursor-agent --project . --message "List available Figma tools"
```

### Test 2: Manifest Validation  
```bash
# Validate sample manifests
python integrations/slds/validator.py samples/wolverine/manifest.json
python integrations/slds/validator.py samples/acme-corp/manifest.json

# Both should pass with compliance scores
```

### Test 3: Drive Monitoring
```bash
# Start monitoring (Ctrl+C to stop)
python core/monitors/watch_drive.py samples/wolverine --interval 5

# In another terminal, modify the manifest
touch samples/wolverine/manifest.json

# Verify monitoring detects the change
```

### Test 4: End-to-End Pipeline
```bash
# Run complete pipeline on sample
cursor-agent --project . --message "Run enhanced pipeline for samples/acme-corp/manifest.json"

# Should execute without critical errors
```

## 🔧 Configuration Customization

### Custom SLDS Tokens
Edit `core/schemas/slds_tokens.json` to add custom design tokens:
```json
{
  "colors": {
    "brand": {
      "custom_primary": "#YOUR_COLOR_HERE"
    }
  }
}
```

### Drive Polling Interval
Adjust monitoring frequency in `core/monitors/watch_drive.py`:
```python
# Default: 30 seconds, adjust as needed
polling_interval = 30  # seconds
```

### Export Folder Structure
Customize export paths in manifest files:
```json
{
  "drive": {
    "exports_folder": "/path/to/your/custom/exports"
  }
}
```

## 🚨 Troubleshooting

### Common Issues

**Issue**: MCP server connection fails
```bash
# Check if Figma Desktop is running
ps aux | grep -i figma

# Verify Dev Mode is enabled
curl http://127.0.0.1:3845/mcp
```

**Issue**: SLDS validation errors
```bash
# Check Python dependencies
pip list | grep -E "(jsonschema|pathlib2|requests)"

# Verify SLDS token files
python -c "import core.schemas.slds_tokens as t; print('✅ SLDS tokens loaded')"
```

**Issue**: Drive monitoring not triggering
```bash
# Check file permissions
ls -la /path/to/drive/folder/

# Test with manual trigger
python core/monitors/watch_drive.py --help
```

**Issue**: Exports not generating
```bash
# Check exports directory permissions
mkdir -p exports/test && touch exports/test/test.txt && rm exports/test/test.txt

# Verify Figma connection for screenshots
cursor-agent --message "Test Figma screenshot capture"
```

### Debug Mode

Enable verbose logging for troubleshooting:
```bash
# Set debug environment
export DEBUG=1
export VERBOSE=1

# Run with enhanced logging
python core/monitors/watch_drive.py /path/to/drive --verbose
```

### Log Files

Check log files for detailed error information:
```bash
# Monitor logs
tail -f core/monitors/watch_drive.log

# Pipeline trigger logs  
tail -f core/monitors/pipeline_triggers.jsonl

# SLDS validation logs
tail -f integrations/slds/validation.log
```

## 📞 Support

### Self-Help Resources
1. Check the [README.md](../README.md) for overview
2. Review [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) if upgrading
3. Browse [EXAMPLES.md](EXAMPLES.md) for usage patterns

### Community Support
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Q&A and community help
- **Documentation Wiki**: Detailed technical guides

### Professional Support
For enterprise support and custom integrations, contact the development team.

---

## 🎉 Next Steps

Once setup is complete:

1. **Create Your First Manifest**: Copy `samples/acme-corp/manifest.json` and customize
2. **Run the Pipeline**: Execute your first enhanced Figma build
3. **Review Exports**: Check generated assets in the `exports/` folder
4. **Enable Drive Monitoring**: Set up automatic pipeline execution
5. **Customize SLDS Integration**: Adapt design tokens to your brand

**🚀 You're ready to use the Enhanced Narrative Orchestrator v2.0!**