from langgraph.graph import StateGraph, END

from app.workflow.state import ReferralState
from app.workflow.nodes import extract_node


builder = StateGraph(ReferralState)

builder.add_node("extract", extract_node)

builder.set_entry_point("extract")

builder.add_edge("extract", END)

graph = builder.compile()