"""
Robust Figma Generator for Authentic Template Matching.
Handles reliable screen generation with error handling and template fidelity.
"""
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class FigmaGenerator:
    """Reliable Figma screen generator with template matching capabilities."""
    
    def __init__(self, figma_client=None):
        """Initialize with optional Figma client."""
        self.figma_client = figma_client
        self.required_fonts = [
            {"family": "Inter", "style": "Regular"},
            {"family": "Inter", "style": "Medium"},
            {"family": "Inter", "style": "Bold"}
        ]
        self.generation_log = []
        
    def log_action(self, action: str, details: Dict[str, Any] = None):
        """Log generation actions for debugging."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details or {}
        }
        self.generation_log.append(log_entry)
        logger.info(f"Figma Generator: {action} - {details}")
        
    def validate_figma_connection(self) -> bool:
        """Validate connection to Figma."""
        try:
            # Test basic Figma access
            if not self.figma_client:
                self.log_action("connection_error", {"error": "No Figma client provided"})
                return False
                
            self.log_action("connection_validated", {"status": "success"})
            return True
            
        except Exception as e:
            self.log_action("connection_error", {"error": str(e)})
            return False
    
    def prepare_fonts(self) -> Dict[str, Any]:
        """Pre-load all required fonts with error handling."""
        font_status = {"loaded": [], "failed": []}
        
        font_loading_script = """
        // Pre-load all required fonts
        const fontsToLoad = [
            { family: 'Inter', style: 'Regular' },
            { family: 'Inter', style: 'Medium' },
            { family: 'Inter', style: 'Bold' }
        ];
        
        const loadResults = [];
        
        for (const font of fontsToLoad) {
            try {
                await figma.loadFontAsync(font);
                loadResults.push({ font, status: 'success' });
            } catch (error) {
                loadResults.push({ font, status: 'error', error: error.message });
            }
        }
        
        return {
            message: 'Font loading completed',
            results: loadResults,
            totalLoaded: loadResults.filter(r => r.status === 'success').length,
            totalFailed: loadResults.filter(r => r.status === 'error').length
        };
        """
        
        try:
            # Execute font loading via Figma client
            if hasattr(self.figma_client, 'execute_script'):
                result = self.figma_client.execute_script(font_loading_script)
                self.log_action("fonts_prepared", result)
                return result
            else:
                self.log_action("font_preparation_skipped", {"reason": "No script execution capability"})
                return {"message": "Font preparation skipped", "totalLoaded": 0, "totalFailed": 0}
                
        except Exception as e:
            self.log_action("font_preparation_error", {"error": str(e)})
            return {"message": "Font preparation failed", "error": str(e)}
    
    def get_web_template_specs(self) -> Dict[str, Any]:
        """Get exact Web channel template specifications."""
        return {
            "background": {
                "color": "#F5F6F7",
                "rgb": {"r": 0.96, "g": 0.96, "b": 0.97}
            },
            "agent_bubble": {
                "color": "#EDEEF2", 
                "rgb": {"r": 0.93, "g": 0.94, "b": 0.95},
                "alignment": "left",
                "corner_radius": 12,
                "padding": {"horizontal": 12, "vertical": 8}
            },
            "user_bubble": {
                "color": "#007AFF",
                "rgb": {"r": 0.0, "g": 0.48, "b": 1.0},
                "alignment": "right", 
                "corner_radius": 12,
                "padding": {"horizontal": 12, "vertical": 8}
            },
            "typography": {
                "font_family": "Inter",
                "agent_text": {"size": 14, "line_height": 18, "style": "Regular"},
                "user_text": {"size": 14, "line_height": 18, "style": "Regular"},
                "header_text": {"size": 16, "line_height": 20, "style": "Medium"}
            },
            "layout": {
                "frame_width": 375,
                "frame_height": 812,
                "padding": 16,
                "bubble_spacing": 16,
                "header_height": 50,
                "input_height": 70
            }
        }
    
    def create_web_screen_structure(self, screen_number: int, screen_name: str, 
                                  x_position: int, y_position: int) -> str:
        """Generate Figma script for web screen structure."""
        specs = self.get_web_template_specs()
        
        return f"""
        // Create {screen_name}
        const screen{screen_number} = figma.createFrame();
        screen{screen_number}.name = '{screen_name}';
        screen{screen_number}.resize({specs['layout']['frame_width']}, {specs['layout']['frame_height']});
        screen{screen_number}.x = {x_position};
        screen{screen_number}.y = {y_position};
        screen{screen_number}.fills = [{{ 
            type: 'SOLID', 
            color: {{ r: {specs['background']['rgb']['r']}, g: {specs['background']['rgb']['g']}, b: {specs['background']['rgb']['b']} }} 
        }}];
        
        // Header
        const header{screen_number} = figma.createFrame();
        header{screen_number}.name = 'Header';
        header{screen_number}.resize({specs['layout']['frame_width']}, {specs['layout']['header_height']});
        header{screen_number}.fills = [{{ type: 'SOLID', color: {{ r: 1, g: 1, b: 1 }} }}];
        header{screen_number}.layoutMode = 'HORIZONTAL';
        header{screen_number}.paddingLeft = {specs['layout']['padding']};
        header{screen_number}.primaryAxisAlignItems = 'CENTER';
        
        const headerText{screen_number} = figma.createText();
        headerText{screen_number}.name = 'Header Text';
        headerText{screen_number}.characters = 'Agent';
        headerText{screen_number}.fontName = {{ family: '{specs['typography']['font_family']}', style: '{specs['typography']['header_text']['style']}' }};
        headerText{screen_number}.fontSize = {specs['typography']['header_text']['size']};
        headerText{screen_number}.fills = [{{ type: 'SOLID', color: {{ r: 0.1, g: 0.1, b: 0.1 }} }}];
        
        header{screen_number}.appendChild(headerText{screen_number});
        screen{screen_number}.appendChild(header{screen_number});
        
        // Return screen reference
        screen{screen_number};
        """
    
    def create_agent_message(self, screen_number: int, message_text: str, y_offset: int = 70) -> str:
        """Generate Figma script for agent message bubble."""
        specs = self.get_web_template_specs()
        
        return f"""
        // Agent Message for Screen {screen_number}
        const agentMsg{screen_number} = figma.createFrame();
        agentMsg{screen_number}.name = 'Agent Message';
        agentMsg{screen_number}.resize(280, 60);
        agentMsg{screen_number}.x = {specs['layout']['padding']};
        agentMsg{screen_number}.y = {y_offset};
        agentMsg{screen_number}.fills = [{{ 
            type: 'SOLID', 
            color: {{ r: {specs['agent_bubble']['rgb']['r']}, g: {specs['agent_bubble']['rgb']['g']}, b: {specs['agent_bubble']['rgb']['b']} }} 
        }}];
        agentMsg{screen_number}.cornerRadius = {specs['agent_bubble']['corner_radius']};
        agentMsg{screen_number}.layoutMode = 'VERTICAL';
        agentMsg{screen_number}.paddingLeft = {specs['agent_bubble']['padding']['horizontal']};
        agentMsg{screen_number}.paddingRight = {specs['agent_bubble']['padding']['horizontal']};
        agentMsg{screen_number}.paddingTop = {specs['agent_bubble']['padding']['vertical']};
        agentMsg{screen_number}.paddingBottom = {specs['agent_bubble']['padding']['vertical']};
        
        const agentText{screen_number} = figma.createText();
        agentText{screen_number}.name = 'Agent Text';
        agentText{screen_number}.characters = '{message_text}';
        agentText{screen_number}.fontName = {{ family: '{specs['typography']['font_family']}', style: '{specs['typography']['agent_text']['style']}' }};
        agentText{screen_number}.fontSize = {specs['typography']['agent_text']['size']};
        agentText{screen_number}.lineHeight = {{ unit: 'PIXELS', value: {specs['typography']['agent_text']['line_height']} }};
        agentText{screen_number}.fills = [{{ type: 'SOLID', color: {{ r: 0.1, g: 0.1, b: 0.1 }} }}];
        agentText{screen_number}.resize(256, 44);
        
        agentMsg{screen_number}.appendChild(agentText{screen_number});
        screen{screen_number}.appendChild(agentMsg{screen_number});
        """
    
    def create_user_message(self, screen_number: int, message_text: str, y_offset: int = 150) -> str:
        """Generate Figma script for user message bubble."""
        specs = self.get_web_template_specs()
        
        return f"""
        // User Message for Screen {screen_number}
        const userMsg{screen_number} = figma.createFrame();
        userMsg{screen_number}.name = 'User Message';
        userMsg{screen_number}.resize(250, 40);
        userMsg{screen_number}.x = 109; // Right aligned
        userMsg{screen_number}.y = {y_offset};
        userMsg{screen_number}.fills = [{{ 
            type: 'SOLID', 
            color: {{ r: {specs['user_bubble']['rgb']['r']}, g: {specs['user_bubble']['rgb']['g']}, b: {specs['user_bubble']['rgb']['b']} }} 
        }}];
        userMsg{screen_number}.cornerRadius = {specs['user_bubble']['corner_radius']};
        userMsg{screen_number}.layoutMode = 'VERTICAL';
        userMsg{screen_number}.paddingLeft = {specs['user_bubble']['padding']['horizontal']};
        userMsg{screen_number}.paddingRight = {specs['user_bubble']['padding']['horizontal']};
        userMsg{screen_number}.paddingTop = {specs['user_bubble']['padding']['vertical']};
        userMsg{screen_number}.paddingBottom = {specs['user_bubble']['padding']['vertical']};
        
        const userText{screen_number} = figma.createText();
        userText{screen_number}.name = 'User Text';
        userText{screen_number}.characters = '{message_text}';
        userText{screen_number}.fontName = {{ family: '{specs['typography']['font_family']}', style: '{specs['typography']['user_text']['style']}' }};
        userText{screen_number}.fontSize = {specs['typography']['user_text']['size']};
        userText{screen_number}.fills = [{{ type: 'SOLID', color: {{ r: 1, g: 1, b: 1 }} }}];
        userText{screen_number}.resize(226, 24);
        
        userMsg{screen_number}.appendChild(userText{screen_number});
        screen{screen_number}.appendChild(userMsg{screen_number});
        """
    
    def generate_web_screens(self, conversation_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate complete Web channel screens with template matching."""
        self.log_action("generation_started", {"channel": "web", "screens": len(conversation_data)})
        
        # Build complete Figma script
        full_script = """
        // Clear existing content
        const wolverinePage = figma.root.children.find(p => p.id === '36:114');
        await figma.setCurrentPageAsync(wolverinePage);
        wolverinePage.children.forEach(child => child.remove());
        
        // Load fonts first
        await figma.loadFontAsync({ family: 'Inter', style: 'Regular' });
        await figma.loadFontAsync({ family: 'Inter', style: 'Medium' });
        await figma.loadFontAsync({ family: 'Inter', style: 'Bold' });
        
        // Version header
        const versionHeader = figma.createText();
        versionHeader.name = 'V1 - Web Channel';
        versionHeader.characters = 'VERSION 1 - WEB CHANNEL (Authentic Template Matching)';
        versionHeader.fontName = { family: 'Inter', style: 'Bold' };
        versionHeader.fontSize = 20;
        versionHeader.fills = [{ type: 'SOLID', color: { r: 0.1, g: 0.1, b: 0.1 } }];
        versionHeader.x = 50;
        versionHeader.y = 50;
        
        const createdScreens = [];
        """
        
        # Generate each screen
        for i, screen_data in enumerate(conversation_data):
            screen_number = i + 1
            screen_name = screen_data.get('name', f'WEB-{screen_number:02d}')
            x_pos = 50 + (i * 400)  # Horizontal spacing
            y_pos = 100
            
            # Add screen structure
            full_script += self.create_web_screen_structure(screen_number, screen_name, x_pos, y_pos)
            
            # Add agent message if present
            if 'agent_message' in screen_data:
                full_script += self.create_agent_message(screen_number, screen_data['agent_message'])
            
            # Add user message if present  
            if 'user_message' in screen_data:
                full_script += self.create_user_message(screen_number, screen_data['user_message'])
            
            full_script += f"createdScreens.push({{ id: screen{screen_number}.id, name: '{screen_name}' }});\n"
        
        # Return results
        full_script += """
        return {
            message: 'Web screens generated with template matching',
            screensCreated: createdScreens.length,
            screens: createdScreens,
            templateSpecs: 'authentic_web_chatbot'
        };
        """
        
        return {
            "script": full_script,
            "screens_count": len(conversation_data),
            "generation_log": self.generation_log
        }
    
    def validate_generation_result(self, result: Dict[str, Any]) -> bool:
        """Validate that generation was successful."""
        try:
            if not result:
                return False
                
            screens_created = result.get('screensCreated', 0)
            expected_screens = 4  # WISMO web flow
            
            success = screens_created == expected_screens
            
            self.log_action("validation_completed", {
                "success": success,
                "screens_created": screens_created,
                "expected_screens": expected_screens
            })
            
            return success
            
        except Exception as e:
            self.log_action("validation_error", {"error": str(e)})
            return False
    
    def get_generation_summary(self) -> Dict[str, Any]:
        """Get summary of generation process."""
        return {
            "total_actions": len(self.generation_log),
            "log_entries": self.generation_log,
            "template_specs": self.get_web_template_specs(),
            "status": "ready_for_execution"
        }