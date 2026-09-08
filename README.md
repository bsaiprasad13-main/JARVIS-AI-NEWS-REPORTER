# 🤖 JARVIS AI News Reporter

Jarvis is an automated pipeline that curates the latest AI tools, AI industry news, and tech startup updates, delivering a beautifully formatted daily digest directly to your inbox. It is built to run entirely on **Zoho Catalyst's Free Tier** using Python, and uses Google Gemini for processing and Resend for email delivery.

## 🌟 Features
- **Daily Tech Digest**: AI tools, industry news, and startup funding updates.
- **Automated**: Runs on a schedule via Zoho Catalyst Cron.
- **AI-Powered**: Uses Google Gemini (RAG) to process and summarize news.
- **Cost-Effective**: Designed to operate within the generous free limits of Zoho Catalyst.

---

## 🛠️ Prerequisites & API Keys
To run this project, you will need the following accounts and API keys:

1. **Zoho Catalyst Account**: Where the code will be hosted.
   - [Sign up for Zoho Catalyst](https://catalyst.zoho.com/)
   - *Good News*: Zoho Catalyst offers a very generous free tier that includes Basic I/O functions, Cron jobs, and Data Store usage, which is more than enough to run this daily digest for free!

2. **Google Gemini API Key**: For AI processing.
   - [Get Gemini API Key](https://aistudio.google.com/)

3. **Product Hunt Developer Token**: For fetching new AI tools.
   - [Get Product Hunt API Token](https://api.producthunt.com/v2/docs)

4. **Resend Account**: For sending the emails.
   - [Sign up for Resend](https://resend.com/)

### ⚠️ Critical Warning regarding Resend & Email Deliverability
By default, Resend provides a testing domain, but to send emails to arbitrary addresses reliably, **you MUST verify your own domain name** in Resend.
- **The Issue**: If you send emails from an unverified domain (or a generic email like `@gmail.com` as the sender), your emails are highly likely to end up in the **Spam/Junk folder**, or be blocked entirely by email providers.
- **The Solution**: 
  1. Purchase a domain name (or use one you own).
  2. Add the domain in your Resend Dashboard.
  3. Add the provided DNS records (TXT, MX, etc.) to your domain registrar to verify it.
  4. Once verified, configure your `FROM_EMAIL` to use that domain (e.g., `"Jarvis <jarvis@yourdomain.com>"`).

---

## 🚀 Installation & Deployment

We have designed a unique, AI-assisted installation process to make deployment incredibly simple. Instead of following tedious manual steps, you can use an AI Coding Assistant to do the heavy lifting for you!

**👉 Please see the [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for step-by-step instructions on how to set this up automatically using your AI IDE.**

---

## ⚙️ Environment Variables
For reference, here are the environment variables the project requires. You can find a template in `.env.example`:

- `GEMINI_API_KEY`: Your Google Gemini API Key.
- `RESEND_API_KEY`: Your Resend API Key.
- `PRODUCT_HUNT_DEVELOPER_TOKEN`: Your Product Hunt token.
- `TO_EMAIL`: The email address where you want to receive the digest.
- `FROM_EMAIL`: The sender email address (must use your verified Resend domain).

---

## 💡 Customization
You can modify the HTML template used for the email in `functions/jarvis_pipeline/template.html` to change the look and feel of your daily digest.
