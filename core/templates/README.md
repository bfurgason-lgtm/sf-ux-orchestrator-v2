# Enhanced Narrative Orchestrator Template Library

This library contains production-ready channel templates based on authentic user experience designs from the Wolverine engagement. All templates prioritize visual appeal and user engagement while maintaining SLDS 2.0 compliance where applicable.

## Template Philosophy

**Exact Visual Fidelity**: The primary goal is creating designs that exactly match the provided user examples. Visual authenticity and stakeholder recognition take absolute priority. SLDS compliance is reserved for the development phase - presentation phase focuses purely on matching the intended user experience.

## Channel Templates

### Web Templates (`web/`)
- **Framework**: Authentic Chatbot Interface (matching provided examples)
- **Base Design**: Real-time chat conversation with message bubbles
- **Key Features**: Natural conversation flow, authentic UI chrome, user-friendly interactions
- **Visual Priority**: Exact match to provided chatbot design examples

### Email Templates (`email/`)
- **Framework**: Responsive Email Thread
- **Base Design**: Authentic email client appearance
- **Key Features**: Realistic headers, conversation threading, branded signatures
- **Compatibility**: Multi-client responsive design

### SMS Templates (`sms/`)
- **Framework**: Native Mobile Interface
- **Base Design**: Authentic messaging app appearance
- **Key Features**: Message bubbles, status indicators, mobile UI chrome
- **Optimization**: Character limits and mobile UX patterns

### Voice Templates (`voice/`)
- **Framework**: Conversational AI Dialogue
- **Base Design**: Natural conversation flow patterns
- **Key Features**: Greeting scripts, confirmation patterns, error handling

## Usage

Templates are referenced in manifests through the `template` field in channel definitions:

```json
{
  "channels": {
    "web": {
      "template": "slds_agentforce_success",
      "slds_patterns": ["success-banner", "data-card"]
    },
    "email": {
      "template": "transactional_thread", 
      "template_type": "transactional"
    },
    "sms": {
      "template": "conversation_thread"
    }
  }
}
```

## Quality Standards

All templates meet these presentation requirements:
- ✅ Exact visual match to provided examples (>90% fidelity)
- ✅ Authentic, engaging user experience
- ✅ Stakeholder-ready appearance
- ✅ Channel-appropriate interaction patterns
- ✅ No further refinement needed for presentations

Note: SLDS compliance and accessibility requirements are handled in the development phase.

## Template Structure

Each template includes:
- `layout.json` - UI structure and component arrangement
- `styling.json` - Colors, typography, and visual tokens
- `content.json` - Text patterns and messaging templates
- `metadata.json` - Template info and usage guidelines