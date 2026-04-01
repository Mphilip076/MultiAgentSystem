import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
from google import genai

st.set_page_config(page_title="Competitive Intelligence Report", layout="wide")
st.title("Competitive Intelligence Report: Pharma Advancements")

# Setting the Gemini API key
os.environ['GOOGLE_API_KEY'] = "AIzaSyDSH3g7x4Fj-HCv2dj_c3tdFEARAvAdlKE"
client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])

def read_input():
    # Targeted Pharma URLs for AbbVie's competitive intelligence
    links = {
        "1": ["AbbVie", "https://news.abbvie.com/news/press-releases/"],
        "2": ["Merck", "https://www.merck.com/news/"],
        "3": ["Pfizer", "https://www.pfizer.com/news/press-releases/"],
        "4": ["National Institutes of Health", "https://www.cancer.gov/news-events/press-releases/2025"],
        "5": ["Pub MD", "https://pubmed.ncbi.nlm.nih.gov/?term=Ovarian+Cancer"],
        "6": ["FDA", "https://www.fda.gov/search?s=Ovarian+Cancer"]
    }
    
    st.sidebar.header("Data Sources")
    for company, url in links.values():
        st.sidebar.write(f"**{company}**: [Press Releases]({url})")

    for i in range(1, 6):
        company_name = links[str(i)][0]
        url = links[str(i)][1]
        
        with st.status(f"Scraping {company_name} news...", expanded=False) as status:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            data = soup.text
            
            # Extract links to specific press releases if needed
            all_links = soup.find_all('a', href=True)
            link_list = "\n".join([a['href'] for a in all_links if len(a['href']) > 15]) 
            
            # Refined query for continuous competitive intelligence monitoring
            query = (
                f"Analyze the following data from {company_name} for RECENT significant product advancements, "
                "trial results, or strategic news. \n"
                "CRITICAL: If no significant new advancements or news are found in the provided data, "
                "return ONLY the text 'NO_RECENT_UPDATES'.\n\n"
                "Otherwise, provide a concise bulleted summary of the findings.\n"
                f"RAW DATA: {data[:5000]} \n"
                f"OTHER LINKS FOUND: {link_list[:1000]}"
            )
            
            status.update(label=f"Analyzing {company_name} insights with Gemini...", state="running")
            llm_function(company_name, query)
            status.update(label=f"Done for {company_name}!", state="complete")

def llm_function(company_name, query):
    try:
        response = client.models.generate_content(model="gemini-3-flash-preview", contents=query)
        result = response.text.strip()
        
        # Only display if there's actual news to report
        if result != "NO_RECENT_UPDATES":
            st.subheader(f"New Insights for {company_name}")
            st.markdown(result)
        else:
            # We skip displaying anything to keep the dashboard clean
            pass
    except Exception as e:
        # In a production scraper, we might want to log this vs show error
        st.error(f"Error processing {company_name}: {e}")

if __name__ == "__main__":
    if st.button("Generate Intelligence Report"):
        read_input()
    else:
        st.info("Click the button above to start pulling competitor intel.")
