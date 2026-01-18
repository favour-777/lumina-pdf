"""
Export Manager - Generate various export formats
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import json
from typing import Dict, Any


class ExportManager:
    """Generate exports in various formats"""
    
    def create_exports(self, study_materials: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create all export formats"""
        
        exports = {}
        
        # Anki CSV
        if 'flashcards' in study_materials:
            exports['anki_csv'] = self._create_anki_csv(study_materials['flashcards'])
        
        # Notion Markdown
        exports['notion_md'] = self._create_notion_markdown(study_materials, metadata)
        
        # Interactive HTML Quiz
        if 'quiz' in study_materials:
            exports['quiz_html'] = self._create_quiz_html(study_materials['quiz'], metadata)
        
        # JSON export
        exports['json'] = json.dumps({
            'metadata': metadata,
            'studyMaterials': study_materials
        }, indent=2)
        
        # PDF export
        exports['pdf'] = self._create_pdf(study_materials, metadata)
        
        return exports
    
    def _create_anki_csv(self, flashcards: list) -> str:
        """Generate Anki-compatible CSV"""
        
        csv_lines = ['Front,Back,Tags']
        
        for card in flashcards:
            front = card['front'].replace('"', '""')
            back = card['back'].replace('"', '""')
            tags = ' '.join(card.get('tags', [])).replace('"', '""')
            
            csv_lines.append(f'"{front}","{back}","{tags}"')
        
        return '\n'.join(csv_lines)
    
    def _create_notion_markdown(self, materials: Dict, metadata: Dict) -> str:
        """Generate Notion-optimized markdown with callouts"""
        
        md_parts = []
        
        # Header
        md_parts.append(f"# 📚 Study Guide: {metadata.get('filename', 'Document')}\n")
        md_parts.append(f"**Source:** {metadata.get('source_url', 'N/A')}")
        md_parts.append(f"**Processed:** {metadata.get('processed_at', 'N/A')}\n")
        md_parts.append("---\n")
        
        # Summary
        if 'summary' in materials:
            summary = materials['summary']
            md_parts.append("## 📋 Executive Summary\n")
            md_parts.append(f"{summary.get('overview', '')}\n")
            
            if summary.get('keyPoints'):
                md_parts.append("### Key Points\n")
                for point in summary['keyPoints']:
                    md_parts.append(f"- **{point['point']}**: {point.get('details', '')}")
                md_parts.append("")
            
            if summary.get('conclusion'):
                md_parts.append(f"> [!TIP] Conclusion\n> {summary['conclusion']}\n")
        
        # Cornell Notes
        if 'cornellNotes' in materials:
            notes = materials['cornellNotes']
            md_parts.append("## 📝 Cornell Notes\n")
            
            md_parts.append("| Cues | Notes |")
            md_parts.append("|------|-------|")
            
            cues = notes.get('cues', [])
            note_items = notes.get('notes', [])
            
            for i in range(max(len(cues), len(note_items))):
                cue = cues[i] if i < len(cues) else ''
                note = note_items[i] if i < len(note_items) else ''
                md_parts.append(f"| {cue} | {note} |")
            
            md_parts.append("")
            
            if notes.get('summary'):
                md_parts.append(f"> [!NOTE] Summary\n> {notes['summary']}\n")
        
        # Flashcards
        if 'flashcards' in materials:
            md_parts.append("## 🎴 Flashcards\n")
            
            for i, card in enumerate(materials['flashcards'], 1):
                difficulty = card.get('difficulty', 'medium')
                emoji = {'easy': '🟢', 'medium': '🟡', 'hard': '🔴'}.get(difficulty, '🟡')
                
                md_parts.append(f"### {emoji} Card {i}")
                md_parts.append(f"> [!QUESTION] Question\n> {card['front']}\n")
                md_parts.append(f"> [!SUCCESS] Answer\n> {card['back']}\n")
                
                if card.get('tags'):
                    tags = ', '.join([f"`{tag}`" for tag in card['tags']])
                    md_parts.append(f"**Tags:** {tags}\n")
        
        # Quiz
        if 'quiz' in materials:
            quiz = materials['quiz']
            md_parts.append("## 📊 Practice Quiz\n")
            
            for i, q in enumerate(quiz.get('questions', []), 1):
                md_parts.append(f"### Question {i}\n")
                md_parts.append(f"{q['question']}\n")
                
                for option in q.get('options', []):
                    md_parts.append(f"- {option}")
                
                md_parts.append("")
                md_parts.append(f"> [!SUCCESS] Answer: {q['correctAnswer']}")
                md_parts.append(f"> {q.get('explanation', '')}\n")
        
        # Mind Map
        if 'mindMap' in materials:
            md_parts.append("## 🗺️ Mind Map\n")
            md_parts.append("```mermaid")
            md_parts.append(materials['mindMap'])
            md_parts.append("```\n")
        
        return '\n'.join(md_parts)
    
    def _create_quiz_html(self, quiz: Dict, metadata: Dict) -> str:
        """Generate interactive HTML quiz"""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quiz: {metadata.get('filename', 'Document')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #667eea;
            margin-bottom: 0.5rem;
            font-size: 2rem;
        }}
        .metadata {{
            color: #666;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #f0f0f0;
        }}
        .question {{
            margin-bottom: 2rem;
            padding: 1.5rem;
            background: #f9f9f9;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }}
        .question-text {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #333;
        }}
        .options {{
            list-style: none;
        }}
        .option {{
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .option:hover {{
            border-color: #667eea;
            transform: translateX(5px);
        }}
        .explanation {{
            margin-top: 1rem;
            padding: 1rem;
            background: #e8f5e9;
            border-radius: 8px;
            display: none;
        }}
        .explanation.show {{
            display: block;
            animation: slideDown 0.3s ease;
        }}
        @keyframes slideDown {{
            from {{ opacity: 0; transform: translateY(-10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .show-answer-btn {{
            margin-top: 1rem;
            padding: 0.5rem 1rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.3s;
        }}
        .show-answer-btn:hover {{
            background: #764ba2;
        }}
        .correct-answer {{
            color: #2e7d32;
            font-weight: 600;
        }}
        .footer {{
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 2px solid #f0f0f0;
            text-align: center;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Practice Quiz</h1>
        <div class="metadata">
            <strong>Document:</strong> {metadata.get('filename', 'N/A')}<br>
            <strong>Questions:</strong> {len(quiz.get('questions', []))}
        </div>
"""
        
        for i, q in enumerate(quiz.get('questions', []), 1):
            html += f"""
        <div class="question">
            <div class="question-text">{i}. {q['question']}</div>
            <ul class="options">
"""
            for option in q.get('options', []):
                html += f"                <li class='option'>{option}</li>\n"
            
            html += f"""
            </ul>
            <button class="show-answer-btn" onclick="toggleAnswer({i})">Show Answer</button>
            <div class="explanation" id="explanation-{i}">
                <div class="correct-answer">✓ Correct Answer: {q['correctAnswer']}</div>
                <p style="margin-top: 0.5rem;">{q.get('explanation', '')}</p>
            </div>
        </div>
"""
        
        html += """
        <div class="footer">
            Good luck with your studies! 📚✨
        </div>
    </div>
    <script>
        function toggleAnswer(questionNum) {
            const explanation = document.getElementById('explanation-' + questionNum);
            explanation.classList.toggle('show');
        }
    </script>
</body>
</html>"""
        
        return html
    
    def _create_pdf(self, materials: Dict, metadata: Dict) -> bytes:
        """Generate professional PDF study guide"""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
        
        # Container for PDF elements
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph(f"📚 Study Guide: {metadata.get('filename', 'Document')}", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Metadata
        story.append(Paragraph(f"<b>Source:</b> {metadata.get('source_url', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"<b>Processed:</b> {metadata.get('processed_at', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        if 'summary' in materials:
            summary = materials['summary']
            story.append(Paragraph("📋 Executive Summary", heading_style))
            story.append(Paragraph(summary.get('overview', ''), styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            if summary.get('keyPoints'):
                story.append(Paragraph("<b>Key Points:</b>", styles['Normal']))
                for point in summary['keyPoints']:
                    story.append(Paragraph(f"• <b>{point['point']}</b>: {point.get('details', '')}", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        
        # Cornell Notes
        if 'cornellNotes' in materials:
            notes = materials['cornellNotes']
            story.append(Paragraph("📝 Cornell Notes", heading_style))
            
            # Create table
            table_data = [['Cues', 'Notes']]
            cues = notes.get('cues', [])
            note_items = notes.get('notes', [])
            
            for i in range(max(len(cues), len(note_items))):
                cue = cues[i] if i < len(cues) else ''
                note = note_items[i] if i < len(note_items) else ''
                table_data.append([cue, note])
            
            table = Table(table_data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.2*inch))
        
        # Flashcards
        if 'flashcards' in materials:
            story.append(PageBreak())
            story.append(Paragraph("🎴 Flashcards", heading_style))
            
            for i, card in enumerate(materials['flashcards'], 1):
                story.append(Paragraph(f"<b>Card {i}</b>", styles['Normal']))
                story.append(Paragraph(f"<i>Q: {card['front']}</i>", styles['Normal']))
                story.append(Paragraph(f"A: {card['back']}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(story)
        
        return buffer.getvalue()