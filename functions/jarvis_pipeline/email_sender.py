import os
import sys
import json
import requests
import datetime

# Load HTML template
TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html')

def render_email_html(generated_data):
    """
    Renders the HTML template using standard Python string formatting/substitution
    with zero template-engine dependency conflicts.
    """
    tools = generated_data.get('section_1_tools', [])
    ai_news = generated_data.get('section_2_ai_news', [])
    india_news = generated_data.get('section_3_india_news', [])
    notes = generated_data.get('section_notes', {})

    # Check if Jinja2 is available
    try:
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))
        template = env.get_template('template.html')
        return template.render(
            tools=tools,
            ai_news=ai_news,
            india_news=india_news,
            notes=notes
        )
    except Exception:
        pass

    # Built-in robust HTML fallback generator
    def build_cards(items):
        cards = ""
        for it in items:
            cards += f"""
            <div style="background:#ffffff; border-radius:10px; padding:18px; margin-bottom:14px; border:1px solid #eaeaea;">
                <h3 style="margin:0 0 6px 0; font-size:16px;"><a href="{it.get('link','#')}" style="color:#111827; text-decoration:none; font-weight:600;">{it.get('title','')}</a></h3>
                <div style="font-size:12px; color:#6b7280; margin-bottom:8px; font-weight:500;">Source: {it.get('source','')}</div>
                <p style="margin:0; font-size:14px; color:#374151; line-height:1.5;">{it.get('why_it_matters','')}</p>
            </div>
            """
        return cards

    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,sans-serif; background:#f9fafb; padding:24px; color:#111827;">
        <div style="max-width:600px; margin:0 auto;">
            <div style="text-align:center; padding-bottom:20px;">
                <h1 style="margin:0; font-size:24px; color:#111827;">🤖 Jarvis: Your Daily PM Digest</h1>
                <p style="margin:4px 0 0 0; font-size:14px; color:#6b7280;">AI & Tech curated for your product management journey</p>
            </div>
            
            <h2 style="font-size:18px; color:#2563eb; border-bottom:2px solid #e5e7eb; padding-bottom:6px; margin-top:24px;">🛠️ AI Tools for Product Managers</h2>
            {build_cards(tools) if tools else '<p style="color:#6b7280; font-size:14px;">Today was quiet for new tool releases.</p>'}

            <h2 style="font-size:18px; color:#2563eb; border-bottom:2px solid #e5e7eb; padding-bottom:6px; margin-top:24px;">📰 AI Industry News</h2>
            {build_cards(ai_news) if ai_news else '<p style="color:#6b7280; font-size:14px;">Today was quiet in major AI headlines.</p>'}

            <h2 style="font-size:18px; color:#2563eb; border-bottom:2px solid #e5e7eb; padding-bottom:6px; margin-top:24px;">🇮🇳 India Startup & Tech News</h2>
            {build_cards(india_news) if india_news else '<p style="color:#6b7280; font-size:14px;">No major startup funding/updates logged today.</p>'}
            
            <div style="text-align:center; margin-top:32px; font-size:12px; color:#9ca3af;">
                Jarvis Daily Digest • Automated with Google Gemini & Zoho Catalyst
            </div>
        </div>
    </body>
    </html>
    """

def send_daily_digest(generated_data):
    api_key = os.environ.get("RESEND_API_KEY")
    to_email = os.environ.get("TO_EMAIL")
    from_email = os.environ.get("FROM_EMAIL")

    if not api_key or not to_email or not from_email:
        print("Error: RESEND_API_KEY, TO_EMAIL, or FROM_EMAIL not set.")
        return False
        
    html_content = render_email_html(generated_data)
    
    # Direct Resend REST API (100% dependable, eliminates resend package issues)
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    payload = {
        "from": from_email,
        "to": [to_email],
        "reply_to": to_email,
        "subject": f"Jarvis: Your Daily PM Digest - {date_str}",
        "html": html_content
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code in [200, 201]:
            print(f"Email sent successfully. Response: {response.text}")
            return True
        else:
            print(f"Resend API Error ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_alert_email(error_message):
    api_key = os.environ.get("RESEND_API_KEY")
    to_email = os.environ.get("TO_EMAIL")
    from_email = os.environ.get("FROM_EMAIL")
    if not api_key or not to_email or not from_email:
        return
        
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    date_str = datetime.datetime.now().strftime("%B %d, %Y %H:%M")
    payload = {
        "from": from_email,
        "to": [to_email],
        "reply_to": to_email,
        "subject": f"Jarvis System Alert: Pipeline Failure - {date_str}",
        "text": f"The Jarvis pipeline encountered a critical error during execution:\n\n{error_message}"
    }
    try:
        requests.post(url, headers=headers, json=payload, timeout=10)
        print("Alert email dispatched.")
    except Exception:
        pass
