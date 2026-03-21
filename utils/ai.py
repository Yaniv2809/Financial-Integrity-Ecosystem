import os
import requests
from dotenv import load_dotenv
from config.config import ConfigManager

load_dotenv()

def get_ai_error_analysis(error_message: str) -> str:
    """
    Receives an error, sends to Groq AI (openai/gpt-oss-120b) via REST API, and returns an analysis.
    Includes a timeout mechanism to prevent test suite freezing.
    """
    api_key = os.getenv("GROQ_API_KEY")
    
    # Cleaning the key in case quotes or spaces were accidentally inserted in the .env file
    if api_key:
        api_key = api_key.replace('"', '').replace("'", "").strip()
        
    if not api_key:
        return "🤖 AI Analysis failed: GROQ_API_KEY not found in .env file."

    url = ConfigManager.get_env_data()['ai_url']
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openai/gpt-oss-120b", 
        "temperature": 0.1, # טמפרטורה נמוכה גורמת למודל להיות אנליטי, מדויק ופחות "יצירתי" (מעולה לדיבוג)
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an Elite QA Automation Architect. "
                    "Your technology stack is strict: Python 3, Pytest, Playwright (Sync API ONLY), "
                    "Requests (for API testing), and standard SQL (for Database testing). "
                    "CRITICAL RULES: "
                    "1. NEVER use async/await in your code examples. "
                    "2. NEVER write JavaScript/TypeScript. "
                    "3. Provide exactly 2 short sentences explaining the root cause, followed by a valid Python code snippet to fix it."
                )
            },
            {
                "role": "user",
                "content": f"Analyze this test error and suggest a fix:\n\n{error_message}"
            }
        ]
    }

    try:
        # הוספת timeout של 10 שניות - קריטי כדי לא לתקוע את הריצה
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        # אם יש שגיאה, הפעם נדפיס בדיוק מה השרת של Groq אומר לנו!
        if not response.ok:
            return f"🤖 Groq API Error {response.status_code}:\n{response.text}"
            
        data = response.json()
        ai_text = data['choices'][0]['message']['content']
        
        return "🤖 AI Analysis (Powered by Groq/Openai-gpt-oss-120b):\n\n" + ai_text
        
    except requests.exceptions.Timeout:
        return "🤖 AI Analysis failed: Groq API timed out after 10 seconds. Skipping analysis to keep tests running."
        
    except requests.exceptions.RequestException as e:
        return f"🤖 AI Analysis failed due to a network error: {str(e)}"
        
    except Exception as e:
        return f"🤖 AI Analysis failed: {str(e)}"