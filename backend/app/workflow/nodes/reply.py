def reply_node(state):

    print("========== STATE ENTRING TO REPLY NODE ==========")
    print(state["extracted"])

    field = state["next_question"]["field"]

    value = state["patient_answer"]

    print("========== Saving ==========")
    print("Saving:", field, "=", value)

    state["extracted"][field] = value

    print("========== STATE RETURNING FROM REPLY NODE ==========")
    print(state["extracted"])

    return state