# Migration Guide: v0.4 → v0.5

Complete guide for migrating from the original Narrative Orchestrator v0.4 to the Enhanced v2.0 (schema v0.5) with SLDS integration and automated Drive monitoring.

## 🎯 Migration Overview

### What's New in v0.5
- **Enhanced Schema**: Rich design system integration
- **SLDS v2.0 Compliance**: Full Lightning Design System integration
- **Drive Monitoring**: Automated manifest change detection
- **Accessibility First**: WCAG AA/AAA validation built-in
- **Responsive Design**: Multi-breakpoint support
- **Component Mapping**: UI component and SLDS pattern specifications

### Breaking Changes
- Schema version must be updated to `"0.5"`
- New required `design_system` configuration block
- Enhanced `channels` structure with UI components
- Updated export folder structure
- New SLDS validation requirements

## 📋 Migration Checklist

- [ ] **Schema Updates**: Update manifest to v0.5 format
- [ ] **Design System Config**: Add SLDS configuration block
- [ ] **Channel Enhancement**: Add UI components and SLDS patterns  
- [ ] **Accessibility Metadata**: Add WCAG compliance settings
- [ ] **Export Folders**: Update export folder structure
- [ ] **Rules Update**: Upgrade Cursor rules to v0.5
- [ ] **Drive Integration**: Configure automated monitoring
- [ ] **Validation Setup**: Install SLDS validator tools

## 🔄 Step-by-Step Migration

### Step 1: Update Schema Version

**Old v0.4:**
```json
{
  "initiative_metadata": {
    "name": "My Project"
  }
}
```

**New v0.5:**
```json
{
  "schema_version": "0.5",
  "initiative_metadata": {
    "name": "My Project",
    "brand_context": {
      "primary_brand": "My Company",
      "brand_guidelines_url": null
    }
  }
}
```

### Step 2: Add Design System Configuration

**Required new block:**
```json
{
  "design_system": {
    "framework": "slds_v2",
    "theme": "light",
    "brand_tokens": {
      "primary_color": "#1589EE",
      "secondary_color": "#5C6B73",
      "font_family": "Salesforce Sans"
    },
    "accessibility": {
      "wcag_level": "AA",
      "color_contrast_verified": true,
      "screen_reader_optimized": false
    },
    "responsive_breakpoints": {
      "mobile": "390px",
      "tablet": "768px",
      "desktop": "1200px"
    }
  }
}
```

### Step 3: Enhance Channel Configurations

**Old v0.4:**
```json
{
  "channels": {
    "web": {
      "agent": "Hello! How can I help?",
      "user": "I need support"
    }
  }
}
```

**New v0.5:**
```json
{
  "channels": {
    "web": {
      "agent": "Hello! How can I help?",
      "user": "I need support",
      "ui_components": ["button", "card", "input"],
      "slds_patterns": ["welcome-mat", "button-group"]
    }
  }
}
```

### Step 4: Add Enhanced Metadata

**Flow-level enhancements:**
```json
{
  "flows": [{
    "topic": "Support",
    "flow_metadata": {
      "primary_persona": "Customer",
      "complexity_score": 2,
      "estimated_completion_time": "3m"
    }
  }]
}
```

**Step-level enhancements:**
```json
{
  "steps": [{
    "step_name": "greeting",
    "design_notes": "Warm welcome with clear CTAs",
    "accessibility_notes": "High contrast with focus indicators"
  }]
}
```

### Step 5: Update Drive Configuration

**Enhanced drive block:**
```json
{
  "drive": {
    "project_folder": "/path/to/drive/project",
    "exports_folder": "/path/to/exports", 
    "auto_sync": true
  }
}
```

### Step 6: Update Figma Configuration

**Enhanced figma block:**
```json
{
  "figma": {
    "target_file_url": "https://figma.com/design/...",
    "design_system_library": "https://figma.com/design/slds-library",
    "brand_kit_library": null
  }
}
```

## 🔧 Automated Migration Tool

### Using the Migration Script

```bash
# Run automatic migration
python tools/migrate_manifest.py path/to/old-manifest.json

# Output: path/to/old-manifest-v0.5.json
```

### Manual Migration Template

Copy this template and fill in your specific values:

```json
{
  "schema_version": "0.5",
  "initiative_metadata": {
    "name": "YOUR_PROJECT_NAME",
    "version": "1.0",
    "timestamp": "2026-04-21T10:00:00Z",
    "brand_context": {
      "primary_brand": "YOUR_BRAND",
      "sub_brands": [],
      "brand_guidelines_url": null
    },
    "handoff_metadata": {
      "last_updated_by": "YOUR_EMAIL",
      "last_updated_at": "2026-04-21T10:00:00Z",
      "status": "active",
      "handoff_notes": "Migrated to v0.5 with SLDS integration",
      "design_review_status": "pending"
    }
  },
  "data_tier": "2",
  "design_system": {
    "framework": "slds_v2",
    "theme": "light",
    "brand_tokens": {
      "primary_color": "#1589EE",
      "secondary_color": "#5C6B73",
      "accent_color": "#45C65A",
      "font_family": "Salesforce Sans"
    },
    "accessibility": {
      "wcag_level": "AA",
      "color_contrast_verified": false,
      "screen_reader_optimized": false
    }
  },
  "flows": [
    // Your existing flows with enhanced channel configs
  ],
  "drive": {
    "project_folder": "YOUR_DRIVE_PATH",
    "exports_folder": "YOUR_EXPORTS_PATH",
    "auto_sync": true
  },
  "figma": {
    "target_file_url": "YOUR_FIGMA_URL",
    "design_system_library": "https://figma.com/design/slds-library",
    "brand_kit_library": null
  }
}
```

## ⚙️ System Configuration Updates

### Update Cursor Rules

1. **Backup existing rules:**
   ```bash
   cp .cursor/rules/orchestrator.mdc .cursor/rules/orchestrator-v0.4-backup.mdc
   ```

2. **Replace with v0.5 rules:**
   ```bash
   cp enhanced-orchestrator-v2/.cursor/rules/orchestrator.mdc .cursor/rules/
   ```

### Install Python Dependencies

```bash
# Install enhanced validation tools
pip install -r enhanced-orchestrator-v2/requirements.txt

# Verify SLDS validator
python -m integrations.slds.validator --help
```

### Configure Drive Monitoring

```bash
# Set up monitoring script
python enhanced-orchestrator-v2/core/monitors/watch_drive.py --help

# Test monitoring (Ctrl+C to stop)
python enhanced-orchestrator-v2/core/monitors/watch_drive.py /path/to/drive --interval 30
```

## 🧪 Testing Your Migration

### Validation Tests

```bash
# Test schema validation
python tools/validate_manifest.py your-migrated-manifest.json

# Test SLDS compliance
python integrations/slds/validator.py your-migrated-manifest.json

# Expected output: Validation passes with compliance score
```

### Pipeline Test

```bash
# Test enhanced pipeline execution
cursor-agent --project . --message "Run enhanced pipeline for your-migrated-manifest.json"

# Verify exports are generated in new structure
ls -la exports/
```

### Drive Integration Test

```bash
# Start monitoring
python core/monitors/watch_drive.py /path/to/drive --verbose

# In another terminal, modify your manifest
touch your-migrated-manifest.json

# Verify monitoring detects change and logs trigger
```

## 📊 Migration Comparison

| Feature | v0.4 | v0.5 Enhanced |
|---|---|---|
| Schema Version | Not specified | Required: "0.5" |
| SLDS Integration | None | Full v2.0 support |
| Design Tokens | Manual colors | SLDS token mapping |
| Accessibility | Basic | WCAG AA/AAA validation |
| Drive Monitoring | Manual | Automated file watching |
| Component Specs | None | Auto-generated for devs |
| Export Structure | Basic PNGs | Rich metadata + specs |
| Responsive Design | Single size | Multi-breakpoint |
| Voice Channel | Not supported | Full voice integration |

## 🚨 Common Migration Issues

### Schema Validation Errors

**Issue**: `"schema_version is required"`
```bash
# Solution: Add to top of manifest
{
  "schema_version": "0.5",
  // ... rest of manifest
}
```

**Issue**: `"design_system is required"`  
```bash
# Solution: Add minimal design system config
{
  "design_system": {
    "framework": "slds_v2",
    "theme": "light"
  }
}
```

### SLDS Validation Issues

**Issue**: Color contrast failures
```bash
# Check current colors against SLDS standards
python integrations/slds/validator.py manifest.json --verbose

# Use suggested SLDS tokens from output
```

**Issue**: Component pattern mismatches
```bash
# Review UI components in web channels
# Ensure they match SLDS component library:
# "ui_components": ["button", "input", "card"]  // ✅ Valid
# "ui_components": ["custom-widget"]            // ❌ Invalid
```

### Drive Monitoring Issues

**Issue**: Monitoring not detecting changes
```bash
# Check file permissions
ls -la /path/to/drive/manifest.json

# Test with manual file touch
touch /path/to/drive/manifest.json

# Verify monitoring logs
tail -f core/monitors/watch_drive.log
```

## 📞 Migration Support

### Self-Service Resources
1. **Validation Tool**: Use `python tools/validate_manifest.py` for automated checks
2. **Example Manifests**: Check `samples/` folder for v0.5 examples
3. **Schema Reference**: Review `core/schemas/manifest_v0_5.json`

### Community Support
- **GitHub Issues**: Tag with `migration` label
- **Discussions**: Post in Migration Help category
- **Documentation**: Check troubleshooting sections

### Professional Migration Services
For complex migrations or enterprise support, contact the development team for:
- **Custom migration scripts**
- **Bulk manifest processing**
- **Advanced SLDS customization**
- **Team training and onboarding**

## ✅ Migration Complete

After successful migration, you should have:

- [ ] **Valid v0.5 manifest** with all required fields
- [ ] **SLDS compliance** validation passing
- [ ] **Enhanced exports** with component specs and tokens
- [ ] **Drive monitoring** (if enabled) detecting changes
- [ ] **Figma pipeline** executing with new SLDS features

**🎉 Welcome to Enhanced Narrative Orchestrator v2.0!**

Your manifests are now future-ready with full SLDS integration, automated workflows, and comprehensive accessibility support.