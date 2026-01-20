“””
Study Material Generator - Uses Claude AI to generate study materials
“””

import os
import json
import re
from typing import Dict, List, Any
import anthropic

class StudyMaterialGenerator:
“”“Generate study materials using Claude Sonnet”””

```
def __init__(self, user_api_key: str = None):
    """
    Initialize generator
    
    Args:
        user_api_key: Optional user-provided Claude API key
                     If not provided, uses environment variable (your key)
    """
    # Priority: User key > Environment key
    api_key = user_api_key or os.environ.get('ANTHROPIC_API_KEY')
    
    if not api_key:
        raise ValueError("No Claude API key available. Either provide one or set ANTHROPIC_API_KEY environment variable.")
    
    self.client = anthropic.Anthropic(api_key=api_key)
    self.using_user_key = bool(user_api_key)

async def generate_materials(
    self,
    text: str,
    metadata: Dict[str, Any],
    formats: List[str],
    num_flashcards: int = 30,
    num_quiz_questions: int = 20,
    difficulty: str = 'mixed'
) -> Dict[str, Any]:
    """Generate all requested study materials"""
    
    materials = {}
    
    if 'summary' in formats:
        materials['summary'] = await self._generate_summary(text, metadata)
    
    if 'cornellNotes' in formats:
        materials['cornellNotes'] = await self._generate_cornell_notes(text, metadata)
    
    if 'flashcards' in formats:
        materials['flashcards'] = await self._generate_flashcards(
            text, metadata, num_flashcards, difficulty
        )
    
    if 'quiz' in formats:
        materials['quiz'] = await self._generate_quiz(
            text, metadata, num_quiz_questions, difficulty
        )
    
    if 'mindMap' in formats:
        materials['mindMap'] = await self._generate_mind_map(text, metadata)
    
    return materials

def _call_claude(self, system: str, user_prompt: str, max_tokens: int = 4000) -> str:
    """Call Claude API - synchronous because anthropic SDK doesn't support async"""
    
    message = self.client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system,
        messages=[{
            "role": "user",
            "content": user_prompt
        }]
    )
    
    return message.content[0].text

async def _generate_summary(self, text: str, metadata: Dict) -> Dict:
    """Generate executive summary with key points"""
    
    system = """You are an expert academic writer who creates insightful, comprehensive summaries that capture both the main ideas and important nuances of educational content."""
    
    prompt = f"""Analyze this document and create a professional executive summary.
```

Document: {metadata.get(‘filename’, ‘Unknown’)}

Full Text:
{text[:20000]}

Create a comprehensive summary that:

1. Captures the document’s main purpose and central argument
1. Identifies 5-8 key points with specific details and examples
1. Provides a meaningful conclusion that synthesizes the content

Return ONLY valid JSON (no markdown, no backticks):
{{
“overview”: “3-4 sentences explaining what this document is about, its main purpose, and central thesis”,
“keyPoints”: [
{{
“point”: “First major concept or finding”,
“details”: “2-3 sentences with specific information, examples, or evidence from the text”
}},
{{
“point”: “Second major concept”,
“details”: “Concrete details and context”
}}
],
“conclusion”: “2-3 sentences synthesizing how the key points connect and what the main takeaway is”
}}”””

```
    response = self._call_claude(system, prompt, max_tokens=3000)
    return self._parse_json_response(response)

async def _generate_cornell_notes(self, text: str, metadata: Dict) -> Dict:
    """Generate Cornell-style notes"""
    
    system = """You are a master educator who creates exceptional Cornell Notes. Your notes are detailed, well-organized, and optimized for learning and retention. You understand that Cornell Notes should have specific questions in the Cues column and comprehensive answers in the Notes column."""
    
    prompt = f"""Create comprehensive Cornell Notes from this document.
```

Document: {metadata.get(‘filename’, ‘Unknown’)}

Full Text:
{text[:20000]}

CORNELL NOTES FORMAT:

- **Cues**: Specific questions that test understanding (e.g., “How does photosynthesis convert light into energy?” not just “Photosynthesis”)
- **Notes**: Detailed 2-4 sentence answers with examples, explanations, and context
- **Summary**: A comprehensive paragraph (4-6 sentences) that synthesizes the main concepts and their relationships

REQUIREMENTS:

- Create 15-20 high-quality cue-note pairs
- Questions should be specific and meaningful
- Notes should be detailed with concrete information
- Organize by major concepts, not chronologically
- Include examples and explanations in notes

Return ONLY valid JSON (no markdown, no backticks):
{{
“cues”: [
“Specific question about first major concept?”,
“How does X relate to Y?”,
“What are the key components of Z?”,
…
],
“notes”: [
“Detailed answer with 2-4 sentences. Includes specific examples and explanations. Provides context and connections to other concepts.”,
“Another comprehensive answer with concrete details from the text…”,
…
],
“summary”: “A 4-6 sentence synthesis explaining: (1) what this document covers, (2) the main concepts and how they connect, (3) key insights or conclusions, and (4) why this matters or how to apply it.”
}}”””

```
    response = self._call_claude(system, prompt, max_tokens=5000)
    return self._parse_json_response(response)

async def _generate_flashcards(
    self,
    text: str,
    metadata: Dict,
    num_cards: int,
    difficulty: str
) -> List[Dict]:
    """Generate flashcards for spaced repetition"""
    
    system = """You are an expert at creating highly effective flashcards for spaced repetition learning. Your flashcards follow best practices: they're focused, clear, test real understanding, and use the minimum information principle. Each card tests one concept precisely."""
    
    difficulty_guidance = {
        'easy': 'Focus on fundamental facts, definitions, and basic relationships. Questions should be straightforward.',
        'medium': 'Balance factual recall with conceptual understanding. Include some application questions.',
        'hard': 'Emphasize complex concepts, analysis, synthesis, and application. Test deep understanding.',
        'mixed': 'Create a balanced mix: 40% easy (facts/definitions), 40% medium (concepts/relationships), 20% hard (analysis/application)'
    }
    
    prompt = f"""Create {num_cards} high-quality flashcards from this document.
```

Document: {metadata.get(‘filename’, ‘Unknown’)}
Difficulty: {difficulty} - {difficulty_guidance.get(difficulty, ‘’)}

Full Text:
{text[:20000]}

FLASHCARD BEST PRACTICES:

- Each card tests ONE specific concept
- Front: Clear, specific question (avoid vague questions)
- Back: Concise answer (1-3 sentences max)
- Use concrete examples when helpful
- Test understanding, not just memorization
- Vary question types (definition, application, comparison, etc.)

Return ONLY valid JSON array (no markdown, no backticks):
[
{{
“front”: “Precise, specific question that tests understanding”,
“back”: “Clear, concise answer in 1-3 sentences with key information”,
“difficulty”: “easy|medium|hard”,
“tags”: [“main-topic”, “subtopic”, “concept-type”]
}}
]

Create {num_cards} cards covering the full range of important concepts.”””

```
    response = self._call_claude(system, prompt, max_tokens=6000)
    return self._parse_json_response(response)

async def _generate_quiz(
    self,
    text: str,
    metadata: Dict,
    num_questions: int,
    difficulty: str
) -> Dict:
    """Generate multiple-choice quiz"""
    
    system = """You are an expert assessment designer who creates fair, well-crafted multiple-choice questions. Your questions test genuine understanding, have plausible distractors, and include clear explanations."""
    
    prompt = f"""Create a {num_questions}-question multiple-choice quiz from this document.
```

Document: {metadata.get(‘filename’, ‘Unknown’)}
Difficulty: {difficulty}

Full Text:
{text[:20000]}

QUIZ QUESTION REQUIREMENTS:

- Questions should test understanding, not just recall
- All 4 options should be plausible (no obviously wrong answers)
- Explanations should teach why the correct answer is right AND why others are wrong
- Cover different concepts (don’t repeat similar questions)
- Vary question types (direct recall, application, analysis, comparison)

Return ONLY valid JSON (no markdown, no backticks):
{{
“questions”: [
{{
“type”: “multiple_choice”,
“question”: “Clear, specific question that tests understanding”,
“options”: [
“A) First plausible option with specific details”,
“B) Second plausible option”,
“C) Third plausible option”,
“D) Fourth plausible option”
],
“correctAnswer”: “A”,
“explanation”: “A is correct because [specific reason from the text]. B is incorrect because [reason]. C is wrong because [reason]. D is incorrect because [reason].”,
“difficulty”: “easy|medium|hard”
}}
]
}}

Create {num_questions} high-quality questions.”””

```
    response = self._call_claude(system, prompt, max_tokens=6000)
    return self._parse_json_response(response)

async def _generate_mind_map(self, text: str, metadata: Dict) -> str:
    """Generate Mermaid mind map"""
    
    system = """You are an expert at creating clear, hierarchical mind maps that visualize complex information. Your mind maps use proper Mermaid syntax and organize concepts logically."""
    
    prompt = f"""Create a comprehensive Mermaid mind map from this document.
```

Document: {metadata.get(‘filename’, ‘Unknown’)}

Text:
{text[:15000]}

REQUIREMENTS:

- Start with the main topic as the root
- Create 4-6 main branches (major concepts)
- Each branch should have 2-4 sub-branches (details)
- Use clear, concise labels
- Organize hierarchically by concept relationships

Respond with ONLY the Mermaid code (no markdown fences, no backticks, no explanations):

mindmap
root((Main Topic))
Major Concept 1
Important Detail A
Important Detail B
Important Detail C
Major Concept 2
Detail D
Detail E
Major Concept 3
Detail F
Detail G
Detail H”””

```
    response = self._call_claude(system, prompt, max_tokens=2000)
    
    # Clean up the response
    mermaid_code = response.strip()
    mermaid_code = re.sub(r'```mermaid\n?', '', mermaid_code)
    mermaid_code = re.sub(r'```\n?', '', mermaid_code)
    
    return mermaid_code.strip()

def _parse_json_response(self, response: str) -> Any:
    """Parse JSON from Claude response, handling markdown code blocks"""
    
    # Remove markdown code blocks if present
    response = response.strip()
    response = re.sub(r'^```json\n?', '', response)
    response = re.sub(r'^```\n?', '', response)
    response = re.sub(r'\n?```$', '', response)
    
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}|\[.*\]', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        raise ValueError(f"Could not parse JSON from response: {e}")
```
