# Study Material Generator - Uses Claude AI to generate study materials

import os
import json
import re
from typing import Dict, List, Any
import anthropic


class StudyMaterialGenerator:
    """Generate study materials using Claude Sonnet"""
    
    def __init__(self, user_api_key: str = None):
        api_key = user_api_key or os.environ.get('ANTHROPIC_API_KEY')
        
        if not api_key:
            raise ValueError("No Claude API key available")
        
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
        system = "You are an expert academic writer who creates insightful, comprehensive summaries that capture both the main ideas and important nuances of educational content."
        
        prompt = f"""Analyze this document and create a professional executive summary.

Document: {metadata.get('filename', 'Unknown')}

Full Text:
{text[:20000]}

Create a comprehensive summary that:
1. Captures the document's main purpose and central argument
2. Identifies 5-8 key points with specific details and examples
3. Provides a meaningful conclusion that synthesizes the content

Return ONLY valid JSON (no markdown, no backticks):
{{
    "overview": "3-4 sentences explaining what this document is about, its main purpose, and central thesis",
    "keyPoints": [
        {{
            "point": "First major concept or finding",
            "details": "2-3 sentences with specific information, examples, or evidence from the text"
        }},
        {{
            "point": "Second major concept",
            "details": "Concrete details and context"
        }}
    ],
    "conclusion": "2-3 sentences synthesizing how the key points connect and what the main takeaway is"
}}"""
        
        response = self._call_claude(system, prompt, max_tokens=3000)
        return self._parse_json_response(response)
    
    async def _generate_cornell_notes(self, text: str, metadata: Dict) -> Dict:
        system = "You are a master educator who creates exceptional Cornell Notes. Your notes are detailed, well-organized, and optimized for learning and retention."
        
        prompt = f"""Create comprehensive Cornell Notes from this document.

Document: {metadata.get('filename', 'Unknown')}

Full Text:
{text[:20000]}

CORNELL NOTES FORMAT:
- Cues: Specific questions that test understanding
- Notes: Detailed 2-4 sentence answers with examples
- Summary: A comprehensive paragraph synthesizing main concepts

REQUIREMENTS:
- Create 15-20 high-quality cue-note pairs
- Questions should be specific and meaningful
- Notes should be detailed with concrete information
- Include examples and explanations

Return ONLY valid JSON:
{{
    "cues": ["Specific question about first major concept?", "How does X relate to Y?"],
    "notes": ["Detailed answer with 2-4 sentences including examples.", "Another comprehensive answer."],
    "summary": "A 4-6 sentence synthesis explaining what this covers, main concepts, and key insights."
}}"""
        
        response = self._call_claude(system, prompt, max_tokens=5000)
        return self._parse_json_response(response)
    
    async def _generate_flashcards(self, text: str, metadata: Dict, num_cards: int, difficulty: str) -> List[Dict]:
        system = "You are an expert at creating highly effective flashcards for spaced repetition learning."
        
        difficulty_guidance = {
            'easy': 'Focus on fundamental facts and definitions',
            'medium': 'Balance factual recall with conceptual understanding',
            'hard': 'Emphasize complex concepts and application',
            'mixed': 'Create a balanced mix: 40% easy, 40% medium, 20% hard'
        }
        
        prompt = f"""Create {num_cards} high-quality flashcards from this document.

Document: {metadata.get('filename', 'Unknown')}
Difficulty: {difficulty} - {difficulty_guidance.get(difficulty, '')}

Full Text:
{text[:20000]}

FLASHCARD BEST PRACTICES:
- Each card tests ONE specific concept
- Front: Clear, specific question
- Back: Concise answer (1-3 sentences)
- Test understanding, not just memorization

Return ONLY valid JSON array:
[
    {{
        "front": "Precise, specific question",
        "back": "Clear answer in 1-3 sentences",
        "difficulty": "easy|medium|hard",
        "tags": ["topic", "subtopic"]
    }}
]"""
        
        response = self._call_claude(system, prompt, max_tokens=6000)
        return self._parse_json_response(response)
    
    async def _generate_quiz(self, text: str, metadata: Dict, num_questions: int, difficulty: str) -> Dict:
        system = "You are an expert assessment designer who creates fair, well-crafted multiple-choice questions."
        
        prompt = f"""Create a {num_questions}-question multiple-choice quiz from this document.

Document: {metadata.get('filename', 'Unknown')}
Difficulty: {difficulty}

Full Text:
{text[:20000]}

REQUIREMENTS:
- All 4 options should be plausible
- Explanations should teach why correct answer is right AND why others are wrong
- Cover different concepts

Return ONLY valid JSON:
{{
    "questions": [
        {{
            "type": "multiple_choice",
            "question": "Clear, specific question",
            "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
            "correctAnswer": "A",
            "explanation": "A is correct because [reason]. B is incorrect because [reason].",
            "difficulty": "easy|medium|hard"
        }}
    ]
}}"""
        
        response = self._call_claude(system, prompt, max_tokens=6000)
        return self._parse_json_response(response)
    
    async def _generate_mind_map(self, text: str, metadata: Dict) -> str:
        system = "You are an expert at creating clear mind maps using Mermaid syntax."
        
        prompt = f"""Create a Mermaid mind map from this document.

Document: {metadata.get('filename', 'Unknown')}

Text:
{text[:15000]}

REQUIREMENTS:
- 4-6 main branches (major concepts)
- Each branch has 2-4 sub-branches
- Use clear, concise labels

Respond with ONLY the Mermaid code (no markdown fences):

mindmap
  root((Main Topic))
    Major Concept 1
      Detail A
      Detail B"""
        
        response = self._call_claude(system, prompt, max_tokens=2000)
        mermaid_code = response.strip()
        mermaid_code = re.sub(r'```mermaid\n?', '', mermaid_code)
        mermaid_code = re.sub(r'```\n?', '', mermaid_code)
        return mermaid_code.strip()
    
    def _parse_json_response(self, response: str) -> Any:
        response = response.strip()
        response = re.sub(r'^```json\n?', '', response)
        response = re.sub(r'^```\n?', '', response)
        response = re.sub(r'\n?```$', '', response)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            json_match = re.search(r'\{.*\}|\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Could not parse JSON from response: {e}")