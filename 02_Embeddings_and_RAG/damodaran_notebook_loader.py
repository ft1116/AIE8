# Professor Damodaran Knowledge Base Loader - Jupyter Notebook Cell
# Copy and paste this code into a Jupyter notebook cell

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

# Load the knowledge base
damodaran_vector_db = load_damodaran_knowledge_base()

if damodaran_vector_db:
    print(f"\n🎉 Professor Damodaran knowledge base is ready!")
    print(f"💡 You can now use 'damodaran_vector_db' to search for finance insights")
    
    # Quick test
    print(f"\n🧪 Quick Test:")
    test_query = "What is the DCF model?"
    results = damodaran_vector_db.search_by_text(test_query, k=1)
    
    if results:
        text, similarity = results[0]
        print(f"Query: {test_query}")
        print(f"Best match (similarity: {similarity:.4f}):")
        print(f"  {text[:200]}...")
    
    print(f"\n📚 Usage in your RAG system:")
    print(f"  # Search for insights")
    print(f"  results = damodaran_vector_db.search_by_text('your question', k=3)")
    print(f"  # Use results in your RAG pipeline")
else:
    print("❌ Failed to load knowledge base")
