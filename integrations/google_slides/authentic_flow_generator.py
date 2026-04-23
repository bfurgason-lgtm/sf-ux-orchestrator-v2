"""
Authentic Flow Generator for Figma.
Creates conversation flows that match provided examples exactly, prioritizing visual fidelity over SLDS compliance.
"""
from typing import Dict, List, Tuple, Any, Optional

class AuthenticFlowGenerator:
    """Generates authentic conversation flows matching user-provided examples."""
    
    def __init__(self):
        """Initialize with visual fidelity as priority."""
        self.phase = "presentation"
        self.visual_fidelity_priority = True
        
    def organize_conversation_flow(self, manifest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Organize manifest steps into conversation screens with proper flow structure.
        
        Args:
            manifest_data: Enhanced manifest v0.5 data
            
        Returns:
            Dictionary with organized screens per channel
        """
        flows = manifest_data.get('flows', [])
        organized_flows = {}
        
        for flow in flows:
            flow_name = flow.get('topic', 'Flow')
            channels = flow.get('channels', [])
            steps = flow.get('steps', [])
            
            # Filter main flow steps (exclude edge cases for main flow)
            main_steps = [step for step in steps if not step.get('is_edge_case', False)]
            edge_steps = [step for step in steps if step.get('is_edge_case', False)]
            
            for channel in channels:
                channel_flow = self._organize_channel_flow(channel, main_steps, edge_steps, flow_name)
                
                if channel not in organized_flows:
                    organized_flows[channel] = []
                organized_flows[channel].append(channel_flow)
        
        return organized_flows
    
    def _organize_channel_flow(self, channel: str, main_steps: List[Dict], 
                              edge_steps: List[Dict], flow_name: str) -> Dict[str, Any]:
        """Organize steps into screens for a specific channel."""
        
        if channel == 'web':
            return self._organize_web_flow(main_steps, edge_steps, flow_name)
        elif channel == 'sms':
            return self._organize_sms_flow(main_steps, edge_steps, flow_name)
        elif channel == 'email':
            return self._organize_email_flow(main_steps, edge_steps, flow_name)
        else:
            return self._organize_generic_flow(main_steps, edge_steps, flow_name, channel)
    
    def _organize_web_flow(self, main_steps: List[Dict], edge_steps: List[Dict], flow_name: str) -> Dict[str, Any]:
        """Organize web channel flow: 4-7 screens, one exchange per screen."""
        screens = []
        
        # Group main steps into conversation screens
        step_groups = self._group_steps_for_web(main_steps)
        
        for i, step_group in enumerate(step_groups):
            screen = {
                'screen_number': i + 1,
                'screen_name': f"{flow_name}_Web_Screen_{i+1}",
                'screen_type': 'conversation_exchange',
                'steps_included': step_group,
                'conversation_elements': self._extract_web_conversation(step_group),
                'visual_style': 'authentic_chatbot',
                'template_reference': 'provided_chatbot_example'
            }
            screens.append(screen)
        
        # Add edge case screens if they exist
        if edge_steps:
            for j, edge_step in enumerate(edge_steps):
                edge_screen = {
                    'screen_number': len(screens) + j + 1,
                    'screen_name': f"{flow_name}_Web_EdgeCase_{j+1}",
                    'screen_type': 'edge_case_handling',
                    'steps_included': [edge_step],
                    'conversation_elements': self._extract_web_conversation([edge_step]),
                    'visual_style': 'authentic_chatbot_error',
                    'template_reference': 'provided_chatbot_example'
                }
                screens.append(edge_screen)
        
        return {
            'channel': 'web',
            'flow_name': flow_name,
            'total_screens': len(screens),
            'screens': screens,
            'flow_type': 'real_time_chat'
        }
    
    def _organize_sms_flow(self, main_steps: List[Dict], edge_steps: List[Dict], flow_name: str) -> Dict[str, Any]:
        """Organize SMS channel flow: 4-7 screens, short exchanges per screen."""
        screens = []
        
        # Group steps for SMS (similar to web but more condensed)
        step_groups = self._group_steps_for_sms(main_steps)
        
        for i, step_group in enumerate(step_groups):
            screen = {
                'screen_number': i + 1,
                'screen_name': f"{flow_name}_SMS_Screen_{i+1}",
                'screen_type': 'sms_exchange',
                'steps_included': step_group,
                'conversation_elements': self._extract_sms_conversation(step_group),
                'visual_style': 'authentic_mobile_messaging',
                'template_reference': 'provided_sms_example'
            }
            screens.append(screen)
        
        # Add edge cases
        if edge_steps:
            for j, edge_step in enumerate(edge_steps):
                edge_screen = {
                    'screen_number': len(screens) + j + 1,
                    'screen_name': f"{flow_name}_SMS_EdgeCase_{j+1}",
                    'screen_type': 'sms_error_handling',
                    'steps_included': [edge_step],
                    'conversation_elements': self._extract_sms_conversation([edge_step]),
                    'visual_style': 'authentic_mobile_messaging_error',
                    'template_reference': 'provided_sms_example'
                }
                screens.append(edge_screen)
        
        return {
            'channel': 'sms',
            'flow_name': flow_name,
            'total_screens': len(screens),
            'screens': screens,
            'flow_type': 'mobile_messaging'
        }
    
    def _organize_email_flow(self, main_steps: List[Dict], edge_steps: List[Dict], flow_name: str) -> Dict[str, Any]:
        """Organize email channel flow: 2-3 screens, multiple exchanges per screen."""
        screens = []
        
        # Group steps for email (fewer screens, more content per screen)
        step_groups = self._group_steps_for_email(main_steps)
        
        for i, step_group in enumerate(step_groups):
            screen = {
                'screen_number': i + 1,
                'screen_name': f"{flow_name}_Email_Screen_{i+1}",
                'screen_type': 'email_thread',
                'steps_included': step_group,
                'conversation_elements': self._extract_email_conversation(step_group),
                'visual_style': 'authentic_email_thread',
                'template_reference': 'provided_email_example'
            }
            screens.append(screen)
        
        # Add edge cases (usually combined into last screen for email)
        if edge_steps and len(screens) > 0:
            screens[-1]['steps_included'].extend(edge_steps)
            screens[-1]['conversation_elements']['edge_cases'] = self._extract_email_conversation(edge_steps)
        
        return {
            'channel': 'email',
            'flow_name': flow_name,
            'total_screens': len(screens),
            'screens': screens,
            'flow_type': 'email_thread'
        }
    
    def _group_steps_for_web(self, steps: List[Dict]) -> List[List[Dict]]:
        """Group steps into screens for web channel (1-2 steps per screen)."""
        groups = []
        current_group = []
        
        for step in steps:
            current_group.append(step)
            
            # Create new screen after every 1-2 steps for real-time chat feel
            if len(current_group) >= 2 or step.get('step_name', '').lower() in ['resolution', 'confirmation']:
                groups.append(current_group.copy())
                current_group = []
        
        # Add remaining steps
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _group_steps_for_sms(self, steps: List[Dict]) -> List[List[Dict]]:
        """Group steps into screens for SMS channel (1-2 steps per screen)."""
        # Similar to web but optimized for mobile
        return self._group_steps_for_web(steps)
    
    def _group_steps_for_email(self, steps: List[Dict]) -> List[List[Dict]]:
        """Group steps into screens for email channel (2-4 steps per screen)."""
        groups = []
        current_group = []
        
        for step in steps:
            current_group.append(step)
            
            # Create new screen after every 3-4 steps for email threading
            if len(current_group) >= 3:
                groups.append(current_group.copy())
                current_group = []
        
        # Add remaining steps
        if current_group:
            groups.append(current_group)
        
        # Ensure we have 2-3 screens maximum
        while len(groups) > 3:
            # Merge smallest groups
            if len(groups) >= 2:
                groups[-2].extend(groups[-1])
                groups.pop()
        
        return groups
    
    def _extract_web_conversation(self, steps: List[Dict]) -> Dict[str, Any]:
        """Extract conversation elements for web chatbot interface."""
        messages = []
        
        for step in steps:
            step_messages = {
                'step_number': step.get('step_number'),
                'step_name': step.get('step_name', ''),
                'agent_message': step.get('channels', {}).get('web', {}).get('agent', ''),
                'user_message': step.get('channels', {}).get('web', {}).get('user', ''),
                'ui_components': step.get('channels', {}).get('web', {}).get('ui_components', []),
                'is_edge_case': step.get('is_edge_case', False)
            }
            messages.append(step_messages)
        
        return {
            'conversation_type': 'chatbot',
            'messages': messages,
            'ui_style': 'bubble_interface',
            'interaction_pattern': 'real_time'
        }
    
    def _extract_sms_conversation(self, steps: List[Dict]) -> Dict[str, Any]:
        """Extract conversation elements for SMS mobile interface."""
        messages = []
        
        for step in steps:
            step_messages = {
                'step_number': step.get('step_number'),
                'step_name': step.get('step_name', ''),
                'agent_message': step.get('channels', {}).get('sms', {}).get('agent', ''),
                'user_message': step.get('channels', {}).get('sms', {}).get('user', ''),
                'is_edge_case': step.get('is_edge_case', False),
                'character_count': len(step.get('channels', {}).get('sms', {}).get('agent', ''))
            }
            messages.append(step_messages)
        
        return {
            'conversation_type': 'sms',
            'messages': messages,
            'ui_style': 'mobile_native',
            'interaction_pattern': 'asynchronous'
        }
    
    def _extract_email_conversation(self, steps: List[Dict]) -> Dict[str, Any]:
        """Extract conversation elements for email thread interface."""
        messages = []
        
        for step in steps:
            email_data = step.get('channels', {}).get('email', {})
            step_messages = {
                'step_number': step.get('step_number'),
                'step_name': step.get('step_name', ''),
                'subject': email_data.get('subject', ''),
                'body': email_data.get('body', ''),
                'template_type': email_data.get('template_type', 'transactional'),
                'is_edge_case': step.get('is_edge_case', False)
            }
            messages.append(step_messages)
        
        return {
            'conversation_type': 'email_thread',
            'messages': messages,
            'ui_style': 'email_client',
            'interaction_pattern': 'threaded'
        }
    
    def _organize_generic_flow(self, main_steps: List[Dict], edge_steps: List[Dict], 
                              flow_name: str, channel: str) -> Dict[str, Any]:
        """Generic flow organization for other channels."""
        screens = []
        
        for i, step in enumerate(main_steps):
            screen = {
                'screen_number': i + 1,
                'screen_name': f"{flow_name}_{channel.upper()}_Screen_{i+1}",
                'screen_type': 'generic_exchange',
                'steps_included': [step],
                'visual_style': f'authentic_{channel}',
                'template_reference': f'provided_{channel}_example'
            }
            screens.append(screen)
        
        return {
            'channel': channel,
            'flow_name': flow_name,
            'total_screens': len(screens),
            'screens': screens,
            'flow_type': 'generic'
        }