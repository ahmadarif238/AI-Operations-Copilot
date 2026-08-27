from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from app.agents.agents_definitions import (
    QueryAgent, RetrievalAgent, OpsMonitorAgent, 
    TicketAgent, NotificationAgent, WeeklySummaryAgent
)

class AgentState(TypedDict):
    query: Optional[str]
    user_id: Optional[str]
    log_entry: Optional[Dict]
    next: Optional[str]
    answer: Optional[str]
    sources: Optional[List[Dict]]
    ticket_id: Optional[str]
    severity: Optional[str]
    summary_stats: Optional[Dict]

# Initialize Agents
query_agent = QueryAgent()
retrieval_agent = RetrievalAgent()
ops_agent = OpsMonitorAgent()
ticket_agent = TicketAgent()
notif_agent = NotificationAgent()
summary_agent = WeeklySummaryAgent()

# Define Graph
workflow = StateGraph(AgentState)

# Nodes
workflow.add_node("router", query_agent.route)
workflow.add_node("retrieval", retrieval_agent.retrieve_and_answer)
workflow.add_node("ops_monitor", ops_agent.analyze)
workflow.add_node("ticket_creation", ticket_agent.create_ticket)
workflow.add_node("notification", notif_agent.send_alert)
workflow.add_node("weekly_summary", summary_agent.generate)

# Edges
def router_logic(state):
    return state["next"]

workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    router_logic,
    {
        "retrieval": "retrieval",
        "ops_monitor": "ops_monitor",
        "weekly_summary": "weekly_summary"
    }
)

def ops_logic(state):
    if state.get("next") == "ticket_creation":
        return "ticket_creation"
    return END

workflow.add_conditional_edges("ops_monitor", ops_logic, {"ticket_creation": "ticket_creation", END: END})

workflow.add_edge("ticket_creation", "notification")
workflow.add_edge("notification", END)
workflow.add_edge("retrieval", END)
workflow.add_edge("weekly_summary", END)

app_graph = workflow.compile()
