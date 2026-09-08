import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

lib_dir = os.path.join(current_dir, 'lib')
if os.path.exists(lib_dir) and lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)

import traceback
import datetime
import json
from database import init_db, get_last_run_time, update_last_run_time, get_sources, update_source_url, log_sent_items, is_item_sent_recently, prune_sent_items
from fetchers import fetch_all_data, get_utc_now
from vector_store import VectorStore
from rag_engine import generate_email_content
from email_sender import send_daily_digest, send_alert_email

def run_daily_pipeline():
    """Core pipeline execution logic."""
    print("=== JARVIS: Starting Daily Run ===")
    
    # 1. Cleanup & Init Phase
    print("\n[1/5] Cleanup & Init Phase")
    init_db() # Populates initial state/sources if empty
    prune_sent_items() # Remove sent logs > 14 days old
    
    vector_store = VectorStore()
    vector_store.reset_for_new_run() # Wipe /tmp ChromaDB
    
    last_run_utc = get_last_run_time()
    print(f"Last successful run was: {last_run_utc}")

    # 2. Data Gathering Phase
    print("\n[2/5] Data Gathering Phase")
    sources = get_sources()
    all_items, failed_sources, updated_urls = fetch_all_data(sources, last_run_utc)
    
    # Self-healing: Update DB if any RSS feeds redirected/changed
    for name, new_url in updated_urls.items():
        update_source_url(name, new_url)
        print(f"Self-Healed: Updated URL for {name} in Data Store.")
        
    print(f"Gathered {len(all_items)} potential items.")
    if failed_sources:
        print(f"Warning, failed sources: {failed_sources}")

    # 3. Storage & Deduplication Phase
    print("\n[3/5] Storage Phase")
    stored_items = []
    for item in all_items:
        # Check Data Store if sent in last 14 days
        if is_item_sent_recently(item['url']):
            print(f"Skipping already sent item: {item.get('title')}")
            continue
            
        # Check ChromaDB for semantic duplicates
        if vector_store.add_item_if_not_duplicate(item):
            stored_items.append(item)
            
    print(f"Successfully stored {len(stored_items)} unique, unsent items in Vector DB.")

    # 4. Generation Phase (RAG)
    print("\n[4/5] Generation Phase")
    valid_vector_data = vector_store.get_all_items()
    
    if not valid_vector_data:
        print("No new data to report today. Email will indicate a quiet day.")
        
    generated_json = generate_email_content(valid_vector_data, failed_sources)
    
    if not generated_json:
        raise Exception("RAG generation returned None (LLM failure).")
        
    print("Generated JSON payload successfully.")

    # 5. Delivery Phase
    print("\n[5/5] Delivery Phase")
    email_sent = send_daily_digest(generated_json)
    
    if email_sent:
        # Mark items as sent in Data Store
        log_sent_items(valid_vector_data)
        # Update successful run timestamp
        update_last_run_time(get_utc_now().isoformat())
        print("Pipeline completed successfully! Timestamps and sent logs updated in Data Store.")
        return {"status": "success", "items_processed": len(valid_vector_data)}
    else:
        raise Exception("Email failed to send via Resend.")

def runner(context):
    """
    Zoho Catalyst Cron Function entry point.
    """
    try:
        result = run_daily_pipeline()
        print(f"Cron execution finished successfully: {result}")
        if hasattr(context, 'close'):
            context.close()
    except Exception as e:
        error_trace = traceback.format_exc()
        print("\n!!! PIPELINE FAILED !!!")
        print(error_trace)
        try:
            send_alert_email(error_trace)
        except Exception as alert_err:
            print(f"Failed to send alert email: {alert_err}")
        if hasattr(context, 'close'):
            context.close()

def handler(context, basicio=None):
    """
    Zoho Catalyst Basic I/O Function entry point.
    """
    try:
        result = run_daily_pipeline()
        if basicio and hasattr(basicio, 'write'):
            basicio.write(json.dumps(result))
        if hasattr(context, 'close'):
            context.close()
    except Exception as e:
        error_trace = traceback.format_exc()
        print("\n!!! PIPELINE FAILED !!!")
        print(error_trace)
        try:
            send_alert_email(error_trace)
        except Exception as alert_err:
            print(f"Failed to send alert email: {alert_err}")
            
        if basicio and hasattr(basicio, 'write'):
            basicio.write(json.dumps({"status": "failed", "error": str(e)}))
        if hasattr(context, 'close'):
            context.close()

if __name__ == "__main__":
    # For local debugging if needed
    run_daily_pipeline()
