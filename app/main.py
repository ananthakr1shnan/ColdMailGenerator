import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text

def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold Mail Generator")

    col1, col2 = st.columns([2, 1])
    with col1:
        url_input = st.text_input("Enter a URL:", value="https://jobs.nike.com/job/R-37921", placeholder="e.g., https://example.com/job")
    with col2:
        submit_button = st.button("Submit")

    if submit_button:
        with st.spinner("Loading..."):
            try:
                loader = WebBaseLoader([url_input])
                data = clean_text(loader.load().pop().page_content)
                portfolio.load_portfolio()
                jobs = llm.extract_jobs(data)

                for job in jobs:
                    title = job.get('title')
                    if title:  # Only display if there's a title
                        st.subheader("Extracted Jobs:")
                        st.write(f"- {title}")


            
                for job in jobs:
                    skills = job.get('skills', [])
                    links = portfolio.query_links(skills)
                    email = llm.write_mail(job, links)
                    st.subheader("Generated Email:")
                    st.code(email, language='markdown')

            except Exception as e:
                st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)
