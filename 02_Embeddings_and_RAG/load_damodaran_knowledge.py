#!/usr/bin/env python3
"""
Load Professor Damodaran Knowledge Base for Jupyter Notebook
This script loads the saved knowledge base files and creates a vector database
"""

import os
import asyncio
from aimakerspace.text_utils import CharacterTextSplitter
from aimakerspace.vectordatabase import VectorDatabase

def load_damodaran_knowledge_base():
    """
    Load the saved Professor Damodaran knowledge base
    """
    print("🎓 Loading Professor Damodaran Knowledge Base")
    print("=" * 50)
    
    # Check if files exist
    if not os.path.exists('damodaran_chunks.txt'):
        print("❌ damodaran_chunks.txt not found!")
        print("Please run youtube_api_damodaran_scraper.py first to create the knowledge base.")
        return None
    
    # Read chunks from file
    print("📖 Reading chunks from file...")
    with open('damodaran_chunks.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into individual chunks
    chunks = []
    current_chunk = ""
    
    for line in content.split('\n'):
        if line.startswith('=== CHUNK'):
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = ""
        else:
            current_chunk += line + '\n'
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    print(f"✅ Loaded {len(chunks)} chunks")
    
    # Create vector database
    print("🔄 Creating vector database...")
    vector_db = VectorDatabase()
    vector_db = asyncio.run(vector_db.abuild_from_list(chunks))
    
    print(f"✅ Professor Damodaran knowledge base loaded with {len(vector_db.vectors)} vectors")
    
    return vector_db

def test_knowledge_base(vector_db):
    """
    Test the loaded knowledge base
    """
    print(f"\n🧪 Testing Loaded Knowledge Base")
    print("=" * 40)
    
    test_queries = [
        "What is the DCF model and how do you use it?",
        "How do you calculate the cost of capital?",
        "What are the key principles of valuation?"
    ]
    
    for query in test_queries:
        print(f"\n--- Query: {query} ---")
        
        results = vector_db.search_by_text(query, k=2)
        print(f"Found {len(results)} relevant insights:")
        
        for i, (text, similarity) in enumerate(results):
            print(f"\n  Insight {i+1} (similarity: {similarity:.4f}):")
            print(f"    💡 Content: {text[:200]}...")

if __name__ == "__main__":
    # Load the knowledge base
    vector_db = load_damodaran_knowledge_base()
    
    if vector_db:
        # Test it
        test_knowledge_base(vector_db)
        print(f"\n🎉 Knowledge base is ready for use in Jupyter notebook!")
    else:
        print("❌ Failed to load knowledge base")
