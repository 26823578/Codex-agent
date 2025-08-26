# Codex-agent
Personal Codex Agent
A context-aware RAG-based chatbot that answers questions about you as a candidate, built for the Ubundi AI Graduate Engineer trial project.
🎯 Overview
This agent ingests your personal documents (CV, README files, blog posts, etc.) and creates a conversational interface that can answer questions about your background, skills, projects, and values in your own voice.
✨ Features

Document Processing: Supports PDF, DOCX, and TXT files
Smart Chunking: Sentence-boundary aware chunking with configurable overlap
Vector Search: FAISS-powered semantic search with OpenAI embeddings
Multiple Response Modes:

🎯 Interview Mode: Professional, concise answers for job interviews
📖 Personal Storytelling: Narrative, reflective responses with context
⚡ Fast Facts: Quick bullet-point style answers
💪 Confident Mode: Achievement-focused responses that highlight strengths


Clean UI: Streamlit-based interface with document management and chat
Real-time Stats: Track processed documents and chunks

🚀 Quick Start
Prerequisites

Python 3.8+
OpenAI API key

Installation

Clone the repository:

bashgit clone <your-repo-url>
cd personal-codex-agent

Install dependencies:

bashpip install -r requirements.txt

Set up environment:

bashcp .env.example .env
# Edit .env and add your OpenAI API key

Run the application:

bashstreamlit run app.py
📖 Usage
Document Upload

Upload your documents (PDF, DOCX, TXT) using the sidebar
Click "Process Documents" to ingest and vectorize the content
Wait for confirmation that processing is complete

Chatting with Your Agent

Select a response mode from the sidebar
Ask questions about yourself in the main chat interface
Try the sample questions or ask your own

Sample Questions

"What kind of engineer are you?"
"What are your strongest technical skills?"
"What projects or experiences are you most proud of?"
"What do you value in a team or company culture?"
"What's your approach to learning or debugging something new?"

🏗️ Architecture
System Design
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │ Document         │    │ Vector Store    │
│                 │────│ Processor        │────│ (FAISS)         │
│ • File Upload   │    │                  │    │                 │
│ • Chat Interface│    │ • PDF/DOCX/TXT   │    │ • Embeddings    │
│ • Mode Selector │    │ • Smart Chunking │    │ • Similarity    │
└─────────────────┘    │ • Sentence Aware │    │   Search        │
                       └──────────────────┘    └─────────────────┘
                                ↓                        ↓
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Text Chunks      │    │ Chat Agent      │
                       │                  │    │                 │
                       │ • Content        │    │ • Context       │
                       │ • Metadata       │    │   Retrieval     │
                       │ • Token Count    │────│ • LLM Response  │
                       └──────────────────┘    │ • Mode Handling │
                                               └─────────────────┘
Key Components

DocumentProcessor: Extracts and chunks text from various file formats
VectorStore: FAISS-based vector database for semantic search
ChatAgent: RAG-powered conversational interface with multiple modes
Config: Centralized configuration management

Data Flow

Ingestion: Documents → Text Extraction → Smart Chunking → Embeddings → Vector Store
Query: Question → Embedding → Similarity Search → Context Retrieval → LLM → Response

⚙️ Configuration
Key settings in src/config.py:
pythonCHUNK_SIZE = 450          # Target tokens per chunk
CHUNK_OVERLAP = 50        # Overlap tokens between chunks
TOP_K_RESULTS = 5         # Number of context chunks to retrieve
SIMILARITY_THRESHOLD = 0.7 # Minimum similarity for relevance
OPENAI_MODEL = "gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-3-small"
📊 Technical Specifications

Chunking Strategy: Sentence-boundary aware with token counting
Embedding Model: OpenAI text-embedding-3-small (1536 dimensions)
Vector Database: FAISS with cosine similarity
LLM: GPT-3.5-turbo with mode-specific prompting
Supported Formats: PDF, DOCX, TXT, MD

🧪 Testing
Test the system with various document types and question styles:
bash# Example test documents to include:
# - Your CV/resume
# - README files from your projects  
# - Blog posts or articles you've written
# - Code documentation with comments
# - Personal notes about your work style
🔮 Future Enhancements
Immediate Improvements (with more time):

Advanced Chunking: Implement hierarchical or context-aware chunking
Memory Management: Add conversation history and follow-up context
Better UI: Enhanced chat interface with message threading
Document Highlighting: Show which parts of documents informed each answer
Export Features: Save conversations or generate candidate summaries

RAG Enhancements:

Hybrid Search: Combine semantic and keyword-based retrieval
Query Expansion: Automatically expand questions for better context retrieval
Source Attribution: Clearly cite which documents contributed to each answer
Confidence Scoring: Add confidence levels to responses

Advanced Features:

Multi-modal Support: Process images, charts, and diagrams from documents
Real-time Updates: Live document updates without full reprocessing
Analytics Dashboard: Insights into question patterns and document usage
API Integration: REST API for programmatic access

🛠️ Development Notes
Design Decisions

FAISS over Pinecone/Weaviate: Chosen for simplicity and local deployment
Sentence-boundary Chunking: Preserves semantic integrity over rigid token limits
Multiple Response Modes: Addresses different interview contexts and styles
Streamlit UI: Rapid prototyping while maintaining professional appearance

Error Handling

Graceful handling of unsupported file formats
API rate limiting and retry logic
Fallback token counting when tiktoken fails
Clear error messages in the UI

Performance Considerations

Batch embedding generation to reduce API calls
Normalized vectors for efficient cosine similarity
In-memory FAISS index for fast retrieval
Configurable chunk sizes for different document types

📝 Show Your Thinking Artifacts
AI Collaboration Process
This project was built with extensive AI assistance. Here's how the collaboration worked:
1. System Architecture Planning
Prompt: "Design a complete RAG system architecture for a personal chatbot with document ingestion, vector storage, and multiple response modes"
AI Response: Provided the overall system design with component breakdown, data flow, and technology stack recommendations.
Human Refinement: Adjusted chunking strategy to be sentence-aware and added mode-specific prompting.
2. Document Processing Implementation
Prompt: "Implement a document processor that handles PDF, DOCX, and TXT files with smart chunking that respects sentence boundaries"
AI Generated: Complete DocumentProcessor class with file type detection, text extraction, and token-aware chunking.
Manual Edits: Added better error handling and fallback encoding detection.
3. Vector Store Development
Prompt: "Create a FAISS-based vector store with OpenAI embeddings that supports similarity search with configurable thresholds"
AI Generated: Full VectorStore implementation with embedding generation, indexing, and search functionality.
Human Optimization: Added batch processing for embeddings and better similarity scoring.
4. Chat Agent Logic
Prompt: "Build a chat agent that uses RAG to answer questions with different personality modes (interview, story, fast facts, confident)"
AI Generated: Complete agent with mode-specific prompting and context assembly.
Refinement: Enhanced system prompts and added better context formatting.
5. Streamlit UI Creation
Prompt: "Create a professional Streamlit interface with file upload, document processing, chat interface, and mode selection"
AI Generated: Full UI implementation with sidebar controls and main chat area.
Manual Polish: Added status indicators, error handling, and improved UX flow.
Code Generation Breakdown

~85% AI Generated: Core functionality, class structures, algorithm implementations
~15% Manual Editing: Error handling, UX improvements, configuration tuning

Agent Instructions Used
You are a senior software engineer specializing in RAG systems and document processing. 
Build production-ready code with:
- Proper error handling
- Clean architecture
- Type hints where appropriate  
- Comprehensive documentation
- Scalable design patterns
Iteration Examples
Initial Chunking Approach: Fixed 450-token chunks
Problem: Sentences cut mid-way, poor semantic coherence
Solution: Sentence-boundary aware chunking with token counting
Result: Better context retrieval and more coherent responses
🔐 Security & Privacy

Environment variables for API keys
Local vector storage (no external vector DB)
No persistent storage of uploaded documents
Rate limiting considerations for API usage



Built with ❤️ for the Ubundi AI Graduate Engineer trial project