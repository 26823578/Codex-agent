import streamlit as st
import os
from dotenv import load_dotenv
from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore
from src.chat_agent import ChatAgent
from src.config import Config
import time

# Load environment variables
load_dotenv()

def initialize_session_state():
    """Initialize session state variables"""
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = None
    if 'chat_agent' not in st.session_state:
        st.session_state.chat_agent = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'documents_ingested' not in st.session_state:
        st.session_state.documents_ingested = False

def main():
    st.set_page_config(
        page_title="Personal Codex Agent",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    initialize_session_state()
    
    st.title("🤖 Personal Codex Agent")
    st.markdown("*A context-aware agent that knows you as a candidate*")
    
    # Sidebar for document management
    with st.sidebar:
        st.header("📄 Document Management")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload your documents",
            type=['pdf', 'txt'],  # Removed docx since python-docx not in requirements
            accept_multiple_files=True,
            help="Upload your CV, README files, blog posts, or any personal documents (PDF, TXT)"
        )
        
        # Process documents button
        if st.button("🔄 Process Documents", type="primary"):
            if uploaded_files:
                process_documents(uploaded_files)
            else:
                st.warning("Please upload at least one document first.")
        
        # Re-run ingest button
        if st.session_state.documents_ingested:
            if st.button("🔄 Re-run Ingest"):
                if uploaded_files:
                    process_documents(uploaded_files)
                else:
                    st.warning("Please upload documents first.")
        
        # Status indicator
        if st.session_state.documents_ingested:
            st.success("✅ Documents processed and ready!")
        else:
            st.info("📤 Upload documents to get started")
        
        st.markdown("---")
        
        # Mode selection
        st.header("🎭 Response Mode")
        mode = st.selectbox(
            "Choose response style:",
            options=["interview", "story", "fast", "humble_brag"],
            format_func=lambda x: {
                "interview": "🎯 Interview Mode",
                "story": "📖 Personal Storytelling",
                "fast": "⚡ Fast Facts",
                "humble_brag": "💪 Confident Mode"
            }[x]
        )
        
        st.markdown("---")
        
        # Sample questions
        st.header("💡 Sample Questions")
        sample_questions = [
            "What kind of engineer are you?",
            "What are your strongest technical skills?",
            "What projects are you most proud of?",
            "What do you value in team culture?",
            "How do you approach learning new things?"
        ]
        
        for question in sample_questions:
            if st.button(f"Ask: {question}", key=f"sample_{question}"):
                st.session_state.current_question = question
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("💬 Chat Interface")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for i, (q, a) in enumerate(st.session_state.chat_history):
                st.markdown(f"**You:** {q}")
                st.markdown(f"**Agent:** {a}")
                st.markdown("---")
        
        # Chat input
        if st.session_state.documents_ingested:
            question = st.text_input(
                "Ask me anything about the candidate:",
                value=getattr(st.session_state, 'current_question', ''),
                key="question_input"
            )
            
            if st.button("Send", type="primary") or question:
                if question.strip():
                    with st.spinner("Thinking..."):
                        response = get_agent_response(question, mode)
                        st.session_state.chat_history.append((question, response))
                        if hasattr(st.session_state, 'current_question'):
                            delattr(st.session_state, 'current_question')
                        st.experimental_rerun()
        else:
            st.info("Please upload and process documents first to start chatting.")
    
    with col2:
        st.header("📊 Stats")
        if st.session_state.vector_store:
            stats = st.session_state.vector_store.get_stats()
            st.metric("Documents", stats.get('num_documents', 0))
            st.metric("Text Chunks", stats.get('num_chunks', 0))
        
        st.header("🔧 System Info")
        st.text(f"OpenAI API: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")
        st.text(f"Model: {Config.OPENAI_MODEL}")
        st.text(f"Embedding: {Config.EMBEDDING_MODEL}")

def process_documents(uploaded_files):
    """Process uploaded documents and create vector store"""
    with st.spinner("Processing documents..."):
        try:
            # Initialize processor
            processor = DocumentProcessor()
            
            # Save uploaded files temporarily
            temp_files = []
            for uploaded_file in uploaded_files:
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                temp_files.append(temp_path)
            
            # Process documents
            chunks = processor.process_documents(temp_files)
            
            # Create vector store
            vector_store = VectorStore()
            vector_store.add_chunks(chunks)
            
            # Initialize chat agent
            chat_agent = ChatAgent(vector_store)
            
            # Update session state
            st.session_state.vector_store = vector_store
            st.session_state.chat_agent = chat_agent
            st.session_state.documents_ingested = True
            
            # Clean up temp files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            st.success(f"✅ Successfully processed {len(uploaded_files)} documents with {len(chunks)} chunks!")
            
        except Exception as e:
            st.error(f"Error processing documents: {str(e)}")

def get_agent_response(question, mode):
    """Get response from chat agent"""
    try:
        if st.session_state.chat_agent:
            return st.session_state.chat_agent.get_response(question, mode)
        else:
            return "Please upload and process documents first."
    except Exception as e:
        return f"Error generating response: {str(e)}"

if __name__ == "__main__":
    main()