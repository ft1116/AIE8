import os
import re
from typing import List
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


class TextFileLoader:
    def __init__(self, path: str, encoding: str = "utf-8"):
        self.documents = []
        self.path = path
        self.encoding = encoding

    def load(self):
        if os.path.isdir(self.path):
            self.load_directory()
        elif os.path.isfile(self.path) and self.path.endswith(".txt"):
            self.load_file()
        else:
            raise ValueError(
                "Provided path is neither a valid directory nor a .txt file."
            )

    def load_file(self):
        with open(self.path, "r", encoding=self.encoding) as f:
            self.documents.append(f.read())

    def load_directory(self):
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.endswith(".txt"):
                    with open(
                        os.path.join(root, file), "r", encoding=self.encoding
                    ) as f:
                        self.documents.append(f.read())

    def load_documents(self):
        self.load()
        return self.documents


class CharacterTextSplitter:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        assert (
            chunk_size > chunk_overlap
        ), "Chunk size must be greater than chunk overlap"

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> List[str]:
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunks.append(text[i : i + self.chunk_size])
        return chunks

    def split_texts(self, texts: List[str]) -> List[str]:
        chunks = []
        for text in texts:
            chunks.extend(self.split(text))
        return chunks


class YouTubeLoader:
    def __init__(self, url: str, language_codes: List[str] = None):
        """
        Initialize YouTube loader with a YouTube URL.
        
        Args:
            url: YouTube video URL (e.g., "https://www.youtube.com/watch?v=VIDEO_ID")
            language_codes: List of language codes to try for transcript (default: ['en'])
        """
        self.url = url
        self.video_id = self._extract_video_id(url)
        self.language_codes = language_codes or ['en']
        self.documents = []
        
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        # Handle various YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError(f"Could not extract video ID from URL: {url}")
    
    def load(self):
        """Load transcript from YouTube video."""
        try:
            # Create API instance
            api = YouTubeTranscriptApi()
            
            # Get available transcripts
            transcript_list = api.list(self.video_id)
            
            # Try to find transcript in preferred languages
            transcript = transcript_list.find_transcript(self.language_codes)
            
            # Fetch the actual transcript data
            transcript_data = transcript.fetch()
            
            # Format transcript as plain text
            formatter = TextFormatter()
            transcript_text = formatter.format_transcript(transcript_data)
            
            # Clean up the transcript
            cleaned_text = self._clean_transcript(transcript_text)
            self.documents.append(cleaned_text)
            
        except Exception as e:
            raise ValueError(f"Could not retrieve transcript for video {self.video_id}: {str(e)}")
    
    def _clean_transcript(self, text: str) -> str:
        """Clean and format transcript text."""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Add video metadata as context
        video_info = f"Video ID: {self.video_id}\nURL: {self.url}\n\nTranscript:\n"
        return video_info + text
    
    def load_documents(self):
        """Load documents and return them."""
        self.load()
        return self.documents
    
    def get_video_info(self) -> dict:
        """Get basic video information."""
        return {
            "video_id": self.video_id,
            "url": self.url,
            "language_codes": self.language_codes
        }


class MultiYouTubeLoader:
    def __init__(self, urls: List[str], language_codes: List[str] = None):
        """
        Initialize multi-YouTube loader with multiple YouTube URLs.
        
        Args:
            urls: List of YouTube video URLs
            language_codes: List of language codes to try for transcripts (default: ['en'])
        """
        self.urls = urls
        self.language_codes = language_codes or ['en']
        self.documents = []
        self.video_info = []
        self.failed_videos = []
        
    def load_all(self):
        """Load transcripts from all YouTube videos."""
        print(f"📺 Loading transcripts from {len(self.urls)} videos...")
        
        for i, url in enumerate(self.urls, 1):
            try:
                print(f"  [{i}/{len(self.urls)}] Processing: {url}")
                
                # Create individual loader
                loader = YouTubeLoader(url, self.language_codes)
                documents = loader.load_documents()
                
                # Add video metadata to each document
                video_info = loader.get_video_info()
                for doc in documents:
                    # Add video metadata as a prefix
                    enhanced_doc = f"VIDEO: {video_info['video_id']} | {doc}"
                    self.documents.append(enhanced_doc)
                
                self.video_info.append(video_info)
                print(f"    ✅ Successfully loaded transcript")
                
            except Exception as e:
                print(f"    ❌ Failed to load transcript: {str(e)}")
                self.failed_videos.append({"url": url, "error": str(e)})
        
        print(f"\n📊 Summary:")
        print(f"  ✅ Successfully loaded: {len(self.video_info)} videos")
        print(f"  ❌ Failed to load: {len(self.failed_videos)} videos")
        print(f"  📄 Total documents: {len(self.documents)}")
        
        if self.failed_videos:
            print(f"\n❌ Failed videos:")
            for failed in self.failed_videos:
                print(f"  - {failed['url']}: {failed['error']}")
    
    def load_documents(self):
        """Load all documents and return them."""
        self.load_all()
        return self.documents
    
    def get_successful_videos(self) -> List[dict]:
        """Get information about successfully loaded videos."""
        return self.video_info
    
    def get_failed_videos(self) -> List[dict]:
        """Get information about failed videos."""
        return self.failed_videos
    
    def get_summary(self) -> dict:
        """Get a summary of the loading process."""
        return {
            "total_urls": len(self.urls),
            "successful_videos": len(self.video_info),
            "failed_videos": len(self.failed_videos),
            "total_documents": len(self.documents),
            "success_rate": len(self.video_info) / len(self.urls) if self.urls else 0
        }


if __name__ == "__main__":
    # Test with text file
    loader = TextFileLoader("data/KingLear.txt")
    loader.load()
    splitter = CharacterTextSplitter()
    chunks = splitter.split_texts(loader.documents)
    print(len(chunks))
    print(chunks[0])
    print("--------")
    print(chunks[1])
    print("--------")
    print(chunks[-2])
    print("--------")
    print(chunks[-1])
    
    # Test with YouTube (uncomment to test)
    # youtube_loader = YouTubeLoader("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    # youtube_docs = youtube_loader.load_documents()
    # print(f"YouTube transcript loaded: {len(youtube_docs)} documents")
    # print(f"First 200 chars: {youtube_docs[0][:200]}...")
