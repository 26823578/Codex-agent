import numpy as np
import faiss
from typing import List, Tuple, Dict, Any
from openai import OpenAI
from tqdm import tqdm
from src.config import Config
from src.document_processor import TextChunk

class VectorStore:
    """FAISS-based vector store for semantic search"""
    
    def __init__(self):
        self.config = Config()
        self.index = None
        self.chunks: List[TextChunk] = []
        self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
        
    def add_chunks(self, chunks: List[TextChunk]):
        """Add text chunks to the vector store"""
        if not chunks:
            return
        
        self.chunks = chunks
        print(f"Generating embeddings for {len(chunks)} chunks...")
        
        # Generate embeddings for all chunks
        embeddings = self._generate_embeddings([chunk.content for chunk in chunks])
        
        # Create FAISS index
        self.index = faiss.IndexFlatIP(self.config.VECTOR_DIM)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        embeddings_normalized = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Add to index
        self.index.add(embeddings_normalized.astype('float32'))
    
    def search(self, query: str, top_k: int = None) -> List[Tuple[TextChunk, float]]:
        """Search for similar chunks"""
        if self.index is None or len(self.chunks) == 0:
            return []
        
        if top_k is None:
            top_k = self.config.TOP_K_RESULTS
        
        # Generate query embedding
        query_embedding = self._generate_embeddings([query])[0]
        query_embedding_normalized = query_embedding / np.linalg.norm(query_embedding)
        
        # Search
        scores, indices = self.index.search(
            query_embedding_normalized.reshape(1, -1).astype('float32'), 
            top_k
        )
        
        # Return results with similarity scores
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks) and score > self.config.SIMILARITY_THRESHOLD:
                results.append((self.chunks[idx], float(score)))
        
        return results
    
    def _generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using OpenAI API with progress tracking"""
        try:
            # Process in batches to avoid rate limits
            batch_size = 100
            all_embeddings = []
            
            for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
                batch = texts[i:i + batch_size]
                response = self.client.embeddings.create(
                    model=self.config.EMBEDDING_MODEL,
                    input=batch
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
            
            return np.array(all_embeddings)
            
        except Exception as e:
            raise ValueError(f"Error generating embeddings: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        if not self.chunks:
            return {
                'num_documents': 0,
                'num_chunks': 0,
                'total_tokens': 0,
                'avg_tokens_per_chunk': 0
            }
        
        # Count unique documents
        sources = set(chunk.metadata.get('source', 'unknown') for chunk in self.chunks)
        total_tokens = sum(chunk.token_count for chunk in self.chunks)
        
        return {
            'num_documents': len(sources),
            'num_chunks': len(self.chunks),
            'total_tokens': total_tokens,
            'avg_tokens_per_chunk': total_tokens / len(self.chunks) if self.chunks else 0,
            'sources': list(sources)
        }
    
    def get_all_chunks(self) -> List[TextChunk]:
        """Get all stored chunks"""
        return self.chunks.copy()
    
    def clear(self):
        """Clear the vector store"""
        self.index = None
        self.chunks = []