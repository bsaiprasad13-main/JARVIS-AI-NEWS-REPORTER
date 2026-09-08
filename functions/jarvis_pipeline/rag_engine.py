import os
import sys
import json
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def construct_prompt(items, failed_sources):
    items_text = ""
    for item in items:
        signal_text = f" (Signal: {item.get('signal')})" if item.get('signal') else ""
        items_text += f"- [{item['section']}] [{item['source']}] {item['title']}: {item['url']}{signal_text}\n"

    failed_sources_text = ""
    if failed_sources:
        failed_sources_text = f"\nThe following sources failed to return data today: {', '.join(failed_sources)}. If a section's low or zero item count is because a source failed, say so clearly instead of making it sound like a quiet news day."

    prompt = f"""You are writing a daily personalized digest email for a final-year 
engineering student who is transitioning into a product management 
career. They are actively looking for Associate Product Manager (APM) 
and Product Manager (PM) roles as a fresher. Everything you pick and 
every explanation you write should answer this: "Would this genuinely 
help someone trying to break into product management right now?"

Write in a casual, friendly tone. Use simple, everyday English. Avoid 
complex or fancy words. Keep sentences short and easy to read, like 
you're explaining it to a friend.

You have access to a database of articles, tool listings, and news 
items gathered from the last 24-72 hours. Each item may include a 
popularity/quality signal (such as upvotes or points) where available 
— use this, alongside relevance to the user's goals, to judge 
credibility and importance. Use ONLY this retrieved data. Do not use 
outside knowledge or make anything up. Every item must come directly 
from the retrieved content.

Within each section, order the items by relevance and importance to 
the user (not strictly by publish date) — put the most useful, most 
credible, most significant items first.

Generate exactly three sections, in this order:

SECTION 1: AI Tools for Product Managers
Pick 3 to 8 tools from the retrieved data (sourced from Product Hunt 
and Hacker News, labeled as section_1). Prioritize tools that are genuinely useful for PM 
work (roadmapping, user research, analytics, prototyping, writing, 
productivity) or broadly useful for student/professional life. Judge 
quality and popularity yourself based on what's in the data (upvotes, 
engagement, discussion) — skip anything that looks obscure or 
low-effort.

SECTION 2: AI Industry News
Pick 3 to 8 items from the retrieved data (sourced from TechCrunch and 
VentureBeat, labeled as section_2). Focus on new model releases, model performance, big 
company moves, funding, shutdowns, or anything shaping the AI industry.

SECTION 3: India Startup & Company News
Pick 3 to 8 items from the retrieved data (sourced from YourStory, 
Inc42, and TechCircle, labeled as section_3). Focus on funding rounds, layoffs, leadership 
changes, product launches, or big moves by companies and startups in 
India specifically.

For EVERY item in every section, include:
1. A short, clear title
2. The source name it came from (e.g. "TechCrunch", "Product Hunt")
3. The direct link/URL
4. A 1-2 sentence explanation, in simple casual language, of why this 
   matters to a student trying to get into product management — be 
   specific, not generic

If a section has fewer than 3 genuine items available, include only 
what's real and clearly say today was quiet in this area. Do not pad 
with weak or irrelevant content just to hit a minimum.
{failed_sources_text}

Return your response strictly as JSON in this structure:
{{
  "section_1_tools": [
    {{
      "title": "",
      "source": "",
      "link": "",
      "why_it_matters": ""
    }}
  ],
  "section_2_ai_news": [ ... same structure ... ],
  "section_3_india_news": [ ... same structure ... ],
  "section_notes": {{
    "section_1_status": "normal | quiet | source_issue",
    "section_2_status": "normal | quiet | source_issue",
    "section_3_status": "normal | quiet | source_issue"
  }}
}}

RETRIEVED DATA:
{items_text}
"""
    return prompt

def generate_email_content(items, failed_sources):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set.")
        return None

    prompt = construct_prompt(items, failed_sources)
    
    # Direct official Google Gemini REST API call (100% reliable, zero SDK dependency issues)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            res_json = response.json()
            raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
            # Clean possible markdown block wrappers
            cleaned_text = raw_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            return json.loads(cleaned_text.strip())
        else:
            print(f"Gemini API Error ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        print(f"Error calling Gemini REST API: {e}")
        return None
