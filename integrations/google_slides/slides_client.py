"""
Google Slides API client for the sf-ux-orchestrator.
Handles authentication and basic Slides API operations.
"""
import os
import json
from typing import Dict, List, Optional, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleSlidesClient:
    """Google Slides API client with authentication and presentation management."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/presentations',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    def __init__(self, credentials_path: str = None, token_path: str = None):
        """Initialize the Google Slides client.
        
        Args:
            credentials_path: Path to credentials.json from Google Cloud Console
            token_path: Path to store/retrieve token.json for authentication
        """
        self.credentials_path = credentials_path or os.path.join(
            os.path.dirname(__file__), 'credentials.json'
        )
        self.token_path = token_path or os.path.join(
            os.path.dirname(__file__), 'token.json'
        )
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Slides API using OAuth2."""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        # If no valid credentials, run OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Google credentials file not found at {self.credentials_path}. "
                        "Download from Google Cloud Console and place it here."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('slides', 'v1', credentials=creds)
    
    def create_presentation(self, title: str) -> Dict[str, Any]:
        """Create a new Google Slides presentation.
        
        Args:
            title: Title for the new presentation
            
        Returns:
            Presentation resource containing ID and metadata
        """
        try:
            body = {
                'title': title
            }
            presentation = self.service.presentations().create(body=body).execute()
            return presentation
        except HttpError as error:
            raise Exception(f"Failed to create presentation: {error}")
    
    def get_presentation(self, presentation_id: str) -> Dict[str, Any]:
        """Get presentation metadata and structure.
        
        Args:
            presentation_id: Google Slides presentation ID
            
        Returns:
            Presentation resource with slides and layout info
        """
        try:
            presentation = self.service.presentations().get(
                presentationId=presentation_id
            ).execute()
            return presentation
        except HttpError as error:
            raise Exception(f"Failed to get presentation {presentation_id}: {error}")
    
    def batch_update(self, presentation_id: str, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute batch updates to a presentation.
        
        Args:
            presentation_id: Target presentation ID
            requests: List of batch update request objects
            
        Returns:
            Batch update response with replies
        """
        try:
            body = {
                'requests': requests
            }
            response = self.service.presentations().batchUpdate(
                presentationId=presentation_id, body=body
            ).execute()
            return response
        except HttpError as error:
            raise Exception(f"Failed to update presentation {presentation_id}: {error}")
    
    def create_slide(self, presentation_id: str, slide_id: str = None, 
                    layout: str = "BLANK") -> str:
        """Create a new slide in the presentation.
        
        Args:
            presentation_id: Target presentation ID
            slide_id: Optional custom slide ID (auto-generated if None)
            layout: Slide layout type (BLANK, TITLE_AND_BODY, etc.)
            
        Returns:
            ID of the created slide
        """
        request = {
            'createSlide': {
                'slideLayoutReference': {
                    'predefinedLayout': layout
                }
            }
        }
        
        if slide_id:
            request['createSlide']['objectId'] = slide_id
        
        response = self.batch_update(presentation_id, [request])
        return response['replies'][0]['createSlide']['objectId']
    
    def add_text_box(self, presentation_id: str, slide_id: str, 
                     text: str, x: float, y: float, width: float, height: float,
                     font_size: int = 14) -> str:
        """Add a text box to a slide.
        
        Args:
            presentation_id: Target presentation ID
            slide_id: Target slide ID
            text: Text content
            x, y: Position in points (top-left origin)
            width, height: Size in points
            font_size: Font size in points
            
        Returns:
            Object ID of the created text box
        """
        text_box_id = f"text_box_{len(str(x))}{len(str(y))}"
        
        requests = [
            {
                'createShape': {
                    'objectId': text_box_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'height': {'magnitude': height, 'unit': 'PT'},
                            'width': {'magnitude': width, 'unit': 'PT'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': x,
                            'translateY': y,
                            'unit': 'PT'
                        }
                    }
                }
            },
            {
                'insertText': {
                    'objectId': text_box_id,
                    'insertionIndex': 0,
                    'text': text
                }
            },
            {
                'updateTextStyle': {
                    'objectId': text_box_id,
                    'style': {
                        'fontSize': {
                            'magnitude': font_size,
                            'unit': 'PT'
                        }
                    },
                    'fields': 'fontSize'
                }
            }
        ]
        
        self.batch_update(presentation_id, requests)
        return text_box_id
    
    def add_shape(self, presentation_id: str, slide_id: str, shape_type: str,
                  x: float, y: float, width: float, height: float,
                  fill_color: str = None) -> str:
        """Add a shape to a slide.
        
        Args:
            presentation_id: Target presentation ID
            slide_id: Target slide ID
            shape_type: RECTANGLE, ELLIPSE, DIAMOND, etc.
            x, y: Position in points
            width, height: Size in points
            fill_color: Hex color (e.g., '#FF0000')
            
        Returns:
            Object ID of the created shape
        """
        shape_id = f"shape_{shape_type.lower()}_{len(str(x))}{len(str(y))}"
        
        request = {
            'createShape': {
                'objectId': shape_id,
                'shapeType': shape_type,
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'height': {'magnitude': height, 'unit': 'PT'},
                        'width': {'magnitude': width, 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': x,
                        'translateY': y,
                        'unit': 'PT'
                    }
                }
            }
        }
        
        requests = [request]
        
        # Add fill color if specified
        if fill_color:
            color_request = {
                'updateShapeProperties': {
                    'objectId': shape_id,
                    'shapeProperties': {
                        'shapeBackgroundFill': {
                            'solidFill': {
                                'color': {
                                    'rgbColor': self._hex_to_rgb(fill_color)
                                }
                            }
                        }
                    },
                    'fields': 'shapeBackgroundFill'
                }
            }
            requests.append(color_request)
        
        self.batch_update(presentation_id, requests)
        return shape_id
    
    def connect_shapes(self, presentation_id: str, slide_id: str,
                      start_shape_id: str, end_shape_id: str,
                      line_type: str = "STRAIGHT_CONNECTOR_1") -> str:
        """Connect two shapes with a line/arrow.
        
        Args:
            presentation_id: Target presentation ID
            slide_id: Target slide ID
            start_shape_id: Starting shape object ID
            end_shape_id: Ending shape object ID
            line_type: Connector line type
            
        Returns:
            Object ID of the created line
        """
        line_id = f"line_{start_shape_id}_{end_shape_id}"
        
        request = {
            'createLine': {
                'objectId': line_id,
                'lineCategory': 'CONNECTOR',
                'elementProperties': {
                    'pageObjectId': slide_id
                },
                'connectorType': line_type,
                'startConnection': {
                    'connectedObjectId': start_shape_id
                },
                'endConnection': {
                    'connectedObjectId': end_shape_id
                }
            }
        }
        
        self.batch_update(presentation_id, [request])
        return line_id
    
    def _hex_to_rgb(self, hex_color: str) -> Dict[str, float]:
        """Convert hex color to RGB dict for Google Slides API.
        
        Args:
            hex_color: Hex color string (e.g., '#FF0000')
            
        Returns:
            RGB color dict with red, green, blue values (0-1)
        """
        hex_color = hex_color.lstrip('#')
        return {
            'red': int(hex_color[0:2], 16) / 255.0,
            'green': int(hex_color[2:4], 16) / 255.0,
            'blue': int(hex_color[4:6], 16) / 255.0
        }
    
    def get_presentation_url(self, presentation_id: str) -> str:
        """Get the shareable URL for a presentation.
        
        Args:
            presentation_id: Google Slides presentation ID
            
        Returns:
            Shareable presentation URL
        """
        return f"https://docs.google.com/presentation/d/{presentation_id}/edit"