from typing import Any, Dict, Optional
from urllib.parse import urlparse, parse_qs
import re
from youtube_transcript_api import YouTubeTranscriptApi
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("youtube-transcript")

def extract_youtube_id(input_url: str) -> str:
    """Extract YouTube video ID from various URL formats or direct ID input."""
    if not input_url:
        raise ValueError("YouTube URL or ID is required")

    # Try parsing as URL
    try:
        url = urlparse(input_url)
        if url.hostname == "youtu.be":
            return url.path[1:]
        elif "youtube.com" in url.hostname:
            video_id = parse_qs(url.query).get("v", [None])[0]
            if not video_id:
                raise ValueError(f"Invalid YouTube URL: {input_url}")
            return video_id
    except ValueError:
        # Not a URL, check if it's a direct video ID
        if re.match(r"^[a-zA-Z0-9_-]{11}$", input_url):
            return input_url
        
    raise ValueError(f"Could not extract video ID from: {input_url}")

def format_transcript(transcript: list[dict]) -> str:
    """Format transcript lines into readable text."""
    return " ".join(
        line["text"].strip() 
        for line in transcript 
        if line["text"].strip()
    )

@mcp.tool()
async def get_transcript(url: str, lang: str = "en") -> str:
    """Extract transcript from a YouTube video URL or ID.
    
    Args:
        url: YouTube video URL or ID
        lang: Language code for transcript (e.g., 'ko', 'en')
    """
    try:
        video_id = extract_youtube_id(url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
        return format_transcript(transcript)
    except Exception as e:
        return f"Failed to retrieve transcript: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio") 