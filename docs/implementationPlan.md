# Implementation Plan: Jarvis (Local Code Architecture)

I have saved the deployment plan to `deployment-plan.md` in your workspace. We will focus purely on writing and running the code locally for now.

## Local Development Strategy
Since we aren't using Zoho Catalyst yet, we will use a **local SQLite database** to track the state, sent items, and sources. When we eventually deploy to Catalyst, we will simply swap out the SQLite code for Catalyst Data Store code. Everything else (fetching, ChromaDB, Gemini, Resend) will run exactly the same locally as it will in the cloud.

## Proposed Code Structure

We will write the application in modular Python files to keep things clean and easy to maintain:

### 1. `database.py` (Local Persistence)
Manages a local SQLite file (`jarvis.db`) to track:
- **System State:** The UTC timestamp of the last successful run.
- **Sent Items Log:** Prevents duplicate sends (auto-pruned after 14 days).
- **Sources Table:** The list of RSS feeds and API endpoints (auto-updated if an RSS feed heals itself).

### 2. `fetchers.py` (Data Gathering & Self-Healing)
Contains the logic to pull data from all sources:
- **API Fetchers:** GraphQL for Product Hunt and Algolia API for Hacker News.
- **RSS Fetchers:** Parses XML feeds (TechCrunch, VentureBeat, YourStory, Inc42, TechCircle) and handles the "self-healing" logic (guessing a new URL if the feed breaks).

### 3. `vector_db.py` (Storage & Deduplication)
- Initializes an in-memory ChromaDB instance.
- Uses the `BAAI/bge-small-en-v1.5` embedding model.
- Checks the cosine similarity (> 0.90) of new items against already stored items for the day to reject duplicates.

### 4. `rag.py` (Generation)
- Connects to the **Gemini 3 Flash** API.
- Constructs the large RAG prompt, injecting the day's data and any failed sources.
- Returns the structured JSON.

### 5. `email_generator.py` & `template.html` (Delivery)
- A Jinja2 HTML template (`template.html`) for the email layout.
- Python logic to parse the Gemini JSON, populate the HTML template, and send the email using the **Resend API**.

### 6. `main.py` (The Orchestrator)
The single script we will run every day (e.g., `python main.py`). It ties all the above phases together:
Cleanup -> Gather -> Store -> Generate -> Deliver.

## Open Questions
- Do you have Python installed on your computer? (We can check by running `python --version`).
- We will need to store API keys for Gemini, Resend, and Product Hunt in a `.env` file. Do you have these keys ready to paste in?

## User Review Required
Does this modular code structure look good to you? If you approve, I will start by writing the `requirements.txt`, the database initialization code, and the data fetchers. Click **Proceed** to authorize the start of coding!
