import os
import feedparser
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ==========================================
# 1. LOAD CONFIGURATION FROM GITHUB SECRETS
# ==========================================
GEMINI_KEY = os.getenv("GEMINI_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
BLOG_ID = os.getenv("BLOG_ID")

def run_blogger_bot():
    try:
        # ==========================================
        # 2. FETCH TRENDS FROM GOOGLE RSS
        # ==========================================
        print("Fetching Google Trends...")
        feed = feedparser.parse("https://trends.google.com/trending/rss?geo=US")
        if not feed.entries:
            print("No trends found.")
            return

        # Get the top trend and a related news link
        top_trend = feed.entries[0]
        keyword = top_trend.title
        source_link = top_trend.link
        print(f"Top Trend Found: {keyword}")

        # ==========================================
        # 3. GENERATE ARTICLE CONTENT WITH GEMINI
        # ==========================================
        print("Generating article with Gemini AI...")
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')

        prompt = f"""
        Write a professional, engaging blog post about the trending topic: '{keyword}'.
        Use the following news source for context: {source_link}
        
        Requirements:
        1. Format the entire response in clean HTML (use <h2>, <p>, <ul>, etc.).
        2. Make it at least 400 words.
        3. Include an introductory paragraph, 3 subheadings, and a conclusion.
        4. Do NOT include Markdown code blocks (like ```html). Just the raw HTML tags.
        """
        
        response = model.generate_content(prompt)
        article_html = response.text

        # ==========================================
        # 4. AUTHENTICATE AND POST TO BLOGGER
        # ==========================================
        print("Connecting to Blogger API...")
        creds = Credentials(
            None, 
            refresh_token=REFRESH_TOKEN, 
            client_id=CLIENT_ID, 
            client_secret=CLIENT_SECRET, 
            token_uri="[https://oauth2.googleapis.com/token](https://oauth2.googleapis.com/token)"
        )
        
        service = build('blogger', 'v3', credentials=creds)

        post_body = {
            'title': f"Everything You Need to Know About {keyword}",
            'content': article_html,
            'labels': ['Trending', keyword, 'Automated News']
        }

        request = service.posts().insert(blogId=BLOG_ID, body=post_body)
        result = request.execute()

        print(f"Success! Post published at: {result.get('url')}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_blogger_bot()
