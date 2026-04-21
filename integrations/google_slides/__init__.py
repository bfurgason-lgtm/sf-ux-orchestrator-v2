"""
Google Slides Integration for sf-ux-orchestrator.
Provides automated presentation generation with three-tier structure and flow diagrams.
"""
from .slides_client import GoogleSlidesClient
from .presentation_builder import PresentationBuilder
from .flow_diagram_generator import FlowDiagramGenerator
from .content_organizer import ContentOrganizer
from .template_engine import TemplateEngine
from .pdf_exporter import PDFExporter

__all__ = [
    'GoogleSlidesClient',
    'PresentationBuilder', 
    'FlowDiagramGenerator',
    'ContentOrganizer',
    'TemplateEngine',
    'PDFExporter',
    'generate_presentation_from_manifest',
    'SlidesIntegrationError'
]

class SlidesIntegrationError(Exception):
    """Exception raised for Google Slides integration errors."""
    pass

def generate_presentation_from_manifest(manifest_data: dict, 
                                      credentials_path: str = None,
                                      export_to_drive: bool = True) -> dict:
    """Main entry point for generating presentations from manifest data.
    
    Args:
        manifest_data: Enhanced manifest v0.5 data
        credentials_path: Path to Google credentials JSON
        export_to_drive: Whether to export to Drive folder
        
    Returns:
        Dictionary with presentation results and export information
    """
    try:
        # Initialize Google Slides client
        client = GoogleSlidesClient(credentials_path=credentials_path)
        
        # Create presentation builder
        builder = PresentationBuilder(client)
        
        # Generate presentation
        build_result = builder.build_presentation_from_manifest(manifest_data)
        
        # Export if requested
        export_results = {}
        slides_config = manifest_data.get('google_slides', {})
        
        if slides_config.get('auto_generate', False):
            exporter = PDFExporter(client)
            export_formats = slides_config.get('export_formats', ['pdf'])
            
            # Export to multiple formats
            export_results = exporter.batch_export_multiple_formats(
                build_result['presentation_id'],
                formats=export_formats
            )
            
            # Export to Drive if configured
            if export_to_drive:
                drive_config = manifest_data.get('drive', {})
                exports_folder = drive_config.get('exports_folder')
                
                if exports_folder:
                    drive_result = exporter.export_to_drive_folder(
                        build_result['presentation_id'],
                        exports_folder
                    )
                    export_results['drive_export'] = drive_result
        
        return {
            'success': True,
            'presentation': build_result,
            'exports': export_results,
            'integration_version': '0.5'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }