import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_ai_error_analysis(error_message: str) -> str:
    """
    מקבלת שגיאה, שולחת ל-Groq AI (מודל Llama 3.1) דרך REST API, ומחזירה ניתוח.
    """
    api_key = os.getenv("GROQ_API_KEY")
    
    # ניקוי המפתח למקרה שהוכנסו גרשיים או רווחים בטעות בקובץ ה-.env
    if api_key:
        api_key = api_key.replace('"', '').replace("'", "").strip()
        
    if not api_key:
        return "🤖 AI Analysis failed: GROQ_API_KEY not found in .env file."

    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-8b-instant", # המודל העדכני והתקין!
        "messages": [
            {
                "role": "system",
                "content": "You are a Senior QA Automation Engineer."
            },
            {
                "role": "user",
                "content": f"Analyze this Playwright test error in 2 short sentences and suggest a fix: '{error_message}'"
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        # אם יש שגיאה, הפעם נדפיס בדיוק מה השרת של Groq אומר לנו!
        if not response.ok:
            return f"🤖 Groq API Error {response.status_code}:\n{response.text}"
            
        data = response.json()
        ai_text = data['choices'][0]['message']['content']
        
        return "🤖 AI Analysis (Powered by Groq/Llama-3.1):\n\n" + ai_text
        
    except Exception as e:
        return f"🤖 AI Analysis failed: {str(e)}"