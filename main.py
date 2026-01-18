"""
Lumina PDF - AI-Powered Document Study Companion
Main entry point for Apify Actor
"""

from apify import Actor
import asyncio
from pathlib import Path
import json
from datetime import datetime
from study_generator import StudyMaterialGenerator
from export_utils import ExportManager
from document_processor import DocumentProcessor


async def main():
    async with Actor:
        # Get actor input
        actor_input = await Actor.get_input() or {}
        
        # Extract configuration
        file_urls = actor_input.get('fileUrls', '').strip().split('\n')
        file_urls = [url.strip() for url in file_urls if url.strip()]
        
        if not file_urls:
            Actor.log.error('No document URLs provided')
            await Actor.fail('Please provide at least one document URL')
            return
        
        output_formats = actor_input.get('outputFormats', [
            'cornellNotes', 'flashcards', 'quiz', 'summary', 'mindMap'
        ])
        
        num_flashcards = actor_input.get('numFlashcards', 30)
        num_quiz_questions = actor_input.get('numQuizQuestions', 20)
        difficulty_level = actor_input.get('difficultyLevel', 'mixed')
        
        Actor.log.info(f'Processing {len(file_urls)} document(s)')
        Actor.log.info(f'Output formats: {output_formats}')
        
        # Initialize processors
        doc_processor = DocumentProcessor()
        study_gen = StudyMaterialGenerator()
        export_mgr = ExportManager()
        
        # Process each document
        for idx, file_url in enumerate(file_urls, 1):
            try:
                Actor.log.info(f'[{idx}/{len(file_urls)}] Processing: {file_url}')
                
                # Download and extract text from document
                Actor.log.info('Downloading document...')
                file_data = await doc_processor.download_file(file_url)
                
                Actor.log.info(f'Extracting text from {file_data["format"]}...')
                extracted_text = await doc_processor.extract_text(
                    file_data['content'],
                    file_data['format']
                )
                
                if not extracted_text or len(extracted_text.strip()) < 100:
                    Actor.log.warning(f'Insufficient text extracted from {file_url}')
                    continue
                
                Actor.log.info(f'Extracted {len(extracted_text)} characters')
                
                # Generate study materials
                Actor.log.info('Generating study materials with AI...')
                study_materials = await study_gen.generate_materials(
                    text=extracted_text,
                    metadata={
                        'source_url': file_url,
                        'filename': file_data['filename'],
                        'format': file_data['format']
                    },
                    formats=output_formats,
                    num_flashcards=num_flashcards,
                    num_quiz_questions=num_quiz_questions,
                    difficulty=difficulty_level
                )
                
                # Generate exports
                Actor.log.info('Creating export formats...')
                exports = export_mgr.create_exports(
                    study_materials=study_materials,
                    metadata={
                        'filename': file_data['filename'],
                        'source_url': file_url,
                        'processed_at': datetime.utcnow().isoformat() + 'Z'
                    }
                )
                
                # Save PDF to key-value store
                if exports.get('pdf'):
                    pdf_key = f"{file_data['file_id']}_study_guide.pdf"
                    await Actor.set_value(pdf_key, exports['pdf'], content_type='application/pdf')
                    Actor.log.info(f'PDF saved to key-value store: {pdf_key}')
                    pdf_url = f"https://api.apify.com/v2/key-value-stores/{Actor.get_env().get('default_key_value_store_id')}/records/{pdf_key}"
                else:
                    pdf_url = None
                    pdf_key = None
                
                # Prepare dataset output
                result = {
                    'fileId': file_data['file_id'],
                    'filename': file_data['filename'],
                    'sourceUrl': file_url,
                    'format': file_data['format'],
                    'processedAt': datetime.utcnow().isoformat() + 'Z',
                    
                    'studyMaterials': study_materials,
                    
                    'exports': {
                        'ankiCsv': exports.get('anki_csv'),
                        'notionMarkdown': exports.get('notion_md'),
                        'quizHtml': exports.get('quiz_html'),
                        'json': exports.get('json')
                    },
                    
                    'pdfUrl': pdf_url,
                    'pdfKey': pdf_key,
                    
                    'statistics': {
                        'textLength': len(extracted_text),
                        'wordCount': len(extracted_text.split()),
                        'estimatedReadTime': f"{len(extracted_text.split()) // 200}m",
                        'generatedFormats': output_formats,
                        'flashcardCount': len(study_materials.get('flashcards', [])),
                        'quizQuestionCount': len(study_materials.get('quiz', {}).get('questions', []))
                    },
                    
                    'status': 'success'
                }
                
                # Push to dataset
                await Actor.push_data(result)
                Actor.log.info(f'✓ Successfully processed {file_data["filename"]}')
                
            except Exception as e:
                Actor.log.error(f'Error processing {file_url}: {str(e)}')
                await Actor.push_data({
                    'sourceUrl': file_url,
                    'status': 'failed',
                    'error': str(e),
                    'processedAt': datetime.utcnow().isoformat() + 'Z'
                })
        
        # Clean up
        await doc_processor.close()
        
        Actor.log.info('All documents processed successfully!')


if __name__ == '__main__':
    asyncio.run(main())