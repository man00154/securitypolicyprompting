# app.py
import streamlit as st
import json
import time

# --- Configuration ---
# Note: The API call is mocked to avoid requiring an actual API key and network request.
# The `gemini-2.0-flash-lite` model is mentioned as per the user's request, but this code
# simulates its behavior rather than calling it directly.
MODEL_NAME = "gemini-2.0-flash-lite"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

# --- Simple Hardcoded Security Policies (The "Safety Shield") ---
# These lists act as our simple "prompt guardrails" and "output filters."
# In a real application, these would be much more sophisticated,
# potentially using a separate classification model or more extensive dictionaries.

# Prompt Guardrails: Keywords that are not allowed in the user's input.
PROMPT_DENY_LIST = [
    "malicious", "exploit", "unauthorized", "bypass", "attack",
    "shutdown", "delete all", "wipe", "DDoS", "phishing"
]

# Prompt-based Authorization: A simple "password phrase" for the user.
AUTH_PHRASE = "I am an authorized admin"

# Output Filters: Keywords we don't want the LLM to output.
OUTPUT_DENY_LIST = [
    "sudo rm -rf /", "reboot", "shutdown now", "unmount", "kill -9"
]

# --- Core LLM Interaction Logic (MOCK) ---
def mock_generate_content(prompt):
    """
    This function simulates a call to the LLM API.
    In a real application, you would use the 'requests' library to make an HTTP POST call
    to the Gemini API with your API key and prompt.
    """
    st.info(f"Connecting to model: {MODEL_NAME}...")
    time.sleep(2) # Simulate network latency

    # Simple, predictive logic based on the input.
    if "firewall" in prompt.lower():
        return {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": "Generated policy for firewall: \n- Block all incoming traffic on port 22 (SSH) from external networks. \n- Allow web traffic on ports 80 and 443. \n- Log all dropped packets to the security information and event management (SIEM) system. \n- Please note: This is a basic policy. Always review and customize for your specific needs."
                    }]
                }
            }]
        }
    elif "VPN" in prompt.lower():
        return {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": "Generated policy for VPN access: \n- Enforce two-factor authentication for all VPN users. \n- Require a minimum password length of 16 characters. \n- Implement an idle timeout of 30 minutes. \n- Ensure all user traffic is encrypted using AES-256. \n- All VPN access should be logged and monitored for suspicious activity."
                    }]
                }
            }]
        }
    else:
        return {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": "Generated generic security policy: \n- Implement strong password policies. \n- Use endpoint protection software. \n- Regularly patch all systems. \n- Conduct routine security audits."
                    }]
                }
            }]
        }

# --- Streamlit Application Layout ---
st.set_page_config(
    page_title="MANISH -Network Security Policy Assistant",
    page_icon="🛡️"
)

st.title("🛡️ Secure Network Policy Assistant")
st.subheader("A multi-layered defense tool with simple prompt-based guardrails.")

st.info("This application demonstrates a 'safety shield' around an LLM. It validates your input and filters the model's output before displaying it.")

# User Input
user_prompt = st.text_area(
    "Enter your network security policy request:",
    "Create a basic firewall policy for a web server."
)
authorization_check = st.text_input(
    f"Enter the authorization phrase to proceed (e.g., '{AUTH_PHRASE}'):"
)

# Button to trigger the process
if st.button("Generate Policy", use_container_width=True):
    st.write("---")
    st.markdown("### Process Log")
    
    # --- Layer 1: Prompt-based Authentication and Authorization ---
    if authorization_check.strip() != AUTH_PHRASE:
        st.error("❌ **Authorization Failed:** Please enter the correct authorization phrase.")
        st.stop()
    st.success("✅ **Authorization Passed.**")

    # --- Layer 2: Prompt Guardrails and Filters (Input Validation) ---
    is_safe_prompt = True
    for word in PROMPT_DENY_LIST:
        if word in user_prompt.lower():
            st.error(f"❌ **Prompt Guardrail Triggered:** The word '{word}' is not allowed in the prompt.")
            is_safe_prompt = False
            break
    
    if not is_safe_prompt:
        st.warning("Please modify your request to proceed.")
        st.stop()
    st.success("✅ **Input Validation Passed.** Your prompt is safe.")
    st.write("") # Add a little space

    # --- Core LLM Interaction ---
    try:
        # Simulate the LLM API call
        response = mock_generate_content(user_prompt)
        raw_output = response["candidates"][0]["content"]["parts"][0]["text"]
        
        st.info("✅ **Policy Generated.** Applying output filters...")

        # --- Layer 3: Output Validation and Filtering ---
        final_output_parts = []
        is_safe_output = True
        for line in raw_output.split('\n'):
            is_safe_line = True
            for word in OUTPUT_DENY_LIST:
                if word in line.lower():
                    st.warning(f"⚠️ **Output Filter Triggered:** A potentially dangerous command was detected and will be removed.")
                    st.info(f"Line removed: `{line.strip()}`")
                    is_safe_line = False
                    is_safe_output = False
                    break
            if is_safe_line:
                final_output_parts.append(line)

        final_output = '\n'.join(final_output_parts)
        
        if is_safe_output:
            st.success("✅ **Output Filters Passed.**")
        st.write("---")
        st.markdown("### Final Security Policy")
        st.code(final_output)

    except Exception as e:
        st.error(f"An error occurred during generation: {e}")

