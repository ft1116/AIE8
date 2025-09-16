#!/usr/bin/env python3
"""
Simple example of using MultiYouTubeLoader
"""

import os
import asyncio
from dotenv import load_dotenv
from aimakerspace.text_utils import MultiYouTubeLoader, CharacterTextSplitter
from aimakerspace.vectordatabase import VectorDatabase

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

os.environ["OPENAI_API_KEY"] = api_key

# Example: Load multiple YouTube videos
youtube_urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll
    "https://www.youtube.com/watch?v=9bZkp7q19f0",  # PSY - GANGNAM STYLE
    # Add more URLs here
]

print("🎥 Multi-YouTube RAG Example")
print("=" * 40)

# Step 1: Load all videos
print("📺 Loading multiple YouTube videos...")
multi_loader = MultiYouTubeLoader(youtube_urls)
documents = multi_loader.load_documents()

# Step 2: Create vector database
print("\n🔄 Creating vector database...")
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_texts(documents)

vector_db = VectorDatabase()
vector_db = asyncio.run(vector_db.abuild_from_list(chunks))

# Step 3: Search across all videos
print("\n🔍 Searching across all videos...")
query = "What are the main themes across all videos?"
results = vector_db.search_by_text(query, k=3)

print(f"Query: {query}")
for i, (text, similarity) in enumerate(results):
    if "VIDEO:" in text:
        video_id = text.split("VIDEO:")[1].split("|")[0].strip()
        clean_text = text.split("|", 1)[1].strip() if "|" in text else text
        print(f"\nResult {i+1} (similarity: {similarity:.4f}):")
        print(f"  📺 From video: {video_id}")
        print(f"  📝 Content: {clean_text[:200]}...")

print("\n✅ Multi-YouTube RAG example completed!")
