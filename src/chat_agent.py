from openai import OpenAI
from typing import List, Dict
from src.vector_store import VectorStore
from src.config import Config

class ChatAgent:
    """Chat agent that uses RAG to answer questions about the candidate"""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.config = Config()
        self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
        
        # Mode-specific prompts
        self.mode_prompts = {
            "interview": {
                "style": "professional, concise, and informative",
                "instruction": "Answer as if in a job interview - be direct, highlight key achievements, and demonstrate competence."
            },
            "story": {
                "style": "narrative, reflective, and detailed",
                "instruction": "Tell stories with context, emotions, and lessons learned. Be personal and engaging."
            },
            "fast": {
                "style": "brief, bullet-pointed, and to-the-point",
                "instruction": "Provide quick, scannable answers in bullet points or short paragraphs."
            },
            "humble_brag": {
                "style": "confident, achievement-focused, and slightly promotional",
                "instruction": "Highlight impressive accomplishments and skills while staying grounded in truth."
            }
        }
    
    def get_response(self, question: str, mode: str = "interview") -> str:
        """Generate a response to a question using RAG"""
        try:
            # Retrieve relevant context
            search_results = self.vector_store.search(question, top_k=5)
            
            if not search_results:
                return "I don't have enough information in the provided documents to answer that question."
            
            # Build context from retrieved chunks
            context_chunks = []
            for chunk, score in search_results:
                context_chunks.append({
                    'content': chunk.content,
                    'source': chunk.metadata.get('source', 'unknown'),
                    'score': score
                })
            
            # Generate response using LLM
            response = self._generate_llm_response(question, context_chunks, mode)
            
            return response
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _generate_llm_response(self, question: str, context_chunks: List[Dict], mode: str) -> str:
        """Generate response using OpenAI LLM"""
        
        # Build context string
        context_str = ""
        for i, chunk in enumerate(context_chunks, 1):
            context_str += f"\n--- Context {i} (from {chunk['source']}) ---\n"
            context_str += chunk['content']
            context_str += f"\n(Similarity: {chunk['score']:.3f})\n"
        
        # Get mode configuration
        mode_config = self.mode_prompts.get(mode, self.mode_prompts["interview"])
        
        # Build system prompt
        system_prompt = f"""You are a personal AI agent representing a job candidate based on their provided documents.

RESPONSE MODE: {mode.upper()}
Style: {mode_config['style']}
Instruction: {mode_config['instruction']}

GUIDELINES:
1. Answer questions about the candidate using ONLY the provided context
2. Speak in first person as if you ARE the candidate
3. Reference specific experiences, projects, or skills mentioned in the documents
4. If information is not in the context, say so honestly
5. Match the requested response style and tone
6. Be authentic and true to what's in the documents

CONTEXT FROM CANDIDATE'S DOCUMENTS:
{context_str}

Remember: You are answering AS the candidate, not ABOUT the candidate."""

        # Build user prompt
        user_prompt = f"Question: {question}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"
    
    def get_self_reflection(self, topic: str) -> str:
        """Generate self-reflective responses about working style, growth areas, etc."""
        reflection_prompt = f"""Based on the candidate's documents, provide a thoughtful self-reflection on: {topic}

Consider:
- What patterns emerge from their experiences?
- What do their choices reveal about their values?
- How do they approach challenges and growth?
- What might energize or drain them based on their background?

Be honest, insightful, and authentic to what the documents reveal."""
        
        return self.get_response(reflection_prompt, mode="story")