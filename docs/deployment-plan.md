# Deployment Plan: Jarvis (Zoho Catalyst via GitHub)

First, good news about Hacker News: **The Hacker News API is completely free and does not require an API key.** We can query it directly without any setup. So you already have everything you need!

Since you are new to Zoho Catalyst and cloud deployments, we have designed the deployment process to be **100% code-free**. We achieve this by using **GitHub Integration**.

## What is "GitHub Integration" (CI/CD)?
Instead of downloading tools to your computer and typing commands into a terminal to upload your code to Zoho, we link your Zoho Catalyst account directly to your GitHub account.

When Zoho Catalyst is linked to your GitHub repository, it can "pull" the code automatically. This means Zoho acts as the server running the code, and GitHub acts as the storage folder holding the code.

Here is how the automated deployment flows, step by step:

## Phase 1: Preparation (GitHub)

1. **Fork the Repository:** You create your own personal copy ("Fork") of the Jarvis project on your own GitHub account. This gives you ownership of the code.

## Phase 2: Zoho Catalyst Setup (The Cloud Server)

1. **Create a Project:** You log into Zoho Catalyst and create a blank project.
2. **Connect GitHub:** You tell Zoho Catalyst to look at your GitHub account and find the Jarvis repository you just forked.
3. **Automated Deployment:** You click a button in Zoho, and Zoho automatically downloads the Python code from GitHub, installs all necessary requirements, and sets up the serverless function. No terminal required!

## Phase 3: Configuration & Automation

1. **Add Environment Variables:** You securely paste your API keys (Product Hunt, Gemini, Resend) directly into the Zoho Catalyst dashboard so the code can use them.
2. **Set up Cron:** You configure the Catalyst Cron service to automatically trigger the function every day at a specific time (e.g., 10:00 AM).

*(For step-by-step click-by-click instructions on how to do this, please see the `README.md` file!)*
