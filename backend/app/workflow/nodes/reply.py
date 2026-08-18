# And the reply_node has the complementary job: Take the patient's answer and add it to what we know i.e. ectarcted field

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