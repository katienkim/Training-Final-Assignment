import os
import requests
import json
import streamlit as st

API_ENDPOINT_URL = os.environ.get("API_ENDPOINT_URL", "https://c99i1dn479.execute-api.us-west-2.amazonaws.com/prod/hr")

def streamlit_app(prompt):
    if "YOUR_API_ENDPOINT_URL_HERE" in API_ENDPOINT_URL:
        print("ERROR: Please set the API_ENDPOINT_URL in this script.")
        return

    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'query': prompt
    }
    try:
        # Call the deployed API Gateway endpoint
        response = requests.post(API_ENDPOINT_URL, headers=headers, data=json.dumps(payload), timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes

        response_data = response.json()
                
        # Print the response from the Lambda function
        return f"## Answer\n{response_data.get('answer')}\n\n---\n\n### Sources\n{response_data.get('sources')}"

    except Exception as e:
        return f"## ERROR\n{e}"

# --- Streamlit User Interface ---
st.set_page_config(page_title="HR Policy Assistant", page_icon="📑", layout="centered")

st.title("📑 HR Policy Assistant")
st.markdown("Ask a question about HR policies. The system will retrieve relevant information from our documents and provide a sourced answer.")

with st.form("hr_query_form"):
    user_query = st.text_area("Your Question", placeholder="e.g., What is the policy on remote work?", height=120)
    submitted = st.form_submit_button("Ask")

if submitted and user_query.strip():
    with st.spinner("Retrieving answer..."):
        result = streamlit_app(user_query)
    st.markdown(result)
elif submitted:
    st.warning("⚠️ Please enter a question before submitting.")