# Jarvis: Detailed Architecture Plan

This document outlines the complete architectural blueprint for **Jarvis**, an AI-powered daily RAG application designed to curate and deliver personalized AI and startup news for aspiring Product Managers.

---

## 1. High-Level System Architecture

Jarvis operates as a **Serverless batch job**, triggered once daily. It does not have a user-facing frontend or an always-on backend. The entire architecture is designed to spin up, execute a specific pipeline, and spin down.

### The Pipeline Flow (The "Daily Run")
1. **Cleanup Phase:** Reset transient storage and prune old logs.
2. **Gathering Phase:** Fetch new data from external APIs and RSS feeds.
3. **Storage & Deduplication Phase:** Embed the data, check for duplicates, and store in an in-memory vector database.
4. **Generation Phase (RAG):** Construct a single dynamic prompt containing all valid data and query the LLM.
5. **Delivery Phase:** Parse the LLM's JSON response, inject it into an HTML template, and send the email.

---

## 2. Component Design & Tech Stack

### 2.1 Compute & Orchestration: Zoho Catalyst Serverless
- **Environment:** Python Serverless Function.
- **Trigger:** Zoho Catalyst Cron (Scheduled for 10:00 AM IST daily).
- **Secrets Management:** Catalyst Environment Variables (API Keys for Resend, Gemini, Product Hunt).

### 2.2 Persistent Data Layer: Zoho Catalyst Data Store (or Local SQLite)
A small, persistent relational database that maintains state across daily runs.
**Tables Needed:**
1. `SystemState`: Tracks the UTC timestamp of the last successful run. (1 row only).
2. `Sources`: Stores the source name, URL, access method (API/RSS), and designated section. This table is updated dynamically if self-healing changes a URL.
3. `SentItems`: A log of previously sent articles (URL/Title, Date) to prevent duplicate sends over a rolling 14-day window.

### 2.3 Transient Vector Database: ChromaDB (Persisted to Disk)
- **Role:** Temporary storage for the day's fetched articles to enable RAG similarity search and semantic deduplication.
- **Lifecycle:** Persisted to disk locally (e.g., `./chroma_data`) so that the data remains available for you to inspect between runs. At the very start of the *next* daily trigger, the database is explicitly cleared/wiped before gathering new data.
- **Embeddings Model:** `BAAI/bge-small-en-v1.5` (via Hugging Face `sentence-transformers`).
- **Deduplication Logic:** Before inserting a new item, its embedding is compared against the current memory. If Cosine Similarity > 0.90, the item is discarded as a duplicate.

### 2.4 Data Fetchers (Ingestion Layer)
Modular fetchers designed to handle specific source types without HTML scraping.
- **API Fetcher:** GraphQL queries for Product Hunt; Algolia REST API for Hacker News.
- **RSS Fetcher:** Standard XML parsing using `feedparser` for TechCrunch, VentureBeat, YourStory, Inc42, and TechCircle.
- **Time Filtering:** All timestamps from APIs/RSS are converted to UTC immediately and compared against the `SystemState` "last successful run" timestamp. Hard lookback cap: 72 hours.

### 2.5 The RAG Engine (Generative Layer)
- **Model:** Gemini 3 Flash (Google AI Studio Free Tier).
- **Prompt Construction:** A single mega-prompt is built dynamically. It includes:
  1. The static instructions (Tone, Persona, Section constraints).
  2. The dynamically fetched articles (Title, Link, Source, Upvotes/Signal).
  3. A dynamic placeholder `{{FAILED_SOURCES_PLACEHOLDER}}` if any fetchers failed.
- **Output:** Strictly structured JSON defining `section_1_tools`, `section_2_ai_news`, `section_3_india_news`, and `section_notes`.

### 2.6 Delivery System (Presentation Layer)
- **Templating:** `Jinja2` (or Python's built-in string formatting) renders a static, single-column HTML email template.
- **Mailing:** The `resend` Python SDK dispatches the HTML string to the user.

---

## 3. Resilience and Self-Healing Architecture

Jarvis is designed to run unattended. Its architecture accounts for external failures gracefully.

### 3.1 RSS Self-Healing
If an RSS source returns an error (404, malformed XML):
1. The fetcher enters a retry/guess loop (up to 4-5 attempts) to find an updated RSS URL for the publication.
2. A URL is only deemed "fixed" if it passes a structural content check (valid XML with dated items).
3. If fixed, the `Sources` table in the persistent database is silently overwritten with the new URL.

### 3.2 Degraded State Handling
- **Source Failures:** If a source fails completely (API down, or RSS cannot self-heal), the system catches the exception, flags the source as failed, and continues fetching from the remaining sources. The failed source name is passed to the Gemini prompt so the AI can explain the lack of news in the email.
- **Partial Content:** If a section has 0-2 items, the email still sends, using the `section_notes` to display a "Quiet Day" or "Source Issue" message instead of failing the pipeline.

### 3.3 Critical Alerting
If a core component fails (e.g., Database unreachable, Gemini API quota exceeded, Resend down), the main pipeline crashes, and a secondary, independent try/except block catches the fatal error and sends a plain-text "System Health Alert" email containing the stack trace.

---

## 4. GitHub Repository Structure Blueprint

```text
jarvis/
├── main.py                 # Cron entry point, orchestrates the daily run
├── fetchers.py             # Logic for API/RSS fetching and self-healing
├── vector_store.py         # ChromaDB in-memory setup and deduplication
├── database.py             # SQLite/Catalyst Data Store interface
├── rag_engine.py           # Gemini 3 Flash integration and prompt handling
├── email_sender.py         # Resend integration and Jinja2 rendering
├── template.html           # The static HTML email layout
├── requirements.txt        # Python dependencies
└── .env                    # API keys (Not pushed to version control)
```
