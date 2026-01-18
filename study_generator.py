"""
Study Material Generator - Uses AI to generate study materials
"""

from apify import Actor
import json
import re
from typing import Dict, List, Any


class StudyMaterialGenerator:
    """Generate study materials using AI via Apify's GPT-4o-mini actor"""
    
    def __init__(self):
        """Initialize generator - no API key needed, uses Apify credits"""
        pass
    
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
    
    async def _call_gpt(self, system: str, user_prompt: str, max_tokens: int = 4000) -> str:
        """Call GPT-4o-mini via Apify actor"""
        
        run_input = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "maxTokens": max_tokens
        }
        
        run = await Actor.call(
            actor_id='apify/chatgpt-gpt-4o-mini',
            run_input=run_input
        )
        
        # Get dataset items from the run
        dataset_id = run.get('defaultDatasetId')
        if not dataset_id:
            raise Exception("No dataset returned from GPT call")
        
        dataset_items = await Actor.apify_client.dataset(dataset_id).list_items()
        
        if not dataset_items or not dataset_items.items:
            raise Exception("No response from GPT")
        
        # Extract the response text
        response_item = dataset_items.items[0]
        
        # Handle different response formats
        if isinstance(response_item, dict):
            if 'choices' in response_item:
                return response_item['choices'][0]['message']['content']
            elif 'message' in response_item:
                return response_item['message']['content']
            elif 'content' in response_item:
                return response_item['content']
            elif 'text' in response_item:
                return response_item['text']
        
        # If we have a string, return it
        if isinstance(response_item, str):
            return response_item
        
        raise Exception(f"Unexpected response format: {type(response_item)}")
    
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
        
        response = await self._call_gpt(system, prompt, max_tokens=2000)
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
        
        response = await self._call_gpt(system, prompt, max_tokens=3000)
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
        
        response = await self._call_gpt(system, prompt, max_tokens=4000)
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
        
        response = await self._call_gpt(system, prompt, max_tokens=4000)
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
        
        response = await self._call_gpt(system, prompt, max_tokens=1500)
        
        # Clean up the response
        mermaid_code = response.strip()
        mermaid_code = re.sub(r'```mermaid\n?', '', mermaid_code)
        mermaid_code = re.sub(r'```\n?', '', mermaid_code)
        
        return mermaid_code.strip()
    
    def _parse_json_response(self, response: str) -> Any:
        """Parse JSON from AI response, handling markdown code blocks"""
        
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