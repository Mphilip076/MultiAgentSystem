import os
import sys
import json
import hashlib
import requests
import datetime
import concurrent.futures
from bs4 import BeautifulSoup
from groq import Groq
from dotenv import load_dotenv

# SETUP & PATHS
load_dotenv()

# Add System/src to path to import the Crew
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "System", "src"))

try:
    from system.crew import System
except ImportError as e:
    print(f"Error: Could not import 'System' from 'system.crew'. {e}")
    sys.exit(1)

# Scraper Configuration
GROQ_MODEL = "qwen/qwen3-32b"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
DB_FILE = "processed_news.json"
now = datetime.datetime.now()
current_year = now.year
current_month = "March" #now.strftime("%B")

# -------------------- DATABASE HELPERS --------------------#
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

def get_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

# -------------------- SCRAPING LOGIC ------------------#
def scrape_url(company_name, url):
    """Fetches raw content from company news pages."""
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        
        text_content = ""
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'a']):
            text_str = tag.get_text(strip=True)
            if len(text_str) > 20:
                link = tag.get('href', '')
                if link.startswith('/'):
                    from urllib.parse import urljoin
                    link = urljoin(url, link)
                text_content += f"ITEM: {text_str} | LINK: {link}\n"
        
        return company_name, text_content[:10000], None
    except Exception as e:
        return company_name, None, str(e)

def clean_data_with_ai(company_name, raw_data):
    """Uses LLM to filter for strategic news items only."""
    prompt = f"""
            ### MISSION: 
            Extract a CLEAN JSON list of high-value, strategic Industry news from {company_name} relevant to AbbVie.
            
            ### STRATEGIC AREAS OF INTEREST:
            - Immunology, Oncology, Neuroscience, Aesthetics.

            ### FORMAT: 
            JSON LIST ONLY: {{"items": [{{"title": "Full Headline", "link": "Direct URL", "date": "Date found", "snippet" : "Short summary of the news" }}]}}

            ### RAW DATA:
            {raw_data}
            """
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": f"You are a data extraction tool. Extract ONLY strategic news for {current_month} {current_year}. Return {{'items': []}} if nothing found."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        data = json.loads(completion.choices[0].message.content)
        return data.get("items", [])
    except Exception:
        return []

# -------------------- INTEGRATED EXECUTION ------------------#
def run_system():
    print(f"Starting Integrated Scraper & Crew System [{current_month} {current_year}]")
    
    links = {
        "1": ["AbbVie", "https://news.abbvie.com/news/press-releases/"],
        "2": ["Merck", "https://www.merck.com/media/news/"],
        "3": ["Pfizer", "https://www.pfizer.com/news/press-releases/"],
        "4": ["National Cancer Institute", f"https://www.cancer.gov/news-events"],
        "5": ["FDA", "https://www.fda.gov/search?s=Ovarian+Cancer"],
    }

    db = load_db()
    news_queue = []

    # 1. Scrape URLs concurrently
    print(f"Scraping {len(links)} sources...")
    scraped_results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(scrape_url, name, url) for name, url in links.values()]
        for future in concurrent.futures.as_completed(futures):
            name, data, err = future.result()
            if not err:
                scraped_results.append((name, data))
                print(f"   Fetched: {name}")

    # 2. Clean and Check for New Items
    print(f"\nFiltering for strategic news using AI ({GROQ_MODEL})...")
    for name, raw_data in scraped_results:
        items = clean_data_with_ai(name, raw_data)
        for item in items:
            title = item.get("title", "")
            if not title: continue
            
            item_id = get_hash(f"{name}-{title}")
            if item_id not in db:
                item['source_name'] = name
                news_queue.append(item)
                db[item_id] = {"title": title, "date": item.get("date", ""), "processed_at": str(datetime.datetime.now())}
                print(f"   NEW ITEM FOUND: {title}")

    save_db(db)

    # 3. Trigger the Crew for each new item
    if not news_queue:
        print("\nNo new strategic news found. System on standby.")
        return

    print(f"\nFound {len(news_queue)} new items. Initializing CrewAI Agents...")
    
    for news in news_queue[:1]:
        print(f"\n" + "-"*50)
        print(f"ANALYZING: {news['title']}")
        print(f"SOURCE: {news['source_name']}")
        
        inputs = {
            'topic': 'Biopharmaceutical Market Dynamics and Competitor Strategy',
            'news_item': f"Source: {news['source_name']}. Title: {news['title']}. Date: {news.get('date', 'N/A')}. URL: {news.get('link', 'N/A')}",
            'template': "Executive Strategic Impact Brief",
            'company_goals': (
                "1. Protect market share in core Immunology and Oncology portfolios. "
                "2. Monitor competitor R&D breakthroughs. "
                "3. Identify M&A activity or strategic pivots. "
                "4. Assess risks to patent estates."
            )
        }

        try:
            result = System().crew().kickoff(inputs=inputs)
            print(f"\nCREW REPORT FOR: {news['title']}\n")
            print(result)
        except Exception as e:
            print(f"Crew analysis failed for this item: {e}")

if __name__ == "__main__":
    
    run_system()
