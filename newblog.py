import os
import google.generativeai as genai
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime
import time
import random
import re 
import logging
import requests
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BLOGGER_BLOG_ID = os.getenv("BLOGGER_BLOG_ID")
OAUTH_CLIENT_ID_HARDCODED = os.getenv("OAUTH_CLIENT_ID_HARDCODED")
OAUTH_CLIENT_SECRET_HARDCODED = os.getenv("OAUTH_CLIENT_SECRET_HARDCODED")

if not GEMINI_API_KEY or "YOUR_GEMINI_API_KEY_HERE" in GEMINI_API_KEY:
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!! CRITICAL ERROR: You MUST replace 'YOUR_GEMINI_API_KEY_HERE'")
    print("!!!                 with your actual Gemini API key.")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    exit() 

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    print("Please ensure your GEMINI_API_KEY is valid.")
    exit()

BLOG_CATEGORIES = [
    "Technology Trends",
    "Digital Marketing",
    "Personal Development",
    "Health and Wellness",
    "Travel Adventures",
    "Career Growth",
    "Financial Tips",
    "Lifestyle","Current Trending Topics","Political Situation",
    "Education","Economy","News and awareness",
    "Technology launches"
]

try:
    title_model = genai.GenerativeModel("gemini-1.5-flash")
    content_model = genai.GenerativeModel("gemini-1.5-pro")
except Exception as e:
    print(f"Error creating Gemini models: {e}")
    print("Check your API key and network connection.")
    exit()


def generate_blog_title(category):
    """Generates a single blog title using the Gemini API."""
    print(f"Generating title for category: {category}...")
    prompt = f"""Generate exactly ONE unique, engaging, and SEO-friendly blog title for the category: {category}.
    The title should be compelling and click-worthy while maintaining professionalism.
    The title must be between 40 and 70 characters long.
    Return ONLY the title text itself, with no extra explanation, formatting (like bullet points or quotes), or introductory phrases."""

    try:
        response = title_model.generate_content(prompt)

        if response and response.text:
          
            title = response.text.strip().strip('"').strip("'").strip("*").strip("`").strip()
            
            title = title.splitlines()[0].strip()
           
            title = re.sub(r'^\s*[\*\-\d\.]+\s*', '', title)

            title_len = len(title)
            print(f"   Raw title response: '{response.text}'")

            if 30 <= title_len <= 75: 
                 print(f"   Cleaned title: '{title}' (Length: {title_len})")
                 return title
            else:
                 print(f"   Warning: Generated title '{title}' (Length: {title_len}) is outside desired range (30-75). Using fallback.")
                 
                 fallback_options = [f"{category}: Key Insights", f"Exploring {category} Today", f"Your Guide to {category}"]
                 return random.choice(fallback_options)
        else:
            print("   Warning: Failed to generate title text from API. Using fallback.")
            return f"Updates on {category}" 

    except Exception as e:
        print(f"   Error during title generation: {e}")
        
        return f"Exploring {category}"

def generate_blog_content(title, category):
    """Generates blog post content using the Gemini API."""
    print(f"Generating content for title: \"{title}\"...")
    prompt = f"""Write a comprehensive blog post titled: "{title}"
    Category: {category}

    Requirements:
    1.  Engaging Introduction: Hook the reader immediately, clearly stating what the post is about.
    2.  Main Body Sections: Break down the topic into logical sections using clear H2 Markdown subheadings (e.g., `## Section Title`). Use H3 (`### Sub-Section`) for further breakdown if needed.
    3.  Practical Advice: Include actionable tips, steps, strategies, or real-world examples directly relevant to "{title}".
    4.  Supporting Details: Where appropriate, incorporate relevant (even if illustrative or hypothetical) statistics or data points to add credibility. Cite sources if possible, otherwise frame them as examples (e.g., "Studies often show...", "Imagine data indicating...").
    5.  Conversational & Engaging Tone: Write in a natural, approachable style. Avoid overly academic or dry language. Use "you" and "I" (sparingly) where appropriate.
    6.  SEO Considerations: Naturally integrate keywords related to "{title}" and "{category}" throughout the text, especially in headings and the introduction/conclusion, but prioritize readability over keyword density.
    7.  Unique Perspective: Offer a distinct viewpoint, synthesis of information, or analysis. Go beyond simply listing facts.
    8.  Strong Conclusion: Summarize the key takeaways. Offer a final thought, encouragement, or a relevant call to action (e.g., "What are your thoughts?", "Try implementing one tip this week").
    9.  Word Count: Aim for approximately 800-1200 words.
    10. Originality: Ensure the content is unique and does not directly copy from specific sources. It should be your own interpretation and writing based on the prompt.
    11. Formatting: Use paragraphs for readability. Use Markdown bullet points (`*` or `-`) for lists. Use Markdown bold (`**bold text**`) for emphasis where appropriate. Ensure proper spacing between paragraphs and sections.
    """
    full_response = ""
    try:
        
        response_stream = content_model.generate_content(prompt, stream=True)

        print("   Streaming content from API...")
        for chunk in response_stream:
            
            if chunk.text and chunk.text.strip():
                full_response += chunk.text
                print(".", end="", flush=True) 

        print("\n   Content stream finished.") 
        cleaned_content = full_response.strip()

        if not cleaned_content:
             print("   Warning: Content generation resulted in empty response.")
             return f"Content generation failed for '{title}'. Please try again."

        print(f"   Content generated successfully (Length: {len(cleaned_content)} chars).")
        return cleaned_content

    except Exception as e:
        print(f"\n   Error during content generation: {e}")
        
        return f"An error occurred while generating content for '{title}'. Details: {e}"

def get_blogger_credentials():
    """Sets up OAuth2 credentials for Blogger API using hardcoded config."""
    print("Attempting to get Blogger credentials...")
    TOKEN_FILE = 'token.json'
    SCOPES = ['https://www.googleapis.com/auth/blogger']

    client_config = {
        "installed": {
            "client_id": OAUTH_CLIENT_ID_HARDCODED,
            "project_id": "PROJECT_ID_IF_APPLICABLE",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": OAUTH_CLIENT_SECRET_HARDCODED,
        
            "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"]
        }
    }
  

    creds = None
    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        print(f"   Found existing token file: {TOKEN_FILE}")
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            print("   Credentials loaded from token file.")
        except Exception as e:
            print(f"   Error loading token file ({TOKEN_FILE}): {e}. Will attempt OAuth flow.")
            creds = None

    # Check if credentials are valid or need refresh/creation
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("   Credentials expired. Attempting to refresh...")
            try:
                creds.refresh(Request())
                print("   Credentials refreshed successfully.")
            except Exception as e:
                print(f"   Error refreshing token: {e}. Need to re-authenticate.")
                creds = None 

        # If still no valid credentials, run the OAuth flow
        if not creds:
            try:
                print("   No valid credentials. Initiating OAuth flow...")
                print("   A browser window may open for authentication.")
                # Use from_client_config with the dictionary defined above
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)

                # run_local_server starts a temporary web server to handle the OAuth redirect.
                
                creds = flow.run_local_server(port=0)
                print("   OAuth flow completed successfully.")
            except Exception as e:
                print(f"   Error during OAuth flow: {e}")
                print("   Possible issues:")
                print("     - Ensure 'http://localhost' is an Authorized Redirect URI in Google Cloud Console.")
                print("     - Check network connection.")
                print("     - Ensure the OAuth Client ID/Secret are correct.")
                return None 

        # Save the fresh or refreshed credentials
        if creds:
            try:
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
                print(f"   Credentials saved to {TOKEN_FILE}")
            except Exception as e:
                print(f"   Error saving token file: {e}")

    if creds and creds.valid:
        print("   Blogger credentials obtained successfully.")
        return creds
    else:
        print("   Failed to obtain valid Blogger credentials.")
        return None


def post_to_blogspot(title, content, credentials, category_label):
    """Posts content to Blogspot using the Blogger API with improved HTML conversion."""
    print(f"Preparing to post to Blogger: \"{title}\"")
    if not credentials:
        print("   Error: Cannot post to Blogspot - Invalid credentials provided.")
        return False 

    # Use the hardcoded Blog ID
    if not BLOGGER_BLOG_ID or "YOUR_BLOGGER_BLOG_ID_HERE" in BLOGGER_BLOG_ID:
        print("   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("   !!! CRITICAL ERROR: You MUST replace 'YOUR_BLOGGER_BLOG_ID_HERE'")
        print("   !!!                 with your actual Blog ID.")
        print("   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return False 

    blog_id = BLOGGER_BLOG_ID

    try:
        print("   Building Blogger service...")
        service = build('blogger', 'v3', credentials=credentials, cache_discovery=False)

      
        print("   Converting content to HTML for Blogger...")
        html_lines = []
        in_list = False
        
        blocks = content.strip().split('\n\n')

        for block in blocks:
            block = block.strip() 
            if not block:
                continue

            lines_in_block = block.split('\n')
            processed_lines_in_block = []

            for line in lines_in_block:
                line = line.strip()
                if not line:
                    continue

                
                if line.startswith("### "):
                    processed_line = f"<h3>{line[4:].strip()}</h3>"
                    if in_list: 
                        processed_lines_in_block.append("</ul>")
                        in_list = False
                elif line.startswith("## "):
                    processed_line = f"<h2>{line[3:].strip()}</h2>"
                    if in_list: 
                        processed_lines_in_block.append("</ul>")
                        in_list = False
             
                elif line.startswith("* ") or line.startswith("- "):
                    list_content = line[2:].strip()
                  
                    list_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', list_content)
                    if not in_list: 
                        processed_lines_in_block.append("<ul>")
                        in_list = True
                    processed_line = f"<li>{list_content}</li>"
                
                else:
                    if in_list: 
                        processed_lines_in_block.append("</ul>")
                        in_list = False
                    
                    paragraph_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                    processed_line = f"<p>{paragraph_content}</p>"

                processed_lines_in_block.append(processed_line)

            html_lines.extend(processed_lines_in_block)

        if in_list:
            html_lines.append("</ul>")

        html_content = "\n".join(html_lines)
        print("   HTML conversion done.")
       
        labels = [re.sub(r'\s+', '', category_label)] 
        body = {
            'kind': 'blogger#post',
            'blog': {
                'id': blog_id
            },
            'title': title,
            'content': html_content, 
            'labels': labels
        }

        print(f"   Inserting post with labels: {labels} to blog ID {blog_id}...")
        posts = service.posts()
        
        request = posts.insert(blogId=blog_id, body=body, isDraft=False, fetchBody=True) # Fetch body to get URL
        post = request.execute()

        print(f"   Successfully posted: '{title}'")
        print(f"   Post URL: {post.get('url', 'N/A - Check Blogger Dashboard')}")
        return True 

    except Exception as e:
        print(f"   Error posting to Blogspot: {e}")
        if hasattr(e, 'content'):
            try:
                import json
                error_details = json.loads(e.content.decode('utf-8'))
                print(f"   API Error Details: {json.dumps(error_details, indent=2)}")
            except:
                 print(f"   Raw Error Content: {e.content}")
        return False 


def main():
    """Main function to run the blog post generation and posting process."""
    print("=============================================")
    print("=== Starting AI Blog Post Generator ===")
    print("=============================================")
    start_time = time.time()

    credentials = get_blogger_credentials()
    if not credentials:
        print("\nExiting script due to authentication failure.")
        return 
    try:
      
        category = random.choice(BLOG_CATEGORIES)
        print(f"\nSelected category: {category}")

        
        title = generate_blog_title(category)
        
        if "Exploring" in title or "Updates on" in title or "Insights" in title:
             print(f"   Proceeding with generated/fallback title: \"{title}\"")
        else:
            print(f"   Using generated title: \"{title}\"")


        
        content = generate_blog_content(title, category)

        
        if not content or "error occurred" in content.lower() or "generation failed" in content.lower():
            print("\nContent generation failed. Skipping post to Blogger.")
            return 

        # 5. Post to Blogspot
        print("\nAttempting to post generated content to Blogspot...")
        success = post_to_blogspot(title, content, credentials, category) # Pass category for label

        if success:
            print("\nBlog post published successfully!")
        else:
            print("\nFailed to publish blog post.")

    except Exception as e:
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"!!! An unexpected error occurred in the main loop: {e}")
        import traceback
        traceback.print_exc() # Print detailed traceback for debugging
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    finally:
        end_time = time.time()
        print("\n=============================================")
        print(f"=== Script finished in {end_time - start_time:.2f} seconds ===")
        print("=============================================")


if __name__ == "__main__":
    # Final check for placeholders before running main
    if "YOUR_GEMINI_API_KEY_HERE" in GEMINI_API_KEY or \
       "YOUR_BLOGGER_BLOG_ID_HERE" in BLOGGER_BLOG_ID:
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! ERROR: You must replace the placeholder API key and Blog ID")
        print("!!!        with your actual values near the top of the script before running.")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        main()
