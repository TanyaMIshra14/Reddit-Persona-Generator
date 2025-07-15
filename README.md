Reddit User Persona Generator

Setup Instructions

1. Install Dependencies
   pip install -r requirements.txt

Configure Environment Variables
Create a .env file with:
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=PersonaGenerator/1.0
OPENAI_API_KEY=your_openai_api_key

Get Reddit API Credentials

Go to https://www.reddit.com/prefs/apps
Create a new app (script type)
Copy client ID and secret


Get Gemini API Key

Visit https://aistudio.google.com/app/apikey
Create new API key



Usage(Terminal)
python main.py https://www.reddit.com/user/UserID/
