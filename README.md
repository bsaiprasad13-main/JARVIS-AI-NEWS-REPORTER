# 🤖 JARVIS AI News Reporter

Jarvis is an automated pipeline that curates the latest AI tools, AI industry news, and tech startup updates, delivering a beautifully formatted daily digest directly to your inbox. It is built to run entirely on **Zoho Catalyst's Free Tier** using Python, and uses Google Gemini for processing and Resend for email delivery.

> [!TIP]
> **Recommended: Use an AI IDE**
> To make exploring, modifying, or deploying this project even easier, we highly recommend opening this repository in an AI Coding Assistant like **Google Anti Gravity**, Cursor, or any agentic AI IDE. They can help you understand the codebase or even automate the setup steps for you!

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

## 🚀 Ultimate Beginner's Deployment Guide (No Coding Required)

We have designed this project so that **absolutely anyone** can deploy it to Zoho Catalyst for free, even if you have never used a terminal or written code before. We will do this by connecting your GitHub account directly to Zoho Catalyst!

### Step 1: Fork this Repository
First, you need your own copy of this code.
1. Scroll to the top of this page on GitHub.
2. Click the **Fork** button (top right corner).
3. Click **Create Fork**. You now have your own copy of the project in your GitHub account!

### Step 2: Get Your API Keys
Your JARVIS reporter needs a few keys to access the AI and send emails. Keep these tabs open:
1. **Google Gemini Key:** Go to [Google AI Studio](https://aistudio.google.com/), sign in, and click "Get API Key". It's 100% free.
2. **Product Hunt Token:** Go to [Product Hunt API Dashboard](https://api.producthunt.com/v2/docs), sign in, and create an application to get your "Developer Token".
3. **Resend API Key:** Go to [Resend](https://resend.com/), sign up, and generate an API key. 
   - *Note:* To send emails reliably, you must verify a domain in Resend. Once verified, note your sending email (e.g., `jarvis@yourdomain.com`).

### Step 3: Create Your Zoho Catalyst Project
This is where the magic happens. Zoho Catalyst will run our code for free.
1. Go to the [Zoho Catalyst Console](https://console.catalyst.zoho.com/) and create a free account.
2. Click **Create Project**. Name it `Jarvis-News-Reporter`.
3. Accept the terms and open your new project dashboard.

### Step 4: Deploy Directly from GitHub
Now, we tell Zoho to pull the code from your GitHub fork.
1. In your Zoho Catalyst project, look at the left sidebar.
2. Click on **Environments** (or **CI/CD** depending on your layout), and find the **GitHub Integration** or **Deploy from Git** option.
3. Click **Connect to GitHub**. Zoho will ask for permission to view your repositories—click Authorize.
4. From the dropdown list, select your forked `JARVIS-AI-NEWS-REPORTER` repository.
5. Choose the `main` branch.
6. Click **Deploy**. Catalyst will automatically download the code, install everything, and set up your `jarvis_pipeline` Python function!

### Step 5: Add Your Variables to Zoho
Your code is deployed, but it needs those API keys you gathered in Step 2 to actually run!
1. In the Zoho Catalyst left sidebar, click **Compute**, then click **Functions**.
2. You will see your newly deployed `jarvis_pipeline` function. Click on it.
3. Go to the **Configuration** or **Environment Variables** tab.
4. You need to add exactly 5 variables here. Click "Add Variable" for each one:
   - **Key:** `GEMINI_API_KEY` | **Value:** (Paste your Gemini key here)
   - **Key:** `RESEND_API_KEY` | **Value:** (Paste your Resend key here)
   - **Key:** `TO_EMAIL`       | **Value:** (The email address where you want to receive the digest)
   - **Key:** `FROM_EMAIL`     | **Value:** (Your verified Resend sending email)
   - **Key:** `PRODUCT_HUNT_DEVELOPER_TOKEN` | **Value:** (Your Product Hunt token)
5. Save your variables!

### Step 6: Schedule the Daily Email (Cron Job)
Finally, let's tell Zoho to run this automatically every morning.
1. In the Zoho Catalyst left sidebar, find the **Serverless** section and click **Cron**.
2. Click **Create Cron Job**.
3. Set the frequency to **Daily** and pick your preferred time (e.g., 8:00 AM).
4. Set the Target Type to **Function**, and select your `jarvis_pipeline` function.
5. Save it!

**🎉 Congratulations!** You have successfully deployed your own automated AI News Reporter. It will now run on autopilot and email you every day!

*(Advanced users: If you prefer deploying via the CLI, please see [ADVANCED_DEPLOYMENT.md](./ADVANCED_DEPLOYMENT.md))*

---

## 💡 Customization
You can modify the HTML template used for the email in `functions/jarvis_pipeline/template.html` to change the look and feel of your daily digest.
