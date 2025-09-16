#!/usr/bin/env python3
"""
Setup guide for YouTube API to scrape Professor Damodaran videos
"""

def setup_youtube_api():
    """
    Guide for setting up YouTube API
    """
    print("🎓 YouTube API Setup Guide for Professor Damodaran Videos")
    print("=" * 60)
    
    print("\n📋 Step 1: Get YouTube API Key")
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable YouTube Data API v3:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'YouTube Data API v3'")
    print("   - Click 'Enable'")
    print("4. Create credentials:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'API Key'")
    print("   - Copy the API key")
    
    print("\n🔑 Step 2: Set Environment Variable")
    print("In your terminal, run:")
    print("export YOUTUBE_API_KEY='your_api_key_here'")
    print("\nOr add to your .bashrc/.zshrc:")
    print("echo 'export YOUTUBE_API_KEY=\"your_api_key_here\"' >> ~/.bashrc")
    
    print("\n📺 Step 3: Professor Damodaran's Channel")
    print("Main channel: https://www.youtube.com/@AswathDamodaran")
    print("Channel ID: UCKn6CPi8h4IG3g4ga5FgKfQ")
    
    print("\n🔍 Step 4: Search Terms")
    print("The scraper will search for:")
    search_terms = [
        "Aswath Damodaran",
        "Professor Damodaran", 
        "Damodaran valuation",
        "Damodaran corporate finance",
        "Damodaran investment",
        "Damodaran DCF",
        "Damodaran risk",
        "Damodaran NYU",
        "Damodaran lectures",
        "Damodaran equity valuation"
    ]
    for term in search_terms:
        print(f"  - {term}")
    
    print("\n⚙️ Step 5: Run the Scraper")
    print("python youtube_api_damodaran_scraper.py")
    
    print("\n💡 Tips:")
    print("- The API has quotas (10,000 units/day for free)")
    print("- Each search costs ~100 units")
    print("- Video details cost ~1 unit per video")
    print("- Start with fewer results to test")
    
    print("\n🎯 Expected Results:")
    print("- 50+ videos from his channel")
    print("- 100+ videos from keyword searches")
    print("- Filtered to high-quality, relevant content")
    print("- Comprehensive knowledge base for RAG")

if __name__ == "__main__":
    setup_youtube_api()

