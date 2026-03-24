"""
AI Test Generator - Generates test case suggestions using AI.
Analyzes a web page or API endpoint and suggests pytest test cases.

Usage:
    from utils.ai_test_generator import AITestGenerator
    
    # Generate web tests from URL
    suggestions = AITestGenerator.generate_web_tests("https://atidcollege.co.il/Xamples/expense-tracker/")
    
    # Generate API tests from endpoint
    suggestions = AITestGenerator.generate_api_tests("http://localhost:3000/expenses")
"""

import os
import json
import requests
from dotenv import load_dotenv
from utils.logger import Logger

load_dotenv()
log = Logger()


class AITestGenerator:

    @staticmethod
    def _call_ai(prompt: str) -> str:
        """שליחת prompt ל-Groq AI וקבלת תשובה"""
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            api_key = api_key.replace('"', '').replace("'", "").strip()

        if not api_key:
            return "ERROR: GROQ_API_KEY not found in .env file."

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a Senior QA Automation Engineer specializing in Python, pytest, "
                        "Playwright, and API testing. Generate practical, production-ready test cases. "
                        "Use pytest conventions, allure decorators, and Page Object Model pattern."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if not response.ok:
                return f"Groq API Error {response.status_code}: {response.text}"
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            return f"AI call failed: {str(e)}"

    @staticmethod
    def generate_web_tests(page_source: str, page_url: str = "") -> str:
        """
        מקבל page source של דף HTML ומייצר הצעות לטסטים.
        """
        log.info(f"AI Test Generator: Analyzing web page {page_url}...")

        # חותכים את ה-source אם הוא ארוך מדי
        truncated = page_source[:3000] if len(page_source) > 3000 else page_source

        prompt = f"""Analyze this web page HTML and generate 5 pytest test cases.

Page URL: {page_url}
HTML Source (truncated):
{truncated}

Requirements:
- Use Playwright with Python
- Use Page Object Model (selectors in a separate class)
- Use allure decorators (@allure.title, @allure.description)
- Include both positive and negative tests
- Include at least one boundary test
- Use assertions from a WebVerify class (WebVerify.contain_text, WebVerify.visible, etc.)

Output format: Python code with clear comments in English."""

        return AITestGenerator._call_ai(prompt)

    @staticmethod
    def generate_api_tests(endpoint_url: str, method: str = "GET", sample_response: dict = None) -> str:
        """
        מקבל endpoint URL ומייצר הצעות לטסטים.
        """
        log.info(f"AI Test Generator: Analyzing API endpoint {endpoint_url}...")

        response_str = json.dumps(sample_response, indent=2) if sample_response else "Not provided"

        prompt = f"""Generate 5 pytest API test cases for this endpoint.

Endpoint: {method} {endpoint_url}
Sample Response: {response_str}

Requirements:
- Use Python requests library
- Use allure decorators
- Include: status code validation, response body validation, negative tests
- Include at least one test for invalid input
- Use an APIVerifications class (APIVerifications.verify_status_code, verify_response_value)
- Include proper test data setup and cleanup

Output format: Python code with clear comments in English."""

        return AITestGenerator._call_ai(prompt)

    @staticmethod
    def generate_from_bug(bug_description: str) -> str:
        """
        מקבל תיאור באג ומייצר טסט שמשחזר אותו.
        """
        log.info(f"AI Test Generator: Generating regression test for bug...")

        prompt = f"""A QA engineer found this bug:
{bug_description}

Generate a pytest regression test that:
1. Reproduces the bug step by step
2. Has clear assertions that will FAIL when the bug exists
3. Has clear assertions that will PASS when the bug is fixed
4. Uses allure decorators with severity=CRITICAL
5. Includes comments explaining the expected vs actual behavior

Output format: Python code ready to paste into a test file."""

        return AITestGenerator._call_ai(prompt)

    @staticmethod
    def classify_bug(error_message: str, test_layer: str = "unknown") -> str:
        """
        מסווג באג לפי סוג וחומרה.
        """
        log.info("AI Bug Classifier: Analyzing failure...")

        prompt = f"""Classify this test failure:

Error: {error_message}
Test Layer: {test_layer}

Respond in this exact JSON format only, no other text:
{{
    "bug_type": "UI/API/Data/Infrastructure/Logic",
    "severity": "Critical/High/Medium/Low",
    "category": "short category name",
    "summary": "one sentence summary",
    "suggested_fix": "one sentence fix suggestion"
}}"""

        result = AITestGenerator._call_ai(prompt)

        # ניסיון לפרסר JSON
        try:
            cleaned = result.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            return json.loads(cleaned)
        except (json.JSONDecodeError, IndexError):
            return {"raw_response": result}


# ============================================
# CLI Interface - הרצה ישירה מהטרמינל
# ============================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Test Generator - Generate test cases using AI")
    parser.add_argument("--web-url", help="Generate web tests from a URL")
    parser.add_argument("--api-url", help="Generate API tests from an endpoint")
    parser.add_argument("--bug", help="Generate regression test from bug description")
    parser.add_argument("--output", help="Save output to file", default=None)

    args = parser.parse_args()

    result = ""

    if args.web_url:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(args.web_url)
                source = page.content()
                browser.close()
            result = AITestGenerator.generate_web_tests(source, args.web_url)
        except Exception as e:
            result = f"Failed to fetch page: {e}"

    elif args.api_url:
        try:
            resp = requests.get(args.api_url)
            sample = resp.json() if resp.ok else None
            result = AITestGenerator.generate_api_tests(args.api_url, sample_response=sample)
        except Exception as e:
            result = f"Failed to fetch API: {e}"

    elif args.bug:
        result = AITestGenerator.generate_from_bug(args.bug)

    else:
        parser.print_help()
        exit()

    print("\n" + "=" * 60)
    print("AI TEST GENERATOR OUTPUT")
    print("=" * 60)
    print(result)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"\nSaved to: {args.output}")
