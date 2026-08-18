# Given what we know and what's still missing, decide what one question to ask next.
from app.ai.conversation import next_question

def planner_node(state):
    print("=== STATE ENTERING IN Planner NODE ==========")
    print(state["extracted"])
    print(state["missing_fields"])

    next_q = next_question(referral=state["referral"], extracted=state["extracted"], priority=state["priority"], missing_fields=state["missing_fields"],)

    print("======= State RETURNING FROM PLANNER NODE =====")
    print(next_q)

    # No more questions to ask
    if next_q["field"] is None:
        return {
            "next_question": None
        }

    # Ask the next question
    return {
        "next_question": next_q
    }


"""
# ReferralState after this node

ReferralState
-------------------------------------------------------------------
extracted
    ↓
{
    "Patient Name": "Ravi Singh",
    "Diagnosis": "chest pain"
}

missing_fields
    ↓
["Date of Birth", "Phone Number", ...]

next_question
    ↓
{
    "field": "Date of Birth",
    "question": "What is your date of birth?"
}
-----------------------------------------------------------------------
# ReferralState before thos node
# hypothetically
--------------------------------------------------------------------
{
    "referral": "my name is Ravi Singh and I have chest pain",

    "extracted": {
        "Patient Name": "Ravi Singh",
        "Diagnosis": "chest pain"
    },

    "priority": {
        "priority": "HIGH"
    },

    "missing_fields": {
        "missing_fields": [
            "Date of Birth",
            "Phone Number",
            "Insurance Provider"
        ]
    }
}

"""
