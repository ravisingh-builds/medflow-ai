
from app.workflow.checkpoint import checkpointer
from langgraph.graph import StateGraph, END, START
from app.workflow.state import ReferralState

from app.workflow.nodes import (
    extract_node,
    priority_node,
    missing_fields_node,
    planner_node,
    save_lead_node,
    create_conversation_node,
    interrupt_node,
    reply_node,
)

def should_continue(state: ReferralState):
    """
    Decide whether the workflow should finish or wait for the patient's next response.
    """
    if state.get("next_question") is None:
        return "finish"
    return "wait"


builder = StateGraph(ReferralState)

# Nodes
builder.add_node("extract", extract_node)
builder.add_node("priority", priority_node)
builder.add_node("missing_fields", missing_fields_node)
builder.add_node("planner", planner_node)
builder.add_node("save_lead", save_lead_node)
builder.add_node("interrupt", interrupt_node)
builder.add_node("reply", reply_node)
builder.add_node("create_conversation", create_conversation_node)

#entry point
#builder.set_entry_point("extract")

#edge
builder.add_edge(START, "extract")
builder.add_edge("extract", "priority")
builder.add_edge("priority", "missing_fields")
builder.add_edge("missing_fields", "planner")

builder.add_conditional_edges(
    "planner",
    should_continue,
    {
        "wait": "save_lead",
        "finish": END,
    },
)

builder.add_edge("save_lead", "create_conversation")
builder.add_edge("create_conversation", "interrupt")
builder.add_edge("interrupt", "reply")
builder.add_edge("reply", "missing_fields")
builder.add_edge("missing_fields", "planner")

graph = builder.compile(checkpointer=checkpointer)