from langgraph.graph import StateGraph, END, START

from app.workflow.checkpoint import checkpointer
from app.workflow.state import ReferralState
from app.workflow.routing import should_continue, after_interrupt, after_confirm
from app.workflow.nodes import (
    extract_node,
    priority_node,
    missing_fields_node,
    planner_node,
    save_lead_node,
    create_conversation_node,
    interrupt_node,
    reply_node,
    finish_node,
    offer_slots_node,
    confirm_slot_node,
)

builder = StateGraph(ReferralState)

builder.add_node("extract", extract_node)
builder.add_node("priority", priority_node)
builder.add_node("missing_fields", missing_fields_node)
builder.add_node("planner", planner_node)
builder.add_node("save_lead", save_lead_node)
builder.add_node("interrupt", interrupt_node)
builder.add_node("reply", reply_node)
builder.add_node("create_conversation", create_conversation_node)
builder.add_node("offer_slots", offer_slots_node)
builder.add_node("confirm_slot", confirm_slot_node)
builder.add_node("finish", finish_node)

builder.add_edge(START, "extract")
builder.add_edge("extract", "priority")
builder.add_edge("priority", "missing_fields")
builder.add_edge("missing_fields", "planner")

builder.add_conditional_edges(
    "planner",
    should_continue,
    {
        "wait": "save_lead",
        "schedule": "offer_slots",
    },
)

builder.add_edge("save_lead", "create_conversation")
builder.add_edge("create_conversation", "interrupt")

builder.add_conditional_edges(
    "interrupt",
    after_interrupt,
    {
        "reply": "reply",
        "confirm": "confirm_slot",
    },
)

builder.add_edge("reply", "missing_fields")
builder.add_edge("missing_fields", "planner")

builder.add_edge("offer_slots", "interrupt")

builder.add_conditional_edges(
    "confirm_slot",
    after_confirm,
    {
        "finish": "finish",
        "reoffer": "offer_slots",
    },
)

builder.add_edge("finish", END)

graph = builder.compile(checkpointer=checkpointer)
