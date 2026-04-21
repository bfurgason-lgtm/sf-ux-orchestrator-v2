"""
Content Organizer for Google Slides.
Implements the three-tier content organization strategy based on the PDF template.
"""
from typing import Dict, List, Any

class ContentOrganizer:
    """Organizes manifest data into the three-tier presentation structure."""
    
    def organize_three_tier_content(self, manifest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Organize manifest data using the three-tier strategy.
        
        Args:
            manifest_data: Enhanced manifest v0.5 data
            
        Returns:
            Organized content plan with persona examples, sections, and appendix
        """
        flows = manifest_data.get('flows', [])
        
        # Extract different types of content
        persona_examples = self._extract_persona_examples(flows)
        main_sections = self._organize_main_sections(flows, manifest_data)
        appendix_items = self._extract_appendix_items(flows, manifest_data)
        
        return {
            'persona_examples': persona_examples,
            'sections': main_sections,
            'appendix': appendix_items,
            'organization_strategy': 'three_tier'
        }
    
    def _extract_persona_examples(self, flows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract persona examples for early stakeholder buy-in slides.
        
        These slides demonstrate how the same flow adapts to different brand personalities.
        """
        persona_examples = []
        
        # Take the first flow and create persona variations
        if flows:
            base_flow = flows[0]
            
            # Create three persona variations
            personas = [
                {
                    'persona_name': 'Professional',
                    'tone': 'Formal, precise, business-focused',
                    'color_scheme': '#2C3E50',
                    'example_messaging': self._adapt_flow_for_persona(base_flow, 'professional')
                },
                {
                    'persona_name': 'Friendly', 
                    'tone': 'Warm, conversational, approachable',
                    'color_scheme': '#27AE60',
                    'example_messaging': self._adapt_flow_for_persona(base_flow, 'friendly')
                },
                {
                    'persona_name': 'Technical',
                    'tone': 'Detailed, systematic, solution-oriented',
                    'color_scheme': '#8E44AD',
                    'example_messaging': self._adapt_flow_for_persona(base_flow, 'technical')
                }
            ]
            
            for persona in personas:
                persona_examples.append({
                    **persona,
                    'base_flow': base_flow,
                    'purpose': 'stakeholder_buy_in'
                })
        
        return persona_examples
    
    def _adapt_flow_for_persona(self, flow: Dict[str, Any], persona_type: str) -> Dict[str, Any]:
        """Adapt flow messaging for specific persona."""
        steps = flow.get('steps', [])
        adapted_steps = []
        
        for step in steps[:3]:  # Just first 3 steps for examples
            adapted_step = step.copy()
            
            # Adapt agent messaging based on persona
            original_agent = step.get('utterances', {}).get('agent', '')
            if original_agent:
                adapted_step['utterances'] = step['utterances'].copy()
                adapted_step['utterances']['agent'] = self._adapt_message_for_persona(
                    original_agent, persona_type
                )
            
            adapted_steps.append(adapted_step)
        
        return {
            **flow,
            'steps': adapted_steps,
            'persona_type': persona_type
        }
    
    def _adapt_message_for_persona(self, message: str, persona_type: str) -> str:
        """Adapt a message for a specific persona type."""
        if persona_type == 'professional':
            # More formal, concise
            return message.replace('Hi', 'Hello').replace("I'll", 'I will').replace('!', '.')
        elif persona_type == 'friendly':
            # Warmer, more personal
            return message.replace('Hello', 'Hi there').replace('.', '!').replace('I will', "I'll")
        elif persona_type == 'technical':
            # More detailed, systematic
            return f"{message} I'll provide step-by-step guidance to ensure accuracy."
        else:
            return message
    
    def _organize_main_sections(self, flows: List[Dict[str, Any]], 
                               manifest_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Organize main presentation sections following PDF template pattern."""
        sections = []
        section_number = 1
        
        # Section 1: Overview and value proposition
        sections.append({
            'section_number': f"{section_number:02d}",
            'title': 'Initiative Overview',
            'type': 'overview',
            'slides': ['overview_slide'],
            'purpose': 'value_proposition'
        })
        section_number += 1
        
        # Section 2-N: Flow overviews (persona-agnostic)
        for flow in flows:
            sections.append({
                'section_number': f"{section_number:02d}",
                'title': f"{flow.get('topic', 'Flow')} - Overview",
                'type': 'flow_overview', 
                'flows': [flow],
                'purpose': 'requirements_gathering'
            })
            section_number += 1
        
        # Section N+1: Edge cases for all flows
        edge_case_flows = [flow for flow in flows if self._has_edge_cases(flow)]
        if edge_case_flows:
            sections.append({
                'section_number': f"{section_number:02d}",
                'title': 'Edge Cases & Exception Handling',
                'type': 'edge_cases',
                'flows': edge_case_flows,
                'purpose': 'technical_implementation'
            })
            section_number += 1
        
        # Section N+2: Channel implementations
        channels = self._extract_channels(flows)
        if channels:
            sections.append({
                'section_number': f"{section_number:02d}",
                'title': 'Multi-Channel Implementation',
                'type': 'channel_implementation',
                'channels': channels,
                'purpose': 'implementation_details'
            })
            section_number += 1
        
        return sections
    
    def _has_edge_cases(self, flow: Dict[str, Any]) -> bool:
        """Check if flow has edge case steps."""
        steps = flow.get('steps', [])
        return any(step.get('is_edge_case', False) for step in steps)
    
    def _extract_channels(self, flows: List[Dict[str, Any]]) -> List[str]:
        """Extract unique channels from all flows."""
        channels = set()
        
        for flow in flows:
            flow_channels = flow.get('channels', [])
            channels.update(flow_channels)
        
        # Return in standard order
        standard_order = ['web', 'email', 'sms', 'voice']
        ordered_channels = [ch for ch in standard_order if ch in channels]
        
        return ordered_channels
    
    def _extract_appendix_items(self, flows: List[Dict[str, Any]], 
                               manifest_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract items for appendix section."""
        appendix_items = []
        
        # Detailed technical specifications
        appendix_items.append({
            'title': 'Detailed Technical Specifications',
            'type': 'technical_details',
            'content': {
                'design_system': manifest_data.get('design_system', {}),
                'deployment': manifest_data.get('deployment', {}),
                'drive_config': manifest_data.get('drive', {})
            }
        })
        
        # Complete flow step lists
        for flow in flows:
            appendix_items.append({
                'title': f"{flow.get('topic', 'Flow')} - Complete Step List",
                'type': 'complete_flow',
                'content': {
                    'steps': flow.get('steps', []),
                    'step_count': len(flow.get('steps', [])),
                    'edge_case_count': sum(1 for step in flow.get('steps', []) 
                                         if step.get('is_edge_case', False))
                }
            })
        
        # Terminology and definitions
        terminology = manifest_data.get('terminology_map', {})
        if terminology:
            appendix_items.append({
                'title': 'Terminology and Definitions',
                'type': 'terminology',
                'content': terminology
            })
        
        return appendix_items