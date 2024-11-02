from anthropic import Anthropic
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Dict
import json

# Initialize Anthropic client
client = Anthropic()

@dataclass
class Persona:
    role: str
    expertise: str
    focus_areas: List[str]
    perspective: str

# Define our personas
PERSONAS = {
    "product_manager": Persona(
        role="Product Manager",
        expertise="Product strategy, market analysis, and feature prioritization",
        focus_areas=["Business value", "Market fit", "Feature prioritization", "Success metrics"],
        perspective="Strategic product development and market success"
    ),
    "ux_designer": Persona(
        role="UX Designer",
        expertise="User experience, interface design, and user research",
        focus_areas=["User flows", "Interface design", "Accessibility", "User research needs"],
        perspective="User-centered design and experience optimization"
    ),
    "marketing": Persona(
        role="Marketing Specialist",
        expertise="Market positioning, messaging, and go-to-market strategy",
        focus_areas=["Value proposition", "Market positioning", "Target audience", "Competitive advantage"],
        perspective="Market communication and product positioning"
    ),
    "engineer": Persona(
        role="Software Engineer",
        expertise="Technical implementation, system architecture, and feasibility",
        focus_areas=["Technical feasibility", "System architecture", "Performance requirements", "Integration needs"],
        perspective="Technical implementation and system design"
    )
}

def generate_persona_prompt(persona: Persona) -> str:
    """
    Have Opus generate a specific prompt for each persona's sub-agent
    """
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""Generate a detailed prompt for a sub-agent that will analyze a Product Requirements Document (PRD) from the perspective of a {persona.role}.

The sub-agent should embody this persona:
Role: {persona.role}
Expertise: {persona.expertise}
Focus Areas: {', '.join(persona.focus_areas)}
Perspective: {persona.perspective}

Generate a prompt that will make the sub-agent:
1. Analyze the PRD from this specific persona's perspective
2. Identify key concerns and opportunities
3. Provide specific suggestions for improvement
4. Highlight any missing elements crucial for this role
5. Structure the feedback in a clear, actionable format

Output only the prompt text that will be given to the sub-agent."""
                }
            ]
        }
    ]

    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        messages=messages
    )
    
    return response.content[0].text

def analyze_prd_with_persona(prd_text: str, persona: Persona, prompt: str) -> dict:
    """
    Have Haiku analyze the PRD from a specific persona's perspective
    """
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""PRD Content:
{prd_text}

{prompt}

Format your response as JSON with the following structure:
{{
    "key_insights": [],
    "concerns": [],
    "improvement_suggestions": [],
    "missing_elements": [],
    "priority_areas": []
}}"""
                }
            ]
        }
    ]

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=2000,
        messages=messages
    )
    
    return json.loads(response.content[0].text)

def synthesize_feedback(prd_text: str, persona_feedback: Dict[str, dict]) -> str:
    """
    Have Opus synthesize all persona feedback into a comprehensive analysis
    """
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""Original PRD:
{prd_text}

Feedback from different personas:
{json.dumps(persona_feedback, indent=2)}

Please synthesize this feedback into a comprehensive analysis that:
1. Summarizes key insights from each persona
2. Identifies common themes and concerns
3. Prioritizes improvement areas
4. Provides specific recommendations for enhancing the PRD
5. Highlights any potential conflicts in feedback between personas

Format your response in a clear, structured manner with sections and bullet points."""
                }
            ]
        }
    ]

    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=3000,
        messages=messages
    )
    
    return response.content[0].text

def analyze_prd(prd_text: str) -> str:
    """
    Main function to orchestrate the entire PRD analysis process
    """
    # Step 1: Generate prompts for each persona
    persona_prompts = {}
    for persona_id, persona in PERSONAS.items():
        persona_prompts[persona_id] = generate_persona_prompt(persona)
    
    # Step 2: Analyze PRD with each persona in parallel
    def process_persona(persona_tuple):
        persona_id, persona = persona_tuple
        prompt = persona_prompts[persona_id]
        return persona_id, analyze_prd_with_persona(prd_text, persona, prompt)
    
    with ThreadPoolExecutor() as executor:
        persona_feedback = dict(executor.map(
            process_persona, 
            PERSONAS.items()
        ))
    
    # Step 3: Synthesize all feedback
    final_analysis = synthesize_feedback(prd_text, persona_feedback)
    
    return final_analysis

# Example usage
if __name__ == "__main__":
    # Example PRD text
    sample_prd = """
    Product Requirements Document: Mobile Task Management App
    
    Overview:
    A mobile application for personal task management with smart prioritization features.
    
    Key Features:
    1. Task Creation and Organization
    2. Smart Priority Algorithm
    3. Daily/Weekly Views
    4. Reminder System
    
    Target Users:
    Busy professionals and students
    
    Success Metrics:
    - User retention
    - Task completion rate
    """
    
    # Run the analysis
    analysis = analyze_prd(sample_prd)
    print(analysis)
