import streamlit as st
import requests
import datetime
from bs4 import BeautifulSoup
from groq import Groq
import concurrent.futures
import json
import os
import hashlib
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configuration variables
now = datetime.datetime.now()
current_year = now.year
current_month = "March" #now.strftime("%B")

GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DB_FILE = "processed_news.json"

# LIST OF MODELS TO USE (IN CASE THE CURRENT ONE RUNS OUT OF TOKENS)
# qwen/qwen3-32b
# llama-3.1-8b-instant
# llama-3.3-70b-versatile
# meta-llama/llama-4-scout-17b-16e-instruct
# meta-llama/llama-prompt-guard-2-86m
# openai/gpt-oss-120b

# Streamlit UI (delete later)
st.set_page_config(page_title="AI Competitive Intelligence Scraper", layout="wide")
st.title(f"Test Scraper For {current_month} {current_year}")

# -------------------- DATABASE HELPERS --------------------#

def load_db():
    """
    Loads the database of processed news from the local JSON file.
    
    Returns:
        dict: A dictionary containing previously processed news items, indexed by their unique hash.
    """

    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_db(db):
    """
    Saves the updated news database to a JSON file.
    
    Args:
        db (dict): The current state of the news database to be saved.
    """

    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

def get_hash(text):
    """
    Generates a unique MD5 hash for a given string. 
    Used to identify and deduplicate news items based on their title and source.
    
    Args:
        text (str): The text to be hashed.
        
    Returns:
        str: The hexadecimal MD5 hash of the input text.
    """

    return hashlib.md5(text.encode()).hexdigest()
# -----------------------------------------------------------#

# -------------------- SCRAPING LOGIC --------------------#
def scrape_url(company_name, url):
    """
    Fetches the content of a given URL and extracts potential news text.
    
    Args:
        company_name (str): The name of the company being scraped.
        url (str): The target URL to fetch news from.
    
    Returns:
        tuple: (company_name, text_content, error_message)
               - text_content is a string of extracted links and headers.
               - error_message is None if successful, or a string describing the error.
    """
    
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Focus on capturing blocks that likely contain news entries
        # Returns a rough text dump that the 1B model will clean into a JSON list
        text_content = ""
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'a']):
            text_str = tag.get_text(strip=True)
            if len(text_str) > 20:
                link = tag.get('href', '')
                if link.startswith('/'): # Handle relative links
                    from urllib.parse import urljoin
                    link = urljoin(url, link)
                text_content += f"ITEM: {text_str} | LINK: {link}\n"
        
        return company_name, text_content[:10000], None
    except Exception as e:
        return company_name, None, str(e)
# -----------------------------------------------------------#

# --------------------- AI DATA CLEANING---------------------#
def clean_data(company_name, raw_data):
    """
    Uses an LLM to filter and format raw scraped text into a clean list of relevant news.
    
    Args:
        company_name (str): The name of the company the data belongs to.
        raw_data (str): The raw text extracted from the company's news page.
        
    Returns:
        list: A list of dictionaries, each containing 'title', 'date', and 'link' of a news item.
    """

    prompt = f"""
            ### MISSION: 
            Extract a CLEAN JSON list of specific Pharma Industry news from {company_name} that is STRATEGICALLY RELEVANT to AbbVie.

            ### STRATEGIC AREAS OF INTEREST:
            - **Immunology:** RA, Crohn's, Colitis, Psoriasis (Competitors to Humira, Skyrizi, Rinvoq).
            - **Oncology:** Hemato-oncology (CLL, AML) and solid tumors (Competitors to Venclexta, Imbruvica).
            - **Neuroscience:** Parkinson's, Migraine, Depression (Competitors to Vraylar, Qulipta).
            - **Aesthetics:** Medical aesthetics, toxins, fillers (Competitors to Botox).

            ### DISCARD / IGNORE:
            - Generic corporate HR news, social media links, press kits, media libraries.
            - "About us" or "Email alerts" buttons.
            - Financial reports unless they mention specific product performance or M&A.

            ### KEEP ONLY:
            - Clinical trial results (Phase 1-3), FDA/EMA approvals, R&D breakthroughs, and strategic competitor moves (M&A, licensing) in the focus areas above.
            - **IMPORTANT:** ONLY include news from the TARGET MONTH ({current_month} {current_year}). If an article is from a different time period, DISCARD it.

            ### GROUNDING RULES:
            - **NO SYNTHESIS:** Do NOT combine fragments to create a new title.
            - **NO URL GUESSING:** If the link is not clearly next to the headline in the RAW DATA, do NOT include the item.
            - **NO HALLUCINATIONS:** If the exact news title or link is not in the RAW DATA, do NOT include it.
            - **DATE ACCURACY:** If a year is not explicitly {current_year}, assume it is NOT {current_year} and discard it. 
            - **EMPTY RESULTS:** If no news items meet all criteria (AbbVie relevance + {current_year} date), return an EMPTY list: {{"items": []}}. 
            - Do not make up links. Links must come directly from the LINK: markers.

            ### FORMAT: 
            JSON LIST ONLY: {{"items": [{{"title": "Full Headline", "date": "Date found", "link": "Direct URL"}}]}}

            ### RAW DATA:
            {raw_data}
            """
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": f"You are a verbatim data extraction tool. You only output valid JSON. You must NEVER fabricate data. Your task is to extract ONLY what is explicitly written in the raw text for the month of {current_month} {current_year}. Return an empty list: {{'items': []}} if nothing is found."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        res_text = completion.choices[0].message.content
        data = json.loads(res_text)
        return data.get("items", [])
    except Exception as e:
        st.error(f"Error during AI extraction: {e}")
        return []
# -----------------------------------------------------------#

# ---------------------- START SCRAPER ----------------------#
def start_scraper():
    """
    Scrapes company websites, cleans news data using an LLM, and identifies new items.
    
    Returns:
        list: A list of dictionaries representing the newly found news items (news_queue).
    """

    links = {
        "1": ["AbbVie", "https://news.abbvie.com/news/press-releases/"],
        "2": ["Merck", "https://www.merck.com/media/news/"],
        "3": ["Pfizer", "https://www.pfizer.com/news/press-releases/"],
        "4": ["National Cancer Institute", f"https://www.cancer.gov/news-events"],
        "5": ["FDA", "https://www.fda.gov/search?s=Ovarian+Cancer"],
    }

    db = load_db()
    news_queue = []

    with st.status("Gathering news candidates...", expanded=True) as status:
        # Concurrent Scraping
        scraped_results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(scrape_url, name, url) for name, url in links.values()]
            for future in concurrent.futures.as_completed(futures):
                name, data, err = future.result()
                if not err:
                    scraped_results.append((name, data))
                    st.write(f"Fetched data from **{name}**")
                else:
                    st.error(f"Error on {name}: {err}")

        # Extraction & Deduplication
        status.update(label="Cleaning data and checking for new items...", state="running")
        for name, raw_data in scraped_results:
            items = clean_data(name, raw_data)
            new_for_this_company = 0
            
            for item in items:
                title = item.get("title", "")
                if not title: continue
                
                item_id = get_hash(f"{name}-{title}")
                
                if item_id not in db:
                    item['source_name'] = name
                    news_queue.append(item)
                    db[item_id] = {"title": title, "date": item.get("date", ""), "scraped_at": str(os.times())}
                    new_for_this_company += 1
            
            if new_for_this_company > 0:
                st.success(f"Found {new_for_this_company} new items for **{name}**")
            else:
                st.write(f"Nothing new for {name}.")

        save_db(db)
        status.update(label=f"Done! {len(news_queue)} items ready found.", state="complete")

    # Display queue of news (later we can send this to the AI agents, so it would be a return item)
    if news_queue:
        st.subheader("Note: The JSON contains links to the articles, but probably an AI agent will need to research more.")
        st.json(news_queue)
    else:
        st.info("The News Queue is empty (No new items found since the last run).")
    
    # Note: Later on, we will send this into the AI Agents. So it would be a return item.
    return news_queue
# -----------------------------------------------------------#

# -------------------- MAIN ------------------#
if __name__ == "__main__":
    if st.button("Scan for New Competitor Data"):
        start_scraper()
    else:
        st.info("Click to scan. The system will only show items it hasn't processed before.")