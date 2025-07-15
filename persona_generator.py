import google.generativeai as genai
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class PersonaGenerator:
    def __init__(self):
        # Configure Gemini API
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not self.gemini_api_key:
            print("Error: GEMINI_API_KEY not found in environment. Persona generation will not work.")
            self.model = None
        else:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel("models/gemini-2.5-pro")

    def generate_persona(self, user_data):
        """Generate user persona from scraped Reddit data"""
        
        # Prepare data for analysis
        posts_text = self._prepare_posts_data(user_data['posts'])
        comments_text = self._prepare_comments_data(user_data['comments'])
        
        # Create prompt for AI analysis
        prompt = self._create_persona_prompt(user_data, posts_text, comments_text)
        
        # Generate persona using Gemini
        if not self.model:
            return "Error: Gemini model not initialized due to missing API key."
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=8192,
                    temperature=0.7,
                )
            )
            # Check if response contains valid text
            if hasattr(response, 'text') and response.text:
                persona_text = response.text
                final_persona = self._format_persona_with_citations(persona_text, user_data)
                return final_persona
            else:
                # Log the full response for debugging
                debug_info = f"No valid persona generated. Full Gemini response: {response}"
                return f"Error generating persona: No valid content returned by Gemini API.\n{debug_info}"
        except Exception as e:
            return f"Error generating persona: {str(e)}"
    
    def _prepare_posts_data(self, posts):
        """Prepare posts data for analysis"""
        posts_summary = []
        for i, post in enumerate(posts):
            summary = f"Post {i+1}: [{post['subreddit']}] {post['title']}"
            if post['text']:
                summary += f" - {post['text'][:200]}..."
            posts_summary.append(summary)
        return "\n".join(posts_summary)
    
    def _prepare_comments_data(self, comments):
        """Prepare comments data for analysis"""
        comments_summary = []
        for i, comment in enumerate(comments):
            summary = f"Comment {i+1}: [{comment['subreddit']}] {comment['text'][:200]}..."
            comments_summary.append(summary)
        return "\n".join(comments_summary)
    
    def _create_persona_prompt(self, user_data, posts_text, comments_text):
        """Create comprehensive prompt for persona generation"""
        prompt = f"""
        Analyze the following Reddit user data and create a detailed user persona:

        Username: {user_data['username']}
        
        POSTS:
        {posts_text}
        
        COMMENTS:
        {comments_text}
        
        Create a comprehensive user persona that includes:
        
        1. DEMOGRAPHICS (age range, location hints, occupation clues)
        2. INTERESTS & HOBBIES (based on subreddits and content)
        3. PERSONALITY TRAITS (communication style, values, attitudes)
        4. ONLINE BEHAVIOR (posting patterns, engagement style)
        5. PAIN POINTS & MOTIVATIONS (what drives them, what frustrates them)
        6. GOALS & ASPIRATIONS (short-term and long-term)
        7. TECHNOLOGY USAGE (how they interact with platforms)
        8. SOCIAL CONNECTIONS (community involvement, relationship hints)
        
        For each characteristic, provide specific examples from their posts/comments.
        Be thorough but respectful. Focus on behavioral patterns rather than personal details.
        """
        
        return prompt
    
    def _format_persona_with_citations(self, persona_text, user_data):
        """Format persona with proper citations"""
        
        # Add header
        formatted_persona = f"""
# USER PERSONA: {user_data['username']}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Based on: {len(user_data['posts'])} posts and {len(user_data['comments'])} comments

## PERSONA ANALYSIS

{persona_text}

## CITATION SOURCES

### Posts Analyzed:
"""
        
        # Add post citations
        for i, post in enumerate(user_data['posts']):
            formatted_persona += f"""
Post {i+1}: [{post['subreddit']}] "{post['title']}"
Content: {post['text'][:300]}...
URL: {post.get('url', 'N/A')}
---
"""
        
        formatted_persona += "\n### Comments Analyzed:\n"
        
        # Add comment citations
        for i, comment in enumerate(user_data['comments']):
            formatted_persona += f"""
Comment {i+1}: [{comment['subreddit']}] 
Content: {comment['text'][:300]}...
URL: {comment.get('url', 'N/A')}
---
"""
        
        return formatted_persona