"""
Template Engine for Google Slides.
Loads and applies slide templates with data substitution.
"""
import json
import os
import re
from typing import Dict, List, Any, Optional

class TemplateEngine:
    """Loads and applies slide templates to Google Slides."""
    
    def __init__(self, template_path: str):
        """Initialize template engine.
        
        Args:
            template_path: Path to slide templates directory
        """
        self.template_path = template_path
        self.loaded_templates = {}
    
    def load_template(self, template_file: str) -> Dict[str, Any]:
        """Load a slide template from JSON file.
        
        Args:
            template_file: Relative path to template file (e.g., 'framework/cover_slide.json')
            
        Returns:
            Loaded template dictionary
        """
        if template_file in self.loaded_templates:
            return self.loaded_templates[template_file]
        
        template_full_path = os.path.join(self.template_path, template_file)
        
        if not os.path.exists(template_full_path):
            raise FileNotFoundError(f"Template not found: {template_full_path}")
        
        with open(template_full_path, 'r') as f:
            template = json.load(f)
        
        self.loaded_templates[template_file] = template
        return template
    
    def apply_template(self, presentation_id: str, slide_id: str, 
                      template: Dict[str, Any], data: Dict[str, Any],
                      slides_client: Any) -> Dict[str, Any]:
        """Apply template to a slide with data substitution.
        
        Args:
            presentation_id: Target presentation ID
            slide_id: Target slide ID
            template: Loaded template dictionary
            data: Data for template substitution
            slides_client: Google Slides client instance
            
        Returns:
            Dictionary with created object IDs
        """
        layout = template.get('layout', {})
        elements = layout.get('elements', [])
        
        created_objects = {}
        
        for element in elements:
            element_type = element.get('type')
            
            if element_type == 'text_box':
                obj_id = self._create_text_box(presentation_id, slide_id, element, data, slides_client)
                created_objects[element.get('id', 'text_box')] = obj_id
                
            elif element_type == 'shape':
                obj_id = self._create_shape(presentation_id, slide_id, element, data, slides_client)
                created_objects[element.get('id', 'shape')] = obj_id
                
            elif element_type == 'list':
                obj_id = self._create_list(presentation_id, slide_id, element, data, slides_client)
                created_objects[element.get('id', 'list')] = obj_id
                
            elif element_type == 'table':
                obj_id = self._create_table(presentation_id, slide_id, element, data, slides_client)
                created_objects[element.get('id', 'table')] = obj_id
                
            elif element_type == 'flow_diagram':
                # Flow diagrams are handled by FlowDiagramGenerator
                created_objects[element.get('id', 'flow_diagram')] = 'flow_diagram_placeholder'
        
        return created_objects
    
    def _create_text_box(self, presentation_id: str, slide_id: str, 
                        element: Dict[str, Any], data: Dict[str, Any], slides_client) -> str:
        """Create a text box element."""
        position = element.get('position', {})
        size = element.get('size', {})
        style = element.get('style', {})
        content = element.get('content', '')
        
        # Substitute template variables
        content = self._substitute_template_variables(content, data)
        
        # Create text box
        text_box_id = slides_client.add_text_box(
            presentation_id, slide_id, content,
            position.get('x', 0), position.get('y', 0),
            size.get('width', 100), size.get('height', 50),
            font_size=style.get('font_size', 14)
        )
        
        return text_box_id
    
    def _create_shape(self, presentation_id: str, slide_id: str,
                     element: Dict[str, Any], data: Dict[str, Any], slides_client) -> str:
        """Create a shape element."""
        position = element.get('position', {})
        size = element.get('size', {})
        style = element.get('style', {})
        shape_type = element.get('shape_type', 'RECTANGLE')
        
        # Create shape
        shape_id = slides_client.add_shape(
            presentation_id, slide_id, shape_type,
            position.get('x', 0), position.get('y', 0),
            size.get('width', 100), size.get('height', 50),
            fill_color=style.get('fill_color')
        )
        
        return shape_id
    
    def _create_list(self, presentation_id: str, slide_id: str,
                    element: Dict[str, Any], data: Dict[str, Any], slides_client) -> str:
        """Create a list element (as formatted text box)."""
        position = element.get('position', {})
        size = element.get('size', {})
        style = element.get('style', {})
        content_items = element.get('content', [])
        
        # Format list content
        bullet_style = style.get('bullet_style', 'bullet')
        formatted_content = []
        
        for i, item in enumerate(content_items):
            # Substitute template variables
            item = self._substitute_template_variables(str(item), data)
            
            if bullet_style == 'numbered':
                formatted_content.append(f"{i + 1}. {item}")
            else:
                formatted_content.append(f"• {item}")
        
        list_text = '\n'.join(formatted_content)
        
        # Create as text box
        list_id = slides_client.add_text_box(
            presentation_id, slide_id, list_text,
            position.get('x', 0), position.get('y', 0),
            size.get('width', 200), size.get('height', 100),
            font_size=style.get('font_size', 14)
        )
        
        return list_id
    
    def _create_table(self, presentation_id: str, slide_id: str,
                     element: Dict[str, Any], data: Dict[str, Any], slides_client) -> str:
        """Create a table element (as formatted text)."""
        position = element.get('position', {})
        size = element.get('size', {})
        table_config = element.get('table_config', {})
        
        headers = table_config.get('headers', [])
        rows = table_config.get('rows', [])
        
        # Format table as text
        table_lines = []
        
        # Headers
        if headers:
            header_line = ' | '.join(headers)
            table_lines.append(header_line)
            table_lines.append('-' * len(header_line))
        
        # Rows
        for row in rows:
            # Substitute template variables in row data
            processed_row = []
            for cell in row:
                processed_cell = self._substitute_template_variables(str(cell), data)
                processed_row.append(processed_cell)
            
            row_line = ' | '.join(processed_row)
            table_lines.append(row_line)
        
        table_text = '\n'.join(table_lines)
        
        # Create as text box
        table_id = slides_client.add_text_box(
            presentation_id, slide_id, table_text,
            position.get('x', 0), position.get('y', 0),
            size.get('width', 400), size.get('height', 200),
            font_size=table_config.get('styling', {}).get('font_size', 12)
        )
        
        return table_id
    
    def _substitute_template_variables(self, content: str, data: Dict[str, Any]) -> str:
        """Substitute template variables in content string.
        
        Supports dot notation: {{initiative_metadata.name}}, {{flows.0.topic}}
        """
        if not isinstance(content, str):
            return str(content)
        
        def replace_variable(match):
            variable_path = match.group(1)
            try:
                return str(self._get_nested_value(data, variable_path))
            except (KeyError, TypeError, IndexError):
                return f"[{variable_path}]"  # Leave placeholder if not found
        
        # Replace {{variable.path}} patterns
        return re.sub(r'{{([^}]+)}}', replace_variable, content)
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get value from nested dictionary using dot notation.
        
        Examples:
            'initiative_metadata.name' -> data['initiative_metadata']['name']
            'flows.0.topic' -> data['flows'][0]['topic']
        """
        keys = path.split('.')
        current = data
        
        for key in keys:
            # Check if key is numeric (array index)
            if key.isdigit():
                current = current[int(key)]
            else:
                current = current[key]
        
        return current
    
    def list_available_templates(self) -> Dict[str, List[str]]:
        """List all available templates organized by category."""
        templates = {}
        
        for root, dirs, files in os.walk(self.template_path):
            # Get relative path from template root
            rel_path = os.path.relpath(root, self.template_path)
            if rel_path == '.':
                rel_path = 'root'
            
            # Filter JSON files
            json_files = [f for f in files if f.endswith('.json')]
            
            if json_files:
                templates[rel_path] = json_files
        
        return templates