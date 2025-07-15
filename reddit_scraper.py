import praw
import requests
from bs4 import BeautifulSoup
import time
import os
from dotenv import load_dotenv

load_dotenv()

class RedditScraper:
    def __init__(self):
        # Initialize Reddit API client
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT', 'PersonaGenerator/1.0')
        )
        
        # Fallback to web scraping if API limits are reached
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_user_data(self, username, limit=100):
        """Scrape posts and comments from a Reddit user"""
        user_data = {
            'username': username,
            'posts': [],
            'comments': [],
            'profile_info': {}
        }
        try:
            # Try Reddit API first
            result = self._scrape_with_api(username, limit)
            if result and isinstance(result, dict):
                user_data = result
        except Exception as e:
            print(f"API scraping failed: {e}")
            print("Falling back to web scraping...")
            try:
                result = self._scrape_with_web(username, limit)
                if result and isinstance(result, dict):
                    user_data = result
            except Exception as e2:
                print(f"Web scraping failed: {e2}")
                # user_data remains as initialized
        return user_data
    
    def _scrape_with_api(self, username, limit):
        """Scrape using Reddit API (PRAW)"""
        user_data = {
            'username': username,
            'posts': [],
            'comments': [],
            'profile_info': {}
        }
        
        try:
            print(f"[DEBUG] Fetching Redditor object for username: {username}")
            user = self.reddit.redditor(username)
            print(f"[DEBUG] Redditor object: {user}")
            # Get user profile info
            user_data['profile_info'] = {
                'created_utc': user.created_utc,
                'comment_karma': user.comment_karma,
                'link_karma': user.link_karma,
                'is_verified': getattr(user, 'is_verified', False)
            }
            # Get posts
            posts_list = list(user.submissions.new(limit=limit//2))
            print(f"[DEBUG] Number of posts fetched: {len(posts_list)}")
            for post in posts_list:
                post_data = {
                    'title': post.title,
                    'text': post.selftext,
                    'subreddit': str(post.subreddit),
                    'score': post.score,
                    'created_utc': post.created_utc,
                    'url': f"https://reddit.com{post.permalink}",
                    'type': 'post'
                }
                user_data['posts'].append(post_data)
            # Get comments
            comments_list = list(user.comments.new(limit=limit//2))
            print(f"[DEBUG] Number of comments fetched: {len(comments_list)}")
            for comment in comments_list:
                comment_data = {
                    'text': comment.body,
                    'subreddit': str(comment.subreddit),
                    'score': comment.score,
                    'created_utc': comment.created_utc,
                    'url': f"https://reddit.com{comment.permalink}",
                    'type': 'comment'
                }
                user_data['comments'].append(comment_data)
        except Exception as e:
            print(f"[DEBUG] Exception in _scrape_with_api: {e}")
            raise Exception(f"Reddit API error: {str(e)}")
        return user_data
    def _scrape_with_web(self, username, limit):
        """Fallback web scraping method"""
        user_data = {
            'username': username,
            'posts': [],
            'comments': []
        }
        try:
            # Scrape user profile page
            profile_url = f"https://www.reddit.com/user/{username}"
            response = self.session.get(profile_url)
            if response.status_code != 200:
                raise Exception(f"Failed to access profile: {response.status_code}")
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract posts
            posts = soup.find_all('div', {'data-testid': 'post-container'})
            for post in posts[:limit//2]:
                title_elem = post.find('h3')
                content_elem = post.find('div', {'data-testid': 'post-content'})
                if title_elem:
                    post_data = {
                        'title': title_elem.get_text(strip=True),
                        'text': content_elem.get_text(strip=True) if content_elem else '',
                        'subreddit': 'unknown',
                        'score': 0,
                        'created_utc': time.time(),
                        'url': '',
                        'type': 'post'
                    }
                    user_data['posts'].append(post_data)
            # Extract comments
            comments = soup.find_all('div', {'data-testid': 'comment'})
            for comment in comments[:limit//2]:
                content_elem = comment.find('p')
                comment_data = {
                    'text': content_elem.get_text(strip=True) if content_elem else '',
                    'subreddit': 'unknown',
                    'score': 0,
                    'created_utc': time.time(),
                    'url': '',
                    'type': 'comment'
                }
                user_data['comments'].append(comment_data)
        except Exception as e:
            raise Exception(f"Web scraping error: {str(e)}")
        return user_data