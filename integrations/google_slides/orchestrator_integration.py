"""
Orchestrator Integration for Google Slides.
Integrates presentation generation into the main sf-ux-orchestrator pipeline.
"""
import os
import json
from typing import Dict, Any, Optional
from . import generate_presentation_from_manifest

class SlidesOrchestrator:
    """Orchestrates Google Slides generation within the main pipeline."""
    
    def __init__(self, credentials_path: str = None):
        """Initialize slides orchestrator.
        
        Args:
            credentials_path: Path to Google credentials JSON
        """
        self.credentials_path = credentials_path or self._get_default_credentials_path()
    
    def _get_default_credentials_path(self) -> str:
        """Get default path for Google credentials."""
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, 'credentials.json')
    
    def should_generate_presentation(self, manifest_data: Dict[str, Any]) -> bool:
        """Check if presentation should be auto-generated based on manifest config.
        
        Args:
            manifest_data: Enhanced manifest v0.5 data
            
        Returns:
            True if presentation should be generated
        """
        slides_config = manifest_data.get('google_slides', {})
        return slides_config.get('auto_generate', False)
    
    def generate_presentation(self, manifest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate presentation as part of orchestrator pipeline.
        
        Args:
            manifest_data: Enhanced manifest v0.5 data
            
        Returns:
            Generation results with presentation info and export status
        """
        # Validate Google Slides credentials
        if not os.path.exists(self.credentials_path):
            return {
                'success': False,
                'error': f'Google Slides credentials not found at {self.credentials_path}',
                'skip_reason': 'missing_credentials'
            }
        
        # Check if auto-generation is enabled
        if not self.should_generate_presentation(manifest_data):
            return {
                'success': True,
                'skipped': True,
                'skip_reason': 'auto_generate_disabled'
            }
        
        # Generate presentation
        try:
            result = generate_presentation_from_manifest(
                manifest_data,
                credentials_path=self.credentials_path,
                export_to_drive=True
            )
            
            # Add orchestrator metadata
            if result['success']:
                result['orchestrator_metadata'] = {
                    'pipeline_step': 'google_slides_generation',
                    'manifest_version': manifest_data.get('schema_version', 'unknown'),
                    'integration_point': 'post_figma_export'
                }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to generate presentation: {str(e)}',
                'error_type': type(e).__name__
            }
    
    def format_orchestrator_report(self, slides_result: Dict[str, Any]) -> str:
        """Format slides results for orchestrator completion report.
        
        Args:
            slides_result: Results from presentation generation
            
        Returns:
            Formatted report string
        """
        if not slides_result['success']:
            if slides_result.get('skipped'):
                return "📊 Google Slides: Skipped (auto_generate disabled)"
            else:
                error = slides_result.get('error', 'Unknown error')
                return f"📊 Google Slides: Failed - {error}"
        
        presentation = slides_result.get('presentation', {})
        exports = slides_result.get('exports', {})
        
        # Format presentation info
        lines = [
            "📊 Google Slides: Generated successfully",
            f" ✅ Presentation: {presentation.get('slide_count', 0)} slides",
            f" ✅ Sections: {presentation.get('sections_created', 0)} sections created",
            f" ✅ Flow diagrams: {presentation.get('flow_diagrams', 0)} generated",
            f" ✅ URL: {presentation.get('presentation_url', 'N/A')}"
        ]
        
        # Format export info
        export_count = len([k for k, v in exports.items() 
                           if k != 'drive_export' and v.get('success', False)])
        
        if export_count > 0:
            lines.append(f" ✅ Exports: {export_count} format(s) exported")
            
            # Drive export status
            drive_export = exports.get('drive_export')
            if drive_export:
                if drive_export.get('success'):
                    lines.append(f" ✅ Drive sync: Saved to {drive_export.get('drive_path', 'Drive')}")
                else:
                    lines.append(f" ⚠️  Drive sync: Failed - {drive_export.get('error', 'Unknown')}")
        
        return '\n'.join(lines)
    
    def get_setup_instructions(self) -> Dict[str, Any]:
        """Get setup instructions for Google Slides integration.
        
        Returns:
            Setup instructions and requirements
        """
        return {
            'title': 'Google Slides Integration Setup',
            'requirements': [
                'Google Cloud Console project with Slides API enabled',
                'OAuth2 credentials downloaded as credentials.json',
                'Google account with presentation creation permissions'
            ],
            'setup_steps': [
                {
                    'step': 1,
                    'description': 'Enable Google Slides API in Google Cloud Console',
                    'url': 'https://console.cloud.google.com/apis/library/slides.googleapis.com'
                },
                {
                    'step': 2,
                    'description': 'Create OAuth2 credentials (Desktop application)',
                    'url': 'https://console.cloud.google.com/apis/credentials'
                },
                {
                    'step': 3,
                    'description': f'Save credentials.json to {self.credentials_path}',
                    'note': 'Download and place the OAuth2 client JSON file'
                },
                {
                    'step': 4,
                    'description': 'Run first-time authentication',
                    'command': 'python -c "from integrations.google_slides import GoogleSlidesClient; GoogleSlidesClient()"'
                },
                {
                    'step': 5,
                    'description': 'Enable auto-generation in manifest',
                    'example': '{"google_slides": {"auto_generate": true}}'
                }
            ],
            'credentials_path': self.credentials_path,
            'credentials_exists': os.path.exists(self.credentials_path)
        }