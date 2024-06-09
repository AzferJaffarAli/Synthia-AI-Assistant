import streamlit as st
import requests

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
API_KEY = "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"

def query_model(payload, max_new_tokens=1000):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {"inputs": payload["inputs"], "parameters": {"max_new_tokens": max_new_tokens}}
    response = requests.post(API_URL, headers=headers, json=data)
    return response.json()

# Streamlit app interface
def main():
    # Custom CSS for the multicolor gradient background
    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(to right, #d3d3d3, #e0e7ff);
                color: black;
            }
            .css-18e3th9 {
                background-color: transparent !important;
                background: linear-gradient(to right, #d3d3d3, #e0e7ff);
                color: black;
            }
            .css-1d391kg {
                background: transparent;
            }
            .css-1v3fvcr {
                background: transparent;
            }
            .css-1q8dd3e {
                background: transparent;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("Synthia - Your Personal AI Assistant")

    st.sidebar.title("Model Information")
    st.sidebar.info("This model is powered by MistralAI, capable of generating text based on user prompts.")

    st.sidebar.markdown("---")
    st.sidebar.info("Please clearly specify what you want in the prompt.")

    example_prompts = [
        "Explain Machine Learning to me in a nutshell.",
        "What are the latest trends in artificial intelligence?",
        "Write a short story about a journey through time.",
        "Describe the process of photosynthesis.",
        "Compose a poem about the beauty of nature."
    ]

    st.sidebar.markdown("### Example Prompts")
    for prompt in example_prompts:
        st.sidebar.code(prompt)

    # Adjust the width of the sidebar with CSS
    st.markdown(
        f"""
        <style>
            .sidebar .sidebar-content {{
                width: 300px;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

    user_prompt = st.text_area("Enter your prompt:", height=50)

    if st.button("Generate Response"):
        payload = {"inputs": user_prompt}
        response = query_model(payload, max_new_tokens=1000)
        
        if response and isinstance(response, list) and len(response) > 0:
            generated_text = response[0].get("generated_text", "No response from Synthia.")
            generated_text = generated_text.replace(user_prompt, "", 1).strip()

            st.subheader("Synthia's Response")
            st.text_area(label="", value=generated_text, height=600)
        else:
            st.error("No response from Synthia.")

if __name__ == "__main__":
    main()
