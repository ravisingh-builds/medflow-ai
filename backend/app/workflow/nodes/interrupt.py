from langgraph.types import interrupt


def interrupt_node(state):
    """
    Pause the workflow and return the current question
    to the caller.
    """

    question = state["next_question"]["question"]

    answer = interrupt(question)

    state["patient_answer"] = answer

    print("======= State RETURNING FROM INTERRUPT NODE =====")
    print(state)


    return state