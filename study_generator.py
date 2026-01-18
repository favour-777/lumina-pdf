"""
Study Material Generator - Uses Claude AI to generate study materials
"""

import anthropic
import json
import re
from typing import Dict, List, Any


class StudyMaterialGenerator:
    """Generate study materials using Claude AI"""
    
    def __init__(self, api_key: str = None, use_apify: bool = True):
        """
        Initialize generator
        
        Args:
            api_key: Anthropic API key (optional if using Apify integration)
            use_apify: Use Apify's built-in Claude integration
        """
        self.use_apify = use_apify and not api_key
        
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        elif not use_apify:
            raise ValueError("Must provide api_key or set use_apify=True")
    
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
        
        # Generate each format
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
    
    async def _call_claude(self, system: str, prompt: str, max_tokens: int = 4000) -> str:
        """Call Claude API"""
        
        if self.use_apify:
            # Use Apify's built-in integration via HTTP
            import aiohttp
            import os
            
            apify_token = os.environ.get('APIFY_TOKEN')
            if not apify_token:
                raise ValueError("APIFY_TOKEN not found in environment")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.apify.com/v2/acts/apify~anthropic-claude-scraper/runs',
                    headers={'Authorization': f'Bearer {apify_token}'},
                    json={
                        'model': 'claude-sonnet-4-20250514',
                        'systemPrompt': system,
                        'userPrompt': prompt,
                        'maxTokens': max_tokens
                    }
                ) as resp:
                    if resp.status != 201:
                        raise Exception(f"Apify API error: {resp.status}")
                    
                    run_data = await resp.json()
                    run_id = run_data['data']['id']
                    
                    # Poll for completion
                    import asyncio
                    for _ in range(60):  # 60 attempts, 2 seconds each = 2 minutes max
                        await asyncio.sleep(2)
                        
                        async with session.get(
                            f'https://api.apify.com/v2/actor-runs/{run_id}',
                            headers={'Authorization': f'Bearer {apify_token}'}
                        ) as status_resp:
                            status_data = await status_resp.json()
                            status = status_data['data']['status']
                            
                            if status == 'SUCCEEDED':
                                # Get output
                                async with session.get(
                                    f'https://api.apify.com/v2/actor-runs/{run_id}/dataset/items',
                                    headers={'Authorization': f'Bearer {apify_token}'}
                                ) as output_resp:
                                    output_data = await output_resp.json()
                                    if output_data and len(output_data) > 0:
                                        return output_data[0].get('text', '')
                                    raise Exception("No output from Claude")
                            
                            elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                                raise Exception(f"Claude run {status}")
                    
                    raise Exception("Claude run timed out")
        else:
            # Use direct API
            message = self.client.messages.create(
                model='claude-sonnet-4-20250514',
                max_tokens=max_tokens,
                system=system,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )
            return message.content[0].text
    
    async def _generate_summary(self, text: str, metadata: Dict) -> Dict:
        """Generate executive summary with key points"""
        
        system = """You are an expert at creating concise, informative summaries of academic and professional documents. 
Generate summaries that capture the essence and main ideas."""
        
        prompt = f"""Create a comprehensive summary of this document in JSON format.

Document: {metadata.get('filename', 'Unknown')}

Text:
{text[:15000]}

Respond with ONLY a JSON object (no markdown, no backticks) with this structure:
{{
    "overview": "2-3 sentence overview of the entire document",
    "keyPoints": [
        {{"point": "Main idea 1", "details": "Brief explanation"}},
        {{"point": "Main idea 2", "details": "Brief explanation"}}
    ],
    "conclusion": "Final takeaway or conclusion"
}}"""
        
        response = await self._call_claude(system, prompt, max_tokens=2000)
        return self._parse_json_response(response)
    
    async def _generate_cornell_notes(self, text: str, metadata: Dict) -> Dict:
        """Generate Cornell-style notes"""
        
        system = """You are an expert at creating Cornell Notes - a proven note-taking method with cues, notes, and summary sections."""
        
        prompt = f"""Create Cornell Notes from this document in JSON format.

Document: {metadata.get('filename', 'Unknown')}

Text:
{text[:15000]}

Respond with ONLY a JSON object (no markdown, no backticks) with this structure:
{{
    "cues": ["Question 1?", "Key term 2", "Question 3?"],
    "notes": ["Detailed explanation 1", "Detailed explanation 2", "Detailed explanation 3"],
    "summary": "Overall summary in 2-3 sentences"
}}

Generate 10-15 cue-note pairs that cover the main concepts."""
        
        response = await self._call_claude(system, prompt, max_tokens=3000)
        return self._parse_json_response(response)
    
    async def _generate_flashcards(
        self,
        text: str,
        metadata: Dict,
        num_cards: int,
        difficulty: str
    ) -> List[Dict]:
        """Generate flashcards for spaced repetition"""
        
        system = """You are an expert at creating effective flashcards for spaced repetition learning (like Anki). 
Your flashcards should be clear, concise, and test understanding."""
        
        difficulty_guidance = {
            'easy': 'Focus on basic facts and definitions',
            'medium': 'Balance facts with conceptual understanding',
            'hard': 'Focus on complex concepts and applications',
            'mixed': 'Mix of easy, medium, and hard questions'
        }
        
        prompt = f"""Create {num_cards} flashcards from this document in JSON format.

Document: {metadata.get('filename', 'Unknown')}
Difficulty: {difficulty} - {difficulty_guidance.get(difficulty, '')}

Text:
{text[:15000]}

Respond with ONLY a JSON array (no markdown, no backticks) with this structure:
[
    {{
        "front": "Clear, specific question",
        "back": "Concise answer (1-3 sentences)",
        "difficulty": "easy|medium|hard",
        "tags": ["topic1", "concept2"]
    }}
]

Make flashcards that test real understanding, not just memorization."""
        
        response = await self._call_claude(system, prompt, max_tokens=4000)
        return self._parse_json_response(response)
    
    async def _generate_quiz(
        self,
        text: str,
        metadata: Dict,
        num_questions: int,
        difficulty: str
    ) -> Dict:
        """Generate multiple-choice quiz"""
        
        system = """You are an expert at creating effective multiple-choice questions that test understanding."""
        
        prompt = f"""Create a {num_questions}-question multiple-choice quiz from this document in JSON format.

Document: {metadata.get('filename', 'Unknown')}
Difficulty: {difficulty}

Text:
{text[:15000]}

Respond with ONLY a JSON object (no markdown, no backticks) with this structure:
{{
    "questions": [
        {{
            "type": "multiple_choice",
            "question": "Clear question text",
            "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
            "correctAnswer": "A",
            "explanation": "Why this answer is correct",
            "difficulty": "easy|medium|hard"
        }}
    ]
}}

Create questions that test understanding, not just recall."""
        
        response = await self._call_claude(system, prompt, max_tokens=4000)
        return self._parse_json_response(response)
    
    async def _generate_mind_map(self, text: str, metadata: Dict) -> str:
        """Generate Mermaid mind map"""
        
        system = """You are an expert at creating clear mind maps that visualize concept relationships using Mermaid syntax."""
        
        prompt = f"""Create a Mermaid mind map from this document.

Document: {metadata.get('filename', 'Unknown')}

Text:
{text[:10000]}

Respond with ONLY the Mermaid code (no markdown code fences, no backticks, no explanations).
Use this format:

mindmap
  root((Main Topic))
    Subtopic 1
      Detail A
      Detail B
    Subtopic 2
      Detail C
      Detail D

Keep it clear and organized with 3-5 main branches."""
        
        response = await self._call_claude(system, prompt, max_tokens=1500)
        
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