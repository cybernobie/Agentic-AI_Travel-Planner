import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from tools import get_tools
import markdown
from xhtml2pdf import pisa
from io import BytesIO

def generate_pdf(md_text):
    """
    Converts the markdown itinerary generated into a downloadable PDF format.
    This is used to provide the user with a convenient way to save and share their personalized travel plan.
    """
    # Sanitize Unicode characters that are not supported by default xhtml2pdf fonts
    safe_md_text = md_text.replace("₹", "Rs. ").replace("°C", " deg C")
    html_content = "<html><head><style>body { font-family: Helvetica, Arial, sans-serif; }</style></head><body>" + markdown.markdown(safe_md_text) + "</body></html>"
    result = BytesIO()
    # Explicitly specify encoding to prevent mojibake with other special characters
    pisa.CreatePDF(BytesIO(html_content.encode('utf-8')), dest=result, encoding='utf-8')
    return result.getvalue()
st.set_page_config(page_title="AI Travel Planner", page_icon="✈️", layout="wide")

# Custom CSS for UI enhancements
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        font-weight: 700 !important;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0rem;
    }
    .sub-header {
        font-size: 1.2rem !important;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    div[data-testid="stForm"] {
        background-color: #F8FAFC;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
    }
    div.stButton > button:first-child {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #1D4ED8;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🌍 Agentic AI Travel Planner</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Plan your dream trip with our intelligent assistant! ✈️🏖️</p>', unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Read API Configuration from environment
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_base = os.getenv("OPENAI_API_BASE")

if not openai_api_key or not openai_api_base:
    st.warning("Please set OPENAI_API_KEY and OPENAI_API_BASE in your .env file to proceed.")
else:
    llm = ChatOpenAI(model="gemini-3-flash", api_key=openai_api_key, base_url=openai_api_base)
    tools = get_tools

    system_prompt = (
        "You are an intelligent travel agent. Your job is to create a complete, personalized travel itinerary for the user based on their preferences.\n"
        "You have access to tools for flight search, hotel recommendations, places to visit, weather forecast, and budget estimation.\n"
        "Always use the tools to find actual data. Do not make up flights or hotels.\n"
        "For flight and hotel selections, you MUST include a brief justification explaining why you selected them (e.g., 'Selected because it was the cheapest option' or 'Selected due to 5-star rating').\n"
        "Construct a final response structured EXACTLY as follows:\n\n"
        "### Trip Summary\n"
        "### Flight Option Selected (with Justification)\n"
        "### Hotel Recommendation (with Justification)\n"
        "### Day-wise Itinerary\n"
        "### Weather for Each Day\n"
        "### Budget Breakdown\n\n"
        "After the markdown output, you MUST provide the exact same itinerary data in a raw JSON block wrapped in ```json and ```.\n"
        "If you cannot find a flight or hotel, inform the user."
    )

    def clean_messages(state):
        """
        Cleans and formats the conversation history (messages) before passing them back to the LLM.
        This is used to manage context, enforce the system prompt, and format tool call logs clearly,
        ensuring the React agent can properly reason about past actions without getting confused.
        """
        from langchain_core.messages import AIMessage, ToolMessage, SystemMessage, HumanMessage
        messages = state["messages"]
        new_messages = [SystemMessage(content=system_prompt)]
        for msg in messages:
            if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
                content = msg.content or ""
                for tc in msg.tool_calls:
                    content += f"\n[Called Tool: {tc['name']} with args: {tc['args']}]"
                new_messages.append(AIMessage(content=content))
            elif isinstance(msg, ToolMessage):
                new_messages.append(HumanMessage(content=f"Tool {msg.name} returned: {msg.content}"))
            else:
                new_messages.append(msg)
        return new_messages

    agent_executor = create_react_agent(llm, tools, prompt=clean_messages)

    # Input Form
    with st.form("travel_form"):
        st.subheader("Tell us about your trip")
        col1, col2 = st.columns(2)
        with col1:
            source = st.text_input("🛫 Source City", placeholder="e.g., Delhi")
        with col2:
            destination = st.text_input("🛬 Destination City", placeholder="e.g., Goa")
            
        col3, col4, col5 = st.columns([1, 1, 2])
        with col3:
            import datetime
            start_date = st.date_input("📅 Start Date", min_value=datetime.date.today())
        with col4:
            duration = st.number_input("⏱️ Duration (days)", min_value=1, max_value=30, value=3)
        with col5:
            preferences = st.text_area("✨ Specific preferences?", placeholder="e.g., 5-star hotel, beachfront, vegetarian food...", height=68)
            
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✨ Generate My Custom Itinerary ✨", use_container_width=True)

    if submitted:
        if not source or not destination:
            st.error("Please provide both source and destination cities.")
        else:
            user_input = f"Plan a {duration}-day trip from {source} to {destination} starting on {start_date.strftime('%A, %B %d, %Y')}. Preferences: {preferences}"
            with st.spinner("Planning your trip... This might take a minute."):
                try:
                    response = agent_executor.invoke({"messages": [HumanMessage(content=user_input)]})
                    st.success("Trip planned successfully!")
                    
                    content = response["messages"][-1].content
                    if isinstance(content, list):
                        text = "".join(item.get("text", "") for item in content if isinstance(item, dict) and "text" in item)
                    else:
                        text = content
                        
                    if "```json" in text:
                        parts = text.split("```json")
                        markdown_part = parts[0]
                        json_part = parts[1].split("```")[0]
                        st.markdown(markdown_part)
                        
                        pdf_data = generate_pdf(markdown_part)
                        st.download_button(
                            label="📄 Download Trip Summary as PDF",
                            data=pdf_data,
                            file_name=f"{source}_to_{destination}_Trip_Summary.pdf",
                            mime="application/pdf"
                        )
                        
                        with st.expander("View Raw JSON Format"):
                            try:
                                import json
                                st.json(json.loads(json_part))
                            except:
                                st.code(json_part, language="json")
                    else:
                        st.markdown(text)
                        pdf_data = generate_pdf(text)
                        st.download_button(
                            label="📄 Download Trip Summary as PDF",
                            data=pdf_data,
                            file_name=f"{source}_to_{destination}_Trip_Summary.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
