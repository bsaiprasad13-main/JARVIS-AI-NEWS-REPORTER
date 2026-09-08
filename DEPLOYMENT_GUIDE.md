# 🤖 AI-Assisted Deployment Guide

Deploying code and setting up cloud environments can be tricky. To make this process as smooth as possible, we recommend using an AI Coding Assistant (like **Google Anti Gravity**, cursor, or any agentic AI IDE) to automate the deployment to Zoho Catalyst.

## Step-by-Step AI Setup

### Step 1: Download & Open the Project
1. Download or clone this repository to your local machine.
2. Open the downloaded folder in your AI IDE (e.g., Google Anti Gravity).

### Step 2: Feed the Setup Prompt to the AI
Open the AI chat/prompt window in your IDE, copy the exact prompt below, and paste it in. 

***

**📋 Copy this prompt:**

> "I have just downloaded the JARVIS AI News Reporter project. Please act as my deployment assistant.
> 
> Here is our plan:
> 1. **Environment Setup**: Scan the codebase to find `.env.example`. Ask me to provide the 5 required values one-by-one. Once I give them to you, create the actual `.env` file for me.
> 2. **Zoho Catalyst Initialization**: Check if the Zoho Catalyst CLI is installed on my machine. If not, give me the command to install it globally via npm.
> 3. **Login**: Ask me to run `catalyst login` in the terminal and let you know when I'm successfully authenticated.
> 4. **Project Setup**: Guide me to initialize the project using `catalyst init`. I want to select 'Functions' (Basic I/O). Help me link it to my existing Zoho project or create a new one.
> 5. **Deployment**: Finally, run the necessary command to deploy the function to my Zoho Catalyst account (`catalyst deploy`).
> 
> Let's do this step-by-step. Start with step 1 and wait for my input."

***

### Step 3: Follow the AI's Lead
The AI assistant will now read the codebase, understand the requirements, and guide you interactively. 
- It will ask you for your API keys (Gemini, Resend, Product Hunt).
- It will create the hidden `.env` file securely on your machine.
- It will run the deployment commands for you or ask you to run them if it needs your manual browser authentication.

### Final Steps: Cron Setup
Once the AI has successfully deployed the code to Zoho Catalyst:
1. Go to your [Zoho Catalyst Console](https://console.catalyst.zoho.com/).
2. Navigate to **Compute > Functions** to verify your `jarvis_pipeline` function is deployed.
3. Navigate to **Cron** (under Serverless) and create a new Cron job.
4. Set the frequency to **Daily** (e.g., 8:00 AM).
5. Set the target to your `jarvis_pipeline` function.

Congratulations! Your automated AI News Reporter is now live and will email you daily.
