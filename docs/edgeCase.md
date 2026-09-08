# Jarvis: Comprehensive Edge Case & Resilience Analysis

This document identifies, analyzes, and documents every conceivable failure mode, edge case, and architectural risk in **Jarvis**, detailing how each is handled in the codebase.

---

## 1. Ingestion Layer Edge Cases (APIs & RSS Feeds)

| Edge Case / Scenario | Impact | Mitigation / Built-in Handling |
| :--- | :--- | :--- |
| **RSS Feed URL 404 / 301 Redirect** | Source fails to deliver articles. | **Self-Healing RSS Engine:** The fetcher attempts 4-5 alternative RSS paths (e.g., `/feed/`, `/rss/`, `/feed/atom/`, category feeds). If a valid XML feed is detected, the URL is updated automatically. |
| **Malformed XML or Incomplete Feed** | XML parser crash. | Multi-tier XML parsing: Falls back from `feedparser` to `xml.etree.ElementTree` with character cleaning. Skips broken `<item>` blocks without crashing the batch. |
| **Publish Date Missing or Non-Standard** | Time-window comparison failure. | Multi-format date parsing: Handles RFC 822 (`email.utils.parsedate_to_datetime`), ISO 8601 (`datetime.fromisoformat`), and pubDate heuristics. Falls back to current UTC timestamp. |
| **Feed Returns 0 Items in 72-Hour Window** | Empty dataset for that source. | Flagged as quiet source (not a fatal error). Remaining sources proceed unimpeded. |
| **API Rate Limiting (Product Hunt / HN)** | HTTP 429 Too Many Requests. | Fetchers employ timeout caps (10-15s) and catch HTTP errors gracefully, logging the failure to `failed_sources` for AI contextualization. |
| **Product Hunt GraphQL Token Expired/Invalid** | API returns 401 Unauthorized. | Logs warning and skips PH, gracefully populating Section 1 with Hacker News AI tools. |
| **Hacker News Algolia Search Outage** | 500 Server Error. | HN fetcher catches exception, logs `Hacker News` into `failed_sources`. |
| **All Sources in a Category Fail Simultaneously** | Empty section in newsletter. | The RAG Engine detects 0 items for that section and generates a clear PM explanation in `section_notes`. |

---

## 2. Storage, Vector DB & Deduplication Edge Cases

| Edge Case / Scenario | Impact | Mitigation / Built-in Handling |
| :--- | :--- | :--- |
| **Identical Article Across Multiple Publications** | Duplicate news stories in email. | **Hybrid Semantic Deduplication:** Vector store checks both exact URL matches and word-overlap / sequence similarity (> 0.85 threshold). Duplicate is skipped. |
| **Syndicated Articles with Different URLs** | Appears as unique by URL. | Text-level similarity checks title and snippet, preventing syndicated duplicates. |
| **Previously Sent Story Resurfaces Days Later** | Repeated content sent to user. | `SentItems` Data Store / SQLite log checks rolling 14-day history. Articles in `SentItems` are skipped during Phase 3. |
| **Corrupted or Native C-Dependency Failures in Serverless** | `chromadb` / `sentence-transformers` crash on lightweight cloud runtimes. | **Pure-Python Vector Store Fallback:** Lightweight pure-Python similarity matching ensures zero-dependency execution across any Serverless Python environment. |
| **Rolling Window Lookback Drift** | Articles older than 72 hours leaking into digest. | Hard 72-hour lookback filter enforced during timestamp normalization. |

---

## 3. Generative Layer (Gemini RAG) Edge Cases

| Edge Case / Scenario | Impact | Mitigation / Built-in Handling |
| :--- | :--- | :--- |
| **Gemini API Quota / Free Tier Limit Exceeded (HTTP 429)** | LLM generation failure. | `rag_engine.py` tries primary model (`gemini-2.5-flash`), falls back to secondary models (`gemini-2.5-flash-lite`, `gemini-1.5-flash`). |
| **LLM Returns Markdown Code Fences (````json ... ````)** | JSON parser error (`json.loads`). | Multi-pass JSON sanitizer strips markdown fences (````json ... ````), extracts valid `{ ... }` blocks using regex. |
| **LLM Omits a Section or Returns Incomplete Keys** | Template rendering crash. | Strict dictionary `.get(..., [])` fallbacks and schema validation ensure all 3 sections and `section_notes` are always present. |
| **Quiet News Day (0 Articles Found Across All Sources)** | LLM has no data to summarize. | Custom "Quiet Day" prompt generates an encouraging PM career tip / concept-of-the-day instead of failing. |
| **Hallucination / Fabrication Risk** | AI invents fake news. | Strict prompt constraints: "Use ONLY retrieved data. Every item must link directly to provided URLs." |

---

## 4. Delivery & Templating Edge Cases (Resend & Email)

| Edge Case / Scenario | Impact | Mitigation / Built-in Handling |
| :--- | :--- | :--- |
| **Template Engine (Jinja2) Dependency Missing** | Template rendering failure. | **Zero-Dependency HTML Generator:** `email_sender.py` includes a robust built-in pure-Python HTML card generator as a fallback. |
| **Resend API Key Invalid or Missing** | Email dispatch fails. | Catches error, triggers alerting workflow with stack trace. |
| **Email Client Breaks CSS / Dark Mode Incompatibility** | Unreadable email formatting. | Fully inlined CSS styles with web-safe font stacks (`-apple-system, Segoe UI, Roboto`) and table/div layout compatibility. |
| **Recipient Mailbox Full / Bounce** | Non-delivery. | Resend handles delivery retries and webhook logging. |

---

## 5. Serverless Runtime & Scheduling Edge Cases (Zoho Catalyst)

| Edge Case / Scenario | Impact | Mitigation / Built-in Handling |
| :--- | :--- | :--- |
| **Cron Trigger Context Mismatch (`AttributeError: 'Context' object has no attribute 'write'`)** | Cron job throws post-execution exception. | Dual entrypoint handlers: `runner(context)` for Cron triggers and `handler(context, basicio)` for Basic I/O, with safe `hasattr()` checks. |
| **Execution Timeout (Exceeding 15-30s Serverless Limit)** | Function killed by platform. | Fast parallel-capable fetching, short socket timeouts (10-15s), lightweight similarity calculations, and minimal network roundtrips keep total execution under 7-10 seconds. |
| **Catalyst SDK Not Initialized / Unreachable** | State persistence fails. | Safe fallback wrappers (`get_catalyst_app()`) allow the pipeline to proceed without breaking newsletter generation and delivery. |
| **Catastrophic Pipeline Failure (Uncaught Exception)** | Silent failure without user notification. | Top-level `try/except` block catches fatal errors and sends an emergency **System Health Alert Email** containing the full traceback. |
