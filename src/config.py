import os
from dataclasses import dataclass

@dataclass
class Config:
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Chunking Configuration
    CHUNK_SIZE: int = 450  # tokens
    CHUNK_OVERLAP: int = 50  # tokens
    
    # RAG Configuration
    TOP_K_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Vector Store Configuration
    VECTOR_DIM: int = 1536  # dimension for text-embedding-3-small
    
    # File Processing
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    SUPPORTED_EXTENSIONS: list = None
    
    def __post_init__(self):
        if self.SUPPORTED_EXTENSIONS is None:
            self.SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.txt', '.md']
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        return True