# Import necessary libraries
import requests  # Used for making HTTP requests
import streamlit as st  # Used for creating the web app interface
from PIL import Image, UnidentifiedImageError  # Used for handling image data
import io  # Used for handling byte streams
import time  # Used for handling delays

# Hugging Face API URLs and Authorization Keys
TEXT_GENERATION_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
IMAGE_CAPTIONING_API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
IMAGE_GENERATION_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
API_KEY = "YOUR_API_KEY"

def query_text_generation(payload, max_new_tokens=1000):
    """
    Sends a request to the Hugging Face API to generate text based on the provided payload.
    
    Args:
        payload (dict): The input prompt for the model.
        max_new_tokens (int): The maximum number of tokens to generate.
    
    Returns:
        dict: The JSON response from the API containing the generated text.
    """
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {"inputs": payload["inputs"], "parameters": {"max_new_tokens": max_new_tokens}}
    response = requests.post(TEXT_GENERATION_API_URL, headers=headers, json=data)
    return response.json()

def query_image_captioning(filename):
    """
    Sends an image file to the Hugging Face API for image captioning.

    Args:
        filename (str): The path to the image file.
    
    Returns:
        dict: The JSON response from the API containing the image caption.
    """
    headers = {"Authorization": f"Bearer {API_KEY}"}
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(IMAGE_CAPTIONING_API_URL, headers=headers, data=data)
    return response.json()

def query_image_generation(payload):
    """
    Sends a text prompt to the Hugging Face API for image generation.

    Args:
        payload (dict): The input text prompt for the model.
    
    Returns:
        requests.Response: The response object from the API containing the generated image bytes.
    """
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.post(IMAGE_GENERATION_API_URL, headers=headers, json=payload)
    return response

def generate_image_with_retry(payload, retries=5, delay=30):
    """
    Attempts to generate an image using the Hugging Face API with retry logic.

    Args:
        payload (dict): The input text prompt for the model.
        retries (int): Number of times to retry if the model is still loading.
        delay (int): Delay between retries in seconds.

    Returns:
        requests.Response: The response object from the API containing the generated image bytes.
    """
    for attempt in range(retries):
        response = query_image_generation(payload)
        if response.status_code == 200:
            return response
        elif response.status_code == 503:
            st.warning(f"Model is currently loading. Retrying in {delay} seconds...")
            time.sleep(delay)
        else:
            st.error(f"Failed to generate image. Status code: {response.status_code}")
            st.error(f"Response content: {response.content.decode('utf-8')}")
            return response
    return response

def main():
    """
    Main function to create the Streamlit web app interface and handle user interactions.
    """
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

    # Sidebar with model information and example prompts
    st.sidebar.title("Model Information")
    st.sidebar.info("This app is powered by MistralAI, capable of generating text, captioning images, and creating images from text.")

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

    # Tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Text Generation", "Image Captioning", "Image Generation"])

    with tab1:
        # Text Generation
        user_prompt = st.text_area("Enter your text prompt:", height=50)
        if st.button("Generate Text Response"):
            payload = {"inputs": user_prompt}
            response = query_text_generation(payload, max_new_tokens=1000)
            
            if response and isinstance(response, list) and len(response) > 0:
                generated_text = response[0].get("generated_text", "No response from Synthia.")
                generated_text = generated_text.replace(user_prompt, "", 1).strip()

                st.subheader("Synthia's Response")
                st.text_area(label="", value=generated_text, height=600)
            else:
                st.error("No response from Synthia.")

    with tab2:
        # Image Captioning
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            with open("uploaded_image.jpg", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

            if st.button("Generate Caption"):
                response = query_image_captioning("uploaded_image.jpg")
                if response and "generated_text" in response[0]:
                    caption = response[0]["generated_text"]
                    st.subheader("Image Caption")
                    st.text(caption)
                else:
                    st.error("No caption generated.")

    with tab3:
        # Image Generation
        text_prompt = st.text_area("Enter a text prompt for image generation:", height=50)
        if st.button("Generate Image"):
            payload = {"inputs": text_prompt}
            response = generate_image_with_retry(payload, retries=5, delay=30)
            if response.status_code == 200:
                try:
                    image = Image.open(io.BytesIO(response.content))
                    st.subheader("Generated Image")
                    st.image(image, use_column_width=True)
                except UnidentifiedImageError:
                    st.error("The response content is not a valid image.")
            else:
                st.error(f"Failed to generate image. Status code: {response.status_code}")
                st.error(f"Response content: {response.content.decode('utf-8')}")

if __name__ == "__main__":
    main()
