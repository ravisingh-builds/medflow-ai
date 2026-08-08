from app.ai.conversation import next_question


def planner_node(state):
    print("=== STATE ENTERING IN Planner NODE ==========")
    print(state["extracted"])
    print(state["missing_fields"])

    next_q = next_question(
        referral=state["referral"],
        extracted=state["extracted"],
        priority=state["priority"],
        missing_fields=state["missing_fields"],
    )

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