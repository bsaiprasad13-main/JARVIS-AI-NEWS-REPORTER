# Implementation Plan: Jarvis (Zoho Catalyst Setup)

First, good news about Hacker News: **The Hacker News API is completely free and does not require an API key.** We can query it directly without any setup. So you already have everything you need!

Since you are new to Zoho Catalyst and want step-by-step guidance, I have created this plan to explain exactly what "project structure" means and how we will build and deploy Jarvis together.

## What is a "Project Structure"?
A project structure simply means the organized folders and files on your computer where we will write the code before uploading it to Zoho Catalyst. Catalyst expects files to be in specific folders so it knows what they are (e.g., a folder for "functions", a folder for "client" stuff). 

Here is how we will proceed, step by step:

## Phase 1: Installation & Setup (Your Local Computer)

1. **Install Node.js (Prerequisite):** Zoho's command-line tool needs Node.js installed on your computer.
2. **Install Zoho Catalyst CLI:** We will install the command-line tool by running a simple command.
3. **Login to Catalyst:** You will log into your Zoho account from the command line.
4. **Initialize Project:** We will run a command to create the basic folders (the "project structure") for our Python serverless function.

## Phase 2: Building the Application (The Python Code)

1. **Write the RAG Pipeline:** We will write the Python code inside the Catalyst function folder to:
   - Connect to Product Hunt, Hacker News, TechCrunch, VentureBeat, and the other RSS feeds.
   - Extract and summarize the content using the Gemini 3 Flash model.
   - Compare articles to avoid duplicates using ChromaDB.
2. **Setup Zoho Data Store:** We will create the tables in your Zoho Catalyst dashboard to store the `Sources`, `Sent Items`, and `System State`.
3. **Format the Email:** We will write an HTML template to format the AI's JSON output into a beautiful email.
4. **Integrate Resend:** We will add the code to actually send the email using your Resend API key.

## Phase 3: Deployment & Automation

1. **Add Environment Variables:** We will securely add your API keys (Product Hunt, Gemini, Resend) into Zoho Catalyst so they aren't hardcoded in the files.
2. **Deploy to Catalyst:** We will upload our code to Zoho's servers.
3. **Set up Cron:** We will configure the Catalyst Cron service to automatically run our function every day at 10:00 AM IST.

> [!NOTE]
> Since we need to install the Zoho Catalyst CLI on your Windows machine, do you have Node.js installed? You can check by running `node -v` in your terminal. If you don't have it, I will guide you on how to install it.

## User Review Required

Does this step-by-step plan make sense? If you approve, our very first step will be to install the Catalyst CLI. Let me know if you have Node.js installed, and click **Proceed** if you are ready to begin Phase 1!
