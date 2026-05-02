import os
import feedparser
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# CONFIGURATION
GEMINI_KEY = os.getenv("GEMINI_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
BLOG_ID = os.getenv("BLOG_ID")

def run_blogger_bot():
    try:
        print("Fetching Google Trends...")
        feed = feedparser.parse("https://trends.google.com/trending/rss?geo=US")
        if not feed.entries:
            return

        # EXTRACT TREND DATA
        entry = feed.entries[0]
        keyword = entry.title
        source_link = entry.link
        
        # EXTRACT IMAGE URL from the RSS feed
        # Google Trends RSS uses 'media_thumbnail' or 'picture' tags
        image_url = ""
        if 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
            image_url = entry.media_thumbnail[0]['url']
        
        print(f"Trend: {keyword} | Image: {image_url}")

        # GENERATE CONTENT WITH AI
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')

        prompt = f"""
        Write a professional blog post about '{keyword}'.
        Context: {source_link}
        
        CRITICAL INSTRUCTIONS:
        1. Start the post with this exact HTML tag: <img src="{image_url}" style="width:100%; height:auto; border-radius:10px;" />
        2. Follow with the article in clean HTML (<h2>, <p>, etc.).
        3. Make it 400+ words.
        4. Do not use markdown code blocks.
        """
        
        response = model.generate_content(prompt)
        article_html = response.text

        # POST TO BLOGGER
        creds = Credentials(None, refresh_token=REFRESH_TOKEN, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, token_uri="https://oauth2.googleapis.com/token")
        service = build('blogger', 'v3', credentials=creds)

        post_body = {
            'title': f"Latest Update: {keyword}",
            'content': article_html,
            'labels': ['News', keyword]
        }

        request = service.posts().insert(blogId=BLOG_ID, body=post_body)
        result = request.execute()
        print(f"Success! Link: {result.get('url')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_blogger_bot()
