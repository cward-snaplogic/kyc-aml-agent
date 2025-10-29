import streamlit as st
import requests
import json

# Configure Streamlit - must be the first Streamlit command
st.set_page_config(
    page_title="KYC/AML Onboarding Agent",
    layout="wide"
)

st.title("KYC/AML Onboarding Agent")

# Sidebar with file upload and tools
with st.sidebar:
    # File Upload Section
    st.header("📄 Document Upload")
    uploaded_file = st.file_uploader(
        "Upload a document (PDF, Word, Excel, etc.)",
        type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv']
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        # Store file data in session state
        if "uploaded_file_data" not in st.session_state:
            st.session_state.uploaded_file_data = {}
        
        # Read file content based on type
        try:
            if uploaded_file.type == "text/plain":
                st.session_state.uploaded_file_data = {
                    "name": uploaded_file.name,
                    "type": uploaded_file.type,
                    "content": str(uploaded_file.read(), "utf-8")
                }
            else:
                # For other file types, store as base64
                import base64
                st.session_state.uploaded_file_data = {
                    "name": uploaded_file.name,
                    "type": uploaded_file.type,
                    "content": base64.b64encode(uploaded_file.read()).decode()
                }
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
    else:
        # Clear file data if no file is uploaded
        if "uploaded_file_data" in st.session_state:
            del st.session_state.uploaded_file_data
    
    st.divider()
    
    # Agent Tools Section
    st.header("🔧 Agent Tools")
    
    # nCino Tool
    try:
        st.image("attached_assets/download (75)_1750676484142.png", width=120)
    except:
        st.markdown("**📊 nCino**")
    st.markdown("""
    **nCino Loan Lookup**  
    Performs a loan lookup in nCino for a given company to retrieve existing lending relationships and account information.
    """)
    st.divider()
    
    # Creditsafe Tool
    try:
        st.image("attached_assets/images (6)_1750676484141.png", width=120)
    except:
        st.markdown("**🔍 Creditsafe**")
    st.markdown("""
    **Company Search & Risk Analysis**  
    Search for a company using the Creditsafe API. Returns registered name, status, registration number, and risk indicators (e.g., PEPs, sanctions).
    """)
    st.divider()
    
    # Companies House Tool
    try:
        st.image("attached_assets/comp-house-Logo-300x300_1750676484142.jpg", width=120)
    except:
        st.markdown("**🏛️ Companies House**")
    st.markdown("""
    **Official UK Registration Search**  
    Searches Companies House to retrieve official registration details and filing history for UK-registered entities.
    """)
    st.divider()

# Initialize chat history with welcome message
def init_session_state():
    if "messages" not in st.session_state:
        welcome_message = """👋 **Welcome to the KYC/AML Onboarding Agent!**

I'm here to help you complete the KYC (Know Your Customer) and AML (Anti-Money Laundering) onboarding process for new corporate borrowers as part of the CCB onboarding workflow.

**What I can help you with:**
- 🔍 Search for existing Loan Applications in nCino
- ✅ Extract and verify company identity using Creditsafe and Companies House
- 📄 Process uploaded documents like Application Forms to extract relevant data
- 🔍 Screen for risk indicators including PEPs (Politically Exposed Persons), sanctions, and alerts
- ⚠️ Detect and report any data discrepancies
- 📋 Guide you through the complete onboarding process efficiently

**To get started:**
- Ask me questions about a company or the onboarding process
- I'll run the necessary verification checks for you

How can I assist you with your KYC/AML onboarding today?"""

        st.session_state.messages = [{"role": "assistant", "content": welcome_message}]

# Initialize session state
init_session_state()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
prompt = st.chat_input("What is your question?")

if prompt:
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Process the request
    api_url = "https://prodeu-connectfasterinc-cloud-fm.emea.snaplogic.io/api/1/rest/feed-master/queue/ConnectFasterInc/projects/Chris%20Ward/Driver_Task_Ultra?bearer_token=7XTRF28rachuuepVujqBJpinQNijorlh"

    # Prepare payload
    payload = {
        "messages": st.session_state.messages,
        "current_message": prompt
    }
    
    # Add uploaded file data if available
    if "uploaded_file_data" in st.session_state:
        payload["file"] = st.session_state.uploaded_file_data

    # Show thinking message and process request
    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("Thinking...")

        try:
            # Make API call
            response = requests.post(api_url, json=payload, timeout=300)

            if response.status_code == 200:
                try:
                    api_response = response.json()
                    if isinstance(api_response, list) and len(api_response) > 0:
                        first_item = api_response[0]
                        if isinstance(first_item, dict):
                            bot_response = first_item.get("response", str(first_item))
                        else:
                            bot_response = str(first_item)
                    elif isinstance(api_response, dict):
                        bot_response = api_response.get("response", str(api_response))
                    else:
                        bot_response = str(api_response)
                except json.JSONDecodeError:
                    bot_response = response.text
            else:
                bot_response = f"Sorry, I encountered an error (Status: {response.status_code}). Please try again."

        except requests.exceptions.Timeout:
            bot_response = "Sorry, the request timed out. Please try again."
        except requests.exceptions.RequestException as e:
            bot_response = f"Sorry, I couldn't connect to the service. Error: {str(e)}"
        except Exception as e:
            bot_response = f"An unexpected error occurred: {str(e)}"

        # Replace thinking message with actual response
        thinking_placeholder.markdown(bot_response)

        # Add to session state
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
