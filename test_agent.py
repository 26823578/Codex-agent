#!/usr/bin/env python3
"""
Simple test script for the Personal Codex Agent
Run this to verify everything works without the full UI
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore
from src.chat_agent import ChatAgent
from src.config import Config

def create_sample_document():
    """Create a sample document for testing"""
    sample_content = """
John Doe - Software Engineer

TECHNICAL SKILLS:
- Python, JavaScript, React
- Machine Learning, TensorFlow
- Cloud platforms: AWS, GCP
- Databases: PostgreSQL, MongoDB

EXPERIENCE:
Software Engineer at TechCorp (2021-2023)
- Built scalable web applications using React and Node.js
- Implemented ML models for customer recommendation systems
- Led a team of 3 junior developers
- Improved system performance by 40%

PROJECTS:
1. E-commerce Platform
   - Full-stack web application with 10k+ users
   - Technologies: React, Node.js, PostgreSQL
   - Features: user auth, payment processing, admin dashboard

2. AI Chatbot
   - Natural language processing chatbot
   - Technologies: Python, TensorFlow, Flask
   - Achieved 95% accuracy in intent recognition

EDUCATION:
BSc Computer Science, University of Tech (2017-2021)
- First Class Honours
- Thesis: "Deep Learning for Natural Language Processing"

PERSONAL VALUES:
I believe in continuous learning and collaborative teamwork. 
I'm passionate about using technology to solve real-world problems 
and creating user-friendly applications that make a difference.
"""
    
    with open("sample_cv.txt", "w") as f:
        f.write(sample_content)
    
    return "sample_cv.txt"

def test_system():
    """Test the complete system end-to-end"""
    load_dotenv()
    
    print("🤖 Testing Personal Codex Agent...")
    
    # Check configuration
    try:
        Config.validate()
        print("✅ Configuration valid")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Create sample document
    print("\n📄 Creating sample document...")
    sample_file = create_sample_document()
    
    try:
        # Test document processing
        print("🔄 Testing document processing...")
        processor = DocumentProcessor()
        chunks = processor.process_documents([sample_file])
        print(f"✅ Processed {len(chunks)} chunks")
        
        # Test vector store
        print("🔍 Testing vector store...")
        vector_store = VectorStore()
        vector_store.add_chunks(chunks)
        print("✅ Vector store created")
        
        # Test search
        search_results = vector_store.search("What are the technical skills?")
        print(f"✅ Search returned {len(search_results)} results")
        
        # Test chat agent
        print("💬 Testing chat agent...")
        agent = ChatAgent(vector_store)
        
        # Test questions
        test_questions = [
            "What kind of engineer are you?",
            "What are your strongest technical skills?",
            "Tell me about your projects"
        ]
        
        for question in test_questions:
            print(f"\n❓ Question: {question}")
            response = agent.get_response(question, mode="interview")
            print(f"✅ Response: {response[:100]}...")
        
        # Test different modes
        print(f"\n🎭 Testing different modes...")
        for mode in ["interview", "story", "fast", "humble_brag"]:
            response = agent.get_response("What projects are you proud of?", mode=mode)
            print(f"✅ Mode '{mode}': {len(response)} chars")
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        # Cleanup
        if os.path.exists(sample_file):
            os.remove(sample_file)

if __name__ == "__main__":
    success = test_system()
    sys.exit(0 if success else 1)