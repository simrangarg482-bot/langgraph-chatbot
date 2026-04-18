import streamlit as st
import os
st.write(os.environ.get("OPENAI_API_KEY"))
st.write(os.environ.get("LANGCHAIN_API_KEY"))