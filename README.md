# Enhanced Narrative Orchestrator v2.0

**Salesforce Lightning Design System (SLDS) Integrated Figma Pipeline**

An enhanced version of the Narrative Orchestrator system with full SLDS v2.0 compliance, automated Drive monitoring, design system integration, and comprehensive accessibility validation.

## 🚀 Key Features

### ✨ Enhanced v2.0 Features
- **🎨 SLDS v2.0 Integration**: Full Lightning Design System compliance with design token validation
- **🔄 Auto Drive Monitoring**: Watches Google Drive for manifest changes and triggers pipeline automatically  
- **📚 Design System Support**: Component library integration with brand kit compatibility
- **♿ Accessibility First**: WCAG AA/AAA compliance validation with automated contrast checking
- **📱 Responsive Design**: Multi-breakpoint support (mobile, tablet, desktop)
- **🔧 Enhanced Validation**: Comprehensive manifest validation with detailed error reporting
- **⚡ Developer Handoff**: Auto-generated component specs and design tokens for seamless development

### 🔄 Workflow Improvements
- **Seamless Gem Integration**: Direct manifest sync from Narrative Orchestrator Gem
- **Real-time Monitoring**: Automatic pipeline execution when manifests are updated
- **Enhanced Reporting**: Detailed compliance reports with auto-fix suggestions
- **Multi-channel Support**: Web, SMS, Email, and Voice channel support

## 📁 Project Structure

```
sf-ux-orchestrator-v2/
├── .cursor/
│   ├── mcp.json                    # Figma MCP server configuration
│   └── rules/
│       └── orchestrator.mdc        # Enhanced orchestrator rules v0.5
├── core/
│   ├── schemas/
│   │   ├── manifest_v0_5.json      # Enhanced manifest schema
│   │   └── slds_tokens.json        # SLDS v2.0 design tokens
│   ├── templates/                  # Project templates
│   └── monitors/
│       ├── watch_drive.py          # Drive file monitoring system
│       └── pipeline_triggers.jsonl # Auto-trigger logs
├── integrations/
│   ├── slds/
│   │   ├── validator.py            # SLDS compliance validator  
│   │   └── fix_issues.py           # Auto-fix suggestions
│   ├── drive/                      # Google Drive integration
│   └── figma/                      # Figma API extensions
├── samples/
│   ├── wolverine/                  # Wolverine Worldwide example
│   │   └── manifest.json          # Complex multi-flow example
│   └── acme-corp/                  # Acme Corp example  
│       └── manifest.json          # Simple single-flow example
├── exports/                        # Generated assets and reports
│   ├── frames/                     # PNG exports with metadata
│   ├── components/                 # Component specifications  
│   ├── tokens/                     # Design tokens (CSS)
│   └── reports/                    # Compliance and accessibility reports
└── docs/                           # Comprehensive documentation
    ├── SETUP_GUIDE.md             # Complete setup instructions
    ├── MIGRATION_GUIDE.md         # Migration from v0.4 to v0.5
    ├── API_REFERENCE.md           # API documentation
    └── EXAMPLES.md                # Usage examples and tutorials
```

## 🎯 Quick Start

### 1. Prerequisites
- Figma Desktop App with Dev Mode enabled
- Google Drive access for manifest sync
- Cursor IDE with MCP support
- Python 3.10+ (for validation tools)

### 2. Installation
```bash
# Clone the enhanced orchestrator
git clone https://github.com/your-org/sf-ux-orchestrator-v2.git
cd sf-ux-orchestrator-v2

# Install Python dependencies
pip install -r requirements.txt

# Initialize the project
python -m core.setup --init
```

### 3. Configuration
```bash
# Start Figma MCP server (in Figma Desktop)
# Enable Dev Mode in Figma
# Verify MCP connection
curl http://127.0.0.1:3845/mcp
```

### 4. Run Your First Pipeline
```bash
# Option 1: Auto-monitoring mode
python core/monitors/watch_drive.py "/path/to/google-drive/project"

# Option 2: Manual execution
cursor-agent --project . --message "Run enhanced pipeline for samples/wolverine/manifest.json"
```

## 📋 Schema v0.5 Highlights

### Enhanced Manifest Structure
- **Schema Version**: Now requires `"schema_version": "0.5"`
- **Brand Context**: Rich brand metadata with guidelines URLs
- **Design System**: Full SLDS integration with token mapping
- **Accessibility**: WCAG compliance levels and verification flags
- **Responsive**: Multi-breakpoint configuration
- **Enhanced Channels**: Voice channel support added
- **Component Mapping**: UI component and SLDS pattern specifications

### Example Enhanced Manifest
```json
{
  "schema_version": "0.5",
  "design_system": {
    "framework": "slds_v2",
    "theme": "light",
    "brand_tokens": {
      "primary_color": "#1589EE",
      "secondary_color": "slds_text_weak"
    },
    "accessibility": {
      "wcag_level": "AA",
      "color_contrast_verified": true
    }
  },
  "flows": [{
    "steps": [{
      "channels": {
        "web": {
          "ui_components": ["button", "card", "input"],
          "slds_patterns": ["form-element", "button-group"]
        }
      }
    }]
  }]
}
```

## 🔧 Advanced Features

### SLDS Validation
```bash
# Validate manifest against SLDS standards  
python integrations/slds/validator.py samples/wolverine/manifest.json

# Generate compliance report
python integrations/slds/validator.py samples/wolverine/manifest.json --output reports/compliance.json
```

### Drive Monitoring
```bash
# Start monitoring with custom polling interval
python core/monitors/watch_drive.py "/path/to/drive" --interval 15 --verbose

# Check trigger logs
tail -f core/monitors/pipeline_triggers.jsonl
```

### Enhanced Exports
- **Frames**: High-resolution PNGs with metadata JSON
- **Components**: SLDS component specifications for developers
- **Tokens**: CSS custom properties for design tokens
- **Reports**: Accessibility and compliance audit results

## 📚 Documentation

| Document | Description |
|---|---|
| [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) | Complete setup and installation instructions |
| [MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md) | Migrating from v0.4 to v0.5 |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | API documentation and tool reference |
| [EXAMPLES.md](docs/EXAMPLES.md) | Usage examples and tutorials |

## 🎨 SLDS Integration Features

### Design Token Validation
- Automatic SLDS token validation
- Brand token mapping to SLDS equivalents
- Color contrast verification (WCAG AA/AAA)
- Typography scale compliance

### Component Library Integration  
- Figma design system library linking
- SLDS component pattern mapping
- Auto-generated component specifications
- Responsive design pattern application

### Accessibility Validation
- Color contrast ratio checking
- Touch target size validation  
- Focus indicator verification
- Screen reader optimization flags

## 🔄 Migration from v0.4

### Schema Changes
- Add `"schema_version": "0.5"`
- Add `design_system` configuration
- Enhance `channels` with `ui_components` and `slds_patterns`
- Add accessibility metadata

### Rule Updates
- Update `.cursor/rules/orchestrator.mdc` to v0.5
- Enable SLDS validation in pipeline
- Configure responsive breakpoints

### Drive Integration
- Set up `auto_sync: true` in manifest
- Configure Drive monitoring script
- Update export folder structure

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋 Support

- **Documentation**: Check the `/docs` folder for detailed guides
- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join our GitHub Discussions for Q&A and community support

## 🎉 Acknowledgments

- Salesforce UX Team for Lightning Design System
- Figma Team for the robust Plugin API
- Cursor Team for MCP integration
- Narrative Orchestrator Gem contributors

---

**Enhanced Narrative Orchestrator v2.0** - Bringing SLDS compliance and automated workflows to your Salesforce conversation design process.