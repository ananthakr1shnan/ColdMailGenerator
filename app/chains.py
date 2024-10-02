import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()
os.getenv("api_key")

class Chain:
    def __init__(self):  
        self.llm = ChatGroq(temperature=1, groq_api_key=os.getenv("api_key"), model_name="llama-3.1-70b-versatile")
         
    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links, user_name, company_name):
        prompt_email = PromptTemplate.from_template(
            
             f"""
            ### JOB DESCRIPTION:
            {{job_description}}

            ### INSTRUCTION:
            You are {user_name}, a business development executive at {company_name}. {company_name} is an AI & Software Consulting company dedicated to facilitating
            the seamless integration of business processes through automated tools. 
            Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, 
            process optimization, cost reduction, and heightened overall efficiency. 
            Your job is to write a cold email to the client regarding the job mentioned above describing the capability of {company_name} 
            in fulfilling their needs.
            Also add the most relevant ones from the following links to showcase {company_name}'s portfolio: {{link_list}}
            Remember you are {user_name}, BDE at {company_name}. 
            Do not provide a preamble.
            ### EMAIL (NO PREAMBLE):
            ### Add a new line after each of these: [User's Name], new line Business Development Executive,new line [Company Name]
            """

        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links})
        return res.content
