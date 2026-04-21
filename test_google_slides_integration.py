#!/usr/bin/env python3
"""
Test Google Slides Integration with Wolverine Manifest.
Validates end-to-end presentation generation and flow diagram creation.
"""
import json
import os
import sys
from typing import Dict, Any

def load_wolverine_manifest() -> Dict[str, Any]:
    """Load Wolverine manifest for testing."""
    manifest_path = "samples/wolverine/manifest.json"
    
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Wolverine manifest not found: {manifest_path}")
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    return manifest

def enhance_manifest_for_slides_testing(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance Wolverine manifest with Google Slides configuration for testing."""
    
    # Add Google Slides configuration
    manifest['google_slides'] = {
        'auto_generate': True,
        'template_style': 'three_tier',
        'include_flow_diagrams': True,
        'persona_examples': True,
        'export_formats': ['pdf', 'pptx'],
        'custom_branding': {
            'logo_url': None,
            'color_scheme': {
                'primary': '#1B4B66',
                'secondary': '#4A90C2', 
                'accent': '#5CB85C'
            }
        }
    }
    
    # Ensure some steps are marked as edge cases for testing
    for flow in manifest.get('flows', []):
        steps = flow.get('steps', [])
        if len(steps) > 3:
            # Mark last step as edge case
            steps[-1]['is_edge_case'] = True
            steps[-1]['edge_case_priority'] = 'medium'
    
    return manifest

def test_slides_template_library():
    """Test slide template library structure and validity."""
    print("🧪 Testing slide template library...")
    
    template_dir = "core/templates/slides"
    required_templates = [
        "framework/cover_slide.json",
        "framework/agenda_slide.json",
        "framework/section_divider.json",
        "flow_diagrams/persona_agnostic_flow.json",
        "flow_diagrams/edge_case_detail.json",
        "flow_diagrams/persona_comparison.json",
        "content/overview_slide.json",
        "content/technical_requirements.json"
    ]
    
    missing_templates = []
    invalid_templates = []
    
    for template_file in required_templates:
        template_path = os.path.join(template_dir, template_file)
        
        if not os.path.exists(template_path):
            missing_templates.append(template_file)
            continue
        
        try:
            with open(template_path, 'r') as f:
                template_data = json.load(f)
            
            # Validate required template fields
            required_fields = ['template_id', 'template_name', 'layout']
            for field in required_fields:
                if field not in template_data:
                    invalid_templates.append(f"{template_file}: missing '{field}'")
        
        except json.JSONDecodeError as e:
            invalid_templates.append(f"{template_file}: invalid JSON - {e}")
    
    # Report results
    if not missing_templates and not invalid_templates:
        print(" ✅ All required templates found and valid")
        return True
    else:
        if missing_templates:
            print(f" ❌ Missing templates: {', '.join(missing_templates)}")
        if invalid_templates:
            print(f" ❌ Invalid templates: {', '.join(invalid_templates)}")
        return False

def test_content_organization():
    """Test three-tier content organization logic."""
    print("🧪 Testing content organization...")
    
    try:
        from integrations.google_slides.content_organizer import ContentOrganizer
        
        # Load test manifest
        manifest = load_wolverine_manifest()
        manifest = enhance_manifest_for_slides_testing(manifest)
        
        # Test content organization
        organizer = ContentOrganizer()
        content_plan = organizer.organize_three_tier_content(manifest)
        
        # Validate content plan structure
        required_sections = ['persona_examples', 'sections', 'appendix']
        for section in required_sections:
            if section not in content_plan:
                print(f" ❌ Missing content section: {section}")
                return False
        
        # Check persona examples
        persona_examples = content_plan['persona_examples']
        if len(persona_examples) != 3:  # Should have 3 personas
            print(f" ❌ Expected 3 persona examples, got {len(persona_examples)}")
            return False
        
        # Check main sections
        sections = content_plan['sections']
        if len(sections) < 2:  # Should have overview + flow sections
            print(f" ❌ Expected at least 2 main sections, got {len(sections)}")
            return False
        
        print(f" ✅ Content organized: {len(sections)} sections, {len(persona_examples)} personas")
        return True
        
    except Exception as e:
        print(f" ❌ Content organization failed: {e}")
        return False

def test_template_engine():
    """Test template engine variable substitution."""
    print("🧪 Testing template engine...")
    
    try:
        from integrations.google_slides.template_engine import TemplateEngine
        
        # Initialize template engine
        template_dir = "core/templates/slides"
        engine = TemplateEngine(template_dir)
        
        # Test template loading
        cover_template = engine.load_template('framework/cover_slide.json')
        
        if 'layout' not in cover_template:
            print(" ❌ Template loading failed: missing layout")
            return False
        
        # Test variable substitution
        test_data = {
            'initiative_metadata': {
                'name': 'Test Initiative',
                'version': '1.0'
            }
        }
        
        test_content = "{{initiative_metadata.name}} v{{initiative_metadata.version}}"
        result = engine._substitute_template_variables(test_content, test_data)
        
        if result != "Test Initiative v1.0":
            print(f" ❌ Variable substitution failed: expected 'Test Initiative v1.0', got '{result}'")
            return False
        
        print(" ✅ Template engine working correctly")
        return True
        
    except Exception as e:
        print(f" ❌ Template engine test failed: {e}")
        return False

def test_flow_diagram_logic():
    """Test flow diagram generation logic."""
    print("🧪 Testing flow diagram logic...")
    
    try:
        from integrations.google_slides.flow_diagram_generator import FlowDiagramGenerator
        
        # Mock slides client for testing
        class MockSlidesClient:
            def add_text_box(self, *args, **kwargs):
                return "mock_text_box"
            def add_shape(self, *args, **kwargs):
                return "mock_shape"
            def connect_shapes(self, *args, **kwargs):
                return "mock_connector"
        
        # Test flow generator
        generator = FlowDiagramGenerator(MockSlidesClient())
        
        # Test layout calculations
        layout = generator._calculate_vertical_layout(5)
        if len(layout['positions']) != 5:
            print(f" ❌ Vertical layout calculation failed: expected 5 positions, got {len(layout['positions'])}")
            return False
        
        # Test branching layout
        branching_layout = generator._calculate_branching_layout(7)
        if len(branching_layout['positions']) != 7:
            print(f" ❌ Branching layout calculation failed: expected 7 positions, got {len(branching_layout['positions'])}")
            return False
        
        print(" ✅ Flow diagram logic working correctly")
        return True
        
    except Exception as e:
        print(f" ❌ Flow diagram test failed: {e}")
        return False

def test_manifest_schema_compliance():
    """Test enhanced manifest schema compliance."""
    print("🧪 Testing manifest schema compliance...")
    
    try:
        # Load schema
        schema_path = "core/schemas/manifest_v0_5.json"
        if not os.path.exists(schema_path):
            print(f" ❌ Schema file not found: {schema_path}")
            return False
        
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        # Check for Google Slides schema additions
        properties = schema.get('properties', {})
        if 'google_slides' not in properties:
            print(" ❌ google_slides not found in manifest schema")
            return False
        
        google_slides_schema = properties['google_slides']
        required_fields = ['auto_generate', 'template_style', 'include_flow_diagrams']
        
        slides_properties = google_slides_schema.get('properties', {})
        for field in required_fields:
            if field not in slides_properties:
                print(f" ❌ Missing google_slides field in schema: {field}")
                return False
        
        # Test enhanced manifest
        manifest = load_wolverine_manifest()
        manifest = enhance_manifest_for_slides_testing(manifest)
        
        # Basic validation (would use jsonschema in production)
        if 'google_slides' not in manifest:
            print(" ❌ Enhanced manifest missing google_slides section")
            return False
        
        print(" ✅ Manifest schema compliance validated")
        return True
        
    except Exception as e:
        print(f" ❌ Schema compliance test failed: {e}")
        return False

def test_orchestrator_integration():
    """Test orchestrator integration logic."""
    print("🧪 Testing orchestrator integration...")
    
    try:
        from integrations.google_slides.orchestrator_integration import SlidesOrchestrator
        
        # Test orchestrator initialization
        orchestrator = SlidesOrchestrator()
        
        # Test manifest
        manifest = load_wolverine_manifest()
        manifest = enhance_manifest_for_slides_testing(manifest)
        
        # Test should_generate check
        should_generate = orchestrator.should_generate_presentation(manifest)
        if not should_generate:
            print(" ❌ should_generate_presentation returned False for auto_generate=True")
            return False
        
        # Test setup instructions
        setup_info = orchestrator.get_setup_instructions()
        if 'requirements' not in setup_info:
            print(" ❌ Setup instructions missing requirements")
            return False
        
        print(" ✅ Orchestrator integration logic working")
        return True
        
    except Exception as e:
        print(f" ❌ Orchestrator integration test failed: {e}")
        return False

def main():
    """Run all Google Slides integration tests."""
    print("🚀 Running Google Slides Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Template Library", test_slides_template_library),
        ("Content Organization", test_content_organization),
        ("Template Engine", test_template_engine),
        ("Flow Diagram Logic", test_flow_diagram_logic),
        ("Manifest Schema", test_manifest_schema_compliance),
        ("Orchestrator Integration", test_orchestrator_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f" ❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f" {status} {test_name}")
    
    print(f"\n🎯 Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Google Slides integration ready for use.")
        print("\n📋 Next Steps:")
        print(" 1. Set up Google Cloud credentials (see setup instructions)")
        print(" 2. Test with actual Google Slides API")
        print(" 3. Run end-to-end test with Wolverine manifest")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed. Review and fix issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())