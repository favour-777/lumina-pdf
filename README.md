# ✨ Lumina PDF: Universal Document Study Companion

> **Transform any document into professional study materials with AI**

Lumina PDF analyzes documents in multiple formats (PDF, DOCX, EPUB, TXT, MD, HTML, RTF) and generates comprehensive study materials in seconds. From Cornell Notes to Anki-ready flashcards and interactive quizzes—everything you need to master any written content.

---

## 🎯 Why Lumina PDF?

Turn research papers, textbooks, lecture notes, ebooks, and any document into structured, high‑quality study materials instantly.

| Traditional Workflow | With Lumina PDF ✨ |
| --- | --- |
| Hours reading and manually taking notes | ⏱️ **Under 2 minutes** to generate complete study materials |
| Notes depend on focus and manual effort | 📝 Clean, consistent Cornell Notes every time |
| Flashcards require hours to create | 🎴 Automatically generated Anki‑ready flashcards |
| No built‑in practice questions | 📊 Quiz questions with detailed explanations |
| Learning quality varies | 📚 Professionally structured materials optimized for retention |

**Lumina PDF doesn't replace reading — it supercharges your study workflow.**

---

## 🌟 Features

### 📝 Cornell Notes
Professional two-column notes with:
- **Cues**: Key questions and terms extracted from content
- **Notes**: Detailed explanations and concepts
- **Summary**: Main takeaways and conclusions

Perfect for structured review and exam preparation.

### 🎴 Anki-Ready Flashcards
Generate 5-100 flashcards with:
- Clear, specific questions (front)
- Concise answers (back)
- Relevant tags for organization
- Difficulty levels (easy/medium/hard)

Export directly to Anki CSV format for spaced repetition learning.

### 📊 Interactive Practice Quiz
Test your understanding with:
- Multiple-choice questions
- 4 well-crafted options per question
- Correct answers with detailed explanations
- Beautiful, interactive HTML interface

### 📄 Professional PDF Export
Download a complete study guide with:
- Document metadata and source links
- Executive summary with key points
- Cornell Notes in table format
- All flashcards organized and formatted
- Direct link back to source

### 🗺️ Mind Maps
Visualize concept relationships with:
- Mermaid diagram syntax
- Hierarchical structure
- Main topics and subtopics
- Easy to embed in Notion, Obsidian, or any markdown editor

### 📋 Notion-Optimized Markdown
Import directly to Notion with:
- Callout blocks for important info
- Clickable source links
- Clean hierarchical structure
- Formatted tables for Cornell Notes
- Color-coded difficulty indicators

---

## 📚 Supported Document Formats

### Fully Supported ✅
- **PDF** (.pdf) - Research papers, textbooks, articles
- **Microsoft Word** (.docx, .doc) - Lecture notes, reports
- **EPUB** (.epub) - Ebooks, digital publications
- **Plain Text** (.txt) - Simple notes and documents
- **Markdown** (.md) - Documentation, wikis
- **HTML** (.html, .htm) - Web articles, saved pages
- **Rich Text Format** (.rtf) - Formatted documents

### Coming Soon 🔜
- PowerPoint (.pptx) - Presentation slides
- Excel (.xlsx) - Data tables and notes
- OpenDocument (.odt, .ods) - LibreOffice documents
- LaTeX (.tex) - Academic papers

---

## 🚀 Perfect For

| User Type | Use Case |
| --- | --- |
| 🎓 **College Students** | Convert textbook chapters and lecture PDFs into study materials |
| 📚 **Self-Learners** | Transform ebooks and articles into structured learning resources |
| 🔬 **Researchers** | Generate study guides from research papers and journals |
| 👨‍🏫 **Educators** | Create supplementary materials and quizzes from documents |
| 💼 **Professionals** | Turn training manuals and documentation into quick-reference guides |
| 📖 **Book Readers** | Create flashcards and summaries from ebooks |

---

## 📖 How to Use

### Simple 3-Step Process

1. **Provide Document URLs**
   ```
   https://example.com/textbook-chapter.pdf
   https://example.com/lecture-notes.docx
   https://example.com/research-paper.pdf
   ```
   One per line for batch processing.

2. **Select Formats**
   - ✅ Cornell Notes
   - ✅ Flashcards (30 cards)
   - ✅ Practice Quiz (20 questions)
   - ✅ Summary
   - ✅ Mind Map

3. **Download Results**
   - **Dataset tab**: Markdown, JSON, Anki CSV
   - **Key-Value Store tab**: Professional PDF
   - **Interactive HTML quiz** embedded in results

### Advanced Configuration

**Flashcard Count**: 5-100 cards  
**Quiz Questions**: 5-50 questions  
**Difficulty**: Easy, Medium, Hard, or Mixed  
**API Key**: Optional - use your own Claude API key for unlimited processing

---

## 📊 Input Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| **fileUrls** | string | required | Document URLs (one per line) |
| **outputFormats** | array | All | Cornell Notes, Flashcards, Quiz, Summary, Mind Map |
| **numFlashcards** | integer | 30 | Number of flashcards (5-100) |
| **numQuizQuestions** | integer | 20 | Number of quiz questions (5-50) |
| **difficultyLevel** | string | mixed | easy/medium/hard/mixed |
| **useApifyIntegration** | boolean | true | Use built-in processing (no API key needed) |
| **anthropicApiKey** | string | optional | Your Claude API key for unlimited processing |

---

## 📤 Output Structure

### Dataset Output

```json
{
  "fileId": "abc123def456",
  "filename": "quantum-physics-lecture.pdf",
  "sourceUrl": "https://example.com/lecture.pdf",
  "format": "pdf",
  "processedAt": "2026-01-13T10:30:00Z",
  
  "studyMaterials": {
    "cornellNotes": {
      "cues": ["What is quantum entanglement?", "Key principle?"],
      "notes": ["Quantum entanglement is...", "The key principle states..."],
      "summary": "Main takeaways from quantum physics lecture."
    },
    "flashcards": [
      {
        "front": "What is the Heisenberg Uncertainty Principle?",
        "back": "States that you cannot simultaneously know both position and momentum of a particle with perfect precision.",
        "difficulty": "medium",
        "tags": ["quantum-mechanics", "fundamentals"]
      }
    ],
    "quiz": {
      "questions": [
        {
          "type": "multiple_choice",
          "question": "What does wave-particle duality describe?",
          "options": ["A) Only particles", "B) Both wave and particle nature", "C) Only waves", "D) Neither"],
          "correctAnswer": "B",
          "explanation": "Wave-particle duality describes how quantum objects exhibit both wave-like and particle-like properties.",
          "difficulty": "medium"
        }
      ]
    },
    "summary": {
      "overview": "This lecture covers fundamental principles of quantum mechanics...",
      "keyPoints": [
        {"point": "Quantum entanglement", "details": "Non-local correlation between particles"}
      ],
      "conclusion": "Quantum mechanics fundamentally changes our understanding of reality."
    },
    "mindMap": "mindmap\n  root((Quantum Physics))..."
  },
  
  "exports": {
    "ankiCsv": "Front,Back,Tags\n...",
    "notionMarkdown": "# Study Guide...",
    "quizHtml": "<!DOCTYPE html>...",
    "json": "{...}"
  },
  
  "pdfUrl": "https://api.apify.com/v2/key-value-stores/.../abc123_study_guide.pdf",
  "pdfKey": "abc123_study_guide.pdf",
  
  "statistics": {
    "textLength": 45230,
    "wordCount": 7842,
    "estimatedReadTime": "39m",
    "generatedFormats": ["cornellNotes", "flashcards", "quiz", "summary", "mindMap"],
    "flashcardCount": 30,
    "quizQuestionCount": 20
  },
  
  "status": "success"
}
```

---

## 🎨 Export Formats

### 1. **Professional PDF**
- Document metadata and source link
- Executive summary with key points
- Cornell Notes in formatted table
- All flashcards organized by difficulty
- Beautiful, print-ready layout

### 2. **Interactive HTML Quiz**
- Smooth animations and transitions
- "Show Answer" toggle for each question
- Correct answers with explanations
- Mobile-responsive design
- Direct link back to source

### 3. **Anki CSV**
- Standard 3-column format (Front, Back, Tags)
- Import directly to Anki desktop or mobile
- Pre-tagged for easy organization
- Ready for spaced repetition

### 4. **Notion Markdown**
- Callout blocks for flashcards and important info
- Clickable source links
- Formatted tables for Cornell Notes
- Color-coded difficulty indicators
- Mermaid mind maps
- Copy-paste ready

### 5. **JSON**
- Complete data structure
- Pretty-printed format
- Perfect for custom integrations
- All metadata included

---

## 🆚 Lumina PDF vs Alternatives

| Feature | Lumina PDF ✨ | Manual Notes | Basic Extractors | Other AI Tools |
| --- | --- | --- | --- | --- |
| **Multi-Format Support** | ✅ 7+ formats | ✅ All | ⚠️ Limited | ⚠️ PDF only |
| **Cornell Notes** | ✅ Professional | ⏱️ Hours | ❌ | ⚠️ Basic |
| **Anki Export** | ✅ CSV ready | ⏱️ Manual | ❌ | ❌ |
| **Interactive Quiz** | ✅ Styled HTML | ❌ | ❌ | ⚠️ Plain text |
| **PDF Export** | ✅ Professional | ❌ | ❌ | ❌ |
| **Mind Maps** | ✅ Mermaid | ⏱️ Manual | ❌ | ❌ |
| **Notion Format** | ✅ Callouts | ⏱️ Manual | ❌ | ⚠️ Basic |
| **Batch Processing** | ✅ Unlimited | ❌ | ⚠️ Limited | ⚠️ Limited |
| **No API Key** | ✅ Optional | N/A | ✅ | ❌ Required |
| **Processing Time** | ⭐ 1-2 min | ⏱️ Hours | ⭐ Fast | ⭐ 2-5 min |
| **Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |

---

## 💡 Use Cases

### 1. **Academic Research**
**Input**: 5 research papers (PDF)  
**Output**: 100 flashcards + comprehensive quiz + mind map  
**Result**: Master the literature review efficiently

### 2. **Textbook Study**
**Input**: Textbook chapter (PDF, EPUB)  
**Output**: Cornell notes + practice questions  
**Result**: Active learning instead of passive reading

### 3. **Professional Development**
**Input**: Technical documentation (HTML, MD)  
**Output**: Quick-reference flashcards + quiz  
**Result**: Certify faster with structured study

### 4. **Ebook Learning**
**Input**: Non-fiction ebook (EPUB)  
**Output**: Summary + key concepts flashcards  
**Result**: Retain more from your reading

### 5. **Lecture Notes Organization**
**Input**: Multiple lecture DOCX files  
**Output**: Unified study guide with all formats  
**Result**: Everything in one place for exam prep

---

## 🔧 Technical Details

### Document Processing
- **Encoding**: Auto-detects UTF-8, Latin-1, CP1252
- **Text Extraction**: Format-specific optimized parsers
- **Content Cleaning**: Removes headers, footers, page numbers
- **Large Documents**: Handles documents up to 100+ pages

### AI Generation
- **Model**: Claude Sonnet 4 (latest)
- **Context**: Full document text (up to ~15K characters shown to AI)
- **Quality**: Professional-grade educational content
- **Customization**: Adjustable difficulty and quantity

### Processing Time
- **Small document** (<10 pages): ~1 minute
- **Medium document** (10-50 pages): ~2 minutes
- **Large document** (50-100 pages): ~3-5 minutes
- **Batch**: Process multiple documents in parallel

---

## 🐛 Troubleshooting

### "Unable to extract text from document"
**Problem**: Document is corrupted, password-protected, or image-based PDF.  
**Solution**: Ensure document is not password-protected. For image PDFs, use OCR preprocessing.

### "Insufficient text extracted"
**Problem**: Document contains mostly images or is very short.  
**Solution**: Use documents with substantial text content (minimum ~500 words recommended).

### "Processing failed"
**Problem**: Document format not supported or file corrupted.  
**Solution**: Convert to supported format (PDF, DOCX) or try re-downloading the file.

### "API rate limit"
**Problem**: Too many requests in short time.  
**Solution**: Wait a few minutes or provide your own Anthropic API key for unlimited processing.

---

## 🎯 Best Practices

### For Best Results

✅ **Use clear, well-formatted documents** for better extraction  
✅ **Enable all formats** to get complete study ecosystem  
✅ **Batch similar documents** for efficient processing  
✅ **Review AI output** and add personal insights  
✅ **Export to Anki** for long-term retention with spaced repetition  
✅ **Use Notion format** for collaborative study with classmates

### Tips for Students

🎓 **Process materials immediately** after lectures  
🎓 **Use quiz feature** for self-testing before exams  
🎓 **Import flashcards to Anki** for daily review  
🎓 **Print PDF** for offline studying  
🎓 **Share Notion pages** with study groups  
🎓 **Combine with active recall** techniques

---

## 📈 Pricing

### Free Tier
- ✅ 5 documents per month
- ✅ All output formats
- ✅ Full feature access
- ✅ No credit card required

### Pay-As-You-Go
- 💰 $0.003 - $0.010 per document
- 💰 Depends on document length
- 💰 No subscription required
- 💰 Only pay for what you use

### Bring Your Own Key
- 🔑 Use your Anthropic API key
- 🔑 Pay Claude directly (~$0.003-0.015 per document)
- 🔑 Unlimited processing
- 🔑 Full control over costs

---

## 🏆 Why Students & Professionals Love Lumina PDF

> "Transformed my research workflow. I can now process 10 papers in the time it used to take me to read one!"  
> — Dr. Sarah K., PhD Candidate

> "The Anki flashcards alone are worth it. Saved me dozens of hours creating cards from textbooks."  
> — James L., Medical Student

> "Finally, a tool that works with ALL my document formats. Perfect for my ebook library!"  
> — Maria G., Lifelong Learner

> "The Cornell Notes are better than what I could create manually. This is my exam prep secret weapon."  
> — Alex R., College Senior

> "As a professional preparing for certifications, the quiz feature helps me test my knowledge efficiently."  
> — Michael T., IT Professional

---

## 🚀 Getting Started

1. Click **"Try for Free"** on the Apify platform
2. Paste your first document URL (PDF, DOCX, EPUB, etc.)
3. Select Cornell Notes, Flashcards, Quiz, Summary, and Mind Map
4. Click **"Start"**
5. Download your professional study materials in 2 minutes

**No credit card required. Start studying smarter today!**

---

## 📞 Support

* 🐛 **Issues**: [Open an issue on GitHub](https://github.com/favour-777/lumina-pdf/issues)
* 💬 **Questions**: Message through Apify platform
* 📧 **Email**: Contact via GitHub
* 📖 **Docs**: Check troubleshooting section above
* 💬 **Other**: Visit [GitHub profile](https://github.com/favour-777)

---

## 📜 License

MIT License - Free to use and modify

---

## 🙏 Acknowledgments

Built with:
* 🤖 Anthropic Claude Sonnet 4 for AI generation
* 📄 PyPDF2, python-docx, mammoth for document processing
* 📊 ReportLab for PDF generation
* 🎨 Apify platform for automation
* 💜 Love for learners everywhere

---

## 🔮 Roadmap

### Coming Soon
- ✨ PowerPoint (.pptx) support
- ✨ LaTeX (.tex) document support
- ✨ OCR for image-based PDFs
- ✨ Multi-language support (Spanish, French, German, etc.)
- ✨ Custom prompt templates
- ✨ Bulk download as ZIP
- ✨ Direct Notion integration
- ✨ Obsidian plugin format

### Future Ideas
- 🔮 Audio/video transcript processing
- 🔮 Collaborative study groups
- 🔮 Spaced repetition scheduling
- 🔮 Progress tracking dashboard
- 🔮 Mobile app

Have feature requests? [Open an issue!](https://github.com/favour-777/lumina-pdf/issues)

---

**Made with 💛 for learners who want to study smarter, not harder.**

**Lumina PDF — Transform Any Document into Your Personal Study System**

---

## 🆕 What's New vs Original Lumina

| Feature | Original Lumina (YouTube) | Lumina PDF (New) |
| --- | --- | --- |
| **Input** | YouTube videos only | 7+ document formats |
| **Source** | Video transcripts | PDFs, DOCX, EPUB, TXT, MD, HTML, RTF |
| **Flexibility** | YouTube-dependent | Any document source |
| **Formats** | Same great outputs | Same + enhanced |
| **Use Cases** | Online lectures | Research, textbooks, ebooks, articles |

**Same great study materials, now works with ANY document!** 🎉