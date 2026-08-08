from app.ai.priority import classify_priority


def priority_node(state):
    state["priority"] = classify_priority(
        state["referral"]
    )

    print("======= State RETURNING FROM PRIORITY NODE =====")
    print(state)


    return state