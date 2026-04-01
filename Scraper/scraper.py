import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
from google import genai

st.title("Proposal Calls") # Title for the page

os.environ['GOOGLE_API_KEY'] = "AIzaSyDSH3g7x4Fj-HCv2dj_c3tdFEARAvAdlKE"
client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])

def read_input():
    # dictionary of all the links to be webscraped.
    # You can add more if you want to
    links = {
        "1":["DST","https://dst.gov.in/call-for-proposals"],
        "2":["BIRAC","https://birac.nic.in/cfp.php"]
    }
    for i in range(1,3):
        url = links[str(i)][1] # Get URL of each organization
        r = requests.get(url) # Request for data
        soup = BeautifulSoup(r.text, 'html.parser') # Parse the HTML elements
        data = soup.text # Get raw data in string format
        link = soup.find_all('a', href=True) # Get list of all links on the site in html formet
        l = ""
        for a in link:
            l = l +"\n"+ a['href'][1:] # Get the actual links
        # Create a query
        query = data + "name of organization is"+links[str(i)][0]+ "Jumbled links of calls for proposals:"+l+"\n Create a table with the following columns: Call for proposals or joint call for proposals along with respective link, opening date, closing date and the name of the organization."
        llm_function(query)

def llm_function(query):
    # Using the modern gemini-1.5-flash model with the new SDK syntax
    response = client.models.generate_content(model="gemini-3-flash-preview", contents=query) # Generate response
    st.markdown(response.text) # Print it out using streamlit

if __name__ == "__main__":
    read_input()
