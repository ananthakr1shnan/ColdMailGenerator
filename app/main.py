import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text

def create_streamlit_app(llm, portfolio, clean_text):
    # Set page config
    st.set_page_config(layout="wide", page_title="📧 Cold Email Generator", page_icon="📧")

    # Title and subtitle
    st.title("📧 Cold Mail Generator")
    st.markdown("Generate professional cold emails effortlessly!")

    # Add some styling
    st.markdown("""
        <style>
            .stTextInput {
                border: 1px solid #0072B1;
                border-radius: 5px;
                padding: 10px;
            }
            .stButton {
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            .result {
                border: 2px solid #0072B1;
                border-radius: 5px;
                padding: 15px;
                background-color: #000000
            }
        </style>
    """, unsafe_allow_html=True)

    # Input columns
    col1, col2 = st.columns([2, 1])

    # URL and user info input
    with col1:
        url_input = st.text_input("Enter a Job URL:", 
                                   value="https://jobs.nike.com/job/R-37921", 
                                   placeholder="e.g., https://example.com/job",
                                   key="url_input")
        user_name = st.text_input("Your Name:", placeholder="e.g., Mohan", key="user_name")
        company_name = st.text_input("Your Company Name:", placeholder="e.g., AtliQ", key="company_name")
    
    with col2:
        submit_button = st.button("Generate Email")

    # Process input and generate email
    if submit_button:
        with st.spinner("Generating..."):
            try:
                # Load job data
                loader = WebBaseLoader([url_input])
                data = clean_text(loader.load().pop().page_content)
                portfolio.load_portfolio()
                jobs = llm.extract_jobs(data)

                if jobs:
                    st.subheader("Extracted Job Titles:")
                    for job in jobs:
                        title = job.get('role')
                        if title:
                            st.write(f"- **{title}**")

                    st.subheader("Generated Emails:")
                    for job in jobs:
                        skills = job.get('skills', [])
                        links = portfolio.query_links(skills)
                        email = llm.write_mail(job, links, user_name, company_name)
                        st.markdown(f"<div class='result'>{email}</div>", unsafe_allow_html=True)
                else:
                    st.warning("No jobs found. Please check the URL.")

            except Exception as e:
                st.error(f"An Error Occurred: {e}")

if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    create_streamlit_app(chain, portfolio, clean_text)
