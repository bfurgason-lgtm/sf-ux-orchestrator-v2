"""
PDF Exporter for Google Slides presentations.
Converts presentations to PDF format for distribution and archival.
"""
import os
import requests
from typing import Dict, Any, Optional
from .slides_client import GoogleSlidesClient

class PDFExporter:
    """Exports Google Slides presentations to PDF format."""
    
    def __init__(self, slides_client: GoogleSlidesClient):
        """Initialize PDF exporter with slides client."""
        self.client = slides_client
    
    def export_presentation_to_pdf(self, presentation_id: str, 
                                  output_path: str = None, 
                                  export_format: str = "pdf") -> Dict[str, Any]:
        """Export presentation to PDF file.
        
        Args:
            presentation_id: Google Slides presentation ID
            output_path: Local file path for PDF (optional)
            export_format: Export format ('pdf' or 'pptx')
            
        Returns:
            Export result with file path and metadata
        """
        if not output_path:
            # Generate default output path
            presentation = self.client.get_presentation(presentation_id)
            title = presentation.get('title', 'presentation')
            safe_title = self._sanitize_filename(title)
            output_path = f"{safe_title}.{export_format}"
        
        # Get export URL
        export_url = self._get_export_url(presentation_id, export_format)
        
        # Download the file
        try:
            response = requests.get(export_url, timeout=300)  # 5 minute timeout
            response.raise_for_status()
            
            # Save to file
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            # Get file size
            file_size = os.path.getsize(output_path)
            
            return {
                'success': True,
                'output_path': output_path,
                'file_size': file_size,
                'format': export_format,
                'presentation_id': presentation_id
            }
            
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f"Failed to download presentation: {str(e)}",
                'presentation_id': presentation_id
            }
        except IOError as e:
            return {
                'success': False,
                'error': f"Failed to save file: {str(e)}",
                'presentation_id': presentation_id
            }
    
    def export_to_drive_folder(self, presentation_id: str, 
                              drive_folder_path: str) -> Dict[str, Any]:
        """Export presentation and save to specified Drive folder.
        
        Args:
            presentation_id: Google Slides presentation ID
            drive_folder_path: Target folder path for export
            
        Returns:
            Export result with Drive file information
        """
        # Create local PDF first
        local_result = self.export_presentation_to_pdf(presentation_id)
        
        if not local_result['success']:
            return local_result
        
        try:
            # Move to Drive folder (requires Drive API integration)
            drive_path = os.path.join(drive_folder_path, os.path.basename(local_result['output_path']))
            
            # For now, just copy to the specified path
            # In production, this would use Drive API to upload
            os.makedirs(drive_folder_path, exist_ok=True)
            
            import shutil
            shutil.move(local_result['output_path'], drive_path)
            
            return {
                'success': True,
                'drive_path': drive_path,
                'local_path': drive_path,  # Same in this implementation
                'file_size': local_result['file_size'],
                'format': local_result['format'],
                'presentation_id': presentation_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to save to Drive folder: {str(e)}",
                'presentation_id': presentation_id
            }
    
    def batch_export_multiple_formats(self, presentation_id: str,
                                     formats: list = None,
                                     output_dir: str = None) -> Dict[str, Any]:
        """Export presentation in multiple formats.
        
        Args:
            presentation_id: Google Slides presentation ID
            formats: List of formats to export ('pdf', 'pptx', 'png')
            output_dir: Output directory for exported files
            
        Returns:
            Dictionary with results for each format
        """
        if formats is None:
            formats = ['pdf', 'pptx']
        
        if output_dir is None:
            output_dir = './exports'
        
        results = {}
        
        for fmt in formats:
            output_path = os.path.join(output_dir, f"presentation.{fmt}")
            
            if fmt in ['pdf', 'pptx']:
                result = self.export_presentation_to_pdf(presentation_id, output_path, fmt)
            elif fmt == 'png':
                result = self._export_slides_as_images(presentation_id, output_dir)
            else:
                result = {
                    'success': False,
                    'error': f"Unsupported format: {fmt}"
                }
            
            results[fmt] = result
        
        return results
    
    def _get_export_url(self, presentation_id: str, export_format: str) -> str:
        """Get Google Slides export URL for specified format."""
        base_url = f"https://docs.google.com/presentation/d/{presentation_id}/export"
        
        if export_format == 'pdf':
            return f"{base_url}/pdf"
        elif export_format == 'pptx':
            return f"{base_url}/pptx"
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
    
    def _export_slides_as_images(self, presentation_id: str, output_dir: str) -> Dict[str, Any]:
        """Export individual slides as PNG images."""
        try:
            presentation = self.client.get_presentation(presentation_id)
            slides = presentation.get('slides', [])
            
            exported_images = []
            
            for i, slide in enumerate(slides):
                slide_id = slide.get('objectId')
                image_url = f"https://docs.google.com/presentation/d/{presentation_id}/export/png?id={presentation_id}&pageid={slide_id}"
                
                # Download slide image
                response = requests.get(image_url, timeout=60)
                response.raise_for_status()
                
                # Save image
                image_path = os.path.join(output_dir, f"slide_{i+1:02d}.png")
                os.makedirs(output_dir, exist_ok=True)
                
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                
                exported_images.append({
                    'slide_number': i + 1,
                    'slide_id': slide_id,
                    'image_path': image_path,
                    'file_size': len(response.content)
                })
            
            return {
                'success': True,
                'exported_images': exported_images,
                'total_slides': len(slides),
                'output_directory': output_dir
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to export slide images: {str(e)}"
            }
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage."""
        # Remove or replace problematic characters
        import re
        # Keep alphanumeric, spaces, hyphens, underscores
        sanitized = re.sub(r'[^\w\s\-_.]', '', filename)
        # Replace spaces with underscores
        sanitized = re.sub(r'\s+', '_', sanitized)
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Trim underscores from ends
        sanitized = sanitized.strip('_')
        
        return sanitized or 'presentation'