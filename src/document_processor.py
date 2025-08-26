import os
import re
from typing import List, Dict, Any
import tiktoken
from PyPDF2 import PdfReader
from docx import Document
from src.config import Config

class TextChunk:
    """Represents a chunk of text with metadata"""
    def __init__(self, content: str, metadata: Dict[str, Any]):
        self.content = content
        self.metadata = metadata
        self.token_count = self._count_tokens(content)
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken"""
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except:
            # Fallback to word count * 1.3 as rough estimate
            return int(len(text.split()) * 1.3)
    
    def __repr__(self):
        return f"TextChunk(tokens={self.token_count}, source={self.metadata.get('source', 'unknown')})"

class DocumentProcessor:
    """Handles document loading, parsing, and chunking"""
    
    def __init__(self):
        self.config = Config()
    
    def process_documents(self, file_paths: List[str]) -> List[TextChunk]:
        """Process multiple documents and return text chunks"""
        all_chunks = []
        
        for file_path in file_paths:
            try:
                chunks = self._process_single_document(file_path)
                all_chunks.extend(chunks)
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue
        
        return all_chunks
    
    def _process_single_document(self, file_path: str) -> List[TextChunk]:
        """Process a single document"""
        # Extract text based on file type
        text = self._extract_text(file_path)
        
        if not text.strip():
            return []
        
        # Create metadata
        metadata = {
            'source': os.path.basename(file_path),
            'file_type': os.path.splitext(file_path)[1].lower(),
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
        }
        
        # Chunk the text
        chunks = self._chunk_text(text, metadata)
        
        return chunks
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from different file types"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif ext == '.docx':
            return self._extract_from_docx(file_path)
        elif ext in ['.txt', '.md']:
            return self._extract_from_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Error reading PDF: {str(e)}")
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Error reading DOCX: {str(e)}")
    
    def _extract_from_text(self, file_path: str) -> str:
        """Extract text from plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                raise ValueError(f"Error reading text file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error reading text file: {str(e)}")
    
    def _chunk_text(self, text: str, base_metadata: Dict[str, Any]) -> List[TextChunk]:
        """Chunk text into smaller pieces with sentence boundary awareness"""
        # First, split by sentences
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)
            
            # If adding this sentence would exceed chunk size, finalize current chunk
            if current_tokens + sentence_tokens > self.config.CHUNK_SIZE and current_chunk:
                # Create chunk with metadata
                metadata = {
                    **base_metadata,
                    'chunk_index': chunk_index,
                    'chunk_type': 'text'
                }
                
                chunk = TextChunk(current_chunk.strip(), metadata)
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk, self.config.CHUNK_OVERLAP)
                current_chunk = overlap_text + " " + sentence if overlap_text else sentence
                current_tokens = self._count_tokens(current_chunk)
                chunk_index += 1
            else:
                # Add sentence to current chunk
                current_chunk += " " + sentence if current_chunk else sentence
                current_tokens += sentence_tokens
        
        # Add final chunk if it has content
        if current_chunk.strip():
            metadata = {
                **base_metadata,
                'chunk_index': chunk_index,
                'chunk_type': 'text'
            }
            chunk = TextChunk(current_chunk.strip(), metadata)
            chunks.append(chunk)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex"""
        # Clean up text
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        
        # Split on sentence endings, but be careful with abbreviations
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
        sentences = re.split(sentence_pattern, text)
        
        # Filter out very short sentences
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        return sentences
    
    def _get_overlap_text(self, text: str, max_tokens: int) -> str:
        """Get the last part of text up to max_tokens for overlap"""
        if max_tokens <= 0:
            return ""
        
        words = text.split()
        overlap_words = []
        token_count = 0
        
        # Build overlap from end of text
        for word in reversed(words):
            word_tokens = self._count_tokens(word)
            if token_count + word_tokens > max_tokens:
                break
            overlap_words.insert(0, word)
            token_count += word_tokens
        
        return " ".join(overlap_words)
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except:
            # Fallback estimation
            return int(len(text.split()) * 1.3)