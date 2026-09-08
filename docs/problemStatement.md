# Problem Statement & Project Context: Jarvis

## Overview
Jarvis is a daily AI-powered RAG (Retrieval-Augmented Generation) application designed to generate a personalized email digest. The primary target audience is a final-year engineering student transitioning into a product management (APM/PM) career.

## The Problem
Aspiring Product Managers need to stay up-to-date with industry trends, AI advancements, and local startup ecosystems to remain competitive. However, information is scattered across numerous platforms (Product Hunt, Hacker News, TechCrunch, VentureBeat, Inc42, etc.). Manually curating this information, filtering out the noise, and contextualizing it for a fresher aiming for PM roles is a time-consuming and overwhelming daily task.

## The Solution
Jarvis automates this curation process. Every day at 10:00 AM IST, it gathers fresh information (published within the last 24-72 hours) from a curated set of sources, temporarily stores it in an in-memory vector database, and uses a single RAG query to generate a structured, personalized email digest. All content is filtered through one specific lens: **"Does this genuinely help someone trying to break into product management right now?"**

## Core Features & Workflow

### 1. Data Gathering & Sources
The system pulls data daily from free, official APIs and RSS feeds (no HTML scraping to ensure reliability and zero-cost).
- **AI Tools for PMs:** Product Hunt (API), Hacker News (API)
- **AI Industry & News:** TechCrunch (RSS), VentureBeat (RSS)
- **India Startup & Company News:** YourStory (RSS), Inc42 (RSS), TechCircle (RSS)

### 2. Storage & Deduplication
- A lightweight, transient **ChromaDB** vector database is spun up each run. It is wiped completely at the start of each day.
- A small persistent **SQL database (Zoho Catalyst Data Store)** maintains the list of sources, tracks the "last successful run" timestamp to ensure only new articles are processed, and keeps a 14-day log of sent items to prevent duplicates.
- Semantic deduplication (cosine similarity > 0.90) is performed via embeddings (`BAAI/bge-small-en-v1.5`) *before* storing items in the daily vector database.

### 3. Generation (RAG)
- Uses **Gemini 3 Flash** (free tier).
- A single, dynamically constructed prompt instructs the AI to extract and structure 3 to 8 highly relevant items per section.
- The AI autonomously judges the importance of each item using available metadata (e.g., upvotes) and writes a custom "why it matters" explanation tailored to an aspiring PM.

### 4. Self-Healing Mechanisms
- If an RSS feed breaks, the system attempts to auto-guess and validate a new URL. If successful, it updates the database silently.
- Failed sources are dynamically logged and reported in the daily email without failing the entire pipeline.
- Separate alerts are sent for critical system failures (e.g., database connection issues).

### 5. Delivery
- The final output is parsed from JSON and formatted into a clean, static HTML template.
- The email is sent via the **Resend** API.
- Scheduled and hosted entirely on **Zoho Catalyst** (Serverless Functions, Data Store, and Cron).

## Constraints
- **Zero Cost:** Absolutely no paid APIs or tiers.
- **Data Freshness:** Lookback window is strictly capped at 72 hours.
- **Accuracy:** Strict "No fabrication" rule; the AI must only use retrieved data.
- **Reliability:** The system must gracefully handle partial failures (e.g., empty sections on a slow news day) and continue to deliver the email.
