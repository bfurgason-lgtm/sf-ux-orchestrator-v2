"""
Screen Validator for Figma Generation Quality Assurance.
Validates template matching, screen completeness, and visual fidelity.
"""
import json
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ScreenValidator:
    """Validates generated Figma screens against template specifications."""
    
    def __init__(self, template_spec_path: str = None):
        """Initialize with template specifications."""
        self.template_spec_path = template_spec_path or "core/templates/web_template_spec.json"
        self.template_specs = self._load_template_specs()
        self.validation_results = []
        
    def _load_template_specs(self) -> Dict[str, Any]:
        """Load template specifications from JSON file."""
        try:
            with open(self.template_spec_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load template specs: {e}")
            return {}
    
    def validate_generation_result(self, generation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate complete generation result against specifications."""
        validation_report = {
            "timestamp": datetime.now().isoformat(),
            "validation_status": "pending",
            "template_fidelity_score": 0,
            "checks_performed": [],
            "issues_found": [],
            "recommendations": []
        }
        
        # Check 1: Screen Count Validation
        screen_count_check = self._validate_screen_count(generation_result)
        validation_report["checks_performed"].append(screen_count_check)
        
        # Check 2: Template Color Validation 
        color_check = self._validate_template_colors(generation_result)
        validation_report["checks_performed"].append(color_check)
        
        # Check 3: Font Loading Validation
        font_check = self._validate_font_loading(generation_result)
        validation_report["checks_performed"].append(font_check)
        
        # Check 4: Screen Structure Validation
        structure_check = self._validate_screen_structure(generation_result)
        validation_report["checks_performed"].append(structure_check)
        
        # Calculate overall validation score
        passed_checks = [check for check in validation_report["checks_performed"] if check["passed"]]
        total_checks = len(validation_report["checks_performed"])
        validation_report["template_fidelity_score"] = (len(passed_checks) / total_checks) * 100 if total_checks > 0 else 0
        
        # Determine overall status
        if validation_report["template_fidelity_score"] >= 95:
            validation_report["validation_status"] = "excellent"
        elif validation_report["template_fidelity_score"] >= 85:
            validation_report["validation_status"] = "good"
        elif validation_report["template_fidelity_score"] >= 70:
            validation_report["validation_status"] = "acceptable"
        else:
            validation_report["validation_status"] = "needs_improvement"
        
        # Collect issues and recommendations
        for check in validation_report["checks_performed"]:
            if not check["passed"]:
                validation_report["issues_found"].extend(check.get("issues", []))
            validation_report["recommendations"].extend(check.get("recommendations", []))
        
        self.validation_results.append(validation_report)
        return validation_report
    
    def _validate_screen_count(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that the correct number of screens were created."""
        expected_screens = 4  # WISMO web flow
        actual_screens = result.get('screensCreated', 0)
        
        check_result = {
            "check_name": "Screen Count Validation",
            "passed": actual_screens == expected_screens,
            "details": {
                "expected": expected_screens,
                "actual": actual_screens,
                "difference": abs(expected_screens - actual_screens)
            },
            "issues": [],
            "recommendations": []
        }
        
        if not check_result["passed"]:
            check_result["issues"].append(f"Screen count mismatch: expected {expected_screens}, got {actual_screens}")
            if actual_screens < expected_screens:
                check_result["recommendations"].append("Regenerate missing screens with proper error handling")
            else:
                check_result["recommendations"].append("Remove extra screens to match specification")
        
        return check_result
    
    def _validate_template_colors(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that template colors match specifications exactly."""
        template_specs = result.get('templateSpecs', {})
        expected_colors = self.template_specs.get('visual_specifications', {})
        
        check_result = {
            "check_name": "Template Color Validation",
            "passed": True,
            "details": {
                "colors_checked": [],
                "color_matches": []
            },
            "issues": [],
            "recommendations": []
        }
        
        # Check background color
        if 'backgroundUsed' in template_specs and 'background' in expected_colors:
            expected_bg = expected_colors['background']['color_rgb']
            actual_bg = template_specs['backgroundUsed']
            
            bg_match = self._colors_match(expected_bg, actual_bg)
            check_result["details"]["colors_checked"].append("background")
            check_result["details"]["color_matches"].append(bg_match)
            
            if not bg_match:
                check_result["passed"] = False
                check_result["issues"].append(f"Background color mismatch: expected {expected_bg}, got {actual_bg}")
        
        # Check agent bubble color
        if 'agentBubbleColor' in template_specs and 'agent_bubble' in expected_colors:
            expected_agent = expected_colors['agent_bubble']['color_rgb']
            actual_agent = template_specs['agentBubbleColor']
            
            agent_match = self._colors_match(expected_agent, actual_agent)
            check_result["details"]["colors_checked"].append("agent_bubble")
            check_result["details"]["color_matches"].append(agent_match)
            
            if not agent_match:
                check_result["passed"] = False
                check_result["issues"].append(f"Agent bubble color mismatch: expected {expected_agent}, got {actual_agent}")
        
        # Check user bubble color
        if 'userBubbleColor' in template_specs and 'user_bubble' in expected_colors:
            expected_user = expected_colors['user_bubble']['color_rgb']
            actual_user = template_specs['userBubbleColor']
            
            user_match = self._colors_match(expected_user, actual_user)
            check_result["details"]["colors_checked"].append("user_bubble")
            check_result["details"]["color_matches"].append(user_match)
            
            if not user_match:
                check_result["passed"] = False
                check_result["issues"].append(f"User bubble color mismatch: expected {expected_user}, got {actual_user}")
        
        if not check_result["passed"]:
            check_result["recommendations"].append("Update color specifications to match template exactly")
            check_result["recommendations"].append("Verify RGB color conversion from hex values")
        
        return check_result
    
    def _validate_font_loading(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that fonts were loaded successfully."""
        validation_data = result.get('validation', {})
        fonts_loaded = validation_data.get('fontsLoaded', 0)
        expected_fonts = 3  # Inter Regular, Medium, Bold
        
        check_result = {
            "check_name": "Font Loading Validation",
            "passed": fonts_loaded >= expected_fonts,
            "details": {
                "fonts_loaded": fonts_loaded,
                "expected_fonts": expected_fonts,
                "loading_success_rate": (fonts_loaded / expected_fonts) * 100 if expected_fonts > 0 else 0
            },
            "issues": [],
            "recommendations": []
        }
        
        if not check_result["passed"]:
            check_result["issues"].append(f"Font loading incomplete: {fonts_loaded}/{expected_fonts} fonts loaded")
            check_result["recommendations"].append("Implement font loading retry mechanism")
            check_result["recommendations"].append("Add fallback font specifications")
        
        return check_result
    
    def _validate_screen_structure(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that screens have proper structure and naming."""
        screens = result.get('screens', [])
        expected_screens = [
            "WEB-01: Initial Greeting",
            "WEB-02: Information Collection", 
            "WEB-03: Order Processing",
            "WEB-04: Follow-up Services"
        ]
        
        check_result = {
            "check_name": "Screen Structure Validation",
            "passed": True,
            "details": {
                "screens_found": [screen.get('name', 'Unnamed') for screen in screens],
                "naming_matches": [],
                "structure_score": 0
            },
            "issues": [],
            "recommendations": []
        }
        
        # Check screen naming
        for i, expected_name in enumerate(expected_screens):
            if i < len(screens):
                actual_name = screens[i].get('name', '')
                name_match = actual_name == expected_name
                check_result["details"]["naming_matches"].append(name_match)
                
                if not name_match:
                    check_result["passed"] = False
                    check_result["issues"].append(f"Screen {i+1} naming mismatch: expected '{expected_name}', got '{actual_name}'")
            else:
                check_result["passed"] = False
                check_result["issues"].append(f"Missing screen: '{expected_name}'")
        
        # Calculate structure score
        matches = sum(check_result["details"]["naming_matches"])
        check_result["details"]["structure_score"] = (matches / len(expected_screens)) * 100
        
        if not check_result["passed"]:
            check_result["recommendations"].append("Ensure consistent screen naming convention")
            check_result["recommendations"].append("Verify screen generation order matches specification")
        
        return check_result
    
    def _colors_match(self, expected: Dict[str, float], actual: Dict[str, float], tolerance: float = 0.01) -> bool:
        """Check if two RGB color values match within tolerance."""
        if not expected or not actual:
            return False
        
        r_match = abs(expected.get('r', 0) - actual.get('r', 0)) <= tolerance
        g_match = abs(expected.get('g', 0) - actual.get('g', 0)) <= tolerance 
        b_match = abs(expected.get('b', 0) - actual.get('b', 0)) <= tolerance
        
        return r_match and g_match and b_match
    
    def validate_reference_fidelity(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate results against the reference screenshot requirements."""
        
        check_result = {
            "check_name": "Reference Screenshot Fidelity",
            "passed": True,
            "details": {
                "mobile_frames": False,
                "agent_avatars": False,
                "authentic_styling": False,
                "professional_layout": False
            },
            "issues": [],
            "recommendations": []
        }
        
        # Check for reference-specific features
        features = result.get('features', [])
        template_version = result.get('templateVersion', '1.0')
        reference_matched = result.get('referenceMatched', False)
        
        # Validate mobile frames
        if 'mobile_frames' in features:
            check_result["details"]["mobile_frames"] = True
        else:
            check_result["passed"] = False
            check_result["issues"].append("Missing mobile device frames - reference shows iPhone-style mockups")
        
        # Validate agent avatars
        if 'agent_avatars' in features:
            check_result["details"]["agent_avatars"] = True
        else:
            check_result["passed"] = False
            check_result["issues"].append("Missing agent avatars - reference shows dark circular avatars for all agent messages")
        
        # Validate authentic styling
        if 'authentic_styling' in features and 'precise_bubbles' in features:
            check_result["details"]["authentic_styling"] = True
        else:
            check_result["passed"] = False
            check_result["issues"].append("Styling doesn't match reference - need precise bubble styling and authentic appearance")
        
        # Validate professional layout
        if template_version == '2.0' and reference_matched:
            check_result["details"]["professional_layout"] = True
        else:
            check_result["passed"] = False
            check_result["issues"].append("Layout doesn't match reference professional standard")
        
        # Add recommendations if issues found
        if not check_result["passed"]:
            check_result["recommendations"].extend([
                "Ensure mobile device frames are implemented with proper iPhone styling",
                "Add dark circular avatars for all agent messages",
                "Match exact bubble styling from reference screenshot", 
                "Use template version 2.0 with reference-matched specifications"
            ])
        
        return check_result
    
    def calculate_reference_accuracy_score(self, result: Dict[str, Any]) -> float:
        """Calculate accuracy score against reference screenshot."""
        
        # Base scoring criteria
        scoring_criteria = {
            'mobile_frames': 25,      # Professional device mockups
            'agent_avatars': 25,      # Dark circular avatars  
            'precise_bubbles': 20,    # Exact bubble styling
            'authentic_styling': 15,  # Overall authentic appearance
            'template_v2': 10,        # Updated template version
            'reference_matched': 5    # Reference matching flag
        }
        
        score = 0
        features = result.get('features', [])
        
        # Check each criterion
        if 'mobile_frames' in features:
            score += scoring_criteria['mobile_frames']
        
        if 'agent_avatars' in features:
            score += scoring_criteria['agent_avatars']
            
        if 'precise_bubbles' in features:
            score += scoring_criteria['precise_bubbles']
            
        if 'authentic_styling' in features:
            score += scoring_criteria['authentic_styling']
            
        if result.get('templateVersion') == '2.0':
            score += scoring_criteria['template_v2']
            
        if result.get('referenceMatched', False):
            score += scoring_criteria['reference_matched']
        
        return min(score, 100)  # Cap at 100%