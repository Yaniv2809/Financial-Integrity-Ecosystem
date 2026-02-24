import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_ai_error_analysis(error_message: str) -> str:

    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return "AI Analysis failed: GEMINI_API_KEY not found in .env file."
 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"You are a Senior QA Engineer. Analyze this Playwright error in 2 short sentences: '{error_message}'"
            }]
        }]
    }
    
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        ai_text = data['candidates'][0]['content']['parts'][0]['text']
        
        return " Gemini AI Analysis:\n\n" + ai_text
        
    except requests.exceptions.HTTPError as http_err:
        return f" Google API Error: {http_err}\nResponse details: {response.text}"
    except Exception as e:
        return f"AI Analysis failed: {str(e)}"