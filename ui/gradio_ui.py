import os
import requests
import json
import gradio as gr

API_ENDPOINT_URL = os.environ.get("API_ENDPOINT_URL", "https://c99i1dn479.execute-api.us-west-2.amazonaws.com/prod/hr")

def gradio_app(prompt):
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

# --- Create and Launch the Gradio Interface ---
with gr.Blocks(gr.themes.Citrus(primary_hue="pink", secondary_hue="pink")) as gradioUI:
    gr.Interface(
        fn=gradio_app,
        inputs=gr.Textbox(
            lines=3, 
            label="Your Question", 
            placeholder="e.g., What is the policy on remote work?"
        ),
        outputs=gr.Markdown(label="Response"),
        title="HR Policy Assistant",
        description="Ask a question about HR policies. The system will retrieve relevant information from our documents and provide a sourced answer.",
        allow_flagging="never"
    )

if __name__ == "__main__":
    gradioUI.launch()