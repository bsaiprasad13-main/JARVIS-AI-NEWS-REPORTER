# Jarvis — Final Project Documentation

**Purpose of this document:** This is the complete, confirmed build specification for Jarvis. It is meant to be used directly as the reference for building the project in Antigravity.

---

## 1. Core Concept

Jarvis is a daily AI-powered RAG (Retrieval-Augmented Generation) application. Every day it gathers fresh information from a set of sources, stores it temporarily in a vector database, and uses a single RAG query to generate a personalized email digest.

**Primary goal:** Help the user — a final-year engineering student transitioning into a product management career, actively seeking APM/PM roles as a fresher — stay updated on:
- The AI industry (new models, model performance, company moves, funding, shutdowns)
- Credible AI tools relevant to product management work and student life
- Company and startup activity specifically in India (funding rounds, layoffs, leadership changes, product launches, major moves)

All content is filtered through one lens: **"Does this genuinely help someone trying to break into product management right now?"**

---

## 2. Daily Pipeline Flow

Runs automatically once per day, at **10:00 AM IST**. Each run follows this sequence:

1. **Cleanup phase (start of run):**
   - Vector database is **completely cleared** (no memory carried over from previous days)
   - Sent-items log is **pruned**: entries older than 14 days are deleted
2. **Data gathering phase:**
   - System pulls data from all active sources
   - Only items **published after the last successful run** are considered
   - Lookback window is **capped at 72 hours maximum**, regardless of how long since the last successful run
   - The system tracks which sources succeeded and which failed during this phase
3. **Storage phase:**
   - New data is stored in the (now-empty) vector database
   - **Duplicate detection happens here, before storage** — no duplicate content is allowed to enter the vector database in the first place (see Section 6)
4. **Generation phase:**
   - A **single RAG query** (one prompt, see Section 4) is sent, instructing the AI to extract and structure all three email sections at once from whatever is currently in the vector database
   - The prompt is dynamically filled at runtime with the list of any sources that failed that day — this information is used only for that run and is not stored for future runs
   - No secondary quality-check step, no retry loop, no fallback-on-failure logic on the generated content itself
5. **Delivery phase:**
   - Email is sent to the user, built from the AI's structured JSON output

---

## 3. Email Structure

### Three Sections

1. **AI tools for product managers** — tools useful for PM work and student life. Doesn't strictly exclude tools that aren't PM-specific, but clearly highlights which ones are PM-relevant.
2. **AI industry and news updates** — new models, model performance, company moves, general industry activity. (No distinction between "industry updates" and "news updates" — merged into one section.)
3. **India-specific company and startup news** — funding rounds, layoffs, leadership changes, product launches, major company moves. India-specific, not global.

### Per-Item Content Requirements

Every item included in the email must have:
- A short, clear **title**
- The **source name** it came from (e.g. "TechCrunch", "Product Hunt", "Entrackr") — stated explicitly, not just implied by the link
- The **direct source link**, so the user can read further
- An **AI-written line explaining why it matters** to the user specifically, in casual, simple language — grounded in their context as a student transitioning into product management

### Item Volume

- **Hard limit: 3 to 8 items per section**
- The **AI decides the exact count** based on what's genuinely available that day
- This instruction is given explicitly inside the RAG query itself

### Section 1 Specifics (AI Tools)

- Sourced from a **shared pool** across two sources: Product Hunt and Hacker News
- AI picks the best 3–8 items **combined across both sources**, not a fixed split per source
- **No numeric popularity/verification threshold.** Left entirely to AI judgment, guided by signals present in the retrieved data (upvotes, engagement, discussion quality)

### Empty / Reduced Section Handling

If a section has fewer than 3 genuine items available, the email includes only what's real and does **not** pad with weak or irrelevant content. Additionally, the message shown distinguishes **why**:
- **Quiet day** — filters ran normally, there just wasn't much genuine activity in that area
- **Source issue** — one or more of that section's sources technically failed to return data, so the low/zero count may not reflect actual quiet news

This distinction reuses the source success/failure tracking already captured during the data-gathering phase — it is not separate new infrastructure.

---

## 4. The RAG Query (Final Prompt)

There is **one single RAG query** per run — one prompt, not three separate ones. Retrieval uses similarity-based search against the day's vector database (standard RAG pattern), pulling the most relevant stored items for the AI to work from. The pipeline injects the failed-sources list into the placeholder at runtime; this data is not persisted.

**Metadata passed alongside each retrieved item:** each item given to the AI includes not just its title, link, and source, but also its available **popularity/quality signal** where one exists (Product Hunt vote count, Hacker News points). This is what allows the AI to actually judge "popular and credible" in practice — since the numeric threshold was removed (Section 11), the AI needs this signal visible in the data itself, not just implied by the title, to make that judgment meaningfully rather than guessing.

**Item ordering within each section:** items are ordered by **relevance/importance**, as judged by the AI, not strictly by publish date. The AI decides this using the full context available (recency, popularity signal, and how directly the item relates to the user's PM-transition goal).

**Output format: structured JSON** (not raw prose), so the email-building code can reliably parse and format it consistently every day.

```
You are writing a daily personalized digest email for a final-year 
engineering student who is transitioning into a product management 
career. They are actively looking for Associate Product Manager (APM) 
and Product Manager (PM) roles as a fresher. Everything you pick and 
every explanation you write should answer this: "Would this genuinely 
help someone trying to break into product management right now?"

Write in a casual, friendly tone. Use simple, everyday English. Avoid 
complex or fancy words. Keep sentences short and easy to read, like 
you're explaining it to a friend.

You have access to a database of articles, tool listings, and news 
items gathered from the last 24-72 hours. Each item may include a 
popularity/quality signal (such as upvotes or points) where available 
— use this, alongside relevance to the user's goals, to judge 
credibility and importance. Use ONLY this retrieved data. Do not use 
outside knowledge or make anything up. Every item must come directly 
from the retrieved content.

Within each section, order the items by relevance and importance to 
the user (not strictly by publish date) — put the most useful, most 
credible, most significant items first.

Generate exactly three sections, in this order:

SECTION 1: AI Tools for Product Managers
Pick 3 to 8 tools from the retrieved data (sourced from Product Hunt 
and Hacker News). Prioritize tools that are genuinely useful for PM 
work (roadmapping, user research, analytics, prototyping, writing, 
productivity) or broadly useful for student/professional life. Judge 
quality and popularity yourself based on what's in the data (upvotes, 
engagement, discussion) — skip anything that looks obscure or 
low-effort.

SECTION 2: AI Industry News
Pick 3 to 8 items from the retrieved data (sourced from TechCrunch and 
VentureBeat). Focus on new model releases, model performance, big 
company moves, funding, shutdowns, or anything shaping the AI industry.

SECTION 3: India Startup & Company News
Pick 3 to 8 items from the retrieved data (sourced from YourStory, 
Inc42, and TechCircle). Focus on funding rounds, layoffs, leadership 
changes, product launches, or big moves by companies and startups in 
India specifically.

For EVERY item in every section, include:
1. A short, clear title
2. The source name it came from (e.g. "TechCrunch", "Product Hunt")
3. The direct link/URL
4. A 1-2 sentence explanation, in simple casual language, of why this 
   matters to a student trying to get into product management — be 
   specific, not generic

If a section has fewer than 3 genuine items available, include only 
what's real and clearly say today was quiet in this area. Do not pad 
with weak or irrelevant content just to hit a minimum.

{{FAILED_SOURCES_PLACEHOLDER}} — this will be filled in at runtime by 
the pipeline with a list of any sources that technically failed to 
return data today (if any). If a section's low or zero item count is 
because a source failed, say so clearly instead of making it sound 
like a quiet news day. This information is provided fresh for this 
run only and should not be treated as something to remember for 
future runs.

Return your response strictly as JSON in this structure:
{
  "section_1_tools": [
    {
      "title": "",
      "source": "",
      "link": "",
      "why_it_matters": ""
    }
  ],
  "section_2_ai_news": [ ... same structure ... ],
  "section_3_india_news": [ ... same structure ... ],
  "section_notes": {
    "section_1_status": "normal | quiet | source_issue",
    "section_2_status": "normal | quiet | source_issue",
    "section_3_status": "normal | quiet | source_issue"
  }
}
```

---

## 5. Data Freshness & Reliability Logic

- The system tracks its **own internal "last successful run" timestamp** rather than depending solely on source-provided timestamps
- **All timestamps are normalized to UTC internally**, the moment they're captured, before any comparison happens. This avoids inconsistencies between US-timezone sources (TechCrunch, VentureBeat) and IST-timezone sources (YourStory, Inc42, TechCircle)
  - IST is only relevant for the **10:00 AM trigger time** itself, which is internally converted to UTC for execution
- If a run fails, the next run automatically looks back further, since lookback is based on "time since last **successful** run," not "time since last **scheduled** run" — no special-case handling needed
- **Lookback window capped at 72 hours maximum.** Beyond this, the email should note that some earlier updates may have been missed

### How Publish Dates Are Actually Obtained, Per Source Type

- **API-based sources (Product Hunt, Hacker News):** Both return a structured timestamp field as part of the normal API response (Product Hunt: `createdAt`; Hacker News Algolia API: `created_at`). No extra handling needed beyond converting to UTC.
- **RSS-based sources (TechCrunch, VentureBeat, YourStory, Inc42, TechCircle):** RSS is a standardized format with a built-in `pubDate` field as part of the spec itself. Every properly-formed feed item includes this. Read directly, convert to UTC, filter normally.
- With the source list now fully API/RSS-based (see Section 8), **every source provides a real, structured publish timestamp** — no fallback logic (first-seen time, position-based ordering) is currently needed anywhere in the pipeline. This is documented here for completeness in case a future source lacks a reliable timestamp field.

### What Is Actually Stored Long-Term vs. What Is Transient

It's important to be precise about this, since it's easy to assume published dates are logged somewhere historically — they are not.

- **Stored long-term (persists across days):** Only a single value — the **last successful run timestamp**, held in the system-state table (Section 7). This is the one reference point every run compares against.
- **Not stored long-term:** Individual published dates of articles/tools are never saved as an ongoing historical record. Each run reads an item's published date live from the source (API field or RSS `pubDate`), compares it against the single stored "last successful run" timestamp to decide new vs. old, and then discards that comparison — it isn't logged anywhere as a record.
- **Transient (exists only for that day):** If an item passes the filter, its published date may be included as metadata alongside it in that day's vector database entry (useful context for the AI during generation). This disappears when the vector database resets at the start of the next run.
- **A separate, different table — not to be confused with the above:** The sent-items log (Section 7) stores *when an item was sent to the user*, not when it was *published*. It exists purely to prevent duplicate sends and is unrelated to the new-vs-old filtering logic described here.

In short: the system doesn't need a growing archive of every article's publish date. It only needs one saved reference point (last successful run) and a live, in-the-moment comparison against it, every run.

---

## 6. Duplicate Content Handling

- Duplicate detection happens **at the point of storage into the vector database**, not later during generation
- Before a new item is inserted, its embedding is compared against what's already stored that day. **Similarity threshold: cosine similarity above 0.90** is treated as a duplicate and is not stored. This is a standard, well-tested starting point for near-duplicate detection at the embedding model scale being used (`BAAI/bge-small-en-v1.5`) — high enough to avoid false positives (flagging genuinely different stories as duplicates), while still catching the same underlying story covered by two different outlets with different wording.
- This solves the "same story from two different sources, different URL/title" problem (e.g., TechCrunch and VentureBeat covering the same announcement), since comparison is based on semantic content, not exact URL/title matching
- Because duplicates are prevented at storage, **no special merge/display logic is needed in the email**

---

## 7. Data Storage Architecture

### Vector Database
- Resets **completely** on every run
- Exists only to support that day's RAG generation
- No persistence, no memory across days
- Duplicate-free by design

### Small SQL Database (SQLite or Postgres)
Persists across days. Contains:

1. **Sources table** — source name, current URL, access method (API/RSS/scrape), which section it belongs to. **Self-updating** for RSS/HTML sources: when the source-monitoring agent finds a working replacement URL for a broken source, it permanently overwrites the old URL here
2. **Sent-items log** — item URL/title, date sent, section. Used for deduplication against previously sent content (active check window: last 3–4 days). **Entries older than 14 days are automatically pruned** at the start of each daily run
3. **System-state table** — single-row table tracking the last successful run timestamp (UTC) and last run status

---

## 8. Final Source List & Strategy (Confirmed)

### Section 1: AI Tools
| Source | Access Method | Notes |
|---|---|---|
| **Product Hunt** | Official free GraphQL API v2 (developer token via producthunt.com/v2/oauth/applications) | Query by AI-related topic, filter by launch date |
| **Hacker News** | Official free Algolia Search API (hn.algolia.com/api), no key required | Filter by "show_hn" tag and date |

Both feed a **shared pool**; AI selects the best 3–8 combined. No self-healing URL logic applies to either (API failures are auth/schema issues, not URL issues) — if a call fails, the source is skipped for the day and flagged.

### Section 2: AI Industry/News
| Source | Access Method | Notes |
|---|---|---|
| **TechCrunch** (AI category) | RSS | Confirmed via site's own "RSS Terms of Use" — RSS is the sanctioned method; general scraping is explicitly prohibited by TechCrunch's ToS |
| **VentureBeat** (AI category) | RSS | RSS confirmed via third-party evidence. Note: if ever falling back to HTML, the page mixes real articles with "Partner Content" (sponsored) — must be filtered out |

### Section 3: India Startups/Companies
| Source | Access Method | Notes |
|---|---|---|
| **YourStory** | RSS | Confirmed via third-party evidence; dedicated Funding category also available as backup reference |
| **Inc42** | RSS | Confirmed via third-party evidence. Some content is gated behind "Inc42 Plus" paywall — headlines and snippets are accessible, full article text may not be. Use headline + snippet only |
| **TechCircle** (startups category — techcircle.in/category/startups) | RSS | Replaces Entrackr. Confirmed RSS via independent directory listing. Owned by VCCircle (part of HT Media Limited), a credible, established Indian business/investment media group. Strong fit for funding and investment-focused coverage |

**Note on this swap:** Entrackr was originally in this slot but had no confirmed RSS feed, requiring HTML scraping and a timestamp-fallback strategy. TechCircle was chosen as a replacement specifically because it has confirmed RSS (solving the publish-date problem cleanly — see Section 5) and comes from a credible, established media house with a strong investment/funding focus, closely matching what was wanted from Entrackr in the first place.

### Self-Healing Logic (RSS Sources Only)
Applies to TechCrunch, VentureBeat, YourStory, Inc42, TechCircle — not to Product Hunt or Hacker News (API-based, different failure mode). With this swap, **every RSS/scrape-category source is now RSS-based** — no HTML scraping remains anywhere in the source list.

- If a source stops returning valid data, the AI **attempts to guess a corrected/updated URL**, up to **4–5 attempts**, no human approval required
- A URL is only accepted as "fixed" if it passes a **structural content check** (for RSS: valid feed XML with multiple dated items; for HTML: recognizable article-list structure with titles, links, dates). Returning HTTP 200 alone is not sufficient — a structurally invalid response counts as a failed attempt
- On success, the new URL **permanently replaces the old one** in the sources table, silently
- On failure after 4–5 attempts: source is skipped for the day, system continues with other sources, and the broken source is **flagged inside that day's regular content email**

### Redesign / Feed Change Detection
A basic sanity check runs after every fetch: did it return at least one item, with all expected fields (title, link, date)? Zero items or malformed items are treated exactly like a broken source — same flagging and self-healing logic applies. This also naturally covers the rare case of an RSS feed becoming malformed or discontinued.

### Manual Verification Steps Remaining
With the Entrackr-to-TechCircle swap, the source list is now fully API/RSS-based, with no HTML scraping and no unresolved robots.txt concerns. **No outstanding manual verification steps remain in the source list.**

---

## 9. Failure Notification System

Two separate, independent types of failure communication:

1. **Broken-source flag** — included inside that day's regular content email. Communicates "one or more sources couldn't be reached/fixed today," while the rest of the digest still sends normally. Also drives the "source_issue" section status used in the empty/reduced-section messaging (Section 3).
2. **System-health alert email** — a **separate email**, triggered by any unhandled pipeline failure (database connection failure, RAG query failure, email delivery failure, etc.). Sent via a path **independent of the main pipeline**, so a broken main pipeline isn't responsible for reporting its own failure. Includes what step failed, the error message, and the timestamp.

These are kept deliberately separate so one type of issue never buries or gets confused with the other.

---

## 10. Budget & Manual Work Constraints

- **Budget: zero.** No paid APIs, no paid tiers, no paid calls
- **Manual work the user is willing to do:** signing up for and managing free API keys
- **Source type:** entirely official free APIs (Product Hunt, Hacker News) and RSS feeds (TechCrunch, VentureBeat, YourStory, Inc42, TechCircle) — no HTML scraping anywhere in the current source list

---

## 11. Explicitly Removed / Rejected During Design

Noted here so these aren't accidentally reintroduced during build:

- **Output quality-checking layer** — no AI-driven review/retry loop on generated email content before sending
- **Token-exhaustion fallback messaging** — no logic for falling back to a "first attempt" output or flagging token exhaustion
- **Merged/duplicate-story display logic in the email** — unnecessary once duplicate prevention was moved to the storage stage
- **Popularity/verification numeric threshold** (e.g., minimum upvotes) for the AI Tools section — removed, left fully to AI judgment guided by the RAG query
- **The Verge AI** as a source — dropped after direct verification showed the site blocks automated fetching
- **Entrackr** as a source — replaced with TechCircle, since Entrackr had no confirmed RSS feed and would have required HTML scraping plus a timestamp-fallback strategy (first-seen time / newest-first ordering). TechCircle solves this cleanly via RSS
- **Self-healing URL logic for Product Hunt and Hacker News** — not applicable, since these are API-based sources with a different failure mode (skip-and-flag instead)

---

## 12. Tech Stack (Confirmed)

- **Embeddings model:** `BAAI/bge-small-en-v1.5` (via Hugging Face). Used to generate embeddings for items before storing them in the vector database, both for RAG retrieval and for the duplicate-detection similarity check (Section 6). Note: Antigravity may suggest adjustments to this choice based on the actual data it extracts during build — this is expected and acceptable.
- **Generation model:** Gemini (Google AI Studio free tier), specifically **Gemini 3 Flash** (or Flash-Lite if needed for higher throughput during testing). No credit card or billing account required on the free tier. Free-tier rate limits are tight (roughly 10-15 requests per minute), but since Jarvis makes only one RAG generation call per day, this is not a practical constraint. Note: as of May 2026, Gemini Pro models require billing — only Flash-tier models remain free, which is sufficient for this structured-generation task.
- **Vector database:** ChromaDB, run in lightweight in-memory/embedded mode within the Python function, not as a separately hosted service. This fits naturally since the vector database is already designed to reset completely every run (Section 7) — an in-memory instance that's created fresh, filled, queried, and discarded each run matches this exactly, and pairs well with the chosen embeddings model.
- **Email delivery:** Resend. Handles sending the final formatted email to the user.
- **Hosting & scheduling:** Zoho Catalyst. Confirmed to support:
  - **Cron** — a built-in job scheduler that can trigger a function daily at a specific time (10:00 AM IST), exactly what's needed for the daily trigger
  - **Data Store** — Catalyst's own hosted database, a natural fit for the small SQL database described in Section 7 (sources table, sent-items log, system-state table), avoiding the need for a separate external database service
  - **Serverless Functions** — supports Python, which fits the RAG/embedding/scraping pipeline logic
  - **Environment Variables** — Catalyst's built-in, secure mechanism for storing sensitive credentials (Product Hunt key, Resend key, Gemini key, etc.) rather than hardcoding them into function code. Confirmed as a standard supported feature.
  - Free tier is available and suitable for this project's scale (daily, low-frequency execution)

### Testing
Testing before relying on the live daily schedule is being handled directly by the user — not a process defined in this document.

---

## 13. Email HTML Formatting

The AI outputs structured JSON (Section 4), which is then converted into the actual visual email before being sent via Resend.

- **Approach: a predefined, static HTML email template with placeholders**, populated using Python string/template substitution (e.g. Jinja2), rather than having the AI generate HTML directly. This keeps visual formatting consistent every single day, regardless of what content the AI produces, and avoids the risk of the AI generating broken or inconsistent HTML/CSS.
- **Layout:** single-column, simple structure — a short header/greeting, followed by the three sections in order (AI Tools, AI Industry News, India Startups/Companies), each with a clear section heading. Within each section, items are displayed as simple stacked blocks: title (as a clickable link to the source), source name, and the "why it matters" line underneath.
- **Styling:** inline CSS (required for reliable rendering across email clients like Gmail/Outlook, since many clients strip `<style>` blocks). Kept minimal and clean — no heavy design system needed for a personal daily digest.
- **Empty/reduced sections:** rendered using the same template structure, but showing the quiet-day or source-issue message (Section 3) in place of item blocks for that section.
- **Delivery:** the populated HTML string is passed to Resend's send-email API as the email body.

This keeps the AI responsible only for *content* (what to say), while formatting/presentation stays deterministic and fully controlled by the template — this separation also makes the email's appearance easy to redesign later without touching the RAG prompt at all.

---

## 14. Constraints & Success Criteria

### Constraints (Hard Rules the System Must Always Respect)
1. **Cost constraint** — zero paid API usage. If a source or service requires payment, it is excluded, not worked around.
2. **Item count constraint** — never fewer than 0 or more than 8 items per section.
3. **Data freshness constraint** — never include content older than 72 hours from the last successful run.
4. **No fabrication constraint** — the AI must never generate or include an item not grounded in retrieved data.
5. **Delivery reliability constraint** — the email must attempt to send even in degraded conditions (e.g., only one section has content); it should never silently fail to send just because content is thin.

### Success Criteria (How to Judge Whether a Day "Worked")
1. **Delivery success** — did the email arrive by roughly 10:15 AM IST (a small buffer past the 10:00 trigger)?
2. **Structural success** — does the email contain all three sections (even if some are marked quiet/source-issue), with every item having a title, source name, link, and "why it matters" line?
3. **Freshness success** — is every included item genuinely published within the lookback window, not stale content slipping through?
4. **No-duplicates success** — no item appears that was already sent in the last 3–4 days?
5. **Relevance success** — do the "why it matters" lines actually sound specific and grounded, not generic filler? (Harder to automate — worth periodic manual spot-checking rather than a system-level check.)
