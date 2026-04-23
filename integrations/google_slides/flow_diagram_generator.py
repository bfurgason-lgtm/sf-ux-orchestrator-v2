"""
Flow Diagram Generator for Google Slides.
Creates automated flow diagrams from manifest step sequences matching PDF template patterns.
"""
import math
from typing import Dict, List, Tuple, Any, Optional
from .slides_client import GoogleSlidesClient

class FlowDiagramGenerator:
    """Generates flow diagrams in Google Slides from manifest data."""
    
    # Flow component styling (matching PDF template)
    STYLES = {
        'start_end': {
            'shape': 'ROUND_RECTANGLE',
            'fill_color': '#E8F4FD',  # Light blue
            'text_color': '#1B4B66',
            'border_color': '#4A90C2'
        },
        'process': {
            'shape': 'RECTANGLE', 
            'fill_color': '#F0F8F0',  # Light green
            'text_color': '#2D5016',
            'border_color': '#5CB85C'
        },
        'decision': {
            'shape': 'DIAMOND',
            'fill_color': '#FFF2CC',  # Light yellow
            'text_color': '#8A6914',
            'border_color': '#F1C40F'
        },
        'user_input': {
            'shape': 'RECTANGLE',
            'fill_color': '#F8F0FF',  # Light purple
            'text_color': '#5A2D91',
            'border_color': '#9B59B6'
        },
        'escalation': {
            'shape': 'RECTANGLE',
            'fill_color': '#FFEBEE',  # Light red
            'text_color': '#C62828',
            'border_color': '#E74C3C'
        },
        'channel_badge': {
            'shape': 'ELLIPSE',
            'fill_color': '#263238',  # Dark gray
            'text_color': '#FFFFFF',
            'border_color': '#37474F'
        }
    }
    
    # Layout constants (in points)
    CANVAS_WIDTH = 720  # 10 inches at 72 DPI
    CANVAS_HEIGHT = 540  # 7.5 inches at 72 DPI
    MARGIN = 40
    NODE_WIDTH = 140
    NODE_HEIGHT = 60
    DECISION_SIZE = 80  # Diamonds are square
    VERTICAL_SPACING = 100
    HORIZONTAL_SPACING = 180
    
    def __init__(self, slides_client: GoogleSlidesClient, visual_fidelity_mode: bool = True):
        """Initialize with Google Slides client and visual fidelity option."""
        self.client = slides_client
        self.visual_fidelity_mode = visual_fidelity_mode
    
    def generate_flow_diagram(self, presentation_id: str, slide_id: str,
                            flow_data: Dict[str, Any], diagram_type: str = "main") -> Dict[str, Any]:
        """Generate a flow diagram on the specified slide.
        
        Args:
            presentation_id: Target presentation ID
            slide_id: Target slide ID  
            flow_data: Flow data from manifest
            diagram_type: Type of diagram (main, edge_cases, persona_comparison)
            
        Returns:
            Dictionary with created object IDs and layout info
        """
        if diagram_type == "main":
            return self._generate_main_flow(presentation_id, slide_id, flow_data)
        elif diagram_type == "edge_cases":
            return self._generate_edge_case_flow(presentation_id, slide_id, flow_data)
        elif diagram_type == "persona_comparison":
            return self._generate_persona_comparison(presentation_id, slide_id, flow_data)
        else:
            raise ValueError(f"Unknown diagram type: {diagram_type}")
    
    def _generate_main_flow(self, presentation_id: str, slide_id: str, 
                           flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate persona-agnostic main flow diagram."""
        steps = flow_data.get('steps', [])
        topic = flow_data.get('topic', 'Flow Diagram')
        
        # Filter out edge cases for main flow
        main_steps = [step for step in steps if not step.get('is_edge_case', False)]
        
        # Calculate layout
        layout = self._calculate_vertical_layout(len(main_steps))
        
        created_objects = {}
        
        # Add title
        title_id = self.client.add_text_box(
            presentation_id, slide_id,
            f"{topic} - Main Flow",
            self.MARGIN, self.MARGIN, 
            self.CANVAS_WIDTH - 2 * self.MARGIN, 40,
            font_size=18
        )
        created_objects['title'] = title_id
        
        # Create flow nodes
        node_ids = []
        for i, step in enumerate(main_steps):
            node_id = self._create_flow_node(
                presentation_id, slide_id, step, 
                layout['positions'][i], f"step_{i}"
            )
            node_ids.append(node_id)
            created_objects[f'step_{i}'] = node_id
        
        # Connect nodes with arrows
        for i in range(len(node_ids) - 1):
            connector_id = self.client.connect_shapes(
                presentation_id, slide_id,
                node_ids[i], node_ids[i + 1]
            )
            created_objects[f'connector_{i}'] = connector_id
        
        # Add channel indicators
        channels = flow_data.get('channels', [])
        if channels:
            channel_ids = self._add_channel_badges(
                presentation_id, slide_id, channels
            )
            created_objects['channels'] = channel_ids
        
        return created_objects
    
    def _generate_edge_case_flow(self, presentation_id: str, slide_id: str,
                                flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate edge case detail flow diagram."""
        steps = flow_data.get('steps', [])
        topic = flow_data.get('topic', 'Edge Cases')
        
        # Filter for edge cases only
        edge_steps = [step for step in steps if step.get('is_edge_case', False)]
        
        if not edge_steps:
            # Create "No Edge Cases" message
            return {
                'message': self.client.add_text_box(
                    presentation_id, slide_id,
                    f"{topic} - No Edge Cases Defined",
                    self.CANVAS_WIDTH // 2 - 100, self.CANVAS_HEIGHT // 2 - 20,
                    200, 40, font_size=16
                )
            }
        
        created_objects = {}
        
        # Add title
        title_id = self.client.add_text_box(
            presentation_id, slide_id,
            f"{topic} - Edge Cases & Exceptions",
            self.MARGIN, self.MARGIN,
            self.CANVAS_WIDTH - 2 * self.MARGIN, 40,
            font_size=18
        )
        created_objects['title'] = title_id
        
        # Create branching layout for edge cases
        layout = self._calculate_branching_layout(len(edge_steps))
        
        # Create nodes for each edge case
        for i, step in enumerate(edge_steps):
            node_id = self._create_flow_node(
                presentation_id, slide_id, step,
                layout['positions'][i], f"edge_{i}",
                node_type='escalation'
            )
            created_objects[f'edge_{i}'] = node_id
        
        return created_objects
    
    def _generate_persona_comparison(self, presentation_id: str, slide_id: str,
                                   flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate persona comparison diagram showing brand variations."""
        steps = flow_data.get('steps', [])
        topic = flow_data.get('topic', 'Persona Comparison')
        
        # Take first few steps to show persona differences
        comparison_steps = steps[:3] if len(steps) >= 3 else steps
        
        created_objects = {}
        
        # Add title
        title_id = self.client.add_text_box(
            presentation_id, slide_id,
            f"{topic} - Persona Variations",
            self.MARGIN, self.MARGIN,
            self.CANVAS_WIDTH - 2 * self.MARGIN, 40,
            font_size=18
        )
        created_objects['title'] = title_id
        
        # Create side-by-side comparison layout
        personas = ['Professional', 'Friendly', 'Technical']  # Example personas
        layout = self._calculate_comparison_layout(len(personas))
        
        for i, persona in enumerate(personas):
            # Create persona column
            persona_objects = self._create_persona_column(
                presentation_id, slide_id, comparison_steps,
                layout['columns'][i], persona
            )
            created_objects[f'persona_{i}'] = persona_objects
        
        return created_objects
    
    def _create_flow_node(self, presentation_id: str, slide_id: str, 
                         step_data: Dict[str, Any], position: Tuple[float, float],
                         node_id: str, node_type: str = None) -> str:
        """Create a single flow node (shape + text)."""
        x, y = position
        
        # Determine node type from step data if not specified
        if node_type is None:
            if step_data.get('step_number') == 1:
                node_type = 'start_end'
            elif 'decision' in step_data.get('step_name', '').lower():
                node_type = 'decision'
            elif step_data.get('is_edge_case'):
                node_type = 'escalation'
            elif 'user' in step_data.get('utterances', {}).get('user', '').lower():
                node_type = 'user_input'
            else:
                node_type = 'process'
        
        style = self.STYLES[node_type]
        
        # Adjust dimensions for diamond shape
        if node_type == 'decision':
            width = height = self.DECISION_SIZE
        else:
            width, height = self.NODE_WIDTH, self.NODE_HEIGHT
        
        # Create shape
        shape_id = self.client.add_shape(
            presentation_id, slide_id, style['shape'],
            x, y, width, height, style['fill_color']
        )
        
        # Add text overlay
        text = self._format_step_text(step_data)
        text_id = self.client.add_text_box(
            presentation_id, slide_id, text,
            x + 5, y + 10, width - 10, height - 20,
            font_size=10
        )
        
        return shape_id
    
    def _format_step_text(self, step_data: Dict[str, Any]) -> str:
        """Format step data into concise node text."""
        step_name = step_data.get('step_name', 'Step')
        step_num = step_data.get('step_number', '')
        
        # Truncate long names
        if len(step_name) > 20:
            step_name = step_name[:17] + "..."
        
        return f"{step_num}. {step_name}" if step_num else step_name
    
    def _calculate_vertical_layout(self, num_nodes: int) -> Dict[str, Any]:
        """Calculate vertical flow layout positions."""
        start_y = self.MARGIN + 60  # Below title
        available_height = self.CANVAS_HEIGHT - start_y - self.MARGIN
        
        if num_nodes > 1:
            spacing = min(self.VERTICAL_SPACING, available_height / (num_nodes - 1))
        else:
            spacing = 0
        
        center_x = self.CANVAS_WIDTH // 2 - self.NODE_WIDTH // 2
        
        positions = []
        for i in range(num_nodes):
            y = start_y + i * spacing
            positions.append((center_x, y))
        
        return {'positions': positions, 'spacing': spacing}
    
    def _calculate_branching_layout(self, num_nodes: int) -> Dict[str, Any]:
        """Calculate branching layout for edge cases."""
        rows = math.ceil(num_nodes / 3)  # Max 3 per row
        cols = min(3, num_nodes)
        
        start_x = self.MARGIN + 50
        start_y = self.MARGIN + 100
        
        positions = []
        for i in range(num_nodes):
            row = i // cols
            col = i % cols
            x = start_x + col * self.HORIZONTAL_SPACING
            y = start_y + row * self.VERTICAL_SPACING
            positions.append((x, y))
        
        return {'positions': positions}
    
    def _calculate_comparison_layout(self, num_columns: int) -> Dict[str, Any]:
        """Calculate side-by-side comparison layout."""
        column_width = (self.CANVAS_WIDTH - 2 * self.MARGIN) / num_columns
        
        columns = []
        for i in range(num_columns):
            x = self.MARGIN + i * column_width
            columns.append({
                'x': x,
                'width': column_width,
                'center_x': x + column_width // 2 - self.NODE_WIDTH // 2
            })
        
        return {'columns': columns}
    
    def _create_persona_column(self, presentation_id: str, slide_id: str,
                              steps: List[Dict], column_layout: Dict, persona: str) -> Dict[str, str]:
        """Create a column of nodes for persona comparison."""
        objects = {}
        
        # Persona header
        header_id = self.client.add_text_box(
            presentation_id, slide_id, persona,
            column_layout['x'], self.MARGIN + 60,
            column_layout['width'], 30, font_size=14
        )
        objects['header'] = header_id
        
        # Create nodes for this persona
        start_y = self.MARGIN + 120
        for i, step in enumerate(steps):
            y = start_y + i * self.VERTICAL_SPACING
            node_id = self._create_flow_node(
                presentation_id, slide_id, step,
                (column_layout['center_x'], y), f"{persona}_{i}"
            )
            objects[f'step_{i}'] = node_id
        
        return objects
    
    def _add_channel_badges(self, presentation_id: str, slide_id: str, 
                           channels: List[str]) -> Dict[str, str]:
        """Add channel indicator badges to the diagram."""
        badge_ids = {}
        
        # Position badges in top-right corner
        start_x = self.CANVAS_WIDTH - self.MARGIN - 60
        start_y = self.MARGIN + 60
        
        for i, channel in enumerate(channels):
            x = start_x - i * 70  # Horizontal spacing
            badge_id = self.client.add_shape(
                presentation_id, slide_id, 
                self.STYLES['channel_badge']['shape'],
                x, start_y, 50, 25,
                self.STYLES['channel_badge']['fill_color']
            )
            
            # Add channel text
            text_id = self.client.add_text_box(
                presentation_id, slide_id, channel.upper(),
                x + 5, start_y + 5, 40, 15, font_size=8
            )
            
            badge_ids[f'{channel}_badge'] = badge_id
            badge_ids[f'{channel}_text'] = text_id
        
        return badge_ids