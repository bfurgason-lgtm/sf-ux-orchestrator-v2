"""
Presentation Builder for Google Slides.
Orchestrates the creation of complete presentations using the three-tier structure.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from .slides_client import GoogleSlidesClient
from .flow_diagram_generator import FlowDiagramGenerator
from .content_organizer import ContentOrganizer
from .template_engine import TemplateEngine

class PresentationBuilder:
    """Main presentation builder orchestrating slide generation."""
    
    def __init__(self, slides_client: GoogleSlidesClient, template_path: str = None):
        """Initialize presentation builder with required components.
        
        Args:
            slides_client: Authenticated Google Slides client
            template_path: Path to slide templates directory
        """
        self.client = slides_client
        self.flow_generator = FlowDiagramGenerator(slides_client)
        self.content_organizer = ContentOrganizer()
        self.template_engine = TemplateEngine(template_path or self._get_default_template_path())
        
    def _get_default_template_path(self) -> str:
        """Get default path to slide templates."""
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, '../../core/templates/slides')
    
    def build_presentation_from_manifest(self, manifest_data: Dict[str, Any],
                                       presentation_title: str = None) -> Dict[str, Any]:
        """Build complete presentation from manifest data using three-tier structure.
        
        Args:
            manifest_data: Enhanced manifest v0.5 data
            presentation_title: Custom title (defaults to initiative name)
            
        Returns:
            Dictionary with presentation ID, URL, and build summary
        """
        # Validate manifest
        self._validate_manifest(manifest_data)
        
        # Generate presentation title
        if not presentation_title:
            initiative_name = manifest_data['initiative_metadata']['name']
            timestamp = datetime.now().strftime("%Y-%m-%d")
            presentation_title = f"{initiative_name} - Solution Design ({timestamp})"
        
        # Create presentation
        presentation = self.client.create_presentation(presentation_title)
        presentation_id = presentation['presentationId']
        
        # Organize content using three-tier strategy
        content_plan = self.content_organizer.organize_three_tier_content(manifest_data)
        
        # Build slides in order
        slide_results = []
        
        try:
            # 1. Framework slides
            framework_slides = self._build_framework_slides(presentation_id, manifest_data)
            slide_results.extend(framework_slides)
            
            # 2. Persona examples (early slides for stakeholder buy-in)
            persona_slides = self._build_persona_examples(presentation_id, content_plan['persona_examples'])
            slide_results.extend(persona_slides)
            
            # 3. Section dividers and main content
            for section in content_plan['sections']:
                # Section divider
                divider_slide = self._build_section_divider(presentation_id, section)
                slide_results.append(divider_slide)
                
                # Section content slides
                section_slides = self._build_section_slides(presentation_id, section)
                slide_results.extend(section_slides)
            
            # 4. Technical requirements
            tech_slides = self._build_technical_slides(presentation_id, manifest_data)
            slide_results.extend(tech_slides)
            
            # 5. Appendix
            appendix_slides = self._build_appendix_slides(presentation_id, content_plan['appendix'])
            slide_results.extend(appendix_slides)
            
        except Exception as e:
            # Clean up on failure
            raise Exception(f"Failed to build presentation {presentation_id}: {str(e)}")
        
        # Generate summary
        build_summary = {
            'presentation_id': presentation_id,
            'presentation_url': self.client.get_presentation_url(presentation_id),
            'slide_count': len(slide_results),
            'sections_created': len(content_plan['sections']),
            'flow_diagrams': sum(1 for slide in slide_results if slide.get('type') == 'flow_diagram'),
            'build_timestamp': datetime.now().isoformat(),
            'manifest_version': manifest_data.get('schema_version', 'unknown')
        }
        
        return build_summary
    
    def _validate_manifest(self, manifest_data: Dict[str, Any]):
        """Validate manifest has required fields for presentation generation."""
        required_fields = [
            'schema_version',
            'initiative_metadata.name',
            'flows'
        ]
        
        for field in required_fields:
            keys = field.split('.')
            current = manifest_data
            try:
                for key in keys:
                    current = current[key]
            except (KeyError, TypeError):
                raise ValueError(f"Required manifest field missing: {field}")
        
        # Validate flows have steps
        flows = manifest_data.get('flows', [])
        if not flows:
            raise ValueError("Manifest must contain at least one flow")
        
        for i, flow in enumerate(flows):
            if not flow.get('steps'):
                raise ValueError(f"Flow {i} must contain at least one step")
    
    def _build_framework_slides(self, presentation_id: str, manifest_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build framework slides (cover, agenda, etc.)."""
        slides = []
        
        # Cover slide
        cover_slide_id = self.client.create_slide(presentation_id, layout="BLANK")
        cover_template = self.template_engine.load_template('framework/cover_slide.json')
        self.template_engine.apply_template(
            presentation_id, cover_slide_id, cover_template, manifest_data
        )
        slides.append({
            'type': 'cover',
            'slide_id': cover_slide_id,
            'template': 'cover_slide'
        })
        
        # Agenda slide  
        agenda_slide_id = self.client.create_slide(presentation_id, layout="BLANK")
        agenda_template = self.template_engine.load_template('framework/agenda_slide.json')
        self.template_engine.apply_template(
            presentation_id, agenda_slide_id, agenda_template, manifest_data
        )
        slides.append({
            'type': 'agenda',
            'slide_id': agenda_slide_id,
            'template': 'agenda_slide'
        })
        
        return slides
    
    def _build_persona_examples(self, presentation_id: str, persona_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build early persona example slides for stakeholder buy-in."""
        slides = []
        
        for persona_example in persona_data:
            slide_id = self.client.create_slide(presentation_id, layout="BLANK")
            
            # Generate persona comparison flow diagram
            flow_objects = self.flow_generator.generate_flow_diagram(
                presentation_id, slide_id, persona_example, "persona_comparison"
            )
            
            slides.append({
                'type': 'persona_example',
                'slide_id': slide_id,
                'flow_objects': flow_objects,
                'persona': persona_example.get('persona_name', 'Unknown')
            })
        
        return slides
    
    def _build_section_divider(self, presentation_id: str, section_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build a section divider slide."""
        slide_id = self.client.create_slide(presentation_id, layout="BLANK")
        
        divider_template = self.template_engine.load_template('framework/section_divider.json')
        template_data = {
            'section_number': section_data.get('section_number', ''),
            'section_title': section_data.get('title', 'Section')
        }
        
        self.template_engine.apply_template(
            presentation_id, slide_id, divider_template, template_data
        )
        
        return {
            'type': 'section_divider',
            'slide_id': slide_id,
            'section': section_data.get('title', 'Section')
        }
    
    def _build_section_slides(self, presentation_id: str, section_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build slides for a content section."""
        slides = []
        section_type = section_data.get('type', 'content')
        
        if section_type == 'flow_overview':
            slides.extend(self._build_flow_overview_slides(presentation_id, section_data))
        elif section_type == 'edge_cases':
            slides.extend(self._build_edge_case_slides(presentation_id, section_data))
        elif section_type == 'channel_implementation':
            slides.extend(self._build_channel_slides(presentation_id, section_data))
        else:
            # Generic content slide
            slide_id = self.client.create_slide(presentation_id, layout="TITLE_AND_BODY")
            slides.append({
                'type': 'content',
                'slide_id': slide_id,
                'section': section_data.get('title', 'Content')
            })
        
        return slides
    
    def _build_flow_overview_slides(self, presentation_id: str, section_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build persona-agnostic flow overview slides."""
        slides = []
        
        for flow_data in section_data.get('flows', []):
            slide_id = self.client.create_slide(presentation_id, layout="BLANK")
            
            # Generate main flow diagram
            flow_objects = self.flow_generator.generate_flow_diagram(
                presentation_id, slide_id, flow_data, "main"
            )
            
            slides.append({
                'type': 'flow_diagram',
                'slide_id': slide_id,
                'flow_objects': flow_objects,
                'flow_topic': flow_data.get('topic', 'Flow'),
                'diagram_type': 'main'
            })
        
        return slides
    
    def _build_edge_case_slides(self, presentation_id: str, section_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build edge case detail slides."""
        slides = []
        
        for flow_data in section_data.get('flows', []):
            slide_id = self.client.create_slide(presentation_id, layout="BLANK")
            
            # Generate edge case diagram
            flow_objects = self.flow_generator.generate_flow_diagram(
                presentation_id, slide_id, flow_data, "edge_cases"
            )
            
            slides.append({
                'type': 'flow_diagram',
                'slide_id': slide_id,
                'flow_objects': flow_objects,
                'flow_topic': flow_data.get('topic', 'Flow'),
                'diagram_type': 'edge_cases'
            })
        
        return slides
    
    def _build_channel_slides(self, presentation_id: str, section_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build channel implementation slides."""
        slides = []
        
        channels = section_data.get('channels', ['web', 'email', 'sms', 'voice'])
        for channel in channels:
            slide_id = self.client.create_slide(presentation_id, layout="TITLE_AND_BODY")
            
            # Add channel-specific content
            channel_title = f"{channel.upper()} Channel Implementation"
            self.client.add_text_box(
                presentation_id, slide_id,
                channel_title, 72, 50, 576, 40, font_size=20
            )
            
            slides.append({
                'type': 'channel_implementation',
                'slide_id': slide_id,
                'channel': channel
            })
        
        return slides
    
    def _build_technical_slides(self, presentation_id: str, manifest_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build technical requirements slides."""
        slides = []
        
        # Technical requirements slide
        tech_slide_id = self.client.create_slide(presentation_id, layout="BLANK")
        tech_template = self.template_engine.load_template('content/technical_requirements.json')
        self.template_engine.apply_template(
            presentation_id, tech_slide_id, tech_template, manifest_data
        )
        
        slides.append({
            'type': 'technical_requirements',
            'slide_id': tech_slide_id,
            'template': 'technical_requirements'
        })
        
        return slides
    
    def _build_appendix_slides(self, presentation_id: str, appendix_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build appendix slides for additional details."""
        slides = []
        
        # Appendix divider
        appendix_slide_id = self.client.create_slide(presentation_id, layout="SECTION_HEADER")
        self.client.add_text_box(
            presentation_id, appendix_slide_id,
            "Appendix", 72, 200, 576, 60, font_size=32
        )
        
        slides.append({
            'type': 'appendix_divider',
            'slide_id': appendix_slide_id
        })
        
        # Additional detail slides as needed
        for item in appendix_data:
            detail_slide_id = self.client.create_slide(presentation_id, layout="TITLE_AND_BODY")
            slides.append({
                'type': 'appendix_detail',
                'slide_id': detail_slide_id,
                'item': item.get('title', 'Detail')
            })
        
        return slides