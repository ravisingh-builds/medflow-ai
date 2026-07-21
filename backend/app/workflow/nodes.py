from app.ai.extractor import extract_referral


def extract_node(state):
    result = extract_referral(state["referral"])

    state["extracted"] = result

    return state