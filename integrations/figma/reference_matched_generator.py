"""
Reference-Matched Figma Generator.
Creates Figma designs that precisely match the provided reference screenshot.
"""
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ReferenceMatchedGenerator:
    """Generates Figma screens that exactly match the provided reference screenshot."""
    
    def __init__(self):
        """Initialize with reference-matched specifications."""
        self.template_specs = self._load_reference_specs()
        self.generation_log = []
        
    def _load_reference_specs(self) -> Dict[str, Any]:
        """Load the updated template specifications matching the reference."""
        try:
            with open('core/templates/web_template_spec.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load reference specs: {e}")
            return {}
    
    def generate_reference_matched_script(self, conversation_data: List[Dict[str, Any]]) -> str:
        """Generate Figma script that matches the reference screenshot exactly."""
        
        specs = self.template_specs
        mobile_specs = specs.get('mobile_frame_specifications', {})
        avatar_specs = specs.get('agent_avatar_specifications', {})
        visual_specs = specs.get('visual_specifications', {})
        layout_specs = specs.get('layout_specifications', {})
        
        script = f"""
        // Reference-Matched Web Channel Generation
        // Based on user-provided screenshot for exact visual fidelity
        
        const wolverinePage = figma.root.children.find(p => p.id === '36:114');
        await figma.setCurrentPageAsync(wolverinePage);
        wolverinePage.children.forEach(child => child.remove());
        
        // Load fonts
        await figma.loadFontAsync({{ family: 'Inter', style: 'Regular' }});
        await figma.loadFontAsync({{ family: 'Inter', style: 'Medium' }});
        
        // Create page title matching reference
        const pageTitle = figma.createText();
        pageTitle.name = 'Page Title';
        pageTitle.characters = 'Returns';
        pageTitle.fontName = {{ family: 'Inter', style: 'Medium' }};
        pageTitle.fontSize = 18;
        pageTitle.fills = [{{ type: 'SOLID', color: {{ r: 0.1, g: 0.1, b: 0.1 }} }}];
        pageTitle.x = 50;
        pageTitle.y = 20;
        
        const createdScreens = [];
        const screenSpacing = {layout_specs.get('spacing', {}).get('between_screens', 20)};
        
        // Generate each mobile screen with reference accuracy
        """
        
        # Generate each conversation screen
        for i, screen_data in enumerate(conversation_data):
            x_position = 50 + (i * (mobile_specs.get('frame_width', 375) + 30))
            y_position = 60
            
            script += self._generate_mobile_screen_script(i + 1, screen_data, x_position, y_position)
        
        script += """
        return {
            message: 'Reference-matched screens generated with high fidelity',
            screensCreated: createdScreens.length,
            screens: createdScreens,
            templateVersion: '2.0',
            referenceMatched: true,
            features: ['mobile_frames', 'agent_avatars', 'precise_bubbles', 'authentic_styling']
        };
        """
        
        return script
    
    def _generate_mobile_screen_script(self, screen_number: int, screen_data: Dict[str, Any], 
                                     x_pos: int, y_pos: int) -> str:
        """Generate script for a single mobile screen with reference accuracy."""
        
        specs = self.template_specs
        mobile_specs = specs.get('mobile_frame_specifications', {})
        avatar_specs = specs.get('agent_avatar_specifications', {})
        visual_specs = specs.get('visual_specifications', {})
        
        screen_name = screen_data.get('name', f'Screen {screen_number}')
        agent_message = screen_data.get('agent_message', 'Agent message')
        user_message = screen_data.get('user_message', 'User message')
        
        return f"""
        // Screen {screen_number}: {screen_name}
        
        // Create mobile device frame (iPhone style)
        const deviceFrame{screen_number} = figma.createFrame();
        deviceFrame{screen_number}.name = 'Device Frame {screen_number}';
        deviceFrame{screen_number}.resize({mobile_specs.get('frame_width', 375)}, {mobile_specs.get('frame_height', 812)});
        deviceFrame{screen_number}.x = {x_pos};
        deviceFrame{screen_number}.y = {y_pos};
        deviceFrame{screen_number}.fills = [{{ type: 'SOLID', color: {{ r: 0, g: 0, b: 0 }} }}];
        deviceFrame{screen_number}.cornerRadius = {mobile_specs.get('corner_radius', 30)};
        deviceFrame{screen_number}.strokeWeight = 2;
        deviceFrame{screen_number}.strokes = [{{ type: 'SOLID', color: {{ r: 0, g: 0, b: 0 }} }}];
        
        // Create screen content area
        const screenContent{screen_number} = figma.createFrame();
        screenContent{screen_number}.name = 'Screen Content';
        screenContent{screen_number}.resize({mobile_specs.get('frame_width', 375) - 8}, {mobile_specs.get('frame_height', 812) - 8});
        screenContent{screen_number}.x = 4;
        screenContent{screen_number}.y = 4;
        screenContent{screen_number}.fills = [{{ type: 'SOLID', color: {{ r: 1, g: 1, b: 1 }} }}];
        screenContent{screen_number}.cornerRadius = {mobile_specs.get('corner_radius', 30) - 4};
        
        // Add screen title above device
        const screenTitle{screen_number} = figma.createText();
        screenTitle{screen_number}.name = 'Screen Title';
        screenTitle{screen_number}.characters = '{screen_number}. {screen_name}';
        screenTitle{screen_number}.fontName = {{ family: 'Inter', style: 'Medium' }};
        screenTitle{screen_number}.fontSize = 12;
        screenTitle{screen_number}.fills = [{{ type: 'SOLID', color: {{ r: 0.4, g: 0.4, b: 0.4 }} }}];
        screenTitle{screen_number}.x = 0;
        screenTitle{screen_number}.y = -25;
        
        // Create header
        const header{screen_number} = figma.createFrame();
        header{screen_number}.name = 'Header';
        header{screen_number}.resize({mobile_specs.get('frame_width', 375) - 8}, 50);
        header{screen_number}.fills = [{{ type: 'SOLID', color: {{ r: 1, g: 1, b: 1 }} }}];
        header{screen_number}.layoutMode = 'HORIZONTAL';
        header{screen_number}.paddingLeft = 16;
        header{screen_number}.primaryAxisAlignItems = 'CENTER';
        
        const headerText{screen_number} = figma.createText();
        headerText{screen_number}.name = 'Header Text';
        headerText{screen_number}.characters = 'Agent';
        headerText{screen_number}.fontName = {{ family: 'Inter', style: 'Medium' }};
        headerText{screen_number}.fontSize = 16;
        headerText{screen_number}.fills = [{{ type: 'SOLID', color: {{ r: 0.1, g: 0.1, b: 0.1 }} }}];
        
        header{screen_number}.appendChild(headerText{screen_number});
        screenContent{screen_number}.appendChild(header{screen_number});
        
        // Create conversation area
        const conversation{screen_number} = figma.createFrame();
        conversation{screen_number}.name = 'Conversation';
        conversation{screen_number}.resize({mobile_specs.get('frame_width', 375) - 8}, 600);
        conversation{screen_number}.x = 0;
        conversation{screen_number}.y = 60;
        conversation{screen_number}.fills = [];
        
        // Agent avatar
        const avatar{screen_number} = figma.createEllipse();
        avatar{screen_number}.name = 'Agent Avatar';
        avatar{screen_number}.resize({avatar_specs.get('diameter', 32)}, {avatar_specs.get('diameter', 32)});
        avatar{screen_number}.x = {avatar_specs.get('position_offset', {}).get('left', 16)};
        avatar{screen_number}.y = 20;
        avatar{screen_number}.fills = [{{ 
            type: 'SOLID', 
            color: {{ 
                r: {avatar_specs.get('background_color', {}).get('color_rgb', {}).get('r', 0.176)}, 
                g: {avatar_specs.get('background_color', {}).get('color_rgb', {}).get('g', 0.176)}, 
                b: {avatar_specs.get('background_color', {}).get('color_rgb', {}).get('b', 0.176)} 
            }} 
        }}];
        
        // Agent message bubble
        const agentBubble{screen_number} = figma.createFrame();
        agentBubble{screen_number}.name = 'Agent Message';
        agentBubble{screen_number}.resize({visual_specs.get('agent_bubble', {}).get('max_width', 280)}, 80);
        agentBubble{screen_number}.x = {visual_specs.get('agent_bubble', {}).get('margin_left', 48)};
        agentBubble{screen_number}.y = 20;
        agentBubble{screen_number}.fills = [{{ 
            type: 'SOLID', 
            color: {{ 
                r: {visual_specs.get('agent_bubble', {}).get('color_rgb', {}).get('r', 0.941)}, 
                g: {visual_specs.get('agent_bubble', {}).get('color_rgb', {}).get('g', 0.941)}, 
                b: {visual_specs.get('agent_bubble', {}).get('color_rgb', {}).get('b', 0.941)} 
            }} 
        }}];
        agentBubble{screen_number}.cornerRadius = {visual_specs.get('agent_bubble', {}).get('corner_radius', 18)};
        agentBubble{screen_number}.layoutMode = 'VERTICAL';
        agentBubble{screen_number}.paddingLeft = {visual_specs.get('agent_bubble', {}).get('padding', {}).get('horizontal', 16)};
        agentBubble{screen_number}.paddingRight = {visual_specs.get('agent_bubble', {}).get('padding', {}).get('horizontal', 16)};
        agentBubble{screen_number}.paddingTop = {visual_specs.get('agent_bubble', {}).get('padding', {}).get('vertical', 12)};
        agentBubble{screen_number}.paddingBottom = {visual_specs.get('agent_bubble', {}).get('padding', {}).get('vertical', 12)};
        
        const agentText{screen_number} = figma.createText();
        agentText{screen_number}.name = 'Agent Text';
        agentText{screen_number}.characters = '{agent_message}';
        agentText{screen_number}.fontName = {{ family: 'Inter', style: 'Regular' }};
        agentText{screen_number}.fontSize = 15;
        agentText{screen_number}.lineHeight = {{ unit: 'PIXELS', value: 20 }};
        agentText{screen_number}.fills = [{{ type: 'SOLID', color: {{ r: 0.1, g: 0.1, b: 0.1 }} }}];
        agentText{screen_number}.resize({visual_specs.get('agent_bubble', {}).get('max_width', 280) - 32}, 56);
        
        agentBubble{screen_number}.appendChild(agentText{screen_number});
        
        // User message bubble (right aligned)
        const userBubble{screen_number} = figma.createFrame();
        userBubble{screen_number}.name = 'User Message';
        userBubble{screen_number}.resize({visual_specs.get('user_bubble', {}).get('max_width', 280)}, 50);
        userBubble{screen_number}.x = {mobile_specs.get('frame_width', 375) - 8 - visual_specs.get('user_bubble', {}).get('max_width', 280) - visual_specs.get('user_bubble', {}).get('margin_right', 16)};
        userBubble{screen_number}.y = 120;
        userBubble{screen_number}.fills = [{{ 
            type: 'SOLID', 
            color: {{ 
                r: {visual_specs.get('user_bubble', {}).get('color_rgb', {}).get('r', 0.0)}, 
                g: {visual_specs.get('user_bubble', {}).get('color_rgb', {}).get('g', 0.478)}, 
                b: {visual_specs.get('user_bubble', {}).get('color_rgb', {}).get('b', 1.0)} 
            }} 
        }}];
        userBubble{screen_number}.cornerRadius = {visual_specs.get('user_bubble', {}).get('corner_radius', 18)};
        userBubble{screen_number}.layoutMode = 'VERTICAL';
        userBubble{screen_number}.paddingLeft = {visual_specs.get('user_bubble', {}).get('padding', {}).get('horizontal', 16)};
        userBubble{screen_number}.paddingRight = {visual_specs.get('user_bubble', {}).get('padding', {}).get('horizontal', 16)};
        userBubble{screen_number}.paddingTop = {visual_specs.get('user_bubble', {}).get('padding', {}).get('vertical', 12)};
        userBubble{screen_number}.paddingBottom = {visual_specs.get('user_bubble', {}).get('padding', {}).get('vertical', 12)};
        
        const userText{screen_number} = figma.createText();
        userText{screen_number}.name = 'User Text';
        userText{screen_number}.characters = '{user_message}';
        userText{screen_number}.fontName = {{ family: 'Inter', style: 'Regular' }};
        userText{screen_number}.fontSize = 15;
        userText{screen_number}.fills = [{{ type: 'SOLID', color: {{ r: 1, g: 1, b: 1 }} }}];
        userText{screen_number}.resize({visual_specs.get('user_bubble', {}).get('max_width', 280) - 32}, 26);
        
        userBubble{screen_number}.appendChild(userText{screen_number});
        
        // Add elements to conversation
        conversation{screen_number}.appendChild(avatar{screen_number});
        conversation{screen_number}.appendChild(agentBubble{screen_number});
        conversation{screen_number}.appendChild(userBubble{screen_number});
        
        // Create input area
        const inputArea{screen_number} = figma.createFrame();
        inputArea{screen_number}.name = 'Input Area';
        inputArea{screen_number}.resize({mobile_specs.get('frame_width', 375) - 8}, 60);
        inputArea{screen_number}.x = 0;
        inputArea{screen_number}.y = {mobile_specs.get('frame_height', 812) - 68};
        inputArea{screen_number}.fills = [{{ type: 'SOLID', color: {{ r: 1, g: 1, b: 1 }} }}];
        inputArea{screen_number}.layoutMode = 'HORIZONTAL';
        inputArea{screen_number}.paddingLeft = 16;
        inputArea{screen_number}.paddingRight = 16;
        inputArea{screen_number}.paddingTop = 10;
        inputArea{screen_number}.paddingBottom = 10;
        inputArea{screen_number}.primaryAxisAlignItems = 'CENTER';
        inputArea{screen_number}.itemSpacing = 12;
        
        const inputField{screen_number} = figma.createFrame();
        inputField{screen_number}.name = 'Input Field';
        inputField{screen_number}.resize(280, 40);
        inputField{screen_number}.fills = [{{ type: 'SOLID', color: {{ r: 0.97, g: 0.97, b: 0.97 }} }}];
        inputField{screen_number}.cornerRadius = 20;
        
        const sendButton{screen_number} = figma.createEllipse();
        sendButton{screen_number}.name = 'Send Button';
        sendButton{screen_number}.resize(36, 36);
        sendButton{screen_number}.fills = [{{ type: 'SOLID', color: {{ r: 0.0, g: 0.478, b: 1.0 }} }}];
        
        inputArea{screen_number}.appendChild(inputField{screen_number});
        inputArea{screen_number}.appendChild(sendButton{screen_number});
        
        // Assemble the complete screen
        screenContent{screen_number}.appendChild(conversation{screen_number});
        screenContent{screen_number}.appendChild(inputArea{screen_number});
        deviceFrame{screen_number}.appendChild(screenContent{screen_number});
        deviceFrame{screen_number}.appendChild(screenTitle{screen_number});
        
        createdScreens.push({{ id: deviceFrame{screen_number}.id, name: '{screen_name}' }});
        
        """
    
    def get_conversation_data(self) -> List[Dict[str, Any]]:
        """Get the conversation data matching the reference screenshot."""
        return [
            {
                "name": "Welcome & Inquiry",
                "agent_message": "Hi there! I'm here to help with your return request. What can I help you with today?",
                "user_message": "I need to return an item"
            },
            {
                "name": "Identity Request + Reply", 
                "agent_message": "I can help you with that. Can you provide your order number or email address?",
                "user_message": "john.doe@email.com"
            },
            {
                "name": "Product Verification",
                "agent_message": "Thank you! I found your recent orders. Which item would you like to return?",
                "user_message": "The hiking boots from last week"
            },
            {
                "name": "Choice Return Policy",
                "agent_message": "I can help process that return. Would you like a refund or store credit?",
                "user_message": "Refund please"
            },
            {
                "name": "Return Info & Closing",
                "agent_message": "Perfect! I've initiated your return. You should receive a shipping label via email within 24 hours.",
                "user_message": "Thank you so much!"
            }
        ]