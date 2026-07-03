import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# 🔌 Load local .env file if it exists
load_dotenv()

# 🔑 Fetch API Keys securely (Priority: Environment Variables/Local .env -> Streamlit Secrets)
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") or st.secrets.get("TAVILY_API_KEY")
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY") or st.secrets.get("AVIATIONSTACK_API_KEY")

if TAVILY_API_KEY:
    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

# 🧠 Core LLM Engine
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    groq_api_key=GROQ_API_KEY
)