import streamlit as st
import requests
from bs4 import BeautifulSoup
from ollama import chat

st.set_page_config(page_title="Competitive Intelligence Report", layout="wide")
st.title("Competitive Intelligence Report: Pharma Advancements")

OLLAMA_MODEL = "llama3.2"

def read_input():
    links = {
        "1": ["AbbVie", "https://news.abbvie.com/news/press-releases/"],
        "2": ["Merck", "https://www.merck.com/media/news/"],
        "3": ["Pfizer", "https://www.pfizer.com/news/press-releases/"],
        "4": ["National Cancer Institute", "https://www.cancer.gov/news-events/press-releases/2025"],
        "5": ["PubMed", "https://pubmed.ncbi.nlm.nih.gov/?term=Ovarian+Cancer"],
        "6": ["FDA", "https://www.fda.gov/search?s=Ovarian+Cancer"],
    }

    st.sidebar.header("Data Sources")
    for company, url in links.values():
        st.sidebar.write(f"**{company}**: [Source]({url})")

    for i in range(1, 7):
        company_name, url = links[str(i)]

        with st.status(f"Scraping {company_name}...", expanded=False) as status:
            try:
                r = requests.get(
                    url,
                    timeout=15,
                    headers={
                        "User-Agent": "Mozilla/5.0"
                    }
                )
                r.raise_for_status()

                soup = BeautifulSoup(r.text, "html.parser")
                data = soup.get_text(separator=" ", strip=True)

                all_links = soup.find_all("a", href=True)
                link_list = "\n".join(
                    a["href"] for a in all_links if len(a["href"]) > 15
                )

                query = f"""
Analyze the following data from {company_name} for RECENT significant product advancements,
trial results, approvals, safety updates, or strategic medical news.

CRITICAL RULES:
- If no clearly significant recent updates are found, return ONLY:
NO_RECENT_UPDATES
- Otherwise, provide a concise bulleted summary.
- Focus on ovarian cancer, oncology, drug development, clinical progress, and major company/regulatory developments when present.
- Do not invent information. Only use the provided text.

RAW DATA:
{data[:7000]}

OTHER LINKS FOUND:
{link_list[:1500]}
"""

                status.update(label=f"Analyzing {company_name} with Ollama...", state="running")
                llm_function(company_name, query)
                status.update(label=f"Done for {company_name}", state="complete")

            except requests.RequestException as e:
                status.update(label=f"Request failed for {company_name}", state="error")
                st.error(f"Error scraping {company_name}: {e}")

def llm_function(company_name, query):
    try:
        response = chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a competitive intelligence analyst for pharma and medical progress. "
                        "Be concise, accurate, and conservative. "
                    #    "If no meaningful recent update is present in the supplied text, output exactly NO_RECENT_UPDATES."
                    ),
                },
                {
                    "role": "user",
                    "content": query,
                },
            ],
        )

        result = response["message"]["content"].strip()

        if result != "NO_RECENT_UPDATES":
            st.subheader(f"New Insights for {company_name}")
            st.markdown(result)

    except Exception as e:
        st.error(f"Error processing {company_name}: {e}")

if __name__ == "__main__":
    st.caption(f"Using local Ollama model: {OLLAMA_MODEL}")
    if st.button("Generate Intelligence Report"):
        read_input()
    else:
        st.info("Click the button above to start pulling competitor intel.")