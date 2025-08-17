# app.py
import streamlit as st
import requests
import json
import os

# To handle secrets, use Streamlit's secrets management or environment variables.
# For local testing with a Dockerfile, an .env file is a good choice.
# This assumes you have a .env file with the line:
# GOOGLE_API_KEY="YOUR_API_KEY_HERE"
# In a real deployment, use a more secure method.
API_KEY = os.getenv("GOOGLE_API_KEY")

# Model and API Endpoint Configuration
MODEL_NAME = "gemini-2.0-flash-lite"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

# --- Security Layer 1: Prompt Guardrails and Filters ---
# A simple, hardcoded list of forbidden keywords.
# This could be replaced by a more sophisticated LLM-based classifier.
FORBIDDEN_KEYWORDS = ["violence", "hate", "unethical", "illegal", "dangerous"]
# Note: For this demo, let's also add a keyword to check for our simple auth.
REQUIRED_AUTH_PHRASE = "gemini access granted"

def check_prompt_guardrails(prompt: str) -> bool:
    """
    Checks if the prompt contains any forbidden keywords.
    Returns True if safe, False otherwise.
    """
    # Simple check for forbidden words, case-insensitive.
    lower_prompt = prompt.lower()
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in lower_prompt:
            st.warning(f"Your prompt contains a forbidden keyword: '{keyword}'. Please rephrase your request.")
            return False
    return True

# --- Security Layer 2: Prompt-based Authentication ---
# A very simple form of authentication. The user must include a specific phrase.
# This is a basic demonstration of the concept.
def check_prompt_authentication(prompt: str) -> bool:
    """
    Checks if the prompt contains the required authentication phrase.
    Returns True if authenticated, False otherwise.
    """
    if REQUIRED_AUTH_PHRASE not in prompt.lower():
        st.warning(f"Access Denied. To use the model, you must include the phrase '{REQUIRED_AUTH_PHRASE}' in your prompt.")
        return False
    return True

# --- The core Streamlit App ---
st.set_page_config(page_title="GenAI Safety Shield", layout="centered")

st.title("🛡️ MANISH - GenAI SECURITY PROMPTING - Safety Shield")
st.markdown("This app demonstrates a simple, multi-layered defense strategy to protect a GenAI application.")

# User input text area
user_prompt = st.text_area(
    "Enter your prompt here:",
    placeholder=f"E.g., {REQUIRED_AUTH_PHRASE}, write a short story about a brave knight."
)

if st.button("Generate Response"):
    if not API_KEY:
        st.error("API Key not found. Please set the GOOGLE_API_KEY environment variable.")
    elif user_prompt:
        # Step 1: Apply the authentication layer
        if check_prompt_authentication(user_prompt):
            # Step 2: Apply the guardrails and filters layer
            if check_prompt_guardrails(user_prompt):
                with st.spinner("Generating response..."):
                    try:
                        # Prepare the payload for the API call
                        payload = {
                            "contents": [
                                {
                                    "role": "user",
                                    "parts": [{"text": user_prompt}]
                                }
                            ]
                        }

                        # Make the POST request to the Gemini API
                        response = requests.post(API_URL, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
                        response.raise_for_status()  # Raise an exception for bad status codes

                        # Parse the response and extract the generated text
                        response_data = response.json()
                        generated_text = response_data['candidates'][0]['content']['parts'][0]['text']

                        st.subheader("Generated Response:")
                        st.write(generated_text)

                    except requests.exceptions.HTTPError as err:
                        st.error(f"HTTP Error: {err.response.status_code} - {err.response.text}")
                    except KeyError:
                        st.error("Error: Could not parse the model's response. The response format was unexpected.")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}")

