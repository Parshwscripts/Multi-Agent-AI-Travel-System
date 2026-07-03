import operator
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from agents import flight_agent_node, hotel_agent_node, itinerary_agent_node

# 🧠 Definition of Shared Graph Memory State
class AgentState(TypedDict):
    messages: Annotated[List[dict], operator.add] # Keeps appended conversation history
    next_agent: str                               # Directs routing flow
    flight_data: str                              # Holds intermediate flight structures
    hotel_data: str                               # Holds intermediate hotel structures
    itinerary_data: str                           # Holds the final compiled output

# --- SUPERVISOR / ROUTER NODE ---
def supervisor_node(state: AgentState):
    """Evaluates the condition of state variables and instructs execution steps."""
    # Sequential verification step routing
    if not state.get("flight_data"):
        return {"next_agent": "flight_agent"}
    elif not state.get("hotel_data"):
        return {"next_agent": "hotel_agent"}
    elif not state.get("itinerary_data"):
        return {"next_agent": "itinerary_agent"}
    else:
        return {"next_agent": "end"}

# --- GRAPH BUILDER ---
workflow = StateGraph(AgentState)

# Add processing units (Nodes)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("flight_agent", flight_agent_node)
workflow.add_node("hotel_agent", hotel_agent_node)
workflow.add_node("itinerary_agent", itinerary_agent_node)

# Execution flow starts directly with the Supervisor Router
workflow.set_entry_point("supervisor")

# Configure conditional edges based on the value returned in 'next_agent'
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["next_agent"],
    {
        "flight_agent": "flight_agent",
        "hotel_agent": "hotel_agent",
        "itinerary_agent": "itinerary_agent",
        "end": END
    }
)

# Structural hard connections looping workers back into supervision evaluation loop
workflow.add_edge("flight_agent", "supervisor")
workflow.add_edge("hotel_agent", "supervisor")
workflow.add_edge("itinerary_agent", "supervisor")

# Compile the final application graph object
compiled_graph = workflow.compile()