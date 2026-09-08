import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

lib_dir = os.path.join(current_dir, 'lib')
if os.path.exists(lib_dir) and lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)

import datetime

def get_catalyst_app():
    """Safely retrieves or imports the Catalyst App instance."""
    try:
        # Check current directory and lib directory in sys.path
        for p in [current_dir, lib_dir]:
            if os.path.exists(p) and p not in sys.path:
                sys.path.insert(0, p)
        import zcatalyst_sdk
        if hasattr(zcatalyst_sdk, 'initialize'):
            return zcatalyst_sdk.initialize()
    except Exception:
        pass
    return None

def get_datastore():
    """Returns the catalyst datastore service instance."""
    app = get_catalyst_app()
    if app:
        return app.datastore()
    return None

def get_table(table_name):
    """Returns a table instance from Catalyst Data Store."""
    ds = get_datastore()
    return ds.table(table_name)

def init_db():
    """
    Initializes default records if tables are empty.
    Note: Tables SystemState, SentItems, Sources are pre-created in Catalyst console.
    """
    try:
        app = get_catalyst_app()
        if not app:
            return
        ds = app.datastore()
        
        # 1. Check & populate initial SystemState
        state_table = ds.table('SystemState')
        try:
            query_res = app.zcql().execute_query("SELECT ROWID FROM SystemState WHERE state_key = 'last_successful_run'")
            if not query_res:
                initial_time = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3)).isoformat()
                state_table.insert_row({
                    'state_key': 'last_successful_run',
                    'state_value': initial_time
                })
                print("Initialized SystemState in Data Store.")
        except Exception as e:
            print(f"SystemState init check: {e}")

        # 2. Check & populate initial Sources
        sources_table = ds.table('Sources')
        try:
            query_sources = app.zcql().execute_query("SELECT ROWID FROM Sources")
            if not query_sources:
                initial_sources = [
                    {"name": "Product Hunt", "url": "api", "source_type": "api", "enabled": True},
                    {"name": "Hacker News", "url": "api", "source_type": "api", "enabled": True},
                    {"name": "TechCrunch", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "source_type": "rss", "enabled": True},
                    {"name": "VentureBeat", "url": "https://venturebeat.com/category/ai/feed/", "source_type": "rss", "enabled": True},
                    {"name": "YourStory", "url": "https://yourstory.com/feed", "source_type": "rss", "enabled": True},
                    {"name": "Inc42", "url": "https://inc42.com/feed/", "source_type": "rss", "enabled": True},
                    {"name": "TechCircle", "url": "https://www.techcircle.in/category/startups/feed", "source_type": "rss", "enabled": True}
                ]
                for src in initial_sources:
                    sources_table.insert_row(src)
                print("Populated initial Sources in Data Store.")
        except Exception as e:
            print(f"Sources init check: {e}")

    except Exception as e:
        print(f"Init DB general notice: {e}")

def get_last_run_time():
    """Retrieves the last successful run timestamp."""
    try:
        app = get_catalyst_app()
        if app:
            query = "SELECT state_value FROM SystemState WHERE state_key = 'last_successful_run'"
            result = app.zcql().execute_query(query)
            if result and len(result) > 0:
                row = result[0].get('SystemState', result[0])
                val = row.get('state_value')
                if val:
                    return datetime.datetime.fromisoformat(val)
    except Exception as e:
        print(f"Error reading last_run_time: {e}")
    # Default to 3 days ago fallback
    return datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3)

def update_last_run_time(timestamp_iso):
    """Updates the last successful run timestamp."""
    try:
        app = get_catalyst_app()
        if not app:
            return
        query = "SELECT ROWID FROM SystemState WHERE state_key = 'last_successful_run'"
        result = app.zcql().execute_query(query)
        state_table = app.datastore().table('SystemState')
        if result and len(result) > 0:
            row = result[0].get('SystemState', result[0])
            row_id = row.get('ROWID')
            state_table.update_row({
                'ROWID': row_id,
                'state_key': 'last_successful_run',
                'state_value': timestamp_iso
            })
        else:
            state_table.insert_row({
                'state_key': 'last_successful_run',
                'state_value': timestamp_iso
            })
        print(f"Updated last run time to {timestamp_iso}")
    except Exception as e:
        print(f"Error updating last_run_time: {e}")

def get_sources():
    """Returns all enabled sources."""
    try:
        app = get_catalyst_app()
        if app:
            query = "SELECT ROWID, name, url, source_type, enabled FROM Sources"
            results = app.zcql().execute_query(query)
            sources = []
            if results:
                for r in results:
                    row = r.get('Sources', r)
                    name = row.get('name', '')
                    src_type = row.get('source_type', 'rss')
                    
                    if src_type == 'api':
                        section = 'section_1'
                    elif name in ["YourStory", "Inc42", "TechCircle"]:
                        section = 'section_3'
                    else:
                        section = 'section_2'

                    sources.append({
                        "row_id": row.get('ROWID'),
                        "name": name,
                        "url": row.get('url', ''),
                        "method": src_type,
                        "section": section,
                        "enabled": row.get('enabled', True)
                    })
            if sources:
                return sources
    except Exception as e:
        print(f"Error fetching sources: {e}")
    # Default fallback sources
    return [
        {"name": "Product Hunt", "url": "api", "method": "api", "section": "section_1"},
        {"name": "Hacker News", "url": "api", "method": "api", "section": "section_1"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "method": "rss", "section": "section_2"},
        {"name": "VentureBeat", "url": "https://venturebeat.com/category/ai/feed/", "method": "rss", "section": "section_2"},
        {"name": "YourStory", "url": "https://yourstory.com/feed", "method": "rss", "section": "section_3"},
        {"name": "Inc42", "url": "https://inc42.com/feed/", "method": "rss", "section": "section_3"},
        {"name": "TechCircle", "url": "https://www.techcircle.in/category/startups/feed", "method": "rss", "section": "section_3"}
    ]

def update_source_url(name, new_url):
    """Updates source url in Data Store."""
    try:
        app = get_catalyst_app()
        if not app:
            return
        query = f"SELECT ROWID FROM Sources WHERE name = '{name}'"
        result = app.zcql().execute_query(query)
        if result and len(result) > 0:
            row = result[0].get('Sources', result[0])
            row_id = row.get('ROWID')
            app.datastore().table('Sources').update_row({
                'ROWID': row_id,
                'url': new_url
            })
            print(f"Updated source {name} with new URL: {new_url}")
    except Exception as e:
        print(f"Error updating source URL: {e}")

def is_item_sent_recently(url):
    """Checks if an item was already sent."""
    try:
        app = get_catalyst_app()
        if not app:
            return False
        safe_url = url.replace("'", "''")
        query = f"SELECT ROWID FROM SentItems WHERE url = '{safe_url}'"
        result = app.zcql().execute_query(query)
        return bool(result and len(result) > 0)
    except Exception as e:
        print(f"Error checking if item sent: {e}")
        return False

def log_sent_items(items):
    """Logs sent items in SentItems Data Store table."""
    try:
        app = get_catalyst_app()
        if not app:
            return
        sent_table = app.datastore().table('SentItems')
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        for item in items:
            url = item.get('url', '')
            title = item.get('title', '')
            try:
                sent_table.insert_row({
                    'url': url,
                    'title': title,
                    'sent_at': now_iso
                })
            except Exception as insert_err:
                print(f"Notice inserting sent item: {insert_err}")
        print(f"Logged {len(items)} sent items in Data Store.")
    except Exception as e:
        print(f"Error logging sent items: {e}")

def prune_sent_items():
    """Prunes items older than 14 days from SentItems."""
    try:
        app = get_catalyst_app()
        if not app:
            return
        cutoff_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14)).isoformat()
        query = f"SELECT ROWID FROM SentItems WHERE sent_at < '{cutoff_date}'"
        results = app.zcql().execute_query(query)
        if results:
            sent_table = app.datastore().table('SentItems')
            for r in results:
                row = r.get('SentItems', r)
                row_id = row.get('ROWID')
                if row_id:
                    sent_table.delete_row(row_id)
            print(f"Pruned {len(results)} old items from SentItems.")
    except Exception as e:
        print(f"Notice during prune_sent_items: {e}")
