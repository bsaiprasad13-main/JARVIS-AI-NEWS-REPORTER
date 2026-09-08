import os
import sys
import requests
import datetime
import urllib.parse
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

# Try local dotenv if available, else use cloud os.environ directly
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PRODUCT_HUNT_TOKEN = os.environ.get("PRODUCT_HUNT_DEVELOPER_TOKEN")

def get_utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

def is_within_window(item_time_utc, last_run_utc):
    """Checks if item is newer than last_run and within 72 hours max."""
    now = get_utc_now()
    if item_time_utc < (now - datetime.timedelta(hours=72)):
        return False
    if last_run_utc and item_time_utc <= last_run_utc:
        return False
    return True

def fetch_product_hunt(last_run_utc):
    if not PRODUCT_HUNT_TOKEN:
        print("Warning: PRODUCT_HUNT_DEVELOPER_TOKEN not set.")
        return [], False

    url = "https://api.producthunt.com/v2/api/graphql"
    headers = {
        "Authorization": f"Bearer {PRODUCT_HUNT_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    query = """
    {
      posts(first: 30, order: RANKING) {
        edges {
          node {
            id
            name
            tagline
            url
            createdAt
            votesCount
            topics {
              edges {
                node {
                  name
                }
              }
            }
          }
        }
      }
    }
    """
    
    items = []
    success = False
    try:
        response = requests.post(url, headers=headers, json={"query": query}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            posts = data.get("data", {}).get("posts", {}).get("edges", [])
            for post in posts:
                node = post["node"]
                created_at = datetime.datetime.fromisoformat(node["createdAt"].replace('Z', '+00:00'))
                
                # Check if relevant (AI or Productivity)
                topics = [t["node"]["name"].lower() for t in node.get("topics", {}).get("edges", [])]
                is_ai_or_pm = any(keyword in ' '.join(topics) for keyword in ['ai', 'artificial intelligence', 'productivity', 'developer tools'])
                
                if is_ai_or_pm and is_within_window(created_at, last_run_utc):
                    items.append({
                        "id": node["id"],
                        "title": f"{node['name']} - {node['tagline']}",
                        "url": node["url"],
                        "source": "Product Hunt",
                        "section": "section_1",
                        "signal": node["votesCount"]
                    })
            success = True
        else:
            print(f"Product Hunt API failed: {response.status_code}")
    except Exception as e:
        print(f"Error fetching Product Hunt: {e}")
        
    return items, success

def fetch_hacker_news(last_run_utc):
    items = []
    success = False
    try:
        now_ts = int(get_utc_now().timestamp())
        three_days_ago_ts = now_ts - (72 * 3600)
        url = f"https://hn.algolia.com/api/v1/search_by_date?tags=show_hn&numericFilters=created_at_i>{three_days_ago_ts}&hitsPerPage=50"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            hits = response.json().get("hits", [])
            for hit in hits:
                created_at = datetime.datetime.fromisoformat(hit["created_at"].replace('Z', '+00:00'))
                if is_within_window(created_at, last_run_utc):
                    points = hit.get("points", 0)
                    if points > 5:
                        items.append({
                            "id": hit["objectID"],
                            "title": hit.get("title", ""),
                            "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit['objectID']}",
                            "source": "Hacker News",
                            "section": "section_1",
                            "signal": points
                        })
            success = True
        else:
             print(f"Hacker News API failed: {response.status_code}")
    except Exception as e:
        print(f"Error fetching Hacker News: {e}")
        
    return items, success

def parse_xml_feed(xml_text):
    """
    Standard XML parser for RSS and Atom feeds using built-in xml.etree.ElementTree.
    100% pure standard library - zero external dependencies!
    """
    entries = []
    root = ET.fromstring(xml_text)
    
    # Handle RSS 2.0 (<rss><channel><item>...)
    channel = root.find('channel')
    if channel is not None:
        for item in channel.findall('item'):
            title = item.findtext('title') or ''
            link = item.findtext('link') or ''
            guid = item.findtext('guid') or link
            pub_date_str = item.findtext('pubDate') or ''
            
            dt = None
            if pub_date_str:
                try:
                    dt = parsedate_to_datetime(pub_date_str)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=datetime.timezone.utc)
                except Exception:
                    pass
                    
            entries.append({
                'title': title.strip(),
                'link': link.strip(),
                'id': guid.strip(),
                'published': dt
            })
        return entries
        
    # Handle Atom (<feed><entry>...)
    # Remove XML namespaces for easier matching
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]
            
    for entry in root.findall('entry'):
        title = entry.findtext('title') or ''
        link_elem = entry.find('link')
        link = link_elem.attrib.get('href', '') if link_elem is not None else ''
        id_str = entry.findtext('id') or link
        published_str = entry.findtext('published') or entry.findtext('updated') or ''
        
        dt = None
        if published_str:
            try:
                dt = datetime.datetime.fromisoformat(published_str.replace('Z', '+00:00'))
            except Exception:
                pass
                
        entries.append({
            'title': title.strip(),
            'link': link.strip(),
            'id': id_str.strip(),
            'published': dt
        })
        
    return entries

def fetch_rss(source_name, feed_url, section, last_run_utc):
    items = []
    success = False
    new_url = feed_url
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 JarvisNewsBot/1.0'
    }
    
    urls_to_try = [feed_url]
    base_url = urllib.parse.urljoin(feed_url, '/')
    urls_to_try.extend([
        urllib.parse.urljoin(base_url, '/feed'),
        urllib.parse.urljoin(base_url, '/rss'),
        urllib.parse.urljoin(base_url, '/feed/'),
        urllib.parse.urljoin(base_url, '/rss.xml')
    ])
    urls_to_try = list(dict.fromkeys(urls_to_try))
    
    for url in urls_to_try:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200 and resp.text:
                entries = parse_xml_feed(resp.text)
                if entries:
                    new_url = url
                    for entry in entries:
                        dt = entry.get('published')
                        if dt and is_within_window(dt, last_run_utc):
                            items.append({
                                "id": entry.get('id') or entry.get('link'),
                                "title": entry.get('title'),
                                "url": entry.get('link'),
                                "source": source_name,
                                "section": section,
                                "signal": None
                            })
                    success = True
                    break
        except Exception as e:
            continue
            
    if not success:
        print(f"Failed to fetch RSS for {source_name}")
        
    return items, success, new_url

def fetch_all_data(sources, last_run_utc):
    all_items = []
    failed_sources = []
    updated_urls = {}
    
    for source in sources:
        name = source["name"]
        method = source["method"]
        url = source["url"]
        section = source["section"]
        
        items = []
        success = False
        
        if method == "api":
            if name == "Product Hunt":
                items, success = fetch_product_hunt(last_run_utc)
            elif name == "Hacker News":
                items, success = fetch_hacker_news(last_run_utc)
        elif method == "rss":
            items, success, new_url = fetch_rss(name, url, section, last_run_utc)
            if success and new_url != url:
                updated_urls[name] = new_url
                
        if success:
            all_items.extend(items)
        else:
            failed_sources.append(name)
            
    return all_items, failed_sources, updated_urls
