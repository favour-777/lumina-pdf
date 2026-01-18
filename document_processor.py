"""
Document Processor - Handles downloading and text extraction from various formats
Supports: PDF, DOCX, TXT, MD, HTML, EPUB, RTF
"""

import aiohttp
import hashlib
from pathlib import Path
from io import BytesIO
import PyPDF2
import docx
import mammoth
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
from striprtf.striprtf import rtf_to_text
import re


class DocumentProcessor:
    """Extract text from various document formats"""
    
    SUPPORTED_FORMATS = {
        'pdf': ['.pdf'],
        'docx': ['.docx', '.doc'],
        'txt': ['.txt', '.text'],
        'markdown': ['.md', '.markdown'],
        'html': ['.html', '.htm'],
        'epub': ['.epub'],
        'rtf': ['.rtf']
    }
    
    def __init__(self):
        self.session = None
    
    async def download_file(self, url: str) -> dict:
        """Download file from URL and detect format"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to download file: HTTP {response.status}")
            
            content = await response.read()
            
            # Extract filename from URL or Content-Disposition
            filename = self._extract_filename(url, response.headers)
            file_format = self._detect_format(filename, content)
            
            # Generate unique file ID
            file_id = hashlib.md5(content).hexdigest()[:12]
            
            return {
                'content': content,
                'filename': filename,
                'format': file_format,
                'file_id': file_id,
                'size': len(content)
            }
    
    def _extract_filename(self, url: str, headers: dict) -> str:
        """Extract filename from URL or headers"""
        # Try Content-Disposition header first
        if 'Content-Disposition' in headers:
            content_disp = headers['Content-Disposition']
            if 'filename=' in content_disp:
                filename = content_disp.split('filename=')[-1].strip('"\'')
                return filename
        
        # Fall back to URL path
        from urllib.parse import urlparse, unquote
        path = urlparse(url).path
        filename = Path(unquote(path)).name
        
        return filename or 'document'
    
    def _detect_format(self, filename: str, content: bytes) -> str:
        """Detect document format from filename or content"""
        ext = Path(filename).suffix.lower()
        
        # Check by extension
        for format_type, extensions in self.SUPPORTED_FORMATS.items():
            if ext in extensions:
                return format_type
        
        # Check by magic bytes
        if content.startswith(b'%PDF'):
            return 'pdf'
        elif content.startswith(b'PK\x03\x04'):  # ZIP-based formats
            if b'word/' in content[:1000]:
                return 'docx'
            elif b'EPUB' in content[:100]:
                return 'epub'
        elif content.startswith(b'{\\rtf'):
            return 'rtf'
        elif b'<html' in content[:1000].lower():
            return 'html'
        
        # Default to txt
        return 'txt'
    
    async def extract_text(self, content: bytes, format_type: str) -> str:
        """Extract text from document based on format"""
        extractors = {
            'pdf': self._extract_pdf,
            'docx': self._extract_docx,
            'txt': self._extract_txt,
            'markdown': self._extract_txt,
            'html': self._extract_html,
            'epub': self._extract_epub,
            'rtf': self._extract_rtf
        }
        
        extractor = extractors.get(format_type, self._extract_txt)
        text = await extractor(content)
        
        # Clean up extracted text
        text = self._clean_text(text)
        
        return text
    
    async def _extract_pdf(self, content: bytes) -> str:
        """Extract text from PDF"""
        pdf_file = BytesIO(content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text_parts = []
        for page in pdf_reader.pages:
            text_parts.append(page.extract_text())
        
        return '\n\n'.join(text_parts)
    
    async def _extract_docx(self, content: bytes) -> str:
        """Extract text from DOCX using mammoth for better formatting"""
        docx_file = BytesIO(content)
        
        # Use mammoth for better HTML conversion, then strip HTML
        result = mammoth.convert_to_html(docx_file)
        html_text = result.value
        
        # Parse HTML and extract text
        soup = BeautifulSoup(html_text, 'html.parser')
        text = soup.get_text(separator='\n')
        
        return text
    
    async def _extract_txt(self, content: bytes) -> str:
        """Extract text from plain text files"""
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        
        # Fallback: decode with errors='ignore'
        return content.decode('utf-8', errors='ignore')
    
    async def _extract_html(self, content: bytes) -> str:
        """Extract text from HTML"""
        html = await self._extract_txt(content)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        text = soup.get_text(separator='\n')
        return text
    
    async def _extract_epub(self, content: bytes) -> str:
        """Extract text from EPUB"""
        epub_file = BytesIO(content)
        book = epub.read_epub(epub_file)
        
        text_parts = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text_parts.append(soup.get_text())
        
        return '\n\n'.join(text_parts)
    
    async def _extract_rtf(self, content: bytes) -> str:
        """Extract text from RTF"""
        rtf_text = await self._extract_txt(content)
        text = rtf_to_text(rtf_text)
        return text
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove page numbers and headers/footers patterns
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
        # Normalize line endings
        text = text.replace('\r\n', '\n')
        
        return text.strip()
    
    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()