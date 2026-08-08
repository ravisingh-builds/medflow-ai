def finish_node(state):
    state["completed"] = True

    print("======= State RETURNING FROM FINISH NODE =====")
    print(state)

    return state