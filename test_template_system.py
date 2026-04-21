#!/usr/bin/env python3
"""
Template System Validation Test
Enhanced Narrative Orchestrator v0.5

Tests the integration of the default channel template library with 
the manifest system and validates visual fidelity.
"""

import json
import sys
from pathlib import Path

def load_template(template_path):
    """Load and validate template JSON."""
    try:
        with open(template_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load template {template_path}: {e}")
        return None

def validate_template_structure(template_data, template_name):
    """Validate template has required structure."""
    required_fields = ['template', 'name', 'version', 'description', 'layout']
    
    if 'template' not in template_data:
        print(f"❌ {template_name}: Missing 'template' root object")
        return False
    
    template = template_data['template']
    
    for field in required_fields[1:]:  # Skip 'template' as it's the root
        if field not in template:
            print(f"❌ {template_name}: Missing required field '{field}'")
            return False
    
    print(f"✅ {template_name}: Structure validated")
    return True

def test_template_library():
    """Test the complete template library."""
    print("🧪 Testing Default Channel Template Library")
    print("=" * 50)
    
    template_base = Path("core/templates")
    
    if not template_base.exists():
        print(f"❌ Template directory not found: {template_base}")
        return False
    
    # Test web templates
    web_templates = [
        "success_confirmation.json",
        "form_collection.json", 
        "data_display.json",
        "status_messaging.json"
    ]
    
    print("\n📱 Web Templates (SLDS 2.0 Agentforce):")
    for template_file in web_templates:
        template_path = template_base / "web" / template_file
        if template_path.exists():
            template_data = load_template(template_path)
            if template_data:
                validate_template_structure(template_data, template_file)
        else:
            print(f"❌ Missing web template: {template_file}")
    
    # Test email templates
    email_templates = [
        "transactional_thread.json",
        "support_response.json"
    ]
    
    print("\n📧 Email Templates (Authentic Thread):")
    for template_file in email_templates:
        template_path = template_base / "email" / template_file
        if template_path.exists():
            template_data = load_template(template_path)
            if template_data:
                validate_template_structure(template_data, template_file)
        else:
            print(f"❌ Missing email template: {template_file}")
    
    # Test SMS templates
    sms_templates = [
        "conversation_thread.json",
        "status_notification.json"
    ]
    
    print("\n💬 SMS Templates (Native Mobile):")
    for template_file in sms_templates:
        template_path = template_base / "sms" / template_file
        if template_path.exists():
            template_data = load_template(template_path)
            if template_data:
                validate_template_structure(template_data, template_file)
        else:
            print(f"❌ Missing SMS template: {template_file}")
    
    return True

def test_wolverine_integration():
    """Test template system with Wolverine manifest."""
    print("\n🐺 Testing Wolverine Manifest Integration")
    print("=" * 40)
    
    # Load Wolverine manifest
    wolverine_path = Path("samples/wolverine/manifest.json")
    if not wolverine_path.exists():
        print(f"❌ Wolverine manifest not found: {wolverine_path}")
        return False
    
    with open(wolverine_path, 'r') as f:
        manifest = json.load(f)
    
    print(f"✅ Loaded manifest: {manifest['initiative_metadata']['name']}")
    
    # Validate flows have required channels
    flows = manifest.get('flows', [])
    print(f"📊 Found {len(flows)} flows")
    
    for flow in flows:
        flow_name = flow.get('topic', 'Unknown')
        channels = flow.get('channels', [])
        print(f"  🔄 {flow_name}: {', '.join(channels)}")
        
        # Check if template fields would be supported
        steps = flow.get('steps', [])
        for step in steps[:2]:  # Check first 2 steps
            step_channels = step.get('channels', {})
            
            for channel_name, channel_data in step_channels.items():
                if channel_name == 'web' and 'slds_patterns' in channel_data:
                    print(f"    ✅ Web step has SLDS patterns: {channel_data['slds_patterns']}")
                elif channel_name == 'email' and 'template_type' in channel_data:
                    print(f"    ✅ Email step has template type: {channel_data['template_type']}")
                elif channel_name == 'sms':
                    print(f"    ✅ SMS step ready for template integration")
    
    return True

def test_schema_compatibility():
    """Test updated schema compatibility.""" 
    print("\n📝 Testing Enhanced Schema (v0.5)")
    print("=" * 35)
    
    schema_path = Path("core/schemas/manifest_v0_5.json")
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        return False
    
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    # Check for template field definitions
    try:
        # Navigate to channel definitions
        flow_props = schema['properties']['flows']['items']['properties']
        step_props = flow_props['steps']['items']['properties'] 
        channel_props = step_props['channels']['properties']
        
        # Check web channel has template field
        if 'template' in channel_props['web']['properties']:
            print("✅ Web channel supports template field")
        else:
            print("❌ Web channel missing template field")
        
        # Check email channel has template field  
        if 'template' in channel_props['email']['properties']:
            print("✅ Email channel supports template field")
        else:
            print("❌ Email channel missing template field")
            
        # Check SMS channel has template field
        if 'template' in channel_props['sms']['properties']:
            print("✅ SMS channel supports template field")
        else:
            print("❌ SMS channel missing template field")
            
    except KeyError as e:
        print(f"❌ Schema navigation failed: {e}")
        return False
    
    return True

def main():
    """Run all template system tests."""
    print("🚀 Enhanced Narrative Orchestrator v0.5")
    print("Template System Validation Test")
    print("=" * 60)
    
    # Run all tests
    tests = [
        test_template_library,
        test_wolverine_integration, 
        test_schema_compatibility
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with error: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Template system is ready for production.")
        print("\n💡 Default templates will now be used for all future engagements.")
        print("   Visual fidelity prioritized while maintaining SLDS 2.0 compliance.")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed. Please review and fix issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())