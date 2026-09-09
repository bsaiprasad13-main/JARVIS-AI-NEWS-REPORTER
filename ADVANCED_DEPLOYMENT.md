# Advanced Deployment Guide (CLI Method)

> [!NOTE]
> This guide is for advanced users who prefer to use the command line. If you are a beginner, please see the `README.md` for the much easier, code-free GitHub deployment method.

## Phase 1: Installation & Setup (Your Local Computer)

1. **Install Node.js (Prerequisite):** Zoho's command-line tool needs Node.js installed on your computer. Download it from [nodejs.org](https://nodejs.org/).
2. **Install Zoho Catalyst CLI:** Open your terminal and run:
   ```bash
   npm install -g zcatalyst-cli
   ```
3. **Login to Catalyst:** Log into your Zoho account from the command line:
   ```bash
   catalyst login
   ```
4. **Initialize Project:** Navigate to your downloaded JARVIS folder and run:
   ```bash
   catalyst init
   ```
   Select 'Functions' (Basic I/O) when prompted and link it to your Catalyst project.

## Phase 2: Deployment & Automation

1. **Add Environment Variables:** You must securely add your API keys (Product Hunt, Gemini, Resend) into your `.env` file before deploying.
2. **Deploy to Catalyst:** Upload your code to Zoho's servers by running:
   ```bash
   catalyst deploy
   ```
3. **Set up Cron:** Go to the Zoho Catalyst Console, navigate to Serverless -> Cron, and configure it to automatically run your function every day at 10:00 AM IST.
