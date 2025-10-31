#!/usr/bin/env python3
# Instagram Lead Generator with Multi-API Key Rotation
# Allows using multiple Google API keys to bypass daily limits

import os
import time
import logging
import re
from urllib.parse import urlparse
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

try:
    import instaloader
except Exception:
    instaloader = None

logging.basicConfig(filename='logs/run.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Support multiple API keys (comma-separated in .env)
API_KEYS = os.getenv("GOOGLE_API_KEYS", os.getenv("GOOGLE_API_KEY", "")).split(',')
CX_IDS = os.getenv("GOOGLE_CX_IDS", os.getenv("GOOGLE_CX", "")).split(',')
API_KEYS = [k.strip() for k in API_KEYS if k.strip()]
CX_IDS = [c.strip() for c in CX_IDS if c.strip()]

INSTALOADER_SESSION_FILE = os.getenv("INSTALOADER_SESSION_FILE") or None
MAX_FOLLOWERS = 100000

# Track queries per API key
current_key_index = 0
queries_per_key = {}

def get_current_api_credentials():
    """Rotate through available API keys"""
    global current_key_index
    
    if not API_KEYS or not CX_IDS:
        return None, None
    
    # Rotate if current key has been used too much (95 queries)
    if queries_per_key.get(current_key_index, 0) >= 95:
        current_key_index = (current_key_index + 1) % len(API_KEYS)
        logging.info(f"Rotating to API key #{current_key_index + 1}")
        print(f"🔄 Switching to API key #{current_key_index + 1}")
    
    api_key = API_KEYS[current_key_index]
    cx = CX_IDS[min(current_key_index, len(CX_IDS) - 1)]  # Use last CX if fewer CX than keys
    
    return api_key, cx

def extract_username(url):
    try:
        p = urlparse(url)
        path = p.path.strip('/')
        if path and not path.startswith(('p/', 'reel/', 'tv/')):
            username = path.split('/')[0]
            username = re.sub(r'[^0-9A-Za-z._-]', '', username)
            return username.lower()
    except Exception:
        return None
    return None

def google_search(query, start=1):
    global current_key_index, queries_per_key
    
    api_key, cx = get_current_api_credentials()
    if not api_key or not cx:
        logging.error("No valid API credentials available")
        return []
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"q": query, "key": api_key, "cx": cx, "start": start}
    
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        
        # Track successful query
        queries_per_key[current_key_index] = queries_per_key.get(current_key_index, 0) + 1
        
        return data.get("items", [])
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logging.warning(f"API key #{current_key_index + 1} hit rate limit")
            # Mark this key as exhausted
            queries_per_key[current_key_index] = 95
            # Try with next key
            current_key_index = (current_key_index + 1) % len(API_KEYS)
            if queries_per_key.get(current_key_index, 0) < 95:
                return google_search(query, start)
        logging.error(f"Google API error for query={query} start={start}: {e}")
        return []
    except Exception as e:
        logging.error(f"Google API error for query={query} start={start}: {e}")
        return []

def collect_instagram_links(profession, location="India", max_results=50):
    found = []
    
    search_variations = [
        f'site:instagram.com "{profession}" "{location}"',
        f'site:instagram.com "{profession}" bio "{location}"',
    ]
    
    for q_base in search_variations:
        logging.info(f"Searching Google for: {q_base}")
        for start in range(1, max_results + 1, 10):
            items = google_search(q_base, start)
            if not items:
                break
            
            for it in items:
                link = it.get("link") or ""
                if "instagram.com" in link and not any(x in link for x in ["/p/", "/reel/", "/tv/", "/stories/"]):
                    username = extract_username(link)
                    if username and len(username) > 2:
                        found.append({
                            "name": it.get("title", "").replace(" | Instagram", "").strip(),
                            "link": link,
                            "snippet": it.get("snippet", ""),
                            "username": username,
                            "profession": profession
                        })
            time.sleep(0.5)
    
    unique = {x["username"]: x for x in found}
    return list(unique.values())

def enrich_with_instaloader(entries, use_instaloader=True):
    if not use_instaloader or instaloader is None:
        logging.info("Instaloader not available or disabled")
        return entries

    L = instaloader.Instaloader(dirname_pattern=None, filename_pattern=None, 
                                download_pictures=False, download_videos=False,
                                download_geotags=False, download_comments=False)
    
    if INSTALOADER_SESSION_FILE and os.path.exists(INSTALOADER_SESSION_FILE):
        try:
            username = INSTALOADER_SESSION_FILE.split('session-')[-1]
            L.load_session_from_file(username, filename=INSTALOADER_SESSION_FILE)
            logging.info("Loaded instaloader session file.")
        except Exception as e:
            logging.warning(f"Could not load session file: {e}")

    enriched = []
    for e in entries:
        username = e["username"]
        profile_data = {
            "username": username,
            "link": e["link"],
            "name": e.get("name",""),
            "profession": e.get("profession",""),
            "snippet": e.get("snippet",""),
            "followers": None,
            "biography": None,
            "email": None,
            "external_url": None
        }
        try:
            profile = instaloader.Profile.from_username(L.context, username)
            profile_data["followers"] = profile.followers
            profile_data["biography"] = profile.biography
            profile_data["external_url"] = getattr(profile, 'external_url', None)
            bio = profile.biography or ""
            m = re.search(r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})', bio)
            if m:
                profile_data["email"] = m.group(1)
        except Exception as ex:
            logging.warning(f"Instaloader failed for {username}: {ex}")
        enriched.append(profile_data)
        time.sleep(1)
    return enriched

def filter_entries(entries):
    filtered = []
    for e in entries:
        followers = e.get("followers")
        external = e.get("external_url")
        
        if followers is not None:
            try:
                if int(followers) >= MAX_FOLLOWERS:
                    logging.info(f"Filtered out {e['username']}: {followers} followers")
                    continue
            except Exception:
                pass
        
        if external and str(external).strip() and 'http' in str(external):
            logging.info(f"Filtered out {e['username']}: has external URL")
            continue
            
        filtered.append(e)
    return filtered

def save_csv(entries, path="data/instagram_profiles.csv"):
    keys = ["username","name","profession","link","followers","biography","email","external_url","snippet"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df = pd.DataFrame(entries)
    for k in keys:
        if k not in df.columns:
            df[k] = None
    df = df[keys]
    df.to_csv(path, index=False, encoding="utf-8")
    logging.info(f"Saved {len(df)} rows to {path}")
    print(f"✅ Saved {len(df)} profiles to {path}")

def main():
    if not API_KEYS or not CX_IDS:
        print("⚠️ No API credentials found!")
        print("Please set GOOGLE_API_KEYS and GOOGLE_CX_IDS in .env")
        return

    print(f"\n{'='*60}")
    print(f"🚀 MULTI-KEY INSTAGRAM LEAD GENERATOR")
    print(f"Available API Keys: {len(API_KEYS)}")
    print(f"Estimated Capacity: {len(API_KEYS) * 95} queries")
    print(f"{'='*60}\n")

    profession_keywords = {
        "Doctor": ["Doctor", "Physician"],
        "Lawyer": ["Lawyer", "Advocate"],
        "E-commerce": ["E-commerce", "Online Store"]
    }
    
    locations = ["Mumbai", "Delhi"]
    all_found = []
    
    for profession_group, keywords in profession_keywords.items():
        print(f"\n{'='*60}")
        print(f"Searching for profession: {profession_group}")
        print(f"{'='*60}")
        
        for keyword in keywords:
            for location in locations:
                total_queries = sum(queries_per_key.values())
                print(f"\n🔍 Searching: {keyword} in {location} (Total queries: {total_queries})")
                found = collect_instagram_links(keyword, location=location, max_results=50)
                print(f"  -> Found {len(found)} raw profiles")
                
                if found:
                    enriched = enrich_with_instaloader(found, use_instaloader=True)
                    print(f"  -> Enriched {len(enriched)} profiles")
                    filtered = filter_entries(enriched)
                    print(f"  -> {len(filtered)} profiles passed filters")
                    all_found.extend(filtered)
                    
                time.sleep(1)
    
    unique = {x["username"]: x for x in all_found}
    final = list(unique.values())
    
    total_queries = sum(queries_per_key.values())
    print(f"\n{'='*60}")
    print(f"✅ TOTAL PROFILES FOUND: {len(final)}")
    print(f"📊 Total API Queries Used: {total_queries}")
    for idx, count in queries_per_key.items():
        print(f"   API Key #{idx + 1}: {count} queries")
    print(f"{'='*60}")
    
    save_csv(final)
    print(f"\n💾 Results saved to: data/instagram_profiles.csv")

if __name__ == '__main__':
    main()
