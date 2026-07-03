import streamlit as st
import time
from langchain_core.messages import HumanMessage
from graph import compiled_graph

# 🎨 Page Configuration & Dashboard Layout
st.set_page_config(
    page_title="AI Travel Booking System",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🚀 Custom CSS Injector for Premium Tech Dark Theme, Glow Effects, and Image Slider
st.markdown("""
    <style>
    /* Global Background Adjustments */
    .stApp {
        background-color: #0d1117;
        color: #ffffff;
    }
    
    /* Sidebar styling */
    div[data-testid="stSidebar"] {
        background-color: #070a0e !important;
        border-right: 1px solid #1f2937;
    }
    
    /* Technology Badges styling */
    .tech-badge {
        padding: 8px 12px;
        border-radius: 6px;
        background-color: #111827;
        border: 1px solid #1e3a8a;
        margin-bottom: 8px;
        font-size: 13px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Dynamic Pipeline Status Tracking */
    .pipeline-step {
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 6px;
        font-size: 14px;
        background-color: #1f2937;
        border-left: 4px solid #4b5563;
    }
    .pipeline-active {
        background-color: #1e3a8a !important;
        border-left: 4px solid #3b82f6 !important;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
    }
    .pipeline-done {
        background-color: #064e3b !important;
        border-left: 4px solid #10b981 !important;
    }
    
    /* Premium Action Button styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #1d4ed8, #2563eb);
        color: white !important;
        border: none !important;
        padding: 14px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #2563eb, #3b82f6);
        box-shadow: 0px 0px 20px rgba(59, 130, 246, 0.6);
        transform: translateY(-1px);
    }

    /* Slider Container Constraints */
    .slider-container {
        width: 100%;
        height: 280px;
        overflow: hidden;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    
    /* The filmstrip row holding the images */
    .slider-wrapper {
        display: flex;
        width: 400%; /* 100% per image x 4 images */
        height: 100%;
        animation: slideCarousel 16s infinite ease-in-out;
    }
    
    /* Force consistent layout across all slide images */
    .slider-wrapper img {
        width: 25%; /* Takes exactly 1/4th of the 400% width wrapper */
        height: 100%;
        object-fit: cover;
    }
    
    /* Keyframe instructions tracking horizontal shifts */
    @keyframes slideCarousel {
        0%, 20%   { transform: translateX(0); }
        25%, 45%  { transform: translateX(-25%); }
        50%, 70%  { transform: translateX(-50%); }
        75%, 95%  { transform: translateX(-75%); }
        100%      { transform: translateX(0); }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 💾 INITIALIZE STATE MANAGEMENT KEYS
# ==========================================
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "current_agent" not in st.session_state:
    st.session_state.current_agent = "idle"

# ==========================================
# 🎛️ SIDEBAR PIPELINE MONITORING CONTROL
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#3b82f6; margin-bottom:0;'>📁 AI Travel Planner</h2>", unsafe_allow_html=True)
    
    # 👤 User Configuration Identifier
    user_id = st.text_input("👤 User ID", value="PARSHW_USER", placeholder="Enter account handle...")
    
    st.markdown("---")
    
    # Tech Stack Badges
    st.subheader("Powered by")
    st.markdown("<div class='tech-badge'>🔗 LangGraph Framework</div>", unsafe_allow_html=True)
    st.markdown("<div class='tech-badge'>🦙 Groq • LLaMA 3.3 70B</div>", unsafe_allow_html=True)
    st.markdown("<div class='tech-badge'>🗄️ Shared Memory Pool</div>", unsafe_allow_html=True)
    st.markdown("<div class='tech-badge'>🔍 Tavily Search Engine</div>", unsafe_allow_html=True)
    st.markdown("<div class='tech-badge'>✈️ AviationStack Live API</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Live Active Agent Execution State Pipeline
    st.subheader("Agent Pipeline Execution")
    
    ca = st.session_state.current_agent
    
    f_class = "pipeline-active" if ca == "flight" else ("pipeline-done" if ca in ["hotel", "itinerary", "complete"] else "")
    h_class = "pipeline-active" if ca == "hotel" else ("pipeline-done" if ca in ["itinerary", "complete"] else "")
    i_class = "pipeline-active" if ca == "itinerary" else ("pipeline-done" if ca == "complete" else "")
    fn_class = "pipeline-done" if ca == "complete" else ""

    st.markdown(f"<div class='pipeline-step {f_class}'>✈️ 1. Flight Routing Agent</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='pipeline-step {h_class}'>🏨 2. Hotel Lodging Agent</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='pipeline-step {i_class}'>🗓️ 3. Itinerary Compilation Agent</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='pipeline-step {fn_class}'>🤖 4. Final Aggregator Engine</div>", unsafe_allow_html=True)

# ==========================================
# 🚀 MAIN BLUEPRINT WORKING CANVAS
# ==========================================

# Modern Auto-Sliding Panoramic Header Display (CSS Animation)
st.markdown("""
    <div class="slider-container">
        <div class="slider-wrapper">
            <img src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?q=80&w=1400" alt="Flight Route Planning">
            <img src="https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1400" alt="Boutique Luxury Hotels">
            <img src="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1400" alt="Scenic Travel Destination">
            <img src="https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=1400" alt="Exploration Planning">
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; margin-top: 15px;'>✨ AI Travel Booking System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9ca3af; font-size: 16px;'>Four specialized coordinate agents architecture dynamically querying live data networks to compile optimized itineraries.</p>", unsafe_allow_html=True)

st.markdown("---")

# 🗺️ POPULAR SUGGESTIONS INTERACTIVE CHIPS
st.subheader("🗺️ Popular Suggestions Quick Selection")
card_col1, card_col2, card_col3, card_col4 = st.columns(4)

with card_col1:
    if st.button("🇯🇵 7-day Japan under ₹2L"):
        st.session_state.input_text = "Plan a complete 7 days Japan trip including flights, hotels and sightseeing under 2lakhs."
        st.rerun()

with card_col2:
    if st.button("🇫🇷 Paris trip for 5 days"):
        st.session_state.input_text = "Plan a comprehensive 5 days exploration itinerary of Paris with mid-range accommodation choices."
        st.rerun()

with card_col3:
    if st.button("🇦🇪 Dubai weekend getaway"):
        st.session_state.input_text = "A quick weekend getaway action plan to Dubai focusing on shopping hubs and skyline view hotels."
        st.rerun()

with card_col4:
    if st.button("🇮🇩 Bali backpacking 10 days"):
        st.session_state.input_text = "10 days backpacking route blueprint across Bali emphasizing affordable hostels and beach spots."
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Main Multi-line Prompt Canvas
user_prompt = st.text_area(
    "📝 DESCRIBE YOUR TRIP",
    value=st.session_state.input_text,
    placeholder="Select an interactive preset card above or enter specific customizable routing constraints right here...",
    height=120
)

# Core Execution Trigger Action Row
if st.button("🚀 Generate My Travel Plan", key="main_generation_btn"):
    if not user_prompt.strip():
        st.error("Validation Error: Please specify target path metrics or choose a suggestion item framework.")
    else:
        # Build initial LangGraph runtime dictionary matching schema requirements
        initial_state = {
            "messages": [HumanMessage(content=user_prompt)],
            "next_agent": "supervisor",
            "flight_data": "",
            "hotel_data": "",
            "itinerary_data": ""
        }
        
        # Transparent Processing Monitor
        with st.status("🧠 Multi-Agent Graph Sequence Orchestrating...", expanded=True) as status_box:
            
            st.write("🛰️ **Supervisor Router:** Inspecting global workspace allocations...")
            st.session_state.current_agent = "flight"
            time.sleep(1) # Visual pacing to track sidebar updates cleanly
            
            st.write("✈️ **Flight Agent:** Initializing live external network parameters...")
            # Run graph execution engine synchronously
            final_output = compiled_graph.invoke(initial_state)
            
            st.session_state.current_agent = "hotel"
            st.write("🏨 **Hotel Agent:** Pulling structural evaluations from Tavily search indices...")
            time.sleep(0.5)
            
            st.session_state.current_agent = "itinerary"
            st.write("🗓️ **Itinerary Agent:** Folding constraints into daily schedule matrices...")
            time.sleep(0.5)
            
            st.session_state.current_agent = "complete"
            status_box.update(label="✨ Analysis Completed and Compiled!", state="complete", expanded=False)
            
        st.success(f"🎉 Tailored Master Strategy Blueprint Prepared for Profile: **{user_id}**")
        
        # Primary Output Container
        st.markdown(final_output.get("itinerary_data", "Compilation Exception Intercepted."))
        
        # Inspection Logs Expanders for Portfolio Demonstrations
        with st.expander("🛠️ View Raw Multi-Agent Distributed Ledger Data Logs"):
            tab1, tab2 = st.tabs(["Flight Metadata Cache", "Hotel Search Cache"])
            with tab1:
                st.code(final_output.get("flight_data"), language="text")
            with tab2:
                st.code(final_output.get("hotel_data"), language="text")