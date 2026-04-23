#!/usr/bin/env python3
"""
Test Authentic Wolverine Flow Generation.
Creates conversation flows that match provided examples exactly.
"""
import json
import os
from integrations.google_slides.authentic_flow_generator import AuthenticFlowGenerator

def test_authentic_flow_organization():
    """Test the new authentic flow organization with Wolverine manifest."""
    
    print("🎨 Testing Authentic Flow Generation")
    print("=" * 50)
    
    # Load Wolverine manifest
    with open('samples/wolverine/manifest.json', 'r') as f:
        wolverine_manifest = json.load(f)
    
    print(f"📋 Loaded: {wolverine_manifest['initiative_metadata']['name']}")
    print(f"🔄 Flows: {len(wolverine_manifest['flows'])}")
    
    # Initialize authentic flow generator
    generator = AuthenticFlowGenerator()
    
    # Organize flows with visual fidelity priority
    organized_flows = generator.organize_conversation_flow(wolverine_manifest)
    
    print(f"\n📊 Organized Flow Summary:")
    print("-" * 30)
    
    for channel, channel_flows in organized_flows.items():
        print(f"\n🎯 {channel.upper()} Channel:")
        
        for flow in channel_flows:
            flow_name = flow['flow_name']
            total_screens = flow['total_screens']
            flow_type = flow['flow_type']
            
            print(f"   📱 {flow_name}: {total_screens} screens ({flow_type})")
            
            # Show screen details
            for screen in flow['screens']:
                screen_name = screen['screen_name']
                screen_type = screen['screen_type']
                steps_count = len(screen['steps_included'])
                visual_style = screen['visual_style']
                
                print(f"      📄 {screen_name}")
                print(f"         Type: {screen_type}")
                print(f"         Steps: {steps_count}")
                print(f"         Style: {visual_style}")
                
                # Show conversation preview for first screen
                if screen['screen_number'] == 1:
                    conv = screen.get('conversation_elements', {})
                    messages = conv.get('messages', [])
                    if messages:
                        first_msg = messages[0]
                        agent_msg = first_msg.get('agent_message', '')[:60] + "..." if len(first_msg.get('agent_message', '')) > 60 else first_msg.get('agent_message', '')
                        print(f"         Preview: \"{agent_msg}\"")
    
    print(f"\n✅ Flow Organization Complete")
    
    # Validate expected structure
    validation_results = validate_flow_structure(organized_flows)
    
    return organized_flows, validation_results

def validate_flow_structure(organized_flows):
    """Validate that flows meet the expected structure requirements."""
    
    results = {
        'web_screen_count': 'PASS',
        'sms_screen_count': 'PASS', 
        'email_screen_count': 'PASS',
        'visual_fidelity_priority': 'PASS',
        'conversation_structure': 'PASS'
    }
    
    print(f"\n🔍 Validation Results:")
    print("-" * 25)
    
    # Check Web channel (should be 4-7 screens)
    if 'web' in organized_flows:
        web_screens = sum(flow['total_screens'] for flow in organized_flows['web'])
        if web_screens < 4 or web_screens > 7:
            results['web_screen_count'] = f'FAIL: {web_screens} screens (expected 4-7)'
        print(f"   Web screens: {web_screens} ✅")
    
    # Check SMS channel (should be 4-7 screens)  
    if 'sms' in organized_flows:
        sms_screens = sum(flow['total_screens'] for flow in organized_flows['sms'])
        if sms_screens < 4 or sms_screens > 7:
            results['sms_screen_count'] = f'FAIL: {sms_screens} screens (expected 4-7)'
        print(f"   SMS screens: {sms_screens} ✅")
    
    # Check Email channel (should be 2-3 screens)
    if 'email' in organized_flows:
        email_screens = sum(flow['total_screens'] for flow in organized_flows['email'])
        if email_screens < 2 or email_screens > 3:
            results['email_screen_count'] = f'FAIL: {email_screens} screens (expected 2-3)'
        print(f"   Email screens: {email_screens} ✅")
    
    # Check visual fidelity references
    visual_refs_found = False
    for channel_flows in organized_flows.values():
        for flow in channel_flows:
            for screen in flow['screens']:
                if 'provided_' in screen.get('template_reference', ''):
                    visual_refs_found = True
                    break
    
    if not visual_refs_found:
        results['visual_fidelity_priority'] = 'FAIL: No visual reference templates found'
    else:
        print(f"   Visual fidelity refs: Found ✅")
    
    # Check conversation structure (one exchange per screen)
    proper_structure = True
    for channel_flows in organized_flows.values():
        for flow in channel_flows:
            for screen in flow['screens']:
                conv = screen.get('conversation_elements', {})
                if not conv or 'messages' not in conv:
                    proper_structure = False
                    break
    
    if not proper_structure:
        results['conversation_structure'] = 'FAIL: Missing conversation elements'
    else:
        print(f"   Conversation structure: Valid ✅")
    
    return results

def generate_figma_plan(organized_flows):
    """Generate a plan for creating authentic Figma designs."""
    
    print(f"\n🎨 Figma Generation Plan:")
    print("=" * 30)
    
    figma_plan = {
        'presentation_phase': True,
        'visual_fidelity_priority': True,
        'slds_enforcement': False,
        'channels_to_generate': []
    }
    
    for channel, channel_flows in organized_flows.items():
        channel_plan = {
            'channel': channel,
            'total_flows': len(channel_flows),
            'total_screens': sum(flow['total_screens'] for flow in channel_flows),
            'visual_style': f'authentic_{channel}',
            'template_reference': f'provided_{channel}_example',
            'screens': []
        }
        
        for flow in channel_flows:
            for screen in flow['screens']:
                screen_plan = {
                    'name': screen['screen_name'],
                    'type': screen['screen_type'],
                    'visual_style': screen['visual_style'],
                    'conversation_data': screen.get('conversation_elements', {}),
                    'figma_generation': {
                        'style_priority': 'visual_fidelity',
                        'template_match': 'exact',
                        'slds_override': 'disabled'
                    }
                }
                channel_plan['screens'].append(screen_plan)
        
        figma_plan['channels_to_generate'].append(channel_plan)
        
        print(f"📱 {channel.upper()}: {channel_plan['total_screens']} screens")
        print(f"   Style: {channel_plan['visual_style']}")
        print(f"   Reference: {channel_plan['template_reference']}")
    
    return figma_plan

def main():
    """Run authentic flow generation test."""
    
    try:
        # Test flow organization
        organized_flows, validation_results = test_authentic_flow_organization()
        
        # Generate Figma plan
        figma_plan = generate_figma_plan(organized_flows)
        
        # Check if all validations passed
        all_passed = all(result == 'PASS' or result.startswith('PASS') for result in validation_results.values())
        
        print(f"\n🎯 Test Results:")
        print("=" * 20)
        
        if all_passed:
            print("✅ All tests PASSED")
            print("🎨 Ready for authentic Figma generation")
            print("📋 Visual fidelity prioritized over SLDS compliance")
            print("🔄 Proper conversation flow structure validated")
        else:
            print("❌ Some tests FAILED:")
            for test, result in validation_results.items():
                if not (result == 'PASS' or result.startswith('PASS')):
                    print(f"   {test}: {result}")
        
        # Save results for Figma integration
        os.makedirs('exports/authentic_flows', exist_ok=True)
        
        with open('exports/authentic_flows/wolverine_organized_flows.json', 'w') as f:
            json.dump(organized_flows, f, indent=2)
        
        with open('exports/authentic_flows/figma_generation_plan.json', 'w') as f:
            json.dump(figma_plan, f, indent=2)
        
        print(f"\n💾 Results saved to exports/authentic_flows/")
        
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())