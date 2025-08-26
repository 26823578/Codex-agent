import os
import re
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pypdf
from sentence_transformers import SentenceTransformer
import nltk
from tqdm import tqdm
from src.config import Config

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

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
    """Handles document loading, parsing, and chunking using LangChain"""
    
    def __init__(self):
        self.config = Config()
        # Initialize text splitter with sentence awareness
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def process_documents(self, file_paths: List[str]) -> List[TextChunk]:
        """Process multiple documents and return text chunks"""
        all_chunks = []
        
        print("Processing documents...")
        for file_path in tqdm(file_paths, desc="Documents"):
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
        """Extract text from PDF using pypdf"""
        try:
            with open(file_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Error reading PDF: {str(e)}")
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX - fallback to simple text reading"""
        try:
            # Since python-docx is not in requirements, treat as text file
            return self._extract_from_text(file_path)
        except Exception as e:
            raise ValueError(f"Error reading DOCX (treating as text): {str(e)}")
    
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
        """Chunk text using LangChain's RecursiveCharacterTextSplitter"""
        # Use LangChain's text splitter
        text_chunks = self.text_splitter.split_text(text)
        
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            if not chunk_text.strip():
                continue
                
            metadata = {
                **base_metadata,
                'chunk_index': i,
                'chunk_type': 'text'
            }
            
            chunk = TextChunk(chunk_text.strip(), metadata)
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
        """Count tokens in text - simplified character-based estimation"""
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    # Remove unused methods that were replaced by LangChain
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using NLTK"""
        from nltk.tokenize import sent_tokenize
        return sent_tokenize(text)
    
    def _get_overlap_text(self, text: str, max_chars: int) -> str:
        """Get the last part of text up to max_chars for overlap"""
        if max_chars <= 0:
            return ""
        return text[-max_chars:] if len(text) > max_chars else text