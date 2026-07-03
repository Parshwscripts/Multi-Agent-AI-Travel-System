import requests
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from config import llm, AVIATIONSTACK_API_KEY

# --- 1. FLIGHT AGENT ---
def flight_agent_node(state):
    """Fetches flight availability metadata and structures options using LLM."""
    user_query = state["messages"][-1].content
    
    # Live API call to AviationStack
    url = "https://api.aviationstack.com/v1/flights"
    params = {
        'access_key': AVIATIONSTACK_API_KEY,
        'limit': 3
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json().get('data', [])
            # Reduce raw token footprint by stripping out deeply nested empty keys
            flight_data_summary = [
                {
                    "flight_date": f.get("flight_date"),
                    "status": f.get("flight_status"),
                    "airline": f.get("airline", {}).get("name"),
                    "departure": f.get("departure", {}).get("airport"),
                    "arrival": f.get("arrival", {}).get("airport")
                } for f in data if f.get("airline")
            ]
        else:
            flight_data_summary = "API response non-200. Using standard scheduling routing."
    except Exception as e:
        flight_data_summary = f"Live endpoint timed out. Defaulting to standard schedules. Details: {str(e)}"

    # Prompt Llama to convert raw payload to structured recommendations
    prompt = f"""
    You are an expert flight consultant agent. 
    User Requirement: {user_query}
    Raw Data available: {flight_data_summary}
    
    Extract or recommend the top 3 best flight route frameworks for this trip. 
    Be concise, structured, and provide explicit airport codes if available.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"flight_data": response.content, "next_agent": "supervisor"}


# --- 2. HOTEL AGENT ---
def hotel_agent_node(state):
    """Queries Tavily Search to identify top accommodations and rates."""
    user_query = state["messages"][-1].content
    
    # Initialize Tavily search tool container
    tavily_tool = TavilySearchResults(max_results=3)
    
    try:
        search_results = tavily_tool.invoke({"query": f"top rated hotels accommodation deals in {user_query}"})
    except Exception as e:
        search_results = f"Search fallback activated. Error executing live query: {str(e)}"
        
    prompt = f"""
    You are an expert hospitality agent. 
    Analyze the user intent: '{user_query}' with these search results: {search_results}.
    Provide a list of 3 highly recommended hotel options with pricing tiers and features.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"hotel_data": response.content, "next_agent": "supervisor"}


# --- 3. ITINERARY AGENT ---
def itinerary_agent_node(state):
    """Combines flights and hotel structures into a beautiful markdown travel guide."""
    user_query = state["messages"][-1].content
    flights = state.get("flight_data", "No flight options found.")
    hotels = state.get("hotel_data", "No hotel options found.")
    
    prompt = f"""
    You are a premium travel concierge. 
    Create a highly engaging, professional day-by-day itinerary matching this request: {user_query}.
    
    Incorporate the options found below:
    - Flight Options: {flights}
    - Hotel Selections: {hotels}
    
    Format the response explicitly in beautiful, clean Markdown with clear emoji headings.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"itinerary_data": response.content, "next_agent": "supervisor"}