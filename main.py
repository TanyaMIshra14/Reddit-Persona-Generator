#!/usr/bin/env python3
"""
Reddit User Persona Generator
Scrapes Reddit user data and generates detailed personas using AI
"""

import os
import sys
import argparse
from datetime import datetime
from reddit_scraper import RedditScraper
from persona_generator import PersonaGenerator

def extract_username_from_url(url):
    """Extract username from Reddit profile URL"""
    if '/user/' in url:
        username = url.split('/user/')[1].rstrip('/')
        return username
    else:
        raise ValueError("Invalid Reddit profile URL format")

def main():
    parser = argparse.ArgumentParser(description='Generate user persona from Reddit profile')
    parser.add_argument('profile_url', help='Reddit user profile URL')
    parser.add_argument('--output-dir', default='outputs', help='Output directory for persona files')
    
    args = parser.parse_args()
    
    try:
        # Extract username from URL
        username = extract_username_from_url(args.profile_url)
        print(f"Processing Reddit user: {username}")
        
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Initialize scraper and generator
        scraper = RedditScraper()
        generator = PersonaGenerator()
        
        # Scrape user data
        print("Scraping Reddit data...")
        user_data = scraper.scrape_user_data(username)
        print(f"Scraped {len(user_data['posts'])} posts and {len(user_data['comments'])} comments.")
        if not user_data['posts'] and not user_data['comments']:
            print("No posts or comments found for this user.")
            return
        # Generate persona
        print("Generating user persona...")
        persona = generator.generate_persona(user_data)
        # Save to file
        output_file = os.path.join(args.output_dir, f"{username}_persona.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(persona)
        print(f"Persona saved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()