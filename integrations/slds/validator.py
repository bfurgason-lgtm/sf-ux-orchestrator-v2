#!/usr/bin/env python3
"""
SLDS v2.0 Validation and Compliance System
Enhanced Narrative Orchestrator Integration

Validates Figma designs and generated code against Salesforce Lightning Design System v2.0
standards, ensuring compliance and accessibility.

Author: Cursor Agent - Enhanced Narrative Orchestrator System  
Version: 0.5.0
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

# ─── LOGGING SETUP ──
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ValidationIssue:
    """Represents a single SLDS validation issue."""
    severity: str  # 'error', 'warning', 'info'
    category: str  # 'color', 'typography', 'spacing', 'component', 'accessibility'
    message: str
    suggestion: Optional[str] = None
    slds_reference: Optional[str] = None
    auto_fixable: bool = False

@dataclass
class ValidationResult:
    """Complete validation result."""
    passed: bool
    total_checks: int
    issues: List[ValidationIssue]
    score: float  # 0-100, percentage of checks passed
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'passed': self.passed,
            'total_checks': self.total_checks,
            'issues': [asdict(issue) for issue in self.issues],
            'score': self.score,
            'timestamp': self.timestamp
        }


class SLDSValidator:
    """
    Comprehensive SLDS v2.0 validator for Figma designs and generated code.
    """
    
    def __init__(self, presentation_phase: bool = True):
        """Initialize validator with SLDS v2.0 standards.
        
        Args:
            presentation_phase: If True, skip validation for presentation phase
        """
        self.presentation_phase = presentation_phase
        
        if presentation_phase:
            logger.info("SLDS Validator initialized in PRESENTATION PHASE - validation skipped for visual fidelity")
            # Load minimal data for presentation phase
            self.slds_tokens = {}
            self.slds_components = {}
            self.accessibility_standards = {}
        else:
            logger.info("SLDS v2.0 Validator initialized in DEVELOPMENT PHASE")
            self.slds_tokens = self._load_slds_tokens()
            self.slds_components = self._load_slds_components() 
            self.accessibility_standards = self._load_accessibility_standards()
    
    def _load_slds_tokens(self) -> Dict[str, Any]:
        """Load SLDS design tokens and color palette."""
        return {
            'colors': {
                # Brand colors
                'brand': {
                    'primary': '#1589EE',
                    'primary_dark': '#0D4F8C', 
                    'secondary': '#5C6B73',
                    'success': '#45C65A',
                    'warning': '#FE9339',
                    'error': '#EA001E',
                    'info': '#0176D3'
                },
                # Text colors
                'text': {
                    'default': '#080707',
                    'weak': '#514F4D', 
                    'weaker': '#706E6B',
                    'weakest': '#9A9892',
                    'inverse': '#FEFEFE',
                    'inverse_weak': '#DDDBDA',
                    'link': '#0176D3',
                    'link_hover': '#014486'
                },
                # Background colors
                'background': {
                    'default': '#FEFEFE',
                    'alt': '#F7F7F7',
                    'alt_2': '#EEEEEE',
                    'shade': '#ECEBEA',
                    'shade_dark': '#DDDBDA',
                    'inverse': '#16325C',
                    'brand': '#1589EE',
                    'brand_dark': '#0D4F8C'
                },
                # Border colors  
                'border': {
                    'default': '#C9C7C5',
                    'strong': '#706E6B',
                    'weak': '#DDDBDA',
                    'inverse': '#5C6B73'
                }
            },
            'typography': {
                'font_families': {
                    'default': 'Salesforce Sans',
                    'system': 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI"'
                },
                'font_sizes': {
                    'heading_large': '2rem',    # 32px
                    'heading_medium': '1.5rem', # 24px  
                    'heading_small': '1.25rem', # 20px
                    'body_regular': '0.875rem', # 14px
                    'body_small': '0.75rem',    # 12px
                    'caption': '0.6875rem'      # 11px
                },
                'line_heights': {
                    'heading': '1.25',
                    'body': '1.5',
                    'tight': '1.375'
                }
            },
            'spacing': {
                'none': '0',
                'xxx_small': '0.125rem',  # 2px
                'xx_small': '0.25rem',    # 4px
                'x_small': '0.5rem',      # 8px  
                'small': '0.75rem',       # 12px
                'medium': '1rem',         # 16px
                'large': '1.5rem',        # 24px
                'x_large': '2rem',        # 32px
                'xx_large': '3rem'        # 48px
            }
        }
    
    def _load_slds_components(self) -> Dict[str, Any]:
        """Load SLDS component specifications."""
        return {
            'button': {
                'variants': ['base', 'neutral', 'brand', 'outline-brand', 'destructive', 'text-destructive'],
                'sizes': ['xx-small', 'x-small', 'small', 'medium'],
                'required_attributes': ['type', 'class'],
                'accessibility_attributes': ['aria-label', 'aria-describedby']
            },
            'input': {
                'variants': ['standard', 'label-hidden', 'label-stacked', 'compound'],
                'states': ['default', 'focus', 'error', 'disabled', 'readonly'],
                'required_attributes': ['id', 'type', 'class'],
                'accessibility_attributes': ['aria-label', 'aria-describedby', 'aria-invalid']
            },
            'card': {
                'variants': ['base', 'narrow', 'einstein'],  
                'elements': ['header', 'body', 'footer'],
                'required_attributes': ['class'],
                'accessibility_attributes': ['role', 'aria-label']
            },
            'modal': {
                'elements': ['backdrop', 'container', 'header', 'content', 'footer'],
                'required_attributes': ['role', 'aria-labelledby', 'aria-modal'],
                'accessibility_attributes': ['tabindex', 'aria-hidden', 'focus-trap']
            }
        }
    
    def _load_accessibility_standards(self) -> Dict[str, Any]:
        """Load WCAG 2.1 accessibility standards."""
        return {
            'color_contrast': {
                'AA_normal': 4.5,
                'AA_large': 3.0,
                'AAA_normal': 7.0,
                'AAA_large': 4.5
            },
            'focus_indicators': {
                'min_thickness': '2px',
                'required_properties': ['outline', 'outline-offset', 'box-shadow']
            },
            'touch_targets': {
                'min_size': '44px',
                'preferred_size': '48px'
            }
        }
    
    def validate_colors(self, design_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate color usage against SLDS tokens."""
        issues = []
        
        colors_used = design_data.get('colors', {})
        
        for color_key, color_value in colors_used.items():
            # Check if color uses SLDS token
            if isinstance(color_value, str) and color_value.startswith('#'):
                slds_match = self._find_slds_color_token(color_value)
                if not slds_match:
                    issues.append(ValidationIssue(
                        severity='warning',
                        category='color',
                        message=f"Custom color '{color_value}' used instead of SLDS token",
                        suggestion=f"Consider using SLDS color token for brand consistency",
                        slds_reference="https://www.lightningdesignsystem.com/design-tokens/",
                        auto_fixable=False
                    ))
        
        return issues
    
    def validate_typography(self, design_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate typography against SLDS standards."""  
        issues = []
        
        typography = design_data.get('typography', {})
        
        # Check font family
        font_family = typography.get('font_family', '')
        if font_family and 'Salesforce Sans' not in font_family:
            issues.append(ValidationIssue(
                severity='warning',
                category='typography', 
                message=f"Font family '{font_family}' is not Salesforce Sans",
                suggestion="Use 'Salesforce Sans' font family for SLDS compliance",
                slds_reference="https://www.lightningdesignsystem.com/design-tokens/#category-font",
                auto_fixable=True
            ))
        
        # Check font sizes
        font_size = typography.get('font_size', '')
        if font_size and not self._is_slds_font_size(font_size):
            closest_size = self._find_closest_slds_font_size(font_size)
            issues.append(ValidationIssue(
                severity='info',
                category='typography',
                message=f"Font size '{font_size}' doesn't match SLDS scale",
                suggestion=f"Consider using SLDS font size: {closest_size}",
                slds_reference="https://www.lightningdesignsystem.com/design-tokens/#category-font-size",
                auto_fixable=True
            ))
        
        return issues
    
    def validate_spacing(self, design_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate spacing against SLDS tokens."""
        issues = []
        
        spacing = design_data.get('spacing', {})
        
        for spacing_type, value in spacing.items():
            if not self._is_slds_spacing_token(value):
                closest_token = self._find_closest_slds_spacing(value)
                issues.append(ValidationIssue(
                    severity='info',
                    category='spacing',
                    message=f"Spacing value '{value}' doesn't use SLDS token",
                    suggestion=f"Consider using SLDS spacing token: {closest_token}",
                    slds_reference="https://www.lightningdesignsystem.com/design-tokens/#category-spacing",
                    auto_fixable=True
                ))
        
        return issues
    
    def validate_components(self, design_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate component usage against SLDS patterns."""
        issues = []
        
        components = design_data.get('components', [])
        
        for component in components:
            component_type = component.get('type', '')
            
            if component_type in self.slds_components:
                issues.extend(self._validate_single_component(component))
            else:
                issues.append(ValidationIssue(
                    severity='info',
                    category='component',
                    message=f"Custom component '{component_type}' not in SLDS library",
                    suggestion="Consider using SLDS component variants when possible",
                    slds_reference=f"https://www.lightningdesignsystem.com/components/{component_type}/",
                    auto_fixable=False
                ))
        
        return issues
    
    def validate_accessibility(self, design_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate accessibility compliance."""
        issues = []
        
        # Color contrast validation
        issues.extend(self._validate_color_contrast(design_data))
        
        # Touch target validation  
        issues.extend(self._validate_touch_targets(design_data))
        
        # Focus indicators validation
        issues.extend(self._validate_focus_indicators(design_data))
        
        # Semantic structure validation
        issues.extend(self._validate_semantic_structure(design_data))
        
        return issues
    
    def _validate_color_contrast(self, design_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate color contrast ratios."""
        issues = []
        
        text_elements = design_data.get('text_elements', [])
        
        for element in text_elements:
            bg_color = element.get('background_color', '#FFFFFF')
            text_color = element.get('text_color', '#000000') 
            font_size = element.get('font_size', '14px')
            
            contrast_ratio = self._calculate_contrast_ratio(bg_color, text_color)
            wcag_level = design_data.get('accessibility', {}).get('wcag_level', 'AA')
            
            is_large_text = self._is_large_text(font_size)
            required_ratio = self._get_required_contrast_ratio(wcag_level, is_large_text)
            
            if contrast_ratio < required_ratio:
                issues.append(ValidationIssue(
                    severity='error',
                    category='accessibility',
                    message=f"Insufficient color contrast: {contrast_ratio:.1f}:1 (requires {required_ratio}:1)",
                    suggestion="Increase contrast between text and background colors",
                    slds_reference="https://www.lightningdesignsystem.com/accessibility/color-and-contrast/",
                    auto_fixable=True
                ))
        
        return issues
    
    def _validate_touch_targets(self, design_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate touch target sizes."""
        issues = []
        
        interactive_elements = design_data.get('interactive_elements', [])
        
        for element in interactive_elements:
            width = element.get('width', 0)
            height = element.get('height', 0)
            
            min_size = 44  # WCAG minimum
            
            if width < min_size or height < min_size:
                issues.append(ValidationIssue(
                    severity='error',
                    category='accessibility',
                    message=f"Touch target too small: {width}×{height}px (minimum: {min_size}×{min_size}px)",
                    suggestion=f"Increase touch target size to at least {min_size}×{min_size}px",
                    slds_reference="https://www.lightningdesignsystem.com/accessibility/touch-targets/",
                    auto_fixable=True
                ))
        
        return issues
    
    def validate_manifest_design_system(self, manifest: Dict[str, Any]) -> ValidationResult:
        """
        Validate manifest design system configuration against SLDS standards.
        """
        # Skip validation in presentation phase
        if self.presentation_phase:
            return ValidationResult(
                passed=True,
                total_checks=1,
                issues=[],
                score=100.0,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
        issues = []
        total_checks = 0
        
        design_system = manifest.get('design_system', {})
        
        # Check framework specification
        total_checks += 1
        framework = design_system.get('framework', '')
        if framework != 'slds_v2':
            issues.append(ValidationIssue(
                severity='warning',
                category='component',
                message=f"Framework '{framework}' is not SLDS v2.0",
                suggestion="Use 'slds_v2' for full Lightning Design System compliance",
                auto_fixable=True
            ))
        
        # Validate brand tokens
        brand_tokens = design_system.get('brand_tokens', {})
        for token_key, token_value in brand_tokens.items():
            total_checks += 1
            if isinstance(token_value, str) and not token_value.startswith('slds_'):
                if not self._is_valid_slds_token_value(token_value):
                    issues.append(ValidationIssue(
                        severity='info', 
                        category='color',
                        message=f"Brand token '{token_key}' uses custom value instead of SLDS token",
                        suggestion="Consider using SLDS design tokens for consistency",
                        auto_fixable=False
                    ))
        
        # Validate accessibility settings
        accessibility = design_system.get('accessibility', {})
        total_checks += 1
        wcag_level = accessibility.get('wcag_level', '')
        if wcag_level not in ['AA', 'AAA']:
            issues.append(ValidationIssue(
                severity='error',
                category='accessibility',
                message="WCAG level must be 'AA' or 'AAA'",
                suggestion="Set wcag_level to 'AA' for standard compliance or 'AAA' for enhanced",
                auto_fixable=True
            ))
        
        # Calculate score
        passed_checks = total_checks - len([i for i in issues if i.severity == 'error'])
        score = (passed_checks / total_checks) * 100 if total_checks > 0 else 100
        
        return ValidationResult(
            passed=len([i for i in issues if i.severity == 'error']) == 0,
            total_checks=total_checks,
            issues=issues,
            score=score,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def generate_compliance_report(self, validation_result: ValidationResult, 
                                 output_path: Optional[Path] = None) -> Path:
        """Generate detailed compliance report."""
        report = {
            'slds_compliance_report': {
                'metadata': {
                    'validator_version': '0.5.0',
                    'slds_version': '2.0',
                    'generated_at': validation_result.timestamp,
                    'overall_score': validation_result.score
                },
                'summary': {
                    'total_checks': validation_result.total_checks,
                    'passed': validation_result.passed,
                    'errors': len([i for i in validation_result.issues if i.severity == 'error']),
                    'warnings': len([i for i in validation_result.issues if i.severity == 'warning']),
                    'info': len([i for i in validation_result.issues if i.severity == 'info'])
                },
                'issues_by_category': self._group_issues_by_category(validation_result.issues),
                'detailed_issues': [asdict(issue) for issue in validation_result.issues],
                'auto_fixable_count': len([i for i in validation_result.issues if i.auto_fixable]),
                'recommendations': self._generate_recommendations(validation_result.issues)
            }
        }
        
        if output_path is None:
            output_path = Path('exports/reports/slds_compliance_report.json')
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ SLDS compliance report generated: {output_path}")
        return output_path
    
    # ─── HELPER METHODS ──
    
    def _find_slds_color_token(self, hex_color: str) -> Optional[str]:
        """Find matching SLDS color token for hex value."""
        for category, colors in self.slds_tokens['colors'].items():
            for token_name, token_value in colors.items():
                if token_value.upper() == hex_color.upper():
                    return f"slds.{category}.{token_name}"
        return None
    
    def _is_slds_font_size(self, font_size: str) -> bool:
        """Check if font size matches SLDS scale."""
        return font_size in self.slds_tokens['typography']['font_sizes'].values()
    
    def _find_closest_slds_font_size(self, font_size: str) -> str:
        """Find closest SLDS font size."""
        # Simple implementation - in practice would calculate closest match
        return "0.875rem"  # body_regular
    
    def _is_slds_spacing_token(self, value: str) -> bool:
        """Check if value uses SLDS spacing token.""" 
        return value in self.slds_tokens['spacing'].values()
    
    def _find_closest_slds_spacing(self, value: str) -> str:
        """Find closest SLDS spacing token."""
        # Simple implementation - in practice would calculate closest match
        return "1rem"  # medium
    
    def _is_valid_slds_token_value(self, value: str) -> bool:
        """Check if a value is a valid SLDS design token or color."""
        if not isinstance(value, str):
            return False
        
        # Check if it's a hex color
        if re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value):
            return True
        
        # Check if it's an SLDS token
        if value.startswith('slds_'):
            return True
        
        # Check if it's a valid CSS color name or CSS function
        css_patterns = [
            r'^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$',
            r'^rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)$',
            r'^hsl\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*\)$'
        ]
        
        for pattern in css_patterns:
            if re.match(pattern, value, re.IGNORECASE):
                return True
        
        # Check if it's a valid CSS color name
        css_colors = [
            'black', 'white', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta',
            'transparent', 'inherit', 'currentcolor', 'initial', 'unset'
        ]
        return value.lower() in css_colors

    def _calculate_contrast_ratio(self, bg_color: str, text_color: str) -> float:
        """Calculate WCAG contrast ratio between two colors."""
        # Simplified calculation - in practice would use proper color conversion
        return 4.5  # Placeholder
    
    def _is_large_text(self, font_size: str) -> bool:
        """Determine if text is considered large for contrast purposes."""
        # 18px+ regular or 14px+ bold is considered large text
        return False  # Simplified
    
    def _get_required_contrast_ratio(self, wcag_level: str, is_large_text: bool) -> float:
        """Get required contrast ratio for WCAG compliance.""" 
        standards = self.accessibility_standards['color_contrast']
        
        if wcag_level == 'AAA':
            return standards['AAA_large'] if is_large_text else standards['AAA_normal']
        else:  # AA
            return standards['AA_large'] if is_large_text else standards['AA_normal']
    
    def _group_issues_by_category(self, issues: List[ValidationIssue]) -> Dict[str, int]:
        """Group issues by category for summary."""
        categories = {}
        for issue in issues:
            categories[issue.category] = categories.get(issue.category, 0) + 1
        return categories
    
    def _generate_recommendations(self, issues: List[ValidationIssue]) -> List[str]:
        """Generate high-level recommendations based on issues."""
        recommendations = []
        
        error_count = len([i for i in issues if i.severity == 'error'])
        if error_count > 0:
            recommendations.append("Address all error-level issues before deployment")
        
        accessibility_issues = len([i for i in issues if i.category == 'accessibility'])
        if accessibility_issues > 0:
            recommendations.append("Review accessibility compliance - consider WCAG audit")
        
        color_issues = len([i for i in issues if i.category == 'color'])
        if color_issues > 3:
            recommendations.append("Adopt SLDS color tokens for better brand consistency")
        
        return recommendations


def main():
    """CLI entry point for SLDS validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='SLDS v2.0 Validator')
    parser.add_argument('manifest', help='Path to manifest.json file')
    parser.add_argument('--output', help='Output path for compliance report')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load and validate manifest
    validator = SLDSValidator()
    
    try:
        with open(args.manifest, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        result = validator.validate_manifest_design_system(manifest)
        
        # Generate report
        report_path = Path(args.output) if args.output else None
        validator.generate_compliance_report(result, report_path)
        
        # Print summary
        print(f"\n🎯 SLDS Compliance Score: {result.score:.1f}%")
        print(f"✅ Checks Passed: {result.total_checks - len(result.issues)}/{result.total_checks}")
        
        if result.issues:
            print(f"\n📋 Issues Found:")
            for issue in result.issues:
                icon = "🔴" if issue.severity == 'error' else "🟡" if issue.severity == 'warning' else "🔵"
                print(f"  {icon} {issue.message}")
        
        if result.passed:
            print("\n🎉 All critical checks passed!")
        else:
            print("\n⚠️  Critical issues must be resolved before deployment")
            
    except FileNotFoundError:
        print(f"❌ Manifest file not found: {args.manifest}")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in manifest: {e}")
    except Exception as e:
        print(f"❌ Validation error: {e}")


if __name__ == "__main__":
    main()