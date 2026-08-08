from app.ai.extractor import extract_referral


def extract_node(state):
    state["extracted"] = extract_referral(
        state["referral"]
    )

    print("======= State RETURNING FROM EXTRACT NODE =====")
    print(state)

    return state